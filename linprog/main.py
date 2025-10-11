import numpy as np
from scipy.optimize import linprog
import json

# 输入数据（每个分组代表一类需求的可选板卡）
input_data = [
      {
        "matrix": [
          16,
          16,
          0,
          0,
          32,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0
        ],
        "model": "Links-IPC-DAQ-05",
        "price_cny": 250,
        "id": "8132be0c-6ec1-4a3d-bdc3-07ae1e33cc56"
      },
      {
        "matrix": [
          0,
          16,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0
        ],
        "model": "Links-IPC-DA-03",
        "price_cny": 150,
        "id": "243dda57-772c-4f24-ab12-781fd0fefc0d"
      },
      {
        "matrix": [
          0,
          16,
          0,
          0,
          16,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0
        ],
        "model": "Links-IPC-DA-04",
        "price_cny": 180,
        "id": "6207d7f3-1339-428d-a02e-502bbf458776"
      },
      {
        "matrix": [
          16,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0
        ],
        "model": "Links-IPC-AD-01",
        "price_cny": 190,
        "id": "e05bc51b-ca37-459c-9284-317d3e497091"
      },
      {
        "matrix": [
          32,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0
        ],
        "model": "Links-IPC-AD-02",
        "price_cny": 190,
        "id": "d5fa8240-a251-4689-bd65-8cad87cf0977"
      },
      {
        "matrix": [
          32,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0
        ],
        "model": "Links-IPC-AD-03",
        "price_cny": 270,
        "id": "624ba57c-b9e4-4a29-a0f8-f5c8a5cf4a6b"
      },
      {
        "matrix": [
          32,
          0,
          16,
          16,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0
        ],
        "model": "Links-IPC-DAQ-07",
        "price_cny": 90,
        "id": "12163a5f-88c0-4421-9d5c-8babd7847b96"
      },
      {
        "matrix": [
          0,
          0,
          0,
          0,
          0,
          8,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0
        ],
        "model": "Links-IPC-SER-01",
        "price_cny": 60,
        "id": "749fe5eb-52ad-4269-b0b2-7b99b41f10e1"
      },
      {
        "matrix": [
          0,
          0,
          0,
          0,
          0,
          8,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0
        ],
        "model": "Links-IPCe-SER-02",
        "price_cny": 60,
        "id": "8dbc97f9-f94c-4c7d-ad0f-4a67a0a3eca6"
      },
      {
        "matrix": [
          0,
          0,
          0,
          0,
          0,
          0,
          2,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0
        ],
        "model": "Links-IPC-CAN",
        "price_cny": 60,
        "id": "c3418033-9eba-4c25-8a86-5ae19a61f8dd"
      },
      {
        "matrix": [
          0,
          0,
          0,
          0,
          0,
          0,
          4,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0
        ],
        "model": "Links-IPC-CANFD-04",
        "price_cny": 80,
        "id": "efa83220-6850-4792-a434-c38dbd462a46"
      },
      {
        "matrix": [
          0,
          0,
          0,
          0,
          0,
          0,
          2,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0
        ],
        "model": "Links-IPC-CANFD-02",
        "price_cny": 60,
        "id": "263362c6-ee7b-49f8-929d-4f029871501b"
      },
      {
        "matrix": [
          0,
          0,
          128,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0
        ],
        "model": "Links-IPC-DI128",
        "price_cny": 150,
        "id": "61dcb82e-f78a-418a-adc3-03ef23b8be0b"
      },
      {
        "matrix": [
          0,
          0,
          0,
          128,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0
        ],
        "model": "Links-IPC-DO128",
        "price_cny": 150,
        "id": "02f88e07-79ca-43db-80ac-5a491506bbff"
      },
      {
        "matrix": [
          16,
          24,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0
        ],
        "model": "Links-FPGA-Analog-01",
        "price_cny": 260,
        "id": "3efb5f94-4ed3-4e3b-a40b-01fb2619c738"
      },
      {
        "matrix": [
          0,
          8,
          0,
          0,
          0,
          0,
          0,
          0,
          8,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0
        ],
        "model": "Links-IPC-GTS-02",
        "price_cny": 190,
        "id": "f149cc55-526e-46f9-843c-a7fab5c7b16a"
      },
      {
        "matrix": [
          0,
          0,
          0,
          32,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0
        ],
        "model": "Links-FPGA-DIO-01",
        "price_cny": 30,
        "id": "1e80172d-4540-44ad-9b30-d4cc98ecc345"
      },
      {
        "matrix": [
          0,
          0,
          0,
          16,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0
        ],
        "model": "Links-FPGA-DIO-02",
        "price_cny": 40,
        "id": "0c129aea-9549-4635-894d-701dd50c82a0"
      },
      {
        "matrix": [
          8,
          0,
          8,
          8,
          2,
          0,
          0,
          12,
          2,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0
        ],
        "model": "Links-C3U-DAQ-01",
        "price_cny": 250,
        "id": "47fad5a4-5097-4193-b4b3-35c4e2b5efa9"
      },
      {
        "matrix": [
          16,
          16,
          0,
          0,
          32,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0
        ],
        "model": "Links-C3U-DAQ-02",
        "price_cny": 250,
        "id": "bbce97ab-0ef2-41da-ae57-ba1b442c2095"
      },
      {
        "matrix": [
          0,
          18,
          0,
          0,
          32,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0
        ],
        "model": "Links-C3U-DAQ-03",
        "price_cny": 240,
        "id": "48bfb1d2-a21f-46c4-aff7-2a864a21830c"
      },
      {
        "matrix": [
          16,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0
        ],
        "model": "Links-C3U-AI-02",
        "price_cny": 150,
        "id": "0004b1fa-1229-4385-be2f-bb2fa3d634b6"
      },
      {
        "matrix": [
          32,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0
        ],
        "model": "Links-C3U-AI-03",
        "price_cny": 180,
        "id": "cd057002-718b-421c-962e-0dc6db22dd08"
      },
      {
        "matrix": [
          0,
          8,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0
        ],
        "model": "Links-C3U-AO-01",
        "price_cny": 120,
        "id": "6107b9cc-4844-4769-a7c1-a3a0dbbac56a"
      },
      {
        "matrix": [
          0,
          16,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0
        ],
        "model": "Links-C3U-AO-03",
        "price_cny": 180,
        "id": "dd727364-c847-48ee-b957-3ce2f3c7958a"
      },
      {
        "matrix": [
          0,
          16,
          0,
          0,
          16,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0
        ],
        "model": "Links-C3U-AO-05",
        "price_cny": 250,
        "id": "75164c41-8f2f-4c4c-a6fc-cd33fb878979"
      },
      {
        "matrix": [
          0,
          0,
          32,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0
        ],
        "model": "Links-C3U-DI01",
        "price_cny": 110,
        "id": "3088adea-e2c9-4557-b301-0ba146aa1af5"
      },
      {
        "matrix": [
          0,
          0,
          0,
          32,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0
        ],
        "model": "Links-C3U-DO01",
        "price_cny": 110,
        "id": "97b8b5b5-54b6-4ce4-8f81-8f46c6babd9a"
      },
      {
        "matrix": [
          0,
          0,
          32,
          32,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0
        ],
        "model": "Links-C3U-DIO02",
        "price_cny": 190,
        "id": "ca4832ae-fa32-4ee2-b213-ae29ee40160b"
      },
      {
        "matrix": [
          0,
          0,
          96,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0
        ],
        "model": "Links-C3U-DI04",
        "price_cny": 210,
        "id": "a30e77a0-4e47-4de2-9cb8-319e87e243de"
      },
      {
        "matrix": [
          0,
          0,
          0,
          96,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0
        ],
        "model": "Links-C3U-DO04",
        "price_cny": 220,
        "id": "669c7d0f-79c4-4daf-ac8e-e1a49ab7da6e"
      },
      {
        "matrix": [
          0,
          0,
          48,
          48,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0
        ],
        "model": "Links-C3U-DIO04",
        "price_cny": 220,
        "id": "e441cce3-e10d-43b3-9fd6-536aecc3dbc9"
      },
      {
        "matrix": [
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          8,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0
        ],
        "model": "Links-C3U-ABZ-02",
        "price_cny": 190,
        "id": "d1fe8aa8-5551-4c27-928a-c936d35567c5"
      },
      {
        "matrix": [
          0,
          0,
          0,
          0,
          0,
          0,
          10,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0
        ],
        "model": "Links-C3U-CAN-10",
        "price_cny": 250,
        "id": "83af9f28-0743-457e-9642-f78ae6a48a21"
      },
      {
        "matrix": [
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          8,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0
        ],
        "model": "Links-C3U-ABZ-01",
        "price_cny": 150,
        "id": "362f45df-9a50-478f-99a6-e575398ae8d8"
      },
      {
        "matrix": [
          0,
          0,
          0,
          0,
          0,
          0,
          2,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0
        ],
        "model": "Links-C3U-CAN",
        "price_cny": 80,
        "id": "25110b3a-2d29-46c6-a287-edb9e50f60ee"
      },
      {
        "matrix": [
          0,
          0,
          0,
          0,
          0,
          0,
          4,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0
        ],
        "model": "Links-C3U-CAN-4",
        "price_cny": 150,
        "id": "257d14e0-dc9e-4d82-9483-790f21bd6421"
      },
      {
        "matrix": [
          0,
          0,
          0,
          0,
          0,
          16,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0
        ],
        "model": "Links-C3U-SIO02-16",
        "price_cny": 450,
        "id": "195c7875-b5b8-4d12-b524-10370aabe9ad"
      },
      {
        "matrix": [
          0,
          0,
          0,
          0,
          0,
          16,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0
        ],
        "model": "Links-C3U-SIO03-16",
        "price_cny": 350,
        "id": "c6699f7e-cdb5-41d0-9155-7610df66ef42"
      },
      {
        "matrix": [
          8,
          0,
          8,
          8,
          2,
          0,
          0,
          12,
          2,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          6,
          0,
          0,
          0
        ],
        "model": "Links-IPC-DAQ-08",
        "price_cny": 90,
        "id": "cc9f1c93-96d6-48ac-94e1-bf9b0f4d50f9"
      },
      {
        "matrix": [
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          4,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0
        ],
        "model": "Links-IPC-GTS-01",
        "price_cny": 120,
        "id": "5574c98c-210b-499c-9947-ea6b00733f85"
      },
      {
        "matrix": [
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          8,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0
        ],
        "model": "Links-C3U-ABZ-03",
        "price_cny": 190,
        "id": "189a3eaf-a431-4777-bf14-aa9f9fdeae81"
      }
    ]

# 输入格式：21个元素的数组，对应21种通道类型
requirements_input = [
      8,
      8,
      8,
      8,
      0,
      16,
      2,
      12,
      2,
      0,
      0,
      0,
      0,
      0,
      0,
      0,
      0,
      6,
      0,
      9,
      5
    ]


# 通道类型名称（对应 matrix 的 21 个位置）
channel_types = [
    "analogInputChannels",
    "analogOutputChannels",
    "digitalInputChannels",
    "digitalOutputChannels",
    "digitalIOChannels",
    "serialPortChannels",
    "canBusChannels",
    "pwmOutputChannels",
    "encoderChannels",
    "ssiBusChannels",
    "spiBusChannels",
    "i2cBusChannels",
    "pcmLvdChannels",
    "bissCChannels",
    "afdxChannels",
    "ppsPulseChannels",
    "rtdResistanceChannels",
    "differentialInputChannels",
    "milStd1553BChannels",
    "timerCounterChannels",
    "relayOutputChannels"
]

# 提取所有板卡数据
# input_data 现在直接是板卡数组，不再需要 each_card 这一层
all_cards = input_data

n_cards = len(all_cards)
print(f"板卡总数: {n_cards}")
print("=" * 80)

# 构建资源矩阵（每行是一张板卡，每列是一种通道类型）
# A[i, j] 表示第 i 张板卡提供第 j 种通道的数量
resource_matrix = []
prices = []
models = []

for card in all_cards:
    models.append(card["model"])
    prices.append(card["price_cny"])
    resource_matrix.append(card["matrix"])

# 转换为 numpy 数组
A = np.array(resource_matrix)  # shape: (n_cards, 21)
prices = np.array(prices)

print("板卡信息:")
for i, (model, price) in enumerate(zip(models, prices)):
    print(f"  [{i}] {model:25s} - 价格{price:4d}")
print()

print("资源矩阵 (每行一张板卡):")
print("行数(板卡数):", A.shape[0], "列数(通道类型数):", A.shape[1])
print(A)
print()

# 设置需求约束（根据实际需求修改）
# 转换为 numpy 数组
b_requirements = np.array(requirements_input)

# 打印需求信息
print("需求向量:")
for i, (req, ch_type) in enumerate(zip(requirements_input, channel_types)):
    if req > 0:
        print(f"  [{i:2d}] {ch_type:30s}: {req:3d}")
print()

# 诊断：检查每种通道类型的可用性
print("需求可行性检查:")
print("-" * 80)
for i, channel_type in enumerate(channel_types):
    if b_requirements[i] > 0:
        # 计算该通道类型在所有板卡中的最大可用量
        max_available = A[:, i].sum()  # 所有板卡该通道的总和
        max_single_card = A[:, i].max()  # 单张板卡该通道的最大值
        status = "[OK]" if max_available >= b_requirements[i] else "[不足]"
        print(f"{status} {channel_type:25s}: 需求 {b_requirements[i]:3.0f}, "
              f"可用总量 {max_available:4.0f}, 单卡最大 {max_single_card:3.0f}")
print()

# 识别无法满足的需求并放松约束
unsatisfied_requirements = []
b_requirements_adjusted = b_requirements.copy()

for i, channel_type in enumerate(channel_types):
    if b_requirements[i] > 0:
        max_available = A[:, i].sum()
        if max_available < b_requirements[i]:
            # 记录无法满足的需求
            unsatisfied_requirements.append({
                "channel_type": channel_type,
                "required": int(b_requirements[i]),
                "available": int(max_available)
            })
            # 放松约束
            b_requirements_adjusted[i] = 0

if unsatisfied_requirements:
    print("发现无法满足的需求，将自动放松约束:")
    print("-" * 80)
    for item in unsatisfied_requirements:
        print(f"  [警告] {item['channel_type']:25s}: 需求 {item['required']:3d}, 最大可用 {item['available']:3d}")
    print()

# 目标函数：最小化成本
c = prices

# 约束条件：A.T @ x >= b_requirements_adjusted
# 即：sum(x[i] * A[i, j]) >= b_requirements_adjusted[j] for all j
# 转换为 linprog 格式：-A.T @ x <= -b_requirements_adjusted
A_ub = -A.T
b_ub = -b_requirements_adjusted

# 变量边界：每种板卡数量 x[i] >= 0（整数约束需要用 integrality 参数）
bounds = [(0, None)] * n_cards

# 求解（添加整数约束，因为板卡数量必须是整数）
result = linprog(
    c=c, 
    A_ub=A_ub, 
    b_ub=b_ub, 
    bounds=bounds, 
    method='highs',
    integrality=[1] * n_cards  # 1 表示该变量必须是整数
)

print("=" * 80)
if result.success:
    print("[优化成功!]")
    print()
    
    # 显示无法满足的需求
    if unsatisfied_requirements:
        print("无法满足的需求:")
        for item in unsatisfied_requirements:
            print(f"  [警告] {item['channel_type']:25s}: 原始需求 {item['required']:3d}, 最大可用 {item['available']:3d}")
        print()
    
    print("最优采购方案:")
    total_cost = 0
    for i, quantity in enumerate(result.x):
        if quantity > 0.01:  # 只显示数量 > 0 的板卡
            cost = quantity * prices[i]
            print(f"  {models[i]:25s}: {int(quantity):2d} 块 × {prices[i]:4d}元 = {cost:6.0f}元")
            total_cost += cost
    print()
    print(f"总成本: {total_cost:.0f}元")
    print()
    
    # 验证满足的通道需求
    satisfied_channels = A.T @ result.x
    print("满足的通道需求:")
    has_output = False
    for i, channel_type in enumerate(channel_types):
        if b_requirements[i] > 0 or satisfied_channels[i] > 0.01:
            status = "[OK]" if satisfied_channels[i] >= b_requirements[i] else "[不足]"
            print(f"  {status} {channel_type:25s}: {satisfied_channels[i]:5.0f} (需求: {b_requirements[i]:5.0f})")
            has_output = True
    if not has_output:
        print("  (无有效通道需求)")
else:
    print("✗ 求解失败:", result.message)
