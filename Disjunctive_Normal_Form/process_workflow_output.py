#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
处理 workflow_output.json 文件
1. 取消转义字符
2. 提取每个字段
3. 根据 id 生成 CSV 文件
"""

import json
import csv
import re
from pathlib import Path

# 需要排除的字段名（小写）
EXCLUDED_FIELDS = {
    'category', 'type', 'model', 'brief_description', 
    'detailed_description', 'brand', 'price_cny', 
    'quantity', 'total_amount_cny'
}


def clean_json_string(json_str):
    """
    清理 JSON 字符串，移除可能的代码块标记和转义字符
    """
    # 移除可能的 ```json 和 ``` 标记
    json_str = re.sub(r'^```json\s*', '', json_str, flags=re.MULTILINE)
    json_str = re.sub(r'```\s*$', '', json_str, flags=re.MULTILINE)
    json_str = json_str.strip()
    return json_str


def parse_output(output_str):
    """
    解析 output 字段中的 JSON 字符串
    返回解析后的字典，如果解析失败返回空字典
    """
    try:
        cleaned = clean_json_string(output_str)
        return json.loads(cleaned)
    except json.JSONDecodeError as e:
        print(f"解析 JSON 失败: {e}")
        print(f"问题内容: {output_str[:200]}...")
        return {}


def collect_all_fields(data_list):
    """
    收集所有记录中出现过的字段名，并转换为小写，排除指定字段
    """
    all_fields = set()
    for item in data_list:
        output_data = parse_output(item.get('output', ''))
        # 将所有字段名转换为小写，并排除指定字段
        all_fields.update(key.lower() for key in output_data.keys() 
                         if key.lower() not in EXCLUDED_FIELDS)
    return sorted(list(all_fields))


def process_workflow_output(input_file, output_file):
    """
    处理 workflow_output.json 文件并生成 CSV
    """
    # 读取 JSON 文件
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 获取数据列表
    data_list = data.get('qq', [])
    
    if not data_list:
        print("警告: 未找到数据列表")
        return
    
    print(f"找到 {len(data_list)} 条记录")
    
    # 收集所有字段
    all_fields = collect_all_fields(data_list)
    print(f"找到 {len(all_fields)} 个唯一字段")
    
    # 准备 CSV 数据
    csv_data = []
    for item in data_list:
        row = {'id': item.get('id', '')}
        
        # 解析 output 字段
        output_data = parse_output(item.get('output', ''))
        
        # 创建字段名映射（原始字段名 -> 小写字段名）
        field_mapping = {key.lower(): key for key in output_data.keys()}
        
        # 将所有字段添加到行中（使用小写字段名）
        for field in all_fields:
            # 找到原始字段名（如果存在）
            original_field = field_mapping.get(field, field)
            value = output_data.get(original_field, '')
            # 处理 None 值
            if value is None:
                value = ''
            # 处理布尔值
            elif isinstance(value, bool):
                value = str(value)
            # 处理列表/字典（转换为 JSON 字符串）
            elif isinstance(value, (list, dict)):
                value = json.dumps(value, ensure_ascii=False)
            row[field] = value
        
        csv_data.append(row)
    
    # 写入 CSV 文件
    fieldnames = ['id'] + all_fields
    
    with open(output_file, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(csv_data)
    
    print(f"CSV 文件已生成: {output_file}")
    print(f"共 {len(csv_data)} 行数据，{len(fieldnames)} 个字段")


if __name__ == '__main__':
    # 设置输入和输出文件路径
    script_dir = Path(__file__).parent
    input_file = script_dir / 'workflow_output.json'
    output_file = script_dir / 'workflow_output.csv'
    
    # 处理文件
    process_workflow_output(input_file, output_file)

