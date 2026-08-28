<p align="right">
  <a href="./README.md">English</a> · <strong>Русский</strong>
</p>

<p align="center">
  <img src="./assets/hero.svg" width="100%" alt="Yet Another YouTrack MCP (yayt-mcp)">
</p>

<p align="center">
  <a href="https://www.python.org/"><img src="https://img.shields.io/badge/python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python 3.10+"></a>
  <a href="https://modelcontextprotocol.io/"><img src="https://img.shields.io/badge/протокол-MCP%20Standard-6366F1?style=flat-square" alt="MCP Protocol"></a>
  <a href="https://www.jetbrains.com/youtrack/"><img src="https://img.shields.io/badge/youtrack-Cloud%20%2F%20Server-000000?style=flat-square&logo=youtrack&logoColor=white" alt="YouTrack"></a>
  <a href="https://github.com/uneconomicuse/yayt-mcp"><img src="https://img.shields.io/badge/тесты-13%2F13%20пройдено-3FB950?style=flat-square" alt="Tests"></a>
  <a href="https://github.com/uneconomicuse/yayt-mcp/blob/main/LICENSE"><img src="https://img.shields.io/badge/лицензия-MIT-blue?style=flat-square" alt="License: MIT"></a>
</p>

---

## Описание

**`yayt-mcp`** (**Yet Another YouTrack MCP**) — это production-ready, экономный по токенам сервер **[Model Context Protocol (MCP)](https://modelcontextprotocol.io/)**, подключающий ИИ-ассистентов к **JetBrains YouTrack**.

Сервер разработан на Python 3.10+ с использованием FastMCP и асинхронного клиента HTTP/2 (`httpx`). Он предоставляет 27 специализированных инструментов для поиска по статьям, управления задачами, пакетного применения команд, учета времени и мониторинга изменений проекта.

---

<p align="center">
  <img src="./assets/architecture.svg" width="100%" alt="Архитектура и поток данных yayt-mcp">
</p>

---

## Установка

Установите пакет через стандартный `pip`:

```bash
pip install git+https://github.com/uneconomicuse/yayt-mcp.git
```

После установки серверная команда **`yayt-mcp`** становится доступна глобально в системе.

---

## Настройка и подключение

### Способ А: На уровне проекта (Рекомендуется для команд)
Создайте файл `.mcp.json` в корне репозитория вашего проекта и отправьте его в Git:

```json
{
  "mcpServers": {
    "youtrack": {
      "command": "yayt-mcp",
      "env": {
        "YOUTRACK_URL": "https://company.youtrack.cloud",
        "YOUTRACK_TOKEN": "${YOUTRACK_TOKEN}"
      }
    }
  }
}
```
*Любой разработчик, открывающий этот репозиторий в Cursor, OpenCode, VS Code или Windsurf, сразу получит доступ к YouTrack без ручных настроек.*

### Способ Б: Глобальная настройка в вашем ИИ-агенте
Добавьте блок `youtrack` в глобальный конфиг вашего агента (например, `~/.config/opencode/mcp.json`, `~/.cursor/mcp.json` или Claude Desktop):

```json
{
  "mcpServers": {
    "youtrack": {
      "command": "yayt-mcp",
      "env": {
        "YOUTRACK_URL": "https://company.youtrack.cloud",
        "YOUTRACK_TOKEN": "perm:ваш_постоянный_токен"
      }
    }
  }
}
```

👉 **Нужны готовые конфиги для конкретных приложений (Claude Code, Cursor, JetBrains, OpenCode, Hermes, Pi)?**  
Смотрите полное **[Руководство по подключению агентов](docs/agents.ru.md)**.

---

## Ключевые возможности

* **База знаний и статьи:** Полные CRUD-операции со статьями YouTrack, иерархическая навигация по дереву документации (`list_child_articles`), чтение Markdown, вложения и комментарии.
* **Задачи и движок команд:** Полнотекстовый и структурированный поиск по YouTrack QL с автоматической нормализацией `OR`-запросов, связывание задач (`subtask of`, `relates to`, `depends on`, `duplicates`) и мгновенное применение команд изменения статусов и исполнителей (`POST /api/commands`).
* **Гарантия безопасности (Zero Hard-Delete):** Физическое удаление (`HTTP DELETE`) полностью вырезано из ядра сервера. Любой вызов удаления выполняет безопасную архивацию (**Soft-Delete**: `State Obsolete`), сохраняя полную историю изменений, связи и файлы.
* **Кросс-LLM шаблонизатор:** Встроенные унифицированные шаблоны (`bug`, `feature`, `task`, `incident`, `spike`, `daily`, `release`) обеспечивают одинаковую структуру задач независимо от того, какая модель их генерирует (Claude, GPT, DeepSeek, Gemini).
* **Мониторинг изменений:** Инструмент `poll_changes` возвращает список недавно обновленных задач за $N$ минут для дейли-синхронизаций и выявления блокеров с минимальным расходом токенов.
* **Учет времени и Agile:** Списание трудозатрат (`1h 30m`), просмотр Agile/Kanban досок, группировка задач по колонкам спринта и поиск логинов сотрудников.

---

## Переменные окружения

| Переменная | Обязательна | По умолчанию | Пример | Описание |
|---|---|---|---|---|
| `YOUTRACK_URL` | **Да** | — | `https://company.youtrack.cloud` | Базовый URL вашего инстанса YouTrack. |
| `YOUTRACK_TOKEN` | **Да** | — | `perm-cmFma...` | Постоянный токен авторизации (Permanent Token). |
| `YOUTRACK_READ_ONLY` | Нет | `false` | `false` / `true` | При `true` полностью блокирует создание, изменение и архивацию данных. |

*(См. [`.env.example`](.env.example) для готового шаблона).*

---

## Справочник инструментов (27 Tools)

<details>
<summary><strong>Развернуть полный список инструментов</strong></summary>

### База знаний (Articles)
* `search_articles(query, project, limit)` — Полнотекстовый поиск статей.
* `get_article(article_id)` — Получение Markdown, метаданных, файлов и комментариев.
* `create_article(project_id, summary, content, parent_article_id)` — Создание статьи или подстатьи.
* `update_article(article_id, summary, content)` — Обновление заголовка и содержимого.
* `delete_article(article_id)` — Отключено для безопасности.
* `list_child_articles(article_id)` — Навигация по подстатьям.
* `add_article_comment(article_id, text)` — Комментирование статьи.

### Задачи и Мониторинг
* `search_issues(query, limit)` — Поиск задач с автоисправлением `OR`.
* `get_issue(issue_id)` — Полная карточка задачи с полями, связями и историей.
* `create_issue(project_id, summary, description)` — Создание свободной задачи.
* `create_issue_from_template(project_id, template, summary, section_data)` — Создание шаблонной задачи (`bug`, `feature`, `task`, `incident` и др.).
* `list_templates()` — Просмотр доступных шаблонов.
* `update_issue(issue_id, command, comment)` — Выполнение команд (например: `State Fixed Assignee alex Priority Critical`).
* `archive_issue(issue_id, reason)` — Мягкое удаление/архивация (`State Obsolete`).
* `delete_issue(issue_id)` — Безопасное удаление (всегда Soft-Delete: `State Obsolete`).
* `link_issues(source_id, target_id, link_type)` — Связывание задач (`subtask of`, `relates to`, `depends on`, `duplicates`).
* `get_issue_history(issue_id, limit)` — Журнал аудита и активности задачи.
* `poll_changes(query, since_minutes)` — Мониторинг изменений за последние $N$ минут.

### Комментарии
* `add_comment(issue_id, text)` — Добавить комментарий к задаче.
* `update_comment(issue_id, comment_id, text)` — Отредактировать комментарий.
* `delete_comment(issue_id, comment_id)` — Отключено для безопасности.

### Учет времени
* `get_work_items(issue_id)` — Просмотр списанного времени.
* `add_work_item(issue_id, duration, description, work_type, date)` — Списание времени (`1h 30m`).

### Agile, Проекты и Пользователи
* `get_agile_boards()` — Список Agile/Kanban досок.
* `get_sprint_board(board_id, sprint_id)` — Задачи спринта по колонкам.
* `find_users(query, limit)` — Поиск логинов сотрудников.
* `list_projects(limit)` — Список проектов.
* `get_current_user()` — Проверка соединения и профиль.

</details>

---

## Тестирование

```bash
python -m pytest tests -v
```

---

## Лицензия
Распространяется под лицензией [MIT](LICENSE).
