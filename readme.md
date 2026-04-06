This project build the basic backend system with django framework.

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


# Other topics
## What is Celery?
Celery is a distributed task queue for Python. It lets you run tasks asynchronously in the background, outside of the main web request/response cycle.

### Why you need it:

Without Celery, if a user triggers something slow (e.g., sending emails, generating a report, collecting system metrics), the HTTP request would block and hang until it finishes. With Celery, you instead queue the task and respond to the user immediately — Celery picks it up and runs it separately.

### How it works in your project:

```
Browser → Django (HTTP) → queues task → Redis (message broker)
                                              ↓
                                        Celery Worker
                                        (runs the task)
                                              ↓
                                        PostgreSQL (stores results)
```
 - Redis acts as the broker — it holds the queue of pending tasks
 - Celery worker (celery -A sysdash worker) continuously polls Redis and executes tasks
 - Results/state can be stored back in PostgreSQL or Redis

Celery likely handles things like periodically collecting system metrics from the linux-server agent and saving them to the database.