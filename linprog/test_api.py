"""
测试 FastAPI 板卡优化接口的示例客户端
"""
import requests
import json

# API 基础 URL
BASE_URL = "http://localhost:8000"

# 测试数据（简化版）
test_data = {
    "input_data": [
        {
            "each_card": [
                {
                    "matrix": [0, 8, 4, 0, 0, 2, 8, 8, 2, 0, 0, 0, 12, 0, 0, 0, 0, 0, 0, 0, 0],
                    "model": "Links-IPC-DAQ-08",
                    "price_cny": 90
                }
            ]
        },
        {
            "each_card": [
                {
                    "matrix": [0, 0, 0, 0, 0, 64, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                    "model": "Links-IPC-DIO64",
                    "price_cny": 150
                }
            ]
        },
        {
            "each_card": [
                {
                    "matrix": [0, 16, 16, 0, 0, 32, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                    "model": "Links-IPC-DAQ-05",
                    "price_cny": 250
                }
            ]
        }
    ],
    "requirements_input": [
        0,   # analogInputChannels
        8,   # analogOutputChannels
        8,   # digitalInputChannels
        0,   # digitalOutputChannels
        0,   # digitalIOChannels
        16,  # serialPortChannels
        2,   # canBusChannels
        12,  # pwmOutputChannels
        2,   # encoderChannels
        0,   # ssiBusChannels
        0,   # spiBusChannels
        0,   # i2cBusChannels
        0,   # pcmLvdChannels
        0,   # bissCChannels
        0,   # afdxChannels
        0,   # ppsPulseChannels
        0,   # rtdResistanceChannels
        0,   # differentialInputChannels
        0,   # milStd1553BChannels
        0,   # timerCounterChannels
        0    # relayOutputChannels
    ]
}


def test_root():
    """测试根路径"""
    print("=" * 80)
    print("测试 1: 根路径")
    print("=" * 80)
    
    response = requests.get(f"{BASE_URL}/")
    print(f"状态码: {response.status_code}")
    print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    print()


def test_get_channel_types():
    """测试获取通道类型"""
    print("=" * 80)
    print("测试 2: 获取通道类型列表")
    print("=" * 80)
    
    response = requests.get(f"{BASE_URL}/channel-types")
    print(f"状态码: {response.status_code}")
    data = response.json()
    print(f"通道类型数量: {data['count']}")
    print("通道类型列表:")
    for i, ch_type in enumerate(data['channel_types']):
        print(f"  [{i:2d}] {ch_type}")
    print()


def test_optimize():
    """测试优化接口"""
    print("=" * 80)
    print("测试 3: 板卡选型优化")
    print("=" * 80)
    
    response = requests.post(
        f"{BASE_URL}/optimize",
        json=test_data
    )
    
    print(f"状态码: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        
        print(f"\n优化结果: {result['success']}")
        print(f"消息: {result['message']}")
        print(f"板卡总数: {result['total_cards']}")
        
        print("\n需求摘要:")
        for req in result['requirements_summary']:
            print(f"  [{req['index']:2d}] {req['channel_type']:30s}: {req['required']:3d}")
        
        print("\n可行性检查:")
        for check in result['feasibility_checks']:
            print(f"  [{check['status']}] {check['channel_type']:30s}: "
                  f"需求 {check['required']:3d}, 可用 {check['available_total']:4d}, "
                  f"单卡最大 {check['max_single_card']:3d}")
        
        if result['optimized_solution']:
            print("\n最优采购方案:")
            for card in result['optimized_solution']:
                print(f"  {card['model']:25s}: {card['quantity']:2d} 块 × "
                      f"{card['unit_price']:4d}元 = {card['total_price']:6d}元")
            
            print(f"\n总成本: {result['total_cost']}元")
            
            print("\n满足的通道需求:")
            for ch in result['channel_satisfaction']:
                print(f"  [{ch['status']}] {ch['channel_type']:30s}: "
                      f"{ch['satisfied']:5d} (需求: {ch['required']:5d})")
        
    else:
        print(f"错误: {response.json()}")
    
    print()


if __name__ == "__main__":
    try:
        test_root()
        test_get_channel_types()
        test_optimize()
    except requests.exceptions.ConnectionError:
        print("错误: 无法连接到 API 服务器")
        print("请先运行: python api.py")
    except Exception as e:
        print(f"错误: {e}")


