# 板卡选型优化 API

docker build --network host .
docker build --network host -t linprog-app .

docker run -d -p 8483:8483 linprog-app



基于线性规划的板卡最优采购方案计算 + Excel生成 FastAPI 服务。

## 功能特性

- 🎯 最小化采购成本
- 📊 满足多通道类型需求约束
- ✅ 需求可行性检查
- 🔢 整数线性规划求解
- 📝 详细的优化结果报告
- 📄 Excel报价单自动生成和上传

## 安装依赖

```bash
pip install -r requirements.txt
```

或者使用国内镜像加速：

```bash
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

## 启动服务

```bash
python api.py
```

服务将在 `http://localhost:8483` 启动。

## API 文档

启动服务后，访问以下 URL：

- **Swagger UI**: http://localhost:8483/docs
- **ReDoc**: http://localhost:8483/redoc

## API 端点

### 1. GET `/`
根路径，返回 API 基本信息。

### 2. GET `/health`
健康检查接口。

**响应示例：**
```json
{
  "status": "healthy"
}
```

### 3. GET `/channel-types`
获取所有 23 种通道类型列表。

**响应示例：**
```json
{
  "channel_types": [
    "analogInputChannels",
    "analogOutputChannels",
    ...
  ],
  "count": 23
}
```

### 4. POST `/optimize`
板卡选型优化接口。

**请求体：**
```json
{
  "input_data": [
    {
      "matrix": [0, 8, 4, 0, 0, 2, 8, 8, 2, 0, 0, 0, 12, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
      "model": "Links-IPC-DAQ-08",
      "price_cny": 90,
      "id": "card_001"
    }
  ],
  "requirements_input": [0, 8, 8, 0, 0, 16, 2, 12, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
}
```

**参数说明：**

- `input_data`: 板卡库存数据数组（直接是板卡数组）
  - `matrix`: 长度为 23 的数组，表示各通道类型的数量
  - `model`: 板卡型号名称
  - `price_cny`: 板卡价格（人民币）
  - `id`: 板卡唯一标识ID

- `requirements_input`: 长度为 23 的数组，表示各通道类型的需求量

**响应示例：**
```json
{
  "success": true,
  "message": "优化成功",
  "total_cards": 3,
  "requirements_summary": [
    {
      "index": 1,
      "channel_type": "analogOutputChannels",
      "required": 8
    }
  ],
  "feasibility_checks": [
    {
      "channel_type": "analogOutputChannels",
      "required": 8,
      "available_total": 56,
      "max_single_card": 32,
      "status": "OK"
    }
  ],
  "optimized_solution": [
    {
      "model": "Links-IPC-DAQ-08",
      "quantity": 2,
      "unit_price": 90,
      "total_price": 180,
      "id": "card_001"
    }
  ],
  "total_cost": 330,
  "channel_satisfaction": [
    {
      "channel_type": "analogOutputChannels",
      "required": 8,
      "satisfied": 16,
      "status": "OK"
    }
  ]
}
```

### 5. POST `/generate-excel`
生成Excel文件并自动上传接口。

**请求体：**
```json
{
  "json_data": {
    "array": [
      {
        "each_obj": {
          "id": "card_001",
          "original": "需求点1<br>需求点2",
          "score": 95,
          "reason": "匹配原因1<br>匹配原因2",
          "type": "IO板卡",
          "model": "Links-IPC-DAQ-08",
          "brief_description": "8路模拟输入，4路数字输入",
          "manufacturer": "厂商名称",
          "price_cny": 9000,
          "quantity": 2,
          "total_amount_cny": 18000
        }
      }
    ]
  },
  "token": "sk-zzvwbcaxoss3"
}
```

**参数说明：**

- `json_data`: 包含配置数据的JSON对象
  - `array`: 设备数组
    - `each_obj`: 设备对象
      - `id`: 设备ID
      - `original`: 原始需求（用`<br>`分隔）
      - `score`: 评分
      - `reason`: 匹配原因（用`<br>`分隔）
      - `type`: 设备类型
      - `model`: 规格型号
      - `brief_description`: 简要说明
      - `manufacturer`: 制造商
      - `price_cny`: 单价（元）
      - `quantity`: 数量
      - `total_amount_cny`: 小计（元）
- `token`: 认证token（可选，默认为"sk-zzvwbcaxoss3"）

**响应示例：**
```json
{
  "message": "Excel文件生成并上传成功",
  "total_amount": 18000,
  "file_url": "https://demo.langcore.cn/api/file/xxxxx",
  "file_id": "xxxxx",
  "upload_result": {
    "success": true,
    "status_code": 200,
    "file_url": "https://demo.langcore.cn/api/file/xxxxx",
    "file_id": "xxxxx",
    "response": "文件上传成功，访问地址: https://demo.langcore.cn/api/file/xxxxx"
  }
}
```

生成的Excel包含两个工作表：
1. **报价单**：详细的设备报价信息
2. **需求匹配预览**：需求与设备的匹配关系

## 通道类型索引

23 种通道类型按以下顺序：

| 索引 | 通道类型 | 说明 |
|-----|---------|------|
| 0 | analogInputChannels | 模拟输入通道 |
| 1 | analogOutputChannels | 模拟输出通道 |
| 2 | digitalInputChannels | 数字输入通道 |
| 3 | digitalOutputChannels | 数字输出通道 |
| 4 | digitalIOChannels | 数字 I/O 通道 |
| 5 | serialPortChannels | 串口通道 |
| 6 | canBusChannels | CAN 总线通道 |
| 7 | pwmOutputChannels | PWM 输出通道 |
| 8 | encoderChannels | 编码器通道 |
| 9 | ssiBusChannels | SSI 总线通道 |
| 10 | spiBusChannels | SPI 总线通道 |
| 11 | i2cBusChannels | I2C 总线通道 |
| 12 | pcmLvdChannels | PCM/LVD 通道 |
| 13 | bissCChannels | BiSS-C 通道 |
| 14 | afdxChannels | AFDX 通道 |
| 15 | ppsPulseChannels | PPS 脉冲通道 |
| 16 | rtdResistanceChannels | RTD 电阻通道 |
| 17 | differentialInputChannels | 差分输入通道 |
| 18 | milStd1553BChannels | MIL-STD-1553B 通道 |
| 19 | timerCounterChannels | 定时/计数器通道 |
| 20 | relayOutputChannels | 继电器输出通道 |
| 21 | sharedMemoryChannels | 共享内存通道 |
| 22 | lvdtRvdtSyncChannels | LVDT/RVDT同步通道 |

## 测试

运行测试客户端：

```bash
python test_api.py
```

测试客户端会执行以下测试：
1. 测试根路径
2. 获取通道类型列表
3. 执行板卡优化计算

## 使用 curl 测试

```bash
# 获取通道类型
curl http://localhost:8483/channel-types

# 优化计算
curl -X POST http://localhost:8483/optimize \
  -H "Content-Type: application/json" \
  -d @test_data.json

# 生成Excel
curl -X POST http://localhost:8483/generate-excel \
  -H "Content-Type: application/json" \
  -d @excel_data.json
```

## Python 客户端示例

### 板卡优化
```python
import requests

# 准备数据
data = {
    "input_data": [...],
    "requirements_input": [...]
}

# 发送请求
response = requests.post(
    "http://localhost:8483/optimize",
    json=data
)

# 处理响应
result = response.json()
if result["success"]:
    print(f"总成本: {result['total_cost']}元")
    for card in result["optimized_solution"]:
        print(f"{card['model']}: {card['quantity']} 块")
```

### Excel生成
```python
import requests

# 准备数据
data = {
    "json_data": {
        "array": [...]
    },
    "token": "your-token"
}

# 发送请求
response = requests.post(
    "http://localhost:8483/generate-excel",
    json=data
)

# 处理响应
result = response.json()
if result.get("file_url"):
    print(f"Excel文件地址: {result['file_url']}")
    print(f"总金额: {result['total_amount']}元")
```

## 错误处理

API 会返回以下 HTTP 状态码：

- `200`: 成功
- `400`: 请求参数错误（如数组长度不正确）
- `500`: 服务器内部错误

## 技术栈

- **FastAPI**: Web 框架
- **Pydantic**: 数据验证
- **NumPy**: 数值计算
- **SciPy**: 线性规划求解器
- **Uvicorn**: ASGI 服务器
- **OpenPyXL**: Excel文件生成
- **Requests**: HTTP客户端

## 注意事项

1. `matrix` 和 `requirements_input` 必须都是 **23 个元素**
2. 数组顺序必须与通道类型索引表对应
3. 如果需求无法满足（库存不足），API 会返回详细的可行性检查信息
4. 求解器使用整数线性规划，确保板卡数量为整数
5. Excel生成功能需要 `空白输出模板.xlsx` 模板文件
6. 生成的Excel文件会自动上传到 `demo.langcore.cn` 服务器

## License

MIT


