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

    # 处理报价单数据
    start_row = 13
    result_items = json_data.get('array', [])
    current_row = start_row
    total_amount = 0

    for item in result_items:
        each_obj = item.get('each_obj', {})
        item_id = each_obj.get('id', '')
        price_cny = each_obj.get('price_cny', 0)
        quantity = each_obj.get('quantity', 1)
        total_amount_cny = each_obj.get('total_amount_cny', 0)

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

        # 检查是否有details数组
        if 'details' in each_obj and each_obj['details']:
            for detail in each_obj['details']:
                # 处理无序列表格式
                original_lines = detail.get('original', '').split('<br>')
                original_text = '• ' + '\n• '.join(line.strip() for line in original_lines if line.strip())

                reason_lines = detail.get('reason', '').split('<br>')
                reason_text = '• ' + '\n• '.join(line.strip() for line in reason_lines if line.strip())

                # 设置单元格值并启用自动换行
                cell_item_id = ws1.cell(row=current_row, column=2, value=item_id)
                cell_original = ws1.cell(row=current_row, column=3, value=original_text)
                cell_score = ws1.cell(row=current_row, column=4, value=each_obj.get('score', ''))
                cell_reason = ws1.cell(row=current_row, column=5, value=reason_text)
                cell_type = ws1.cell(row=current_row, column=6, value=each_obj.get('type', ''))
                cell_model = ws1.cell(row=current_row, column=7, value=each_obj.get('model', ''))
                cell_brief = ws1.cell(row=current_row, column=8, value=each_obj.get('brief_description', ''))
                cell_manufacturer = ws1.cell(row=current_row, column=9, value=each_obj.get('manufacturer', ''))
                cell_price = ws1.cell(row=current_row, column=10, value=price_cny)
                cell_quantity = ws1.cell(row=current_row, column=11, value=quantity)
                cell_total = ws1.cell(row=current_row, column=12, value=total_amount_cny)

                # 为包含多行文本的单元格设置自动换行
                if original_text:
                    cell_original.alignment = Alignment(wrap_text=True, vertical='top')
                if reason_text:
                    cell_reason.alignment = Alignment(wrap_text=True, vertical='top')
                if each_obj.get('brief_description', ''):
                    cell_brief.alignment = Alignment(wrap_text=True, vertical='top')

                # 设置行高为自动
                ws1.row_dimensions[current_row].height = None  # 自动行高

                current_row += 1
        else:
            # 处理无序列表格式
            original_lines = each_obj.get('original', '').split('<br>')
            original_text = '• ' + '\n• '.join(line.strip() for line in original_lines if line.strip())

            reason_lines = each_obj.get('reason', '').split('<br>')
            reason_text = '• ' + '\n• '.join(line.strip() for line in reason_lines if line.strip())

            # 设置单元格值并启用自动换行
            cell_item_id = ws1.cell(row=current_row, column=2, value=item_id)
            cell_original = ws1.cell(row=current_row, column=3, value=original_text)
            cell_score = ws1.cell(row=current_row, column=4, value=each_obj.get('score', ''))
            cell_reason = ws1.cell(row=current_row, column=5, value=reason_text)
            cell_type = ws1.cell(row=current_row, column=6, value=each_obj.get('type', ''))
            cell_model = ws1.cell(row=current_row, column=7, value=each_obj.get('model', ''))
            cell_brief = ws1.cell(row=current_row, column=8, value=each_obj.get('brief_description', ''))
            cell_manufacturer = ws1.cell(row=current_row, column=9, value=each_obj.get('manufacturer', ''))
            cell_price = ws1.cell(row=current_row, column=10, value=price_cny)
            cell_quantity = ws1.cell(row=current_row, column=11, value=quantity)
            cell_total = ws1.cell(row=current_row, column=12, value=total_amount_cny)

            # 为包含多行文本的单元格设置自动换行
            if original_text:
                cell_original.alignment = Alignment(wrap_text=True, vertical='top')
            if reason_text:
                cell_reason.alignment = Alignment(wrap_text=True, vertical='top')
            if each_obj.get('brief_description', ''):
                cell_brief.alignment = Alignment(wrap_text=True, vertical='top')

            # 设置行高为自动
            ws1.row_dimensions[current_row].height = None  # 自动行高

            current_row += 1

    # 找到F列值为"小计"和"总计"的行，并填入总金额到L列
    subtotal_row = None
    total_row = None

    # 遍历所有行，寻找"小计"和"总计"
    for row in range(1, ws1.max_row + 1):
        cell_f = ws1.cell(row=row, column=6)  # F列
        if cell_f.value == "小计":
            subtotal_row = row
            ws1.cell(row=row, column=12, value=total_amount)  # L列写入总金额
            # 设置行高为自动
            ws1.row_dimensions[row].height = None
        elif cell_f.value == "总计":
            total_row = row
            ws1.cell(row=row, column=12, value=total_amount)  # L列写入总金额
            # 设置行高为自动
            ws1.row_dimensions[row].height = None

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

    # 建立需求点与设备的映射关系
    demand_device_mapping = []

    for item in result_items:
        each_obj = item.get('each_obj', {})

        # 处理original，将每个需求点与设备建立映射
        original_text = each_obj.get('original', '')
        if original_text:
            # 按换行符和<br>拆分需求点
            demand_lines = []
            for line in original_text.split('\n'):
                line = line.strip()
                if line:
                    # 进一步按<br>拆分
                    sub_lines = [sub_line.strip() for sub_line in line.split('<br>') if sub_line.strip()]
                    demand_lines.extend(sub_lines)

            # 为每个需求点建立映射（这里简单地将需求点与当前设备关联）
            # 实际应用中可能需要更复杂的匹配逻辑
            for demand in demand_lines:
                demand_device_mapping.append({
                    'demand': demand,
                    'reason': each_obj.get('reason', ''),
                    'device': each_obj
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
        ws2.cell(row=current_row, column=7, value=device.get('brief_description', ''))
        ws2.cell(row=current_row, column=8, value=device.get('manufacturer', ''))
        ws2.cell(row=current_row, column=9, value=device.get('quantity', 1))

        # 计算单价
        price_cny = device.get('price_cny', 0)
        if isinstance(price_cny, str):
            price_cny = float(price_cny.replace('￥', '').replace(',', ''))
        ws2.cell(row=current_row, column=10, value=price_cny)

        # 小计
        total_amount_cny = device.get('total_amount_cny', 0)
        if isinstance(total_amount_cny, str):
            total_amount_cny = float(total_amount_cny.replace('￥', '').replace(',', ''))
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

            # 设置对齐方式
            if col in [1, 8, 9, 10, 11]:  # 数字列
                cell.alignment = Alignment(horizontal="center", vertical="center")
            elif col in [2, 3, 5, 6, 7]:  # 文本列
                cell.alignment = Alignment(horizontal="left", vertical="center", wrap_text=True)
            else:  # 其他列
                cell.alignment = Alignment(horizontal="left", vertical="center")

        # 为包含多行文本的单元格设置自动换行
        cell_demand = ws2.cell(row=current_row, column=2)
        cell_reason = ws2.cell(row=current_row, column=3)
        cell_brief = ws2.cell(row=current_row, column=7)

        if '\n' in demand:
            cell_demand.alignment = Alignment(wrap_text=True, vertical='top')

        if reason and '\n' in reason:
            cell_reason.alignment = Alignment(wrap_text=True, vertical='top')

        if device.get('brief_description', ''):
            cell_brief.alignment = Alignment(wrap_text=True, vertical='top')

        # 设置行高为自动
        ws2.row_dimensions[current_row].height = None
        current_row += 1

    # 优化列宽
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
                'http://demo.langcore.cn/api/file',
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
                        full_url = f"https://demo.langcore.cn/api/file/{file_id}"
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
async def generate_excel(json_data: Dict[str, Any], token: str = "sk-zzvwbcaxoss3"):
    """
    生成Excel文件并自动上传

    - **json_data**: 包含配置数据的JSON对象
    - **token**: 认证token（默认为"sk-zzvwbcaxoss3"）
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
    uvicorn.run(app, host="127.0.0.1", port=8483)

