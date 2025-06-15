#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Deep Analysis of 500 Lottery Website - Find Real Lottery Results
"""
import requests
from bs4 import BeautifulSoup
import re

def deep_analyze_c500_page():
    """深度分析500彩票网页面，寻找真正的开奖结果"""
    url = "https://datachart.500.com/ssq/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Referer': 'https://datachart.500.com/'
    }
    
    print("=" * 80)
    print("500彩票网深度页面分析 - 寻找真正的开奖结果")
    print("=" * 80)
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        if response.status_code != 200:
            print(f"Request failed: {response.status_code}")
            return
            
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 1. 搜索包含期号25064的所有元素
        print("\n1. 搜索包含最新期号的元素...")
        issue_elements = soup.find_all(string=re.compile(r'25064|25063|25062'))
        print(f"找到包含最新期号的元素: {len(issue_elements)}")
        
        for i, element in enumerate(issue_elements[:5]):
            parent = element.parent if element.parent else None
            if parent:
                print(f"\n元素 {i+1}:")
                print(f"  文本: {element.strip()}")
                print(f"  父标签: {parent.name}")
                print(f"  父标签class: {parent.get('class', [])}")
                print(f"  父标签id: {parent.get('id', '')}")
                
                # 查看父元素的兄弟元素
                siblings = parent.find_next_siblings()[:5]
                if siblings:
                    print(f"  后续兄弟元素:")
                    for j, sibling in enumerate(siblings):
                        text = sibling.get_text().strip()[:50]
                        print(f"    {j+1}. {sibling.name}: {text}")
        
        # 2. 搜索所有可能的数据表格
        print(f"\n" + "=" * 60)
        print("2. 分析所有表格结构...")
        tables = soup.find_all('table')
        
        for table_idx, table in enumerate(tables):
            print(f"\n--- 表格 {table_idx + 1} ---")
            
            # 获取表格的class和id
            table_class = table.get('class', [])
            table_id = table.get('id', '')
            print(f"Class: {table_class}")
            print(f"ID: {table_id}")
            
            rows = table.find_all('tr')
            print(f"行数: {len(rows)}")
            
            # 查看前几行，寻找真正的开奖数据
            for row_idx, row in enumerate(rows[:8]):
                cols = row.find_all(['td', 'th'])
                if cols:
                    print(f"\n  行 {row_idx + 1} ({len(cols)} 列):")
                    
                    # 显示所有列的内容
                    row_data = []
                    for col_idx, col in enumerate(cols[:10]):  # 只显示前10列
                        text = col.get_text().strip()
                        if text:
                            row_data.append(f"[{col_idx+1}:{text}]")
                    
                    print(f"    数据: {' '.join(row_data)}")
                    
                    # 检查是否包含期号25064和对应的红球数据
                    row_text = ' '.join([col.get_text().strip() for col in cols])
                    if '25064' in row_text:
                        print(f"    *** 发现期号25064! ***")
                        print(f"    完整行文本: {row_text}")
                        
                        # 分析这一行是否包含正确的开奖号码
                        # 用户说25064的红球是: 2, 10, 13, 22, 29, 33, 蓝球: 16
                        expected_balls = [2, 10, 13, 22, 29, 33, 16]
                        found_balls = []
                        
                        for expected in expected_balls:
                            if str(expected) in row_text:
                                found_balls.append(expected)
                        
                        print(f"    期望号码: {expected_balls}")
                        print(f"    找到号码: {found_balls}")
                        print(f"    匹配度: {len(found_balls)}/{len(expected_balls)}")
        
        # 3. 搜索特定的开奖结果区域
        print(f"\n" + "=" * 60)
        print("3. 搜索特定的开奖结果区域...")
        
        # 查找包含"开奖结果"、"历史开奖"等关键词的区域
        keywords = ['开奖结果', '历史开奖', '最新开奖', 'result', 'history']
        for keyword in keywords:
            elements = soup.find_all(string=re.compile(keyword, re.I))
            if elements:
                print(f"\n找到关键词 '{keyword}' 的元素:")
                for element in elements[:3]:
                    parent = element.parent
                    if parent:
                        print(f"  父元素: {parent.name}, class: {parent.get('class', [])}")
        
        # 4. 查找script标签中的数据
        print(f"\n" + "=" * 60)
        print("4. 查找JavaScript中的数据...")
        scripts = soup.find_all('script')
        
        for script_idx, script in enumerate(scripts):
            script_content = script.string if script.string else ""
            if script_content and ('25064' in script_content or 'ssq' in script_content.lower()):
                print(f"\nScript {script_idx + 1} 包含相关数据:")
                # 显示包含25064的行
                lines = script_content.split('\n')
                for line_idx, line in enumerate(lines):
                    if '25064' in line or ('red' in line.lower() and 'ball' in line.lower()):
                        print(f"  行 {line_idx + 1}: {line.strip()[:100]}")
        
        # 5. 查找div等容器中的数据
        print(f"\n" + "=" * 60)
        print("5. 查找div容器中的开奖数据...")
        
        # 查找可能包含开奖数据的div
        divs = soup.find_all('div')
        for div in divs:
            div_text = div.get_text()
            if '25064' in div_text:
                print(f"\n发现包含25064的div:")
                print(f"  Class: {div.get('class', [])}")
                print(f"  ID: {div.get('id', '')}")
                print(f"  文本: {div_text[:200]}")
                
    except Exception as e:
        print(f"Analysis failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    deep_analyze_c500_page() 