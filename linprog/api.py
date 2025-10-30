from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import numpy as np
from scipy.optimize import linprog
import uvicorn
import json
from openpyxl import load_workbook, Workbook
from openpyxl.utils import get_column_letter
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
import os
from datetime import datetime
import requests

# 配置环境变量
API_KEY = os.getenv('API_KEY', 'sk-zzvwbcaxoss3')
FILE_SERVER_URL = os.getenv('FILE_SERVER_URL', 'https://demo.langcore.cn')


# API_KEY = os.getenv('API_KEY', 'sk-6zvekr4931xm')
# FILE_SERVER_URL = os.getenv('FILE_SERVER_URL', 'http://10.120.120.6:3008')


app = FastAPI(
    title="板卡选型优化 API",
    description="基于线性规划的板卡最优采购方案计算+excel生成",
    version="1.0.0"
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 通道类型名称（固定顺序）
CHANNEL_TYPES = [
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
    "sharedMemoryChannels",
    "lvdtRvdtSyncChannels"
]

# 通道类型数量（自动根据 CHANNEL_TYPES 长度计算）
CHANNEL_COUNT = len(CHANNEL_TYPES)

# 请求模型
class CardInfo(BaseModel):
    matrix: List[int] = Field(..., description=f"{CHANNEL_COUNT}个元素的数组，表示各通道类型的数量")
    model: str = Field(..., description="板卡型号")
    price_cny: int = Field(..., description="板卡价格（人民币）")
    id: str = Field(..., description="板卡唯一标识ID")

class OptimizationRequest(BaseModel):
    input_data: List[CardInfo] = Field(..., description="板卡库存数据，直接是板卡数组")
    requirements_input: List[int] = Field(..., description=f"{CHANNEL_COUNT}个元素的需求数组")

# 响应模型
class OptimizedCard(BaseModel):
    model: str
    quantity: int
    unit_price: int
    total_price: int
    id: str

class ChannelSatisfaction(BaseModel):
    channel_type: str
    required: int
    satisfied: int
    status: str

class FeasibilityCheck(BaseModel):
    channel_type: str
    required: int
    available_total: int
    max_single_card: int
    status: str

class OptimizationResponse(BaseModel):
    success: bool
    message: str
    total_cards: int
    requirements_summary: List[dict]
    feasibility_checks: List[FeasibilityCheck]
    optimized_solution: Optional[List[OptimizedCard]] = None
    total_cost: Optional[int] = None
    channel_satisfaction: Optional[List[ChannelSatisfaction]] = None
    unsatisfied_requirements: List[dict] = []


@app.get("/")
async def root():
    """API 根路径"""
    return {
        "message": "板卡选型优化 API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/channel-types")
async def get_channel_types():
    """获取所有通道类型列表"""
    return {
        "channel_types": CHANNEL_TYPES,
        "count": len(CHANNEL_TYPES)
    }


@app.post("/optimize", response_model=OptimizationResponse)
async def optimize_card_selection(request: OptimizationRequest):
    """
    板卡选型优化接口
    
    - **input_data**: 板卡数组，每个板卡包含 matrix（{CHANNEL_COUNT}元素数组）、model（型号）、price_cny（价格）、id（唯一标识）
    - **requirements_input**: 需求向量，{CHANNEL_COUNT}个元素对应{CHANNEL_COUNT}种通道类型
    
    返回最优采购方案，包括总成本和每种板卡的采购数量
    """
    try:
        # 1. 数据验证
        if len(request.requirements_input) != CHANNEL_COUNT:
            raise HTTPException(
                status_code=400,
                detail=f"requirements_input 必须有 {CHANNEL_COUNT} 个元素，当前有 {len(request.requirements_input)} 个"
            )
        
        # 2. 提取所有板卡数据
        # input_data 现在直接是板卡数组，不再需要 each_card 这一层
        all_cards = request.input_data
        
        if len(all_cards) == 0:
            raise HTTPException(status_code=400, detail="input_data 中没有板卡数据")
        
        n_cards = len(all_cards)
        
        # 3. 验证每个板卡的 matrix 长度
        for idx, card in enumerate(all_cards):
            if len(card.matrix) != CHANNEL_COUNT:
                raise HTTPException(
                    status_code=400,
                    detail=f"板卡 [{idx}] {card.model} 的 matrix 必须有 {CHANNEL_COUNT} 个元素，当前有 {len(card.matrix)} 个"
                )
        
        # 4. 构建资源矩阵
        resource_matrix = []
        prices = []
        models = []
        card_ids = []
        
        for card in all_cards:
            models.append(card.model)
            prices.append(card.price_cny)
            card_ids.append(card.id)
            resource_matrix.append(card.matrix)
        
        A = np.array(resource_matrix)  # shape: (n_cards, CHANNEL_COUNT)
        prices = np.array(prices)
        b_requirements = np.array(request.requirements_input)
        
        # 5. 生成需求摘要
        requirements_summary = []
        for i, (req, ch_type) in enumerate(zip(request.requirements_input, CHANNEL_TYPES)):
            if req > 0:
                requirements_summary.append({
                    "index": i,
                    "channel_type": ch_type,
                    "required": req
                })
        
        # 6. 需求可行性检查
        feasibility_checks = []
        
        for i, channel_type in enumerate(CHANNEL_TYPES):
            if b_requirements[i] > 0:
                max_available = int(A[:, i].sum())
                max_single_card = int(A[:, i].max())
                status = "OK" if max_available >= b_requirements[i] else "不足"
                
                feasibility_checks.append(FeasibilityCheck(
                    channel_type=channel_type,
                    required=int(b_requirements[i]),
                    available_total=max_available,
                    max_single_card=max_single_card,
                    status=status
                ))
        
        # 7. 识别无法满足的需求并放松约束
        unsatisfied_requirements = []
        b_requirements_adjusted = b_requirements.copy()
        
        for i, channel_type in enumerate(CHANNEL_TYPES):
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
        
        # 8. 线性规划求解（使用调整后的需求向量）
        c = prices
        A_ub = -A.T
        b_ub = -b_requirements_adjusted
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
            return OptimizationResponse(
                success=False,
                message=f"优化求解失败: {result.message}",
                total_cards=n_cards,
                requirements_summary=requirements_summary,
                feasibility_checks=feasibility_checks,
                unsatisfied_requirements=unsatisfied_requirements
            )
        
        # 9. 构建优化方案
        optimized_solution = []
        total_cost = 0
        
        for i, quantity in enumerate(result.x):
            if quantity > 0.01:
                qty = int(quantity)
                cost = qty * prices[i]
                optimized_solution.append(OptimizedCard(
                    model=models[i],
                    quantity=qty,
                    unit_price=int(prices[i]),
                    total_price=int(cost),
                    id=card_ids[i]
                ))
                total_cost += cost
        
        # 10. 计算实际满足的通道需求
        satisfied_channels = A.T @ result.x
        channel_satisfaction = []
        
        for i, channel_type in enumerate(CHANNEL_TYPES):
            if b_requirements[i] > 0 or satisfied_channels[i] > 0.01:
                satisfied = int(satisfied_channels[i])
                required = int(b_requirements[i])
                status = "OK" if satisfied >= required else "不足"
                
                channel_satisfaction.append(ChannelSatisfaction(
                    channel_type=channel_type,
                    required=required,
                    satisfied=satisfied,
                    status=status
                ))
        
        # 构建响应消息
        if unsatisfied_requirements:
            message = "优化成功（部分需求无法满足）"
        else:
            message = "优化成功"
        
        return OptimizationResponse(
            success=True,
            message=message,
            total_cards=n_cards,
            requirements_summary=requirements_summary,
            feasibility_checks=feasibility_checks,
            optimized_solution=optimized_solution,
            total_cost=int(total_cost),
            channel_satisfaction=channel_satisfaction,
            unsatisfied_requirements=unsatisfied_requirements
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"服务器错误: {str(e)}")


# ================= Excel 生成功能 =================

def generate_combined_excel(json_data: Dict[str, Any], template_path: str, output_path: str):
    """
    Generate combined Excel file with two sheets: quotation sheet and requirement matching preview

    Args:
        json_data: JSON data dictionary
        template_path: Excel template file path
        output_path: Output Excel file path

    Returns:
        str: Output file path
        float: Total amount
    """

    # 1. 先生成报价单（基于模板）
    wb = load_workbook(template_path)

    # 删除不需要的工作表，只保留第一个
    if len(wb.sheetnames) > 1:
        for sheet_name in wb.sheetnames[1:]:
            wb.remove(wb[sheet_name])

    # 重命名第一个工作表为"报价单"
    ws1 = wb.active
    ws1.title = "报价单"
    
    # 定义安全写入单元格的函数（默认上下左右居中）
    def safe_cell_write(ws, row, col, value):
        """安全地写入单元格值，避免合并单元格错误，并统一设置居中"""
        try:
            cell = ws.cell(row=row, column=col)
            # 检查单元格类型
            if cell.__class__.__name__ == 'MergedCell':
                # 如果是合并单元格，跳过写入
                return None
            cell.value = value
            cell.alignment = Alignment(horizontal='center', vertical='center')
            return cell
        except Exception as e:
            print(f"警告：无法写入单元格 ({row}, {col}): {e}")
            return None

    # 自动识别模板表头位置
    def detect_header_positions(ws):
        """在前50行内寻找包含关键表头的一行，返回该行号及列映射"""
        required_headers = ["设备类别", "型号", "数量", "单价", "总价"]
        optional_headers = ["序号", "税率", "应税", "总金额"]
        header_row = None
        header_map = {}

        max_rows = min(ws.max_row, 50)
        max_cols = min(ws.max_column, 30)

        for r in range(1, max_rows + 1):
            current_map = {}
            for c in range(1, max_cols + 1):
                v = ws.cell(row=r, column=c).value
                if isinstance(v, str):
                    text = v.strip()
                else:
                    text = v
                if text in required_headers + optional_headers:
                    current_map[text] = c
            # 至少匹配3个必需表头才认为找到
            if sum(1 for h in required_headers if h in current_map) >= 3:
                header_row = r
                header_map = current_map
                break

        return header_row, header_map

    # 处理报价单数据（自动识别新模板表头）
    header_row, header_map = detect_header_positions(ws1)
    start_row = (header_row + 1) if header_row else 13
    # 兼容多种格式：card、array
    result_items = json_data.get('card', json_data.get('array', []))
    raw_sim_items = json_data.get('raw_sim', [])
    
    # ========== 根据ID进行去重和合并 ==========
    def merge_items_by_id(items):
        """根据板卡ID对数据进行去重和合并（同一张卡满足多个需求）"""
        merged_dict = {}
        
        for item in items:
            # 兼容新旧两种格式
            if 'each_obj' in item:
                each_obj = item.get('each_obj', {})
            else:
                each_obj = item
            
            item_id = each_obj.get('id', '')
            if not item_id:
                # 如果没有ID，直接跳过
                continue
            
            if item_id not in merged_dict:
                # 第一次遇到这个ID，初始化
                merged_dict[item_id] = {
                    'id': item_id,
                    'originals': [],
                    'match_degrees': [],
                    'reasons': [],
                    'type': each_obj.get('type', ''),
                    'model': each_obj.get('model', ''),
                    'description': each_obj.get('description', each_obj.get('brief_description', '')),
                    'manufacturer': each_obj.get('manufacturer', ''),
                    'price_cny': each_obj.get('price_cny', 0),
                    'quantity': each_obj.get('quantity', 1),  # 取第一条记录的数量
                    'details': []
                }
            
            # 收集需要合并的字段（同一张卡的多个需求）
            original = each_obj.get('original', '')
            if original:
                merged_dict[item_id]['originals'].append(original)
            
            match_degree = each_obj.get('match_degree', each_obj.get('score', ''))
            if match_degree:
                merged_dict[item_id]['match_degrees'].append(str(match_degree))
            
            reason = each_obj.get('reason', '')
            if reason:
                merged_dict[item_id]['reasons'].append(reason)
            
            # 处理details（如果存在）
            if 'details' in each_obj and each_obj['details']:
                merged_dict[item_id]['details'].extend(each_obj['details'])
        
        # 将合并后的数据转换为列表
        merged_list = []
        for item_id, data in merged_dict.items():
            merged_item = {
                'id': data['id'],
                'original': '\n'.join(data['originals']),
                'match_degree': '\n'.join(data['match_degrees']),
                'reason': '\n'.join(data['reasons']),
                'type': data['type'],
                'model': data['model'],
                'description': data['description'],
                'manufacturer': data['manufacturer'],
                'price_cny': data['price_cny'],
                'quantity': data['quantity'],  # 不累加，保持原数量
                'details': data['details'] if data['details'] else None
            }
            merged_list.append(merged_item)
        
        return merged_list
    
    # 对 card 数据根据ID进行合并
    result_items = merge_items_by_id(result_items)
    
    current_row = start_row
    total_amount = 0

    # 处理 card 板卡数据（已合并）——适配新模板：只写“序号/设备类别/型号/数量/单价/总价”
    running_index = 1
    for each_obj in result_items:
        item_id = each_obj.get('id', '')
        price_cny = each_obj.get('price_cny', 0)
        quantity = each_obj.get('quantity', 1)

        # 计算总金额
        total_amount_cny = price_cny * quantity

        # 转数字
        try:
            if isinstance(price_cny, str):
                price_cny = float(price_cny.replace('￥', '').replace(',', ''))
            if isinstance(total_amount_cny, str):
                total_amount_cny = float(total_amount_cny.replace('￥', '').replace(',', ''))
        except (ValueError, AttributeError):
            price_cny = 0
            total_amount_cny = 0

        # 累加总价
        total_amount += total_amount_cny

        # 列索引（优先表头映射，回退旧模板列位）
        col_index = {
            '序号': header_map.get('序号', 2),
            '设备类别': header_map.get('设备类别', 2),
            '型号': header_map.get('型号', 7),
            '数量': header_map.get('数量', 11),
            '单价': header_map.get('单价', 10),
            '总价': header_map.get('总价', 12)
        }

        if col_index['序号']:
            safe_cell_write(ws1, current_row, col_index['序号'], running_index)
        if col_index['设备类别']:
            safe_cell_write(ws1, current_row, col_index['设备类别'], each_obj.get('type', ''))
        if col_index['型号']:
            safe_cell_write(ws1, current_row, col_index['型号'], each_obj.get('model', each_obj.get('type', '')))
        if col_index['数量']:
            safe_cell_write(ws1, current_row, col_index['数量'], quantity)
        if col_index['单价']:
            safe_cell_write(ws1, current_row, col_index['单价'], price_cny)
        if col_index['总价']:
            safe_cell_write(ws1, current_row, col_index['总价'], total_amount_cny)

        ws1.row_dimensions[current_row].height = None
        current_row += 1
        running_index += 1

    # 处理 raw_sim 机箱数据（同样写到新模板列）
    for item in raw_sim_items:
        sim_id = item.get('id', '')
        price_cny = item.get('price_cny', 0)
        quantity = item.get('quantity', 1)
        
        # 计算总金额
        total_amount_cny = price_cny * quantity
        
        # 转换价格为数字格式
        try:
            if isinstance(price_cny, str):
                price_cny = float(price_cny.replace('￥', '').replace(',', ''))
            if isinstance(total_amount_cny, str):
                total_amount_cny = float(total_amount_cny.replace('￥', '').replace(',', ''))
        except (ValueError, AttributeError):
            price_cny = 0
            total_amount_cny = 0
        
        # 累加总价
        total_amount += total_amount_cny
        
        # 列索引
        col_index = {
            '序号': header_map.get('序号', 2),
            '设备类别': header_map.get('设备类别', 2),
            '型号': header_map.get('型号', 7),
            '数量': header_map.get('数量', 11),
            '单价': header_map.get('单价', 10),
            '总价': header_map.get('总价', 12)
        }

        if col_index['序号']:
            safe_cell_write(ws1, current_row, col_index['序号'], running_index)
        if col_index['设备类别']:
            safe_cell_write(ws1, current_row, col_index['设备类别'], item.get('type', ''))
        if col_index['型号']:
            safe_cell_write(ws1, current_row, col_index['型号'], item.get('model', item.get('type', '')))
        if col_index['数量']:
            safe_cell_write(ws1, current_row, col_index['数量'], quantity)
        if col_index['单价']:
            safe_cell_write(ws1, current_row, col_index['单价'], price_cny)
        if col_index['总价']:
            safe_cell_write(ws1, current_row, col_index['总价'], total_amount_cny)
        
        # 设置行高为自动
        ws1.row_dimensions[current_row].height = None
        current_row += 1

    # 找到F列值为"小计"和"总计"的行，并填入总金额到L列
    subtotal_row = None
    total_row = None

    # 遍历所有行，寻找"小计"和"总计"（适配任意列）
    for row in range(1, ws1.max_row + 1):
        try:
            found_text = None
            for col in range(1, ws1.max_column + 1):
                val = ws1.cell(row=row, column=col).value
                if val in ("小计", "总计"):
                    found_text = val
                    break
            if found_text == "小计":
                subtotal_row = row
                write_col = header_map.get('总金额') or header_map.get('总价') or 12
                safe_cell_write(ws1, row, write_col, total_amount)
                ws1.row_dimensions[row].height = None
            elif found_text == "总计":
                total_row = row
                write_col = header_map.get('总金额') or header_map.get('总价') or 12
                safe_cell_write(ws1, row, write_col, total_amount)
                ws1.row_dimensions[row].height = None
        except Exception as e:
            print(f"警告：处理第{row}行时出错: {e}")
            continue

    print(f"找到小计行: {subtotal_row}, 总计行: {total_row}")
    print(f"填入总金额: {total_amount}")

    # 2. 创建需求匹配预览工作表
    ws2 = wb.create_sheet("需求匹配预览")

    # 设置表头
    headers = [
        "序号", "原始需求", "匹配依据", "匹配设备ID", "设备名称", "规格型号", "技术参数", "制造商",
        "数量", "单价(元)", "小计(元)"
    ]

    # 美化表头
    header_fill = PatternFill(start_color="4F81BD", end_color="4F81BD", fill_type="solid")
    header_font = Font(bold=True, color="FFFFFF", size=12)
    border = Border(left=Side(style='thin'), right=Side(style='thin'),
                   top=Side(style='thin'), bottom=Side(style='thick'))

    # 写入表头
    for col_num, header in enumerate(headers, 1):
        cell = ws2.cell(row=1, column=col_num, value=header)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = Alignment(horizontal="center", vertical="center")
        cell.border = border

    # 设置表头行高
    ws2.row_dimensions[1].height = 25

    # 从第2行开始写入数据
    current_row = 2
    total_amount = 0

    # 建立需求点与设备的映射关系（合并后的数据作为整体）
    demand_device_mapping = []

    for each_obj in result_items:
        # 合并后的数据，original已经是换行连接的多个需求
        original_text = each_obj.get('original', '')
        if original_text:
            # 将合并后的数据作为一个整体添加
            demand_device_mapping.append({
                'demand': original_text,  # 保持换行符
                'reason': each_obj.get('reason', ''),  # 保持换行符
                'device': each_obj
            })

    # 处理 raw_sim 机箱数据
    for item in raw_sim_items:
        # 机箱使用category作为需求
        demand = item.get('category', '机箱&CPU控制器')
        demand_device_mapping.append({
            'demand': demand,
            'reason': '',  # 机箱一般不需要匹配原因
            'device': item
        })

    # 写入数据行
    for idx, mapping in enumerate(demand_device_mapping, 1):
        demand = mapping['demand']
        reason = mapping['reason']
        device = mapping['device']

        # 写入数据行
        ws2.cell(row=current_row, column=1, value=idx)
        ws2.cell(row=current_row, column=2, value=demand)
        ws2.cell(row=current_row, column=3, value=reason)
        ws2.cell(row=current_row, column=4, value=device.get('id', ''))
        ws2.cell(row=current_row, column=5, value=device.get('type', ''))
        ws2.cell(row=current_row, column=6, value=device.get('model', ''))
        # 兼容字段：description -> detailed_description -> brief_description
        tech_desc = device.get('description', device.get('detailed_description', device.get('brief_description', '')))
        ws2.cell(row=current_row, column=7, value=tech_desc)
        ws2.cell(row=current_row, column=8, value=device.get('manufacturer', ''))
        ws2.cell(row=current_row, column=9, value=device.get('quantity', 1))

        # 计算单价
        price_cny = device.get('price_cny', 0)
        if isinstance(price_cny, str):
            price_cny = float(price_cny.replace('￥', '').replace(',', ''))
        ws2.cell(row=current_row, column=10, value=price_cny)

        # 小计 - 如果没有total_amount_cny，则计算
        total_amount_cny = device.get('total_amount_cny', 0)
        if isinstance(total_amount_cny, str):
            total_amount_cny = float(total_amount_cny.replace('￥', '').replace(',', ''))
        elif total_amount_cny == 0:
            # 如果没有提供total_amount_cny，则计算
            total_amount_cny = price_cny * device.get('quantity', 1)
        ws2.cell(row=current_row, column=11, value=total_amount_cny)

        # 美化数据行样式
        data_border = Border(left=Side(style='thin'), right=Side(style='thin'),
                           top=Side(style='thin'), bottom=Side(style='thin'))

        # 隔行换色
        if current_row % 2 == 0:
            row_fill = PatternFill(start_color="F2F2F2", end_color="F2F2F2", fill_type="solid")
        else:
            row_fill = PatternFill(start_color="FFFFFF", end_color="FFFFFF", fill_type="solid")

        data_font = Font(size=11)

        # 为每一列设置样式
        for col in range(1, 12):
            cell = ws2.cell(row=current_row, column=col)
            cell.font = data_font
            cell.fill = row_fill
            cell.border = data_border

            # 全部统一上下左右居中
            cell.alignment = Alignment(horizontal="center", vertical="center")

        # 对可能的多行文本开启换行，但保持居中
        ws2.cell(row=current_row, column=2).alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
        ws2.cell(row=current_row, column=3).alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
        ws2.cell(row=current_row, column=7).alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)

        # 设置行高为自动
        ws2.row_dimensions[current_row].height = None
        current_row += 1

    # 优化列宽，对ws1主报价单表自适应
    for col in range(1, ws1.max_column + 1):
        maxlen = 8
        for row in range(1, ws1.max_row + 1):
            val = ws1.cell(row=row, column=col).value
            if val is None:
                val = ""
            else:
                val = str(val)
            # 中文字符宽度更大，按比例增大
            try:
                chinese_count = sum(1 for ch in val if ord(ch)>127)
                eff_len = len(val) + chinese_count  # 中文计宽加权
            except:
                eff_len = len(val)
            if eff_len > maxlen:
                maxlen = eff_len
        ws1.column_dimensions[get_column_letter(col)].width = min(max(8, maxlen*1.8), 35)

    # ws2需求匹配预览表还是用固定列宽
    column_widths = [8, 35, 35, 25, 20, 18, 35, 15, 10, 15, 15]
    column_names = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K']
    for i, (width, col_name) in enumerate(zip(column_widths, column_names)):
        ws2.column_dimensions[col_name].width = width

    # 保存文件
    wb.save(output_path)
    return output_path, total_amount


def generate_excel_from_json_string(json_string: str, template_content: bytes) -> tuple:
    """
    Generate Excel file from JSON string and template file content

    Args:
        json_string: JSON data as string
        template_content: Excel template file content as bytes

    Returns:
        tuple: (output_file_path, total_amount)
    """
    try:
        # 解析JSON数据
        json_data = json.loads(json_string)

        # 使用项目temp目录而不是系统临时目录
        project_temp_dir = os.path.join(os.path.dirname(__file__), "temp")
        os.makedirs(project_temp_dir, exist_ok=True)

        # 生成唯一的文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        temp_template_path = os.path.join(project_temp_dir, f"template_{timestamp}.xlsx")
        output_path = os.path.join(project_temp_dir, f"output_{timestamp}.xlsx")

        # 写入模板文件
        with open(temp_template_path, 'wb') as f:
            f.write(template_content)

        try:
            # 生成Excel文件
            result_path, total_amount = generate_combined_excel(json_data, temp_template_path, output_path)
            return result_path, total_amount
        finally:
            # 清理临时模板文件
            try:
                if os.path.exists(temp_template_path):
                    os.unlink(temp_template_path)
            except:
                pass  # 忽略删除错误

    except json.JSONDecodeError as e:
        raise ValueError(f"无效的JSON数据: {str(e)}")
    except Exception as e:
        raise ValueError(f"生成Excel文件时出错: {str(e)}")


async def upload_file_to_server(file_path: str, token: str = None) -> Dict[str, Any]:
    """
    上传文件到服务器

    Args:
        file_path: 要上传的文件路径
        token: 认证token

    Returns:
        dict: 上传结果
    """
    try:
        headers = {}
        if token:
            headers['Authorization'] = f'Bearer {token}'

        with open(file_path, 'rb') as f:
            files = {'file': f}
            response = requests.post(
                f'{FILE_SERVER_URL}/api/file',
                files=files,
                headers=headers,
                timeout=30
            )

        result = {
            "success": response.status_code == 200,
            "status_code": response.status_code
        }

        if response.status_code == 200 and response.text:
            try:
                # 解析返回的JSON字符串
                response_data = json.loads(response.text)
                if response_data.get("status") == "success" and "data" in response_data:
                    file_id = response_data["data"].get("fileId")
                    if file_id:
                        # 构造完整的文件URL
                        full_url = f"{FILE_SERVER_URL}/api/file/{file_id}"
                        result["file_url"] = full_url
                        result["file_id"] = file_id
                        result["response"] = f"文件上传成功，访问地址: {full_url}"
                    else:
                        result["response"] = response.text
                else:
                    result["response"] = response.text
            except json.JSONDecodeError:
                # 如果不是JSON格式，直接返回原始文本
                result["response"] = response.text
        else:
            result["response"] = response.text if response.text else "上传成功"

        return result
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@app.post("/generate-excel")
async def generate_excel(json_data: Dict[str, Any], token: str = API_KEY):
    """
    生成Excel文件并自动上传

    - **json_data**: 包含配置数据的JSON对象
    - **token**: 认证token（默认为 API_KEY ）
    - **returns**: 生成和上传的结果
    """
    try:
        # 获取默认模板文件路径
        template_path = os.path.join(os.path.dirname(__file__), "空白输出模板.xlsx")

        # 验证模板文件是否存在
        if not os.path.exists(template_path):
            raise HTTPException(
                status_code=404,
                detail=f"默认模板文件不存在: {template_path}"
            )

        # 读取模板文件内容
        with open(template_path, 'rb') as template_file:
            template_content = template_file.read()

        # 将JSON数据转换为字符串
        json_string = json.dumps(json_data)

        # 生成Excel文件
        output_path, total_amount = generate_excel_from_json_string(json_string, template_content)

        # 上传文件到服务器
        upload_result = await upload_file_to_server(output_path, token)

        # 清理临时文件
        try:
            if os.path.exists(output_path):
                os.unlink(output_path)
        except:
            pass  # 忽略清理错误

        # 返回结果
        response_data = {
            "message": "Excel文件生成并上传成功",
            "total_amount": total_amount,
            "upload_result": upload_result
        }

        # 如果上传成功且有file_url，添加到响应中
        if upload_result.get("success") and "file_url" in upload_result:
            response_data["file_url"] = upload_result["file_url"]
            response_data["file_id"] = upload_result.get("file_id")

        return response_data

    except json.JSONDecodeError as e:
        raise HTTPException(status_code=400, detail=f"无效的JSON数据: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"处理失败: {str(e)}")


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy"}


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)

