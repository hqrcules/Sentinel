# Sentinel - DevOps Monitoring Backend

A production-ready FastAPI application for monitoring servers and containers using the Prometheus API.

## Features

- **REST API** for managing servers, alert rules, and viewing metrics
- **WebSocket** for real-time metrics streaming
- **Prometheus Integration** for querying system metrics asynchronously
- **Alert System** with customizable rules and thresholds
- **Telegram Notifications** for alert events
- **JWT Authentication** for secure API access
- **Celery** for background tasks and periodic alert checking
- **Docker Compose** for easy deployment
- **Comprehensive Tests** with pytest

## Tech Stack

- **FastAPI** - Modern async web framework
- **PostgreSQL** - Database with SQLAlchemy ORM
- **Redis** - Celery broker and caching
- **Celery** - Background and periodic tasks
- **Prometheus** - Metrics collection and querying
- **Grafana** - Metrics visualization
- **JWT** - Authentication with python-jose
- **HTTPX** - Async HTTP client for Prometheus queries
- **Docker & Docker Compose** - Containerization

## Project Structure

```
Sentinel/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── v1/
│   │   │       ├── endpoints/
│   │   │       │   ├── auth.py
│   │   │       │   ├── servers.py
│   │   │       │   ├── metrics.py
│   │   │       │   ├── alerts.py
│   │   │       │   └── health.py
│   │   │       └── api.py
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   ├── security.py
│   │   │   └── celery_app.py
│   │   ├── db/
│   │   │   └── session.py
│   │   ├── models/
│   │   │   ├── user.py
│   │   │   ├── server.py
│   │   │   ├── alert_rule.py
│   │   │   └── alert_event.py
│   │   ├── schemas/
│   │   │   ├── user.py
│   │   │   ├── server.py
│   │   │   ├── alert_rule.py
│   │   │   ├── alert_event.py
│   │   │   └── metrics.py
│   │   ├── services/
│   │   │   ├── auth_service.py
│   │   │   ├── prometheus_service.py
│   │   │   ├── telegram_service.py
│   │   │   └── alert_service.py
│   │   ├── tests/
│   │   │   ├── conftest.py
│   │   │   ├── test_auth.py
│   │   │   ├── test_servers.py
│   │   │   ├── test_metrics.py
│   │   │   └── test_alerts.py
│   │   └── main.py
│   └── requirements.txt
├── deploy/
│   ├── docker-compose.yml
│   ├── Dockerfile
│   └── prometheus.yml
├── .env.example
└── README.md
```

## Installation

### Prerequisites

- Docker and Docker Compose
- (Optional) Telegram Bot Token for notifications

### Quick Start

1. **Clone the repository**

```bash
cd Sentinel
```

2. **Copy and configure environment variables**

```bash
cp .env.example .env
```

Edit `.env` and set your configuration:

```env
SECRET_KEY=your-secret-key-here-change-this-in-production
DATABASE_URL=postgresql://vigil:vigil_password@db:5432/vigil
TELEGRAM_BOT_TOKEN=your-telegram-bot-token  # Optional
TELEGRAM_CHAT_ID=your-telegram-chat-id      # Optional
```

3. **Start all services with Docker Compose**

```bash
cd deploy
docker-compose up -d
```

This will start:
- **API** - http://localhost:8000
- **Worker** - Celery worker for background tasks
- **Beat** - Celery beat scheduler
- **PostgreSQL** - Database on port 5432
- **Redis** - Cache/broker on port 6379
- **Prometheus** - http://localhost:9090
- **Grafana** - http://localhost:3000 (admin/admin)

4. **Access the API documentation**

Open http://localhost:8000/docs for the interactive API documentation (Swagger UI).

## API Endpoints

### Authentication

- `POST /api/v1/auth/login` - Login and get JWT token
- `GET /api/v1/auth/me` - Get current user info

### Servers

- `GET /api/v1/servers/` - List all servers
- `POST /api/v1/servers/` - Create a new server
- `GET /api/v1/servers/{id}` - Get server details
- `PATCH /api/v1/servers/{id}` - Update server
- `DELETE /api/v1/servers/{id}` - Delete server

### Metrics

- `GET /api/v1/metrics/servers/{id}/summary` - Get server metrics from Prometheus

### Alert Rules

- `GET /api/v1/alerts/rules/` - List alert rules
- `POST /api/v1/alerts/rules/` - Create alert rule
- `GET /api/v1/alerts/rules/{id}` - Get alert rule
- `PATCH /api/v1/alerts/rules/{id}` - Update alert rule
- `DELETE /api/v1/alerts/rules/{id}` - Delete alert rule

### Alert Events

- `GET /api/v1/alerts/events/` - List alert events
- `GET /api/v1/alerts/events/{id}` - Get alert event

### Health Check

- `GET /api/v1/health/liveness` - Liveness probe

### WebSocket

- `WS /ws/metrics/{server_id}` - Stream real-time metrics

## Usage Examples

### 1. Create a User (Manual Database Setup)

Since user registration is not implemented in the API, you need to create a user directly in the database:

```python
# Run this in a Python shell inside the API container
from app.models import User
from app.core import get_password_hash
from app.db import SessionLocal

db = SessionLocal()
user = User(
    email="admin@example.com",
    hashed_password=get_password_hash("admin123"),
    is_superuser=True
)
db.add(user)
db.commit()
```

Or use Docker exec:

```bash
docker exec -it vigil-api python -c "
from app.models import User
from app.core import get_password_hash
from app.db import SessionLocal

db = SessionLocal()
user = User(email='admin@example.com', hashed_password=get_password_hash('admin123'), is_superuser=True)
db.add(user)
db.commit()
print('User created successfully')
"
```

### 2. Login and Get Token

```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@example.com&password=admin123"
```

Response:
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer"
}
```

### 3. Create a Server

```bash
curl -X POST "http://localhost:8000/api/v1/servers/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Production Server",
    "job_name": "node",
    "instance": "prod-server:9100",
    "is_active": true
  }'
```

### 4. Create an Alert Rule

```bash
curl -X POST "http://localhost:8000/api/v1/alerts/rules/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "High CPU Alert",
    "server_id": 1,
    "metric_name": "cpu_usage",
    "promql": "100 - (avg(irate(node_cpu_seconds_total{mode=\"idle\"}[5m])) * 100)",
    "threshold": 80.0,
    "comparison": ">",
    "repeat_interval_sec": 300,
    "is_active": true,
    "channel": "telegram"
  }'
```

### 5. Get Server Metrics

```bash
curl -X GET "http://localhost:8000/api/v1/metrics/servers/1/summary" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 6. WebSocket Connection (JavaScript Example)

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/metrics/1');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Metrics:', data.metrics);
};
```

## Running Tests

```bash
# Enter the backend directory
cd backend

# Install dependencies
pip install -r requirements.txt

# Run tests
pytest app/tests/ -v

# Run tests with coverage
pytest app/tests/ --cov=app --cov-report=html
```

## Celery Tasks

### Alert Checking

The `check_alert_rules` task runs periodically (default: every 60 seconds) to:

1. Fetch all active alert rules
2. Query Prometheus for each rule's metric
3. Compare the result against the threshold
4. Create alert events and send notifications if triggered
5. Respect the repeat interval to avoid notification spam

## Telegram Setup

To enable Telegram notifications:

1. Create a bot using [@BotFather](https://t.me/botfather)
2. Get your bot token
3. Start a chat with your bot
4. Get your chat ID (you can use [@userinfobot](https://t.me/userinfobot))
5. Set `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` in `.env`

## Monitoring Actual Servers

To monitor real servers, you need to:

1. Install [Node Exporter](https://github.com/prometheus/node_exporter) on target servers
2. Configure Prometheus to scrape those servers (edit `deploy/prometheus.yml`)
3. Restart Prometheus container

Example `prometheus.yml` configuration:

```yaml
scrape_configs:
  - job_name: 'production-servers'
    static_configs:
      - targets:
        - 'server1.example.com:9100'
        - 'server2.example.com:9100'
```

## Development

### Running without Docker

```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Run database migrations (if using Alembic)
alembic upgrade head

# Start the API
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# In another terminal, start Celery worker
celery -A app.core.celery_app worker --loglevel=info

# In another terminal, start Celery beat
celery -A app.core.celery_app beat --loglevel=info
```

## Production Deployment

For production:

1. **Change SECRET_KEY** to a strong random value
2. **Use strong database credentials**
3. **Enable HTTPS** with a reverse proxy (nginx/traefik)
4. **Configure CORS** properly in `.env`
5. **Set up database backups**
6. **Configure proper logging**
7. **Use Docker secrets** for sensitive data
8. **Set resource limits** in docker-compose.yml

## Troubleshooting

### Database connection errors

```bash
# Check if PostgreSQL is running
docker-compose ps

# View database logs
docker-compose logs db
```

### Celery not processing tasks

```bash
# Check worker logs
docker-compose logs worker

# Check beat scheduler logs
docker-compose logs beat
```

### Prometheus connection errors

```bash
# Check Prometheus is accessible
curl http://localhost:9090/-/healthy

# View Prometheus logs
docker-compose logs prometheus
```

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
