#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
500 Lottery Website Page Structure Analysis Script
"""
import requests
from bs4 import BeautifulSoup
import re
import sys

def analyze_c500_page():
    """Analyze 500 lottery website page structure"""
    url = "https://datachart.500.com/ssq/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Referer': 'https://datachart.500.com/'
    }
    
    print("=" * 60)
    print("500 Lottery Website Page Structure Analysis")
    print("=" * 60)
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        if response.status_code != 200:
            print(f"Request failed: {response.status_code}")
            return
            
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 1. Find all tables
        tables = soup.find_all('table')
        print(f"Found {len(tables)} tables")
        
        for table_idx, table in enumerate(tables):
            print(f"\n--- Table {table_idx + 1} ---")
            rows = table.find_all('tr')
            print(f"Rows: {len(rows)}")
            
            # Analyze first 5 rows structure
            for row_idx, row in enumerate(rows[:5]):
                cols = row.find_all(['td', 'th'])
                print(f"  Row {row_idx + 1}: {len(cols)} columns")
                
                # Show content of each column (first 15 columns only)
                for col_idx, col in enumerate(cols[:15]):
                    text = col.get_text().strip()
                    try:
                        # Check if possibly issue number
                        if re.match(r'^\d{5}$', text):
                            print(f"    Col{col_idx + 1}: {text} <- Possible issue number")
                        # Check if possibly red ball number (1-33)
                        elif re.match(r'^\d{1,2}$', text) and 1 <= int(text) <= 33:
                            print(f"    Col{col_idx + 1}: {text} <- Possible red ball")
                        # Check if possibly blue ball number (1-16)
                        elif re.match(r'^\d{1,2}$', text) and 1 <= int(text) <= 16:
                            print(f"    Col{col_idx + 1}: {text} <- Possible blue ball")
                        # Check if date
                        elif re.match(r'\d{4}-\d{2}-\d{2}', text):
                            print(f"    Col{col_idx + 1}: {text} <- Possible date")
                        elif text:
                            safe_text = text[:20].encode('ascii', 'ignore').decode('ascii')
                            print(f"    Col{col_idx + 1}: {safe_text}...")
                    except Exception as e:
                        print(f"    Col{col_idx + 1}: [parse error]")
        
        # 2. Specifically analyze lottery number data rows
        print(f"\n" + "=" * 60)
        print("Detailed Analysis of Lottery Number Data Rows")
        print("=" * 60)
        
        # Find main table that likely contains lottery data
        main_table = None
        for table in tables:
            rows = table.find_all('tr')
            if len(rows) > 10:  # Main data table should have more rows
                main_table = table
                break
        
        if main_table:
            rows = main_table.find_all('tr')
            print(f"Analyzing main table with {len(rows)} rows")
            
            # Analyze first 10 rows to find lottery number patterns
            for row_idx, row in enumerate(rows[:10]):
                cols = row.find_all('td')
                if len(cols) >= 10:  # Ensure enough columns
                    print(f"\nAnalyzing Row {row_idx + 1} (total {len(cols)} columns):")
                    
                    # Try to find 6 red balls + 1 blue ball pattern
                    possible_patterns = []
                    
                    # Pattern 1: Starting from column 2, continuous 6 red + 1 blue
                    pattern1 = []
                    for i in range(1, 8):  # Columns 2-8
                        if i < len(cols):
                            text = cols[i].get_text().strip()
                            if text.isdigit():
                                pattern1.append((i+1, int(text)))
                    
                    if len(pattern1) == 7:
                        red_balls = [x[1] for x in pattern1[:6]]
                        blue_ball = pattern1[6][1]
                        if all(1 <= x <= 33 for x in red_balls) and 1 <= blue_ball <= 16:
                            possible_patterns.append(("Pattern1(Col2-8)", red_balls, blue_ball))
                    
                    # Pattern 2: Find specific number combination patterns
                    # Lottery results usually display in specific format
                    row_text = row.get_text()
                    
                    # Find patterns like "01 05 12 18 25 28 08"
                    ball_pattern = re.findall(r'\b(\d{1,2})\b', row_text)
                    if len(ball_pattern) >= 7:
                        numbers = [int(x) for x in ball_pattern if x.isdigit()]
                        # Find possible 6 red + 1 blue combinations
                        for start_idx in range(len(numbers) - 6):
                            red_candidates = numbers[start_idx:start_idx+6]
                            if start_idx + 6 < len(numbers):
                                blue_candidate = numbers[start_idx + 6]
                                if (all(1 <= x <= 33 for x in red_candidates) and 
                                    1 <= blue_candidate <= 16 and
                                    len(set(red_candidates)) == 6):  # Red balls must be unique
                                    possible_patterns.append((f"Pattern2(Pos{start_idx})", red_candidates, blue_candidate))
                    
                    # Show found patterns
                    for pattern_name, red_balls, blue_ball in possible_patterns:
                        print(f"  {pattern_name}: Red{red_balls} Blue{blue_ball}")
                        
                        # Validate number reasonableness
                        if (len(set(red_balls)) == 6 and  # Red balls unique
                            all(1 <= x <= 33 for x in red_balls) and  # Red ball range
                            1 <= blue_ball <= 16):  # Blue ball range
                            print(f"    VALID - Data validation passed")
                        else:
                            print(f"    INVALID - Data validation failed")
                    
                    if not possible_patterns:
                        # Show raw column data for debugging
                        print(f"  Raw data: ", end="")
                        for i, col in enumerate(cols[:15]):
                            text = col.get_text().strip()
                            if text.isdigit():
                                print(f"[{i+1}:{text}]", end=" ")
                        print()
                        
    except Exception as e:
        print(f"Analysis failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    analyze_c500_page() 