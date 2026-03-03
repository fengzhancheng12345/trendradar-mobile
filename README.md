# TrendRadar Mobile 项目

## 项目概述

基于 GPL-3.0 开源项目 TrendRadar 的移动端应用，提供热点监控服务。

## 产品定位

- **免费用户**: 30分钟更新 / 11平台 / 基础功能
- **VIP用户**: 5分钟更新 / 20+平台 / AI分析 / 10+关键词 / 30天历史数据

## 项目架构

```
┌─────────────────────────────────────────────────────────────┐
│                    TrendRadar Mobile App                    │
│                    (Flutter 前端)                           │
│  - 热点监控界面                                             │
│  - VIP 会员管理 (支付宝当面付)                              │
│  - 用户中心                                                 │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼ HTTP/REST
┌─────────────────────────────────────────────────────────────┐
│                 TrendRadar API Server (Python)               │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐    │
│  │  Auth API   │  │  Data API   │  │ Payment (当面付)│    │
│  └─────────────┘  └─────────────┘  └─────────────────┘    │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              TrendRadar Data (NewsNow API)                  │
└─────────────────────────────────────────────────────────────┘
```

## 开发进度

### Phase 1: API Server 基础 ✅

- [x] 项目初始化 (FastAPI)
- [x] 用户认证系统 (JWT)
- [x] VIP权限控制
- [x] 基础数据接口

### Phase 2: 数据源接入 ✅

- [x] 集成 TrendRadar 数据爬虫
- [x] 35+ 平台数据支持
- [x] VIP/免费平台区分

### Phase 3: 支付集成 ✅

- [x] 支付宝当面付 (预下单 + 收款码)
- [x] 订单查询与轮询
- [x] 异步通知回调
- [x] 沙箱/正式环境支持
- [x] 环境变量配置
- [x] 支付配置指南

### Phase 4: 移动端 ✅

- [x] Flutter 项目初始化
- [x] 状态管理 (Provider)
- [x] 登录/注册界面
- [x] 热点监控界面
- [x] VIP 会员界面 (当面付收款码)
- [x] 用户中心界面

## 技术栈

### 后端
- Python 3.11+
- FastAPI
- SQLAlchemy
- JWT 认证
- 支付宝当面付

### 前端
- Flutter 3.0+
- Provider 状态管理
- Dio 网络请求

## 支付方式

**支付宝当面付** - 扫码支付，快速开通VIP

### 支付流程
1. 用户选择套餐，点击购买
2. 服务端生成收款二维码
3. 用户使用支付宝扫码支付
4. 支付成功后自动开通VIP

## 项目结构

```
trendradar-mobile/
├── api-server/              # API 服务端
│   ├── app/
│   │   ├── api/v1/         # API 路由
│   │   ├── core/          # 核心配置
│   │   ├── db/            # 数据库
│   │   └── services/      # 业务服务
│   ├── requirements.txt
│   └── docker-compose.yml
│
├── flutter_app/             # 移动端 App
│   ├── lib/
│   │   ├── config/        # 配置
│   │   ├── providers/    # 状态管理
│   │   ├── screens/      # 界面
│   │   ├── services/    # API 服务
│   │   └── main.dart
│   └── pubspec.yaml
│
└── docs/                   # 文档
    ├── 技术方案.md
    └── 支付配置指南.md
```

## 快速开始

### 后端服务

```bash
cd api-server
pip install -r requirements.txt
cp .env.example .env
# 编辑 .env 填写支付宝配置
uvicorn app.main:app --reload
```

### Flutter App

```bash
cd flutter_app
flutter pub get
flutter run
```

## 相关资源

- 原始开源项目: https://github.com/sansan0/TrendRadar
- 官方网站: https://sansan0.github.io/TrendRadar/

## 许可证

GPL-3.0
