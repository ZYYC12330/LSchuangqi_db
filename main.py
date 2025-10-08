import pandas as pd
from prisma import Prisma
import asyncio
import os
import sys
import re

# 设置标准输出和标准错误的编码为 UTF-8
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

async def parse_detailed_description(detailed_description):
    """
    解析详细描述字段，提取CPU、硬盘、内存和IO扩展插槽信息
    """
    # 初始化结果对象
    listss = {}

    # 定义正则表达式模式
    regex = {
        'cpu': r'CPU：(.*?)[；。]',
        'hard_disk': r'硬盘：(.*?)[；。]',
        'memory': r'内存：\s*(.*?)(?=；|\))',
        'slots': r'IO扩展插槽\s*：\s*(.*?)(?=。|；|$)'
    }

    # 遍历每个正则表达式进行匹配
    for key in regex:
        match = re.search(regex[key], detailed_description, re.IGNORECASE | re.DOTALL)
        if match and match.group(1):
            listss[key] = match.group(1).strip()
        else:
            print(f'未找到{key}的相关信息')
            listss[key] = None

    return listss

async def main():
    # 初始化Prisma客户端
    prisma = Prisma()
    await prisma.connect()
        
    # 导入IO板卡选型数据
    io_path = 'IO板卡选型.csv'
    if os.path.exists(io_path):
        io_df = pd.read_csv(io_path)
        for _, row in io_df.iterrows():
            await prisma.iocard_selection.create({
                'category': row['分类'],
                'type': row['类型'],
                'model': row['型号'],
                'brief_description': row['描述（精简）'],
                'detailed_description': row['描述（详细）'],
                'brand': row['品牌'],
                'price_cny': str(row['报价（￥）']),
                'quantity': int(row['数量']),
                'total_amount_cny': str(row['总价（￥）']),
                'supported_series': row['支持的系列']
            })
        print(f'成功导入 {len(io_df)} 条IO板卡选型数据')
    else:
        print(f'文件 {io_path} 不存在')

    # 导入仿真机选型数据
    sim_path = '仿真机选型.csv'
    if os.path.exists(sim_path):
        sim_df = pd.read_csv(sim_path)
        for _, row in sim_df.iterrows():
            # 解析详细描述字段
            parsed_data = await parse_detailed_description(row['描述（详细）'])

            await prisma.simmachine_selection.create({
                'category': row['分类'],
                'type': row['类型'],
                'model': row['型号'],
                'brief_description': row['描述（精简）'] ,
                'detailed_description': row['描述（详细）'],
                'manufacturer': row['制造商'],
                'price_cny': str(row['报价（￥）']),
                'quantity': int(row['数量']),
                'total_amount_cny': str(row['总价（￥）']),
                'series': row['系列'],
                'cpu': parsed_data.get('cpu'),
                'hard_disk': parsed_data.get('hard_disk'),
                'memory': parsed_data.get('memory'),
                'slots': parsed_data.get('slots')
            })
        print(f'成功导入 {len(sim_df)} 条仿真机选型数据')
    else:
        print(f'文件 {sim_path} 不存在')


    # 断开数据库连接
    await prisma.disconnect()

if __name__ == '__main__':
    asyncio.run(main())