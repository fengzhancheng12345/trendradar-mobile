"""数据服务 - 复用 TrendRadar 的数据源"""
import json
import asyncio
from typing import Dict, List, Optional
from datetime import datetime
import httpx

from app.core.config import settings


class DataService:
    """热点数据服务 - 复用 TrendRadar 数据源"""

    # API 地址 (NewsNow)
    API_URL = "https://newsnow.busiyi.world/api/s"

    # 平台配置
    PLATFORMS = {
        # 免费平台
        "weibo": {"name": "微博", "vip_required": False, "id": "weibo"},
        "baidu": {"name": "百度", "vip_required": False, "id": "baidu"},
        "toutiao": {"name": "今日头条", "vip_required": False, "id": "toutiao"},
        "wangzhoutoupiao": {"name": "网站投票", "vip_required": False, "id": "wangzhoutoupiao"},
        "thepaper": {"name": "澎湃", "vip_required": False, "id": "thepaper"},
        "guanchang": {"name": "观察者", "vip_required": False, "id": "guanchang"},
        "huanqiu": {"name": "环球网", "vip_required": False, "id": "huanqiu"},
        "tencent": {"name": "腾讯", "vip_required": False, "id": "tencent"},
        "people": {"name": "人民网", "vip_required": False, "id": "people"},
        "xinhuanet": {"name": "新华网", "vip_required": False, "id": "xinhuanet"},
        "cctv": {"name": "央视网", "vip_required": False, "id": "cctv"},
        
        # VIP 平台
        "zhihu": {"name": "知乎", "vip_required": True, "id": "zhihu"},
        "bilibili": {"name": "B站", "vip_required": True, "id": "bilibili"},
        "douyin": {"name": "抖音", "vip_required": True, "id": "douyin"},
        "kuaishou": {"name": "快手", "vip_required": True, "id": "kuaishou"},
        "weixin": {"name": "微信", "vip_required": True, "id": "weixin"},
        "toutiao_t": {"name": "头条热榜", "vip_required": True, "id": "toutiao_t"},
        "baidu_t": {"name": "百度热榜", "vip_required": True, "id": "baidu_t"},
        "sina": {"name": "新浪", "vip_required": True, "id": "sina"},
        "ifeng": {"name": "凤凰网", "vip_required": True, "id": "ifeng"},
        "money": {"name": "东方财富", "vip_required": True, "id": "money"},
    }

    def __init__(self):
        self._cache: Dict[str, dict] = {}
        self._cache_time: Dict[str, datetime] = {}
        self._cache_ttl = 300  # 5分钟缓存

    async def fetch_platform_data(self, platform: str, use_cache: bool = True) -> Optional[dict]:
        """获取单个平台数据"""
        # 检查缓存
        if use_cache and platform in self._cache:
            cache_time = self._cache_time.get(platform)
            if cache_time and (datetime.now() - cache_time).seconds < self._cache_ttl:
                return self._cache[platform]

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{self.API_URL}?id={platform}&latest")
                if response.status_code == 200:
                    data = response.json()
                    self._cache[platform] = data
                    self._cache_time[platform] = datetime.now()
                    return data
        except Exception as e:
            print(f"获取 {platform} 数据失败: {e}")
        
        return None

    async def fetch_all_data(
        self, 
        is_vip: bool = False,
        platforms: Optional[List[str]] = None
    ) -> Dict[str, List[dict]]:
        """获取所有平台数据"""
        results = {}
        
        # 确定要获取的平台
        if platforms:
            platform_list = [
                (p, self.PLATFORMS.get(p, {})) 
                for p in platforms
            ]
        else:
            platform_list = [
                (pid, info) 
                for pid, info in self.PLATFORMS.items()
                if not info.get("vip_required", False) or is_vip
            ]

        # 并发获取
        tasks = [
            self._fetch_single_platform(pid, info)
            for pid, info in platform_list
        ]
        
        platform_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for result in platform_results:
            if isinstance(result, dict):
                results.update(result)

        return results

    async def _fetch_single_platform(self, platform_id: str, info: dict) -> dict:
        """获取单个平台数据 (内部方法)"""
        data = await self.fetch_platform_data(platform_id)
        
        if not data:
            return {}
        
        items = []
        for idx, item in enumerate(data.get("items", []), 1):
            items.append({
                "rank": idx,
                "title": item.get("title", ""),
                "url": item.get("url", ""),
                "hot_value": item.get("hot", ""),
                "platform": info.get("name", platform_id),
                "time": item.get("time", ""),
            })
        
        return {platform_id: {
            "name": info.get("name", platform_id),
            "vip_required": info.get("vip_required", False),
            "items": items,
            "updated_at": datetime.now().isoformat(),
        }}

    async def get_trending_data(
        self,
        platform: Optional[str] = None,
        is_vip: bool = False,
        keywords: Optional[List[str]] = None
    ) -> dict:
        """获取热点数据 (主方法)"""
        if platform:
            # 单个平台
            if platform in self.PLATFORMS:
                info = self.PLATFORMS[platform]
                if info.get("vip_required", False) and not is_vip:
                    return {
                        "error": "VIP专享",
                        "message": f"{info['name']} 需要VIP会员权限"
                    }
                
                data = await self._fetch_single_platform(platform, info)
                return data.get(platform, {})
            else:
                return {"error": "平台不存在"}
        
        # 所有平台
        all_data = await self.fetch_all_data(is_vip=is_vip)
        
        # 关键词过滤
        if keywords:
            for platform_id, platform_data in all_data.items():
                items = platform_data.get("items", [])
                filtered_items = [
                    item for item in items
                    if any(kw.lower() in item.get("title", "").lower() for kw in keywords)
                ]
                platform_data["items"] = filtered_items
        
        return all_data

    def get_platform_list(self, is_vip: bool = False) -> List[dict]:
        """获取平台列表"""
        return [
            {
                "id": pid,
                "name": info.get("name", pid),
                "vip_required": info.get("vip_required", False),
            }
            for pid, info in self.PLATFORMS.items()
            if not info.get("vip_required", False) or is_vip
        ]


# 全局实例
data_service = DataService()
