# 📊 Руководство по мониторингу

## Обзор

Данный документ описывает полную стратегию мониторинга Claude Code Bot, включая метрики, алерты, дашборды и процедуры реагирования на инциденты. Мониторинг построен на принципах наблюдаемости (Observability) с использованием современных инструментов.

## 🎯 Философия мониторинга

### Три столпа наблюдаемости

**1. Метрики (Metrics)**

- Количественные показатели системы
- Временные ряды данных
- Агрегация и тренды

**2. Логирование (Logs)**

- Детализированные события системы
- Контекстуальная информация
- Трассировка выполнения

**3. Трассировка (Traces)**

- Путь запроса через систему
- Производительность компонентов
- Зависимости между сервисами

### Принципы мониторинга

- **USE Method** — Utilization, Saturation, Errors
- **RED Method** — Rate, Errors, Duration  
- **Four Golden Signals** — Latency, Traffic, Errors, Saturation
- **SLI/SLO Approach** — Service Level Indicators & Objectives

## 📈 Метрики системы

### Application Metrics

**HTTP Requests:**

```prometheus
# Request rate (requests per second)
rate(http_requests_total[5m])

# Error rate (percentage)
rate(http_requests_total{status=~"5.."}[5m]) / rate(http_requests_total[5m]) * 100

# Response time percentiles
histogram_quantile(0.50, rate(http_request_duration_seconds_bucket[5m]))
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))
histogram_quantile(0.99, rate(http_request_duration_seconds_bucket[5m]))
```

**Business Metrics:**

```prometheus
# Integration creation rate
rate(integrations_created_total[1h])

# Integration success rate
rate(integrations_success_total[1h]) / rate(integrations_total[1h]) * 100

# Webhook processing rate
rate(webhooks_processed_total[5m])

# AI API calls
rate(claude_api_calls_total[5m])

# GitHub API calls
rate(github_api_calls_total[5m])
```

**System Resources:**

```prometheus
# CPU usage
rate(container_cpu_usage_seconds_total[5m]) * 100

# Memory usage
container_memory_usage_bytes / container_spec_memory_limit_bytes * 100

# Disk usage
(node_filesystem_size_bytes - node_filesystem_free_bytes) / node_filesystem_size_bytes * 100

# Network I/O
rate(container_network_receive_bytes_total[5m])
rate(container_network_transmit_bytes_total[5m])
```

### Database Metrics

**PostgreSQL Monitoring:**

```prometheus
# Connection count
pg_stat_activity_count

# Query performance
rate(pg_stat_statements_calls[5m])
pg_stat_statements_mean_time_ms

# Database size
pg_database_size_bytes

# Lock waits
pg_stat_activity_max_tx_duration

# Replication lag
pg_replication_lag_seconds
```

**Redis Monitoring:**

```prometheus
# Memory usage
redis_memory_used_bytes / redis_memory_max_bytes * 100

# Connected clients
redis_connected_clients

# Commands per second
rate(redis_commands_processed_total[5m])

# Cache hit rate
rate(redis_keyspace_hits_total[5m]) / (rate(redis_keyspace_hits_total[5m]) + rate(redis_keyspace_misses_total[5m])) * 100
```

### Infrastructure Metrics

**Kubernetes Metrics:**

```prometheus
# Pod status
kube_pod_status_phase

# Node resources
kube_node_status_capacity
kube_node_status_allocatable

# Container restarts
rate(kube_pod_container_status_restarts_total[1h])

# Deployment status
kube_deployment_status_replicas_available
```

## 🚨 Алертинг

### Alert Categories

**1. Critical Alerts (P0)**

- Service completely down
- Data loss risk  
- Security breach
- Response time: Immediate

**2. High Priority Alerts (P1)**

- Service degradation
- High error rate
- Performance issues
- Response time: 15 minutes

**3. Medium Priority Alerts (P2)**

- Resource warnings
- Non-critical failures
- Trend concerns
- Response time: 1 hour

**4. Low Priority Alerts (P3)**

- Informational
- Capacity planning
- Maintenance reminders
- Response time: Next business day

### Critical Alert Rules

```yaml
# alertmanager/alerts.yml
groups:
  - name: critical-alerts
    rules:
      - alert: ServiceDown
        expr: up{job="claude-code-bot"} == 0
        for: 30s
        labels:
          severity: critical
        annotations:
          summary: "Service {{ $labels.job }} is down"
          description: "Service has been down for more than 30 seconds"
          runbook_url: "https://docs.claude-code-bot.com/runbooks/service-down"
          
      - alert: HighErrorRate
        expr: |
          (
            rate(http_requests_total{status=~"5.."}[5m]) / 
            rate(http_requests_total[5m])
          ) * 100 > 5
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "High error rate detected"
          description: "Error rate is {{ $value | humanizePercentage }}"
          
      - alert: DatabaseDown
        expr: pg_up == 0
        for: 30s
        labels:
          severity: critical
        annotations:
          summary: "Database is down"
          description: "PostgreSQL database is not responding"
          
      - alert: HighResponseTime
        expr: |
          histogram_quantile(0.95, 
            rate(http_request_duration_seconds_bucket[5m])
          ) > 2
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High response time"
          description: "95th percentile latency is {{ $value }}s"
```

### Business Alert Rules

```yaml
  - name: business-alerts
    rules:
      - alert: IntegrationFailureSpike
        expr: |
          rate(integrations_failed_total[1h]) > 
          (rate(integrations_failed_total[24h]) * 3)
        for: 10m
        labels:
          severity: high
        annotations:
          summary: "Integration failure spike detected"
          description: "Integration failures increased by {{ $value }}x"
          
      - alert: LowIntegrationCreationRate
        expr: rate(integrations_created_total[2h]) < 0.001  # Less than 1 per hour
        for: 30m
        labels:
          severity: medium
        annotations:
          summary: "Low integration creation rate"
          description: "No integrations created in last 2 hours"
          
      - alert: ExternalAPIRateLimit
        expr: claude_api_rate_limit_remaining < 100
        for: 1m
        labels:
          severity: high
        annotations:
          summary: "Claude API rate limit approaching"
          description: "Only {{ $value }} requests remaining"
          
      - alert: WebhookProcessingLag
        expr: webhook_queue_depth > 1000
        for: 5m
        labels:
          severity: medium
        annotations:
          summary: "Webhook processing lag"
          description: "{{ $value }} webhooks in queue"
```

### Infrastructure Alert Rules

```yaml
  - name: infrastructure-alerts
    rules:
      - alert: HighCPUUsage
        expr: |
          (
            rate(container_cpu_usage_seconds_total[5m]) * 100
          ) > 80
        for: 10m
        labels:
          severity: medium
        annotations:
          summary: "High CPU usage"
          description: "CPU usage is {{ $value }}% on {{ $labels.pod }}"
          
      - alert: HighMemoryUsage
        expr: |
          (
            container_memory_usage_bytes / 
            container_spec_memory_limit_bytes * 100
          ) > 85
        for: 5m
        labels:
          severity: medium
        annotations:
          summary: "High memory usage"
          description: "Memory usage is {{ $value }}% on {{ $labels.pod }}"
          
      - alert: PodCrashLooping
        expr: |
          rate(kube_pod_container_status_restarts_total[1h]) > 0
        labels:
          severity: high
        annotations:
          summary: "Pod crash looping"
          description: "Pod {{ $labels.pod }} has restarted {{ $value }} times"
          
      - alert: DiskSpaceRunningOut
        expr: |
          (
            (node_filesystem_size_bytes - node_filesystem_free_bytes) / 
            node_filesystem_size_bytes * 100
          ) > 90
        for: 5m
        labels:
          severity: high
        annotations:
          summary: "Disk space running out"
          description: "Disk usage is {{ $value }}% on {{ $labels.device }}"
```

## 📊 Dashboard Design

### Executive Dashboard

**Purpose:** High-level business metrics for management

**Panels:**

1. **Service Health Overview**
   - Uptime percentage (24h, 7d, 30d)
   - Current active integrations
   - Response time trend

2. **Business KPIs**
   - Integrations created today/week/month
   - Success rate trend
   - Top integration types

3. **User Activity**
   - API requests per day
   - Webhook events processed
   - Error rate trend

4. **Revenue Impact** (if applicable)
   - Cost per integration
   - API usage costs
   - ROI metrics

### Operations Dashboard

**Purpose:** Technical health monitoring for ops team

**Panels:**

1. **System Overview**
   - Service status (green/red indicators)
   - Request rate and error rate
   - Response time percentiles

2. **Infrastructure Health**
   - CPU/Memory usage by service
   - Database connections and performance
   - Pod status and restarts

3. **External Dependencies**
   - Claude API status and rate limits
   - GitHub API status and rate limits
   - Third-party service health

4. **Alert Summary**
   - Current active alerts
   - Alert history
   - MTTR trends

### Development Dashboard

**Purpose:** Application performance for developers

**Panels:**

1. **Application Metrics**
   - HTTP status code distribution
   - Endpoint performance breakdown
   - Database query performance

2. **Integration Metrics**
   - Integration creation pipeline status
   - AI generation success rate
   - Code review metrics

3. **Error Analysis**
   - Error rate by endpoint
   - Exception types and frequency
   - Failed integration causes

4. **Performance Trends**
   - Response time trends
   - Database query timing
   - Cache hit rates

### Database Dashboard

**Purpose:** Database performance monitoring

**Panels:**

1. **Connection Management**
   - Active connections
   - Connection pool utilization
   - Wait events

2. **Query Performance**
   - Slow query log
   - Query execution time percentiles
   - Most frequent queries

3. **Resource Usage**
   - Database size growth
   - Index usage statistics
   - Lock contention

4. **Replication Health**
   - Replication lag
   - WAL generation rate
   - Backup status

### Sample Grafana Dashboard JSON

```json
{
  "dashboard": {
    "title": "Claude Code Bot - Operations",
    "panels": [
      {
        "title": "Request Rate",
        "type": "stat",
        "targets": [
          {
            "expr": "rate(http_requests_total[5m])",
            "legendFormat": "RPS"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "color": {"mode": "thresholds"},
            "thresholds": {
              "steps": [
                {"color": "green", "value": 0},
                {"color": "yellow", "value": 100},
                {"color": "red", "value": 500}
              ]
            }
          }
        }
      },
      {
        "title": "Error Rate",
        "type": "stat", 
        "targets": [
          {
            "expr": "rate(http_requests_total{status=~\"5..\"}[5m]) / rate(http_requests_total[5m]) * 100",
            "legendFormat": "Error %"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "unit": "percent",
            "thresholds": {
              "steps": [
                {"color": "green", "value": 0},
                {"color": "yellow", "value": 1},
                {"color": "red", "value": 5}
              ]
            }
          }
        }
      }
    ]
  }
}
```

## 🔍 Логирование

### Logging Strategy

**Log Levels:**

- **ERROR** — System errors requiring attention
- **WARN** — Warnings that don't break functionality  
- **INFO** — General information about system operation
- **DEBUG** — Detailed information for troubleshooting

**Structured Logging Format:**

```json
{
  "timestamp": "2024-01-15T10:30:00.123Z",
  "level": "INFO",
  "service": "api",
  "component": "integration_service",
  "trace_id": "abc-123-def",
  "span_id": "456-ghi",
  "user_id": "user-789",
  "integration_id": "int-456",
  "message": "Integration created successfully",
  "context": {
    "integration_type": "slack",
    "processing_time_ms": 1234,
    "github_issue_id": "123"
  }
}
```

### Log Aggregation

**ELK Stack Configuration:**

**Elasticsearch Index Template:**

```json
{
  "index_patterns": ["claude-code-bot-*"],
  "template": {
    "settings": {
      "number_of_shards": 3,
      "number_of_replicas": 1,
      "index.lifecycle.name": "claude-code-bot-policy",
      "index.lifecycle.rollover_alias": "claude-code-bot"
    },
    "mappings": {
      "properties": {
        "timestamp": {"type": "date"},
        "level": {"type": "keyword"},
        "service": {"type": "keyword"},
        "component": {"type": "keyword"},
        "trace_id": {"type": "keyword"},
        "message": {"type": "text"},
        "context": {"type": "object"}
      }
    }
  }
}
```

**Logstash Pipeline:**

```ruby
input {
  beats {
    port => 5044
  }
}

filter {
  if [fields][service] == "claude-code-bot" {
    json {
      source => "message"
    }
    
    date {
      match => [ "timestamp", "ISO8601" ]
      target => "@timestamp"
    }
    
    mutate {
      add_field => { "service_name" => "claude-code-bot" }
      remove_field => [ "timestamp" ]
    }
    
    if [level] == "ERROR" {
      mutate {
        add_tag => [ "error" ]
      }
    }
  }
}

output {
  elasticsearch {
    hosts => ["elasticsearch:9200"]
    index => "claude-code-bot-%{+YYYY.MM.dd}"
    template_name => "claude-code-bot"
  }
}
```

**Kibana Dashboards:**

1. **Error Analysis Dashboard:**
   - Error count over time
   - Top error messages
   - Error distribution by service
   - Error correlation with deployments

2. **Performance Dashboard:**
   - Request processing time distribution
   - Slow request analysis
   - Database query performance
   - External API call timing

3. **Business Intelligence Dashboard:**
   - Integration creation patterns
   - User activity analysis
   - Popular integration types
   - Geographic usage patterns

### Log Retention Policy

```yaml
# Elasticsearch ILM Policy
{
  "policy": {
    "phases": {
      "hot": {
        "actions": {
          "rollover": {
            "max_size": "50gb",
            "max_age": "1d"
          }
        }
      },
      "warm": {
        "min_age": "7d",
        "actions": {
          "allocate": {
            "number_of_replicas": 0
          }
        }
      },
      "cold": {
        "min_age": "30d",
        "actions": {
          "allocate": {
            "number_of_replicas": 0
          }
        }
      },
      "delete": {
        "min_age": "90d"
      }
    }
  }
}
```

## 🔗 Distributed Tracing

### Tracing Architecture

**OpenTelemetry Configuration:**

```yaml
# otel-collector.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: otel-collector-config
data:
  config.yaml: |
    receivers:
      otlp:
        protocols:
          grpc:
            endpoint: 0.0.0.0:4317
          http:
            endpoint: 0.0.0.0:4318
    
    processors:
      batch:
        timeout: 1s
        send_batch_size: 1024
      memory_limiter:
        limit_mib: 512
    
    exporters:
      jaeger:
        endpoint: jaeger-collector:14250
        tls:
          insecure: true
    
    service:
      pipelines:
        traces:
          receivers: [otlp]
          processors: [memory_limiter, batch]
          exporters: [jaeger]
```

**Application Tracing:**

```python
# app/tracing.py
from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor

def configure_tracing():
    trace.set_tracer_provider(TracerProvider())
    tracer = trace.get_tracer(__name__)
    
    jaeger_exporter = JaegerExporter(
        agent_host_name="jaeger-agent",
        agent_port=6831,
    )
    
    span_processor = BatchSpanProcessor(jaeger_exporter)
    trace.get_tracer_provider().add_span_processor(span_processor)
    
    # Auto-instrument frameworks
    FastAPIInstrumentor.instrument()
    RequestsInstrumentor.instrument()
    SQLAlchemyInstrumentor.instrument()

# Usage in application
@tracer.start_as_current_span("create_integration")
async def create_integration(data: IntegrationCreateSchema):
    with tracer.start_as_current_span("validate_request") as span:
        span.set_attribute("integration.type", data.type)
        span.set_attribute("integration.name", data.name)
        
        # Validation logic
        ...
    
    with tracer.start_as_current_span("generate_code"):
        # AI code generation
        ...
    
    return result
```

### Trace Analysis

**Key Traces to Monitor:**

1. **Integration Creation Flow:**
   - GitHub Issue → Requirements Analysis → Code Generation → PR Creation
   - Expected duration: < 15 minutes
   - Critical path: AI API calls

2. **Webhook Processing:**
   - Webhook Receive → Validation → Processing → Response
   - Expected duration: < 500ms
   - Critical path: Database operations

3. **API Request Processing:**
   - Request → Authentication → Business Logic → Response
   - Expected duration: < 200ms
   - Critical path: Database queries

**Sample Trace Queries:**

```promql
# Slow traces (> 5 seconds)
histogram_quantile(0.95, trace_duration_seconds) > 5

# Error traces
trace_error_rate > 0.01

# External dependency latency
histogram_quantile(0.95, external_call_duration_seconds{service="claude-api"})
```

## 🎭 Synthetic Monitoring

### Health Check Endpoints

**Application Health Checks:**

```python
# app/health.py
@router.get("/health/live")
async def liveness_check():
    """Kubernetes liveness probe"""
    return {"status": "alive", "timestamp": datetime.utcnow()}

@router.get("/health/ready") 
async def readiness_check():
    """Kubernetes readiness probe"""
    checks = {
        "database": await check_database(),
        "redis": await check_redis(),
        "claude_api": await check_claude_api()
    }
    
    if not all(checks.values()):
        raise HTTPException(status_code=503, detail=checks)
    
    return {"status": "ready", "checks": checks}

@router.get("/health/startup")
async def startup_check():
    """Kubernetes startup probe"""
    return {"status": "started", "version": get_version()}
```

**External Monitoring:**

```bash
#!/bin/bash
# synthetic-monitor.sh

# Basic health check
HEALTH_STATUS=$(curl -s -o /dev/null -w "%{http_code}" https://api.claude-code-bot.com/health)
if [[ "$HEALTH_STATUS" != "200" ]]; then
    echo "CRITICAL: Health check failed with status $HEALTH_STATUS"
    exit 2
fi

# API functionality test
API_RESPONSE=$(curl -s -H "Authorization: Bearer $TEST_API_KEY" \
  https://api.claude-code-bot.com/v1/integrations | jq '.total')
if [[ "$API_RESPONSE" == "null" ]]; then
    echo "CRITICAL: API functionality test failed"
    exit 2
fi

# Integration creation test (full flow)
ISSUE_ID=$(gh issue create --title "Test Integration" --body "Test synthetic monitoring" --label "integration-request")
sleep 300  # Wait 5 minutes
PR_COUNT=$(gh pr list --label "auto-generated" | wc -l)
if [[ "$PR_COUNT" -eq "0" ]]; then
    echo "CRITICAL: Integration creation test failed"
    exit 2
fi

echo "OK: All synthetic checks passed"
```

### Monitoring Automation

**Automated Health Checks:**

```yaml
# k8s/synthetic-monitor.yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: synthetic-monitor
spec:
  schedule: "*/5 * * * *"  # Every 5 minutes
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: monitor
            image: curlimages/curl:latest
            command:
            - /bin/sh
            - -c
            - |
              curl -f https://api.claude-code-bot.com/health || exit 1
              curl -f https://api.claude-code-bot.com/v1/health || exit 1
          restartPolicy: OnFailure
```

**Chaos Engineering:**

```yaml
# chaos-experiment.yaml
apiVersion: litmuschaos.io/v1alpha1
kind: ChaosExperiment
metadata:
  name: pod-delete
spec:
  definition:
    image: "litmuschaos/go-runner:latest"
    args:
    - -c
    - ./experiments -name pod-delete
    command:
    - /bin/bash
    env:
    - name: TOTAL_CHAOS_DURATION
      value: '30'
    - name: CHAOS_INTERVAL
      value: '10'
    - name: FORCE
      value: 'false'
    labels:
      name: pod-delete
```

## 📱 Notification Management

### Notification Channels

**Slack Integration:**

```yaml
# alertmanager.yml
route:
  group_by: ['alertname', 'cluster', 'service']
  group_wait: 10s
  group_interval: 10s
  repeat_interval: 1h
  receiver: 'default'
  routes:
  - match:
      severity: critical
    receiver: 'critical-alerts'
  - match:
      severity: warning
    receiver: 'warning-alerts'

receivers:
- name: 'critical-alerts'
  slack_configs:
  - api_url: 'https://hooks.slack.com/services/XXX/YYY/ZZZ'
    channel: '#ops-critical'
    title: '🚨 Critical Alert'
    text: '{{ range .Alerts }}{{ .Annotations.summary }}{{ end }}'
    
- name: 'warning-alerts'
  slack_configs:
  - api_url: 'https://hooks.slack.com/services/XXX/YYY/ZZZ'
    channel: '#ops-warnings'
    title: '⚠️ Warning Alert'
    text: '{{ range .Alerts }}{{ .Annotations.summary }}{{ end }}'
```

**PagerDuty Integration:**

```yaml
- name: 'pagerduty'
  pagerduty_configs:
  - routing_key: 'YOUR_PAGERDUTY_INTEGRATION_KEY'
    description: '{{ range .Alerts }}{{ .Annotations.summary }}{{ end }}'
    severity: '{{ .GroupLabels.severity }}'
    details:
      firing: '{{ .Alerts.Firing | len }}'
      resolved: '{{ .Alerts.Resolved | len }}'
      runbook: '{{ range .Alerts }}{{ .Annotations.runbook_url }}{{ end }}'
```

### Alert Fatigue Management

**Alert Grouping Strategy:**

```yaml
route:
  # Group alerts by service for 5 minutes
  group_by: ['service', 'alertname']
  group_wait: 5m
  
  # Send a notification for new groups every 10 minutes
  group_interval: 10m
  
  # Repeat notifications every 4 hours for firing alerts
  repeat_interval: 4h
  
  routes:
  # Critical alerts bypass grouping
  - match:
      severity: critical
    group_wait: 0s
    group_interval: 30s
    repeat_interval: 5m
    receiver: critical-immediate
```

**Alert Inhibition Rules:**

```yaml
inhibit_rules:
# Inhibit warning alerts if critical alert is firing
- source_match:
    severity: critical
  target_match:
    severity: warning
  equal: ['service', 'instance']

# Don't alert on high error rate if service is down
- source_match:
    alertname: ServiceDown
  target_match:
    alertname: HighErrorRate
  equal: ['service']
```

## 📋 Runbooks

### Service Down Runbook

**Alert:** `ServiceDown`
**Severity:** Critical
**Response Time:** Immediate

**Investigation Steps:**

1. **Check Service Status:**

```bash
kubectl get pods -n claude-code-bot -l app=api
kubectl describe pod api-deployment-xxx -n claude-code-bot
```

2. **Check Recent Deployments:**

```bash
kubectl rollout history deployment/api-deployment -n claude-code-bot
kubectl get events --sort-by=.metadata.creationTimestamp -n claude-code-bot
```

3. **Check Dependencies:**

```bash
# Database
kubectl exec -it postgres-0 -- pg_isready
# Redis  
kubectl exec -it redis-0 -- redis-cli ping
```

4. **Recovery Actions:**

```bash
# Restart deployment
kubectl rollout restart deployment/api-deployment -n claude-code-bot

# Scale up if needed
kubectl scale deployment api-deployment --replicas=5 -n claude-code-bot

# Rollback if recent deployment
kubectl rollout undo deployment/api-deployment -n claude-code-bot
```

### High Error Rate Runbook

**Alert:** `HighErrorRate`
**Severity:** Critical
**Response Time:** 15 minutes

**Investigation Steps:**

1. **Identify Error Types:**

```bash
kubectl logs -l app=api -n claude-code-bot --since=10m | grep ERROR | head -20
```

2. **Check External Dependencies:**

```bash
# Test Claude API
curl -H "Authorization: Bearer $CLAUDE_API_KEY" https://api.anthropic.com/v1/usage

# Test GitHub API
curl -H "Authorization: token $GITHUB_TOKEN" https://api.github.com/rate_limit
```

3. **Database Health:**

```bash
kubectl exec -it postgres-0 -- psql -c "SELECT count(*) FROM pg_stat_activity;"
```

## 🎯 Performance Monitoring

### Performance Benchmarks

**Response Time SLOs:**

- P50: < 100ms
- P95: < 500ms  
- P99: < 1000ms

**Throughput SLOs:**

- Normal load: 100 RPS
- Peak load: 500 RPS
- Burst capacity: 1000 RPS

**Availability SLO:**

- 99.9% monthly uptime
- 99.95% during business hours

### Load Testing

**Continuous Load Testing:**

```yaml
# k6-load-test.yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: load-test
spec:
  schedule: "0 2 * * *"  # Daily at 2 AM
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: k6
            image: grafana/k6:latest
            command:
            - k6
            - run
            - --quiet
            - --out
            - influxdb=http://influxdb:8086/k6
            - /scripts/load-test.js
            volumeMounts:
            - name: test-scripts
              mountPath: /scripts
          volumes:
          - name: test-scripts
            configMap:
              name: k6-scripts
```

**Load Test Script:**

```javascript
// load-test.js
import http from 'k6/http';
import { check } from 'k6';

export let options = {
  stages: [
    { duration: '2m', target: 10 },   // Ramp up
    { duration: '5m', target: 10 },   // Stay at 10 users
    { duration: '2m', target: 50 },   // Ramp up to 50 users
    { duration: '5m', target: 50 },   // Stay at 50 users
    { duration: '2m', target: 0 },    // Ramp down
  ],
  thresholds: {
    http_req_duration: ['p(95)<500'],  // 95% of requests under 500ms
    http_req_failed: ['rate<0.01'],    // Error rate under 1%
  },
};

export default function() {
  let response = http.get('https://api.claude-code-bot.com/v1/integrations');
  
  check(response, {
    'status is 200': (r) => r.status === 200,
    'response time < 500ms': (r) => r.timings.duration < 500,
  });
}
```

## 🎯 Заключение

Comprehensive мониторинг Claude Code Bot обеспечивает:

**🔍 Полную видимость:**

- Метрики на всех уровнях системы
- Детализированное логирование
- Распределенная трассировка

**🚨 Proactive алертинг:**

- SLO-based алерты
- Business impact фокус
- Автоматизированное реагирование

**📊 Actionable insights:**

- Performance тренды
- Capacity planning данные
- Business intelligence

**🛡️ Операционную устойчивость:**

- Быстрое обнаружение проблем
- Automated recovery процедуры
- Continuous improvement через данные

Мониторинг - это не просто набор инструментов, это культура наблюдаемости, которая позволяет команде быть proactive и data-driven в принятии решений. 🚀
