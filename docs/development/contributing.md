# 🤝 Contributing Guide

## Добро пожаловать в Claude Code Bot

Мы рады, что вы заинтересованы в участии в разработке Claude Code Bot. Этот документ поможет вам понять процесс внесения изменений и стандарты качества проекта.

## Кодекс поведения

Мы придерживаемся [Contributor Covenant Code of Conduct](CODE_OF_CONDUCT.md). Участвуя в этом проекте, вы соглашаетесь соблюдать его условия.

## Способы участия

### 🐛 Сообщения об ошибках

**Перед созданием issue:**

1. Проверьте [существующие issues](../../issues)
2. Убедитесь, что используете последнюю версию
3. Попробуйте воспроизвести проблему

**При создании bug report включите:**

- Подробное описание проблемы
- Шаги для воспроизведения
- Ожидаемое и фактическое поведение
- Информацию о среде (OS, Python версия, etc.)
- Логи ошибок (если есть)
- Screenshots (если применимо)

**Шаблон bug report:**

```markdown
## Описание проблемы
[Краткое описание]

## Шаги для воспроизведения
1. Перейти к '...'
2. Нажать на '...'
3. Увидеть ошибку

## Ожидаемое поведение
[Что должно было произойти]

## Фактическое поведение
[Что произошло на самом деле]

## Среда выполнения
- OS: [e.g. Ubuntu 22.04]
- Python: [e.g. 3.12]
- Claude Code Bot версия: [e.g. 1.0.0]

## Дополнительная информация
[Логи, screenshots, etc.]
```

### 💡 Предложения функций

**При предложении новой функции:**

1. Проверьте [roadmap проекта](../../projects)
2. Обсудите идею в [Discussions](../../discussions)
3. Создайте feature request с подробным описанием

**Шаблон feature request:**

```markdown
## Проблема, которую решает функция
[Описание проблемы или потребности]

## Предлагаемое решение
[Детальное описание функции]

## Альтернативы
[Другие возможные решения]

## Дополнительная информация
[Mockups, примеры использования, etc.]
```

### 🔧 Разработка интеграций

**Создание новой интеграции:**

1. Создайте issue с лейблом `integration-request`
2. Используйте [шаблон интеграции](../../.github/ISSUE_TEMPLATE/integration-request.md)
3. Дождитесь автоматической генерации кода
4. Участвуйте в code review процессе

**Улучшение существующей интеграции:**

1. Изучите существующий код интеграции
2. Создайте issue или сразу pull request
3. Следуйте [стандартам кодирования](#стандарты-кодирования)

## Процесс разработки

### 🚀 Quick Start для разработчиков

```bash
# 1. Fork и clone репозитория
git clone https://github.com/YOUR-USERNAME/claude-code-bot.git
cd claude-code-bot

# 2. Настройка окружения
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# или .venv\Scripts\activate  # Windows

# 3. Установка зависимостей для разработки
uv pip install -e ".[dev]"

# 4. Настройка pre-commit hooks
pre-commit install

# 5. Запуск тестов для проверки настройки
pytest

# 6. Запуск в режиме разработки
make dev
```

### 🌿 Git Workflow

**Branching Strategy:**

- `main` — стабильная ветка для production
- `develop` — интеграционная ветка для новых функций
- `feature/*` — ветки для новых функций
- `bugfix/*` — ветки для исправления ошибок
- `hotfix/*` — критические исправления для production

**Создание feature branch:**

```bash
# Создать ветку от develop
git checkout develop
git pull origin develop
git checkout -b feature/integration-slack-notifications

# Или для bugfix
git checkout -b bugfix/fix-webhook-validation
```

**Commit Guidelines:**
Мы используем [Conventional Commits](https://www.conventionalcommits.org/):

```text
type(scope): description

[optional body]

[optional footer]
```

**Типы commits:**

- `feat:` — новая функция
- `fix:` — исправление ошибки
- `docs:` — изменения в документации
- `style:` — форматирование, без изменения логики
- `refactor:` — рефакторинг кода
- `test:` — добавление или изменение тестов
- `chore:` — изменения в build процессе или вспомогательных инструментах

**Примеры commits:**

```bash
feat(integrations): add Slack notification support

Add comprehensive Slack integration with support for:
- Channel notifications
- Direct messages
- Custom message formatting
- Error handling and retries

Closes #123

fix(api): handle missing webhook signatures

- Add validation for webhook signature presence
- Return 400 instead of 500 for missing signatures
- Add comprehensive error logging

test(integration): add end-to-end tests for GitHub webhook handling

chore(deps): update dependencies to latest versions
```

### 📝 Pull Request Process

**Создание Pull Request:**

1. Убедитесь, что ваша ветка обновлена с develop
2. Запустите все тесты и линтеры
3. Создайте PR с подробным описанием
4. Заполните все секции PR template
5. Связать PR с соответствующими issues

**PR Template:**

```markdown
## Описание изменений
[Краткое описание что изменилось и почему]

## Тип изменений
- [ ] Bug fix (не ломающие изменения)
- [ ] New feature (не ломающие изменения)
- [ ] Breaking change (изменения, которые ломают существующую функциональность)
- [ ] Documentation update

## Как протестировано
- [ ] Существующие тесты проходят
- [ ] Добавлены новые тесты
- [ ] Тестировано вручную

## Checklist
- [ ] Код соответствует стандартам проекта
- [ ] Self-review проведен
- [ ] Комментарии добавлены для сложных участков
- [ ] Документация обновлена
- [ ] Изменения не генерируют warnings
- [ ] Тесты покрывают новый функционал
- [ ] Локальные тесты проходят

## Screenshots (если применимо)
[Добавить screenshots для UI изменений]

## Связанные Issues
Fixes #(issue number)
```

**Review Process:**

1. Автоматические проверки должны пройти
2. AI review будет создан автоматически  
3. Human reviewer будет назначен
4. Исправить все замечания
5. Получить approval от maintainer
6. Merge будет выполнен автоматически

### 🧪 Тестирование

**Требования к тестированию:**

- Unit tests для всего нового кода
- Integration tests для API endpoints
- End-to-end tests для критических workflows
- Покрытие кода должно быть >= 80%

**Запуск тестов:**

```bash
# Все тесты
pytest

# Только unit tests
pytest tests/unit/

# С покрытием кода
pytest --cov=app --cov-report=html

# Конкретный тест файл
pytest tests/test_integrations.py -v

# Тесты с определенным marker
pytest -m integration
```

**Типы тестов:**

**Unit Tests:**

```python
# tests/unit/test_integration_service.py
import pytest
from app.services.integration_service import IntegrationService

class TestIntegrationService:
    def test_create_integration_success(self):
        service = IntegrationService()
        integration = service.create_integration({
            "name": "test-integration",
            "type": "webhook",
            "config": {"url": "https://example.com"}
        })
        
        assert integration.name == "test-integration"
        assert integration.status == "REQUESTED"

    def test_create_integration_invalid_config(self):
        service = IntegrationService()
        with pytest.raises(ValidationError):
            service.create_integration({
                "name": "test-integration",
                "type": "webhook",
                "config": {}  # Missing required url
            })
```

**Integration Tests:**

```python
# tests/integration/test_api.py
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

class TestIntegrationsAPI:
    def test_create_integration_endpoint(self):
        response = client.post("/api/v1/integrations", json={
            "name": "test-integration",
            "type": "webhook",
            "config": {"url": "https://example.com"}
        })
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "test-integration"
        assert "id" in data

    def test_list_integrations(self):
        # Create test integration first
        client.post("/api/v1/integrations", json={
            "name": "test-integration",
            "type": "webhook",
            "config": {"url": "https://example.com"}
        })
        
        response = client.get("/api/v1/integrations")
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) > 0
```

**E2E Tests:**

```python
# tests/e2e/test_integration_workflow.py
import pytest
from tests.helpers import create_github_issue, wait_for_pr_creation

@pytest.mark.e2e
class TestIntegrationWorkflow:
    def test_full_integration_creation_workflow(self):
        # Create GitHub issue
        issue = create_github_issue(
            title="Add Jira integration",
            body="Integration request template filled",
            labels=["integration-request"]
        )
        
        # Wait for automatic processing
        pr = wait_for_pr_creation(timeout=300)
        
        assert pr is not None
        assert "jira" in pr.title.lower()
        assert pr.files_changed > 0
```

## Стандарты кодирования

### 🐍 Python Code Style

**Инструменты:**

- **Formatter:** `ruff format` (замена Black)
- **Linter:** `ruff check` (замена flake8/isort/pylint)
- **Type checker:** `mypy`
- **Security:** `bandit`

**Конфигурация в pyproject.toml:**

```toml
[tool.ruff]
line-length = 88
target-version = "py312"

[tool.ruff.lint]
select = ["E", "W", "F", "I", "B", "C4", "SIM", "UP", "RUF"]
ignore = ["E501"]  # Line length handled by formatter

[tool.mypy]
python_version = "3.12"
strict = true
warn_return_any = true
warn_unused_configs = true

[tool.pytest.ini_options]
minversion = "6.0"
testpaths = ["tests"]
python_files = ["test_*.py", "*_test.py"]
python_functions = ["test_*"]
markers = [
    "unit: Unit tests",
    "integration: Integration tests", 
    "e2e: End-to-end tests"
]
```

**Автоматическая проверка:**

```bash
# Форматирование кода
ruff format .

# Проверка стиля
ruff check . --fix

# Type checking
mypy app/

# Security check
bandit -r app/

# Все проверки одной командой
make lint
```

### 📁 Структура проекта

**Рекомендуемая организация кода:**

```text
app/
├── __init__.py
├── main.py                     # FastAPI application entry point
├── config.py                   # Configuration management
├── database.py                 # Database connection and session
├── dependencies.py             # FastAPI dependencies
├── exceptions.py               # Custom exceptions
├── api/                        # API routes
│   ├── __init__.py
│   ├── v1/                     # API version 1
│   │   ├── __init__.py
│   │   ├── endpoints/
│   │   │   ├── integrations.py
│   │   │   ├── webhooks.py
│   │   │   └── health.py
│   │   └── dependencies.py
│   └── middleware.py
├── core/                       # Core business logic
│   ├── __init__.py
│   ├── security.py
│   ├── config.py
│   └── events.py
├── services/                   # Business services
│   ├── __init__.py
│   ├── integration_service.py
│   ├── ai_service.py
│   ├── github_service.py
│   └── notification_service.py
├── models/                     # SQLAlchemy models
│   ├── __init__.py
│   ├── integration.py
│   ├── user.py
│   └── webhook.py
├── schemas/                    # Pydantic schemas
│   ├── __init__.py
│   ├── integration.py
│   ├── webhook.py
│   └── common.py
├── integrations/               # Integration implementations
│   ├── __init__.py
│   ├── base/
│   │   ├── __init__.py
│   │   ├── integration.py      # Base integration class
│   │   └── webhook.py          # Base webhook handler
│   ├── github/
│   │   ├── __init__.py
│   │   ├── integration.py
│   │   ├── webhooks.py
│   │   └── schemas.py
│   └── slack/
│       ├── __init__.py
│       ├── integration.py
│       ├── client.py
│       └── schemas.py
├── utils/                      # Utility functions
│   ├── __init__.py
│   ├── logging.py
│   ├── decorators.py
│   └── helpers.py
└── workers/                    # Background workers
    ├── __init__.py
    ├── integration_worker.py
    └── notification_worker.py
```

### 🏗️ Архитектурные принципы

**1. Dependency Injection:**

```python
# Правильно - используйте FastAPI dependency injection
from fastapi import Depends

def get_integration_service() -> IntegrationService:
    return IntegrationService()

@router.post("/integrations")
async def create_integration(
    data: IntegrationCreateSchema,
    service: IntegrationService = Depends(get_integration_service)
):
    return await service.create(data)
```

**2. Error Handling:**

```python
# Кастомные исключения
class IntegrationError(Exception):
    """Base exception for integration operations"""
    pass

class IntegrationNotFoundError(IntegrationError):
    """Raised when integration is not found"""
    pass

# Exception handlers
@app.exception_handler(IntegrationNotFoundError)
async def integration_not_found_handler(request: Request, exc: IntegrationNotFoundError):
    return JSONResponse(
        status_code=404,
        content={"error": "Integration not found", "detail": str(exc)}
    )
```

**3. Configuration Management:**

```python
# settings.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "Claude Code Bot"
    debug: bool = False
    database_url: str
    claude_api_key: str
    github_token: str
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
```

**4. Logging:**

```python
import structlog

logger = structlog.get_logger(__name__)

async def create_integration(data: IntegrationCreateSchema):
    logger.info("Creating integration", name=data.name, type=data.type)
    
    try:
        integration = await integration_service.create(data)
        logger.info("Integration created successfully", 
                   integration_id=integration.id)
        return integration
    except Exception as e:
        logger.error("Failed to create integration", 
                    error=str(e), name=data.name)
        raise
```

### 📚 Документация кода

**Docstring Style:**
Используйте Google style docstrings:

```python
def create_integration(data: IntegrationCreateSchema) -> Integration:
    """Create a new integration.
    
    Args:
        data: Integration creation data including name, type, and configuration
        
    Returns:
        Created integration instance with assigned ID and status
        
    Raises:
        ValidationError: If integration data is invalid
        IntegrationExistsError: If integration with same name exists
        
    Example:
        >>> data = IntegrationCreateSchema(name="slack", type="webhook")
        >>> integration = create_integration(data)
        >>> integration.id
        'uuid-string'
    """
    pass
```

**Type Hints:**
Все публичные функции должны иметь type hints:

```python
from typing import List, Optional, Dict, Any
from uuid import UUID

async def get_integration_by_id(
    integration_id: UUID,
    include_config: bool = False
) -> Optional[Integration]:
    """Get integration by ID with optional config."""
    pass

async def list_integrations(
    limit: int = 10,
    offset: int = 0,
    filters: Optional[Dict[str, Any]] = None
) -> List[Integration]:
    """List integrations with pagination and filtering."""
    pass
```

## Интеграции

### 🔌 Создание новой интеграции

**1. Определение структуры:**

```python
# integrations/your_service/integration.py
from typing import Dict, Any
from ..base import BaseIntegration

class YourServiceIntegration(BaseIntegration):
    """Integration with Your Service."""
    
    service_name = "your_service"
    required_config_keys = ["api_key", "base_url"]
    
    async def validate_config(self, config: Dict[str, Any]) -> bool:
        """Validate integration configuration."""
        # Implementation here
        pass
    
    async def test_connection(self) -> bool:
        """Test connection to Your Service."""
        # Implementation here
        pass
    
    async def handle_webhook(self, payload: Dict[str, Any]) -> None:
        """Handle incoming webhook from Your Service."""
        # Implementation here
        pass
```

**2. Схемы данных:**

```python
# integrations/your_service/schemas.py
from pydantic import BaseModel, Field

class YourServiceConfig(BaseModel):
    """Configuration schema for Your Service integration."""
    
    api_key: str = Field(..., description="API key for authentication")
    base_url: str = Field(..., description="Base URL for API endpoints")
    timeout: int = Field(30, description="Request timeout in seconds")

class YourServiceWebhook(BaseModel):
    """Webhook payload schema for Your Service."""
    
    event_type: str
    timestamp: datetime
    data: Dict[str, Any]
```

**3. Тестирование:**

```python
# tests/integration/test_your_service.py
import pytest
from integrations.your_service import YourServiceIntegration

class TestYourServiceIntegration:
    def test_validate_config_valid(self):
        integration = YourServiceIntegration()
        config = {
            "api_key": "test-key",
            "base_url": "https://api.yourservice.com"
        }
        
        result = await integration.validate_config(config)
        assert result is True
        
    def test_validate_config_missing_key(self):
        integration = YourServiceIntegration()
        config = {"base_url": "https://api.yourservice.com"}
        
        result = await integration.validate_config(config)
        assert result is False
```

### 📝 Документация интеграции

Каждая интеграция должна иметь:

**1. README.md файл:**

```markdown
# Your Service Integration

## Описание
Интеграция с Your Service для автоматизации ...

## Настройка
1. Получите API ключ в Your Service
2. Настройте webhook URL: `https://your-domain/webhooks/your_service`
3. Создайте интеграцию через API или UI

## Конфигурация
- `api_key` - API ключ (обязательно)
- `base_url` - Базовый URL API (обязательно)
- `timeout` - Таймаут запросов в секундах (по умолчанию: 30)

## События
- `issue.created` - Создана новая задача
- `issue.updated` - Обновлена задача
- `project.created` - Создан проект

## Примеры использования
[Примеры кода и сценариев использования]
```

**2. API Documentation:**
Документируйте все endpoints в OpenAPI schema

## Релизный процесс

### 🏷️ Версионирование

Мы используем [Semantic Versioning](https://semver.org/):

- **MAJOR** версия для breaking changes
- **MINOR** версия для новых функций
- **PATCH** версия для bug fixes

**Создание релиза:**

```bash
# Создать release branch
git checkout -b release/1.2.0

# Обновить версию в pyproject.toml
# Обновить CHANGELOG.md

# Создать tag
git tag v1.2.0

# Push tag
git push origin v1.2.0
```

### 📋 Changelog

Поддерживайте актуальный CHANGELOG.md:

```markdown
# Changelog

## [1.2.0] - 2024-03-15

### Added
- New Slack integration with channel support
- Bulk operations API for integrations
- Integration health monitoring

### Changed
- Improved error handling in webhook processing
- Updated dependencies to latest versions

### Fixed
- Fixed race condition in concurrent webhook processing
- Resolved memory leak in long-running workers

### Security
- Updated JWT token validation
- Enhanced webhook signature verification

## [1.1.0] - 2024-02-28
...
```

## Поддержка и сообщество

### 📞 Получение помощи

- **GitHub Issues** — для bug reports и feature requests
- **GitHub Discussions** — для вопросов и обсуждений
- **Documentation** — comprehensive docs в `/docs`
- **Code Examples** — примеры в `/examples`

### 👥 Сообщество

- Respectful и inclusive environment
- Конструктивная обратная связь
- Помощь новичкам
- Sharing knowledge и best practices

### 🎯 Roadmap

Ознакомьтесь с [project roadmap](../../projects) чтобы увидеть планируемые функции и направления развития.

## Полезные команды

### 🛠️ Development Commands

```bash
# Настройка среды разработки
make setup

# Запуск в режиме разработки
make dev

# Форматирование кода
make format

# Проверка качества кода
make lint

# Запуск тестов
make test

# Запуск тестов с покрытием
make test-cov

# Сборка документации
make docs

# Очистка временных файлов
make clean

# Полная проверка перед commit
make check
```

### 📦 Build Commands

```bash
# Сборка Docker образа
make docker-build

# Запуск через Docker Compose
make docker-up

# Остановка контейнеров
make docker-down

# Просмотр логов
make docker-logs
```

## Checklist для Contributors

### ✅ Перед началом работы

- [ ] Прочитал Contributing Guide полностью
- [ ] Настроил development environment
- [ ] Запустил тесты успешно
- [ ] Изучил архитектуру проекта
- [ ] Выбрал issue для работы или создал новый

### ✅ Во время разработки

- [ ] Следую coding standards
- [ ] Пишу тесты для нового кода
- [ ] Обновляю документацию при необходимости
- [ ] Использую meaningful commit messages
- [ ] Тестирую изменения локально

### ✅ Перед созданием PR

- [ ] Все тесты проходят
- [ ] Code coverage поддерживается
- [ ] Линтеры не выдают ошибок
- [ ] Документация обновлена
- [ ] CHANGELOG.md обновлен (для значительных изменений)
- [ ] Self-review проведен

### ✅ После создания PR

- [ ] Заполнил PR template полностью
- [ ] Связал с соответствующими issues
- [ ] Отвечаю на комментарии reviewers
- [ ] Исправляю найденные проблемы
- [ ] Обновляю PR при изменениях

## Заключение

Спасибо за интерес к Claude Code Bot! Ваш вклад помогает создавать лучшую платформу для автоматизации интеграций с помощью ИИ.

Помните:

- **Quality over quantity** — лучше один хорошо продуманный PR чем много поспешных
- **Communication is key** — не стесняйтесь задавать вопросы
- **Learn and grow** — каждый contribution — это возможность узнать что-то новое

Happy coding! 🚀

---

**Есть вопросы?** Создайте [Discussion](../../discussions) или напишите в [Issues](../../issues).

**Нужна помощь с настройкой?** Посмотрите [Development Guide](development.md).

**Хотите предложить улучшение этого гайда?** Создайте PR с изменениями!
