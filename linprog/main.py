import numpy as np
from scipy.optimize import linprog
import json

# 输入数据（每个分组代表一类需求的可选板卡）
input_data = [
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
            0,
            0
        ],
        "model": "Links-IPC-AD-02",
        "price_cny": 190,
        "id": "d5fa8240-a251-4689-bd65-8cad87cf0977"
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
            0,
            0,
            64,
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
        "model": "Links-IPC-DIO64",
        "price_cny": 150,
        "id": "afa80456-23a2-4339-a075-e901d8bce95a"
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
            0,
            1
        ],
        "model": "Links-PCI-RFM-02",
        "price_cny": 220,
        "id": "593318c0-1143-4843-a4b3-ef017dd47501"
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
            1
        ],
        "model": "Links-PCIE-RFM-05",
        "price_cny": 230,
        "id": "cdf931b9-20f9-4f33-8145-e017fb51e79e"
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
            1
        ],
        "model": "Links-PCI-RFM-01",
        "price_cny": 220,
        "id": "aa0443c8-1419-45dd-828f-a635cab7926e"
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
            1
        ],
        "model": "Links-PCIE-RFM-04",
        "price_cny": 230,
        "id": "cd37c2c5-bb22-424e-a128-cc1cb9ba2d38"
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
        "model": "Links-C3U-AO-05",
        "price_cny": 250,
        "id": "75164c41-8f2f-4c4c-a6fc-cd33fb878979"
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
            0,
            0,
            0
        ],
        "model": "Links-C3U-SIO02-4",
        "price_cny": 150,
        "id": "cd4ad8dd-682a-4540-9c83-bcd42fd224f1"
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
            0,
            0
        ],
        "model": "Links-C3U-SIO02-8A",
        "price_cny": 180,
        "id": "08b6c634-6173-455d-96af-a4c8cddc6dc8"
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
            0
        ],
        "model": "Links-C3U-SIO03-8B",
        "price_cny": 150,
        "id": "eb0182f2-9d6f-4828-9607-f2f51dccb096"
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
            0,
            0
        ],
        "model": "Links-C3U-SIO03-8C",
        "price_cny": 150,
        "id": "9f3aa93b-3687-4eff-b1e6-e228257b467c"
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
            1
        ],
        "model": "Links-C3U-RFM-02",
        "price_cny": 240,
        "id": "a433bc77-2533-426b-a05a-d8323ed5428e"
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
            2,
            0,
            0,
            0
        ],
        "model": "Links-C3U-1553-2MA-ZK",
        "price_cny": 680,
        "id": "5d0d2628-1ece-4c8a-b6c9-cfad6398c3aa"
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
            2,
            0,
            0,
            0
        ],
        "model": "Links-IPC-1553-2MA-ZK",
        "price_cny": 680,
        "id": "bb316509-60f0-48b8-a6d9-eca4549a4af4"
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
            32,
            0
        ],
        "model": "Links-C3U-DO03",
        "price_cny": 150,
        "id": "d6295020-3760-4fe8-b8bd-f0106d84b07d"
    },
    {
        "matrix": [
            0,
            0,
            0,
            0,
            0,
            12,
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
            12,
            0,
            0,
            0,
            0
        ],
        "model": "Links-RS422-10M",
        "price_cny": 240,
        "id": "2f92731b-476b-47e9-8bf7-4eb583f77845"
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
            1
        ],
        "model": "Links-C3U-RFM-01",
        "price_cny": 240,
        "id": "414ee781-8676-4eb7-93ba-2c9de005b9db"
    }
]

# 输入格式：21个元素的数组，对应21种通道类型
requirements_input = [
    16,
    16,
    0,
    0,
    32,
    16,
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
    2,
    8,
    16,
    256
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
    "relayOutputChannels",
    "sharedMemoryChannels"
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
        print(
            f"  [警告] {item['channel_type']:25s}: 需求 {item['required']:3d}, 最大可用 {item['available']:3d}")
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
            print(
                f"  [警告] {item['channel_type']:25s}: 原始需求 {item['required']:3d}, 最大可用 {item['available']:3d}")
        print()

    print("最优采购方案:")
    total_cost = 0
    for i, quantity in enumerate(result.x):
        if quantity > 0.01:  # 只显示数量 > 0 的板卡
            cost = quantity * prices[i]
            print(
                f"  {models[i]:25s}: {int(quantity):2d} 块 × {prices[i]:4d}元 = {cost:6.0f}元")
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
            print(
                f"  {status} {channel_type:25s}: {satisfied_channels[i]:5.0f} (需求: {b_requirements[i]:5.0f})")
            has_output = True
    if not has_output:
        print("  (无有效通道需求)")
else:
    print("✗ 求解失败:", result.message)
