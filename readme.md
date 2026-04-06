This project build a backend OS monitor with django framework.

## Framework
Overall:
```
├── django        — 主服务器（API + WebSocket）
├── postgres      — 数据库
├── redis         — 消息队列 + Channel Layer
├── celery        — 异步任务工作者
└── linux-server  — 被监控的 Ubuntu 容器（模拟真实服务器）
```

Database:
```
Server（被监控的服务器）
├── id
├── name          # "linux-server-01"
├── api_key       # Agent 认证用
└── created_at

MetricSnapshot（每次采集的快照）
├── id
├── server (FK)
├── cpu_percent
├── memory_percent
├── memory_used_mb
├── disk_percent
├── net_bytes_sent
├── net_bytes_recv
└── collected_at

Alert（告警规则）
├── server (FK)
├── metric         # "cpu_percent"
├── threshold      # 90.0
├── is_active
└── created_at
```

API Endpoints
```
POST /api/auth/token/          # 用户登录，返回 JWT
POST /api/servers/             # 注册新服务器
GET  /api/servers/             # 查看所有服务器

POST /api/metrics/             # Agent 上报指标（用 api_key 认证）
GET  /api/metrics/?server=1&hours=24  # 查询历史指标

POST /api/alerts/              # 创建告警规则
GET  /api/alerts/              # 查看告警规则
```


## Superuser
 - admin:     admin
 - password:  admin123

## Run
```shell
# first time
docker compose down -v
docker compose up --build

docker compose up
docker ps
docker compose down

# check postgre database
docker exec -it handson_python-postgres-1 psql -U sysdash_user -d sysdash
```

## Test
### test agent
```
cd /Users/seongmin/code/other/python/handson_python/agent

pipenv --python 3.11

pipenv install requests psutil

pipenv install pytest --dev

pipenv run which python
pipenv run which pytest

pipenv run pytest tests.py -v -s
```

