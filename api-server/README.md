# TrendRadar Mobile API Server

基于 TrendRadar 开源项目的移动端 API 服务

## 快速开始

```bash
# 1. 克隆项目
git clone https://github.com/yourname/TrendRadar-Mobile-API.git
cd TrendRadar-Mobile-API

# 2. 配置环境
cp config.example.yaml config.yaml
# 编辑 config.yaml 设置 API 密钥

# 3. 启动服务
docker-compose up -d
```

## API 文档

启动服务后访问: `http://localhost:8000/docs`

## 环境变量

| 变量 | 说明 | 默认值 |
|------|------|--------|
| SECRET_KEY | JWT密钥 | random |
| DATABASE_URL | 数据库连接 | sqlite:///./trendradar.db |
| REDIS_URL | Redis连接 | redis://localhost:6379 |

## 许可证

GPL-3.0
