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


def parse_output(output_data):
    """
    解析 output 字段
    支持两种格式：
    1. 字符串格式：需要解析的 JSON 字符串
    2. 对象格式：已经是字典/对象
    返回解析后的字典，如果解析失败返回空字典
    """
    # 如果已经是字典类型，直接返回
    if isinstance(output_data, dict):
        return output_data
    
    # 如果是字符串，尝试解析
    if isinstance(output_data, str):
        try:
            cleaned = clean_json_string(output_data)
            return json.loads(cleaned)
        except json.JSONDecodeError as e:
            print(f"解析 JSON 失败: {e}")
            print(f"问题内容: {output_data[:200]}...")
            return {}
    
    # 其他类型返回空字典
    return {}


def convert_json_array_to_sql_format(value):
    """
    将JSON数组格式转换为SQL数组格式
    例如: ["RS-232", "RS-422", "RS-485"] -> {"RS-232","RS-422","RS-485}
    或者: [""RS-232"", ""RS-422"", ""RS-485""] -> {"RS-232","RS-422","RS-485}
    """
    if isinstance(value, list):
        # 将列表中的每个元素转换为字符串，保留内容但用双引号括起来
        items = ['"' + str(item).strip('"\'') + '"' for item in value]
        return '{' + ','.join(items) + '}'
    elif isinstance(value, str):
        # 如果已经是字符串，尝试解析为JSON数组
        try:
            parsed = json.loads(value)
            if isinstance(parsed, list):
                items = ['"' + str(item).strip('"\'') + '"' for item in parsed]
                return '{' + ','.join(items) + '}'
        except (json.JSONDecodeError, TypeError):
            pass
        # 如果字符串是JSON数组格式，使用正则表达式提取所有元素
        # 匹配已转义的格式 [""item1"", ""item2"", ...] (CSV转义后的格式)
        # 先尝试匹配转义的双引号格式
        items = re.findall(r'""([^""]+)""', value)
        if items and value.strip().startswith('[') and value.strip().endswith(']'):
            items = ['"' + item + '"' for item in items]
            return '{' + ','.join(items) + '}'
        # 匹配标准JSON数组格式 ["item1", "item2", ...]
        items = re.findall(r'"([^"]+)"', value)
        if items and value.strip().startswith('[') and value.strip().endswith(']'):
            items = ['"' + item + '"' for item in items]
            return '{' + ','.join(items) + '}'
    return value


def clean_currency_value(value):
    """
    清理货币值，移除货币符号，只保留数字
    例如: ￥250 -> 250, ￥123.45 -> 123.45
    """
    if not value or not isinstance(value, str):
        return value

    value_str = str(value).strip()
    if not value_str:
        return value

    # 移除常见的货币符号（包括全角￥、半角¥等）
    cleaned = value_str.replace('￥', '').replace('¥', '').replace(
        '$', '').replace('€', '').replace('£', '')
    # 移除所有非数字、非小数点、非负号的字符
    cleaned = re.sub(r'[^\d\.\-]', '', cleaned)

    return cleaned if cleaned else value


def collect_all_fields(data_list):
    """
    收集所有记录中出现过的字段名，并转换为小写，排除指定字段
    """
    all_fields = set()
    for item in data_list:
        output_data = parse_output(item.get('output', {}))
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
    for idx, item in enumerate(data_list):
        # 如果没有 id 字段，使用索引+1作为 id
        row = {'id': item.get('id', str(idx + 1))}

        # 解析 output 字段
        output_data = parse_output(item.get('output', {}))

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
            # 处理列表（转换为SQL数组格式）
            elif isinstance(value, list):
                value = convert_json_array_to_sql_format(value)
            # 处理字典（转换为 JSON 字符串）
            elif isinstance(value, dict):
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


def merge_csv_files(io_file, workflow_file, output_file):
    """
    整合两个CSV文件
    io_file: IO板卡选型.csv 文件路径
    workflow_file: workflow_output.csv 文件路径
    output_file: 输出文件路径
    """
    # 读取两个CSV文件
    io_data = []
    workflow_data = []

    # 读取 IO板卡选型.csv
    with open(io_file, 'r', encoding='utf-8-sig', newline='') as f:
        reader = csv.DictReader(f)
        io_data = list(reader)

    # 读取 workflow_output.csv
    with open(workflow_file, 'r', encoding='utf-8-sig', newline='') as f:
        reader = csv.DictReader(f)
        workflow_data = list(reader)

    print(f"IO板卡选型.csv: {len(io_data)} 行")
    print(f"workflow_output.csv: {len(workflow_data)} 行")

    # 创建整合后的数据
    merged_data = []

    # 根据 id 匹配数据（workflow_output.csv 的 id 对应 IO板卡选型.csv 的行索引+1）
    for workflow_row in workflow_data:
        workflow_id = workflow_row.get('id', '')

        # 尝试将 id 转换为整数索引（id从1开始，索引从0开始）
        try:
            idx = int(workflow_id) - 1
            if 0 <= idx < len(io_data):
                io_row = io_data[idx]
            else:
                io_row = {}
        except (ValueError, TypeError):
            # 如果 id 不是数字，尝试按行号匹配
            idx = len(merged_data)
            if idx < len(io_data):
                io_row = io_data[idx]
            else:
                io_row = {}

        # 合并两行数据，IO板卡选型的数据在前，workflow_output的数据在后
        merged_row = {}
        # 需要清理货币符号的字段
        currency_fields = {'price_cny', 'total_amount_cny'}

        # 先添加 IO板卡选型.csv 的字段
        for key, value in io_row.items():
            # 转换JSON数组格式为SQL数组格式
            if isinstance(value, str) and value.strip().startswith('[') and value.strip().endswith(']'):
                value = convert_json_array_to_sql_format(value)
            # 清理货币字段的货币符号
            if key.lower() in currency_fields:
                value = clean_currency_value(value)
            merged_row[key] = value
        # 再添加 workflow_output.csv 的字段（如果字段名冲突，保留 workflow_output 的值）
        for key, value in workflow_row.items():
            # 转换JSON数组格式为SQL数组格式
            if isinstance(value, str) and value.strip().startswith('[') and value.strip().endswith(']'):
                value = convert_json_array_to_sql_format(value)
            # 清理货币字段的货币符号
            if key.lower() in currency_fields:
                value = clean_currency_value(value)
            merged_row[key] = value

        merged_data.append(merged_row)

    # 获取所有字段名（id放在第一列，然后是IO板卡选型的字段，最后是workflow_output的其他字段）
    io_fieldnames = list(io_data[0].keys()) if io_data else []
    workflow_fieldnames = list(
        workflow_data[0].keys()) if workflow_data else []

    # 合并字段名，id放在第一列
    all_fieldnames = []
    seen_fields = set()

    # 首先添加 id 字段（如果存在）
    if 'id' in workflow_fieldnames:
        all_fieldnames.append('id')
        seen_fields.add('id')

    # 然后添加 IO板卡选型的字段（排除 id，如果存在）
    for field in io_fieldnames:
        if field not in seen_fields:
            all_fieldnames.append(field)
            seen_fields.add(field)

    # 最后添加 workflow_output 的其他字段（排除 id）
    for field in workflow_fieldnames:
        if field not in seen_fields:
            all_fieldnames.append(field)
            seen_fields.add(field)

    # 写入整合后的CSV文件
    with open(output_file, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=all_fieldnames)
        writer.writeheader()
        writer.writerows(merged_data)

    print(f"整合后的CSV文件已生成: {output_file}")
    print(f"共 {len(merged_data)} 行数据，{len(all_fieldnames)} 个字段")


if __name__ == '__main__':
    # 设置输入和输出文件路径
    script_dir = Path(__file__).parent
    input_file = script_dir / 'workflow_output.json'
    output_file = script_dir / 'workflow_output.csv'
    output_file_1109 = script_dir / 'workflow_output_1109_v3.csv'

    # 处理文件
    process_workflow_output(input_file, output_file)





    # 整合两个CSV文件
    io_file = script_dir / 'IO板卡选型——extend.csv'
    workflow_file = script_dir / 'workflow_output.csv'
    merge_csv_files(io_file, workflow_file, output_file_1109)
