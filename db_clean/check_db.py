#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查数据库中仿真机的实际数据
"""

import psycopg2
import json
from decimal import Decimal

DB_CONFIG = {
    'host': '10.0.4.13',
    'database': 'LS_chuangqi',
    'user': 'postgres',
    'password': '123456789',
    'port': 5433
}

def convert_decimal_to_float(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    elif isinstance(obj, dict):
        return {key: convert_decimal_to_float(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_decimal_to_float(item) for item in obj]
    else:
        return obj

def main():
    conn = None
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        # 检查表是否存在
        cur.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'real_time_simulator_1109'
            );
        """)
        table_exists = cur.fetchone()[0]
        print(f"表 real_time_simulator_1109 存在: {table_exists}")
        
        if not table_exists:
            print("表不存在，检查其他可能的表名...")
            cur.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name LIKE '%sim%'
            """)
            tables = cur.fetchall()
            print(f"找到相关表: {[t[0] for t in tables]}")
            return
        
        # 查询总记录数
        cur.execute("SELECT COUNT(*) FROM real_time_simulator_1109")
        total = cur.fetchone()[0]
        print(f"\n总记录数: {total}")
        
        # 查询前10条记录，查看CPU相关字段
        cur.execute("""
            SELECT 
                id, model, manufacturer,
                cpu_brand, cpu_series, cpu_model_code,
                cpu_cores, cpu_frequency_value, cpu_frequency_unit,
                memory_capacity, storage_capacity, chassis_slots
            FROM real_time_simulator_1109
            LIMIT 10
        """)
        
        rows = cur.fetchall()
        columns = [desc[0] for desc in cur.description]
        
        print("\n前10条记录的CPU相关信息:")
        for i, row in enumerate(rows, 1):
            print(f"\n记录 {i}:")
            for j, col in enumerate(columns):
                value = row[j]
                if isinstance(value, Decimal):
                    value = float(value)
                print(f"  {col}: {value}")
        
        # 统计CPU品牌
        cur.execute("""
            SELECT cpu_brand, COUNT(*) 
            FROM real_time_simulator_1109 
            WHERE cpu_brand IS NOT NULL
            GROUP BY cpu_brand
        """)
        brands = cur.fetchall()
        print("\n\nCPU品牌统计:")
        for brand, count in brands:
            print(f"  {brand}: {count}")
        
        # 统计CPU系列
        cur.execute("""
            SELECT cpu_series, COUNT(*) 
            FROM real_time_simulator_1109 
            WHERE cpu_series IS NOT NULL
            GROUP BY cpu_series
        """)
        series = cur.fetchall()
        print("\nCPU系列统计:")
        for s, count in series:
            print(f"  {s}: {count}")
        
        # 统计CPU型号代码（包含i9的）
        cur.execute("""
            SELECT cpu_model_code, COUNT(*) 
            FROM real_time_simulator_1109 
            WHERE cpu_model_code IS NOT NULL 
            AND LOWER(cpu_model_code) LIKE '%i9%'
            GROUP BY cpu_model_code
        """)
        models = cur.fetchall()
        print("\n包含'i9'的CPU型号:")
        for model, count in models:
            print(f"  {model}: {count}")
        
        # 查询满足部分条件的记录
        print("\n\n查询满足部分条件的记录（CPU核心数>=8）:")
        cur.execute("""
            SELECT 
                id, model, manufacturer,
                cpu_brand, cpu_series, cpu_model_code,
                cpu_cores, cpu_frequency_value, cpu_frequency_unit,
                memory_capacity, storage_capacity, chassis_slots
            FROM real_time_simulator_1109
            WHERE cpu_cores >= 8
            LIMIT 5
        """)
        rows = cur.fetchall()
        for i, row in enumerate(rows, 1):
            print(f"\n记录 {i}:")
            for j, col in enumerate(columns):
                value = row[j]
                if isinstance(value, Decimal):
                    value = float(value)
                print(f"  {col}: {value}")
        
        cur.close()
        
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    main()

