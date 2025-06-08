#!/usr/bin/env python
"""
彩虹数据API测试脚本
"""
import requests
import json

# API基础URL
BASE_URL = 'http://127.0.0.1:8001'

def test_api_endpoint(endpoint, description):
    """测试API端点"""
    url = f"{BASE_URL}{endpoint}"
    print(f"\n🔍 测试: {description}")
    print(f"📡 URL: {url}")
    
    try:
        response = requests.get(url, timeout=10)
        print(f"📊 状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 响应成功!")
            if isinstance(data, dict):
                if 'results' in data:
                    print(f"📋 数据数量: {len(data['results'])}")
                elif 'data' in data:
                    print(f"📋 数据类型: {type(data['data'])}")
                print(f"📄 响应示例: {json.dumps(data, ensure_ascii=False, indent=2)[:200]}...")
            else:
                print(f"📄 响应数据: {str(data)[:200]}...")
        else:
            print(f"❌ 请求失败: {response.text[:200]}")
            
    except requests.exceptions.ConnectionError:
        print("❌ 连接失败: Django服务器可能未启动")
    except requests.exceptions.Timeout:
        print("❌ 请求超时")
    except Exception as e:
        print(f"❌ 错误: {str(e)}")

def main():
    """主测试函数"""
    print("🌈 彩虹数据API接口测试")
    print("=" * 50)
    
    # 测试API端点列表
    test_endpoints = [
        ('/api/v1/results/', '开奖结果列表'),
        ('/api/v1/results/latest/', '最新开奖结果'),
        ('/api/v1/statistics/', '统计分析数据'),
        ('/api/v1/statistics/frequency/', '号码频率统计'),
        ('/api/v1/predictions/', '预测记录'),
        ('/api/docs/', 'API文档页面'),
        ('/admin/', 'Django管理后台'),
    ]
    
    for endpoint, description in test_endpoints:
        test_api_endpoint(endpoint, description)
    
    print("\n" + "=" * 50)
    print("🎯 测试完成!")
    print("💡 提示:")
    print("  - 如果数据为空，这是正常的，因为数据库中还没有开奖数据")
    print("  - 可以访问 http://127.0.0.1:8001/api/docs/ 查看完整API文档")
    print("  - 可以访问 http://127.0.0.1:8001/admin/ 进入管理后台")

if __name__ == '__main__':
    main() 