# 📡 API Reference — Claude Code Bot

## Обзор API

Claude Code Bot предоставляет comprehensive RESTful API для автоматизации создания и управления интеграциями. API следует принципам REST, использует JSON для обмена данными и поддерживает стандартные HTTP методы.

## Базовая информация

### Base URL

```text
Production:  https://api.claude-code-bot.com
Staging:     https://staging-api.claude-code-bot.com
Development: http://localhost:8000
```

### API Versioning

```text
Current Version: v1
URL Format: {base_url}/api/v1/{resource}
Header: Accept: application/vnd.claude-bot.v1+json
```

### Authentication

#### JWT Bearer Token

```http
Authorization: Bearer <jwt_token>
```

#### API Key

```http
X-API-Key: <api_key>
```

#### Example Authentication Flow

```bash
# 1. Login to get JWT token
curl -X POST https://api.claude-code-bot.com/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password"}'

# Response:
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "expires_in": 900
}

# 2. Use token for API calls
curl -X GET https://api.claude-code-bot.com/api/v1/integrations \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
```

### Content Types

```text
Request:  application/json
Response: application/json
Uploads:  multipart/form-data
```

### Rate Limiting

```text
Per User:    1000 requests/hour
Per IP:      100 requests/minute  
Per API Key: 5000 requests/hour
```

Rate limit headers:

```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1641024000
```

## Common Response Format

### Success Response

```json
{
  "data": {
    // Resource data
  },
  "meta": {
    "request_id": "req_abc123",
    "timestamp": "2025-01-01T12:00:00Z",
    "version": "v1"
  }
}
```

### Error Response

```json
{
  "error": {
    "type": "validation_error",
    "message": "Invalid request parameters",
    "details": {
      "field": "name",
      "code": "required",
      "message": "This field is required"
    }
  },
  "meta": {
    "request_id": "req_abc123",
    "timestamp": "2025-01-01T12:00:00Z"
  }
}
```

### Pagination

```json
{
  "data": [...],
  "pagination": {
    "total": 150,
    "count": 20,
    "per_page": 20,
    "current_page": 1,
    "total_pages": 8,
    "next_page": 2,
    "prev_page": null
  }
}
```

## Authentication Endpoints

### POST /api/v1/auth/login

Authenticate user and receive access token.

**Request:**

```json
{
  "email": "user@example.com",
  "password": "password123",
  "remember_me": false
}
```

**Response (200):**

```json
{
  "data": {
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "token_type": "bearer",
    "expires_in": 900,
    "user": {
      "id": "user_123",
      "email": "user@example.com",
      "name": "John Doe",
      "roles": ["developer"]
    }
  }
}
```

### POST /api/v1/auth/refresh

Refresh access token using refresh token.

**Request:**

```json
{
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Response (200):**

```json
{
  "data": {
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "expires_in": 900
  }
}
```

### POST /api/v1/auth/logout

Logout and invalidate tokens.

**Request Headers:**

```text
Authorization: Bearer <access_token>
```

**Response (204):** No content

## Integration Endpoints

### GET /api/v1/integrations

List all integrations with filtering and pagination.

**Query Parameters:**

- `page` (integer): Page number (default: 1)
- `per_page` (integer): Items per page (default: 20, max: 100)
- `status` (string): Filter by status (`active`, `inactive`, `draft`, `failed`)
- `service_type` (string): Filter by service type (`github`, `slack`, `linear`)
- `search` (string): Search in name and description
- `sort` (string): Sort field (`created_at`, `updated_at`, `name`)
- `order` (string): Sort order (`asc`, `desc`)

**Example Request:**

```bash
curl -X GET "https://api.claude-code-bot.com/api/v1/integrations?status=active&per_page=10&sort=created_at&order=desc" \
  -H "Authorization: Bearer <token>"
```

**Response (200):**

```json
{
  "data": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "name": "github-slack-notifier",
      "description": "Sends Slack notifications for GitHub events",
      "status": "active",
      "service_type": "notification",
      "version": "1.2.0",
      "config": {
        "slack_channel": "#dev-notifications",
        "github_repo": "owner/repo"
      },
      "capabilities": ["webhook.receive", "slack.send"],
      "author": {
        "id": "user_123",
        "name": "John Doe"
      },
      "organization": {
        "id": "org_456",
        "name": "Acme Corp"
      },
      "health": {
        "status": "healthy",
        "last_check": "2025-01-01T11:55:00Z",
        "uptime": 99.9
      },
      "created_at": "2025-01-01T10:00:00Z",
      "updated_at": "2025-01-01T12:00:00Z",
      "deployed_at": "2025-01-01T10:30:00Z"
    }
  ],
  "pagination": {
    "total": 25,
    "count": 10,
    "per_page": 10,
    "current_page": 1,
    "total_pages": 3
  }
}
```

### GET /api/v1/integrations/{id}

Get specific integration details.

**Path Parameters:**

- `id` (string): Integration UUID

**Response (200):**

```json
{
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "github-slack-notifier",
    "description": "Sends Slack notifications for GitHub events",
    "status": "active",
    "service_type": "notification",
    "version": "1.2.0",
    "config": {
      "slack_channel": "#dev-notifications",
      "github_repo": "owner/repo",
      "event_types": ["issues", "pull_requests"]
    },
    "capabilities": ["webhook.receive", "slack.send"],
    "dependencies": [
      {
        "name": "requests",
        "version": "2.28.0",
        "type": "python"
      }
    ],
    "endpoints": {
      "webhook": "https://api.claude-code-bot.com/webhooks/550e8400-e29b-41d4-a716-446655440000",
      "health": "https://api.claude-code-bot.com/integrations/550e8400-e29b-41d4-a716-446655440000/health"
    },
    "metrics": {
      "total_executions": 1250,
      "success_rate": 99.2,
      "avg_response_time": 45,
      "last_execution": "2025-01-01T11:55:00Z"
    },
    "author": {
      "id": "user_123",
      "name": "John Doe",
      "email": "john@example.com"
    },
    "created_at": "2025-01-01T10:00:00Z",
    "updated_at": "2025-01-01T12:00:00Z"
  }
}
```

**Response (404):**

```json
{
  "error": {
    "type": "not_found",
    "message": "Integration not found"
  }
}
```

### POST /api/v1/integrations

Create new integration.

**Request:**

```json
{
  "name": "jira-slack-integration",
  "description": "Sync Jira issues with Slack channels",
  "service_type": "project_management",
  "config": {
    "jira_project": "PROJ",
    "slack_channel": "#project-updates",
    "sync_frequency": "real-time"
  },
  "capabilities": ["jira.read", "slack.send"],
  "template": "jira-slack-template"
}
```

**Response (201):**

```json
{
  "data": {
    "id": "660f9511-f3ac-52e5-b827-557766551111",
    "name": "jira-slack-integration",
    "description": "Sync Jira issues with Slack channels",
    "status": "draft",
    "service_type": "project_management",
    "version": "0.1.0",
    "config": {
      "jira_project": "PROJ",
      "slack_channel": "#project-updates",
      "sync_frequency": "real-time"
    },
    "capabilities": ["jira.read", "slack.send"],
    "author": {
      "id": "user_123",
      "name": "John Doe"
    },
    "workflow": {
      "id": "workflow_789",
      "status": "running",
      "steps": [
        {
          "name": "validate_config",
          "status": "completed"
        },
        {
          "name": "generate_code",
          "status": "running"
        }
      ]
    },
    "created_at": "2025-01-01T12:00:00Z"
  }
}
```

**Validation Errors (400):**

```json
{
  "error": {
    "type": "validation_error",
    "message": "Request validation failed",
    "details": [
      {
        "field": "name",
        "code": "invalid_format",
        "message": "Name must contain only lowercase letters, numbers, and hyphens"
      },
      {
        "field": "config.slack_channel",
        "code": "invalid_value",
        "message": "Slack channel must start with #"
      }
    ]
  }
}
```

### PUT /api/v1/integrations/{id}

Update existing integration.

**Path Parameters:**

- `id` (string): Integration UUID

**Request:**

```json
{
  "description": "Updated description",
  "config": {
    "slack_channel": "#new-channel",
    "jira_project": "NEWPROJ"
  }
}
```

**Response (200):**

```json
{
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "jira-slack-integration",
    "description": "Updated description",
    "status": "active",
    "version": "1.1.0",
    "config": {
      "slack_channel": "#new-channel",
      "jira_project": "NEWPROJ",
      "sync_frequency": "real-time"
    },
    "updated_at": "2025-01-01T12:30:00Z"
  }
}
```

### DELETE /api/v1/integrations/{id}

Delete integration.

**Path Parameters:**

- `id` (string): Integration UUID

**Response (204):** No content

**Response (409):**

```json
{
  "error": {
    "type": "conflict",
    "message": "Cannot delete active integration",
    "details": {
      "suggestion": "Deactivate integration before deletion"
    }
  }
}
```

### POST /api/v1/integrations/{id}/test

Test integration functionality.

**Path Parameters:**

- `id` (string): Integration UUID

**Request:**

```json
{
  "test_type": "health_check",
  "parameters": {
    "timeout": 30
  }
}
```

**Response (200):**

```json
{
  "data": {
    "test_id": "test_123",
    "status": "passed",
    "results": {
      "health_check": {
        "status": "healthy",
        "response_time": 45,
        "dependencies": {
          "slack_api": "healthy",
          "jira_api": "healthy"
        }
      }
    },
    "executed_at": "2025-01-01T12:00:00Z"
  }
}
```

### POST /api/v1/integrations/{id}/deploy

Deploy integration to production.

**Path Parameters:**

- `id` (string): Integration UUID

**Request:**

```json
{
  "environment": "production",
  "auto_rollback": true
}
```

**Response (202):**

```json
{
  "data": {
    "deployment_id": "deploy_456",
    "status": "in_progress",
    "environment": "production",
    "estimated_time": "5 minutes"
  }
}
```

## Workflow Endpoints

### GET /api/v1/workflows

List workflows with filtering.

**Query Parameters:**

- `status` (string): Filter by status (`pending`, `running`, `completed`, `failed`)
- `workflow_type` (string): Filter by type
- `created_by` (string): Filter by creator user ID

**Response (200):**

```json
{
  "data": [
    {
      "id": "workflow_789",
      "workflow_type": "create_integration",
      "status": "running",
      "progress": 60,
      "input_parameters": {
        "integration_name": "new-integration",
        "service_type": "github"
      },
      "current_step": "generate_code",
      "estimated_completion": "2025-01-01T12:10:00Z",
      "created_by": "user_123",
      "created_at": "2025-01-01T12:00:00Z"
    }
  ]
}
```

### GET /api/v1/workflows/{id}

Get workflow details and progress.

**Path Parameters:**

- `id` (string): Workflow UUID

**Response (200):**

```json
{
  "data": {
    "id": "workflow_789",
    "workflow_type": "create_integration", 
    "status": "running",
    "progress": 60,
    "input_parameters": {
      "integration_name": "new-integration",
      "service_type": "github",
      "config": {...}
    },
    "steps": [
      {
        "name": "validate_request",
        "status": "completed",
        "started_at": "2025-01-01T12:00:00Z",
        "completed_at": "2025-01-01T12:00:30Z",
        "duration_ms": 30000,
        "output": {
          "validation_passed": true
        }
      },
      {
        "name": "generate_code",
        "status": "running",
        "started_at": "2025-01-01T12:00:30Z",
        "progress": 70,
        "estimated_completion": "2025-01-01T12:05:00Z"
      },
      {
        "name": "run_tests",
        "status": "pending"
      },
      {
        "name": "create_pr",
        "status": "pending"
      }
    ],
    "result": null,
    "created_by": "user_123",
    "created_at": "2025-01-01T12:00:00Z",
    "started_at": "2025-01-01T12:00:00Z"
  }
}
```

### POST /api/v1/workflows

Start new workflow.

**Request:**

```json
{
  "workflow_type": "update_integration",
  "parameters": {
    "integration_id": "550e8400-e29b-41d4-a716-446655440000",
    "changes": {
      "config": {
        "slack_channel": "#new-channel"
      }
    }
  }
}
```

**Response (202):**

```json
{
  "data": {
    "id": "workflow_890",
    "workflow_type": "update_integration",
    "status": "pending",
    "estimated_start": "2025-01-01T12:01:00Z"
  }
}
```

### POST /api/v1/workflows/{id}/cancel

Cancel running workflow.

**Path Parameters:**

- `id` (string): Workflow UUID

**Response (200):**

```json
{
  "data": {
    "id": "workflow_789",
    "status": "cancelled",
    "cancelled_at": "2025-01-01T12:05:00Z"
  }
}
```

## Webhook Endpoints

### GET /api/v1/webhooks

List configured webhooks.

**Response (200):**

```json
{
  "data": [
    {
      "id": "webhook_123",
      "integration_id": "550e8400-e29b-41d4-a716-446655440000",
      "url": "https://api.claude-code-bot.com/webhooks/webhook_123",
      "events": ["github.issues.opened", "github.pull_request.merged"],
      "secret": "whsec_...",
      "status": "active",
      "created_at": "2025-01-01T10:00:00Z"
    }
  ]
}
```

### POST /webhooks/{id}

Receive webhook from external service.

**Path Parameters:**

- `id` (string): Webhook UUID

**Headers:**

```text
Content-Type: application/json
X-GitHub-Event: issues
X-Hub-Signature-256: sha256=...
X-GitHub-Delivery: 12345678-1234-1234-1234-123456789012
```

**Request:**

```json
{
  "action": "opened",
  "issue": {
    "id": 123,
    "title": "Bug report",
    "body": "Description of the bug",
    "user": {
      "login": "username"
    }
  },
  "repository": {
    "full_name": "owner/repo"
  }
}
```

**Response (200):**

```json
{
  "data": {
    "event_id": "event_456",
    "status": "accepted",
    "processed_at": "2025-01-01T12:00:00Z"
  }
}
```

## User Management Endpoints

### GET /api/v1/users/me

Get current user profile.

**Response (200):**

```json
{
  "data": {
    "id": "user_123",
    "email": "john@example.com",
    "name": "John Doe",
    "avatar_url": "https://example.com/avatar.jpg",
    "roles": ["developer", "admin"],
    "permissions": [
      "integrations.read",
      "integrations.write",
      "workflows.execute"
    ],
    "organization": {
      "id": "org_456",
      "name": "Acme Corp",
      "role": "admin"
    },
    "preferences": {
      "timezone": "UTC",
      "language": "en",
      "notifications": {
        "email": true,
        "slack": false
      }
    },
    "created_at": "2024-01-01T00:00:00Z",
    "last_login": "2025-01-01T11:30:00Z"
  }
}
```

### PUT /api/v1/users/me

Update user profile.

**Request:**

```json
{
  "name": "John Smith",
  "preferences": {
    "timezone": "US/Pacific",
    "notifications": {
      "email": false,
      "slack": true
    }
  }
}
```

**Response (200):**

```json
{
  "data": {
    "id": "user_123",
    "name": "John Smith",
    "preferences": {
      "timezone": "US/Pacific",
      "notifications": {
        "email": false,
        "slack": true
      }
    },
    "updated_at": "2025-01-01T12:00:00Z"
  }
}
```

## Organization Endpoints

### GET /api/v1/organizations/{id}

Get organization details.

**Path Parameters:**

- `id` (string): Organization UUID

**Response (200):**

```json
{
  "data": {
    "id": "org_456",
    "name": "Acme Corp",
    "plan": "enterprise",
    "settings": {
      "require_2fa": true,
      "allowed_domains": ["acme.com"],
      "integration_approval_required": false
    },
    "limits": {
      "integrations": "unlimited",
      "users": 100,
      "api_calls_per_month": 1000000
    },
    "usage": {
      "integrations": 45,
      "users": 12,
      "api_calls_this_month": 250000
    },
    "created_at": "2024-01-01T00:00:00Z"
  }
}
```

### GET /api/v1/organizations/{id}/members

Get organization members.

**Query Parameters:**

- `role` (string): Filter by role (`admin`, `developer`, `viewer`)
- `status` (string): Filter by status (`active`, `inactive`, `invited`)

**Response (200):**

```json
{
  "data": [
    {
      "user_id": "user_123",
      "email": "john@acme.com",
      "name": "John Doe",
      "role": "admin",
      "status": "active",
      "joined_at": "2024-01-01T00:00:00Z",
      "last_active": "2025-01-01T11:30:00Z"
    }
  ]
}
```

## Analytics Endpoints

### GET /api/v1/analytics/integrations

Get integration analytics.

**Query Parameters:**

- `period` (string): Time period (`day`, `week`, `month`, `year`)
- `start_date` (string): Start date (ISO 8601)
- `end_date` (string): End date (ISO 8601)
- `integration_id` (string): Specific integration ID

**Response (200):**

```json
{
  "data": {
    "summary": {
      "total_integrations": 45,
      "active_integrations": 42,
      "total_executions": 125000,
      "success_rate": 99.2,
      "avg_response_time": 150
    },
    "metrics": [
      {
        "date": "2025-01-01",
        "executions": 5000,
        "success_rate": 99.1,
        "avg_response_time": 145,
        "errors": 45
      }
    ],
    "top_integrations": [
      {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "name": "github-slack-notifier",
        "executions": 15000,
        "success_rate": 99.8
      }
    ]
  }
}
```

### GET /api/v1/analytics/performance

Get system performance metrics.

**Response (200):**

```json
{
  "data": {
    "api": {
      "requests_per_minute": 1250,
      "avg_response_time": 95,
      "error_rate": 0.2,
      "uptime": 99.9
    },
    "ai_service": {
      "requests_per_hour": 180,
      "avg_generation_time": 45000,
      "success_rate": 98.5,
      "queue_size": 5
    },
    "database": {
      "active_connections": 25,
      "avg_query_time": 15,
      "slow_queries": 2,
      "cache_hit_rate": 95.2
    }
  }
}
```

## Error Codes

### HTTP Status Codes

- `200` - OK
- `201` - Created
- `202` - Accepted (Async operation started)
- `204` - No Content
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `409` - Conflict
- `422` - Unprocessable Entity
- `429` - Too Many Requests
- `500` - Internal Server Error
- `502` - Bad Gateway
- `503` - Service Unavailable

### Error Types

- `validation_error` - Request validation failed
- `authentication_error` - Authentication failed
- `authorization_error` - Insufficient permissions
- `not_found` - Resource not found
- `conflict` - Resource conflict
- `rate_limit_exceeded` - Rate limit exceeded
- `internal_error` - Internal server error
- `service_unavailable` - External service unavailable

### Common Error Examples

#### Validation Error

```json
{
  "error": {
    "type": "validation_error",
    "message": "Request validation failed",
    "details": [
      {
        "field": "name",
        "code": "required",
        "message": "This field is required"
      }
    ]
  }
}
```

#### Rate Limit Error

```json
{
  "error": {
    "type": "rate_limit_exceeded",
    "message": "Rate limit exceeded",
    "details": {
      "limit": 1000,
      "window": "1 hour",
      "retry_after": 3600
    }
  }
}
```

## SDK Examples

### Python SDK

```python
from claude_code_bot import Client

# Initialize client
client = Client(api_key="your_api_key")

# List integrations
integrations = client.integrations.list(status="active")

# Create integration
integration = client.integrations.create({
    "name": "my-integration",
    "service_type": "github",
    "config": {
        "repo": "owner/repo",
        "webhook_url": "https://example.com/webhook"
    }
})

# Get integration details
details = client.integrations.get("integration_id")

# Test integration
test_result = client.integrations.test("integration_id")
```

### JavaScript SDK

```javascript
import { ClaudeCodeBot } from '@claude-code-bot/sdk';

// Initialize client
const client = new ClaudeCodeBot({
  apiKey: 'your_api_key'
});

// List integrations
const integrations = await client.integrations.list({
  status: 'active'
});

// Create integration
const integration = await client.integrations.create({
  name: 'my-integration',
  serviceType: 'github',
  config: {
    repo: 'owner/repo',
    webhookUrl: 'https://example.com/webhook'
  }
});

// Get workflow status
const workflow = await client.workflows.get('workflow_id');
```

### cURL Examples

#### Create Integration

```bash
curl -X POST https://api.claude-code-bot.com/api/v1/integrations \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "github-slack-integration",
    "service_type": "notification",
    "config": {
      "github_repo": "owner/repo",
      "slack_channel": "#notifications"
    }
  }'
```

#### Get Integration

```bash
curl -X GET https://api.claude-code-bot.com/api/v1/integrations/550e8400-e29b-41d4-a716-446655440000 \
  -H "Authorization: Bearer <token>"
```

#### List Workflows

```bash
curl -X GET "https://api.claude-code-bot.com/api/v1/workflows?status=running" \
  -H "Authorization: Bearer <token>"
```

## Webhooks

### Webhook Security

All webhooks должны быть verified используя signature в header:

```python
import hmac
import hashlib

def verify_webhook(payload, signature, secret):
    expected = hmac.new(
        secret.encode(),
        payload.encode(),
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(f"sha256={expected}", signature)
```

### Webhook Events

- `integration.created`
- `integration.updated`
- `integration.deployed`
- `integration.failed`
- `workflow.started`
- `workflow.completed`
- `workflow.failed`

### Webhook Payload Example

```json
{
  "event": "integration.created",
  "data": {
    "integration": {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "name": "new-integration",
      "status": "draft"
    }
  },
  "timestamp": "2025-01-01T12:00:00Z",
  "delivery_id": "delivery_123"
}
```

## Заключение

Этот API Reference предоставляет comprehensive документацию для всех endpoints Claude Code Bot API. Для дополнительной информации и примеров использования обратитесь к:

- [Техническая спецификация](technical-spec.md)
- [Руководство разработчика](../development/getting-started.md)
- [Примеры интеграций](../user/integration-guide.md)

При возникновении вопросов или проблем создайте issue в [GitHub репозитории](https://github.com/yourusername/claude-code-bot/issues) или обратитесь в support.
