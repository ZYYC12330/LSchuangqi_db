import csv
import uuid
import openai
import json
import logging
import os
from dotenv import load_dotenv
from prisma import Prisma

# 加载 .env 文件
load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 从环境变量读取API配置
api_key = os.getenv('OPENAI_API_KEY')
base_url = os.getenv('OPENAI_BASE_URL', 'https://dashscope.aliyuncs.com/compatible-mode/v1')

if not api_key:
    raise ValueError("请设置环境变量 OPENAI_API_KEY")

client = openai.OpenAI(
    api_key=api_key,
    base_url=base_url,
)

# Schema fields from iocard_selection model
schema_fields = [
    'id', 'category', 'type', 'model', 'brief_description', 'detailed_description',
    'brand', 'price_cny', 'quantity', 'total_amount_cny', 'supported_series',
    'resolution', 'currentRangeMin', 'currentRangeMax',
    'voltageRangeMin', 'voltageRangeMax', 'sampleRate', 'isCurrent', 'isOutput',
    'lowLevelMinVoltage', 'lowLevelMaxVoltage', 'highLevelMinVoltage',
    'highLevelMaxVoltage', 'supportsFlexibleInputModes', 'resistanceResolution',
    'resistanceRangeMin', 'resistanceRangeMax', 'supportsRS232', 'supportsRS422',
    'supportsRS485', 'maxBaudRate', 'supportsCAN20A_B', 'is_isolated',
    'analogInputChannels', 'analogOutputChannels', 'digitalInputChannels',
    'digitalOutputChannels', 'digitalIOChannels', 'serialPortChannels',
    'canBusChannels', 'pwmOutputChannels', 'encoderChannels', 'ssiBusChannels',
    'spiBusChannels', 'i2cBusChannels', 'pcmLvdChannels', 'bissCChannels',
    'afdxChannels', 'ppsPulseChannels', 'rtdResistanceChannels'
]

# Mapping from input CSV headers to schema fields
header_mapping = {
    '分类': 'category',
    '类型': 'type',
    '型号': 'model',
    '描述（精简）': 'brief_description',
    '描述（详细）': 'detailed_description',
    '品牌': 'brand',
    '报价（￥）': 'price_cny',
    '数量': 'quantity',
    '总价（￥）': 'total_amount_cny',
    '支持的系列': 'supported_series',
    '是否隔离': 'is_isolated'
}

input_file = 'output/IO板卡选型——extend.csv'
output_file = 'output/IO板卡选型——plus.csv'

def infer_missing_fields(brief_description, missing_fields):
    prompt = '''你是一个工业硬件模块参数解析专家。你的任务是：**根据用户提供的自然语言模块描述，精准提取并填充预定义字段，并以严格 JSON 格式输出**。

        ###  输出要求

        - **输出必须是合法 JSON 对象**，格式为：`{"field_name": value}`
        - 所有字段**必须包含**，即使值为 `null`
        - 值类型必须严格匹配：
        - `Int?` → 整数（如 `8`）或 `null`
        - `Float?` → 浮点数（如 `10.0`, `-0.02`）或 `null`
        - `Boolean?` → `true` / `false` 或 `null`
        - **未提及或不适用的字段一律设为 `null`**
        - **禁止编造、推测或默认填充**（即使字段有 `@default` 注解，也以描述为准；若未提及，仍为 `null`）


        ###  单位与数值规范

        - **电流**：输入单位为 A（安培）→ 将 mA 转换为 A（如 ±20mA → `-0.02`, `0.02`）
        - **波特率**：输入单位为 bps → 将 kbps/Mbps 转换为整数 bps（如 921.6 kbps → `921600`）
        - **采样率**：输入单位为 Hz → 将 kHz 转换为浮点数 Hz（如 200 kHz → `200000.0`）
        - **电压、电阻**：保持原始单位（V、Ω），直接填入数值


        ###  字段定义（必须全部输出）
        {
        "resolution": null,                // 分辨率（单位：位，如12位、16位）
        "currentRangeMin": null,           // 电流量程最小值（单位：A）
        "currentRangeMax": null,           // 电流量程最大值（单位：A）
        "voltageRangeMin": null,           // 电压量程最小值（单位：V）
        "voltageRangeMax": null,           // 电压量程最大值（单位：V）
        "sampleRate": null,                // 采样率（仅适用于模拟量输入模块，单位：Hz）
        "isCurrent": null,                 // 是否为电流型（true=电流，false=电压；用于"电流/电压"二选一）
        "isOutput": null,                  // 是否为输出（true=输出，false=输入；用于"输入/输出"二选一）
        "lowLevelMinVoltage": null,        // 低电平最小电压（单位：V），例如 -1.0
        "lowLevelMaxVoltage": null,        // 低电平最大电压（单位：V），例如 1.0
        "highLevelMinVoltage": null,       // 高电平最小电压（单位：V），例如 18.0
        "highLevelMaxVoltage": null,       // 高电平最大电压（单位：V），例如 36.0
        "supportsFlexibleInputModes": null, // 每通道支持 V/OPEN、V/GND 和 GND/OPEN 三种输入模式
        "resistanceResolution": null,      // 电阻分辨率（位数，如 8 位、12 位）
        "resistanceRangeMin": null,        // 电阻范围最小值（单位：Ω）
        "resistanceRangeMax": null,        // 电阻范围最大值（单位：Ω）
        "supportsRS232": null,             // 是否支持 RS-232
        "supportsRS422": null,             // 是否支持 RS-422
        "supportsRS485": null,             // 是否支持 RS-485
        "maxBaudRate": null,               // 最高支持的波特率（单位：bps），例如 921600（即 921.6 Kbps）
        "supportsCAN20A_B": null,          // 是否支持 CAN 2.0A/B 协议
        "is_isolated": null,               // 是否隔离
        "analogInputChannels": null,       // 模拟量采集 (A/D) 通道数
        "analogOutputChannels": null,      // 模拟量输出 (D/A) 通道数
        "digitalInputChannels": null,      // 数字量输入 (DI) 通道数
        "digitalOutputChannels": null,     // 数字量输出 (DO) 通道数
        "digitalIOChannels": null,         // 数字 I/O (DIO) 通道数
        "serialPortChannels": null,        // 串口通信 (RS-232/422/485) 通道数（物理端口数）
        "canBusChannels": null,            // CAN 总线通道数
        "pwmOutputChannels": null,         // PWM 输出通道数
        "encoderChannels": null,           // 编码器采集 (正交编码器) 通道数
        "ssiBusChannels": null,            // SSI 总线通道数
        "spiBusChannels": null,            // SPI 总线通道数
        "i2cBusChannels": null,            // I²C 总线通道数
        "pcmLvdChannels": null,            // PCM / LVDS 通讯通道数
        "bissCChannels": null,             // BISS-C 总线通道数
        "afdxChannels": null,              // AFDX 接口通道数
        "ppsPulseChannels": null,          // PPS 秒脉冲通道数
        "rtdResistanceChannels": null      // RTD 可编程电阻通道数
        }
        # 解析规则

        ## 详细通道数字段

        针对多功能板卡，需要将各类通道数分别填入对应字段：
        - **analogInputChannels**：A/D、模拟量采集、电压/电流输入的通道数
        - **analogOutputChannels**：D/A、模拟量输出、电压/电流输出的通道数
        - **digitalInputChannels**：DI、数字量输入、离散量输入的通道数
        - **digitalOutputChannels**：DO、数字量输出、离散量输出的通道数
        - **digitalIOChannels**：DIO、双向数字 I/O 的通道数
        - **serialPortChannels**： 串口的物理端口数
        - **canBusChannels**：CAN 总线通道数
        - **pwmOutputChannels**：PWM 输出通道数
        - **encoderChannels**：正交编码器（ABZ）采集通道数
        - **ssiBusChannels**：SSI 总线通道数
        - **spiBusChannels**：SPI 总线通道数
        - **i2cBusChannels**：I²C 总线通道数
        - **pcmLvdChannels**：PCM 或 LVDS 通讯通道数
        - **bissCChannels**：BISS-C 总线通道数
        - **afdxChannels**：AFDX 接口通道数
        - **ppsPulseChannels**：秒脉冲（PPS）通道数
        - **rtdResistanceChannels**：RTD 可编程电阻通道数

        示例："16路A/D并行采集，16路D/A并行输出，32路数字I/O线" 应填充为：
        - analogInputChannels: 16
        - analogOutputChannels: 16
        - digitalIOChannels: 32
        

        ## 数字 I/O 特殊配置规则

        - 当描述中出现类似“32路数字IO”、“32路DIO”、“32路数字量I/O”等表述时，应理解为：
        - 该模块支持 **32 路数字 I/O**，且通常具备 **灵活配置能力**（如可设为 DI 或 DO）。
        - 若明确说明“32路数字输入” → `digitalInputChannels: 32`，其他为 `null`。
        - 若明确说明“32路数字输出” → `digitalOutputChannels: 32`，其他为 `null`。
        - 若说明“16路DI + 16路DO” → 分别填入对应字段。
        - 所有数字 I/O 通道数必须是 **8 的倍数**（最小单元为 8 路），例如：8、16、24、32。
        - 若未明确指出是“输入”或“输出”，或描述中提及“可拆分为 8 路一组”、“最小单元 8 路”等，仍按实际总数填写，但不强制拆分。
        - 若描述为“32路数字输入”或“32路数字输出” → 不视为 DIO，而是单向通道。
        - 若描述为“可配置为 32 路 DI 或 32 路 DO” → 表示支持双向配置，应设为 `digitalIOChannels: 32`。
        - 若描述为“16路DI + 16路DO” → 填写 `digitalInputChannels: 16`, `digitalOutputChannels: 16`，`digitalIOChannels: null`。
        - 若描述为“32路DIO，可配置为任意组合，最小单元8路” → `digitalIOChannels: 32`。
        
        ## 功能类别互斥

        - 若描述仅涉及模拟量，则数字量、通信、电阻字段全为 `null`。
        - 若描述仅涉及通信（RS-232/485等），则模拟量、数字量、电阻字段全为 `null`。
        - 仅填充实际提及的功能字段，其余保持 `null`。

        ## 布尔字段逻辑

        - **isCurrent**：仅当模块固定为电流型时为 `true`；固定为电压型时为 `false`；若"可配置"或未说明 → `null`。
        - **isOutput**：明确为输出模块 → `true`；采集/输入 → `false`；未说明 → `null`。
        - **is_isolated**：明确提及"隔离"、"电气隔离"时为 `true`；明确说"非隔离"则为 `false`；否则 `null`。
        - 通信协议字段（如 `supportsRS232`）：仅当明确提及协议名称时设为 `true`；明确说"不支持"则为 `false`；否则 `null`。
        - 特殊总线（如 EnDat、SSI）不属于 RS/CAN，不得填入通信协议字段。

        ## 忽略无关信息

        如"FIFO"、"UART 型号"、"精度"、"输入阻抗"、"拨码开关"等不在字段列表中的内容，不得映射或影响输出。

        
        ###  示例

        ##  输入：
        "16通道并行模拟量采集，16位分辨率，电压范围-10V～+10V，采样率200kHz"

        ##  输出：
        {
        "resolution": 16,
        "currentRangeMin": null,
        "currentRangeMax": null,
        "voltageRangeMin": -10.0,
        "voltageRangeMax": 10.0,
        "sampleRate": 200000.0,
        "isCurrent": false,
        "isOutput": false,
        "lowLevelMinVoltage": null,
        "lowLevelMaxVoltage": null,
        "highLevelMinVoltage": null,
        "highLevelMaxVoltage": null,
        "supportsFlexibleInputModes": null,
        "resistanceResolution": null,
        "resistanceRangeMin": null,
        "resistanceRangeMax": null,
        "supportsRS232": null,
        "supportsRS422": null,
        "supportsRS485": null,
        "maxBaudRate": null,
        "supportsCAN20A_B": null,
        "is_isolated": null,
        "analogInputChannels": 16,
        "analogOutputChannels": null,
        "digitalInputChannels": null,
        "digitalOutputChannels": null,
        "digitalIOChannels": null,
        "serialPortChannels": null,
        "canBusChannels": null,
        "pwmOutputChannels": null,
        "encoderChannels": null,
        "ssiBusChannels": null,
        "spiBusChannels": null,
        "i2cBusChannels": null,
        "pcmLvdChannels": null,
        "bissCChannels": null,
        "afdxChannels": null,
        "ppsPulseChannels": null,
        "rtdResistanceChannels": null
        }
        请根据用户输入的模块描述，严格按照上述规则生成 完整 JSON 对象。只输出 JSON，不要任何额外文本、解释或 markdown。
    '''
    
    response = client.chat.completions.create(
        model="qwen3-max",
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": f"基于以下描述：\\n{brief_description}\\n\\n推断"}
        ],
        
    )
    try:
        inferred = json.loads(response.choices[0].message.content)
        return inferred
    except:
        return {}

db = Prisma()
db.connect()

row_count = 0

# 打开输出CSV文件并写入表头
with open(output_file, 'w', encoding='utf-8', newline='') as outfile:
    # 准备CSV表头（不包含id字段）
    csv_fields = [f for f in schema_fields if f != 'id']
    writer = csv.DictWriter(outfile, fieldnames=csv_fields)
    writer.writeheader()
    
    with open(input_file, 'r', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)
        
        for row in reader:
            row_count += 1
            logging.info(f"处理第 {row_count} 行")
            
            new_row = {field: None for field in schema_fields if field != 'id'}
            
            for input_key, value in row.items():
                schema_key = header_mapping.get(input_key)
                if schema_key:
                    if schema_key in ['price_cny', 'total_amount_cny']:
                        # 转换为整数（因为schema定义为Int?）
                        if value:
                            cleaned_value = value.replace('￥', '').replace(',', '').strip()
                            new_row[schema_key] = int(float(cleaned_value)) if cleaned_value else None
                        else:
                            new_row[schema_key] = None
                    elif schema_key == 'quantity':
                        new_row[schema_key] = int(value) if value else None
                    elif schema_key == 'is_isolated':
                        # 处理布尔值：True, true, 1, yes 等
                        if value:
                            value_lower = str(value).lower().strip()
                            new_row[schema_key] = value_lower in ['true', '1', 'yes', '是']
                        else:
                            new_row[schema_key] = None
                    else:
                        new_row[schema_key] = value
            
            missing_fields = [f for f in schema_fields if f not in new_row or new_row[f] is None and f != 'id']
            if missing_fields:
                inferred = infer_missing_fields(new_row['brief_description'], missing_fields)
                logging.info(f"行 {row_count} - Brief Description: {new_row['brief_description']}")
                logging.info(f"模型推断的值: {json.dumps(inferred, ensure_ascii=False)}")
                
                for f in missing_fields:
                    val = inferred.get(f)
                    if val is not None and val != 'null':
                        if f in ['resolution', 'resistanceResolution', 'maxBaudRate',
                                 'analogInputChannels', 'analogOutputChannels', 'digitalInputChannels',
                                 'digitalOutputChannels', 'digitalIOChannels', 'serialPortChannels',
                                 'canBusChannels', 'pwmOutputChannels', 'encoderChannels', 'ssiBusChannels',
                                 'spiBusChannels', 'i2cBusChannels', 'pcmLvdChannels', 'bissCChannels',
                                 'afdxChannels', 'ppsPulseChannels', 'rtdResistanceChannels',
                                 'price_cny', 'total_amount_cny', 'quantity']:
                            new_row[f] = int(val)
                        elif f in ['currentRangeMin', 'currentRangeMax', 'voltageRangeMin', 'voltageRangeMax', 'sampleRate', 'lowLevelMinVoltage', 'lowLevelMaxVoltage', 'highLevelMinVoltage', 'highLevelMaxVoltage', 'resistanceRangeMin', 'resistanceRangeMax']:
                            new_row[f] = float(val)
                        elif f in ['isCurrent', 'isOutput', 'supportsFlexibleInputModes', 'supportsRS232', 'supportsRS422', 'supportsRS485', 'supportsCAN20A_B', 'is_isolated']:
                            new_row[f] = bool(val)
                        else:
                            new_row[f] = str(val)
                    else:
                        new_row[f] = None
            
            # 插入到数据库
            db.iocard_selection.create(data=new_row)
            logging.info(f"行 {row_count} 已插入数据库")
            
            # 准备写入CSV的数据（将所有值转换为字符串）
            csv_row = {}
            for field in csv_fields:
                value = new_row.get(field)
                if value is None:
                    csv_row[field] = ''
                else:
                    csv_row[field] = str(value)
            
            # 写入CSV文件
            writer.writerow(csv_row)
            logging.info(f"行 {row_count} 已写入CSV文件")

db.disconnect()

logging.info("处理完成")

print(f"所有数据已插入数据库，并写入到 {output_file}")
