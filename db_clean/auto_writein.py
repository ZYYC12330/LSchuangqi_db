import os
import json
import pandas as pd
from dotenv import load_dotenv
import dashscope
from dashscope import Generation

# 加载环境变量
load_dotenv()

# 从 .env 读取大模型配置
DASHSCOPE_API_KEY = os.getenv("OPENAI_API_KEY")
DASHSCOPE_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://dashscope-intl.aliyuncs.com/api/v1")
QWEN_MODEL = os.getenv("QWEN_MODEL", "qwen-turbo")

if not DASHSCOPE_API_KEY:
    raise ValueError("请在 .env 文件中设置 DASHSCOPE_API_KEY")

# 配置 dashscope
dashscope.api_key = DASHSCOPE_API_KEY
if DASHSCOPE_BASE_URL:
    dashscope.base_http_api_url = DASHSCOPE_BASE_URL

# 缓存路径（从 .env 读取）
CACHE_FILE = os.getenv("CACHE_FILE", "cache.json")

# 加载缓存
def load_cache():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_cache(cache):
    with open(CACHE_FILE, 'w', encoding='utf-8') as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)

# 解析函数：调用大模型提取结构化字段
def extract_fields_from_description(desc: str) -> dict:
    cache = load_cache()
    if desc in cache:
        print(f"✅ 缓存命中: {desc[:30]}...")
        return cache[desc]

    prompt = f"""
你是一个工业实时仿真设备专家，请从以下设备描述中提取精确的结构化信息。只输出 JSON 格式，不要解释。

描述：
{desc}

请提取以下字段（若无则填 null）：
- cpu_model: CPU 型号（如 "Intel Core i7-7700k"、"海光3350"）
- cpu_cores: CPU 核心数（整数，如 4、8、16）
- cpu_frequency: 主频（字符串，如 "4.2GHz"、"3.0GHz"）
- cpu_threads: 线程数（整数，如未说明则 null）
- memory_capacity: 内存容量（GB，整数）
- memory_type: 内存类型（如 "DDR4 SDRAM"、"DDR3-1600"）
- storage_capacity: 存储容量（GB，整数）
- storage_type: 存储类型（如 "SATA硬盘"、"固态盘"）
- io_slots_pci: PCI 插槽数量（整数）
- io_slots_pcie_x1: PCIe x1 插槽数量（整数）
- io_slots_pcie_x4: PCIe x4 插槽数量（整数）
- io_slots_pcie_x8: PCIe x8 插槽数量（整数）
- io_slots_pcie_x16: PCIe x16 插槽数量（整数）
- network_ports: 千兆网口数量（整数）
- os: 操作系统（如 "实时操作系统"、"RTLinux"）
- form_factor: 机箱形态（如 "便携"、"机架式"、"4U cPCI"）
- chassis_slots: 机箱总插槽数（整数，如 8、14）
- chassis_height: 机箱高度（如 "4U"、"3U"）
- chassis_design: 机箱设计（如 "半机架"、"冗余电源"）
- additional_features: 其他特性（如 "2通道串口、2通道USB、VGA/DP显示接口"）

请确保所有字段都存在，即使为 null。不要输出任何其他内容。
"""

    try:
        print(f"🔍 调用大模型解析: {desc[:40]}...")
        
        # 使用 dashscope SDK 调用大模型 API
        response = Generation.call(
            model=QWEN_MODEL,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.1,
            max_tokens=2000
        )
        
        # 检查响应状态
        if response.status_code != 200:
            raise Exception(f"API 调用失败: {response.status_code} - {getattr(response, 'message', '未知错误')}")
        
        # 提取响应内容（根据 dashscope SDK 的响应格式）
        content = None
        if hasattr(response, 'output'):
            if hasattr(response.output, 'choices') and len(response.output.choices) > 0:
                # 标准格式：response.output.choices[0].message.content
                if hasattr(response.output.choices[0], 'message'):
                    content = response.output.choices[0].message.content
                else:
                    content = response.output.choices[0].get('message', {}).get('content', '')
            elif hasattr(response.output, 'text'):
                content = response.output.text
        
        # 如果仍未获取到内容，尝试其他方式
        if not content:
            # 尝试从响应字典中提取
            if isinstance(response, dict):
                content = response.get('output', {}).get('choices', [{}])[0].get('message', {}).get('content', '')
            else:
                content = str(response)
        
        if not content:
            raise Exception("无法从 API 响应中提取内容")
        
        # 提取 JSON 部分（模型可能返回多余文本）
        content = content.strip()
        if content.startswith('```json'):
            content = content[7:-3].strip()
        elif content.startswith('```'):
            content = content[3:-3].strip()

        parsed = json.loads(content)
        cache[desc] = parsed
        save_cache(cache)
        print(f"✅ 解析成功: {parsed}")
        return parsed
    except Exception as e:
        print(f"❌ 解析失败: {e}")
        return {
            "cpu_model": None, "cpu_cores": None, "cpu_frequency": None, "cpu_threads": None,
            "memory_capacity": None, "memory_type": None, "storage_capacity": None, "storage_type": None,
            "io_slots_pci": None, "io_slots_pcie_x1": None, "io_slots_pcie_x4": None, "io_slots_pcie_x8": None, "io_slots_pcie_x16": None,
            "network_ports": None, "os": None, "form_factor": None, "chassis_slots": None, "chassis_height": None,
            "chassis_design": None, "additional_features": None
        }

# 主程序
def main():
    # 从 .env 读取配置，如果没有则使用默认值
    input_csv = os.getenv("INPUT_CSV", "/Users/icemilk/Workspace/LSchuangqi_db/db_clean/仿真机选型.csv")
    output_csv = os.getenv("OUTPUT_CSV", "devices_parsed.csv")

    # 从 CSV 文件读取数据
    print(f"📖 正在读取 CSV 文件: {input_csv}")
    df = pd.read_csv(input_csv, encoding='utf-8-sig')
    print(f"✅ 成功读取 {len(df)} 条记录")

    # 预处理：统一字段名（适配你的原始数据）
    df.rename(columns={
        "分类": "category",
        "类型": "type",
        "型号": "model",
        "描述（精简）": "description_simple",
        "描述（详细）": "description_detailed",
        "制造商": "manufacturer",
        "报价（￥）": "quote_price",
        "数量": "quantity",
        "总价（￥）": "total_price",
        "系列": "series"
    }, inplace=True)

    # 清洗价格字段（去掉￥和逗号）
    df['quote_price'] = df['quote_price'].astype(str).str.replace('￥', '').str.replace(',', '').astype(float)
    df['total_price'] = df['total_price'].astype(str).str.replace('￥', '').str.replace(',', '').astype(float)

    # 解析每一行的 description_simple
    extracted = df['description_simple'].apply(extract_fields_from_description)
    extracted_df = pd.json_normalize(extracted)

    # 合并回原表
    result_df = pd.concat([df.drop(columns=['description_simple', 'description_detailed']), extracted_df], axis=1)

    # 重新排序字段（按你之前设计的 PostgreSQL 表结构）
    ordered_columns = [
        'category', 'type', 'model', 'manufacturer', 'quote_price', 'quantity', 'total_price', 'series',
        'cpu_model', 'cpu_cores', 'cpu_frequency', 'cpu_threads',
        'memory_capacity', 'memory_type',
        'storage_capacity', 'storage_type',
        'io_slots_pci', 'io_slots_pcie_x1', 'io_slots_pcie_x4', 'io_slots_pcie_x8', 'io_slots_pcie_x16',
        'network_ports', 'os',
        'form_factor', 'chassis_slots', 'chassis_height', 'chassis_design', 'additional_features',
        'description_simple', 'description_detailed'
    ]

    result_df = result_df[ordered_columns]

    # 输出到 CSV
    result_df.to_csv(output_csv, index=False, encoding='utf-8-sig')
    print(f"\n🎉 解析完成！结果已保存至：{output_csv}")
    print(f"📊 总共处理 {len(df)} 条记录，缓存已保存至 {CACHE_FILE}")

if __name__ == "__main__":
    main()