#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
根据sim.json中的需求，查询数据库中满足条件的仿真机
参考linprog/process_dnf.py的查询方式
"""

import json
import psycopg2
import re
from typing import List, Dict, Any
from decimal import Decimal

# 数据库配置（参考process_dnf.py）
DB_CONFIG = {
    'host': '10.0.4.13',
    'database': 'LS_chuangqi',
    'user': 'postgres',
    'password': '123456789',
    'port': 5433
}


def convert_decimal_to_float(obj: Any) -> Any:
    """递归地将数据中的 Decimal 类型转换为 float"""
    if isinstance(obj, Decimal):
        return float(obj)
    elif isinstance(obj, dict):
        return {key: convert_decimal_to_float(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_decimal_to_float(item) for item in obj]
    elif isinstance(obj, tuple):
        return tuple(convert_decimal_to_float(item) for item in obj)
    else:
        return obj


def evaluate_condition(machine: Dict[str, Any], field: str, operator: str, value: Any) -> bool:
    """
    评估单个条件是否满足
    
    Args:
        machine: 仿真机数据字典
        field: 字段名
        operator: 操作符 (>=, =, LIKE等)
        value: 需求值
    
    Returns:
        是否满足条件
    """
    machine_value = machine.get(field)
    
    if machine_value is None:
        return False
    
    # 转换为float进行比较（用于数值比较）
    def to_float(val):
        if isinstance(val, Decimal):
            return float(val)
        elif isinstance(val, (int, float)):
            return float(val)
        return None
    
    if operator == '>=':
        machine_float = to_float(machine_value)
        value_float = to_float(value)
        if machine_float is not None and value_float is not None:
            return machine_float >= value_float
        return False
    
    elif operator == '=':
        # 字符串比较（大小写不敏感）
        if isinstance(machine_value, str) and isinstance(value, str):
            return machine_value.lower() == value.lower()
        return str(machine_value).strip() == str(value).strip()
    
    elif operator == 'LIKE':
        # LIKE匹配（大小写不敏感）
        if isinstance(machine_value, str) and isinstance(value, str):
            # 将SQL LIKE模式转换为正则表达式
            pattern = value.replace('%', '.*').replace('_', '.')
            return bool(re.search(pattern, machine_value, re.IGNORECASE))
        return False
    
    return False


def calculate_match_degree(machine: Dict[str, Any], requirements: List[Dict[str, Any]]) -> int:
    """
    计算仿真机对需求的匹配度（0-100）
    
    Args:
        machine: 仿真机数据字典
        requirements: 需求列表
    
    Returns:
        匹配度（0-100的整数）
    """
    if not requirements:
        return 0
    
    total_conditions = 0
    satisfied_conditions = 0
    
    for req in requirements:
        attr = req.get('attribute', {})
        
        # CPU核心数
        if 'cpu_cores' in attr:
            total_conditions += 1
            if evaluate_condition(machine, 'cpu_cores', '>=', attr['cpu_cores']):
                satisfied_conditions += 1
        
        # CPU主频
        if 'cpu_frequency_value' in attr:
            total_conditions += 1
            freq_value = attr['cpu_frequency_value']
            freq_unit = attr.get('cpu_frequency_unit', 'GHz')
            machine_freq_value = machine.get('cpu_frequency_value')
            machine_freq_unit = machine.get('cpu_frequency_unit', 'GHz')
            
            if machine_freq_value is not None:
                # 统一转换为GHz进行比较
                if machine_freq_unit.upper() == 'MHZ':
                    machine_freq_ghz = float(machine_freq_value) / 1000.0
                else:
                    machine_freq_ghz = float(machine_freq_value)
                
                if freq_unit.upper() == 'GHZ':
                    req_freq_ghz = float(freq_value)
                else:
                    req_freq_ghz = float(freq_value) / 1000.0
                
                if machine_freq_ghz >= req_freq_ghz:
                    satisfied_conditions += 1
        
        # CPU品牌
        if 'cpu_brand' in attr:
            total_conditions += 1
            if evaluate_condition(machine, 'cpu_brand', '=', attr['cpu_brand']):
                satisfied_conditions += 1
        
        # CPU系列
        if 'cpu_series' in attr:
            total_conditions += 1
            if evaluate_condition(machine, 'cpu_series', '=', attr['cpu_series']):
                satisfied_conditions += 1
        
        # CPU型号代码
        if 'cpu_model_code' in attr:
            total_conditions += 1
            model_code_pattern = f"%{attr['cpu_model_code']}%"
            if evaluate_condition(machine, 'cpu_model_code', 'LIKE', model_code_pattern):
                satisfied_conditions += 1
        
        # 存储容量
        if 'storage_capacity' in attr:
            total_conditions += 1
            if evaluate_condition(machine, 'storage_capacity', '>=', attr['storage_capacity']):
                satisfied_conditions += 1
        
        # 内存容量
        if 'memory_capacity' in attr:
            total_conditions += 1
            if evaluate_condition(machine, 'memory_capacity', '>=', attr['memory_capacity']):
                satisfied_conditions += 1
        
        # 插槽数
        if 'chassis_slots' in attr:
            total_conditions += 1
            if evaluate_condition(machine, 'chassis_slots', '>=', attr['chassis_slots']):
                satisfied_conditions += 1
    
    if total_conditions == 0:
        return 0
    
    match_degree = int((satisfied_conditions / total_conditions) * 100)
    return match_degree


def query_all_sim_machines() -> List[Dict[str, Any]]:
    """
    查询所有仿真机数据
    
    Returns:
        所有仿真机列表
    """
    conn = None
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        query = (
            "SELECT "
            "id, category, type, model, manufacturer, "
            "quote_price, quantity, total_price, series, "
            "cpu_brand, cpu_series, cpu_model_code, "
            "cpu_cores, cpu_frequency_value, cpu_frequency_unit, cpu_threads, "
            "memory_standard, memory_technology, memory_capacity, "
            "storage_capacity, storage_type, "
            "io_slots_pci, io_slots_pcie_x1, io_slots_pcie_x4, "
            "io_slots_pcie_x8, io_slots_pcie_x16, "
            "network_ports, os, "
            "form_factor, chassis_slots, chassis_height, chassis_design, "
            "additional_features, "
            "description_simple, description_detailed, "
            "cpu, hard_disk, memory, slots "
            "FROM real_time_simulator_1109"
        )
        
        cur.execute(query)
        rows = cur.fetchall()
        
        # 获取列名
        columns = [desc[0] for desc in cur.description]
        
        # 转换为字典列表
        result = []
        for row in rows:
            machine_dict = {}
            for i, col in enumerate(columns):
                machine_dict[col] = row[i]
            result.append(machine_dict)
        
        cur.close()
        
        # 转换Decimal为float
        result = convert_decimal_to_float(result)
        
        return result
        
    except Exception as e:
        print(f"数据库查询错误: {e}")
        import traceback
        traceback.print_exc()
        return []
    finally:
        if conn:
            conn.close()


def query_sim_machines_with_scoring(requirements: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    查询所有仿真机，计算匹配度，并按匹配度降序、价格升序排序
    
    Args:
        requirements: 需求列表，每个需求包含 'original' 和 'attribute'
    
    Returns:
        带匹配度的仿真机列表，已排序
    """
    # 查询所有仿真机
    print("查询所有仿真机数据...")
    all_machines = query_all_sim_machines()
    print(f"共查询到 {len(all_machines)} 台仿真机")
    
    # 为每个仿真机计算匹配度
    print("计算匹配度...")
    machines_with_score = []
    for machine in all_machines:
        match_degree = calculate_match_degree(machine, requirements)
        machine['match_degree'] = match_degree
        machines_with_score.append(machine)
    
    # 按匹配度降序排序，匹配度相同时按价格升序排序
    machines_with_score.sort(key=lambda x: (
        -x.get('match_degree', 0),  # 匹配度降序（负数实现降序）
        x.get('quote_price') or float('inf')  # 价格升序，None视为无穷大
    ))
    
    return machines_with_score


def extract_from_description(description: str) -> Dict[str, str]:
    """
    从描述中提取cpu, hard_disk, memory, slots信息
    """
    result = {
        'cpu': None,
        'hard_disk': None,
        'memory': None,
        'slots': None
    }
    
    if not description:
        return result
    
    # 定义正则表达式模式
    regex = {
        'cpu': r'CPU[：:]\s*(.*?)(?=[；。\n]|硬盘|内存|IO扩展插槽|$)',
        'hard_disk': r'硬盘[：:]\s*(.*?)(?=[；。\n]|内存|CPU|IO扩展插槽|$)',
        'memory': r'内存[：:]\s*(.*?)(?=[；。\n]|硬盘|CPU|IO扩展插槽|$)',
        'slots': r'IO扩展插槽[：:]\s*(.*?)(?=[；。\n]|$)'
    }
    
    for key in regex:
        match = re.search(regex[key], description, re.IGNORECASE | re.DOTALL)
        if match and match.group(1):
            result[key] = match.group(1).strip()
    
    return result


def calculate_requirement_score(machine: Dict[str, Any], requirement: Dict[str, Any], category: str) -> tuple:
    """
    计算单个需求对单个仿真机的评分和原因
    
    Returns:
        (score: float/bool, reason: str)
    """
    original = requirement.get('original', '')
    attr = requirement.get('attribute', {})
    
    if category == 'CPU':
        # CPU评分逻辑
        cpu_cores_req = attr.get('cpu_cores')
        cpu_freq_req = attr.get('cpu_frequency_value')
        cpu_freq_unit_req = attr.get('cpu_frequency_unit', 'GHz')
        cpu_brand_req = attr.get('cpu_brand')
        cpu_series_req = attr.get('cpu_series')
        cpu_model_req = attr.get('cpu_model_code')
        
        machine_cores = machine.get('cpu_cores')
        machine_freq = machine.get('cpu_frequency_value')
        machine_freq_unit = machine.get('cpu_frequency_unit', 'GHz')
        machine_brand = machine.get('cpu_brand')
        machine_series = machine.get('cpu_series')
        machine_model = machine.get('cpu_model_code', '')
        
        # 计算各项得分
        scores = []
        reasons = []
        
        # 核心数
        if cpu_cores_req and machine_cores:
            if machine_cores >= cpu_cores_req:
                scores.append(1.0)
                reasons.append(f"核心数{machine_cores}核满足≥{cpu_cores_req}核")
            else:
                scores.append(0.0)
                reasons.append(f"核心数{machine_cores}核未达{cpu_cores_req}核")
        
        # 主频
        if cpu_freq_req and machine_freq:
            machine_freq_ghz = float(machine_freq) if machine_freq_unit.upper() == 'GHZ' else float(machine_freq) / 1000.0
            req_freq_ghz = float(cpu_freq_req) if cpu_freq_unit_req.upper() == 'GHZ' else float(cpu_freq_req) / 1000.0
            
            if machine_freq_ghz >= req_freq_ghz:
                scores.append(1.0)
                reasons.append(f"主频{machine_freq_ghz}GHz满足≥{req_freq_ghz}GHz")
            else:
                scores.append(0.0)
                reasons.append(f"主频{machine_freq_ghz}GHz低于{req_freq_ghz}GHz")
        
        # 品牌
        if cpu_brand_req and machine_brand:
            if evaluate_condition(machine, 'cpu_brand', '=', cpu_brand_req):
                scores.append(1.0)
                reasons.append(f"品牌{machine_brand}符合")
            else:
                scores.append(0.0)
                reasons.append(f"品牌{machine_brand}不符合{cpu_brand_req}")
        
        # 系列
        if cpu_series_req and machine_series:
            if evaluate_condition(machine, 'cpu_series', '=', cpu_series_req):
                scores.append(1.0)
                reasons.append(f"系列{machine_series}符合")
            else:
                scores.append(0.0)
                reasons.append(f"系列{machine_series}不符合{cpu_series_req}")
        
        # 型号
        if cpu_model_req and machine_model:
            if evaluate_condition(machine, 'cpu_model_code', 'LIKE', f"%{cpu_model_req}%"):
                scores.append(1.0)
                reasons.append(f"型号包含{cpu_model_req}")
            else:
                scores.append(0.0)
                reasons.append(f"型号不包含{cpu_model_req}")
        
        if scores:
            avg_score = sum(scores) / len(scores)
            # 生成更详细的原因说明
            satisfied_count = sum(1 for s in scores if s == 1.0)
            total_count = len(scores)
            
            # 构建详细原因
            reason_parts = []
            if machine_cores and cpu_cores_req:
                if machine_cores >= cpu_cores_req:
                    reason_parts.append(f"满足八核要求（{machine_cores}核）")
                else:
                    reason_parts.append(f"仅{machine_cores}核，未达八核要求")
            
            # 品牌和系列
            brand_series_ok = False
            if machine_brand and cpu_brand_req and machine_series and cpu_series_req:
                if machine_brand.lower() == cpu_brand_req.lower() and machine_series.lower() == cpu_series_req.lower():
                    brand_series_ok = True
                    reason_parts.append(f"满足Intel Core系列要求")
                elif machine_brand.lower() == cpu_brand_req.lower():
                    reason_parts.append(f"品牌{machine_brand}符合，但系列{machine_series}不符合{cpu_series_req}")
                else:
                    reason_parts.append(f"品牌{machine_brand}不符合{cpu_brand_req}")
            
            # 型号
            model_ok = False
            if machine_model and cpu_model_req:
                if cpu_model_req.lower() in machine_model.lower():
                    model_ok = True
                    reason_parts.append(f"满足i9型号要求")
                else:
                    reason_parts.append(f"型号为{machine_model}，不包含{cpu_model_req}")
            
            if machine_freq and cpu_freq_req:
                machine_freq_ghz = float(machine_freq) if machine_freq_unit.upper() == 'GHZ' else float(machine_freq) / 1000.0
                req_freq_ghz = float(cpu_freq_req) if cpu_freq_unit_req.upper() == 'GHZ' else float(cpu_freq_req) / 1000.0
                if machine_freq_ghz >= req_freq_ghz:
                    reason_parts.append(f"主频{machine_freq_ghz}GHz满足≥{req_freq_ghz}GHz要求")
                else:
                    reason_parts.append(f"主频{machine_freq_ghz}GHz低于需求的{req_freq_ghz}GHz")
            
            
            # 生成综合原因（参考用户示例格式）
            if avg_score >= 0.8:
                # 高匹配度：总结满足和不满足的项
                satisfied_summary = []
                unsatisfied_summary = []
                
                if machine_cores and cpu_cores_req and machine_cores >= cpu_cores_req:
                    satisfied_summary.append("八核")
                elif machine_cores and cpu_cores_req:
                    unsatisfied_summary.append(f"仅{machine_cores}核，未达八核")
                
                if brand_series_ok and model_ok:
                    satisfied_summary.append("Intel Core i9系列")
                elif brand_series_ok:
                    satisfied_summary.append("Intel Core系列")
                    if machine_model:
                        unsatisfied_summary.append(f"非i9系列（为{machine_model}）")
                
                if machine_freq and cpu_freq_req:
                    machine_freq_ghz = float(machine_freq) if machine_freq_unit.upper() == 'GHZ' else float(machine_freq) / 1000.0
                    req_freq_ghz = float(cpu_freq_req) if cpu_freq_unit_req.upper() == 'GHZ' else float(cpu_freq_req) / 1000.0
                    if machine_freq_ghz >= req_freq_ghz:
                        satisfied_summary.append(f"主频{machine_freq_ghz}GHz满足要求")
                    else:
                        unsatisfied_summary.append(f"主频{machine_freq_ghz}GHz低于需求的{req_freq_ghz}GHz")
                
                if satisfied_summary and unsatisfied_summary:
                    reason = f"满足{'和'.join(satisfied_summary)}要求，但{'，'.join(unsatisfied_summary)}。核心数与品牌达标，频率略低，整体接近但未完全满足。"
                elif satisfied_summary:
                    reason = f"满足{'和'.join(satisfied_summary)}要求。整体接近但未完全满足。"
                else:
                    reason = f"{'；'.join(reason_parts)}。"
            elif avg_score >= 0.5:
                reason = f"{'；'.join(reason_parts)}。部分指标达标，但关键指标不足。"
            else:
                # 低匹配度：详细列出问题
                problem_list = []
                if machine_cores and cpu_cores_req and machine_cores < cpu_cores_req:
                    problem_list.append(f"仅{machine_cores}核，远低于八核要求")
                if machine_freq and cpu_freq_req:
                    machine_freq_ghz = float(machine_freq) if machine_freq_unit.upper() == 'GHZ' else float(machine_freq) / 1000.0
                    req_freq_ghz = float(cpu_freq_req) if cpu_freq_unit_req.upper() == 'GHZ' else float(cpu_freq_req) / 1000.0
                    if machine_freq_ghz < req_freq_ghz:
                        problem_list.append(f"主频{machine_freq_ghz}GHz远低于{req_freq_ghz}GHz")
                if not brand_series_ok:
                    problem_list.append(f"非Intel Core系列" if machine_brand else "品牌不符")
                if not model_ok:
                    problem_list.append(f"非i9系列" if machine_model else "型号不符")
                
                if problem_list:
                    reason = f"{'；'.join(problem_list)}。{'多项' if len(problem_list) > 2 else '两项'}关键指标严重不达标。"
                else:
                    reason = f"{'；'.join(reason_parts)}。多项关键指标不达标。"
            
            return avg_score, reason
        return 0.0, "无法评估"
    
    elif category == 'Hard Disk':
        storage_req = attr.get('storage_capacity')
        machine_storage = machine.get('storage_capacity')
        
        if storage_req and machine_storage:
            # 1TB = 1024GB，但实际中1000GB也被认为是1TB
            # 如果需求是1024GB，那么1000GB也应该满足
            if machine_storage >= storage_req or (storage_req == 1024 and machine_storage >= 1000):
                # 格式化显示：1000GB显示为1TB，1024GB也显示为1TB
                if machine_storage >= 1000:
                    if machine_storage == 1000:
                        display = "1TB"
                    elif machine_storage >= 1024:
                        display = f"{machine_storage/1024:.1f}TB" if machine_storage % 1024 == 0 else f"{machine_storage}GB"
                    else:
                        display = f"{machine_storage}GB"
                else:
                    display = f"{machine_storage}GB"
                return 1.0, f"硬盘容量（{display}）满足要求的1TB及以上。"
            else:
                return 0.0, f"硬盘容量（{machine_storage}GB）低于要求的1TB及以上。"
        return 0.0, "无法评估"
    
    elif category == 'Memory':
        memory_req = attr.get('memory_capacity')
        machine_memory = machine.get('memory_capacity')
        
        if memory_req and machine_memory:
            if machine_memory >= memory_req:
                return 1.0, f"符合需求，内存容量为{machine_memory}GB，满足{memory_req}G及以上要求。"
            else:
                return 0.0, f"不符合需求，内存容量仅为{machine_memory}GB，未达到{memory_req}G及以上要求。"
        return 0.0, "无法评估"
    
    elif category == 'Slots':
        slots_req = attr.get('chassis_slots')
        machine_slots = machine.get('chassis_slots')
        
        # 如果没有chassis_slots，尝试从description中提取
        if machine_slots is None:
            desc = machine.get('description_simple', '') or machine.get('description_detailed', '')
            extracted = extract_from_description(desc)
            slots_str = extracted.get('slots', '')
            # 尝试从字符串中提取数字并计算总数
            if slots_str:
                # 匹配"X个"或"X槽"的模式
                import re
                # 匹配各种格式：2个PCIe x1, 8槽, 等
                patterns = [
                    r'(\d+)\s*个',  # "2个"
                    r'(\d+)\s*槽',  # "8槽"
                    r'(\d+)\s*x\d+',  # "2x4" (但这里我们只取第一个数字)
                ]
                total_slots = 0
                for pattern in patterns:
                    matches = re.findall(pattern, slots_str)
                    for match in matches:
                        num = int(match)
                        if 1 <= num <= 20:  # 合理的插槽数量范围
                            total_slots += num
                
                if total_slots > 0:
                    machine_slots = total_slots
                else:
                    # 如果没有匹配到，尝试简单数数字
                    numbers = re.findall(r'\d+', slots_str)
                    if numbers:
                        # 只取合理的数字（1-20之间）
                        valid_numbers = [int(n) for n in numbers if 1 <= int(n) <= 20]
                        if valid_numbers:
                            machine_slots = sum(valid_numbers)
        
        if slots_req and machine_slots:
            if machine_slots >= slots_req:
                if machine_slots == slots_req:
                    return 1.0, f"提供{machine_slots}个插槽，刚好满足至少{slots_req}个板卡插槽的需求"
                else:
                    return 1.0, f"提供{machine_slots}个插槽，超过所需的{slots_req}个板卡插槽"
            else:
                return 0.0, f"仅提供{machine_slots}个插槽，少于所需的{slots_req}个板卡插槽"
        elif slots_req:
            # 尝试从description中解析
            desc = machine.get('description_simple', '') or machine.get('description_detailed', '')
            extracted = extract_from_description(desc)
            slots_str = extracted.get('slots', '')
            if slots_str:
                # 简单判断：如果包含多个"个"或"槽"，可能满足
                import re
                slot_count = len(re.findall(r'\d+\s*[个槽]', slots_str))
                if slot_count >= slots_req:
                    return 1.0, f"提供多个插槽（从描述中解析），满足至少{slots_req}个板卡插槽的需求"
                else:
                    return 0.0, f"插槽数量不足（从描述中解析），未达到{slots_req}个"
        return 0.0, "无法评估"
    
    return 0.0, "未知类别"


def generate_output_format(all_machines: List[Dict[str, Any]], all_requirements: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    生成新的输出格式
    """
    # 如果需求为空，直接返回空输出
    if not all_requirements:
        return {
            'result_id': {},
            'sim_raw_data': [],
            'sim_pick_list': []
        }
    
    # 1. 为每个仿真机计算每个需求的评分
    machine_scores = {}  # {machine_id: {req_index: score}}
    
    for machine in all_machines:
        machine_id = str(machine.get('id', ''))
        machine_scores[machine_id] = {}
        total_score = 0.0
        
        for req_idx, req in enumerate(all_requirements):
            original = req.get('original', '')
            # 判断需求类别
            if 'CPU' in original or 'cpu' in original.lower():
                category = 'CPU'
            elif '硬盘' in original or 'hard' in original.lower():
                category = 'Hard Disk'
            elif '内存' in original or 'memory' in original.lower():
                category = 'Memory'
            elif '插槽' in original or 'slot' in original.lower():
                category = 'Slots'
            else:
                category = 'Unknown'
            
            score, reason = calculate_requirement_score(machine, req, category)
            machine_scores[machine_id][req_idx] = {
                'category': category,
                'score': score,
                'reason': reason
            }
            # 累计总分（统一转换为float）
            score_val = 1.0 if score is True else (0.0 if score is False else float(score))
            total_score += score_val
    
    # 2. 找到总评分最高的仿真机作为result_id
    best_machine_id = None
    best_total_score = -1
    
    for machine_id, scores_dict in machine_scores.items():
        total = sum(1.0 if s['score'] is True else (0.0 if s['score'] is False else float(s['score']))
                   for s in scores_dict.values())
        if total > best_total_score:
            best_total_score = total
            best_machine_id = machine_id
    
    # 3. 构建result_id
    result_id_data = {
        'id': best_machine_id or '',
        'details': []
    }
    
    if best_machine_id:
        best_machine = next((m for m in all_machines if str(m.get('id', '')) == best_machine_id), None)
        if best_machine:
            # 直接使用数据库字段
            for req_idx, req in enumerate(all_requirements):
                original = req.get('original', '')
                if 'CPU' in original or 'cpu' in original.lower():
                    category = 'CPU'
                    field_value = best_machine.get('cpu', '')
                    field_key = 'cpu'
                elif '硬盘' in original or 'hard' in original.lower():
                    category = 'Hard Disk'
                    field_value = best_machine.get('hard_disk', '')
                    field_key = 'hard_disk'
                elif '内存' in original or 'memory' in original.lower():
                    category = 'Memory'
                    field_value = best_machine.get('memory', '')
                    field_key = 'memory'
                elif '插槽' in original or 'slot' in original.lower():
                    category = 'Slots'
                    field_value = best_machine.get('slots', '')
                    field_key = 'slots'
                else:
                    continue
                
                score_info = machine_scores[best_machine_id][req_idx]
                detail = {
                    'category': category,
                    'score': score_info['score'],
                    'reason': score_info['reason'],
                    'original': original,
                    field_key: field_value,
                    'model': best_machine.get('model', ''),
                    'price_cny': str(int(best_machine.get('quote_price', 0)))
                }
                result_id_data['details'].append(detail)
            
            result_id_data['total_score'] = best_total_score
    
    # 4. 构建sim_raw_data（只包含最佳匹配的仿真机）
    sim_raw_data = []
    if best_machine_id:
        best_machine = next((m for m in all_machines if str(m.get('id', '')) == best_machine_id), None)
        if best_machine:
            # 直接使用数据库字段
            raw_item = {
                'id': str(best_machine.get('id', '')),
                'category': best_machine.get('category', ''),
                'type': best_machine.get('type', ''),
                'model': best_machine.get('model', ''),
                'brief_description': best_machine.get('description_simple', ''),
                'detailed_description': best_machine.get('description_detailed', ''),
                'manufacturer': best_machine.get('manufacturer', ''),
                'price_cny': int(best_machine.get('quote_price', 0)),
                'series': best_machine.get('series', ''),
                'cpu': best_machine.get('cpu', ''),
                'hard_disk': best_machine.get('hard_disk', ''),
                'memory': best_machine.get('memory', ''),
                'slots': best_machine.get('slots', '')
            }
            sim_raw_data.append(raw_item)
    
    # 5. 构建sim_pick_list（按需求分类）
    sim_pick_list = []
    
    for req_idx, req in enumerate(all_requirements):
        original = req.get('original', '')
        if 'CPU' in original or 'cpu' in original.lower():
            category = 'CPU'
            field_key = 'cpu'
        elif '硬盘' in original or 'hard' in original.lower():
            category = 'Hard Disk'
            field_key = 'hard_disk'
        elif '内存' in original or 'memory' in original.lower():
            category = 'Memory'
            field_key = 'memory'
        elif '插槽' in original or 'slot' in original.lower():
            category = 'Slots'
            field_key = 'slots'
        else:
            continue
        
        kkrr_list = []
        for machine in all_machines:
            machine_id = str(machine.get('id', ''))
            if machine_id in machine_scores and req_idx in machine_scores[machine_id]:
                score_info = machine_scores[machine_id][req_idx]
                # 直接使用数据库字段
                field_value = machine.get(field_key, '') or ''
                
                item = {
                    'id': machine_id,
                    field_key: field_value,
                    'reason': score_info['reason'],
                    'score': score_info['score'],
                    'model': machine.get('model', ''),
                    'price_cny': str(int(machine.get('quote_price', 0))),
                    'original': original
                }
                kkrr_list.append(item)
        
        # 按评分降序、价格升序排序
        kkrr_list.sort(key=lambda x: (
            -(1.0 if x['score'] is True else (0.0 if x['score'] is False else float(x['score']))),
            int(x['price_cny']) if x['price_cny'] else float('inf')
        ))
        
        sim_pick_list.append({
            'kkrr': kkrr_list
        })
    
    return {
        'result_id': result_id_data if result_id_data['id'] else {},
        'sim_raw_data': sim_raw_data,
        'sim_pick_list': sim_pick_list
    }


def main():
    # 读取sim.json
    input_file = '/Users/icemilk/Workspace/LSchuangqi_db/db_clean/sim.json'
    output_file = '/Users/icemilk/Workspace/LSchuangqi_db/db_clean/sim_result.json'
    
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    all_requirements = data.get('require', [])
    
    # 如果输入为空，直接返回空输出
    if not all_requirements:
        print("输入需求为空，返回空输出")
        output_data = {
            'result_id': {},
            'sim_raw_data': [],
            'sim_pick_list': []
        }
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
        print(f"结果已保存到: {output_file}")
        return
    
    print(f"处理所有需求:")
    for i, req in enumerate(all_requirements, 1):
        print(f"  需求 {i}: {req.get('original', '')}")
    
    # 查询所有仿真机
    print("\n开始查询数据库...")
    all_machines = query_all_sim_machines()
    print(f"共查询到 {len(all_machines)} 台仿真机")
    
    # 生成新格式的输出
    print("\n生成输出格式...")
    output_data = generate_output_format(all_machines, all_requirements)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n结果已保存到: {output_file}")
    
    # 打印摘要
    if output_data.get('result_id') and output_data['result_id'].get('id'):
        result_info = output_data['result_id']
        print(f"\n最佳匹配仿真机ID: {result_info.get('id', '')}")
        print(f"总评分: {result_info.get('total_score', 0)}")
        print(f"详情数: {len(result_info.get('details', []))}")
    
    print(f"\n原始数据: {len(output_data.get('sim_raw_data', []))} 条")
    print(f"需求分类: {len(output_data.get('sim_pick_list', []))} 类")


if __name__ == '__main__':
    main()

