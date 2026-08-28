<p align="right">
  <strong>English</strong> · <a href="./agents.ru.md">Русский</a>
</p>

# AI Agent & Client Setup Guide

This guide provides ready-to-use configurations for connecting **Yet Another YouTrack MCP (`yayt-mcp`)** to various AI coding assistants and IDEs.

---

## 1. OpenCode & Goose CLI

### OpenCode
Add to `opencode.json` (in your project root) or global `~/.config/opencode/mcp.json`:
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
# Select: Add Extension -> Command Line Extension
# Name: youtrack
# Command: yayt-mcp
# Env: YOUTRACK_URL=https://..., YOUTRACK_TOKEN=perm:...
```

---

## 2. Claude Code & Claude Desktop

### Claude Code CLI
```bash
claude mcp add youtrack \
  -e YOUTRACK_URL=https://company.youtrack.cloud \
  -e YOUTRACK_TOKEN=perm:your-token-here \
  -- yayt-mcp
```

### Claude Desktop
In `claude_desktop_config.json` (`%APPDATA%\Claude\` on Windows, `~/Library/Application Support/Claude/` on macOS):
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

## 3. Cursor & Windsurf

### Cursor
Add to `.cursor/mcp.json` in your project root or global `~/.cursor/mcp.json`:
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
In `~/.codeium/windsurf/mcp_config.json`:
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

## 4. VS Code Extensions (Cline & Roo Code)

In `cline_mcp_settings.json` (Extension Settings → MCP Servers):
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

In `~/.gemini/antigravity/mcp_config.json`:
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

## 6. OpenAI Codex / ChatGPT Desktop & Agents SDK

### ChatGPT Desktop
In Settings → Developer Mode → MCP Servers:
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

## 7. Hermes Agent & Pi Agent

### Hermes Agent (Nous Research)
In `hermes_config.json`:
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
In `.pi/config.json`:
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

## 8. JetBrains IDEs (IntelliJ IDEA, PyCharm, WebStorm)

Go to **Settings** → **Tools** → **AI Assistant** → **Model Context Protocol (MCP)** → **Add** → **As JSON**:
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

## 9. Self-Hosted Web UIs (LibreChat & Open WebUI)

In `librechat.yaml`:
```yaml
mcpServers:
  youtrack:
    type: stdio
    command: yayt-mcp
    env:
      YOUTRACK_URL: "https://company.youtrack.cloud"
      YOUTRACK_TOKEN: "perm:your-token-here"
```
