# Vigil Architecture

## System Overview

```
┌─────────────┐
│   Client    │
│ (Browser/   │
│  Mobile)    │
└──────┬──────┘
       │
       │ HTTP/WebSocket
       │
┌──────▼──────────────────────────────────────┐
│           FastAPI Application                │
│  ┌────────────────────────────────────────┐ │
│  │         API Endpoints (v1)             │ │
│  │  • Auth   • Servers   • Metrics        │ │
│  │  • Alerts • Health    • WebSocket      │ │
│  └────────────────────────────────────────┘ │
│                                              │
│  ┌────────────────────────────────────────┐ │
│  │           Services Layer               │ │
│  │  • Authentication                      │ │
│  │  • Prometheus Integration              │ │
│  │  • Telegram Notifications              │ │
│  │  • Alert Processing                    │ │
│  └────────────────────────────────────────┘ │
└──────┬────────────┬─────────────┬───────────┘
       │            │             │
       │            │             │
┌──────▼──────┐ ┌───▼──────┐ ┌───▼─────────┐
│ PostgreSQL  │ │  Redis   │ │ Prometheus  │
│  Database   │ │  Cache   │ │   Metrics   │
└─────────────┘ └──────────┘ └─────────────┘
                     │
                     │
              ┌──────▼──────────┐
              │ Celery Workers  │
              │   & Scheduler   │
              └──────┬──────────┘
                     │
              ┌──────▼──────────┐
              │    Telegram     │
              │    Bot API      │
              └─────────────────┘
```

## Components

### 1. FastAPI Application (backend/app/)

The main application server that handles:
- REST API requests
- WebSocket connections for real-time metrics
- Authentication and authorization
- Request validation and response serialization

**Key Features:**
- Async/await for high performance
- JWT-based authentication
- Automatic API documentation (Swagger/OpenAPI)
- CORS support for cross-origin requests

### 2. Database Layer (PostgreSQL)

Stores persistent data:
- **Users** - Authentication credentials and permissions
- **Servers** - Monitored server configurations
- **AlertRules** - Alert conditions and thresholds
- **AlertEvents** - Historical alert occurrences

**ORM:** SQLAlchemy for database operations

### 3. Celery Workers

Background task processing:
- **Periodic Tasks** - Check alert rules every N seconds
- **Alert Evaluation** - Query Prometheus and compare against thresholds
- **Notifications** - Send alerts via Telegram

**Broker:** Redis for task queue management

### 4. Prometheus Integration

Metrics collection and querying:
- Queries Prometheus using PromQL
- Retrieves system metrics (CPU, memory, disk, network)
- Supports custom metric queries for alert rules

### 5. Notification System

Alert delivery:
- **Telegram** - Bot-based notifications with formatted messages
- Respects repeat intervals to avoid spam
- Extensible for other channels (email, Slack, etc.)

## Data Flow

### Metrics Query Flow

```
1. Client → GET /api/v1/metrics/servers/{id}/summary
2. API validates authentication (JWT)
3. API queries database for server details
4. PrometheusService constructs and executes PromQL queries
5. Prometheus returns metric data
6. API formats and returns data to client
```

### Alert Processing Flow

```
1. Celery Beat scheduler triggers check_alert_rules task
2. Worker fetches all active AlertRules from database
3. For each rule:
   a. Query Prometheus with rule's PromQL
   b. Compare result against threshold
   c. If triggered and not recently alerted:
      - Create AlertEvent in database
      - Send notification via Telegram
4. Repeat after interval
```

### WebSocket Real-time Metrics

```
1. Client connects to WS /ws/metrics/{server_id}
2. Server validates server exists and is active
3. Loop:
   a. Query Prometheus for metrics
   b. Send JSON to client
   c. Wait N seconds (configurable)
4. Continue until client disconnects
```

## Security

### Authentication
- JWT tokens with configurable expiration
- Bcrypt password hashing
- OAuth2 password flow for token generation

### Authorization
- User-based access control
- Superuser privileges for administrative actions
- All endpoints (except /auth/login) require authentication

## Configuration

### Environment Variables
All configuration is managed through environment variables:
- Database connection strings
- Redis URLs
- Prometheus endpoints
- Telegram credentials
- Security settings (JWT secret, token expiration)

### Settings Management
- Pydantic Settings for type-safe configuration
- Validation of required fields at startup
- Support for .env files

## Scaling Considerations

### Horizontal Scaling
- Multiple API instances behind a load balancer
- Multiple Celery workers for parallel task processing
- Redis Sentinel for high availability

### Performance
- Async database queries (optional with asyncpg)
- Connection pooling
- Redis caching for frequently accessed data
- Prometheus query optimization

### Monitoring
- Health check endpoints
- Prometheus metrics from the app itself
- Celery task monitoring
- Database connection monitoring

## Development Workflow

1. **Local Development**
   - Run services via Docker Compose
   - Hot reload enabled for code changes
   - Access API docs at /docs

2. **Testing**
   - Unit tests with pytest
   - Integration tests with TestClient
   - Mocked external dependencies (Prometheus, Telegram)

3. **Deployment**
   - Build Docker images
   - Deploy with docker-compose
   - Configure environment variables
   - Run database migrations (if applicable)

## Future Enhancements

- [ ] Multi-tenancy support
- [ ] User management API endpoints
- [ ] More notification channels (Email, Slack, PagerDuty)
- [ ] Alert rule templates
- [ ] Dashboard UI
- [ ] Alert acknowledgment and silencing
- [ ] Grafana dashboard integration
- [ ] Alert history visualization
- [ ] Role-based access control (RBAC)
- [ ] API rate limiting
