"""支付服务 - 支付宝当面付"""
import json
import time
import uuid
import base64
from typing import Optional
from datetime import datetime, timedelta
from decimal import Decimal
import httpx
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA256
import urllib.parse

from app.core.config import settings


class PaymentService:
    """支付服务 - 支付宝当面付 (Barcode Pay)"""

    # 支付宝当面付配置
    ALIPAY_CONFIG = {
        "appid": settings.ALIPAY_APPID,               # 应用ID
        "private_key": settings.ALIPAY_PRIVATE_KEY,    # 应用私钥
        "alipay_public_key": settings.ALIPAY_PUBLIC_KEY,  # 支付宝公钥
        "notify_url": settings.ALIPAY_NOTIFY_URL,      # 异步通知
        "store_id": settings.ALIPAY_STORE_ID,          # 商户门店编号
    }

    # API 地址
    # 正式环境: https://openapi.alipay.com/gateway.do
    # 沙箱环境: https://openapi-sandbox.alipay.com/gateway.do
    ALIPAY_API_URL = "https://openapi.alipay.com/gateway.do"
    ALIPAY_SANDBOX_URL = "https://openapi-sandbox.alipay.com/gateway.do"

    def __init__(self):
        self._is_production = settings.PAYMENT_MODE == "production"
        self._api_url = self.ALIPAY_API_URL if self._is_production else self.ALIPAY_SANDBOX_URL

    # ==================== 支付宝当面付 ====================

    async def create_alipay_order(
        self,
        order_no: str,
        amount: float,
        description: str,
        user_id: int
    ) -> dict:
        """创建支付宝当面付订单 (生成收款码)"""
        
        if not self._is_production:
            return await self._create_sandbox_order(order_no, amount, description)
        
        try:
            # 构造请求参数
            biz_content = {
                "out_trade_no": order_no,
                "total_amount": f"{amount:.2f}",
                "subject": description,
                "body": description,
                "timeout_express": "5m",           # 5分钟超时
                "store_id": self.ALIPAY_CONFIG["store_id"],  # 门店编号
                "qr_code_timeout_express": "5m",   # 二维码超时
            }
            
            # 调用接口
            response = await self._alipay_request(
                "alipay.trade.precreate",  # 预下单 (生成二维码)
                biz_content
            )
            
            if response.get("code") == "10000":  # 成功
                qr_code = response.get("data", {}).get("qr_code")
                return {
                    "order_no": order_no,
                    "amount": amount,
                    "pay_type": "alipay",
                    "qr_code": qr_code,  # 商户可以自己生成二维码
                    "qr_code_image": f"https://api.qrserver.com/v1/create-qr-code/?size=200x200&data={urllib.parse.quote(qr_code or '')}",
                }
            else:
                return {"error": f"创建订单失败: {response.get('msg')}"}
                
        except Exception as e:
            return {"error": f"支付宝当面付异常: {str(e)}"}

    async def query_alipay_order(self, order_no: str) -> dict:
        """查询支付宝订单状态"""
        
        if not self._is_production:
            return {"trade_status": "TRADE_SUCCESS", "sandbox": True}
        
        try:
            biz_content = {
                "out_trade_no": order_no,
            }
            
            response = await self._alipay_request(
                "alipay.trade.query",
                biz_content
            )
            
            if response.get("code") == "10000":
                data = response.get("data", {})
                return {
                    "trade_status": data.get("trade_status"),
                    "total_amount": data.get("total_amount"),
                    "buyer_pay_amount": data.get("buyer_pay_amount"),
                }
            else:
                return {"error": response.get("msg")}
                
        except Exception as e:
            return {"error": str(e)}

    async def close_alipay_order(self, order_no: str) -> dict:
        """关闭未支付的订单"""
        
        if not self._is_production:
            return {"success": True, "sandbox": True}
        
        try:
            biz_content = {
                "out_trade_no": order_no,
            }
            
            response = await self._alipay_request(
                "alipay.trade.close",
                biz_content
            )
            
            return response.get("code") == "10000"
            
        except Exception as e:
            return {"error": str(e)}

    async def verify_alipay_callback(self, params: dict) -> bool:
        """验证支付宝回调签名"""
        try:
            sign = params.get("sign")
            sign_type = params.get("sign_type", "RSA2")
            
            # 移除 sign 和 sign_type
            params_copy = {k: v for k, v in params.items() if k not in ["sign", "sign_type"]}
            
            # 按 key 排序并拼接
            sorted_params = sorted(params_copy.items())
            verify_string = "&".join([f"{k}={v}" for k, v in sorted_params])
            
            # RSA2 验签
            key = RSA.import_key(self.ALIPAY_CONFIG["alipay_public_key"])
            verifier = PKCS1_v1_5.new(key)
            hash_obj = SHA256.new(verify_string.encode('utf-8'))
            
            try:
                verifier.verify(hash_obj, base64.b64decode(sign))
                return True
            except:
                return False
            
        except Exception as e:
            print(f"支付宝验签失败: {e}")
            return False

    # ==================== 当面付扫码支付 ====================

    async def barcode_pay(
        self,
        order_no: str,
        auth_code: str,      # 用户支付宝付款码
        amount: float,
        description: str
    ) -> dict:
        """当面对准用户付款码扣款 (barcode支付)"""
        
        if not self._is_production:
            return {
                "order_no": order_no,
                "trade_no": f"sandbox_{order_no}",
                "trade_status": "TRADE_SUCCESS",
                "buyer_logon_id": "****@sandbox.com",
                "sandbox": True
            }
        
        try:
            biz_content = {
                "out_trade_no": order_no,
                "total_amount": f"{amount:.2f}",
                "subject": description,
                "body": description,
                "auth_code": auth_code,     # 用户付款码
                "timeout_express": "5m",
                "store_id": self.ALIPAY_CONFIG["store_id"],
            }
            
            response = await self._alipay_request(
                "alipay.trade.pay",
                biz_content
            )
            
            if response.get("code") == "10000":
                data = response.get("data", {})
                return {
                    "order_no": order_no,
                    "trade_no": data.get("trade_no"),
                    "trade_status": data.get("trade_status"),
                    "buyer_logon_id": data.get("buyer_logon_id"),
                }
            elif response.get("code") == "10003":  # 用户输入密码中
                return {"status": "processing", "message": "等待用户确认"}
            elif response.get("code") == "10004":  # 支付成功但结果未知
                return {"status": "unknown", "need_query": True}
            else:
                return {"error": response.get("msg"), "sub_code": response.get("sub_code")}
                
        except Exception as e:
            return {"error": str(e)}

    # ==================== 沙箱模拟 ====================

    async def _create_sandbox_order(
        self,
        order_no: str,
        amount: float,
        description: str
    ) -> dict:
        """沙箱环境 - 创建模拟订单"""
        
        # 生成模拟二维码 (沙箱环境专用)
        sandbox_qr = f"https://qr.alipay.com/barlist/{order_no}"
        
        return {
            "order_no": order_no,
            "amount": amount,
            "pay_type": "alipay",
            "qr_code": sandbox_qr,
            "qr_code_image": f"https://api.qrserver.com/v1/create-qr-code/?size=200x200&data={urllib.parse.quote(sandbox_qr)}",
            "sandbox": True,
            "sandbox_tip": "沙箱环境模拟订单",
            "pay_instructions": "沙箱环境请使用支付宝沙箱应用扫码"
        }

    # ==================== 内部方法 ====================

    async def _alipay_request(self, method: str, biz_content: dict) -> dict:
        """发送支付宝请求"""
        
        # 公共参数
        params = {
            "app_id": self.ALIPAY_CONFIG["appid"],
            "method": method,
            "format": "JSON",
            "charset": "utf-8",
            "sign_type": "RSA2",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "version": "1.0",
            "notify_url": self.ALIPAY_CONFIG["notify_url"],
            "biz_content": json.dumps(biz_content, ensure_ascii=False),
        }
        
        # 生成签名
        sign = self._generate_sign(params)
        params["sign"] = sign
        
        # 发送请求
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                self._api_url,
                data=params,
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            
            # 解析响应
            result = response.text
            # 解析 JSONP 格式: {"method":"xxx","biz_content":"{}","sign":"xxx"}
            # 返回结果在 response[root][method_response] 中
            
            try:
                resp_data = json.loads(result)
                # 提取业务响应
                method_response_key = method.replace(".", "_") + "_response"
                if method_response_key in resp_data:
                    return {
                        "code": resp_data.get("code"),
                        "msg": resp_data.get("msg"),
                        "data": resp_data.get(method_response_key, {}),
                        "sign": resp_data.get("sign")
                    }
                return resp_data
            except:
                return {"error": "解析响应失败", "raw": result}

    def _generate_sign(self, params: dict) -> str:
        """生成 RSA2 签名"""
        
        # 1. 排序参数
        sorted_params = sorted([(k, v) for k, v in params.items() if k != "sign"])
        
        # 2. 拼接字符串
        sign_string = "&".join([f"{k}={v}" for k, v in sorted_params])
        
        # 3. RSA2 签名
        try:
            key = RSA.import_key(self.ALIPAY_CONFIG["private_key"])
            signer = PKCS1_v1_5.new(key)
            hash_obj = SHA256.new(sign_string.encode('utf-8'))
            signature = signer.sign(hash_obj)
            return base64.b64encode(signature).decode('utf-8')
        except Exception as e:
            print(f"签名失败: {e}")
            return ""


# 全局实例
payment_service = PaymentService()
