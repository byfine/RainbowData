from django.shortcuts import render
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from django.contrib.auth import login, logout
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count, Q, Max, Min, Avg
from django.utils import timezone
from datetime import datetime, timedelta
import json
import uuid
import logging
from django.core.management import call_command

from .models import LotteryResult, Statistics, Prediction, UserAnalysisLog, UserProfile, DataSource, CrawlLog
from .serializers import (
    LotteryResultSerializer, LotteryResultCreateSerializer,
    StatisticsSerializer, PredictionSerializer, PredictionCreateSerializer,
    UserAnalysisLogSerializer, UserSerializer, UserRegistrationSerializer,
    UserLoginSerializer, ChangePasswordSerializer, UserProfileSerializer,
    DataSourceSerializer, DataSourceCreateSerializer, CrawlLogSerializer, CrawlLogCreateSerializer
)


class LotteryResultViewSet(viewsets.ModelViewSet):
    """开奖结果API视图集"""
    queryset = LotteryResult.objects.all()
    serializer_class = LotteryResultSerializer
    permission_classes = [AllowAny]  # 开奖数据公开访问
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['issue', 'draw_date']
    search_fields = ['issue']
    ordering_fields = ['draw_date', 'issue', 'created_at']
    ordering = ['-draw_date', '-issue']

    def get_serializer_class(self):
        """根据动作选择序列化器"""
        if self.action in ['create', 'update', 'partial_update']:
            return LotteryResultCreateSerializer
        return LotteryResultSerializer

    @action(detail=False, methods=['get'])
    def latest(self, request):
        """获取最新开奖结果"""
        try:
            latest_result = self.queryset.first()
            if latest_result:
                serializer = self.get_serializer(latest_result)
                return Response({
                    'code': 200,
                    'message': '获取成功',
                    'data': serializer.data
                })
            return Response({
                'code': 404,
                'message': '暂无开奖数据',
                'data': None
            })
        except Exception as e:
            return Response({
                'code': 500,
                'message': f'服务器错误: {str(e)}',
                'data': None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'])
    def recent(self, request):
        """获取最近N期开奖结果"""
        try:
            limit = int(request.query_params.get('limit', 10))
            limit = min(max(limit, 1), 100)  # 限制在1-100之间
            
            recent_results = self.queryset[:limit]
            serializer = self.get_serializer(recent_results, many=True)
            
            return Response({
                'code': 200,
                'message': '获取成功',
                'data': {
                    'results': serializer.data,
                    'count': len(serializer.data)
                }
            })
        except ValueError:
            return Response({
                'code': 400,
                'message': 'limit参数必须是有效的数字',
                'data': None
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'code': 500,
                'message': f'服务器错误: {str(e)}',
                'data': None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'])
    def date_range(self, request):
        """按日期范围查询开奖结果"""
        try:
            start_date = request.query_params.get('start_date')
            end_date = request.query_params.get('end_date')
            
            if not start_date or not end_date:
                return Response({
                    'code': 400,
                    'message': '请提供start_date和end_date参数 (格式: YYYY-MM-DD)',
                    'data': None
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # 验证日期格式
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
            
            results = self.queryset.filter(draw_date__range=[start_date, end_date])
            serializer = self.get_serializer(results, many=True)
            
            return Response({
                'code': 200,
                'message': '查询成功',
                'data': {
                    'results': serializer.data,
                    'count': len(serializer.data),
                    'date_range': {
                        'start_date': start_date.strftime('%Y-%m-%d'),
                        'end_date': end_date.strftime('%Y-%m-%d')
                    }
                }
            })
        except ValueError as e:
            return Response({
                'code': 400,
                'message': f'日期格式错误: {str(e)}',
                'data': None
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'code': 500,
                'message': f'服务器错误: {str(e)}',
                'data': None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class StatisticsViewSet(viewsets.ModelViewSet):
    """统计分析API视图集"""
    queryset = Statistics.objects.all()
    serializer_class = StatisticsSerializer
    permission_classes = [AllowAny]  # 统计数据公开访问
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['ball_type', 'ball_number']
    ordering_fields = ['appear_count', 'ball_number', 'max_interval', 'avg_interval']
    ordering = ['ball_type', 'ball_number']

    @action(detail=False, methods=['get'])
    def frequency(self, request):
        """号码频率统计"""
        try:
            ball_type = request.query_params.get('ball_type', 'all')
            
            if ball_type == 'all':
                queryset = self.queryset.all()
            elif ball_type in ['red', 'blue']:
                queryset = self.queryset.filter(ball_type=ball_type)
            else:
                return Response({
                    'code': 400,
                    'message': 'ball_type参数必须是 red、blue 或 all',
                    'data': None
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # 按出现次数降序排列
            queryset = queryset.order_by('-appear_count', 'ball_number')
            serializer = self.get_serializer(queryset, many=True)
            
            return Response({
                'code': 200,
                'message': '获取成功',
                'data': {
                    'statistics': serializer.data,
                    'summary': {
                        'total_count': queryset.count(),
                        'ball_type': ball_type
                    }
                }
            })
        except Exception as e:
            return Response({
                'code': 500,
                'message': f'服务器错误: {str(e)}',
                'data': None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'])
    def hot_cold(self, request):
        """冷热号码分析"""
        try:
            ball_type = request.query_params.get('ball_type', 'red')
            limit = int(request.query_params.get('limit', 5))
            
            if ball_type not in ['red', 'blue']:
                return Response({
                    'code': 400,
                    'message': 'ball_type参数必须是 red 或 blue',
                    'data': None
                }, status=status.HTTP_400_BAD_REQUEST)
            
            queryset = self.queryset.filter(ball_type=ball_type)
            
            # 热号（出现次数最多）
            hot_numbers = queryset.order_by('-appear_count')[:limit]
            
            # 冷号（出现次数最少）
            cold_numbers = queryset.order_by('appear_count')[:limit]
            
            hot_serializer = self.get_serializer(hot_numbers, many=True)
            cold_serializer = self.get_serializer(cold_numbers, many=True)
            
            return Response({
                'code': 200,
                'message': '分析完成',
                'data': {
                    'hot_numbers': hot_serializer.data,
                    'cold_numbers': cold_serializer.data,
                    'ball_type': ball_type,
                    'limit': limit
                }
            })
        except ValueError:
            return Response({
                'code': 400,
                'message': 'limit参数必须是有效的数字',
                'data': None
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'code': 500,
                'message': f'服务器错误: {str(e)}',
                'data': None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['post'])
    def refresh(self, request):
        """刷新统计数据"""
        try:
            # 重新生成统计数据
            call_command('update_statistics')
            
            return Response({
                'code': 200,
                'message': '统计数据刷新成功',
                'data': None
            })
        except Exception as e:
            return Response({
                'code': 500,
                'message': f'统计数据刷新失败: {str(e)}',
                'data': None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'])
    def consecutive_analysis(self, request):
        """连号分析 - 分析连续号码出现情况"""
        try:
            # 获取最近N期数据
            limit = int(request.query_params.get('limit', 100))
            results = LotteryResult.objects.order_by('-draw_date')[:limit]
            
            consecutive_stats = {
                'two_consecutive': 0,  # 两连号
                'three_consecutive': 0,  # 三连号
                'four_consecutive': 0,  # 四连号或更多
                'total_periods': limit,
                'consecutive_patterns': []
            }
            
            for result in results:
                red_balls = [result.red_ball_1, result.red_ball_2, result.red_ball_3, 
                           result.red_ball_4, result.red_ball_5, result.red_ball_6]
                red_balls.sort()
                
                # 检查连号情况
                consecutive_count = 1
                max_consecutive = 1
                consecutive_groups = []
                current_group = [red_balls[0]]
                
                for i in range(1, len(red_balls)):
                    if red_balls[i] == red_balls[i-1] + 1:
                        consecutive_count += 1
                        current_group.append(red_balls[i])
                    else:
                        if len(current_group) >= 2:
                            consecutive_groups.append(current_group.copy())
                        max_consecutive = max(max_consecutive, consecutive_count)
                        consecutive_count = 1
                        current_group = [red_balls[i]]
                
                # 处理最后一组
                if len(current_group) >= 2:
                    consecutive_groups.append(current_group.copy())
                    max_consecutive = max(max_consecutive, consecutive_count)
                
                # 统计连号类型
                for group in consecutive_groups:
                    if len(group) == 2:
                        consecutive_stats['two_consecutive'] += 1
                    elif len(group) == 3:
                        consecutive_stats['three_consecutive'] += 1
                    elif len(group) >= 4:
                        consecutive_stats['four_consecutive'] += 1
                
                # 记录连号模式
                if consecutive_groups:
                    consecutive_stats['consecutive_patterns'].append({
                        'issue': result.issue,
                        'draw_date': result.draw_date.strftime('%Y-%m-%d'),
                        'red_balls': red_balls,
                        'consecutive_groups': consecutive_groups
                    })
            
            # 计算概率
            consecutive_stats['probabilities'] = {
                'two_consecutive': round(consecutive_stats['two_consecutive'] / limit * 100, 2),
                'three_consecutive': round(consecutive_stats['three_consecutive'] / limit * 100, 2),
                'four_consecutive': round(consecutive_stats['four_consecutive'] / limit * 100, 2)
            }
            
            return Response({
                'code': 200,
                'message': '连号分析完成',
                'data': consecutive_stats
            })
            
        except Exception as e:
            return Response({
                'code': 500,
                'message': f'连号分析失败: {str(e)}',
                'data': None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'])
    def ac_value_analysis(self, request):
        """AC值分析 - 分析号码组合的离散程度"""
        try:
            # AC值：号码组合中任意两个数字差值的个数（去重后）
            limit = int(request.query_params.get('limit', 100))
            results = LotteryResult.objects.order_by('-draw_date')[:limit]
            
            ac_stats = {
                'ac_distribution': {},  # AC值分布
                'average_ac': 0,
                'max_ac': 0,
                'min_ac': 99,
                'total_periods': limit,
                'ac_details': []
            }
            
            total_ac = 0
            
            for result in results:
                red_balls = [result.red_ball_1, result.red_ball_2, result.red_ball_3, 
                           result.red_ball_4, result.red_ball_5, result.red_ball_6]
                red_balls.sort()
                
                # 计算AC值
                differences = set()
                for i in range(len(red_balls)):
                    for j in range(i + 1, len(red_balls)):
                        differences.add(abs(red_balls[i] - red_balls[j]))
                
                ac_value = len(differences)
                total_ac += ac_value
                
                # 统计AC值分布
                if ac_value in ac_stats['ac_distribution']:
                    ac_stats['ac_distribution'][ac_value] += 1
                else:
                    ac_stats['ac_distribution'][ac_value] = 1
                
                # 更新最大最小值
                ac_stats['max_ac'] = max(ac_stats['max_ac'], ac_value)
                ac_stats['min_ac'] = min(ac_stats['min_ac'], ac_value)
                
                # 记录详细信息
                ac_stats['ac_details'].append({
                    'issue': result.issue,
                    'draw_date': result.draw_date.strftime('%Y-%m-%d'),
                    'red_balls': red_balls,
                    'ac_value': ac_value,
                    'differences': sorted(list(differences))
                })
            
            # 计算平均AC值
            ac_stats['average_ac'] = round(total_ac / limit, 2)
            
            # 转换分布为百分比
            ac_stats['ac_probability'] = {}
            for ac_val, count in ac_stats['ac_distribution'].items():
                ac_stats['ac_probability'][ac_val] = round(count / limit * 100, 2)
            
            return Response({
                'code': 200,
                'message': 'AC值分析完成',
                'data': ac_stats
            })
            
        except Exception as e:
            return Response({
                'code': 500,
                'message': f'AC值分析失败: {str(e)}',
                'data': None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'])
    def span_analysis(self, request):
        """跨度分析 - 分析红球最大值与最小值的差"""
        try:
            limit = int(request.query_params.get('limit', 100))
            results = LotteryResult.objects.order_by('-draw_date')[:limit]
            
            span_stats = {
                'span_distribution': {},  # 跨度分布
                'average_span': 0,
                'max_span': 0,
                'min_span': 33,
                'total_periods': limit,
                'span_details': []
            }
            
            total_span = 0
            
            for result in results:
                red_balls = [result.red_ball_1, result.red_ball_2, result.red_ball_3, 
                           result.red_ball_4, result.red_ball_5, result.red_ball_6]
                
                # 计算跨度
                span_value = max(red_balls) - min(red_balls)
                total_span += span_value
                
                # 统计跨度分布
                if span_value in span_stats['span_distribution']:
                    span_stats['span_distribution'][span_value] += 1
                else:
                    span_stats['span_distribution'][span_value] = 1
                
                # 更新最大最小值
                span_stats['max_span'] = max(span_stats['max_span'], span_value)
                span_stats['min_span'] = min(span_stats['min_span'], span_value)
                
                # 记录详细信息
                span_stats['span_details'].append({
                    'issue': result.issue,
                    'draw_date': result.draw_date.strftime('%Y-%m-%d'),
                    'red_balls': sorted(red_balls),
                    'span_value': span_value,
                    'min_ball': min(red_balls),
                    'max_ball': max(red_balls)
                })
            
            # 计算平均跨度
            span_stats['average_span'] = round(total_span / limit, 2)
            
            # 转换分布为百分比
            span_stats['span_probability'] = {}
            for span_val, count in span_stats['span_distribution'].items():
                span_stats['span_probability'][span_val] = round(count / limit * 100, 2)
            
            return Response({
                'code': 200,
                'message': '跨度分析完成',
                'data': span_stats
            })
            
        except Exception as e:
            return Response({
                'code': 500,
                'message': f'跨度分析失败: {str(e)}',
                'data': None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'])
    def interval_analysis(self, request):
        """间隔期数分析 - 分析每个号码的出现间隔"""
        try:
            ball_number = request.query_params.get('ball_number')
            ball_type = request.query_params.get('ball_type', 'red')
            limit = int(request.query_params.get('limit', 200))
            
            if not ball_number:
                return Response({
                    'code': 400,
                    'message': '请提供ball_number参数',
                    'data': None
                }, status=status.HTTP_400_BAD_REQUEST)
            
            ball_number = int(ball_number)
            
            # 验证号码范围
            if ball_type == 'red' and not (1 <= ball_number <= 33):
                return Response({
                    'code': 400,
                    'message': '红球号码范围应在1-33之间',
                    'data': None
                }, status=status.HTTP_400_BAD_REQUEST)
            elif ball_type == 'blue' and not (1 <= ball_number <= 16):
                return Response({
                    'code': 400,
                    'message': '蓝球号码范围应在1-16之间',
                    'data': None
                }, status=status.HTTP_400_BAD_REQUEST)
            
            results = LotteryResult.objects.order_by('-draw_date')[:limit]
            
            interval_stats = {
                'ball_number': ball_number,
                'ball_type': ball_type,
                'appear_count': 0,
                'intervals': [],
                'average_interval': 0,
                'max_interval': 0,
                'min_interval': 999,
                'current_interval': 0,
                'total_periods_analyzed': limit,
                'appear_details': []
            }
            
            last_appear_position = None
            current_position = 0
            
            for result in results:
                current_position += 1
                
                # 检查号码是否出现
                ball_appeared = False
                if ball_type == 'red':
                    red_balls = [result.red_ball_1, result.red_ball_2, result.red_ball_3, 
                               result.red_ball_4, result.red_ball_5, result.red_ball_6]
                    if ball_number in red_balls:
                        ball_appeared = True
                else:  # blue
                    if result.blue_ball == ball_number:
                        ball_appeared = True
                
                if ball_appeared:
                    interval_stats['appear_count'] += 1
                    interval_stats['appear_details'].append({
                        'issue': result.issue,
                        'draw_date': result.draw_date.strftime('%Y-%m-%d'),
                        'position_from_latest': current_position
                    })
                    
                    if last_appear_position is not None:
                        interval = current_position - last_appear_position
                        interval_stats['intervals'].append(interval)
                        interval_stats['max_interval'] = max(interval_stats['max_interval'], interval)
                        interval_stats['min_interval'] = min(interval_stats['min_interval'], interval)
                    
                    last_appear_position = current_position
            
            # 计算当前间隔（距离最近一次出现的期数）
            if last_appear_position:
                interval_stats['current_interval'] = last_appear_position - 1
            else:
                interval_stats['current_interval'] = limit  # 在分析期间内未出现
            
            # 计算平均间隔
            if interval_stats['intervals']:
                interval_stats['average_interval'] = round(sum(interval_stats['intervals']) / len(interval_stats['intervals']), 2)
                interval_stats['min_interval'] = min(interval_stats['intervals'])
            else:
                interval_stats['min_interval'] = 0
            
            return Response({
                'code': 200,
                'message': '间隔期数分析完成',
                'data': interval_stats
            })
            
        except Exception as e:
            return Response({
                'code': 500,
                'message': f'间隔期数分析失败: {str(e)}',
                'data': None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'])
    def repeat_analysis(self, request):
        """重复号码分析 - 分析连续期间出现相同号码的情况"""
        try:
            limit = int(request.query_params.get('limit', 50))
            results = LotteryResult.objects.order_by('-draw_date')[:limit]
            
            repeat_stats = {
                'total_periods_analyzed': limit,
                'repeat_patterns': {
                    'one_ball_repeat': 0,    # 重复1个球
                    'two_balls_repeat': 0,   # 重复2个球
                    'three_balls_repeat': 0, # 重复3个球
                    'more_balls_repeat': 0   # 重复4个或更多球
                },
                'repeat_details': [],
                'no_repeat_periods': 0
            }
            
            results_list = list(results)
            
            for i in range(len(results_list) - 1):
                current_result = results_list[i]
                next_result = results_list[i + 1]
                
                # 获取红球号码
                current_red = set([current_result.red_ball_1, current_result.red_ball_2, current_result.red_ball_3, 
                                 current_result.red_ball_4, current_result.red_ball_5, current_result.red_ball_6])
                next_red = set([next_result.red_ball_1, next_result.red_ball_2, next_result.red_ball_3, 
                              next_result.red_ball_4, next_result.red_ball_5, next_result.red_ball_6])
                
                # 计算重复号码
                repeated_red_balls = current_red.intersection(next_red)
                repeated_blue = current_result.blue_ball == next_result.blue_ball
                
                repeat_count = len(repeated_red_balls)
                if repeated_blue:
                    repeat_count += 1
                
                # 统计重复模式
                if repeat_count == 0:
                    repeat_stats['no_repeat_periods'] += 1
                elif repeat_count == 1:
                    repeat_stats['repeat_patterns']['one_ball_repeat'] += 1
                elif repeat_count == 2:
                    repeat_stats['repeat_patterns']['two_balls_repeat'] += 1
                elif repeat_count == 3:
                    repeat_stats['repeat_patterns']['three_balls_repeat'] += 1
                else:
                    repeat_stats['repeat_patterns']['more_balls_repeat'] += 1
                
                # 记录重复详情
                if repeat_count > 0:
                    repeat_detail = {
                        'current_issue': current_result.issue,
                        'next_issue': next_result.issue,
                        'current_date': current_result.draw_date.strftime('%Y-%m-%d'),
                        'next_date': next_result.draw_date.strftime('%Y-%m-%d'),
                        'repeated_red_balls': sorted(list(repeated_red_balls)),
                        'repeated_blue': repeated_blue,
                        'total_repeat_count': repeat_count
                    }
                    repeat_stats['repeat_details'].append(repeat_detail)
            
            # 计算概率
            total_comparisons = len(results_list) - 1
            repeat_stats['probabilities'] = {
                'no_repeat': round(repeat_stats['no_repeat_periods'] / total_comparisons * 100, 2),
                'one_ball_repeat': round(repeat_stats['repeat_patterns']['one_ball_repeat'] / total_comparisons * 100, 2),
                'two_balls_repeat': round(repeat_stats['repeat_patterns']['two_balls_repeat'] / total_comparisons * 100, 2),
                'three_balls_repeat': round(repeat_stats['repeat_patterns']['three_balls_repeat'] / total_comparisons * 100, 2),
                'more_balls_repeat': round(repeat_stats['repeat_patterns']['more_balls_repeat'] / total_comparisons * 100, 2)
            }
            
            return Response({
                'code': 200,
                'message': '重复号码分析完成',
                'data': repeat_stats
            })
            
        except Exception as e:
            return Response({
                'code': 500,
                'message': f'重复号码分析失败: {str(e)}',
                'data': None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PredictionViewSet(viewsets.ModelViewSet):
    """预测记录API视图集"""
    queryset = Prediction.objects.all()
    serializer_class = PredictionSerializer
    permission_classes = [AllowAny]  # 改为允许匿名访问
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['algorithm', 'target_issue', 'is_accurate']
    ordering_fields = ['created_at', 'confidence', 'accuracy_score']
    ordering = ['-created_at']

    def get_queryset(self):
        """返回当前登录用户的预测记录，匿名用户返回空"""
        if self.request.user.is_authenticated:
            try:
                user_profile = self.request.user.userprofile
                return Prediction.objects.filter(user=user_profile)
            except UserProfile.DoesNotExist:
                return Prediction.objects.none()
        else:
            # 匿名用户返回空查询集
            return Prediction.objects.none()

    def get_serializer_class(self):
        """根据动作选择序列化器"""
        if self.action in ['create', 'update', 'partial_update']:
            return PredictionCreateSerializer
        return PredictionSerializer

    @action(detail=False, methods=['post'])
    def generate(self, request):
        """生成娱乐预测 - 支持匿名和登录用户"""
        try:
            algorithm = request.data.get('algorithm', 'frequency')
            target_issue = request.data.get('target_issue')
            
            if not target_issue:
                return Response({
                    'code': 400,
                    'message': '请提供target_issue参数',
                    'data': None
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # 简单的娱乐预测算法（占位实现）
            import random
            
            if algorithm == 'frequency':
                # 频率统计预测 - 选择出现频率较高的号码
                red_stats = Statistics.objects.filter(ball_type='red').order_by('-appear_count')[:15]
                blue_stats = Statistics.objects.filter(ball_type='blue').order_by('-appear_count')[:8]
                
                if red_stats.count() >= 6 and blue_stats.count() >= 1:
                    predicted_red = sorted(random.sample([s.ball_number for s in red_stats], 6))
                    predicted_blue = random.choice([s.ball_number for s in blue_stats])
                    confidence = 0.15  # 娱乐性预测，置信度较低
                else:
                    # 如果统计数据不足，使用随机数
                    predicted_red = sorted(random.sample(range(1, 34), 6))
                    predicted_blue = random.randint(1, 16)
                    confidence = 0.05
            else:
                # 其他算法暂时使用随机数
                predicted_red = sorted(random.sample(range(1, 34), 6))
                predicted_blue = random.randint(1, 16)
                confidence = 0.05
            
            # 准备预测数据
            prediction_data = {
                'algorithm': algorithm,
                'target_issue': target_issue,
                'predicted_red_balls': predicted_red,
                'predicted_blue_ball': predicted_blue,
                'confidence': confidence
            }
            
            # 检查用户是否登录
            if request.user.is_authenticated:
                # 登录用户：保存到数据库，并限制50条记录
                try:
                    user_profile = request.user.userprofile
                    
                    # 保存预测记录
                    serializer = PredictionCreateSerializer(data=prediction_data)
                    if serializer.is_valid():
                        prediction = serializer.save(user=user_profile)

                        # 限制用户最多保留50条记录，删除最旧的记录
                        user_predictions = Prediction.objects.filter(user=user_profile).order_by('-created_at')
                        if user_predictions.count() > 50:
                            # 删除第51条及以后的记录
                            old_predictions = user_predictions[50:]
                            for old_pred in old_predictions:
                                old_pred.delete()

                        result_serializer = PredictionSerializer(prediction)
                        
                        return Response({
                            'code': 200,
                            'message': '娱乐预测生成成功，已保存到您的历史记录',
                            'data': result_serializer.data,
                            'user_status': 'authenticated',
                            'saved_to_history': True,
                            'disclaimer': '⚠️ 本预测仅供娱乐，不构成任何投注建议！彩票开奖完全随机，请理性对待。'
                        })
                    else:
                        return Response({
                            'code': 400,
                            'message': '预测数据验证失败',
                            'data': serializer.errors
                        }, status=status.HTTP_400_BAD_REQUEST)
                        
                except UserProfile.DoesNotExist:
                    # 用户没有profile，创建一个
                    UserProfile.objects.create(user=request.user)
                    # 递归调用自己
                    return self.generate(request)
                    
            else:
                # 匿名用户：只返回预测结果，不保存
                return Response({
                    'code': 200,
                    'message': '娱乐预测生成成功',
                    'data': {
                        'algorithm': algorithm,
                        'algorithm_display': dict(Prediction.ALGORITHM_CHOICES).get(algorithm, algorithm),
                        'target_issue': target_issue,
                        'predicted_red_balls': predicted_red,
                        'predicted_blue_ball': predicted_blue,
                        'confidence': confidence,
                        'predicted_numbers': {
                            'red_balls': predicted_red,
                            'blue_ball': predicted_blue
                        }
                    },
                    'user_status': 'anonymous',
                    'saved_to_history': False,
                    'login_hint': '登录后可保存预测历史记录，最多保留50条记录',
                    'disclaimer': '⚠️ 本预测仅供娱乐，不构成任何投注建议！彩票开奖完全随机，请理性对待。'
                })
                
        except Exception as e:
            return Response({
                'code': 500,
                'message': f'预测生成失败: {str(e)}',
                'data': None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'])
    def accuracy(self, request):
        """算法准确率统计"""
        try:
            algorithm = request.query_params.get('algorithm')
            
            if algorithm:
                queryset = self.queryset.filter(algorithm=algorithm)
            else:
                queryset = self.queryset.all()
            
            # 计算统计信息
            total_predictions = queryset.count()
            accurate_predictions = queryset.filter(is_accurate=True).count()
            
            if total_predictions > 0:
                accuracy_rate = (accurate_predictions / total_predictions) * 100
            else:
                accuracy_rate = 0
            
            # 按算法统计
            algorithm_stats = []
            for algo_choice in Prediction.ALGORITHM_CHOICES:
                algo_code, algo_name = algo_choice
                algo_queryset = self.queryset.filter(algorithm=algo_code)
                algo_total = algo_queryset.count()
                algo_accurate = algo_queryset.filter(is_accurate=True).count()
                algo_accuracy = (algo_accurate / algo_total * 100) if algo_total > 0 else 0
                
                algorithm_stats.append({
                    'algorithm': algo_code,
                    'algorithm_name': algo_name,
                    'total_predictions': algo_total,
                    'accurate_predictions': algo_accurate,
                    'accuracy_rate': round(algo_accuracy, 2)
                })
            
            return Response({
                'code': 200,
                'message': '统计完成',
                'data': {
                    'overall': {
                        'total_predictions': total_predictions,
                        'accurate_predictions': accurate_predictions,
                        'accuracy_rate': round(accuracy_rate, 2)
                    },
                    'by_algorithm': algorithm_stats,
                    'disclaimer': '⚠️ 预测准确率仅供学习参考，不代表未来预测能力！'
                }
            })
        except Exception as e:
            return Response({
                'code': 500,
                'message': f'统计失败: {str(e)}',
                'data': None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserAnalysisLogViewSet(viewsets.ModelViewSet):
    """用户分析日志API视图集"""
    queryset = UserAnalysisLog.objects.all()
    serializer_class = UserAnalysisLogSerializer
    permission_classes = [AllowAny]  # 临时设为公开，后续需要根据用户权限控制
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['analysis_type']
    ordering_fields = ['created_at']
    ordering = ['-created_at']

    @action(detail=False, methods=['get'])
    def summary(self, request):
        """分析日志统计摘要"""
        try:
            # 按分析类型统计
            type_stats = []
            for type_choice in UserAnalysisLog.ANALYSIS_TYPE_CHOICES:
                type_code, type_name = type_choice
                count = self.queryset.filter(analysis_type=type_code).count()
                type_stats.append({
                    'analysis_type': type_code,
                    'type_name': type_name,
                    'count': count
                })
            
            # 最近7天的活动统计
            seven_days_ago = timezone.now() - timedelta(days=7)
            recent_activity = self.queryset.filter(created_at__gte=seven_days_ago).count()
            
            return Response({
                'code': 200,
                'message': '统计完成',
                'data': {
                    'total_logs': self.queryset.count(),
                    'recent_activity_7days': recent_activity,
                    'by_type': type_stats
                }
            })
        except Exception as e:
            return Response({
                'code': 500,
                'message': f'统计失败: {str(e)}',
                'data': None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserRegistrationView(APIView):
    """用户注册API视图"""
    permission_classes = [AllowAny]
    
    def post(self, request):
        """用户注册"""
        try:
            serializer = UserRegistrationSerializer(data=request.data)
            
            if serializer.is_valid():
                user = serializer.save()
                
                # 生成Token
                token, created = Token.objects.get_or_create(user=user)
                
                # 返回用户信息和Token
                user_serializer = UserSerializer(user)
                
                return Response({
                    'code': 201,
                    'message': '注册成功',
                    'data': {
                        'user': user_serializer.data,
                        'token': token.key
                    }
                }, status=status.HTTP_201_CREATED)
            else:
                return Response({
                    'code': 400,
                    'message': '注册失败',
                    'data': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            return Response({
                'code': 500,
                'message': f'服务器错误: {str(e)}',
                'data': None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserLoginView(APIView):
    """用户登录API视图"""
    permission_classes = [AllowAny]
    
    def post(self, request):
        """用户登录"""
        try:
            serializer = UserLoginSerializer(data=request.data)
            
            if serializer.is_valid():
                user = serializer.validated_data['user']
                
                # 更新最后登录时间
                user.last_login = timezone.now()
                user.save()
                
                # 更新用户扩展信息中的IP地址
                try:
                    profile = user.userprofile
                    # 获取客户端IP地址
                    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
                    if x_forwarded_for:
                        ip = x_forwarded_for.split(',')[0]
                    else:
                        ip = request.META.get('REMOTE_ADDR')
                    profile.last_login_ip = ip
                    profile.save()
                except UserProfile.DoesNotExist:
                    # 如果用户扩展信息不存在，创建一个
                    UserProfile.objects.create(
                        user=user,
                        user_type='normal',
                        last_login_ip=request.META.get('REMOTE_ADDR')
                    )
                
                # 获取或创建Token
                token, created = Token.objects.get_or_create(user=user)
                
                # 返回用户信息和Token
                user_serializer = UserSerializer(user)
                
                return Response({
                    'code': 200,
                    'message': '登录成功',
                    'data': {
                        'user': user_serializer.data,
                        'token': token.key
                    }
                })
            else:
                return Response({
                    'code': 400,
                    'message': '登录失败',
                    'data': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            return Response({
                'code': 500,
                'message': f'服务器错误: {str(e)}',
                'data': None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserLogoutView(APIView):
    """用户登出API视图"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """用户登出"""
        try:
            # 删除用户的Token
            try:
                token = Token.objects.get(user=request.user)
                token.delete()
            except Token.DoesNotExist:
                pass
            
            return Response({
                'code': 200,
                'message': '登出成功',
                'data': None
            })
            
        except Exception as e:
            return Response({
                'code': 500,
                'message': f'服务器错误: {str(e)}',
                'data': None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserProfileView(APIView):
    """用户资料API视图"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """获取用户资料"""
        try:
            profile, created = UserProfile.objects.get_or_create(
                user=request.user,
                defaults={'user_type': 'normal'}
            )
            serializer = UserProfileSerializer(profile)
            
            return Response({
                'code': 200,
                'message': '获取成功',
                'data': serializer.data
            })
            
        except Exception as e:
            return Response({
                'code': 500,
                'message': f'服务器错误: {str(e)}',
                'data': None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def put(self, request):
        """更新用户资料"""
        try:
            profile, created = UserProfile.objects.get_or_create(
                user=request.user,
                defaults={'user_type': 'normal'}
            )
            
            serializer = UserProfileSerializer(
                profile, 
                data=request.data, 
                partial=True,
                context={'request': request}
            )
            
            if serializer.is_valid():
                serializer.save()
                return Response({
                    'code': 200,
                    'message': '更新成功',
                    'data': serializer.data
                })
            else:
                return Response({
                    'code': 400,
                    'message': '更新失败',
                    'data': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            return Response({
                'code': 500,
                'message': f'服务器错误: {str(e)}',
                'data': None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ChangePasswordView(APIView):
    """修改密码API视图"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """修改密码"""
        try:
            serializer = ChangePasswordSerializer(
                data=request.data,
                context={'request': request}
            )
            
            if serializer.is_valid():
                user = request.user
                user.set_password(serializer.validated_data['new_password'])
                user.save()
                
                # 删除旧的Token，强制重新登录
                try:
                    token = Token.objects.get(user=user)
                    token.delete()
                except Token.DoesNotExist:
                    pass
                
                return Response({
                    'code': 200,
                    'message': '密码修改成功，请重新登录',
                    'data': None
                })
            else:
                return Response({
                    'code': 400,
                    'message': '密码修改失败',
                    'data': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            return Response({
                'code': 500,
                'message': f'服务器错误: {str(e)}',
                'data': None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CurrentUserView(APIView):
    """当前用户信息API视图"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """获取当前登录用户信息"""
        try:
            serializer = UserSerializer(request.user)
            return Response({
                'code': 200,
                'message': '获取成功',
                'data': serializer.data
            })
            
        except Exception as e:
            return Response({
                'code': 500,
                'message': f'服务器错误: {str(e)}',
                'data': None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ====================================
# 爬虫管理相关API视图
# ====================================

class DataSourceViewSet(viewsets.ModelViewSet):
    """数据源配置API视图集"""
    queryset = DataSource.objects.all()
    serializer_class = DataSourceSerializer
    permission_classes = [AllowAny]  # 临时设为公开，后续需要管理员权限
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['source_type', 'status', 'is_enabled']
    ordering_fields = ['priority', 'name', 'last_success_time', 'created_at']
    ordering = ['priority', 'name']

    def get_serializer_class(self):
        """根据动作选择序列化器"""
        if self.action in ['create', 'update', 'partial_update']:
            return DataSourceCreateSerializer
        return DataSourceSerializer

    @action(detail=True, methods=['post'])
    def enable(self, request, pk=None):
        """启用数据源"""
        try:
            data_source = self.get_object()
            data_source.is_enabled = True
            data_source.status = 'active'
            data_source.save()
            
            serializer = self.get_serializer(data_source)
            return Response({
                'code': 200,
                'message': '数据源已启用',
                'data': serializer.data
            })
        except Exception as e:
            return Response({
                'code': 500,
                'message': f'服务器错误: {str(e)}',
                'data': None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['post'])
    def disable(self, request, pk=None):
        """停用数据源"""
        try:
            data_source = self.get_object()
            data_source.is_enabled = False
            data_source.status = 'inactive'
            data_source.save()
            
            serializer = self.get_serializer(data_source)
            return Response({
                'code': 200,
                'message': '数据源已停用',
                'data': serializer.data
            })
        except Exception as e:
            return Response({
                'code': 500,
                'message': f'服务器错误: {str(e)}',
                'data': None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['post'])
    def test_connection(self, request, pk=None):
        """测试数据源连接"""
        try:
            data_source = self.get_object()
            
            # 这里应该实现实际的连接测试逻辑
            # 目前返回模拟结果
            test_result = {
                'success': True,
                'response_time': 250,  # 毫秒
                'status_code': 200,
                'message': '连接成功'
            }
            
            return Response({
                'code': 200,
                'message': '连接测试完成',
                'data': test_result
            })
        except Exception as e:
            return Response({
                'code': 500,
                'message': f'服务器错误: {str(e)}',
                'data': None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CrawlerManagementView(APIView):
    """爬虫管理API视图"""
    permission_classes = [AllowAny]  # 临时设为公开，后续需要管理员权限

    def post(self, request):
        """启动爬虫任务"""
        try:
            action = request.data.get('action')
            
            if action == 'start':
                # 获取参数
                source_id = request.data.get('source_id')
                task_type = request.data.get('task_type', 'manual_crawl')
                parameters = request.data.get('parameters', {})
                
                if not source_id:
                    return Response({
                        'code': 400,
                        'message': '请提供数据源ID',
                        'data': None
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                # 验证数据源
                try:
                    data_source = DataSource.objects.get(id=source_id, is_enabled=True)
                except DataSource.DoesNotExist:
                    return Response({
                        'code': 404,
                        'message': '数据源不存在或已停用',
                        'data': None
                    }, status=status.HTTP_404_NOT_FOUND)
                
                # 生成任务ID
                task_id = f"crawl_{data_source.source_type}_{uuid.uuid4().hex[:8]}"
                
                # 创建爬虫日志记录
                crawl_log = CrawlLog.objects.create(
                    task_id=task_id,
                    task_type=task_type,
                    data_source=data_source,
                    parameters=parameters,
                    status='pending'
                )
                
                # 这里应该启动实际的爬虫任务（Celery异步任务）
                # 目前返回模拟结果
                crawl_log.start_execution()
                crawl_log.add_log(f'爬虫任务已启动: {task_id}')
                
                serializer = CrawlLogSerializer(crawl_log)
                return Response({
                    'code': 200,
                    'message': '爬虫任务已启动',
                    'data': serializer.data
                })
                
            elif action == 'stop':
                task_id = request.data.get('task_id')
                
                if not task_id:
                    return Response({
                        'code': 400,
                        'message': '请提供任务ID',
                        'data': None
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                try:
                    crawl_log = CrawlLog.objects.get(task_id=task_id)
                    
                    if crawl_log.status == 'running':
                        crawl_log.status = 'cancelled'
                        crawl_log.add_log('任务已被手动停止')
                        crawl_log.complete_execution(success=False, error_message='任务被手动停止')
                        
                        serializer = CrawlLogSerializer(crawl_log)
                        return Response({
                            'code': 200,
                            'message': '爬虫任务已停止',
                            'data': serializer.data
                        })
                    else:
                        return Response({
                            'code': 400,
                            'message': f'任务当前状态为 {crawl_log.get_status_display()}，无法停止',
                            'data': None
                        }, status=status.HTTP_400_BAD_REQUEST)
                        
                except CrawlLog.DoesNotExist:
                    return Response({
                        'code': 404,
                        'message': '任务不存在',
                        'data': None
                    }, status=status.HTTP_404_NOT_FOUND)
            
            else:
                return Response({
                    'code': 400,
                    'message': 'action参数必须是 start 或 stop',
                    'data': None
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            return Response({
                'code': 500,
                'message': f'服务器错误: {str(e)}',
                'data': None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get(self, request):
        """获取爬虫状态"""
        try:
            # 获取正在运行的任务
            running_tasks = CrawlLog.objects.filter(status='running')
            
            # 获取最近的任务统计
            recent_tasks = CrawlLog.objects.filter(
                created_at__gte=timezone.now() - timedelta(hours=24)
            )
            
            status_stats = {}
            for status_choice in CrawlLog.STATUS_CHOICES:
                status_key = status_choice[0]
                status_stats[status_key] = recent_tasks.filter(status=status_key).count()
            
            # 获取数据源状态
            data_sources = DataSource.objects.all()
            source_stats = {}
            for source in data_sources:
                source_stats[source.name] = {
                    'enabled': source.is_enabled,
                    'status': source.status,
                    'last_success': source.last_success_time,
                    'total_success': source.total_success_count,
                    'total_error': source.total_error_count
                }
            
            return Response({
                'code': 200,
                'message': '获取成功',
                'data': {
                    'running_tasks': CrawlLogSerializer(running_tasks, many=True).data,
                    'task_stats': status_stats,
                    'source_stats': source_stats,
                    'system_status': 'healthy'  # 可以根据实际情况计算
                }
            })
            
        except Exception as e:
            return Response({
                'code': 500,
                'message': f'服务器错误: {str(e)}',
                'data': None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CrawlLogViewSet(viewsets.ReadOnlyModelViewSet):
    """爬虫执行记录API视图集（只读）"""
    queryset = CrawlLog.objects.all()
    serializer_class = CrawlLogSerializer
    permission_classes = [AllowAny]  # 临时设为公开，后续需要管理员权限
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status', 'task_type', 'data_source']
    ordering_fields = ['created_at', 'start_time', 'end_time', 'duration_seconds']
    ordering = ['-created_at']

    @action(detail=False, methods=['get'])
    def recent(self, request):
        """获取最近的爬虫日志"""
        try:
            limit = int(request.query_params.get('limit', 20))
            limit = min(max(limit, 1), 100)  # 限制在1-100之间
            
            recent_logs = self.queryset[:limit]
            serializer = self.get_serializer(recent_logs, many=True)
            
            return Response({
                'code': 200,
                'message': '获取成功',
                'data': {
                    'logs': serializer.data,
                    'count': len(serializer.data)
                }
            })
        except ValueError:
            return Response({
                'code': 400,
                'message': 'limit参数必须是有效的数字',
                'data': None
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'code': 500,
                'message': f'服务器错误: {str(e)}',
                'data': None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """获取爬虫执行统计"""
        try:
            # 时间范围过滤
            days = int(request.query_params.get('days', 7))
            start_date = timezone.now() - timedelta(days=days)
            
            logs = self.queryset.filter(created_at__gte=start_date)
            
            # 按状态统计
            status_stats = {}
            for status_choice in CrawlLog.STATUS_CHOICES:
                status_key = status_choice[0]
                status_stats[status_key] = logs.filter(status=status_key).count()
            
            # 按任务类型统计
            type_stats = {}
            for type_choice in CrawlLog.TASK_TYPE_CHOICES:
                type_key = type_choice[0]
                type_stats[type_key] = logs.filter(task_type=type_key).count()
            
            # 按数据源统计
            source_stats = {}
            for data_source in DataSource.objects.all():
                source_stats[data_source.name] = logs.filter(data_source=data_source).count()
            
            # 成功率统计
            total_logs = logs.count()
            success_logs = logs.filter(status='success').count()
            success_rate = (success_logs / total_logs * 100) if total_logs > 0 else 0
            
            return Response({
                'code': 200,
                'message': '获取成功',
                'data': {
                    'period': f'{days}天',
                    'total_tasks': total_logs,
                    'success_rate': round(success_rate, 2),
                    'status_stats': status_stats,
                    'type_stats': type_stats,
                    'source_stats': source_stats
                }
            })
        except ValueError:
            return Response({
                'code': 400,
                'message': 'days参数必须是有效的数字',
                'data': None
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'code': 500,
                'message': f'服务器错误: {str(e)}',
                'data': None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DataSyncView(APIView):
    """数据同步API视图"""
    permission_classes = [AllowAny]  # 临时设为公开，后续需要管理员权限

    def post(self, request):
        """数据同步操作"""
        try:
            sync_type = request.data.get('sync_type')
            
            if sync_type == 'latest':
                # 同步最新数据
                source_id = request.data.get('source_id')
                
                if source_id:
                    # 指定数据源同步
                    try:
                        data_source = DataSource.objects.get(id=source_id, is_enabled=True)
                    except DataSource.DoesNotExist:
                        return Response({
                            'code': 404,
                            'message': '数据源不存在或已停用',
                            'data': None
                        }, status=status.HTTP_404_NOT_FOUND)
                    
                    # 创建同步任务
                    task_id = f"sync_latest_{data_source.source_type}_{uuid.uuid4().hex[:8]}"
                    crawl_log = CrawlLog.objects.create(
                        task_id=task_id,
                        task_type='latest_sync',
                        data_source=data_source,
                        status='pending'
                    )
                    
                    # 启动同步任务（这里应该调用实际的同步逻辑）
                    crawl_log.start_execution()
                    crawl_log.add_log('最新数据同步任务已启动')
                    
                    return Response({
                        'code': 200,
                        'message': '最新数据同步任务已启动',
                        'data': {
                            'task_id': task_id,
                            'data_source': data_source.name
                        }
                    })
                else:
                    # 所有启用的数据源同步
                    active_sources = DataSource.objects.filter(is_enabled=True)
                    task_ids = []
                    
                    for source in active_sources:
                        task_id = f"sync_latest_{source.source_type}_{uuid.uuid4().hex[:8]}"
                        crawl_log = CrawlLog.objects.create(
                            task_id=task_id,
                            task_type='latest_sync',
                            data_source=source,
                            status='pending'
                        )
                        crawl_log.start_execution()
                        crawl_log.add_log('最新数据同步任务已启动')
                        task_ids.append(task_id)
                    
                    return Response({
                        'code': 200,
                        'message': f'已启动 {len(task_ids)} 个最新数据同步任务',
                        'data': {
                            'task_ids': task_ids,
                            'source_count': len(active_sources)
                        }
                    })
                    
            elif sync_type == 'range':
                # 按时间范围同步
                source_id = request.data.get('source_id')
                start_date = request.data.get('start_date')
                end_date = request.data.get('end_date')
                
                if not source_id or not start_date or not end_date:
                    return Response({
                        'code': 400,
                        'message': '范围同步需要提供 source_id, start_date, end_date 参数',
                        'data': None
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                try:
                    data_source = DataSource.objects.get(id=source_id, is_enabled=True)
                except DataSource.DoesNotExist:
                    return Response({
                        'code': 404,
                        'message': '数据源不存在或已停用',
                        'data': None
                    }, status=status.HTTP_404_NOT_FOUND)
                
                # 验证日期格式
                try:
                    start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
                    end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
                except ValueError:
                    return Response({
                        'code': 400,
                        'message': '日期格式错误，请使用 YYYY-MM-DD 格式',
                        'data': None
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                # 创建范围同步任务
                task_id = f"sync_range_{data_source.source_type}_{uuid.uuid4().hex[:8]}"
                crawl_log = CrawlLog.objects.create(
                    task_id=task_id,
                    task_type='incremental_sync',
                    data_source=data_source,
                    target_date_range={
                        'start_date': start_date.strftime('%Y-%m-%d'),
                        'end_date': end_date.strftime('%Y-%m-%d')
                    },
                    status='pending'
                )
                
                crawl_log.start_execution()
                crawl_log.add_log(f'范围数据同步任务已启动: {start_date} ~ {end_date}')
                
                return Response({
                    'code': 200,
                    'message': '范围数据同步任务已启动',
                    'data': {
                        'task_id': task_id,
                        'data_source': data_source.name,
                        'date_range': {
                            'start_date': start_date.strftime('%Y-%m-%d'),
                            'end_date': end_date.strftime('%Y-%m-%d')
                        }
                    }
                })
            
            else:
                return Response({
                    'code': 400,
                    'message': 'sync_type参数必须是 latest 或 range',
                    'data': None
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            return Response({
                'code': 500,
                'message': f'服务器错误: {str(e)}',
                'data': None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get(self, request):
        """获取同步进度"""
        try:
            task_ids = request.query_params.get('task_ids', '').split(',')
            task_ids = [tid.strip() for tid in task_ids if tid.strip()]
            
            if not task_ids:
                # 返回所有正在进行的同步任务
                sync_tasks = CrawlLog.objects.filter(
                    task_type__in=['latest_sync', 'incremental_sync'],
                    status__in=['pending', 'running']
                )
            else:
                # 返回指定任务的进度
                sync_tasks = CrawlLog.objects.filter(task_id__in=task_ids)
            
            # 构建进度信息
            progress_data = []
            for task in sync_tasks:
                progress_info = {
                    'task_id': task.task_id,
                    'task_type': task.get_task_type_display(),
                    'data_source': task.data_source.name,
                    'status': task.get_status_display(),
                    'start_time': task.start_time,
                    'duration_seconds': task.duration_seconds,
                    'progress': self._calculate_progress(task),
                    'records_processed': {
                        'found': task.records_found,
                        'created': task.records_created,
                        'updated': task.records_updated,
                        'skipped': task.records_skipped
                    }
                }
                progress_data.append(progress_info)
            
            return Response({
                'code': 200,
                'message': '获取成功',
                'data': {
                    'tasks': progress_data,
                    'count': len(progress_data)
                }
            })
            
        except Exception as e:
            return Response({
                'code': 500,
                'message': f'服务器错误: {str(e)}',
                'data': None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _calculate_progress(self, crawl_log):
        """计算任务进度百分比"""
        if crawl_log.status == 'success':
            return 100
        elif crawl_log.status == 'failed':
            return 0
        elif crawl_log.status == 'running':
            # 基于已处理记录数估算进度
            total_processed = crawl_log.records_created + crawl_log.records_updated + crawl_log.records_skipped
            if total_processed > 0:
                return min(int(total_processed / max(crawl_log.records_found, 1) * 100), 95)
            return 10  # 运行中但未处理记录
        else:
            return 0
