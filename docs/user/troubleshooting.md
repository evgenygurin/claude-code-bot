# 🔧 Руководство по устранению неполадок

## Обзор

Этот документ поможет вам диагностировать и исправить типичные проблемы при работе с Claude Code Bot. Руководство организовано по категориям проблем с пошаговыми инструкциями по их решению.

## 🚨 Быстрая диагностика

### Проверка статуса системы

**1. Статус сервисов:**

```bash
# Проверка доступности API
curl -s "https://api.claude-code-bot.com/health" | jq

# Проверка статуса интеграции
curl -s "https://api.claude-code-bot.com/v1/integrations/{integration-id}/status" \
  -H "Authorization: Bearer YOUR_API_KEY" | jq
```

**2. Системные метрики:**

- Посетите [Status Page](https://status.claude-code-bot.com)
- Проверьте [System Dashboard](https://dashboard.claude-code-bot.com/system)

**3. Быстрая самодиагностика:**

| Проблема | Быстрая проверка | Решение |
|----------|------------------|---------|
| Интеграция не работает | `GET /integrations/{id}/status` | См. [Проблемы интеграций](#проблемы-интеграций) |
| Webhook не приходят | Проверить webhook URL | См. [Проблемы с webhook](#проблемы-с-webhook) |
| API возвращает 401 | Проверить API key | См. [Аутентификация](#проблемы-аутентификации) |
| Медленные ответы | Проверить метрики latency | См. [Производительность](#проблемы-производительности) |

## 🔌 Проблемы интеграций

### Интеграция не создается

**Симптомы:**

- GitHub Issue создан, но PR не появляется
- Статус интеграции застрял в "requested"
- Нет автоматических комментариев в issue

**Диагностика:**

**1. Проверьте формат issue:**

```markdown
# ❌ Неправильно - отсутствует шаблон
Create Slack integration

# ✅ Правильно - используется шаблон
## 🔌 Запрос на создание интеграции

**Название сервиса:** Slack
**Тип интеграции:** Webhook
...
```

**2. Проверьте лейблы:**

```bash
# Проверить лейблы issue
curl -s "https://api.github.com/repos/{owner}/{repo}/issues/{issue_number}" | jq '.labels[].name'
```

**3. Проверьте логи обработки:**

```bash
curl -s "https://api.claude-code-bot.com/v1/issues/{issue-id}/logs" \
  -H "Authorization: Bearer YOUR_API_KEY" | jq
```

**Решения:**

**A. Исправить формат issue:**

```markdown
1. Отредактируйте issue
2. Добавьте недостающие секции из шаблона
3. Убедитесь, что все обязательные поля заполнены
```

**B. Добавить корректный лейбл:**

```bash
# Через GitHub CLI
gh issue edit {issue-number} --add-label "integration-request"

# Через API
curl -X POST "https://api.github.com/repos/{owner}/{repo}/issues/{issue_number}/labels" \
  -H "Authorization: token YOUR_GITHUB_TOKEN" \
  -d '["integration-request"]'
```

**C. Повторно запустить обработку:**

```bash
curl -X POST "https://api.claude-code-bot.com/v1/issues/{issue-id}/reprocess" \
  -H "Authorization: Bearer YOUR_API_KEY"
```

### Интеграция в статусе "failed"

**Симптомы:**

- Статус: `"status": "failed"`
- Error message в логах
- Отсутствует Pull Request

**Диагностика:**

**1. Получить детали ошибки:**

```bash
curl -s "https://api.claude-code-bot.com/v1/integrations/{id}" \
  -H "Authorization: Bearer YOUR_API_KEY" | jq '.error_details'
```

**2. Проверить логи генерации:**

```bash
curl -s "https://api.claude-code-bot.com/v1/integrations/{id}/logs?level=error" \
  -H "Authorization: Bearer YOUR_API_KEY"
```

**Типичные ошибки и решения:**

**A. Claude API rate limit:**

```json
{
  "error": "Rate limit exceeded",
  "retry_after": "300s"
}
```

**Решение:** Подождите и повторите запрос.

**B. Недостаточно информации:**

```json
{
  "error": "Insufficient integration requirements",
  "missing_fields": ["target_service", "api_endpoints"]
}
```

**Решение:** Дополните описание интеграции недостающей информацией.

**C. Конфликт зависимостей:**

```json
{
  "error": "Dependency conflict detected",
  "conflicts": ["package_version", "api_compatibility"]
}
```

**Решение:** Сообщите в поддержку для резолва конфликтов.

### Интеграция не активируется

**Симптомы:**

- Статус: `"status": "inactive"`
- Pull Request создан, но интеграция не работает
- Конфигурация задана, но события не обрабатываются

**Диагностика:**

**1. Проверить конфигурацию:**

```bash
curl -s "https://api.claude-code-bot.com/v1/integrations/{id}/config" \
  -H "Authorization: Bearer YOUR_API_KEY" | jq
```

**2. Проверить необходимые права доступа:**

```bash
curl -s "https://api.claude-code-bot.com/v1/integrations/{id}/permissions" \
  -H "Authorization: Bearer YOUR_API_KEY" | jq
```

**Решения:**

**A. Добавить недостающую конфигурацию:**

```bash
curl -X PATCH "https://api.claude-code-bot.com/v1/integrations/{id}/config" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "slack_token": "xoxb-your-token",
    "github_token": "ghp_your-token"
  }'
```

**B. Предоставить права доступа:**

- GitHub: настройте GitHub App permissions
- Slack: добавьте необходимые OAuth scopes
- API keys: проверьте права доступа

**C. Активировать интеграцию вручную:**

```bash
curl -X POST "https://api.claude-code-bot.com/v1/integrations/{id}/activate" \
  -H "Authorization: Bearer YOUR_API_KEY"
```

## 📡 Проблемы с Webhook

### Webhook события не приходят

**Симптомы:**

- Интеграция активна, но события не обрабатываются
- В логах нет входящих webhook
- Метрики показывают 0 событий

**Диагностика:**

**1. Проверить настройку webhook URL:**

```bash
# Для GitHub
curl -s "https://api.github.com/repos/{owner}/{repo}/hooks" \
  -H "Authorization: token YOUR_GITHUB_TOKEN" | jq

# Для других сервисов - проверьте в их настройках
```

**2. Проверить доступность webhook endpoint:**

```bash
curl -X POST "https://your-domain.claude-code-bot.com/webhooks/{integration-id}" \
  -H "Content-Type: application/json" \
  -d '{"test": "payload"}' -v
```

**3. Проверить webhook секреты:**

```bash
curl -s "https://api.claude-code-bot.com/v1/integrations/{id}/webhook-config" \
  -H "Authorization: Bearer YOUR_API_KEY" | jq '.secret_configured'
```

**Решения:**

**A. Настроить корректный webhook URL:**

```text
✅ Правильный формат:
https://your-domain.claude-code-bot.com/webhooks/{integration-id}

❌ Неправильные форматы:
http://... (без HTTPS)
.../webhook/... (без 's' в webhook)
.../webhooks/wrong-id
```

**B. Обновить webhook конфигурацию:**

**GitHub:**

```bash
curl -X PATCH "https://api.github.com/repos/{owner}/{repo}/hooks/{hook_id}" \
  -H "Authorization: token YOUR_GITHUB_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "config": {
      "url": "https://your-domain.claude-code-bot.com/webhooks/{integration-id}",
      "content_type": "json",
      "secret": "your-webhook-secret"
    },
    "events": ["issues", "pull_request"]
  }'
```

**Slack:**

```bash
# Обновите Event Subscriptions URL в Slack App настройках
https://api.slack.com/apps/{app-id}/event-subscriptions
```

**C. Настроить webhook секрет:**

```bash
curl -X PATCH "https://api.claude-code-bot.com/v1/integrations/{id}/webhook-secret" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"secret": "your-webhook-secret"}'
```

### Webhook возвращают ошибки

**Симптомы:**

- HTTP 401/403/500 ошибки от webhook endpoint
- События частично обрабатываются
- Высокий error rate в метриках

**Диагностика:**

**1. Проверить HTTP статус коды:**

```bash
curl -X POST "https://your-domain.claude-code-bot.com/webhooks/{integration-id}" \
  -H "Content-Type: application/json" \
  -H "X-Hub-Signature-256: sha256=test" \
  -d '{"test": "payload"}' -w "%{http_code}" -o /dev/null
```

**2. Проверить webhook логи:**

```bash
curl -s "https://api.claude-code-bot.com/v1/integrations/{id}/webhook-logs?limit=50" \
  -H "Authorization: Bearer YOUR_API_KEY" | jq
```

**Типичные ошибки:**

**HTTP 401 - Unauthorized:**

```json
{
  "error": "Invalid webhook signature",
  "message": "Signature verification failed"
}
```

**Решение:** Проверьте webhook секрет в обоих системах.

**HTTP 403 - Forbidden:**

```json
{
  "error": "Integration inactive",
  "message": "Integration must be active to receive webhooks"
}
```

**Решение:** Активируйте интеграцию.

**HTTP 500 - Internal Server Error:**

```json
{
  "error": "Processing failed",
  "message": "Failed to process webhook payload"
}
```

**Решение:** Проверьте формат payload и обратитесь в поддержку.

## 🔐 Проблемы аутентификации

### API Key проблемы

**Симптомы:**

- HTTP 401 "Invalid API Key"
- HTTP 403 "Insufficient permissions"
- Запросы не авторизуются

**Диагностика:**

**1. Проверить формат API key:**

```bash
# Правильный формат
curl -H "Authorization: Bearer ccb_1234567890abcdef..." \
  "https://api.claude-code-bot.com/v1/user"

# Неправильный формат
curl -H "Authorization: ccb_1234567890abcdef..." # ❌ Отсутствует Bearer
```

**2. Проверить права доступа:**

```bash
curl -s "https://api.claude-code-bot.com/v1/auth/verify" \
  -H "Authorization: Bearer YOUR_API_KEY" | jq
```

**3. Проверить срок действия:**

```bash
curl -s "https://api.claude-code-bot.com/v1/auth/token-info" \
  -H "Authorization: Bearer YOUR_API_KEY" | jq '.expires_at'
```

**Решения:**

**A. Создать новый API key:**

```bash
# Через dashboard или API
curl -X POST "https://api.claude-code-bot.com/v1/auth/tokens" \
  -H "Authorization: Bearer EXISTING_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Integration API Key",
    "permissions": ["integrations.read", "integrations.write"]
  }'
```

**B. Обновить права доступа:**

```bash
curl -X PATCH "https://api.claude-code-bot.com/v1/auth/tokens/{token-id}" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "permissions": ["integrations.read", "integrations.write", "webhooks.receive"]
  }'
```

### Внешние сервисы аутентификация

**GitHub Token проблемы:**

**Симптомы:**

- "Bad credentials" при обращении к GitHub API
- PR не создаются автоматически
- Repository access denied

**Решения:**

```bash
# 1. Проверить GitHub token
curl -s -H "Authorization: token YOUR_GITHUB_TOKEN" \
  "https://api.github.com/user"

# 2. Проверить scopes
curl -s -H "Authorization: token YOUR_GITHUB_TOKEN" \
  "https://api.github.com/user" -I | grep -i x-oauth-scopes

# 3. Создать новый token с правильными правами:
# repo, admin:repo_hook, user:email
```

**Slack Token проблемы:**

**Симптомы:**

- "invalid_auth" при отправке сообщений
- Bot не может писать в каналы
- Permissions errors

**Решения:**

```bash
# 1. Проверить Slack token
curl -X POST "https://slack.com/api/auth.test" \
  -H "Authorization: Bearer YOUR_SLACK_TOKEN"

# 2. Проверить bot permissions
curl -X POST "https://slack.com/api/apps.permissions.info" \
  -H "Authorization: Bearer YOUR_SLACK_TOKEN"

# 3. Обновить bot scopes:
# chat:write, channels:read, groups:read, im:read, mpim:read
```

## ⚡ Проблемы производительности

### Медленные ответы API

**Симптомы:**

- Response time > 2 секунд
- Timeout errors
- High latency метрики

**Диагностика:**

**1. Проверить время ответа:**

```bash
curl -w "@curl-format.txt" -s -o /dev/null \
  "https://api.claude-code-bot.com/v1/integrations" \
  -H "Authorization: Bearer YOUR_API_KEY"

# curl-format.txt:
#      time_namelookup:  %{time_namelookup}\n
#         time_connect:  %{time_connect}\n
#      time_appconnect:  %{time_appconnect}\n
#     time_pretransfer:  %{time_pretransfer}\n
#        time_redirect:  %{time_redirect}\n
#   time_starttransfer:  %{time_starttransfer}\n
#                     ----------\n
#           time_total:  %{time_total}\n
```

**2. Проверить системные метрики:**

```bash
curl -s "https://api.claude-code-bot.com/v1/metrics/performance" \
  -H "Authorization: Bearer YOUR_API_KEY" | jq
```

**Решения:**

**A. Оптимизировать запросы:**

```bash
# Использовать пагинацию
curl "https://api.claude-code-bot.com/v1/integrations?limit=10&offset=0"

# Фильтровать ответы
curl "https://api.claude-code-bot.com/v1/integrations?fields=id,name,status"

# Кешировать результаты
curl -H "Cache-Control: max-age=300" "..."
```

**B. Batch запросы:**

```bash
# Вместо множественных запросов
curl -X POST "https://api.claude-code-bot.com/v1/integrations/batch" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "ids": ["id1", "id2", "id3"]
  }'
```

### High memory usage

**Симптомы:**

- Out of memory errors
- Slow processing
- Frequent restarts

**Решения:**

- Увеличьте rate limiting
- Используйте streaming для больших payload
- Оптимизируйте batch размеры
- Обратитесь в поддержку для scaling

## 📊 Проблемы мониторинга

### Отсутствуют метрики

**Симптомы:**

- Пустой dashboard
- Нет данных в графиках
- Missing metrics errors

**Диагностика:**

**1. Проверить сбор метрик:**

```bash
curl -s "https://api.claude-code-bot.com/v1/integrations/{id}/metrics/status" \
  -H "Authorization: Bearer YOUR_API_KEY"
```

**2. Проверить временной диапазон:**

```bash
# Метрики за последний час
curl -s "https://api.claude-code-bot.com/v1/integrations/{id}/metrics?from=1h" \
  -H "Authorization: Bearer YOUR_API_KEY"
```

**Решения:**

**A. Включить сбор метрик:**

```bash
curl -X PATCH "https://api.claude-code-bot.com/v1/integrations/{id}/monitoring" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "metrics_enabled": true,
    "logging_level": "info"
  }'
```

**B. Настроить retention period:**

```bash
curl -X PATCH "https://api.claude-code-bot.com/v1/integrations/{id}/monitoring" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "metrics_retention": "30d",
    "logs_retention": "7d"
  }'
```

### Алерты не работают

**Симптомы:**

- Нет уведомлений при проблемах
- Алерты не отправляются в Slack/Email
- False positive/negative алерты

**Диагностика:**

**1. Проверить конфигурацию алертов:**

```bash
curl -s "https://api.claude-code-bot.com/v1/integrations/{id}/alerts" \
  -H "Authorization: Bearer YOUR_API_KEY" | jq
```

**2. Тест алерта:**

```bash
curl -X POST "https://api.claude-code-bot.com/v1/integrations/{id}/alerts/test" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "alert_type": "error_rate",
    "notification_channel": "slack"
  }'
```

**Решения:**

**A. Настроить алерты:**

```bash
curl -X PUT "https://api.claude-code-bot.com/v1/integrations/{id}/alerts" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "rules": [
      {
        "name": "High Error Rate",
        "condition": "error_rate > 5%",
        "notification_channels": ["slack://dev-alerts", "email://team@company.com"],
        "severity": "critical"
      }
    ]
  }'
```

**B. Проверить notification каналы:**

```bash
# Для Slack
curl -X POST "https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK" \
  -H "Content-Type: application/json" \
  -d '{"text": "Test notification"}'

# Для Email - проверьте SMTP настройки
```

## 🔄 Проблемы синхронизации

### Дублирующие события

**Симптомы:**

- Одно и то же событие обрабатывается несколько раз
- Duplicate notifications
- High event count метрики

**Диагностика:**

**1. Проверить idempotency:**

```bash
curl -s "https://api.claude-code-bot.com/v1/integrations/{id}/events?duplicate=true" \
  -H "Authorization: Bearer YOUR_API_KEY"
```

**2. Проверить webhook delivery:**

```bash
# В GitHub проверить webhook deliveries
curl -s "https://api.github.com/repos/{owner}/{repo}/hooks/{hook_id}/deliveries" \
  -H "Authorization: token YOUR_GITHUB_TOKEN"
```

**Решения:**

**A. Включить idempotency:**

```bash
curl -X PATCH "https://api.claude-code-bot.com/v1/integrations/{id}/config" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "idempotency_enabled": true,
    "idempotency_window": "1h"
  }'
```

**B. Настроить deduplication:**

```bash
curl -X PATCH "https://api.claude-code-bot.com/v1/integrations/{id}/config" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "deduplication_enabled": true,
    "deduplication_key": "event_id"
  }'
```

### Пропуск событий

**Симптомы:**

- События не обрабатываются
- Gaps в event stream
- Missing notifications

**Диагностика:**

**1. Проверить event gaps:**

```bash
curl -s "https://api.claude-code-bot.com/v1/integrations/{id}/events/gaps" \
  -H "Authorization: Bearer YOUR_API_KEY"
```

**2. Проверить queue health:**

```bash
curl -s "https://api.claude-code-bot.com/v1/integrations/{id}/queue/status" \
  -H "Authorization: Bearer YOUR_API_KEY"
```

**Решения:**

**A. Увеличить retry attempts:**

```bash
curl -X PATCH "https://api.claude-code-bot.com/v1/integrations/{id}/config" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "retry_attempts": 5,
    "retry_backoff": "exponential"
  }'
```

**B. Replay пропущенных событий:**

```bash
curl -X POST "https://api.claude-code-bot.com/v1/integrations/{id}/replay" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "from": "2024-01-01T00:00:00Z",
    "to": "2024-01-02T00:00:00Z"
  }'
```

## 🛠️ Диагностические инструменты

### Health Check Script

```bash
#!/bin/bash
# health-check.sh

INTEGRATION_ID=$1
API_KEY=$2

if [[ -z "$INTEGRATION_ID" || -z "$API_KEY" ]]; then
    echo "Usage: $0 <integration-id> <api-key>"
    exit 1
fi

echo "🔍 Running health check for integration: $INTEGRATION_ID"
echo "=================================================="

# 1. Integration Status
echo "1. Integration Status:"
curl -s "https://api.claude-code-bot.com/v1/integrations/$INTEGRATION_ID" \
  -H "Authorization: Bearer $API_KEY" | jq '.status, .last_activity'

# 2. Configuration
echo "2. Configuration Status:"
curl -s "https://api.claude-code-bot.com/v1/integrations/$INTEGRATION_ID/config" \
  -H "Authorization: Bearer $API_KEY" | jq 'keys'

# 3. Recent Events
echo "3. Recent Events (last 10):"
curl -s "https://api.claude-code-bot.com/v1/integrations/$INTEGRATION_ID/events?limit=10" \
  -H "Authorization: Bearer $API_KEY" | jq '.[].timestamp, .[].type'

# 4. Error Rate
echo "4. Error Rate (last 1h):"
curl -s "https://api.claude-code-bot.com/v1/integrations/$INTEGRATION_ID/metrics?metric=error_rate&from=1h" \
  -H "Authorization: Bearer $API_KEY" | jq '.value'

# 5. Webhook Status
echo "5. Webhook Status:"
curl -w "%{http_code}" -o /dev/null -s \
  "https://your-domain.claude-code-bot.com/webhooks/$INTEGRATION_ID"

echo ""
echo "✅ Health check completed"
```

### Event Tracing

```python
# trace-event.py
import requests
import json
import sys

def trace_event(integration_id, event_id, api_key):
    headers = {"Authorization": f"Bearer {api_key}"}
    
    # Get event details
    event_url = f"https://api.claude-code-bot.com/v1/integrations/{integration_id}/events/{event_id}"
    event_response = requests.get(event_url, headers=headers)
    
    if event_response.status_code != 200:
        print(f"❌ Event not found: {event_response.status_code}")
        return
    
    event_data = event_response.json()
    
    print(f"📍 Event Trace: {event_id}")
    print("=" * 50)
    print(f"Timestamp: {event_data['timestamp']}")
    print(f"Type: {event_data['type']}")
    print(f"Status: {event_data['status']}")
    print(f"Processing Time: {event_data.get('processing_time', 'N/A')}")
    
    # Get processing steps
    steps_url = f"https://api.claude-code-bot.com/v1/integrations/{integration_id}/events/{event_id}/steps"
    steps_response = requests.get(steps_url, headers=headers)
    
    if steps_response.status_code == 200:
        steps = steps_response.json()
        print("\n📋 Processing Steps:")
        for i, step in enumerate(steps, 1):
            status_icon = "✅" if step['status'] == 'success' else "❌"
            print(f"  {i}. {status_icon} {step['name']} ({step.get('duration', 'N/A')})")
            if step['status'] == 'error':
                print(f"     Error: {step.get('error_message', 'Unknown error')}")

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python trace-event.py <integration-id> <event-id> <api-key>")
        sys.exit(1)
    
    trace_event(sys.argv[1], sys.argv[2], sys.argv[3])
```

## 📞 Получение помощи

### Сбор диагностической информации

**Перед обращением в поддержку соберите:**

```bash
# 1. Integration details
curl -s "https://api.claude-code-bot.com/v1/integrations/{id}" \
  -H "Authorization: Bearer YOUR_API_KEY" > integration-details.json

# 2. Recent logs
curl -s "https://api.claude-code-bot.com/v1/integrations/{id}/logs?limit=100&level=error" \
  -H "Authorization: Bearer YOUR_API_KEY" > recent-errors.json

# 3. System metrics
curl -s "https://api.claude-code-bot.com/v1/integrations/{id}/metrics?from=1h" \
  -H "Authorization: Bearer YOUR_API_KEY" > metrics.json

# 4. Configuration
curl -s "https://api.claude-code-bot.com/v1/integrations/{id}/config" \
  -H "Authorization: Bearer YOUR_API_KEY" > config.json
```

### Каналы поддержки

**🆓 Community Support:**

- [GitHub Issues](https://github.com/your-org/claude-code-bot/issues)
- [GitHub Discussions](https://github.com/your-org/claude-code-bot/discussions)
- [Stack Overflow](https://stackoverflow.com/questions/tagged/claude-code-bot)

**💼 Business Support:**

- 📧 Email: <support@claude-code-bot.com>
- 💬 Slack: [Support Channel](https://claude-bot-community.slack.com/channels/support)
- SLA: 24 hours

**🏢 Enterprise Support:**

- 📞 Phone: +1-800-CLAUDE-BOT
- 💬 Dedicated Slack channel
- SLA: 4 hours

### Шаблон запроса в поддержку

```markdown
## 🐛 Проблема
[Краткое описание проблемы]

## 🔍 Детали
- **Integration ID:** xxx-xxx-xxx
- **Error Message:** [Точный текст ошибки]
- **When:** [Когда началась проблема]
- **Frequency:** [Как часто происходит]

## 📋 Что уже проверили
- [ ] Status page
- [ ] Integration status
- [ ] API key validity
- [ ] Webhook configuration
- [ ] Recent logs

## 📊 Диагностические данные
[Прикрепите файлы: integration-details.json, recent-errors.json, etc.]

## 💼 Impact
- **Severity:** [Low/Medium/High/Critical]
- **Users Affected:** [Количество]
- **Business Impact:** [Описание влияния на бизнес]
```

## 🔧 Профилактика проблем

### Monitoring Best Practices

**1. Настройте алерты для:**

- Error rate > 1%
- Latency > 500ms
- Webhook failures
- Queue depth > 100

**2. Регулярно проверяйте:**

- API key expiration dates
- Webhook endpoint availability  
- External service quotas
- Integration health metrics

**3. Ведите changelog:**

- Документируйте изменения конфигурации
- Отслеживайте deployment время
- Коррелируйте проблемы с изменениями

### Backup Strategies

**1. Configuration backup:**

```bash
# Ежедневный backup конфигурации
curl -s "https://api.claude-code-bot.com/v1/integrations" \
  -H "Authorization: Bearer YOUR_API_KEY" | \
  jq '.[] | {id, name, config}' > "backup-$(date +%Y%m%d).json"
```

**2. Disaster recovery plan:**

- Документируйте критичные интеграции
- Подготовьте rollback procedures
- Тестируйте восстановление регулярно

## 🎯 Заключение

Большинство проблем с Claude Code Bot можно решить следуя этому руководству. Помните:

**🔍 Диагностика First:**

- Всегда начинайте с проверки статуса системы
- Собирайте логи и метрики
- Используйте диагностические инструменты

**🛠️ Систематический подход:**

- Следуйте пошаговым инструкциям
- Проверяйте каждое изменение
- Документируйте решения

**💪 Профилактика:**

- Настройте comprehensive monitoring
- Регулярно обновляйте конфигурацию
- Следите за best practices

Если проблема не решается, не стесняйтесь обращаться в поддержку — мы здесь, чтобы помочь! 🚀
