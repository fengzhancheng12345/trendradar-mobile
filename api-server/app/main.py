"""
TrendRadar Mobile API Server
基于 TrendRadar 的移动端 API 服务
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.v1 import auth, trending, vip, ai
from app.db.database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时
    await init_db()
    yield
    # 关闭时


app = FastAPI(
    title="TrendRadar Mobile API",
    description="热点舆情监控移动端 API 服务",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应限制域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(auth.router, prefix="/api/v1/auth", tags=["认证"])
app.include_router(trending.router, prefix="/api/v1/trending", tags=["热点数据"])
app.include_router(vip.router, prefix="/api/v1/vip", tags=["VIP会员"])
app.include_router(ai.router, prefix="/api/v1/ai", tags=["AI功能"])


@app.get("/")
async def root():
    """健康检查"""
    return {
        "name": "TrendRadar Mobile API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy"}
