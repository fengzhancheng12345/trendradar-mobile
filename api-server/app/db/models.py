"""数据库模型"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class User(Base):
    """用户表"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True)
    phone = Column(String(20), unique=True, index=True)
    hashed_password = Column(String(255), nullable=False)
    
    # VIP 状态
    is_vip = Column(Boolean, default=False)
    vip_expire_date = Column(DateTime, nullable=True)
    
    # 权限
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    
    # 配额
    keywords_count = Column(Integer, default=1)  # 免费1个，VIP 10个
    
    # 时间
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系
    keywords = relationship("Keyword", back_populates="user", cascade="all, delete-orphan")
    vip_orders = relationship("VIPOrder", back_populates="user")


class Keyword(Base):
    """关键词表"""
    __tablename__ = "keywords"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    word = Column(String(100), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # 关系
    user = relationship("User", back_populates="keywords")


class VIPOrder(Base):
    """VIP 订单表"""
    __tablename__ = "vip_orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    order_no = Column(String(64), unique=True, index=True)  # 订单号
    pay_type = Column(String(20))  # wechat/alipay
    amount = Column(Float, default=0)
    
    status = Column(String(20), default="pending")  # pending/paid/cancelled
    paid_at = Column(DateTime, nullable=True)
    
    # 订阅时长 (天)
    duration_days = Column(Integer, default=30)
    
    created_at = Column(DateTime, default=datetime.utcnow)

    # 关系
    user = relationship("User", back_populates="vip_orders")


class TrendingCache(Base):
    """热点缓存表"""
    __tablename__ = "trending_cache"

    id = Column(Integer, primary_key=True, index=True)
    platform = Column(String(50), index=True)
    data = Column(Text)  # JSON 格式存储
    fetched_at = Column(DateTime, default=datetime.utcnow)
    
    # TTL (秒)
    ttl = Column(Integer, default=1800)  # 默认30分钟
