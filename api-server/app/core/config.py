"""应用配置"""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """应用配置"""

    # 应用基础
    APP_NAME: str = "TrendRadar Mobile API"
    DEBUG: bool = True

    # JWT 配置
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7天
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    # 数据库
    DATABASE_URL: str = "sqlite:///./trendradar.db"

    # Redis
    REDIS_URL: str = "redis://localhost:6379"

    # TrendRadar API
    TRENDRADAR_API_URL: str = "https://api.newsnow.tv"

    # VIP 配置
    VIP_UPDATE_INTERVAL_FREE: int = 30  # 免费用户 30分钟
    VIP_UPDATE_INTERVAL_VIP: int = 5    # VIP 用户 5分钟

    # ==================== 支付配置 (支付宝当面付) ====================
    
    # 支付模式: sandbox | production
    PAYMENT_MODE: str = "sandbox"
    
    # 支付宝当面付配置
    ALIPAY_APPID: str = ""              # 应用ID
    ALIPAY_PRIVATE_KEY: str = ""        # 应用私钥 (RSA2)
    ALIPAY_PUBLIC_KEY: str = ""          # 支付宝公钥
    ALIPAY_NOTIFY_URL: str = ""          # 异步通知地址
    ALIPAY_STORE_ID: str = ""           # 商户门店编号 (当面付必需)

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """获取配置单例"""
    return Settings()


settings = get_settings()
