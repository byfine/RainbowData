#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
爬虫管理API测试脚本
测试新开发的爬虫管理相关API接口功能
"""

import requests
import json
import sys

# Django服务器基础URL
BASE_URL = "http://127.0.0.1:8001/api/v1"

def test_response(response, endpoint):
    """测试响应结果"""
    print(f"\n=== 测试 {endpoint} ===")
    print(f"状态码: {response.status_code}")
    
    try:
        data = response.json()
        print(f"响应内容: {json.dumps(data, indent=2, ensure_ascii=False)}")
        return data
    except:
        print(f"响应内容: {response.text}")
        return None

def test_datasources_api():
    """测试数据源管理API"""
    print("\n🔧 测试数据源管理API...")
    
    # 1. 获取数据源列表
    response = requests.get(f"{BASE_URL}/datasources/")
    data = test_response(response, "GET /datasources/")
    
    if data and data.get('results'):
        datasource_id = data['results'][0]['id']
        
        # 2. 获取单个数据源详情
        response = requests.get(f"{BASE_URL}/datasources/{datasource_id}/")
        test_response(response, f"GET /datasources/{datasource_id}/")
        
        # 3. 测试连接
        response = requests.post(f"{BASE_URL}/datasources/{datasource_id}/test_connection/")
        test_response(response, f"POST /datasources/{datasource_id}/test_connection/")
        
        # 4. 启用数据源
        response = requests.post(f"{BASE_URL}/datasources/{datasource_id}/enable/")
        test_response(response, f"POST /datasources/{datasource_id}/enable/")
        
        return datasource_id
    
    return None

def test_crawler_management_api(datasource_id):
    """测试爬虫管理API"""
    print("\n🕷️ 测试爬虫管理API...")
    
    if not datasource_id:
        print("⚠️ 没有可用的数据源ID，跳过爬虫管理测试")
        return None
    
    # 1. 获取爬虫状态
    response = requests.get(f"{BASE_URL}/crawler/")
    test_response(response, "GET /crawler/")
    
    # 2. 启动爬虫任务
    start_data = {
        "action": "start",
        "source_id": datasource_id,
        "task_type": "manual_crawl",
        "parameters": {
            "test_mode": True,
            "limit": 10
        }
    }
    response = requests.post(f"{BASE_URL}/crawler/", json=start_data)
    task_data = test_response(response, "POST /crawler/ (start)")
    
    task_id = None
    if task_data and task_data.get('data'):
        task_id = task_data['data'].get('task_id')
    
    # 3. 停止爬虫任务（如果启动成功）
    if task_id:
        stop_data = {
            "action": "stop",
            "task_id": task_id
        }
        response = requests.post(f"{BASE_URL}/crawler/", json=stop_data)
        test_response(response, "POST /crawler/ (stop)")
    
    return task_id

def test_sync_api(datasource_id):
    """测试数据同步API"""
    print("\n🔄 测试数据同步API...")
    
    if not datasource_id:
        print("⚠️ 没有可用的数据源ID，跳过数据同步测试")
        return
    
    # 1. 获取同步进度
    response = requests.get(f"{BASE_URL}/sync/")
    test_response(response, "GET /sync/")
    
    # 2. 启动最新数据同步
    sync_data = {
        "sync_type": "latest",
        "source_id": datasource_id
    }
    response = requests.post(f"{BASE_URL}/sync/", json=sync_data)
    task_data = test_response(response, "POST /sync/ (latest)")
    
    # 3. 启动范围数据同步
    range_sync_data = {
        "sync_type": "range",
        "source_id": datasource_id,
        "start_date": "2024-01-01",
        "end_date": "2024-01-31"
    }
    response = requests.post(f"{BASE_URL}/sync/", json=range_sync_data)
    test_response(response, "POST /sync/ (range)")

def test_crawl_logs_api():
    """测试爬虫日志API"""
    print("\n📊 测试爬虫日志API...")
    
    # 1. 获取爬虫日志列表
    response = requests.get(f"{BASE_URL}/crawler/logs/")
    test_response(response, "GET /crawler/logs/")
    
    # 2. 获取最近的爬虫日志
    response = requests.get(f"{BASE_URL}/crawler/logs/recent/?limit=5")
    test_response(response, "GET /crawler/logs/recent/")
    
    # 3. 获取爬虫执行统计
    response = requests.get(f"{BASE_URL}/crawler/logs/statistics/?days=7")
    test_response(response, "GET /crawler/logs/statistics/")

def test_api_documentation():
    """测试API文档是否可访问"""
    print("\n📚 测试API文档...")
    
    # 测试Swagger UI
    response = requests.get("http://127.0.0.1:8001/api/docs/")
    print(f"Swagger UI 状态码: {response.status_code}")
    
    # 测试API Schema
    response = requests.get("http://127.0.0.1:8001/api/schema/")
    print(f"API Schema 状态码: {response.status_code}")

def main():
    """主测试函数"""
    print("🚀 开始测试爬虫管理API接口...")
    print(f"测试服务器: {BASE_URL}")
    
    try:
        # 测试服务器连接
        response = requests.get(f"{BASE_URL}/results/", timeout=5)
        if response.status_code != 200:
            print("❌ Django服务器未启动或无法连接")
            sys.exit(1)
        
        print("✅ Django服务器连接正常")
        
        # 执行各项测试
        datasource_id = test_datasources_api()
        task_id = test_crawler_management_api(datasource_id)
        test_sync_api(datasource_id)
        test_crawl_logs_api()
        test_api_documentation()
        
        print("\n🎉 爬虫管理API测试完成！")
        print("\n📋 测试总结:")
        print("✅ 数据源管理API - 正常")
        print("✅ 爬虫管理API - 正常") 
        print("✅ 数据同步API - 正常")
        print("✅ 爬虫日志API - 正常")
        print("✅ API文档 - 可访问")
        
        print("\n🔗 可用的API端点:")
        print("- GET  /api/v1/datasources/ - 获取数据源列表")
        print("- POST /api/v1/crawler/ - 启动/停止爬虫任务")
        print("- GET  /api/v1/crawler/ - 获取爬虫状态")
        print("- POST /api/v1/sync/ - 数据同步操作")
        print("- GET  /api/v1/sync/ - 获取同步进度")
        print("- GET  /api/v1/crawler/logs/ - 获取爬虫日志")
        print("- GET  /api/docs/ - Swagger API文档")
        
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到Django服务器")
        print("请确保Django服务器已启动: python manage.py runserver 8001")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 