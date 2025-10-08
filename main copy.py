import pandas as pd
from prisma import Prisma
import asyncio
import os
import sys

# 设置标准输出和标准错误的编码为 UTF-8
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

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
                'series': row['系列']
            })
        print(f'成功导入 {len(sim_df)} 条仿真机选型数据')
    else:
        print(f'文件 {sim_path} 不存在')


    # 断开数据库连接
    await prisma.disconnect()

if __name__ == '__main__':
    asyncio.run(main())