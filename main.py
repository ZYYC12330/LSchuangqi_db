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
    
    # # 用于收集处理后的IO板卡数据
    # io_processed_data = []
        
    # # 导入IO板卡选型数据
    # io_path = 'sample/IO板卡选型.csv'
    # if os.path.exists(io_path):
    #     io_df = pd.read_csv(io_path)
    #     for _, row in io_df.iterrows():
    #         # 统一通讯协议和通信协议为"通信协议"
    #         category = row['分类']
    #         if category == '通讯协议':
    #             category = '通信协议'
            
    #         # 处理type列中的括号内容
    #         type_value = row['类型']
    #         is_isolated = None
            
    #         if type_value:
    #             # 提取括号内容
    #             bracket_match = re.search(r'[（(](.*?)[）)]', type_value)
    #             if bracket_match:
    #                 bracket_content = bracket_match.group(1)
    #                 # 判断括号内容
    #                 if '非隔离' in bracket_content:
    #                     is_isolated = False
    #                     # 只删除包含"非隔离"的括号和内容
    #                     type_value = re.sub(r'[（(].*?非隔离.*?[）)]', '', type_value).strip()
    #                 elif '隔离' in bracket_content:
    #                     is_isolated = True
    #                     # 只删除包含"隔离"的括号和内容
    #                     type_value = re.sub(r'[（(].*?隔离.*?[）)]', '', type_value).strip()
    #                 # 其他内容的括号保留，不删除
            
    #         # 确保type列内容结尾是"板卡"
    #         if type_value:
    #             if type_value.endswith('板卡'):
    #                 # 已经是"板卡"结尾，保持不变
    #                 pass
    #             elif type_value.endswith('卡'):
    #                 # 以"卡"结尾但不是"板卡"，替换为"板卡"
    #                 type_value = type_value[:-1] + '板卡'
    #             else:
    #                 # 其他情况，添加"板卡"
    #                 type_value = type_value + '板卡'
            
    #         # 处理价格和数量
    #         price_cny = float(row['报价（￥）'].replace('￥', '').replace(',', '').strip()) if row['报价（￥）'] else None
    #         quantity = int(row['数量']) if row['数量'] else None
    #         total_amount_cny = float(row['总价（￥）'].replace('￥', '').replace(',', '').strip()) if row['总价（￥）'] else None
            
    #         await prisma.iocard_selection.create({
    #             'category': category,
    #             'type': type_value,
    #             'model': row['型号'],
    #             'brief_description': row['描述（精简）'],
    #             'detailed_description': row['描述（详细）'],
    #             'brand': row['品牌'],
    #             'price_cny': price_cny,
    #             'quantity': quantity,
    #             'total_amount_cny': total_amount_cny,
    #             'supported_series': row['支持的系列'],
    #             'is_isolated': is_isolated
    #         })
            
    #         # 收集处理后的数据用于写入CSV
    #         io_processed_data.append({
    #             '分类': category,
    #             '类型': type_value,
    #             '型号': row['型号'],
    #             '描述（精简）': row['描述（精简）'],
    #             '描述（详细）': row['描述（详细）'],
    #             '品牌': row['品牌'],
    #             '报价（￥）': price_cny,
    #             '数量': quantity,
    #             '总价（￥）': total_amount_cny,
    #             '支持的系列': row['支持的系列'],
    #             '是否隔离': is_isolated
    #         })
        
    #     print(f'成功导入 {len(io_df)} 条IO板卡选型数据')
        
    #     # 写入CSV文件
    #     output_path = 'output/IO板卡选型——extend.csv'
    #     os.makedirs(os.path.dirname(output_path), exist_ok=True)
    #     output_df = pd.DataFrame(io_processed_data)
    #     output_df.to_csv(output_path, index=False, encoding='utf-8-sig')
    #     print(f'成功写入CSV文件: {output_path}')
    # else:
    #     print(f'文件 {io_path} 不存在')

    # 导入仿真机选型数据
    sim_path = 'sample/仿真机选型.csv'
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
                'price_cny': float(row['报价（￥）'].replace('￥', '').replace(',', '').strip()) if row['报价（￥）'] else None,
                'quantity': int(row['数量']) if row['数量'] else None,
                'total_amount_cny': float(row['总价（￥）'].replace('￥', '').replace(',', '').strip()) if row['总价（￥）'] else None,
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