#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
将 workflow_output.json 中的数据写入 hardware_specifications_1109 表
"""

import json
import pandas as pd
from sqlalchemy import create_engine, inspect
from typing import Dict, Any
import os
import psycopg2

# 数据库连接配置
DATABASE_URL = "postgresql://postgres:123456789@10.0.4.13:5433/LS_chuangqi"
INPUT_FILE = "/Users/icemilk/Workspace/LSchuangqi_db/db_clean/workflow_output.json"
TABLE_NAME = "hardware_specifications_1109"


def snake_to_pascal_case(snake_str: str) -> str:
    """将 snake_case 转换为 PascalCase（用于字段名映射）"""
    components = snake_str.split('_')
    return ''.join(word.capitalize() for word in components)


def map_json_key_to_db_column(json_key: str) -> str:
    """
    将 JSON 中的字段名映射到数据库列名
    例如: 
    - ad_channel_count_single_ended -> AD_channel_count_single_ended
    - ad_sampling_rate_hz -> AD_sampling_rate_Hz
    - da_output_voltage_min_v -> DA_output_voltage_min_V
    - ad_input_voltage_min_v -> AD_input_voltage_range_min_V
    """
    # 特殊字段映射（需要特殊处理的字段）
    special_mapping = {
        'ad_input_voltage_min_v': 'AD_input_voltage_range_min_V',
        'ad_input_voltage_max_v': 'AD_input_voltage_range_max_V',
        'ad_input_voltage_custom_min_v': 'custom_voltage_range_min_V',
        'ad_input_voltage_custom_max_v': 'custom_voltage_range_max_V',
        'ad_input_current_custom_min_ma': 'custom_current_range_min_mA',
        'ad_input_current_custom_max_ma': 'custom_current_range_max_mA',
        'dio_logic_levels_supported': 'DIO_logic_level',  # 注意：数据库字段名是 DIO_logic_level
        'bus_interface_types_supported': 'Bus_interface_type',  # 注意：数据库字段名是单数
    }
    
    # 先检查特殊映射
    if json_key in special_mapping:
        return special_mapping[json_key]
    # 单位后缀映射（小写转大写）
    unit_mapping = {
        '_hz': '_Hz',
        '_v': '_V',
        '_ma': '_mA',
        '_ohm': '_ohm',  # ohm 保持小写
        '_mw': '_mW',
        '_mv': '_mV',
        '_kv': '_kV',
        '_us': '_us',  # 微秒保持小写
        '_ns': '_ns',
        '_mb': '_Mb',
        '_mbps': '_Mbps',
        '_kbps': '_kbps',
        '_bps': '_bps',
        '_ppb': '_ppb',
        '_arcmin': '_arcmin',
        '_vpp': '_Vpp',
        '_vrms': '_Vrms',
        '_vdc': '_VDC',
    }
    
    # 特殊前缀映射（保持大写）
    prefix_mapping = {
        'ad_': 'AD_',
        'da_': 'DA_',
        'dio_': 'DIO_',
        'di_': 'DI_',
        'do_': 'DO_',
        'pwm_': 'PWM_',
        'encoder_': 'Encoder_',
        'counter_': 'Counter_',
        'can_': 'CAN_',
        'uart_': 'UART_',
        'mil1553_': 'MIL1553_',
        'a429_': 'A429_',
        'afdx_': 'AFDX_',
        'spi_': 'SPI_',
        'ssi_': 'SSI_',
        'endat': 'Endat',
        'bissc_': 'BISSC_',
        'sent_': 'SENT_',
        'psi5_': 'PSI5_',
        'i2c_': 'I2C_',
        'pcm_': 'PCM_',
        'lvds_': 'LVDS_',
        'rdc_sdc_': 'RDC_SDC_',
        'lvdt_rvdt_': 'LVDT_RVDT_',
        'rtd_': 'RTD_',
        'pps_': 'PPS_',
        'rfm_': 'RFM_',
        'fpga_': 'FPGA_',
        'motion_': 'Motion_',
        'bus_': 'Bus_',
        'form_': 'Form_',
        'supported_': 'Supported_',
        'custom_': 'custom_',
        'driver_': 'driver_',
        'protocol_': 'Protocol_',
        'dpm_': 'DPM_',
        'termination_': 'Termination_',
        'coupler_': 'Coupler_',
        'power_': 'Power_',
        'input_': 'Input_',
        'output_': 'Output_',
        'relay_': 'Relay_',
        'profinet_': 'Profinet_',
        'ethercat_': 'EtherCat_',
        'devicenet_': 'DeviceNet_',
        'profibus_': 'Profibus_',
    }
    
    json_key_lower = json_key.lower()
    original_key = json_key
    
    # 先处理单位后缀
    for unit_lower, unit_upper in unit_mapping.items():
        if json_key_lower.endswith(unit_lower):
            original_key = json_key[:-len(unit_lower)] + unit_upper
            json_key_lower = original_key.lower()
            break
    
    # 检查是否有匹配的前缀
    for prefix, db_prefix in prefix_mapping.items():
        if json_key_lower.startswith(prefix):
            # 替换前缀
            remaining = original_key[len(prefix):]
            # 将剩余部分转换为数据库格式（每个单词首字母大写）
            parts = remaining.split('_')
            remaining_formatted = '_'.join(part.capitalize() if part else '' for part in parts)
            return db_prefix + remaining_formatted
    
    # 如果没有匹配的前缀，直接首字母大写每个单词
    parts = original_key.split('_')
    return '_'.join(part.capitalize() if part else '' for part in parts)


def normalize_value(value: Any, json_key: str = None) -> Any:
    """规范化值，处理特殊类型"""
    if value is None:
        return None
    
    # 如果是列表，保持为列表（数组类型）或转换为字符串（VARCHAR类型）
    if isinstance(value, list):
        # 空列表返回 None
        if len(value) == 0:
            return None
        
        # 需要转换为字符串的特殊字段（数据库中是 VARCHAR 而不是数组）
        varchar_fields = {
            'bus_interface_types_supported',  # Bus_interface_type VARCHAR(100)
            'detailed_description',  # 可能是列表但数据库中是 TEXT
        }
        
        if json_key in varchar_fields:
            # 转换为逗号分隔的字符串
            return ', '.join(str(x) for x in value)
        
        # 其他列表保持为列表（让 SQLAlchemy 处理数组类型）
        # 对于数组类型字段，SQLAlchemy 会自动转换为 PostgreSQL 数组格式
        return value
    
    # 如果是布尔值，保持原样
    if isinstance(value, bool):
        return value
    
    # 如果是数字，保持原样
    if isinstance(value, (int, float)):
        return value
    
    # 如果是字符串，保持原样
    if isinstance(value, str):
        return value
    
    return value


def process_json_data(json_file_path: str) -> pd.DataFrame:
    """
    读取并处理 JSON 文件，返回 DataFrame
    """
    with open(json_file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    records = []
    success_count = 0
    error_count = 0
    
    # 遍历 qq 数组
    for item in data.get('qq', []):
        record = {}
        item_id = item.get('id', 'unknown')
        
        # 解析 output 字段（它是 JSON 字符串）
        output_str = item.get('output', '{}')
        try:
            output_data = json.loads(output_str)
        except json.JSONDecodeError as e:
            print(f"✗ 解析失败 - id={item_id}: {e}")
            error_count += 1
            continue
        
        # 添加原始 id
        record['id'] = item_id
        
        # 将 JSON 字段映射到数据库列名
        for json_key, json_value in output_data.items():
            db_column = map_json_key_to_db_column(json_key)
            record[db_column] = normalize_value(json_value, json_key)
        
        records.append(record)
        success_count += 1
    
    # 创建 DataFrame
    df = pd.DataFrame(records)
    
    print(f"✓ 数据解析完成: 成功 {success_count} 条, 失败 {error_count} 条")
    
    return df


def create_custom_inserter(enum_array_columns):
    """
    创建自定义插入函数，用于处理枚举数组字段
    """
    def psql_insert_with_cast(table, conn, keys, data_iter):
        """
        使用 execute 和 CAST 来处理枚举数组
        """
        from sqlalchemy import text
        
        # 转换数据为列表
        data = list(data_iter)
        if not data:
            return
        
        # 构建 SQL 列名部分
        columns = ', '.join(['"{}"'.format(k) for k in keys])
        
        # 构建占位符，对枚举数组列使用 CAST
        placeholders = []
        for key in keys:
            if key in enum_array_columns:
                # 对枚举数组使用 string_to_array + CAST
                enum_type = enum_array_columns[key]
                placeholders.append(f"string_to_array(:p{keys.index(key)}, ', ')::{enum_type}[]")
            else:
                placeholders.append(f":p{keys.index(key)}")
        
        # 构建 UPDATE SET 子句（排除 id 列）
        update_columns = [k for k in keys if k != 'id']
        update_set = ', '.join([f'"{col}" = EXCLUDED."{col}"' for col in update_columns])
        
        # 构建 INSERT ... ON CONFLICT 语句
        insert_sql = f'''
            INSERT INTO {table.name} ({columns}) 
            VALUES ({", ".join(placeholders)})
            ON CONFLICT (id) DO UPDATE SET {update_set}
        '''
        
        # 执行批量插入/更新
        try:
            for row in data:
                # 构建参数字典
                params = {f'p{i}': val for i, val in enumerate(row)}
                conn.execute(text(insert_sql), params)
        except Exception as e:
            raise e
    
    return psql_insert_with_cast


def write_to_database(df: pd.DataFrame, database_url: str, table_name: str):
    """
    使用 pandas 将 DataFrame 写入数据库
    采用分批写入的方式，避免参数过多的问题
    """
    print(f"\n准备写入 {len(df)} 条记录到表 {table_name}...")
    
    # 创建数据库引擎
    try:
        engine = create_engine(database_url)
        print("✓ 数据库连接成功")
    except Exception as e:
        print(f"✗ 数据库连接失败: {e}")
        raise
    
    # 获取数据库表的列名和类型
    try:
        from sqlalchemy.types import ARRAY
        inspector = inspect(engine)
        columns_info = inspector.get_columns(table_name)
        table_columns = [col['name'] for col in columns_info]
        # 创建列类型映射，用于判断哪些列是数组类型
        # 存储类型对象本身，而不是字符串表示
        column_types = {col['name']: col['type'] for col in columns_info}
        column_type_strs = {col['name']: str(col['type']) for col in columns_info}
        print(f"✓ 获取到表 {table_name} 的列信息，共 {len(table_columns)} 列")
    except Exception as e:
        print(f"⚠ 无法获取表列信息: {e}，将尝试写入所有列")
        table_columns = None
        column_types = {}
        column_type_strs = {}
    
    # 初始化枚举数组列映射
    enum_array_columns = {}
    
    # 只保留数据库表中存在的列（忽略大小写匹配）
    if table_columns:
        # 创建数据库表列名的小写映射（小写 -> 原始列名）
        table_columns_lower_map = {col.lower(): col for col in table_columns}
        
        # 找到 DataFrame 中与数据库表列匹配的列（忽略大小写）
        column_mapping = {}  # DataFrame列名 -> 数据库表列名
        valid_columns = []
        invalid_columns = []
        
        for df_col in df.columns:
            df_col_lower = df_col.lower()
            if df_col_lower in table_columns_lower_map:
                # 找到匹配的列，使用数据库表的实际列名
                db_col = table_columns_lower_map[df_col_lower]
                column_mapping[df_col] = db_col
                valid_columns.append(df_col)
            else:
                invalid_columns.append(df_col)
        
        if invalid_columns:
            print(f"⚠ 警告: DataFrame 中有 {len(invalid_columns)} 个列在数据库表中不存在，将被忽略")
            print(f"  无效列: {', '.join(invalid_columns[:10])}{'...' if len(invalid_columns) > 10 else ''}")
        
        if not valid_columns:
            print(f"✗ 错误: DataFrame 中没有与数据库表匹配的列")
            return False
        
        # 重命名 DataFrame 的列以匹配数据库表的列名
        df = df[valid_columns].rename(columns=column_mapping)
        print(f"✓ 将写入 {len(valid_columns)} 个有效列（已匹配到数据库表列名）")
        
        # 首先处理所有非数组列：将列表值转换为逗号分隔的字符串
        # 这是因为normalize_value会保留列表，但某些字段在数据库中不是数组类型
        from sqlalchemy.types import ARRAY
        for col in df.columns:
            col_type = column_types.get(col)
            is_array = isinstance(col_type, ARRAY)
            
            if not is_array:
                # 非数组列：将列表转换为字符串
                df[col] = df[col].apply(lambda x: ', '.join(str(item) for item in x) if isinstance(x, list) else x)
        
        # 检查数组类型的列，获取枚举数组类型的映射
        enum_array_columns = {}  # {列名: 枚举类型名}
        normal_array_columns = []  # 普通数组类型（可转换为列表）
        
        # 已知的枚举数组列名（根据schema）
        known_enum_array_columns = {
            'uart_interface_types_supported': 'uart_mode_enum',
            'ad_input_modes': 'ad_input_mode_enum',
            'encoder_signal_types_supported': 'encoder_signal_level_enum',
            'pps_logic_levels_supported': 'pps_logic_level_enum',
            'mil1553_operation_modes_supported': 'mil1553_operation_mode_enum',
            'di_input_modes': 'dio_input_mode_enum',
            'do_output_modes': 'dio_output_mode_enum',
        }
        
        for col in df.columns:
            col_type = column_types.get(col)
            col_type_str = column_type_strs.get(col, '')
            
            # 首先检查是否在已知枚举数组列表中
            col_lower = col.lower()
            if col_lower in known_enum_array_columns:
                enum_type = known_enum_array_columns[col_lower]
                enum_array_columns[col] = enum_type
                # 将列表转换为逗号分隔的字符串（用于 string_to_array）
                df[col] = df[col].apply(lambda x: ', '.join(x) if isinstance(x, list) else x)
            # 检查是否是数组类型
            elif isinstance(col_type, ARRAY):
                col_type_str_lower = col_type_str.lower()
                # 检查是否是枚举数组（未在已知列表中的）
                if 'enum' in col_type_str_lower:
                    # 提取枚举类型名称
                    enum_type = col_type_str.replace('[]', '').strip()
                    enum_array_columns[col] = enum_type
                    # 将列表转换为逗号分隔的字符串（用于 string_to_array）
                    df[col] = df[col].apply(lambda x: ', '.join(x) if isinstance(x, list) else x)
                else:
                    # 普通数组类型 - 转换为列表，并确保元素类型正确
                    normal_array_columns.append(col)
                    
                    # 获取数组元素类型
                    array_item_type = col_type.item_type if hasattr(col_type, 'item_type') else None
                    is_numeric_array = False
                    if array_item_type:
                        from sqlalchemy.types import Numeric, Integer, Float
                        is_numeric_array = isinstance(array_item_type, (Numeric, Integer, Float))
                    
                    # 将逗号分隔的字符串转换为列表（支持带空格和不带空格的格式）
                    def convert_to_array(x, is_numeric=False):
                        import math
                        # 检查NaN值
                        if pd.isna(x) or (isinstance(x, float) and math.isnan(x)):
                            return None
                        
                        if isinstance(x, list):
                            # 如果已经是列表，确保元素类型正确
                            if is_numeric:
                                try:
                                    # 过滤掉NaN值
                                    result = []
                                    for item in x:
                                        if pd.isna(item) or (isinstance(item, float) and math.isnan(item)):
                                            continue
                                        if item not in (None, '', 'None'):
                                            result.append(float(item))
                                    return result if result else None
                                except (ValueError, TypeError):
                                    # 如果转换失败，保持原样（可能是文本数组）
                                    return x
                            return x
                        elif isinstance(x, str):
                            if ',' in x:
                                # 分割字符串并去除每个元素的空格
                                items = [item.strip() for item in x.split(',')]
                                if is_numeric:
                                    try:
                                        # 转换为数字
                                        result = []
                                        for item in items:
                                            if item and item != 'None':
                                                result.append(float(item))
                                        return result if result else None
                                    except (ValueError, TypeError):
                                        # 如果转换失败，保持为文本列表
                                        return items
                                return items
                            else:
                                # 单个字符串值也要转换为单元素列表
                                if is_numeric:
                                    try:
                                        return [float(x)] if x and x != 'None' else None
                                    except (ValueError, TypeError):
                                        # 如果转换失败，保持为文本列表
                                        return [x] if x else None
                                return [x] if x else None
                        elif x is None:
                            return None
                        else:
                            # 其他类型（如数字）也转换为单元素列表
                            return [x]
                    
                    df[col] = df[col].apply(lambda x: convert_to_array(x, is_numeric_array))
        
        if enum_array_columns:
            print(f"\n✓ 发现 {len(enum_array_columns)} 个枚举数组列（将使用 CAST 转换）")
            for col, enum_type in list(enum_array_columns.items())[:10]:
                print(f"  - {col}: {enum_type}")
        
        if normal_array_columns:
            print(f"✓ 发现 {len(normal_array_columns)} 个普通数组列（已转换为列表）")
            print(f"  普通数组列: {', '.join(normal_array_columns[:10])}")
    
    # 准备插入方法
    insert_method = None
    if enum_array_columns:
        # 如果有枚举数组列，使用自定义插入函数
        insert_method = create_custom_inserter(enum_array_columns)
        print(f"✓ 使用自定义插入方法处理枚举数组")
    
    # 分批写入，每批写入少量记录以避免参数过多
    batch_size = 10  # 每批写入10条记录
    total_rows = len(df)
    success_count = 0
    error_count = 0
    
    try:
        print(f"正在分批写入数据（每批 {batch_size} 条）...")
        
        for i in range(0, total_rows, batch_size):
            batch_df = df.iloc[i:i+batch_size]
            batch_num = (i // batch_size) + 1
            total_batches = (total_rows + batch_size - 1) // batch_size
            
            try:
                batch_df.to_sql(
                    name=table_name,
                    con=engine,
                    if_exists='append',  # 追加模式
                    index=False,  # 不写入索引
                    method=insert_method  # 使用自定义方法处理枚举数组
                )
                success_count += len(batch_df)
                print(f"  批次 {batch_num}/{total_batches}: ✓ 成功写入 {len(batch_df)} 条记录")
            except Exception as e:
                error_count += len(batch_df)
                print(f"  批次 {batch_num}/{total_batches}: ✗ 写入失败 - {e}")
                # 继续处理下一批，不中断整个流程
                continue
        
        print(f"\n{'='*60}")
        if error_count == 0:
            print(f"✓ 写入成功！")
            print(f"  成功写入 {success_count} 条记录到表 {table_name}")
        else:
            print(f"⚠ 部分写入成功")
            print(f"  成功: {success_count} 条")
            print(f"  失败: {error_count} 条")
        print(f"{'='*60}\n")
        
        return error_count == 0
        
    except Exception as e:
        print(f"\n{'='*60}")
        print(f"✗ 写入失败！")
        print(f"  错误信息: {e}")
        print(f"  错误类型: {type(e).__name__}")
        print(f"  已成功写入: {success_count} 条")
        print(f"  失败: {error_count} 条")
        print(f"  准备写入的记录数: {len(df)}")
        print(f"{'='*60}\n")
        raise


def main():
    """主函数"""
    print(f"{'='*60}")
    print(f"开始处理文件: {INPUT_FILE}")
    print(f"{'='*60}\n")
    
    # 检查文件是否存在
    if not os.path.exists(INPUT_FILE):
        print(f"✗ 错误: 文件不存在: {INPUT_FILE}")
        return False
    
    print(f"✓ 文件存在，开始读取...")
    
    # 处理 JSON 数据
    print("\n正在读取和解析 JSON 数据...")
    try:
        df = process_json_data(INPUT_FILE)
    except Exception as e:
        print(f"\n✗ 处理 JSON 数据时出错: {e}")
        return False
    
    if df.empty:
        print("\n⚠ 警告: 没有数据需要写入")
        return False
    
    print(f"\n共处理 {len(df)} 条记录")
    print(f"字段数量: {len(df.columns)}")
    print(f"字段列表: {', '.join(list(df.columns)[:10])}{'...' if len(df.columns) > 10 else ''}")
    
    # 写入数据库
    print(f"\n数据库连接信息:")
    print(f"  数据库: {DATABASE_URL.split('@')[1] if '@' in DATABASE_URL else DATABASE_URL}")
    print(f"  表名: {TABLE_NAME}")
    
    try:
        success = write_to_database(df, DATABASE_URL, TABLE_NAME)
        if success:
            print("✓ 所有操作完成！")
            return True
        else:
            print("✗ 操作失败！")
            return False
    except Exception as e:
        print(f"\n✗ 程序执行失败: {e}")
        return False


if __name__ == "__main__":
    main()

