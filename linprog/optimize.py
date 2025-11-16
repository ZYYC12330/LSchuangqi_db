import numpy as np
from scipy.optimize import linprog
import json
from typing import List, Dict, Any, Tuple
from process_dnf import CHANNEL_COUNT_FIELDS

# 通道类型：直接使用 process_dnf.py 中的 CHANNEL_COUNT_FIELDS（39个字段）
CHANNEL_TYPES = CHANNEL_COUNT_FIELDS

# 通道类型数量（39个）
CHANNEL_COUNT = len(CHANNEL_COUNT_FIELDS)


def optimize_card_selection_core(
    linprog_input_data: List[Dict[str, Any]],
    linprog_requiremnets: List[int]
) -> Dict[str, Any]:
    """
    板卡选型优化核心逻辑
    
    Args:
        linprog_input_data: process_dnf输出的板卡数据数组（包含id, matrix_channel_count, model, price_cny, original）
        linprog_requiremnets: process_dnf输出的需求数组（CHANNEL_COUNT个元素）
    
    Returns:
        包含优化结果的字典，格式与 OptimizationResponse 对应
    """
    # 1. 数据验证
    if len(linprog_requiremnets) != CHANNEL_COUNT:
        raise ValueError(
            f"linprog_requiremnets 必须有 {CHANNEL_COUNT} 个元素，当前有 {len(linprog_requiremnets)} 个"
        )

    if len(linprog_input_data) == 0:
        raise ValueError("linprog_input_data 中没有板卡数据")

    # 2. 转换输入数据格式
    all_cards = []
    for idx, item in enumerate(linprog_input_data):
        # 如果 item 是列表，则展开处理（处理嵌套情况）
        if isinstance(item, list):
            for sub_idx, sub_item in enumerate(item):
                if not isinstance(sub_item, dict):
                    raise ValueError(
                        f"linprog_input_data 中的第 {idx} 个元素是列表，但列表中的第 {sub_idx} 个元素应该是字典类型，实际是 {type(sub_item).__name__} 类型"
                    )
                all_cards.append({
                    'id': str(sub_item.get('id', '')),
                    'matrix_channel_count': sub_item.get('matrix_channel_count', []),
                    'model': sub_item.get('model', ''),
                    'price_cny': sub_item.get('price_cny', 0),
                    'original': sub_item.get('original', None)
                })
        elif isinstance(item, dict):
            all_cards.append({
                'id': str(item.get('id', '')),
                'matrix_channel_count': item.get('matrix_channel_count', []),
                'model': item.get('model', ''),
                'price_cny': item.get('price_cny', 0),
                'original': item.get('original', None)
            })
        else:
            raise ValueError(
                f"linprog_input_data 中的第 {idx} 个元素应该是字典或列表类型，但实际是 {type(item).__name__} 类型"
            )

    requirements = linprog_requiremnets
    n_cards = len(all_cards)

    # 3. 验证每个板卡的 matrix_channel_count 长度
    for idx, card in enumerate(all_cards):
        if len(card['matrix_channel_count']) != CHANNEL_COUNT:
            raise ValueError(
                f"板卡 [{idx}] {card['model']} 的 matrix_channel_count 必须有 {CHANNEL_COUNT} 个元素，当前有 {len(card['matrix_channel_count'])} 个"
            )

    # 4. 构建资源矩阵
    resource_matrix = []
    prices = []
    models = []
    card_ids = []
    originals = []

    for card in all_cards:
        models.append(card['model'])
        prices.append(card['price_cny'])
        card_ids.append(card['id'])
        originals.append(card['original'])
        resource_matrix.append(card['matrix_channel_count'])

    A = np.array(resource_matrix)  # shape: (n_cards, CHANNEL_COUNT)
    prices = np.array(prices)
    b_requirements = np.array(requirements)

    # 5. 生成需求摘要
    requirements_summary = []
    for i, (req, ch_type) in enumerate(zip(requirements, CHANNEL_TYPES)):
        if req > 0:
            requirements_summary.append({
                "index": i,
                "channel_type": ch_type,
                "required": req
            })

    # 6. 线性规划求解（板卡数量无限，无需可行性检查）
    c = prices
    A_ub = -A.T
    b_ub = -b_requirements
    bounds = [(0, None)] * n_cards

    result = linprog(
        c=c,
        A_ub=A_ub,
        b_ub=b_ub,
        bounds=bounds,
        method='highs',
        integrality=[1] * n_cards
    )

    if not result.success:
        return {
            "success": False,
            "message": f"优化求解失败: {result.message}",
            "total_cards": n_cards,
            "requirements_summary": requirements_summary,
            "optimized_solution": None,
            "total_cost": None,
            "channel_satisfaction": None
        }

    # 9. 构建优化方案
    optimized_solution = []
    total_cost = 0

    for i, quantity in enumerate(result.x):
        if quantity > 0.01:
            qty = int(quantity)
            cost = qty * prices[i]
            optimized_solution.append({
                "model": models[i],
                "quantity": qty,
                "unit_price": int(prices[i]),
                "total_price": int(cost),
                "id": card_ids[i],
                "original": originals[i]
            })
            total_cost += cost

    # 10. 计算实际满足的通道需求
    satisfied_channels = A.T @ result.x
    channel_satisfaction = []

    for i, channel_type in enumerate(CHANNEL_TYPES):
        if b_requirements[i] > 0 or satisfied_channels[i] > 0.01:
            satisfied = int(satisfied_channels[i])
            required = int(b_requirements[i])
            status = "OK" if satisfied >= required else "不足"

            channel_satisfaction.append({
                "channel_type": channel_type,
                "required": required,
                "satisfied": satisfied,
                "status": status
            })

    # 构建响应消息
    message = "优化成功"

    return {
        "success": True,
        "message": message,
        "total_cards": n_cards,
        "requirements_summary": requirements_summary,
        "optimized_solution": optimized_solution,
        "total_cost": int(total_cost),
        "channel_satisfaction": channel_satisfaction
    }


# ================= 以下为测试代码 =================

# 输入数据（每个分组代表一类需求的可选板卡）
linprog_input_data = [
      {
        "id": "82",
        "matrix_channel_count": [
          0,
          0,
          0,
          0,
          0,
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
          0,
          0,
          0,
          0,
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
        "original": [
          "16路RS422/485，3Mbps"
        ]
      },
      {
        "id": "81",
        "matrix_channel_count": [
          0,
          0,
          0,
          0,
          0,
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
          0,
          0,
          0,
          0,
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
        "original": [
          "16路RS422/485，3Mbps"
        ]
      },
      {
        "id": "97",
        "matrix_channel_count": [
          0,
          0,
          0,
          0,
          0,
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
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
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
        "model": "ESI-210",
        "price_cny": 40,
        "original": [
          "双口1553B耦合器"
        ]
      },
      {
        "id": "98",
        "matrix_channel_count": [
          0,
          0,
          0,
          0,
          0,
          0,
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
          0,
          0,
          0,
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
        "model": "ESI-410",
        "price_cny": 60,
        "original": [
          "双口1553B耦合器"
        ]
      },
      {
        "id": "99",
        "matrix_channel_count": [
          0,
          0,
          0,
          0,
          0,
          0,
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
          0,
          0,
          0,
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
        "model": "ESI-810",
        "price_cny": 80,
        "original": [
          "双口1553B耦合器"
        ]
      },
      {
        "id": "106",
        "matrix_channel_count": [
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
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
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
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
        "model": "Links-C3U-AFDX-02",
        "price_cny": 980,
        "original": [
          "4个10/100/10 Base-T接口，RJ-45连接器，IEEE802.3x Support"
        ]
      },
      {
        "id": "7",
        "matrix_channel_count": [
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
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
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
        "original": [
          "高精度模拟量采集卡；通道数：8"
        ]
      },
      {
        "id": "8",
        "matrix_channel_count": [
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
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
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
        "original": [
          "高精度模拟量采集卡；通道数：8"
        ]
      },
      {
        "id": "9",
        "matrix_channel_count": [
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
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
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
        "original": [
          "高精度模拟量采集卡；通道数：8"
        ]
      },
      {
        "id": "13",
        "matrix_channel_count": [
          0,
          0,
          0,
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
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
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
        "original": [
          "CAN总线接口，4个高速通道，16Mhz控制速率， 1Mbps传输率，10V隔离，支持CAN2.0A/B协议"
        ]
      },
      {
        "id": "16",
        "matrix_channel_count": [
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
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
        "model": "Links-IPCe-Profinet",
        "price_cny": 150,
        "original": [
          "双口1553B耦合器"
        ]
      },
      {
        "id": "1",
        "matrix_channel_count": [
          16,
          0,
          16,
          32,
          0,
          0,
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
          0,
          0,
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
        "original": [
          "高精度模拟量采集卡；通道数：8"
        ]
      },
      {
        "id": "2",
        "matrix_channel_count": [
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
          0,
          0,
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
        "model": "Links-IPCe-DAQ-06",
        "price_cny": 190,
        "original": [
          "高精度模拟量采集卡；通道数：8"
        ]
      },
      {
        "id": "3",
        "matrix_channel_count": [
          32,
          16,
          0,
          0,
          16,
          16,
          0,
          0,
          0,
          0,
          0,
          1,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
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
        "original": [
          "高精度模拟量采集卡；通道数：8"
        ]
      },
      {
        "id": "4",
        "matrix_channel_count": [
          8,
          0,
          4,
          2,
          8,
          8,
          12,
          2,
          6,
          6,
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
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          2
        ],
        "model": "Links-IPC-DAQ-08",
        "price_cny": 90,
        "original": [
          "高精度模拟量采集卡；通道数：8"
        ]
      },
      {
        "id": "25",
        "matrix_channel_count": [
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
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
        "model": "Links-PCI-RFM-01",
        "price_cny": 220,
        "original": [
          "反射内存卡：PCI接口，256M内存, 16K FIFOs, 多模接口，实时系统驱动"
        ]
      },
      {
        "id": "26",
        "matrix_channel_count": [
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
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
        "model": "Links-PCIE-RFM-04",
        "price_cny": 230,
        "original": [
          "反射内存卡：PCI接口，256M内存, 16K FIFOs, 多模接口，实时系统驱动"
        ]
      },
      {
        "id": "29",
        "matrix_channel_count": [
          4,
          0,
          4,
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
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          4,
          4,
          0
        ],
        "model": "Links-IPC-GTS-01",
        "price_cny": 120,
        "original": [
          "高精度模拟量采集卡；通道数：8"
        ]
      },
      {
        "id": "30",
        "matrix_channel_count": [
          8,
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
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          8,
          8,
          8,
          0
        ],
        "model": "Links-IPC-GTS-02",
        "price_cny": 190,
        "original": [
          "高精度模拟量采集卡；通道数：8"
        ]
      },
      {
        "id": "35",
        "matrix_channel_count": [
          16,
          0,
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
          0,
          0,
          0,
          0,
          0,
          0,
          0,
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
        "original": [
          "高精度模拟量采集卡；通道数：8"
        ]
      },
      {
        "id": "38",
        "matrix_channel_count": [
          8,
          0,
          4,
          16,
          8,
          8,
          12,
          2,
          6,
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
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          2
        ],
        "model": "Links-C3U-DAQ-01",
        "price_cny": 250,
        "original": [
          "高精度模拟量采集卡；通道数：8"
        ]
      },
      {
        "id": "39",
        "matrix_channel_count": [
          16,
          0,
          16,
          32,
          0,
          0,
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
          0,
          0,
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
        "original": [
          "高精度模拟量采集卡；通道数：8"
        ]
      },
      {
        "id": "41",
        "matrix_channel_count": [
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
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
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
        "original": [
          "高精度模拟量采集卡；通道数：8"
        ]
      },
      {
        "id": "42",
        "matrix_channel_count": [
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
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
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
        "original": [
          "高精度模拟量采集卡；通道数：8"
        ]
      },
      {
        "id": "43",
        "matrix_channel_count": [
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
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
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
        "model": "Links-C3U-AI-04",
        "price_cny": 250,
        "original": [
          "高精度模拟量采集卡；通道数：8"
        ]
      },
      {
        "id": "72",
        "matrix_channel_count": [
          0,
          0,
          0,
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
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
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
        "original": [
          "CAN总线接口，4个高速通道，16Mhz控制速率， 1Mbps传输率，10V隔离，支持CAN2.0A/B协议"
        ]
      },
      {
        "id": "73",
        "matrix_channel_count": [
          0,
          0,
          0,
          0,
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
          0,
          0,
          0,
          0,
          0,
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
        "original": [
          "CAN总线接口，4个高速通道，16Mhz控制速率， 1Mbps传输率，10V隔离，支持CAN2.0A/B协议"
        ]
      },
      {
        "id": "76",
        "matrix_channel_count": [
          0,
          0,
          0,
          0,
          0,
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
          0,
          0,
          0,
          0,
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
        "original": [
          "16路RS422/485，3Mbps"
        ]
      },
      {
        "id": "77",
        "matrix_channel_count": [
          0,
          0,
          0,
          0,
          0,
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
          0,
          0,
          0,
          0,
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
        "original": [
          "16路RS422/485，3Mbps"
        ]
      },
      {
        "id": "78",
        "matrix_channel_count": [
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
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
        "original": [
          "16路RS422/485，3Mbps"
        ]
      },
      {
        "id": "111",
        "matrix_channel_count": [
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
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
          0
        ],
        "model": "Links-C3U-RTD01",
        "price_cny": 250,
        "original": [
          "PXI接口，10通道，12位分辨率，0Ω to 4kΩ，提供实时系统驱动"
        ]
      },
      {
        "id": "112",
        "matrix_channel_count": [
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
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
          0
        ],
        "model": "Links-C3U-RTD02",
        "price_cny": 350,
        "original": [
          "PXI接口，10通道，12位分辨率，0Ω to 4kΩ，提供实时系统驱动"
        ]
      },
      {
        "id": "116",
        "matrix_channel_count": [
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
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
          0
        ],
        "model": "Links-C3U-RTD05",
        "price_cny": 390,
        "original": [
          "通道数：8；电阻范围：3欧～100欧；分辨率：0.125欧；精度：±0.1%±0.125欧； 连接器：DB-37公座"
        ]
      },
      {
        "id": "117",
        "matrix_channel_count": [
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
          0,
          0,
          0,
          0,
          0,
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
          0
        ],
        "model": "Links-C3U-RTD06",
        "price_cny": 210,
        "original": [
          "通道数：8；电阻范围：3欧～100欧；分辨率：0.125欧；精度：±0.1%±0.125欧； 连接器：DB-37公座",
          "高精度模拟量采集卡；通道数：8"
        ]
      },
      {
        "id": "118",
        "matrix_channel_count": [
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
          0,
          0,
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
          0
        ],
        "model": "Links-C3U-RTD07",
        "price_cny": 350,
        "original": [
          "高精度模拟量采集卡；通道数：8"
        ]
      },
      {
        "id": "119",
        "matrix_channel_count": [
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
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
          0
        ],
        "model": "Links-C3U-RTD08",
        "price_cny": 350,
        "original": [
          "通道数：8；电阻范围：3欧～100欧；分辨率：0.125欧；精度：±0.1%±0.125欧； 连接器：DB-37公座"
        ]
      }
    ]

# 输入格式：21个元素的数组，对应21种通道类型
linprog_requiremnets = [
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
      4,
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
      10,
      0,
      0,
      0,
      0,
      0,
      0,
      0,
      0,
      0
    ]

def main():
    """
    主函数：用于测试优化功能
    可以单独运行此文件来测试优化逻辑
    """
    # 调用优化函数
    try:
        result = optimize_card_selection_core(
            linprog_input_data=linprog_input_data,
            linprog_requiremnets=linprog_requiremnets
        )

        print("=" * 80)
        print(result)
        print("=" * 80)
        if result['success']:
            print("[优化成功!]")
            print(f"消息: {result['message']}")
            print()

            # 显示无法满足的需求
            if result.get('unsatisfied_requirements'):
                print("无法满足的需求:")
                for item in result['unsatisfied_requirements']:
                    print(
                        f"  [警告] {item['channel_type']:25s}: 原始需求 {item['required']:3d}, 最大可用 {item['available']:3d}")
                print()

            # 显示最优采购方案
            if result.get('optimized_solution'):
                print("最优采购方案:")
                for card in result['optimized_solution']:
                    print(
                        f"  {card['model']:25s}: {card['quantity']:2d} 块 × {card['unit_price']:4d}元 = {card['total_price']:6d}元")
                print()
                print(f"总成本: {result.get('total_cost', 0):.0f}元")
                print()

            # 显示通道需求满足情况
            if result.get('channel_satisfaction'):
                print("满足的通道需求:")
                has_output = False
                for cs in result['channel_satisfaction']:
                    status = "[OK]" if cs['status'] == "OK" else "[不足]"
                    print(
                        f"  {status} {cs['channel_type']:30s}: {cs['satisfied']:5d} (需求: {cs['required']:5d})")
                    has_output = True
                if not has_output:
                    print("  (无有效通道需求)")
        else:
            print("[优化失败]")
            print(f"消息: {result['message']}")
            if result.get('unsatisfied_requirements'):
                print("\n无法满足的需求:")
                for item in result['unsatisfied_requirements']:
                    print(
                        f"  [警告] {item['channel_type']:25s}: 原始需求 {item['required']:3d}, 最大可用 {item['available']:3d}")

    except ValueError as e:
        print(f"[错误] {str(e)}")
    except Exception as e:
        print(f"[异常] {str(e)}")
        import traceback
        traceback.print_exc()

    print("=" * 80)


if __name__ == "__main__":
    main()

