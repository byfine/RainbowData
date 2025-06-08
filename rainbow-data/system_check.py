#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
彩虹数据系统状态检查脚本
用于验证Django后端和Vue.js前端服务的运行状态
"""

import requests
import json
from datetime import datetime

def check_django_api():
    """检查Django API服务状态"""
    print("🔧 检查Django后端API服务...")
    
    # 检查基础API端点
    api_endpoints = [
        'http://127.0.0.1:8001/api/v1/results/',
        'http://127.0.0.1:8001/api/v1/statistics/frequency/',
        'http://127.0.0.1:8001/api/v1/predictions/accuracy/',
    ]
    
    results = {}
    
    for url in api_endpoints:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                results[url] = {
                    'status': '✅ 正常',
                    'response_time': f"{response.elapsed.total_seconds():.3f}s",
                    'data_count': len(data) if isinstance(data, list) else '1'
                }
            else:
                results[url] = {
                    'status': f'❌ 错误 ({response.status_code})',
                    'response_time': f"{response.elapsed.total_seconds():.3f}s",
                    'data_count': '0'
                }
        except requests.exceptions.RequestException as e:
            results[url] = {
                'status': f'❌ 连接失败: {str(e)}',
                'response_time': 'N/A',
                'data_count': '0'
            }
    
    return results

def check_vue_frontend():
    """检查Vue.js前端服务状态"""
    print("🎨 检查Vue.js前端服务...")
    
    try:
        response = requests.get('http://localhost:5173/', timeout=5)
        if response.status_code == 200:
            return {
                'status': '✅ 正常',
                'response_time': f"{response.elapsed.total_seconds():.3f}s",
                'content_length': len(response.text)
            }
        else:
            return {
                'status': f'❌ 错误 ({response.status_code})',
                'response_time': f"{response.elapsed.total_seconds():.3f}s",
                'content_length': 0
            }
    except requests.exceptions.RequestException as e:
        return {
            'status': f'❌ 连接失败: {str(e)}',
            'response_time': 'N/A',
            'content_length': 0
        }

def main():
    """主函数"""
    print("🌈 彩虹数据系统状态检查")
    print("=" * 50)
    print(f"检查时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 检查Django后端
    django_results = check_django_api()
    print("📊 Django后端API状态:")
    for url, result in django_results.items():
        endpoint = url.split('/')[-2] if url.endswith('/') else url.split('/')[-1]
        print(f"  {endpoint:20} | {result['status']:15} | {result['response_time']:8} | 数据量: {result['data_count']}")
    
    print()
    
    # 检查Vue.js前端
    vue_result = check_vue_frontend()
    print("🎨 Vue.js前端状态:")
    print(f"  前端界面          | {vue_result['status']:15} | {vue_result['response_time']:8} | 内容: {vue_result['content_length']} bytes")
    
    print()
    print("=" * 50)
    
    # 总结
    django_ok = all('✅' in result['status'] for result in django_results.values())
    vue_ok = '✅' in vue_result['status']
    
    if django_ok and vue_ok:
        print("🎉 系统状态：全部服务正常运行！")
        print("💡 您可以访问以下地址：")
        print("   - 前端界面: http://localhost:5173/")
        print("   - API文档: http://127.0.0.1:8001/api/docs/")
    elif django_ok:
        print("⚠️  系统状态：后端正常，前端需要检查")
    elif vue_ok:
        print("⚠️  系统状态：前端正常，后端需要检查")  
    else:
        print("❌ 系统状态：服务需要启动")
        print("💡 请检查：")
        print("   - Django服务器: python manage.py runserver 127.0.0.1:8001")
        print("   - Vue.js服务器: npm run dev")

if __name__ == "__main__":
    main() 