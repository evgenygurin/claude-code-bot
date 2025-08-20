# ⚙️ Операционное руководство

## Обзор

Данный документ содержит полное руководство по эксплуатации и поддержке Claude Code Bot в production среде. Документ предназначен для DevOps инженеров, системных администраторов и команд поддержки.

## 🏗️ Архитектура производственной системы

### Компоненты системы

**Core Services:**

```text
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   API Gateway   │────│   Web API       │────│ Integration     │
│   (nginx)       │    │   (FastAPI)     │    │ Manager         │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Load          │    │   AI            │    │   Webhook       │
│   Balancer      │    │   Orchestrator  │    │   Handler       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

**Data Layer:**

```text
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   PostgreSQL    │    │   Redis Cache   │    │   Object        │
│   (Primary DB)  │    │   (Session)     │    │   Storage (S3)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

**Infrastructure Services:**

```text
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Prometheus    │    │   Grafana       │    │   AlertManager  │
│   (Metrics)     │    │   (Dashboard)   │    │   (Alerts)      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Топология сети

**Production Environment:**

```text
Internet
    │
    ▼
[CloudFlare CDN] ── [WAF Protection]
    │
    ▼
[Load Balancer] ── [SSL Termination]
    │
    ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Pod 1         │    │   Pod 2         │    │   Pod 3         │
│   api:8000      │    │   api:8000      │    │   api:8000      │
│   worker:9000   │    │   worker:9000   │    │   worker:9000   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │   Database      │
                    │   Cluster       │
                    └─────────────────┘
```

## 🚀 Развертывание и управление

### Процедура развертывания

**Pre-deployment Checklist:**

1. **Infrastructure Check:**

```bash
# Проверить доступность cluster
kubectl cluster-info

# Проверить health nodes
kubectl get nodes

# Проверить namespace
kubectl get ns claude-code-bot
```

2. **Database Migration:**

```bash
# Backup current database
kubectl exec -it postgres-0 -- pg_dump claude_bot_prod > backup-$(date +%Y%m%d).sql

# Run migrations
kubectl exec -it api-deployment-xxx -- alembic upgrade head

# Verify migration
kubectl exec -it api-deployment-xxx -- alembic current
```

3. **Configuration Check:**

```bash
# Verify secrets
kubectl get secrets -n claude-code-bot

# Check configmaps
kubectl get configmaps -n claude-code-bot

# Validate environment variables
kubectl exec -it api-deployment-xxx -- env | grep -E "(CLAUDE_|GITHUB_|DATABASE_)"
```

### Blue-Green Deployment

**Step 1: Deploy Green Environment**

```bash
# Create green namespace
kubectl create namespace claude-code-bot-green

# Deploy to green
helm upgrade claude-code-bot-green ./helm-chart \
  --namespace claude-code-bot-green \
  --set image.tag=$NEW_VERSION \
  --set environment=green

# Wait for ready
kubectl wait --for=condition=ready pod \
  -l app=claude-code-bot -n claude-code-bot-green \
  --timeout=300s
```

**Step 2: Health Verification**

```bash
# Health check
curl -f https://green.claude-code-bot.com/health

# Smoke tests
kubectl exec -it api-deployment-xxx -n claude-code-bot-green \
  -- python -m pytest tests/smoke/ -v

# Load test (optional)
hey -n 1000 -c 10 https://green.claude-code-bot.com/v1/health
```

**Step 3: Traffic Switch**

```bash
# Switch ingress to green
kubectl patch ingress api-ingress -n claude-code-bot \
  --type='json' \
  -p='[{"op": "replace", "path": "/spec/rules/0/http/paths/0/backend/service/name", "value": "api-service-green"}]'

# Monitor for 10 minutes
watch -n 10 "kubectl get pods -n claude-code-bot-green"

# Verify metrics
curl https://api.claude-code-bot.com/metrics | grep -E "(request_duration|error_rate)"
```

**Step 4: Cleanup Old Version**

```bash
# If everything is OK, cleanup blue
kubectl delete namespace claude-code-bot-blue

# Rename green to production
kubectl label namespace claude-code-bot-green environment=production
```

### Rollback Procedure

**Emergency Rollback:**

```bash
# Immediate rollback
kubectl rollout undo deployment/api-deployment -n claude-code-bot

# Check status
kubectl rollout status deployment/api-deployment -n claude-code-bot

# Verify health
curl https://api.claude-code-bot.com/health
```

**Database Rollback:**

```bash
# Restore from backup
kubectl exec -it postgres-0 -- psql claude_bot_prod < backup-20240101.sql

# Rollback migration
kubectl exec -it api-deployment-xxx -- alembic downgrade -1
```

## 📊 Мониторинг и метрики

### Key Performance Indicators (KPIs)

**Service Level Objectives (SLOs):**

| Метрика | Target | Measurement Window | Alert Threshold |
|---------|--------|-------------------|-----------------|
| Availability | 99.9% | 30 days | < 99.5% |
| Response Time (P95) | 500ms | 5 minutes | > 1s |
| Error Rate | < 0.1% | 5 minutes | > 1% |
| Integration Success Rate | 98% | 1 hour | < 95% |

**Business Metrics:**

| Метрика | Description | Target |
|---------|-------------|--------|
| Integrations Created/Day | Daily new integrations | > 10 |
| Active Integrations | Currently running | Track trends |
| Events Processed/Hour | Webhook events handled | > 1000 |
| Time to Integration | From issue to PR | < 15 minutes |

### Monitoring Setup

**Prometheus Configuration:**

```yaml
# prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "alert_rules.yml"

scrape_configs:
  - job_name: 'claude-code-bot'
    static_configs:
      - targets: ['api-service:8000']
    metrics_path: /metrics
    scrape_interval: 10s
    
  - job_name: 'postgresql'
    static_configs:
      - targets: ['postgres-exporter:9187']
    
  - job_name: 'redis'
    static_configs:
      - targets: ['redis-exporter:9121']

  - job_name: 'kubernetes-pods'
    kubernetes_sd_configs:
      - role: pod
    relabel_configs:
      - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_scrape]
        action: keep
        regex: true
```

**Alert Rules:**

```yaml
# alert_rules.yml
groups:
  - name: claude-code-bot
    rules:
      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.01
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "High error rate detected"
          description: "Error rate is {{ $value | humanizePercentage }}"
          
      - alert: HighResponseTime
        expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 0.5
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High response time"
          description: "95th percentile latency is {{ $value }}s"
          
      - alert: IntegrationFailures
        expr: rate(integration_failures_total[1h]) > 0.05
        for: 10m
        labels:
          severity: critical
        annotations:
          summary: "High integration failure rate"
          description: "Integration failure rate is {{ $value | humanizePercentage }}"
          
      - alert: DatabaseConnections
        expr: pg_stat_activity_count > 80
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High database connection count"
          description: "Database has {{ $value }} active connections"
          
      - alert: PodRestart
        expr: increase(kube_pod_container_status_restarts_total[1h]) > 0
        labels:
          severity: warning
        annotations:
          summary: "Pod restarted"
          description: "Pod {{ $labels.pod }} has restarted {{ $value }} times"
```

### Grafana Dashboards

**Main Dashboard Panels:**

1. **System Health:**
   - Uptime percentage
   - Response time percentiles
   - Error rate trend
   - Active connections

2. **Business Metrics:**
   - Integrations created per day
   - Webhook events processed
   - AI API calls
   - GitHub API calls

3. **Infrastructure:**
   - CPU/Memory usage
   - Disk I/O
   - Network traffic
   - Pod status

**Sample Grafana Queries:**

```promql
# Request rate
rate(http_requests_total[5m])

# Error rate
rate(http_requests_total{status=~"5.."}[5m]) / rate(http_requests_total[5m])

# Response time P95
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))

# Integration success rate
rate(integrations_created_total[1h]) / rate(integration_requests_total[1h])

# Database query time
rate(pg_stat_statements_mean_time_ms[5m])

# Memory usage
container_memory_usage_bytes / container_spec_memory_limit_bytes
```

## 🔧 Обслуживание и администрирование

### Регулярные задачи

**Ежедневные задачи:**

1. **System Health Check:**

```bash
#!/bin/bash
# daily-health-check.sh

echo "=== Daily Health Check $(date) ==="

# Check pod status
kubectl get pods -n claude-code-bot --no-headers | grep -v Running | wc -l

# Check recent errors
kubectl logs --since=24h -l app=claude-code-bot -n claude-code-bot | grep -i error | wc -l

# Check database connections
kubectl exec -it postgres-0 -- psql -c "SELECT count(*) FROM pg_stat_activity;"

# Check disk usage
df -h | grep -E "(80%|90%|95%)"

# Check certificate expiration
echo | openssl s_client -servername api.claude-code-bot.com -connect api.claude-code-bot.com:443 2>/dev/null | openssl x509 -noout -dates

echo "=== Health Check Complete ==="
```

2. **Backup Verification:**

```bash
#!/bin/bash
# verify-backups.sh

# Check latest backup
LATEST_BACKUP=$(find /backups -name "*.sql" -mtime -1 | head -1)
if [[ -z "$LATEST_BACKUP" ]]; then
    echo "ERROR: No recent backup found!"
    exit 1
fi

# Verify backup integrity
pg_restore --list "$LATEST_BACKUP" > /dev/null 2>&1
if [[ $? -eq 0 ]]; then
    echo "Backup verification: OK"
else
    echo "ERROR: Backup verification failed!"
    exit 1
fi
```

**Еженедельные задачи:**

1. **Performance Review:**

```bash
#!/bin/bash
# weekly-performance-review.sh

# Generate performance report
cat << EOF > weekly-report-$(date +%Y%m%d).md
# Weekly Performance Report

## SLO Compliance
- Availability: $(prometheus-query "avg_over_time(up[7d])" | awk '{print $2 * 100}')%
- P95 Response Time: $(prometheus-query "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[7d]))")s
- Error Rate: $(prometheus-query "rate(http_requests_total{status=~\"5..\"}[7d]) / rate(http_requests_total[7d])" | awk '{print $2 * 100}')%

## Business Metrics
- Integrations Created: $(prometheus-query "increase(integrations_created_total[7d])")
- Events Processed: $(prometheus-query "increase(webhook_events_total[7d])")
- Top Integration Types: $(kubectl exec -it postgres-0 -- psql -t -c "SELECT type, count(*) FROM integrations WHERE created_at > now() - interval '7 days' GROUP BY type ORDER BY count DESC LIMIT 5;")

## Infrastructure
- Average CPU Usage: $(prometheus-query "avg_over_time(cpu_usage_percent[7d])")%
- Average Memory Usage: $(prometheus-query "avg_over_time(memory_usage_percent[7d])")%
- Database Size: $(kubectl exec -it postgres-0 -- psql -t -c "SELECT pg_size_pretty(pg_database_size('claude_bot_prod'));")
EOF
```

2. **Security Update:**

```bash
#!/bin/bash
# security-updates.sh

# Check for security updates
kubectl get pods -n claude-code-bot -o jsonpath='{.items[*].spec.containers[*].image}' | \
  xargs -I {} docker run --rm clair-scanner --ip host.docker.internal {}

# Update secrets rotation schedule
kubectl get secrets -n claude-code-bot -o json | \
  jq '.items[] | select(.metadata.creationTimestamp < (now - 2592000 | strftime("%Y-%m-%dT%H:%M:%SZ")))'
```

**Месячные задачи:**

1. **Capacity Planning:**

```bash
#!/bin/bash
# capacity-planning.sh

# Analyze resource trends
echo "=== Capacity Planning Report ==="
echo "CPU Trend (30d): $(prometheus-query 'avg_over_time(cpu_usage_percent[30d])')"
echo "Memory Trend (30d): $(prometheus-query 'avg_over_time(memory_usage_percent[30d])')"
echo "Database Growth: $(kubectl exec -it postgres-0 -- psql -t -c "SELECT pg_size_pretty(pg_database_size('claude_bot_prod'));")"
echo "Storage Usage: $(df -h /data | tail -1 | awk '{print $5}')"

# Predict future needs
CURRENT_CPU=$(prometheus-query 'avg(cpu_usage_percent)')
GROWTH_RATE=1.1  # 10% monthly growth
PREDICTED_CPU=$(echo "$CURRENT_CPU * $GROWTH_RATE" | bc)
echo "Predicted CPU usage next month: ${PREDICTED_CPU}%"
```

### Database Administration

**Database Maintenance:**

```sql
-- Weekly maintenance queries
-- Run every Sunday night

-- Update table statistics
ANALYZE;

-- Rebuild indexes if needed
REINDEX DATABASE claude_bot_prod;

-- Cleanup old data (events older than 90 days)
DELETE FROM integration_events WHERE created_at < NOW() - INTERVAL '90 days';

-- Vacuum to reclaim space
VACUUM FULL;

-- Check database size
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables 
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
LIMIT 10;
```

**Database Performance Monitoring:**

```sql
-- Long running queries
SELECT 
    now() - pg_stat_activity.query_start AS duration,
    query,
    state,
    wait_event_type,
    wait_event
FROM pg_stat_activity 
WHERE (now() - pg_stat_activity.query_start) > interval '5 minutes';

-- Connection analysis
SELECT 
    state,
    count(*)
FROM pg_stat_activity 
GROUP BY state;

-- Slow queries (from pg_stat_statements)
SELECT 
    query,
    calls,
    mean_time,
    total_time,
    rows
FROM pg_stat_statements
ORDER BY mean_time DESC
LIMIT 10;
```

### Log Management

**Log Rotation Configuration:**

```text
# /etc/logrotate.d/claude-code-bot
/var/log/claude-code-bot/*.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
    create 0644 claude-bot claude-bot
    postrotate
        systemctl reload claude-code-bot
    endscript
}
```

**Centralized Logging:**

```yaml
# fluentd-config.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: fluentd-config
data:
  fluent.conf: |
    <source>
      @type tail
      path /var/log/containers/claude-code-bot*.log
      pos_file /var/log/fluentd-docker.log.pos
      tag kubernetes.*
      format json
      time_format %Y-%m-%dT%H:%M:%S.%NZ
    </source>
    
    <filter kubernetes.**>
      @type kubernetes_metadata
    </filter>
    
    <match kubernetes.**>
      @type elasticsearch
      host elasticsearch-service
      port 9200
      index_name claude-code-bot
      type_name _doc
    </match>
```

## 🔒 Безопасность операций

### Security Checklist

**Access Control:**

- [ ] RBAC настроен для всех пользователей
- [ ] Multi-factor authentication включен
- [ ] Service accounts имеют минимальные права
- [ ] API keys ротируются каждые 90 дней

**Network Security:**

- [ ] Network policies настроены
- [ ] TLS 1.2+ используется везде
- [ ] Firewall rules актуальны
- [ ] VPN доступ для администраторов

**Data Protection:**

- [ ] Encryption at rest включен
- [ ] Backup шифрование настроено
- [ ] Sensitive данные не логируются
- [ ] GDPR compliance соблюдается

**Monitoring:**

- [ ] Security event logging включен
- [ ] Intrusion detection настроен
- [ ] Vulnerability scanning еженедельно
- [ ] Penetration testing квартально

### Security Incident Response

**Incident Classification:**

1. **P0 - Critical Security Incident:**
   - Data breach
   - System compromise
   - Service unavailable due to attack

2. **P1 - High Security Incident:**
   - Unauthorized access attempt
   - Malware detection
   - Critical vulnerability discovered

3. **P2 - Medium Security Incident:**
   - Policy violation
   - Non-critical vulnerability
   - Suspicious activity

**Response Procedure:**

```bash
#!/bin/bash
# security-incident-response.sh

INCIDENT_TYPE=$1
SEVERITY=$2

echo "=== Security Incident Response ==="
echo "Type: $INCIDENT_TYPE"
echo "Severity: $SEVERITY"
echo "Time: $(date)"

case $SEVERITY in
  "P0")
    # Immediate isolation
    kubectl scale deployment api-deployment --replicas=0 -n claude-code-bot
    
    # Alert security team
    curl -X POST $SLACK_WEBHOOK -d '{"text": "🚨 P0 Security Incident: '$INCIDENT_TYPE'"}'
    
    # Preserve evidence
    kubectl logs -l app=claude-code-bot -n claude-code-bot > incident-logs-$(date +%Y%m%d-%H%M).txt
    ;;
    
  "P1")
    # Enhanced monitoring
    kubectl patch deployment api-deployment -p '{"spec":{"template":{"spec":{"containers":[{"name":"api","env":[{"name":"LOG_LEVEL","value":"DEBUG"}]}]}}}}' -n claude-code-bot
    
    # Alert ops team
    curl -X POST $SLACK_WEBHOOK -d '{"text": "⚠️ P1 Security Incident: '$INCIDENT_TYPE'"}'
    ;;
esac
```

## 🔄 Disaster Recovery

### Backup Strategy

**Database Backup:**

```bash
#!/bin/bash
# database-backup.sh

BACKUP_DIR="/backups/postgresql"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="${BACKUP_DIR}/claude_bot_prod_${TIMESTAMP}.sql"

# Create backup
kubectl exec -it postgres-0 -- pg_dump claude_bot_prod > "$BACKUP_FILE"

# Compress backup
gzip "$BACKUP_FILE"

# Upload to S3
aws s3 cp "${BACKUP_FILE}.gz" "s3://claude-code-bot-backups/postgresql/"

# Cleanup old backups (keep 30 days)
find "$BACKUP_DIR" -name "*.sql.gz" -mtime +30 -delete

# Verify backup
if [[ -f "${BACKUP_FILE}.gz" ]]; then
    echo "Backup created successfully: ${BACKUP_FILE}.gz"
else
    echo "ERROR: Backup failed!"
    exit 1
fi
```

**Application State Backup:**

```bash
#!/bin/bash
# application-backup.sh

BACKUP_DIR="/backups/application"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Backup Kubernetes resources
kubectl get all -n claude-code-bot -o yaml > "${BACKUP_DIR}/k8s-resources-${TIMESTAMP}.yaml"

# Backup secrets (encrypted)
kubectl get secrets -n claude-code-bot -o yaml | gpg --encrypt --recipient ops@company.com > "${BACKUP_DIR}/secrets-${TIMESTAMP}.yaml.gpg"

# Backup configurations
kubectl get configmaps -n claude-code-bot -o yaml > "${BACKUP_DIR}/configmaps-${TIMESTAMP}.yaml"

# Upload to S3
aws s3 sync "$BACKUP_DIR" "s3://claude-code-bot-backups/application/"
```

### Recovery Procedures

**Database Recovery:**

```bash
#!/bin/bash
# database-recovery.sh

BACKUP_FILE=$1
if [[ -z "$BACKUP_FILE" ]]; then
    echo "Usage: $0 <backup-file>"
    exit 1
fi

echo "=== Database Recovery ==="
echo "Backup file: $BACKUP_FILE"
echo "WARNING: This will overwrite the current database!"
read -p "Continue? (yes/no): " confirm

if [[ "$confirm" != "yes" ]]; then
    echo "Recovery cancelled"
    exit 1
fi

# Stop application
kubectl scale deployment api-deployment --replicas=0 -n claude-code-bot

# Restore database
kubectl exec -it postgres-0 -- dropdb claude_bot_prod
kubectl exec -it postgres-0 -- createdb claude_bot_prod
kubectl exec -it postgres-0 -- psql claude_bot_prod < "$BACKUP_FILE"

# Restart application
kubectl scale deployment api-deployment --replicas=3 -n claude-code-bot

# Verify recovery
sleep 30
curl -f https://api.claude-code-bot.com/health

echo "=== Recovery Complete ==="
```

**Full System Recovery:**

```bash
#!/bin/bash
# full-system-recovery.sh

echo "=== Full System Recovery ==="

# 1. Restore infrastructure
terraform apply -var="environment=production"

# 2. Restore Kubernetes cluster
kubectl apply -f k8s-resources-backup.yaml

# 3. Restore secrets
gpg --decrypt secrets-backup.yaml.gpg | kubectl apply -f -

# 4. Restore database
./database-recovery.sh latest-backup.sql

# 5. Verify all services
kubectl wait --for=condition=ready pod -l app=claude-code-bot --timeout=300s

# 6. Run health checks
./health-check.sh

echo "=== Recovery Complete ==="
```

### Recovery Time Objectives

| Scenario | RTO Target | RPO Target | Steps |
|----------|------------|------------|-------|
| Database failure | 1 hour | 15 minutes | Restore from latest backup |
| Single pod failure | 2 minutes | 0 | Kubernetes auto-restart |
| Node failure | 5 minutes | 0 | Pod rescheduling |
| Complete cluster failure | 2 hours | 1 hour | Full infrastructure rebuild |
| Data center failure | 4 hours | 4 hours | Failover to DR region |

## 📋 Troubleshooting Guide

### Common Issues

**1. High Memory Usage:**

```bash
# Diagnose
kubectl top pods -n claude-code-bot
kubectl describe pod api-deployment-xxx -n claude-code-bot

# Fix
kubectl set resources deployment api-deployment --limits=memory=1Gi -n claude-code-bot
kubectl rollout restart deployment api-deployment -n claude-code-bot
```

**2. Database Connection Pool Exhaustion:**

```bash
# Diagnose
kubectl exec -it postgres-0 -- psql -c "SELECT count(*) FROM pg_stat_activity;"

# Fix
kubectl set env deployment api-deployment DATABASE_MAX_CONNECTIONS=20 -n claude-code-bot
```

**3. Integration Processing Delays:**

```bash
# Check queue depth
kubectl exec -it redis-0 -- redis-cli llen integration_queue

# Scale workers
kubectl scale deployment worker-deployment --replicas=5 -n claude-code-bot

# Check AI API rate limits
curl -H "Authorization: Bearer $CLAUDE_API_KEY" https://api.anthropic.com/v1/usage
```

### Emergency Procedures

**Service Degradation:**

```bash
#!/bin/bash
# emergency-scale.sh

# Scale up all services
kubectl scale deployment api-deployment --replicas=10 -n claude-code-bot
kubectl scale deployment worker-deployment --replicas=8 -n claude-code-bot

# Enable maintenance mode
kubectl set env deployment api-deployment MAINTENANCE_MODE=true -n claude-code-bot

# Alert team
curl -X POST $SLACK_WEBHOOK -d '{"text": "🚨 Emergency scaling activated"}'
```

**Complete Service Outage:**

```bash
#!/bin/bash
# emergency-failover.sh

# Switch to maintenance page
kubectl apply -f maintenance-page.yaml

# Diagnose issue
kubectl get events --sort-by=.metadata.creationTimestamp -n claude-code-bot

# If critical, initiate failover
if [[ "$1" == "failover" ]]; then
    # Update DNS to point to DR site
    aws route53 change-resource-record-sets --hosted-zone-id Z1234567890 --change-batch file://failover-dns.json
    
    # Alert team
    curl -X POST $EMERGENCY_WEBHOOK -d '{"text": "🚨 CRITICAL: Failover to DR site initiated"}'
fi
```

## 📊 Performance Optimization

### Resource Optimization

**CPU Optimization:**

```yaml
# api-deployment.yaml
resources:
  requests:
    cpu: 250m
    memory: 256Mi
  limits:
    cpu: 1000m
    memory: 512Mi

# Horizontal Pod Autoscaler
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: api-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: api-deployment
  minReplicas: 3
  maxReplicas: 20
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

**Database Optimization:**

```sql
-- Index optimization
CREATE INDEX CONCURRENTLY idx_integrations_status_created 
ON integrations(status, created_at) 
WHERE status = 'active';

-- Connection pooling
ALTER SYSTEM SET max_connections = 200;
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET effective_cache_size = '1GB';
ALTER SYSTEM SET work_mem = '4MB';

-- Query optimization
EXPLAIN ANALYZE SELECT * FROM integrations WHERE status = 'active' AND created_at > NOW() - INTERVAL '1 day';
```

### Caching Strategy

**Redis Configuration:**

```conf
# redis.conf
maxmemory 512mb
maxmemory-policy allkeys-lru
save 900 1
save 300 10
save 60 10000

# Specific to application
timeout 300
tcp-keepalive 60
```

**Application Caching:**

```python
# Cache configuration
CACHE_CONFIG = {
    'integration_metadata': {'ttl': 3600, 'max_size': 1000},
    'user_sessions': {'ttl': 1800, 'max_size': 5000},
    'api_responses': {'ttl': 300, 'max_size': 10000},
    'webhook_signatures': {'ttl': 600, 'max_size': 2000}
}
```

## 🎯 Заключение

Операционное руководство Claude Code Bot обеспечивает надежную эксплуатацию системы в production среде. Регулярное выполнение процедур обслуживания, мониторинг ключевых метрик и готовность к аварийным ситуациям гарантируют высокую доступность и производительность системы.

**Ключевые принципы операций:**

- **Proactive monitoring** — предупреждение проблем
- **Automated recovery** — быстрое восстановление
- **Security first** — безопасность во всех процессах
- **Documentation** — актуальная документация процедур
- **Continuous improvement** — постоянное совершенствование

Помните: операционная отличность достигается через систематический подход, автоматизацию рутинных задач и готовность к непредвиденным ситуациям. 🚀
