#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量历史数据导入命令
支持CSV和JSON格式的双色球历史数据导入
包含数据验证、清洗和重复检查功能
"""

import csv
import json
import os
from datetime import datetime
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from lottery.models import LotteryResult, Statistics
from django.utils.dateparse import parse_date


class Command(BaseCommand):
    help = '批量导入双色球历史开奖数据 (支持CSV/JSON格式)'

    def add_arguments(self, parser):
        parser.add_argument(
            'file_path',
            type=str,
            help='数据文件路径 (CSV或JSON格式)'
        )
        parser.add_argument(
            '--format',
            type=str,
            choices=['csv', 'json'],
            help='数据文件格式 (csv/json)，如不指定则根据文件扩展名自动判断'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='试运行模式，只验证数据不实际导入'
        )
        parser.add_argument(
            '--skip-validation',
            action='store_true',
            help='跳过数据验证（谨慎使用）'
        )
        parser.add_argument(
            '--update-existing',
            action='store_true',
            help='更新已存在的记录'
        )

    def handle(self, *args, **options):
        file_path = options['file_path']
        file_format = options.get('format')
        dry_run = options.get('dry_run', False)
        skip_validation = options.get('skip_validation', False)
        update_existing = options.get('update_existing', False)

        # 检查文件是否存在
        if not os.path.exists(file_path):
            raise CommandError(f'文件不存在: {file_path}')

        # 自动判断文件格式
        if not file_format:
            if file_path.endswith('.csv'):
                file_format = 'csv'
            elif file_path.endswith('.json'):
                file_format = 'json'
            else:
                raise CommandError('无法判断文件格式，请使用 --format 参数指定')

        self.stdout.write(f'🌈 开始导入双色球历史数据...')
        self.stdout.write(f'📄 文件: {file_path}')
        self.stdout.write(f'📋 格式: {file_format.upper()}')
        if dry_run:
            self.stdout.write(self.style.WARNING('⚠️  试运行模式：仅验证数据，不实际导入'))

        try:
            # 读取数据
            if file_format == 'csv':
                data = self._read_csv(file_path)
            else:
                data = self._read_json(file_path)

            # 验证数据
            if not skip_validation:
                self.stdout.write('🔍 开始数据验证...')
                valid_data, invalid_data = self._validate_data(data)
                
                if invalid_data:
                    self.stdout.write(
                        self.style.WARNING(f'⚠️  发现 {len(invalid_data)} 条无效数据')
                    )
                    for i, error in enumerate(invalid_data[:5]):  # 只显示前5个错误
                        self.stdout.write(f'  错误 {i+1}: {error}')
                    if len(invalid_data) > 5:
                        self.stdout.write(f'  ... 还有 {len(invalid_data)-5} 个错误')
            else:
                valid_data = data

            self.stdout.write(f'✅ 有效数据记录: {len(valid_data)} 条')

            if not valid_data:
                self.stdout.write(self.style.ERROR('❌ 没有有效数据可以导入'))
                return

            # 导入数据
            if not dry_run:
                self._import_data(valid_data, update_existing)
                
                # 更新统计数据
                self.stdout.write('📈 更新统计数据...')
                self._update_statistics()
                
                self.stdout.write(self.style.SUCCESS('🎉 数据导入完成!'))
            else:
                self.stdout.write(self.style.SUCCESS('✅ 数据验证完成，试运行结束'))

        except Exception as e:
            raise CommandError(f'导入失败: {str(e)}')

    def _read_csv(self, file_path):
        """读取CSV格式数据"""
        data = []
        with open(file_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                data.append(row)
        return data

    def _read_json(self, file_path):
        """读取JSON格式数据"""
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        
        # 支持两种JSON格式：数组和对象包含数组
        if isinstance(data, dict) and 'results' in data:
            return data['results']
        elif isinstance(data, list):
            return data
        else:
            raise CommandError('JSON格式不正确，应为数组或包含results字段的对象')

    def _validate_data(self, data):
        """验证数据格式和内容"""
        valid_data = []
        invalid_data = []

        for i, record in enumerate(data):
            try:
                # 验证必要字段
                if not all(field in record for field in ['issue', 'draw_date']):
                    invalid_data.append(f'第{i+1}行: 缺少必要字段 (issue, draw_date)')
                    continue

                # 验证期号格式
                issue = str(record['issue']).strip()
                if not issue:
                    invalid_data.append(f'第{i+1}行: 期号不能为空')
                    continue

                # 验证开奖日期
                draw_date = record['draw_date']
                if isinstance(draw_date, str):
                    parsed_date = parse_date(draw_date)
                    if not parsed_date:
                        invalid_data.append(f'第{i+1}行: 日期格式错误 ({draw_date})')
                        continue
                    draw_date = parsed_date

                # 验证红球号码
                red_balls = []
                for j in range(1, 7):
                    field_name = f'red_ball_{j}'
                    if field_name not in record:
                        invalid_data.append(f'第{i+1}行: 缺少红球{j}')
                        break
                    
                    try:
                        ball = int(record[field_name])
                        if not (1 <= ball <= 33):
                            invalid_data.append(f'第{i+1}行: 红球{j}超出范围 (1-33): {ball}')
                            break
                        red_balls.append(ball)
                    except (ValueError, TypeError):
                        invalid_data.append(f'第{i+1}行: 红球{j}不是有效数字: {record[field_name]}')
                        break
                
                if len(red_balls) != 6:
                    continue

                # 检查红球重复
                if len(set(red_balls)) != 6:
                    invalid_data.append(f'第{i+1}行: 红球号码重复: {red_balls}')
                    continue

                # 验证蓝球号码
                try:
                    blue_ball = int(record['blue_ball'])
                    if not (1 <= blue_ball <= 16):
                        invalid_data.append(f'第{i+1}行: 蓝球超出范围 (1-16): {blue_ball}')
                        continue
                except (ValueError, TypeError, KeyError):
                    invalid_data.append(f'第{i+1}行: 蓝球不是有效数字或缺失')
                    continue

                # 构建有效数据记录
                valid_record = {
                    'issue': issue,
                    'draw_date': draw_date,
                    'red_ball_1': red_balls[0],
                    'red_ball_2': red_balls[1],
                    'red_ball_3': red_balls[2],
                    'red_ball_4': red_balls[3],
                    'red_ball_5': red_balls[4],
                    'red_ball_6': red_balls[5],
                    'blue_ball': blue_ball,
                }
                valid_data.append(valid_record)

            except Exception as e:
                invalid_data.append(f'第{i+1}行: 处理错误 - {str(e)}')

        return valid_data, invalid_data

    def _import_data(self, data, update_existing=False):
        """导入数据到数据库"""
        created_count = 0
        updated_count = 0
        skipped_count = 0

        with transaction.atomic():
            for record in data:
                try:
                    # 检查记录是否已存在
                    existing = LotteryResult.objects.filter(issue=record['issue']).first()
                    
                    if existing:
                        if update_existing:
                            # 更新现有记录
                            for field, value in record.items():
                                setattr(existing, field, value)
                            existing.save()
                            updated_count += 1
                        else:
                            skipped_count += 1
                    else:
                        # 创建新记录
                        LotteryResult.objects.create(**record)
                        created_count += 1

                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'导入记录失败 (期号: {record["issue"]}): {str(e)}')
                    )

        self.stdout.write(f'📊 导入统计:')
        self.stdout.write(f'  ✅ 新增记录: {created_count} 条')
        if update_existing:
            self.stdout.write(f'  🔄 更新记录: {updated_count} 条')
        if skipped_count > 0:
            self.stdout.write(f'  ⏭️  跳过记录: {skipped_count} 条 (已存在)')

    def _update_statistics(self):
        """更新统计数据"""
        try:
            # 删除现有统计数据
            Statistics.objects.all().delete()
            
            # 重新生成统计数据
            all_results = LotteryResult.objects.all().order_by('draw_date')
            
            # 红球统计 (1-33)
            for ball_num in range(1, 34):
                appear_count = 0
                last_appear_issue = None
                
                for result in all_results:
                    red_balls = result.get_red_balls()
                    if ball_num in red_balls:
                        appear_count += 1
                        last_appear_issue = result.issue
                
                Statistics.objects.create(
                    ball_number=ball_num,
                    ball_type='red',
                    appear_count=appear_count,
                    last_appear_issue=last_appear_issue
                )
            
            # 蓝球统计 (1-16)
            for ball_num in range(1, 17):
                appear_count = 0
                last_appear_issue = None
                
                for result in all_results:
                    if result.blue_ball == ball_num:
                        appear_count += 1
                        last_appear_issue = result.issue
                
                Statistics.objects.create(
                    ball_number=ball_num,
                    ball_type='blue',
                    appear_count=appear_count,
                    last_appear_issue=last_appear_issue
                )
                
            self.stdout.write('✅ 统计数据更新完成')
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'统计数据更新失败: {str(e)}')
            ) 