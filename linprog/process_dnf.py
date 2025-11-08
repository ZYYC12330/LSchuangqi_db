#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
处理input.json中的DNF逻辑表达式，查询数据库，生成output.json
优化版本：增强ID管理、代码结构和错误处理
"""

import json
import psycopg2
import re
import io
from decimal import Decimal
from typing import List, Dict, Tuple, Any, Set, Optional
from itertools import product
import sys
import os
import uuid
from datetime import datetime
import logging

# 数据库配置
DB_CONFIG = {
    'host': '10.0.4.13',
    'database': 'LS_chuangqi',
    'user': 'postgres',
    'password': '123456789',
    'port': 5433
}

# 39个channel_count字段的固定顺序
CHANNEL_COUNT_FIELDS = [
    'AD_channel_count_single_ended',
    'AD_channel_count_differential',
    'DA_channel_count',
    'DIO_total_channel_count',
    'DI_channel_count',
    'DO_channel_count',
    'PWM_output_channel_count',
    'Encoder_quadrature_channel_count',
    'Encoder_hall_channel_count',
    'Encoder_channel_count_differential',
    'Encoder_channel_count_single_ended',
    'Counter_channel_count',
    'CAN_channel_count',
    'UART_channel_count',
    'MIL1553_channel_count',
    'A429_tx_channel_count',
    'A429_rx_channel_count',
    'AFDX_channel_count',
    'SPI_channel_count',
    'SSI_channel_count',
    'Endat_channel_count',
    'BISSC_channel_count',
    'SENT_channel_count',
    'PSI5_channel_count',
    'I2C_channel_count',
    'PCM_channel_count',
    'LVDS_channel_count',
    'RDC_SDC_channel_count',
    'LVDT_RVDT_channel_count',
    'RTD_channel_count',
    'PPS_input_channel_count',
    'PPS_output_channel_count',
    'FPGA_fiber_channel_count',
    'Motion_DA_channel_count',
    'Motion_AD_channel_count',
    'Motion_encoder_input_channel_count',
    'Motion_enable_reset_channel_count',
    'Motion_pulse_output_channel_count',
    'Power_output_channel_count'
]


class BoardProcessor:
    """板卡处理器主类"""

    def __init__(self):
        self.conn = None
        self.all_boards = None
        self.board_cache = {}  # 缓存板卡数据
        self.logger = None  # 日志记录器
        self.log_file = None  # 日志文件路径

    def setup_logging(self, log_file: str = None):
        """
        设置日志记录，同时输出到控制台和文件
        """
        if log_file is None:
            log_file = os.path.join(os.path.dirname(__file__),
                                    f'process_dnf_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')

        self.log_file = log_file

        # 创建日志记录器
        self.logger = logging.getLogger('BoardProcessor')
        self.logger.setLevel(logging.DEBUG)

        # 清除已有的处理器
        self.logger.handlers = []

        # 创建格式器
        formatter = logging.Formatter('%(message)s')

        # 控制台处理器
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.DEBUG)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

        # 文件处理器
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

        self.logger.info(f"日志文件: {log_file}")

    def log_debug(self, message: str):
        """记录调试信息"""
        if self.logger:
            self.logger.debug(message)
        else:
            print(message)

    def get_connection(self):
        """获取数据库连接"""
        if self.conn is None or self.conn.closed:
            self.conn = psycopg2.connect(**DB_CONFIG)
        return self.conn

    def close_connection(self):
        """关闭数据库连接"""
        if self.conn and not self.conn.closed:
            self.conn.close()
            self.conn = None

    def normalize_field_name(self, field_name: str) -> str:
        """将字段名转换为数据库中的格式（小写）"""
        return field_name.strip().lower()

    def is_channel_count_field(self, field_name: str) -> bool:
        """检查字段是否在 CHANNEL_COUNT_FIELDS 中（大小写不敏感）"""
        field_lower = field_name.lower()
        return any(f.lower() == field_lower for f in CHANNEL_COUNT_FIELDS)

    def check_channel_count_field_value(self, field_value: Any) -> bool:
        """检查 CHANNEL_COUNT_FIELDS 字段的值：非空、有值且不为0"""
        if field_value is None:
            return False

        # 转换为数值类型检查
        try:
            if isinstance(field_value, Decimal):
                num_value = float(field_value)
            elif isinstance(field_value, (int, float)):
                num_value = float(field_value)
            else:
                # 尝试转换为数值
                num_value = float(field_value)

            # 检查是否不为0
            return num_value != 0
        except (ValueError, TypeError):
            # 如果无法转换为数值，检查是否为空字符串
            return str(field_value).strip() != ''

    def parse_logical_expression(self, logic_str: str) -> List[List[str]]:
        """
        解析逻辑表达式，返回DNF（析取范式）形式
        例如: (A ∧ B) ∨ (C ∧ D) -> [[A, B], [C, D]]
        """
        if not logic_str or not logic_str.strip():
            return []

        # 清理字符串，保留特殊字符
        logic_str = logic_str.strip().replace('\n', ' ').replace('\t', ' ')

        # 如果整个表达式被括号包裹，去掉外层括号
        while logic_str.startswith('(') and logic_str.endswith(')'):
            # 检查是否是最外层括号
            depth = 0
            is_outer = True
            for i, char in enumerate(logic_str[1:-1], 1):
                if char == '(':
                    depth += 1
                elif char == ')':
                    depth -= 1
                    if depth < 0:
                        is_outer = False
                        break
            if is_outer and depth == 0:
                logic_str = logic_str[1:-1].strip()
            else:
                break

        # 按最外层析取符（∨）分割
        parts = []
        depth = 0
        start = 0
        current_conditions = []
        buffer = []

        i = 0
        while i < len(logic_str):
            char = logic_str[i]

            if char == '(':
                if depth == 0:
                    start = i
                depth += 1
                buffer.append(char)
            elif char == ')':
                depth -= 1
                buffer.append(char)
                if depth == 0:
                    # 提取完整的括号内容
                    content = ''.join(buffer).strip()
                    if content.startswith('(') and content.endswith(')'):
                        content = content[1:-1].strip()
                    if content:
                        current_conditions.append(content)
                    buffer = []
            elif depth == 0:
                # 在顶层，检查逻辑操作符
                remaining = logic_str[i:]
                if remaining.lower().startswith(' and '):
                    # 遇到合取符，保存当前条件
                    if buffer:
                        cond = ''.join(buffer).strip()
                        if cond:
                            current_conditions.append(cond)
                            buffer = []
                    # 跳过 " and "
                    i += 4
                    continue
                elif remaining.lower().startswith(' or '):
                    # 遇到析取符，保存当前合取项
                    if current_conditions or buffer:
                        if buffer:
                            cond = ''.join(buffer).strip()
                            if cond:
                                current_conditions.append(cond)
                                buffer = []
                        if current_conditions:
                            parts.append(current_conditions)
                            current_conditions = []
                    # 跳过 " or "
                    i += 3
                    continue
                elif i < len(logic_str) - 1:
                    two_char = logic_str[i:i+2]
                    if '∨' in two_char:
                        if current_conditions or buffer:
                            if buffer:
                                cond = ''.join(buffer).strip()
                                if cond:
                                    current_conditions.append(cond)
                                    buffer = []
                            if current_conditions:
                                parts.append(current_conditions)
                                current_conditions = []
                        i += 1
                        continue
                    elif '∧' in two_char:
                        if buffer:
                            cond = ''.join(buffer).strip()
                            if cond:
                                current_conditions.append(cond)
                                buffer = []
                        i += 1
                        continue

                buffer.append(char)
            else:
                buffer.append(char)

            i += 1

        # 处理剩余内容
        if buffer:
            cond = ''.join(buffer).strip()
            if cond:
                current_conditions.append(cond)

        if current_conditions:
            parts.append(current_conditions)

        # 如果没有找到析取，整个表达式作为一个合取
        if not parts:
            conditions = []
            import re
            parts_str = re.split(r'\s+and\s+|\s+∧\s+|∧',
                                 logic_str, flags=re.IGNORECASE)
            for part in parts_str:
                part = part.strip()
                if part:
                    if part.startswith('(') and part.endswith(')'):
                        part = part[1:-1].strip()
                    if part:
                        conditions.append(part)

            if conditions:
                parts = [conditions]
            else:
                parts = [[logic_str.strip()]]

        return parts

    def parse_single_condition(self, condition: str) -> Dict[str, Any]:
        """
        解析单个条件，返回操作符和操作数
        """
        condition = condition.strip()

        # 处理集合包含关系 ⊇ (Unicode)
        if '⊇' in condition:
            parts = condition.split('⊇', 1)
            if len(parts) != 2:
                raise ValueError(f"Invalid condition format: {condition}")
            field = parts[0].strip()
            set_str = parts[1].strip()
            if set_str.startswith('{') and set_str.endswith('}'):
                set_str = set_str[1:-1]
                values = [v.strip().strip('"').strip("'")
                          for v in set_str.split(',')]
                return {
                    'id': str(uuid.uuid4()),
                    'field': self.normalize_field_name(field),
                    'operator': '⊇',
                    'values': values
                }
            else:
                raise ValueError(f"Invalid set format: {set_str}")

        # 处理比较操作符
        operators = [
            ('≥', '>='),
            ('≤', '<='),
            ('≠', '!='),
            ('>', '>'),
            ('<', '<'),
            ('=', '=')
        ]

        for unicode_op, ascii_op in operators:
            if unicode_op in condition:
                parts = condition.split(unicode_op, 1)
                if len(parts) == 2:
                    field = parts[0].strip()
                    value_str = parts[1].strip()

                    try:
                        if '.' in value_str:
                            value = float(value_str)
                        else:
                            value = int(value_str)
                    except ValueError:
                        value = value_str.strip('"').strip("'")

                    return {
                        'id': str(uuid.uuid4()),
                        'field': self.normalize_field_name(field),
                        'operator': unicode_op,
                        'value': value
                    }

            if ascii_op in condition and ascii_op != unicode_op:
                parts = condition.split(ascii_op, 1)
                if len(parts) == 2:
                    field = parts[0].strip()
                    value_str = parts[1].strip()

                    try:
                        if '.' in value_str:
                            value = float(value_str)
                        else:
                            value = int(value_str)
                    except ValueError:
                        value = value_str.strip('"').strip("'")

                    return {
                        'id': str(uuid.uuid4()),
                        'field': self.normalize_field_name(field),
                        'operator': unicode_op,
                        'value': value
                    }

        # 处理带 ∨ 的等于条件
        if '=' in condition and ('∨' in condition or ' or ' in condition.lower()):
            field_match = re.match(r'^([^=]+)=', condition)
            if field_match:
                field = self.normalize_field_name(field_match.group(1).strip())
                values = []
                parts = re.split(r'[∨]| or ', condition, flags=re.IGNORECASE)
                for part in parts:
                    part = part.strip()
                    if '=' in part:
                        value = part.split('=', 1)[
                            1].strip().strip('"').strip("'")
                        values.append(value)
                    elif part:
                        value = part.strip().strip('"').strip("'")
                        values.append(value)
                if values:
                    return {
                        'id': str(uuid.uuid4()),
                        'field': field,
                        'operator': '∈',
                        'values': values
                    }

        raise ValueError(f"Unsupported condition format: {condition}")

    def evaluate_condition(self, row: Dict[str, Any], condition_dict: Dict[str, Any]) -> bool:
        """评估单个条件是否满足"""
        try:
            field = condition_dict['field']
            operator = condition_dict['operator']

            field_value = row.get(field)

            if field_value is None:
                return False

            # 对于 CHANNEL_COUNT_FIELDS 中的字段，只检查非空、有值且不为0

            if self.is_channel_count_field(field):
                result = self.check_channel_count_field_value(field_value)
                return result

            # 辅助函数：将数值类型转换为float进行比较
            def to_float(val):
                if isinstance(val, Decimal):
                    return float(val)
                elif isinstance(val, (int, float)):
                    return float(val)
                return None

            if operator in ['≥', '>=']:
                value = condition_dict['value']
                field_float = to_float(field_value)
                value_float = to_float(value)
                if field_float is not None and value_float is not None:
                    result = field_float >= value_float
                    self.log_debug(f"[DEBUG]   字段 '{field}': {field_value} (类型: {type(field_value).__name__}, 转换后: {field_float}) "
                                   f"{operator} {value} (类型: {type(value).__name__}, 转换后: {value_float}) -> 结果: {result}")
                    return result
                self.log_debug(
                    f"[DEBUG] 字段 '{field}': 无法进行数值比较 ({field_value} vs {value})")
                return False

            elif operator in ['≤', '<=']:
                value = condition_dict['value']
                field_float = to_float(field_value)
                value_float = to_float(value)
                if field_float is not None and value_float is not None:
                    result = field_float <= value_float
                    self.log_debug(f"[DEBUG] 字段 '{field}': {field_value} (类型: {type(field_value).__name__}, 转换后: {field_float}) "
                                   f"{operator} {value} (类型: {type(value).__name__}, 转换后: {value_float}) -> 结果: {result}")
                    return result
                self.log_debug(
                    f"[DEBUG] 字段 '{field}': 无法进行数值比较 ({field_value} vs {value})")
                return False

            elif operator == '>':
                value = condition_dict['value']
                field_float = to_float(field_value)
                value_float = to_float(value)
                if field_float is not None and value_float is not None:
                    result = field_float > value_float
                    self.log_debug(f"[DEBUG] 字段 '{field}': {field_value} (类型: {type(field_value).__name__}, 转换后: {field_float}) "
                                   f"{operator} {value} (类型: {type(value).__name__}, 转换后: {value_float}) -> 结果: {result}")
                    return result
                self.log_debug(
                    f"[DEBUG] 字段 '{field}': 无法进行数值比较 ({field_value} vs {value})")
                return False

            elif operator == '<':
                value = condition_dict['value']
                field_float = to_float(field_value)
                value_float = to_float(value)
                if field_float is not None and value_float is not None:
                    result = field_float < value_float
                    self.log_debug(f"[DEBUG] 字段 '{field}': {field_value} (类型: {type(field_value).__name__}, 转换后: {field_float}) "
                                   f"{operator} {value} (类型: {type(value).__name__}, 转换后: {value_float}) -> 结果: {result}")
                    return result
                self.log_debug(
                    f"[DEBUG] 字段 '{field}': 无法进行数值比较 ({field_value} vs {value})")
                return False

            elif operator == '=':
                value = condition_dict['value']
                field_float = to_float(field_value)
                value_float = to_float(value)
                if field_float is not None and value_float is not None:
                    result = abs(field_float - value_float) < 1e-9
                    self.log_debug(f"[DEBUG] 字段 '{field}': 比较 {field_value} (类型: {type(field_value).__name__}, 转换后: {field_float}) "
                                   f"{operator} {value} (类型: {type(value).__name__}, 转换后: {value_float}) "
                                   f"-> 结果: {result} (差值: {abs(field_float - value_float)})")
                    return result
                result = str(field_value).strip() == str(value).strip()
                self.log_debug(
                    f"[DEBUG] 字段 '{field}': 字符串比较 '{field_value}' {operator} '{value}' -> 结果: {result}")
                return result

            elif operator in ['≠', '!=']:
                value = condition_dict['value']
                field_float = to_float(field_value)
                value_float = to_float(value)
                if field_float is not None and value_float is not None:
                    return abs(field_float - value_float) >= 1e-9
                return str(field_value).strip() != str(value).strip()

            elif operator == '⊇':
                required_values = condition_dict['values']
                if isinstance(field_value, str):
                    field_values = []
                    if ',' in field_value:
                        field_values = [v.strip()
                                        for v in field_value.split(',')]
                    else:
                        field_values = [field_value.strip()]
                elif isinstance(field_value, list):
                    field_values = [str(v) for v in field_value]
                else:
                    field_values = [str(field_value)]

                for req_val in required_values:
                    if not any(req_val in fv or fv == req_val for fv in field_values):
                        return False
                return True

            elif operator == '∈':
                allowed_values = condition_dict['values']
                field_value_str = str(field_value).strip()
                return field_value_str in [str(v).strip() for v in allowed_values]

            else:
                raise ValueError(f"Unsupported operator: {operator}")

        except Exception as e:
            return False

    def query_board_data(self) -> List[Dict[str, Any]]:
        """查询所有板卡数据"""
        if self.all_boards is not None:
            return self.all_boards

        conn = None
        try:
            conn = self.get_connection()
            cur = conn.cursor()

            # 查询所有列（除了created_at等元数据）
            cur.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'hardware_specifications' 
                AND column_name NOT IN ('created_at')
                ORDER BY ordinal_position
            """)

            columns = [row[0] for row in cur.fetchall()]

            # 构建查询语句
            column_list = ', '.join(columns)
            cur.execute(f"SELECT {column_list} FROM hardware_specifications")

            rows = cur.fetchall()
            cur.close()

            # 转换为字典列表
            result = []
            for i, row in enumerate(rows):
                board_dict = {}
                for j, col in enumerate(columns):
                    board_dict[col] = row[j]
                result.append(board_dict)

            self.all_boards = result
            return result

        except Exception as e:
            print(f"Database error: {e}")
            return []
        finally:
            pass  # 不要关闭连接，保持复用

    def find_matching_boards(self, logic_str: str) -> Tuple[List[Dict], Dict]:
        """
        根据逻辑表达式查找匹配的板卡
        返回: (匹配的板卡列表, 状态信息)
        """
        # 步骤1：解析逻辑表达式为DNF形式
        dnf_parts = self.parse_logical_expression(logic_str)

        if not dnf_parts:
            return [], {
                "condition_status": {},
                "satisfied_ratio": 0.0,
                "matched_with": []
            }

        # 步骤2：解析每个条件
        parsed_dnf = []
        all_conditions = []
        condition_mapping = {}  # 条件字符串到ID的映射

        for part in dnf_parts:
            parsed_part = []
            for cond_str in part:
                try:
                    cond_dict = self.parse_single_condition(cond_str)
                    parsed_part.append((cond_str, cond_dict))
                    condition_mapping[cond_str] = cond_dict['id']
                    if cond_str not in all_conditions:
                        all_conditions.append(cond_str)
                except Exception as e:
                    print(
                        f"Warning: Failed to parse condition '{cond_str}': {e}")
            if parsed_part:
                parsed_dnf.append(parsed_part)

        if not parsed_dnf:
            return [], {
                "condition_status": {cond: False for cond in all_conditions},
                "satisfied_ratio": 0.0,
                "matched_with": []
            }

        # 步骤3：获取所有板卡数据
        boards = self.query_board_data()

        if not boards:
            return [], {
                "condition_status": {cond: False for cond in all_conditions},
                "satisfied_ratio": 0.0,
                "matched_with": []
            }

        # 步骤4：评估每个板卡
        matched_boards = []
        matched_conditions = set()

        for board in boards:
            # 检查是否符合DNF中的任何一个合取项
            for parsed_part in parsed_dnf:
                part_satisfied = True
                part_conditions = []

                for cond_str, cond_dict in parsed_part:
                    if self.evaluate_condition(board, cond_dict):
                        part_conditions.append(cond_str)
                    else:
                        part_satisfied = False
                        break

                if part_satisfied:
                    matched_boards.append(board)
                    matched_conditions.update(part_conditions)
                    break

        # 步骤5：构建状态信息
        condition_status = {cond: (cond in matched_conditions)
                            for cond in all_conditions}
        satisfied_ratio = len(matched_conditions) / \
            len(all_conditions) if all_conditions else 0.0

        return matched_boards, {
            "condition_status": condition_status,
            "satisfied_ratio": satisfied_ratio,
            "matched_with": list(matched_conditions),
            "total_conditions": len(all_conditions),
            "matched_conditions_count": len(matched_conditions),
            "condition_mapping": condition_mapping
        }

    def build_matrix_channel_count(self, board: Dict[str, Any]) -> List[int]:
        """
        为板卡构建matrix_channel_count矩阵
        """
        matrix = []
        for field in CHANNEL_COUNT_FIELDS:
            value = board.get(field.lower())
            if value is not None:
                try:
                    matrix.append(int(value))
                except (ValueError, TypeError):
                    matrix.append(0)
            else:
                matrix.append(0)
        return matrix

    def extract_fields_from_dnf(self, dnf_str: str) -> Set[str]:
        """
        从DNF表达式中提取所有涉及的字段名
        """
        if not dnf_str or not dnf_str.strip():
            return set()

        fields = set()
        try:
            dnf_parts = self.parse_logical_expression(dnf_str)
            for part in dnf_parts:
                for cond_str in part:
                    try:
                        cond_dict = self.parse_single_condition(cond_str)
                        fields.add(cond_dict['field'])
                    except:
                        pass
        except:
            pass

        return fields

    def find_boards_with_values(self, fields: Set[str], exclude_board_ids: Set[str] = None) -> List[Dict[str, Any]]:
        """
        查找数据库中指定字段至少有一个非NULL的板卡
        """
        if not fields:
            return []

        all_boards = self.query_board_data()
        if exclude_board_ids is None:
            exclude_board_ids = set()

        result = []
        for board in all_boards:
            board_id = board.get('id')
            if board_id and str(board_id) in exclude_board_ids:
                continue

            has_value = False
            for field in fields:
                field_lower = field.lower()
                if board.get(field_lower) is not None:
                    has_value = True
                    break

            if has_value:
                result.append(board)

        return result

    def extract_requirement_specification(self, dnf_str: str) -> Dict[str, Any]:
        """
        从DNF表达式中提取requirement_specification
        """
        if not dnf_str or not dnf_str.strip():
            return {}

        spec = {}
        self.log_debug("\n" + "=" * 80)
        self.log_debug(f"[DEBUG] ========== 开始提取需求规格 ==========")
        self.log_debug(f"[DEBUG] DNF 表达式: {dnf_str}")
        try:
            dnf_parts = self.parse_logical_expression(dnf_str)
            for part in dnf_parts:
                for cond_str in part:
                    try:
                        cond_dict = self.parse_single_condition(cond_str)
                        field = cond_dict['field']
                        operator = cond_dict['operator']
                        self.log_debug(f"[DEBUG] 处理条件: {cond_str}")
                        self.log_debug(
                            f"[DEBUG]   字段: {field}, 操作符: {operator} (类型: {type(operator).__name__})")

                        if operator in ['≥', '>=', '≤', '<=', '>', '<', '=', '≠', '!=']:
                            spec[field] = {
                                'value': cond_dict.get('value'),
                                'operator': operator
                            }
                            self.log_debug(
                                f"[DEBUG]   ✓ 已提取到需求规格: {field} = {cond_dict.get('value')}")
                        elif operator == '⊇':
                            spec[field] = {
                                'values': cond_dict.get('values', []),
                                'operator': operator
                            }
                            self.log_debug(
                                f"[DEBUG]   ✓ 已提取到需求规格: {field} ⊇ {cond_dict.get('values', [])}")
                        elif operator == '∈':
                            spec[field] = {
                                'values': cond_dict.get('values', []),
                                'operator': operator
                            }
                            self.log_debug(
                                f"[DEBUG]   ✓ 已提取到需求规格: {field} ∈ {cond_dict.get('values', [])}")
                        else:
                            self.log_debug(
                                f"[DEBUG]   ✗ 操作符 '{operator}' 不在提取列表中，跳过")
                    except Exception as e:
                        self.log_debug(f"[DEBUG]   处理条件时出错: {e}")
                        import traceback
                        traceback.print_exc()
                        pass
        except Exception as e:
            self.log_debug(f"[DEBUG] 解析 DNF 表达式时出错: {e}")
            import traceback
            traceback.print_exc()
            pass

        self.log_debug(f"[DEBUG] 提取完成，共 {len(spec)} 个字段: {list(spec.keys())}")
        self.log_debug(f"[DEBUG] ========== 需求规格提取完成 ==========")
        self.log_debug("=" * 80 + "\n")
        return spec

    def extract_board_specification(self, board: Dict[str, Any], fields: Set[str], requirement_spec: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        从板卡数据中提取相关字段的值
        """
        spec = {}

        if requirement_spec:
            for field in requirement_spec.keys():
                field_lower = field.lower()
                value = board.get(field_lower)
                if value is not None:
                    spec[field] = {
                        'value': value
                    }
                    self.log_debug(
                        f"[DEBUG] 提取板卡规格 - 字段: {field}, 值: {value} (类型: {type(value).__name__})")
        else:
            for field in sorted(fields):
                field_lower = field.lower()
                value = board.get(field_lower)
                if value is not None:
                    spec[field] = {
                        'value': value
                    }
                    self.log_debug(
                        f"[DEBUG] 提取板卡规格 - 字段: {field}, 值: {value} (类型: {type(value).__name__})")

        return spec

    def build_compliance(self, board: Dict[str, Any], dnf_str: str) -> Dict[str, bool]:
        """
        构建compliance对象，评估每个条件的满足情况
        """
        if not dnf_str or not dnf_str.strip():
            return {}

        compliance = {}
        board_id = board.get('id', 'N/A')
        board_model = board.get('model', 'N/A')
        self.log_debug("\n" + "-" * 80)
        self.log_debug(f"[DEBUG] ========== 开始评估板卡合规性 ==========")
        self.log_debug(f"[DEBUG] 板卡 ID: {board_id}, 型号: {board_model}")
        self.log_debug(f"[DEBUG] DNF 表达式: {dnf_str}")

        try:
            dnf_parts = self.parse_logical_expression(dnf_str)
            self.log_debug(f"[DEBUG] 解析后的 DNF 部分数: {len(dnf_parts)}")

            for part_idx, part in enumerate(dnf_parts):
                self.log_debug(f"[DEBUG] --- 处理 DNF 部分 {part_idx + 1} ---")
                for cond_idx, cond_str in enumerate(part):
                    try:
                        cond_dict = self.parse_single_condition(cond_str)
                        field = cond_dict['field']

                        # 对于 CHANNEL_COUNT_FIELDS 中的字段，使用简化检查
                        if self.is_channel_count_field(field):
                            self.log_debug(
                                f"[DEBUG] 条件 {cond_idx + 1}: {cond_str}")
                            self.log_debug(
                                f"[DEBUG]   字段名: {field} (CHANNEL_COUNT_FIELDS 字段，使用简化检查)")

                            # 获取板卡中的实际值
                            field_value = board.get(field)
                            self.log_debug(
                                f"[DEBUG]   板卡中的值: {field_value} (类型: {type(field_value).__name__ if field_value is not None else 'None'})")

                            # 简化检查：非空、有值且不为0
                            is_ok = self.check_channel_count_field_value(
                                field_value)
                            compliance_key = f"{field}_ok"
                            compliance[compliance_key] = {
                                'value': is_ok
                            }
                            self.log_debug(
                                f"[DEBUG]   评估结果: {is_ok} -> {compliance_key} = {is_ok} (简化检查：非空且不为0)")
                            self.log_debug("")
                        else:
                            # 普通字段，使用正常的条件比较
                            self.log_debug(
                                f"[DEBUG] 条件 {cond_idx + 1}: {cond_str}")
                            self.log_debug(f"[DEBUG]   字段名: {field}")
                            self.log_debug(
                                f"[DEBUG]   操作符: {cond_dict['operator']}")
                            if 'value' in cond_dict:
                                self.log_debug(
                                    f"[DEBUG]   条件值: {cond_dict['value']} (类型: {type(cond_dict['value']).__name__})")
                            if 'values' in cond_dict:
                                self.log_debug(
                                    f"[DEBUG]   条件值列表: {cond_dict['values']}")

                            # 获取板卡中的实际值
                            field_value = board.get(field)
                            self.log_debug(
                                f"[DEBUG]   板卡中的值: {field_value} (类型: {type(field_value).__name__ if field_value is not None else 'None'})")

                            is_ok = self.evaluate_condition(board, cond_dict)
                            compliance_key = f"{field}_ok"
                            compliance[compliance_key] = {
                                'value': is_ok
                            }
                            self.log_debug(
                                f"[DEBUG]   评估结果: {is_ok} -> {compliance_key} = {is_ok}")
                            self.log_debug("")
                    except Exception as e:
                        self.log_debug(f"[DEBUG]   评估条件时出错: {e}")
                        import traceback
                        traceback.print_exc()
                        pass
        except Exception as e:
            self.log_debug(f"[DEBUG] 解析 DNF 表达式时出错: {e}")
            import traceback
            traceback.print_exc()
            pass

        # 计算匹配百分比
        match_percentage = self.calculate_match_percentage(compliance)
        satisfied_count = sum(1 for item in compliance.values()
                              if isinstance(item, dict) and item.get('value') is True)
        total_count = len(compliance)

        self.log_debug(f"[DEBUG] ========== 板卡合规性评估完成 ==========")
        self.log_debug(
            f"[DEBUG] 匹配程度: {match_percentage}% (满足 {satisfied_count}/{total_count} 个条件)")
        self.log_debug("-" * 80 + "\n")
        return compliance

    def calculate_match_percentage(self, compliance: Dict[str, Any]) -> int:
        """
        计算匹配百分比
        """
        if not compliance:
            return 0

        total = len(compliance)
        if total == 0:
            return 0

        satisfied = sum(1 for item in compliance.values()
                        if isinstance(item, dict) and item.get('value') is True)
        return int((satisfied / total) * 100)

    def convert_decimal_to_float(self, obj: Any) -> Any:
        """
        递归地将数据中的 Decimal 类型转换为 float
        """
        if isinstance(obj, Decimal):
            return float(obj)
        elif isinstance(obj, dict):
            return {key: self.convert_decimal_to_float(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [self.convert_decimal_to_float(item) for item in obj]
        elif isinstance(obj, tuple):
            return tuple(self.convert_decimal_to_float(item) for item in obj)
        else:
            return obj

    def process_requirements(self, input_file: str, output_file: str):
        """
        处理input.json，生成output.json
        """
        # 设置日志文件（基于输出文件名）
        log_file = output_file.replace('.json', '.log')
        self.setup_logging(log_file)

        # 1. 读取input.json
        with open(input_file, 'r', encoding='utf-8') as f:
            input_data = json.load(f)

        requirements = input_data.get('require', [])

        # 2. 获取所有板卡数据
        all_boards = self.query_board_data()

        # 用于存储结果
        linprog_input_data = []
        matched_boards = []
        board_original_map = {}
        all_candidate_ids = set()  # 所有有值的板卡ID（去重后）
        all_match_ids = set()  # 完全匹配的板卡ID（match_percentage=100，去重后）

        # 用于计算linprog_requiremnets
        requirement_channel_counts = {}

        # 3. 处理每个需求
        for req_index, req in enumerate(requirements):
            req_id = req.get('id', f"req_{req_index}_{uuid.uuid4().hex[:8]}")
            original = req.get('original', '')
            dnf = req.get('DNF', '')

            if not dnf or not dnf.strip():
                continue

            # 提取字段
            fields = self.extract_fields_from_dnf(dnf)

            # 提取requirement_specification
            req_spec = self.extract_requirement_specification(dnf)

            # 查找所有逻辑表达式中字段有值的板卡（不排除任何板卡）
            boards_with_values = self.find_boards_with_values(
                fields, exclude_board_ids=None)

            if boards_with_values:
                self.log_debug(
                    f"\n[DEBUG] >>>>> 开始处理所有有值的板卡，共 {len(boards_with_values)} 个 <<<<<\n")

            # 对所有有值的板卡进行匹配打分
            for idx, board in enumerate(boards_with_values, 1):
                board_id = str(board.get('id', ''))
                board_model = board.get('model', 'N/A')
                self.log_debug(
                    f"\n[DEBUG] 【处理板卡 ({idx}/{len(boards_with_values)})】ID: {board_id}, 型号: {board_model}")

                # 记录该板卡满足的需求
                if board_id not in board_original_map:
                    board_original_map[board_id] = []
                if original not in board_original_map[board_id]:
                    board_original_map[board_id].append(original)

                # 提取board_specification
                board_spec = self.extract_board_specification(
                    board, fields, req_spec)

                # 构建compliance
                compliance = self.build_compliance(board, dnf)

                # 计算match_percentage
                match_percentage = self.calculate_match_percentage(compliance)

                # 添加到matched_boards
                # 使用 board_id 作为 id（与 linprog_input_data 保持一致）
                matched_boards.append({
                    'id': board_id,
                    'requirement_id': req_id,
                    'model': board.get('model', ''),
                    'description': board.get('brief_description', '') or board.get('detailed_description', ''),
                    'original': original,
                    'match_percentage': match_percentage,
                    'requirement_specification': req_spec,
                    'board_specification': board_spec,
                    'compliance': compliance
                })

                # 统计所有有值的板卡和完全匹配的板卡
                all_candidate_ids.add(board_id)  # 所有有值的板卡
                if match_percentage == 100:
                    all_match_ids.add(board_id)  # 完全匹配的板卡

            # 更新requirement_channel_counts
            for field in fields:
                field_lower = field.lower()
                if field_lower in [f.lower() for f in CHANNEL_COUNT_FIELDS]:
                    if field_lower in req_spec:
                        req_info = req_spec[field_lower]
                        req_value = req_info.get('value') if isinstance(
                            req_info, dict) else req_info
                        if isinstance(req_value, (int, float)) and req_value > 0:
                            if field_lower not in requirement_channel_counts:
                                requirement_channel_counts[field_lower] = 0
                            requirement_channel_counts[field_lower] = max(
                                requirement_channel_counts[field_lower],
                                int(req_value)
                            )

        # 4. 构建linprog_input_data（从matched_boards中提取match_percentage=100的板卡）
        # 按板卡去重，只保留完全匹配的板卡
        # 直接使用 all_match_ids，确保与统计一致
        perfect_match_board_ids = all_match_ids

        board_dict = {}
        for board in all_boards:
            board_id = str(board.get('id', ''))
            if board_id and board_id in perfect_match_board_ids:
                board_dict[board_id] = board

        for board_id, board in board_dict.items():
            matrix = self.build_matrix_channel_count(board)
            original_list = board_original_map.get(board_id, [])

            linprog_input_data.append({
                'id': board_id,  # 使用 board_id 作为 id（与 matched_boards 保持一致）
                'matrix_channel_count': matrix,
                'model': board.get('model', ''),
                'price_cny': board.get('price_cny'),
                'original': original_list
            })

        # 5. 构建linprog_requiremnets
        linprog_requiremnets = []
        for field in CHANNEL_COUNT_FIELDS:
            field_lower = field.lower()
            value = requirement_channel_counts.get(field_lower, 0)
            linprog_requiremnets.append(value)

        # 6. 生成输出
        output_data = {
            'timestamp': datetime.now().isoformat(),
            'linprog_input_data': linprog_input_data,
            'linprog_requiremnets': linprog_requiremnets,
            'matched_boards': matched_boards,
            'total_candidates': len(all_candidate_ids),
            'total_matches': len(all_match_ids),
            'processing_info': {
                'requirements_processed': len(requirements),
                'boards_found': len(linprog_input_data),
                'matches_made': len(matched_boards)
            }
        }

        # 7. 转换 Decimal 为 float
        output_data = self.convert_decimal_to_float(output_data)

        # 8. 写入output.json
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=4)

        print(f"处理完成！")
        print(f"  - 处理了 {len(requirements)} 个需求")
        print(f"  - 找到 {len(linprog_input_data)} 个完全匹配的板卡（用于线性规划）")
        print(f"  - 完全匹配了 {len(all_match_ids)} 个板卡（去重后）")
        print(f"  - 生成了 {len(matched_boards)} 个匹配记录（包含所有有值的板卡）")
        print(f"  - 输出文件: {output_file}")
        if self.log_file:
            print(f"  - 日志文件: {self.log_file}")

    def main(self):
        """主函数"""
        # 设置输出编码为UTF-8（Windows兼容）
        if sys.platform == 'win32':
            try:
                sys.stdout = io.TextIOWrapper(
                    sys.stdout.buffer, encoding='utf-8', errors='replace')
            except:
                pass

        try:
            if len(sys.argv) > 1 and not sys.argv[1].endswith('.json'):
                arg = sys.argv[1]
                if os.path.isfile(arg):
                    with open(arg, 'r', encoding='utf-8') as f:
                        input_logic = f.read().strip()
                else:
                    input_logic = arg

                print("=== 输入的逻辑表达式 ===")
                print(input_logic)
                print()

                try:
                    boards, status = self.find_matching_boards(input_logic)

                    print("=== 匹配的板卡 ===")
                    if boards:
                        print(f"共找到 {len(boards)} 个匹配的板卡:\n")
                        for i, board in enumerate(boards, 1):
                            print(f"板卡 {i}:")
                            print(f"  ID: {board.get('id', 'N/A')}")
                            print(f"  型号: {board.get('model', 'N/A')}")
                            if 'price_cny' in board and board['price_cny']:
                                print(f"  价格: {board['price_cny']} CNY")
                            if board.get('brand'):
                                print(f"  品牌: {board['brand']}")
                            if board.get('type'):
                                print(f"  类型: {board['type']}")

                            condition_fields = set()
                            for cond in status.get('matched_with', []):
                                for field_candidate in ['AD_', 'DA_', 'DI_', 'DO_', 'UART_', 'Counter_',
                                                        'RTD_', 'PWM_', 'Motion_', 'A429_', 'LVDT_', 'RDC_']:
                                    if field_candidate.lower() in cond.lower():
                                        parts = cond.split('≥')[0].split('≤')[0].split(
                                            '>')[0].split('<')[0].split('=')[0].split('⊇')[0]
                                        if parts:
                                            field = parts[0].strip()
                                            condition_fields.add(field.lower())

                            for key, value in board.items():
                                if value is not None and key in condition_fields:
                                    print(f"  {key}: {value}")
                            print()
                    else:
                        print("未找到匹配的板卡")

                    print("\n=== 条件满足情况 ===")
                    print(f"总条件数: {status.get('total_conditions', 0)}")
                    print(
                        f"满足条件数: {status.get('matched_conditions_count', 0)}")
                    if status.get('total_conditions', 0) > 0:
                        print(
                            f"满足比例: {status.get('satisfied_ratio', 0.0):.2%}")

                    if status.get('condition_status'):
                        print("\n各条件状态:")
                        for cond, satisfied in status.get('condition_status', {}).items():
                            status_str = "[OK]" if satisfied else "[NO]"
                            print(f"  {status_str} {cond}")

                    if status.get('matched_with'):
                        print(f"\n匹配时使用的条件:")
                        for cond in status['matched_with']:
                            print(f"  - {cond}")

                except Exception as e:
                    print(f"错误: {e}")
                    import traceback
                    traceback.print_exc()
            else:
                input_file = os.path.join(
                    os.path.dirname(__file__), 'input.json')
                output_file = os.path.join(
                    os.path.dirname(__file__), 'output.json')

                if len(sys.argv) > 1:
                    input_file = sys.argv[1]
                if len(sys.argv) > 2:
                    output_file = sys.argv[2]

                self.process_requirements(input_file, output_file)

        finally:
            self.close_connection()


if __name__ == '__main__':
    processor = BoardProcessor()
    processor.main()
