# 板卡选型优化 API

docker build --network host .

docker run -p 8019:8000 linprog-app


基于线性规划的板卡最优采购方案计算 FastAPI 服务。

## 功能特性

- 🎯 最小化采购成本
- 📊 满足多通道类型需求约束
- ✅ 需求可行性检查
- 🔢 整数线性规划求解
- 📝 详细的优化结果报告

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

服务将在 `http://localhost:8000` 启动。

## API 文档

启动服务后，访问以下 URL：

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API 端点

### 1. GET `/`
根路径，返回 API 基本信息。

### 2. GET `/channel-types`
获取所有 21 种通道类型列表。

**响应示例：**
```json
{
  "channel_types": [
    "analogInputChannels",
    "analogOutputChannels",
    ...
  ],
  "count": 21
}
```

### 3. POST `/optimize`
板卡选型优化接口。

**请求体：**
```json
{
  "input_data": [
    {
      "each_card": [
        {
          "matrix": [0, 8, 4, 0, 0, 2, 8, 8, 2, 0, 0, 0, 12, 0, 0, 0, 0, 0, 0, 0, 0],
          "model": "Links-IPC-DAQ-08",
          "price_cny": 90
        }
      ]
    }
  ],
  "requirements_input": [0, 8, 8, 0, 0, 16, 2, 12, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
}
```

**参数说明：**

- `input_data`: 板卡库存数据数组
  - `matrix`: 长度为 21 的数组，表示各通道类型的数量
  - `model`: 板卡型号名称
  - `price_cny`: 板卡价格（人民币）

- `requirements_input`: 长度为 21 的数组，表示各通道类型的需求量

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
      "total_price": 180
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

## 通道类型索引

21 种通道类型按以下顺序：

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
curl http://localhost:8000/channel-types

# 优化计算
curl -X POST http://localhost:8000/optimize \
  -H "Content-Type: application/json" \
  -d @test_data.json
```

## Python 客户端示例

```python
import requests

# 准备数据
data = {
    "input_data": [...],
    "requirements_input": [...]
}

# 发送请求
response = requests.post(
    "http://localhost:8000/optimize",
    json=data
)

# 处理响应
result = response.json()
if result["success"]:
    print(f"总成本: {result['total_cost']}元")
    for card in result["optimized_solution"]:
        print(f"{card['model']}: {card['quantity']} 块")
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

## 注意事项

1. `matrix` 和 `requirements_input` 必须都是 **21 个元素**
2. 数组顺序必须与通道类型索引表对应
3. 如果需求无法满足（库存不足），API 会返回详细的可行性检查信息
4. 求解器使用整数线性规划，确保板卡数量为整数

## License

MIT


