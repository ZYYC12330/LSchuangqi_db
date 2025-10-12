from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional
import numpy as np
from scipy.optimize import linprog
import uvicorn

app = FastAPI(
    title="板卡选型优化 API",
    description="基于线性规划的板卡最优采购方案计算",
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
    "sharedMemoryChannels"
]

# 请求模型
class CardInfo(BaseModel):
    matrix: List[int] = Field(..., description="22个元素的数组，表示各通道类型的数量")
    model: str = Field(..., description="板卡型号")
    price_cny: int = Field(..., description="板卡价格（人民币）")
    id: str = Field(..., description="板卡唯一标识ID")

class OptimizationRequest(BaseModel):
    input_data: List[CardInfo] = Field(..., description="板卡库存数据，直接是板卡数组")
    requirements_input: List[int] = Field(..., description="22个元素的需求数组")

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
    
    - **input_data**: 板卡数组，每个板卡包含 matrix（22元素数组）、model（型号）、price_cny（价格）、id（唯一标识）
    - **requirements_input**: 需求向量，22个元素对应22种通道类型
    
    返回最优采购方案，包括总成本和每种板卡的采购数量
    """
    try:
        # 1. 数据验证
        if len(request.requirements_input) != 22:
            raise HTTPException(
                status_code=400,
                detail=f"requirements_input 必须有 22 个元素，当前有 {len(request.requirements_input)} 个"
            )
        
        # 2. 提取所有板卡数据
        # input_data 现在直接是板卡数组，不再需要 each_card 这一层
        all_cards = request.input_data
        
        if len(all_cards) == 0:
            raise HTTPException(status_code=400, detail="input_data 中没有板卡数据")
        
        n_cards = len(all_cards)
        
        # 3. 验证每个板卡的 matrix 长度
        for idx, card in enumerate(all_cards):
            if len(card.matrix) != 22:
                raise HTTPException(
                    status_code=400,
                    detail=f"板卡 [{idx}] {card.model} 的 matrix 必须有 22 个元素，当前有 {len(card.matrix)} 个"
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
        
        A = np.array(resource_matrix)  # shape: (n_cards, 22)
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


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)

