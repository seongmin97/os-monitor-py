This project build a real-time server monitor platform with django framework.

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
Server（monitored server）
├── id
├── name          # "linux-server-01"
├── api_key       # Agent 认证用
└── created_at

MetricSnapshot
├── id
├── server (FK)
├── cpu_percent
├── memory_percent
├── memory_used_mb
├── disk_percent
├── net_bytes_sent
├── net_bytes_recv
└── collected_at

Alert (Alert rule)
├── server (FK)
├── metric         # "cpu_percent"
├── threshold      # 90.0
├── is_active
└── created_at
```

API Endpoints
| Path | Method | Auth | Description |
|------|--------|------|-------------|
| /api/auth/register/ | POST | None | Register user, returns JWT |
| /api/auth/token/ | POST | None | Login, obtain JWT |
| /api/auth/token/refresh/ | POST | Refresh token | Refresh access token |
| /api/servers/ | GET/POST | JWT | List / create servers |
| /api/metrics/ | POST | API Key | Agent reports metrics |
| /api/metrics/history/ | GET | JWT | Historical metrics (paginated) |
| /api/metrics/latest/ | GET | JWT | Latest metric entry |
| /api/alerts/rules/ | GET/POST | JWT | Alert rules |
| /api/alerts/events/ | GET | JWT | Alert event records |


## Users
### Superuser
 - username:  admin
 - password:  admin123
### User
 - username:  demouser
 - password:  Demo1234!

## Run
```shell
# first time
docker compose down -v
docker compose up --build

docker compose up
docker ps
docker compose down

# run specific server
docker compose -f 'docker-compose.yml' up -d --build 'postgres'

# check postgre database
docker exec -it handson_python-postgres-1 psql -U sysdash_user -d sysdash

# apply a change 
docker compose build django && docker compose up -d
```

## Test
### test agent
```shell
# prepare env
cd /Users/seongmin/code/other/python/handson_python/agent
pipenv --python 3.11
pipenv install requests psutil
pipenv install pytest --dev
pipenv run which python
pipenv run which pytest

# run test
pipenv run pytest tests.py -v -s
```

