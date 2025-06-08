#!/usr/bin/env python
"""
导入双色球样例数据的Django管理命令
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime, timedelta
import random
from lottery.models import LotteryResult, Statistics


class Command(BaseCommand):
    help = '导入双色球样例数据用于测试和演示'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=100,
            help='要生成的开奖记录数量 (默认: 100)'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='导入前清空现有数据'
        )

    def handle(self, *args, **options):
        count = options['count']
        clear_data = options['clear']
        
        self.stdout.write('🌈 开始导入双色球样例数据...\n')
        
        # 清空现有数据
        if clear_data:
            self.stdout.write('🗑️  清空现有数据...')
            LotteryResult.objects.all().delete()
            Statistics.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('✅ 数据清空完成'))
        
        # 生成样例开奖数据
        self.stdout.write(f'📊 生成 {count} 条开奖记录...')
        
        # 起始日期：从100天前开始
        start_date = datetime.now().date() - timedelta(days=count)
        
        created_count = 0
        for i in range(count):
            # 生成期号 (格式: 2024001, 2024002, ...)
            issue = f"2024{str(i+1).zfill(3)}"
            
            # 生成开奖日期 (每3天一期，模拟真实开奖频率)
            draw_date = start_date + timedelta(days=i*3)
            
            # 生成红球号码（1-33中选6个不重复）
            red_balls = sorted(random.sample(range(1, 34), 6))
            
            # 生成蓝球号码（1-16中选1个）
            blue_ball = random.randint(1, 16)
            
            # 检查是否已存在相同期号
            if not LotteryResult.objects.filter(issue=issue).exists():
                try:
                    lottery_result = LotteryResult.objects.create(
                        issue=issue,
                        draw_date=draw_date,
                        red_ball_1=red_balls[0],
                        red_ball_2=red_balls[1],
                        red_ball_3=red_balls[2],
                        red_ball_4=red_balls[3],
                        red_ball_5=red_balls[4],
                        red_ball_6=red_balls[5],
                        blue_ball=blue_ball
                    )
                    created_count += 1
                    
                    if created_count % 20 == 0:
                        self.stdout.write(f'  ✅ 已创建 {created_count} 条记录')
                        
                except Exception as e:
                    self.stdout.write(
                        self.style.WARNING(f'  ⚠️  跳过期号 {issue}: {str(e)}')
                    )
        
        self.stdout.write(self.style.SUCCESS(f'✅ 开奖数据导入完成! 共创建 {created_count} 条记录'))
        
        # 生成统计数据
        self.stdout.write('\n📈 生成统计分析数据...')
        self.generate_statistics()
        
        self.stdout.write(self.style.SUCCESS('\n🎉 样例数据导入完成!'))
        self.stdout.write('💡 现在可以：')
        self.stdout.write('   - 访问 http://127.0.0.1:8001/api/v1/results/ 查看开奖数据')
        self.stdout.write('   - 访问 http://127.0.0.1:8001/api/v1/statistics/ 查看统计数据') 
        self.stdout.write('   - 访问 http://127.0.0.1:8001/api/docs/ 查看API文档')
        
    def generate_statistics(self):
        """生成统计分析数据"""
        # 清空现有统计数据
        Statistics.objects.all().delete()
        
        # 统计红球（1-33）
        for ball_num in range(1, 34):
            appear_count = 0
            last_issue = None
            
            # 统计每个红球的出现次数
            for result in LotteryResult.objects.all():
                red_balls = result.get_red_balls()
                if ball_num in red_balls:
                    appear_count += 1
                    last_issue = result.issue
            
            # 计算平均间隔（简化计算）
            avg_interval = round(LotteryResult.objects.count() / max(appear_count, 1), 2)
            
            Statistics.objects.create(
                ball_number=ball_num,
                ball_type='red',
                appear_count=appear_count,
                last_appear_issue=last_issue,
                max_interval=random.randint(5, 30),  # 模拟数据
                avg_interval=avg_interval
            )
        
        # 统计蓝球（1-16）
        for ball_num in range(1, 17):
            appear_count = LotteryResult.objects.filter(blue_ball=ball_num).count()
            last_result = LotteryResult.objects.filter(blue_ball=ball_num).first()
            last_issue = last_result.issue if last_result else None
            
            # 计算平均间隔（简化计算）
            avg_interval = round(LotteryResult.objects.count() / max(appear_count, 1), 2)
            
            Statistics.objects.create(
                ball_number=ball_num,
                ball_type='blue',
                appear_count=appear_count,
                last_appear_issue=last_issue,
                max_interval=random.randint(3, 20),  # 模拟数据
                avg_interval=avg_interval
            )
        
        self.stdout.write(self.style.SUCCESS(f'✅ 统计数据生成完成! 红球33个 + 蓝球16个 = 49条统计记录')) 