<p align="right">
  <a href="./agents.md">English</a> · <strong>Русский</strong>
</p>

# Инструкция по подключению ИИ-агентов

Здесь собраны готовые примеры конфигураций для подключения **Yet Another YouTrack MCP (`yayt-mcp`)** ко всем популярным ИИ-ассистентам и средам разработки.

---

## 1. OpenCode и Goose CLI

### OpenCode
Добавьте в `opencode.json` (в корне вашего проекта) или в глобальный `~/.config/opencode/mcp.json`:
```json
{
  "mcpServers": {
    "youtrack": {
      "command": "yayt-mcp",
      "env": {
        "YOUTRACK_URL": "https://company.youtrack.cloud",
        "YOUTRACK_TOKEN": "perm:your-token-here"
      }
    }
  }
}
```

### Goose CLI
```bash
goose configure
# Выберите: Add Extension -> Command Line Extension
# Имя: youtrack
# Команда: yayt-mcp
# Переменные: YOUTRACK_URL=https://..., YOUTRACK_TOKEN=perm:...
```

---

## 2. Claude Code и Claude Desktop

### Claude Code CLI
```bash
claude mcp add youtrack \
  -e YOUTRACK_URL=https://company.youtrack.cloud \
  -e YOUTRACK_TOKEN=perm:your-token-here \
  -- yayt-mcp
```

### Claude Desktop
В файле `claude_desktop_config.json` (`%APPDATA%\Claude\` на Windows, `~/Library/Application Support/Claude/` на macOS):
```json
{
  "mcpServers": {
    "youtrack": {
      "command": "yayt-mcp",
      "env": {
        "YOUTRACK_URL": "https://company.youtrack.cloud",
        "YOUTRACK_TOKEN": "perm:your-token-here"
      }
    }
  }
}
```

---

## 3. Cursor и Windsurf

### Cursor
Добавьте в `.cursor/mcp.json` в корне проекта или глобально в `~/.cursor/mcp.json`:
```json
{
  "mcpServers": {
    "youtrack": {
      "command": "yayt-mcp",
      "env": {
        "YOUTRACK_URL": "https://company.youtrack.cloud",
        "YOUTRACK_TOKEN": "perm:your-token-here"
      }
    }
  }
}
```

### Windsurf (Codeium)
В файле `~/.codeium/windsurf/mcp_config.json`:
```json
{
  "mcpServers": {
    "youtrack": {
      "command": "yayt-mcp",
      "env": {
        "YOUTRACK_URL": "https://company.youtrack.cloud",
        "YOUTRACK_TOKEN": "perm:your-token-here"
      }
    }
  }
}
```

---

## 4. Расширения VS Code (Cline и Roo Code)

В `cline_mcp_settings.json` (Настройки расширения → вкладка MCP Servers):
```json
{
  "mcpServers": {
    "youtrack": {
      "command": "yayt-mcp",
      "env": {
        "YOUTRACK_URL": "https://company.youtrack.cloud",
        "YOUTRACK_TOKEN": "perm:your-token-here"
      }
    }
  }
}
```

---

## 5. Google Antigravity (AGY)

В `~/.gemini/antigravity/mcp_config.json`:
```json
{
  "mcpServers": {
    "youtrack": {
      "command": "yayt-mcp",
      "env": {
        "YOUTRACK_URL": "https://company.youtrack.cloud",
        "YOUTRACK_TOKEN": "perm:your-token-here",
        "YOUTRACK_READ_ONLY": "false"
      }
    }
  }
}
```

---

## 6. OpenAI Codex / ChatGPT Desktop и Agents SDK

### ChatGPT Desktop
В меню Settings → Developer Mode → MCP Servers:
```json
{
  "mcpServers": {
    "youtrack": {
      "command": "yayt-mcp",
      "env": {
        "YOUTRACK_URL": "https://company.youtrack.cloud",
        "YOUTRACK_TOKEN": "perm:your-token-here"
      }
    }
  }
}
```

### OpenAI Agents SDK (Python)
```python
from agents import Agent
from agents.mcp import StdioMCPServer

youtrack_mcp = StdioMCPServer(
    command="yayt-mcp",
    env={"YOUTRACK_URL": "https://company.youtrack.cloud", "YOUTRACK_TOKEN": "perm:..."}
)

agent = Agent(name="YouTrack Assistant", mcp_servers=[youtrack_mcp])
```

---

## 7. Hermes Agent и Pi Agent

### Hermes Agent (Nous Research)
В файле `hermes_config.json`:
```json
{
  "mcp_servers": {
    "youtrack": {
      "command": "yayt-mcp",
      "env": {
        "YOUTRACK_URL": "https://company.youtrack.cloud",
        "YOUTRACK_TOKEN": "perm:your-token-here"
      }
    }
  }
}
```

### Pi Agent / Open-Pi
В файле `.pi/config.json`:
```json
{
  "tools": {
    "mcp": {
      "youtrack": {
        "transport": "stdio",
        "command": "yayt-mcp",
        "env": {
          "YOUTRACK_URL": "https://company.youtrack.cloud",
          "YOUTRACK_TOKEN": "perm:your-token-here"
        }
      }
    }
  }
}
```

---

## 8. JetBrains IDE (IntelliJ IDEA, PyCharm, WebStorm)

Перейдите в **Settings** → **Tools** → **AI Assistant** → **Model Context Protocol (MCP)** → **Add** → **As JSON**:
```json
{
  "youtrack": {
    "command": "yayt-mcp",
    "env": {
      "YOUTRACK_URL": "https://company.youtrack.cloud",
      "YOUTRACK_TOKEN": "perm:your-token-here"
    }
  }
}
```

---

## 9. Веб-интерфейсы (LibreChat и Open WebUI)

В `librechat.yaml`:
```yaml
mcpServers:
  youtrack:
    type: stdio
    command: yayt-mcp
    env:
      YOUTRACK_URL: "https://company.youtrack.cloud"
      YOUTRACK_TOKEN": "perm:your-token-here"
```
