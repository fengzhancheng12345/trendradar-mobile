"""VIP 会员路由 - 支付宝当面付"""
from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.db.database import get_db
from app.db.models import User, VIPOrder
from app.api.v1.auth import get_current_user
from app.services.payment_service import payment_service

router = APIRouter()


# Pydantic 模型
class VIPStatusResponse(BaseModel):
    """VIP状态响应"""
    is_vip: bool
    vip_expire_date: Optional[str]
    keywords_count: int
    features: dict


class CreateOrderRequest(BaseModel):
    """创建订单请求"""
    duration_days: int = Query(30, ge=30, le=365)


class CreateOrderResponse(BaseModel):
    """创建订单响应"""
    order_no: str
    amount: float
    pay_type: str
    qr_code: Optional[str] = None
    qr_code_image: Optional[str] = None


class VIPProduct(BaseModel):
    """VIP产品"""
    duration_days: int
    price: float
    description: str


# VIP 产品定价
VIP_PRODUCTS = {
    30: {"price": 9.9, "description": "月度 VIP"},
    90: {"price": 25.0, "description": "季度 VIP"},
    180: {"price": 45.0, "description": "半年 VIP"},
    365: {"price": 59.9, "description": "年度 VIP"},
}


@router.get("/status", response_model=VIPStatusResponse)
async def get_vip_status(
    current_user: User = Depends(get_current_user)
):
    """获取 VIP 状态"""
    # 检查 VIP 是否过期
    if current_user.is_vip and current_user.vip_expire_date:
        if current_user.vip_expire_date < datetime.utcnow():
            current_user.is_vip = False
    
    features = {
        "update_interval": "5分钟" if current_user.is_vip else "30分钟",
        "platforms": "20+" if current_user.is_vip else "11",
        "keywords": f"{current_user.keywords_count}个",
        "history_days": 30 if current_user.is_vip else 7,
        "ai_analysis": current_user.is_vip,
    }
    
    return VIPStatusResponse(
        is_vip=current_user.is_vip,
        vip_expire_date=current_user.vip_expire_date.isoformat() if current_user.vip_expire_date else None,
        keywords_count=current_user.keywords_count,
        features=features
    )


@router.get("/products")
async def get_vip_products():
    """获取 VIP 产品列表"""
    products = []
    for days, info in VIP_PRODUCTS.items():
        products.append(VIPProduct(
            duration_days=days,
            price=info["price"],
            description=info["description"]
        ))
    return {"products": products}


@router.post("/pay", response_model=CreateOrderResponse)
async def create_pay_order(
    order_data: CreateOrderRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """创建支付宝当面付订单"""
    if order_data.duration_days not in VIP_PRODUCTS:
        raise HTTPException(status_code=400, detail="无效的订阅时长")
    
    product = VIP_PRODUCTS[order_data.duration_days]
    
    # 生成订单号
    order_no = f"VIP{datetime.utcnow().strftime('%Y%m%d%H%M%S')}{current_user.id}"
    
    # 创建订单
    order = VIPOrder(
        user_id=current_user.id,
        order_no=order_no,
        pay_type="alipay",
        amount=product["price"],
        duration_days=order_data.duration_days,
        status="pending"
    )
    db.add(order)
    db.commit()
    
    # 创建支付宝当面付订单 (生成收款码)
    pay_result = await payment_service.create_alipay_order(
        order_no=order_no,
        amount=product["price"],
        description=product["description"],
        user_id=current_user.id
    )
    
    if "error" in pay_result:
        raise HTTPException(status_code=500, detail=pay_result["error"])
    
    return CreateOrderResponse(
        order_no=order_no,
        amount=product["price"],
        pay_type="alipay",
        qr_code=pay_result.get("qr_code"),
        qr_code_image=pay_result.get("qr_code_image")
    )


@router.post("/webhook/alipay")
async def alipay_payment_webhook(
    out_trade_no: str = Query(..., description="订单号"),
    trade_status: str = Query(..., description="交易状态"),
    db: Session = Depends(get_db)
):
    """支付宝异步通知回调"""
    
    # 查询订单
    order = db.query(VIPOrder).filter(VIPOrder.order_no == out_trade_no).first()
    
    if not order:
        return {"code": "40004", "msg": "订单不存在"}
    
    # 检查交易状态
    if trade_status in ["TRADE_SUCCESS", "TRADE_FINISHED"]:
        if order.status == "pending":
            # 更新订单状态
            order.status = "paid"
            order.paid_at = datetime.utcnow()
            
            # 激活 VIP
            user = db.query(User).filter(User.id == order.user_id).first()
            if user:
                # 延长 VIP 时间
                if user.vip_expire_date and user.vip_expire_date > datetime.utcnow():
                    user.vip_expire_date = user.vip_expire_date + timedelta(days=order.duration_days)
                else:
                    user.vip_expire_date = datetime.utcnow() + timedelta(days=order.duration_days)
                
                user.is_vip = True
                user.keywords_count = 10  # VIP 10个关键词
            
            db.commit()
    
    return {"code": "10000", "msg": "success"}


@router.post("/check")
async def check_payment(
    order_no: str,
    db: Session = Depends(get_db)
):
    """检查订单支付状态 (轮询查询)"""
    order = db.query(VIPOrder).filter(VIPOrder.order_no == order_no).first()
    
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    
    # 如果订单已支付，直接返回
    if order.status == "paid":
        return {
            "order_no": order.order_no,
            "status": "paid",
            "paid_at": order.paid_at.isoformat() if order.paid_at else None
        }
    
    # 查询支付宝订单状态
    result = await payment_service.query_alipay_order(order_no)
    
    if "error" not in result:
        trade_status = result.get("trade_status")
        
        # 检查支付成功
        if trade_status in ["TRADE_SUCCESS", "TRADE_FINISHED"]:
            order.status = "paid"
            order.paid_at = datetime.utcnow()
            
            # 激活 VIP
            user = db.query(User).filter(User.id == order.user_id).first()
            if user:
                if user.vip_expire_date and user.vip_expire_date > datetime.utcnow():
                    user.vip_expire_date = user.vip_expire_date + timedelta(days=order.duration_days)
                else:
                    user.vip_expire_date = datetime.utcnow() + timedelta(days=order.duration_days)
                
                user.is_vip = True
                user.keywords_count = 10
            
            db.commit()
    
    return {
        "order_no": order.order_no,
        "status": order.status,
        "trade_status": result.get("trade_status", "UNKNOWN"),
        "paid_at": order.paid_at.isoformat() if order.paid_at else None
    }


@router.post("/cancel")
async def cancel_order(
    order_no: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """取消订单"""
    order = db.query(VIPOrder).filter(
        VIPOrder.order_no == order_no,
        VIPOrder.user_id == current_user.id
    ).first()
    
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    
    if order.status != "pending":
        raise HTTPException(status_code=400, detail="只能取消待支付的订单")
    
    # 尝试关闭支付宝订单
    await payment_service.close_alipay_order(order_no)
    
    order.status = "cancelled"
    db.commit()
    
    return {"status": "cancelled", "order_no": order_no}
