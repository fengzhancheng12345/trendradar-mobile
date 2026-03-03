"""热点数据路由 - 使用真实数据源"""
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.db.database import get_db
from app.db.models import User
from app.api.v1.auth import get_current_user
from app.services.data_service import data_service

router = APIRouter()


# Pydantic 模型
class TrendingItem(BaseModel):
    """热点条目"""
    rank: int
    title: str
    url: Optional[str] = None
    hot_value: Optional[str] = None
    platform: str
    time: Optional[str] = None


class PlatformData(BaseModel):
    """平台数据"""
    name: str
    vip_required: bool
    items: List[TrendingItem]
    updated_at: str


class TrendingResponse(BaseModel):
    """热点响应"""
    platform: str
    data: List[TrendingItem]
    updated_at: str


@router.get("")
async def get_trending(
    platform: Optional[str] = Query(None, description="平台ID"),
    keywords: Optional[str] = Query(None, description="关键词过滤,逗号分隔"),
    current_user: User = Depends(get_current_user),
):
    """获取热点列表"""
    is_vip = current_user.is_vip
    
    # 获取用户关键词
    user_keywords = [kw.word for kw in current_user.keywords if kw.is_active]
    if keywords:
        user_keywords.extend([k.strip() for k in keywords.split(",")])
    
    # 获取数据
    if platform:
        # 单个平台
        result = await data_service.get_trending_data(
            platform=platform,
            is_vip=is_vip,
            keywords=user_keywords if user_keywords else None
        )
        
        if "error" in result:
            raise HTTPException(status_code=403, detail=result.get("message"))
        
        items = result.get("items", [])
        return [TrendingResponse(
            platform=platform,
            data=[TrendingItem(**item) for item in items],
            updated_at=result.get("updated_at", datetime.utcnow().isoformat())
        )]
    else:
        # 所有平台
        result = await data_service.get_trending_data(
            is_vip=is_vip,
            keywords=user_keywords if user_keywords else None
        )
        
        responses = []
        for plat_id, plat_data in result.items():
            items = plat_data.get("items", [])
            if items:
                responses.append(TrendingResponse(
                    platform=plat_id,
                    data=[TrendingItem(**item) for item in items],
                    updated_at=plat_data.get("updated_at", datetime.utcnow().isoformat())
                ))
        
        return responses


@router.get("/platforms")
async def get_platforms(
    current_user: User = Depends(get_current_user)
):
    """获取支持的平台列表"""
    is_vip = current_user.is_vip
    platforms = data_service.get_platform_list(is_vip=is_vip)
    
    return {"platforms": platforms}


@router.get("/history")
async def get_history(
    platform: Optional[str] = Query(None),
    days: int = Query(7, ge=1, le=30),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取历史热点数据"""
    # 免费用户只能看7天，VIP 可以看30天
    if days > 7 and not current_user.is_vip:
        raise HTTPException(
            status_code=403,
            detail="历史数据超过7天需要VIP会员权限"
        )
    
    # 实际项目中从数据库查询历史数据
    return {
        "platform": platform or "all",
        "days": days,
        "data": [],
        "message": "历史数据功能开发中"
    }


@router.get("/refresh")
async def refresh_data(
    platform: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
):
    """强制刷新数据"""
    is_vip = current_user.is_vip
    
    if platform:
        result = await data_service.get_trending_data(
            platform=platform,
            is_vip=is_vip
        )
    else:
        result = await data_service.get_trending_data(is_vip=is_vip)
    
    return {
        "status": "success",
        "platform": platform or "all",
        "updated_at": datetime.utcnow().isoformat()
    }
