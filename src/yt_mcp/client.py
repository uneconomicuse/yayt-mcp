import os
import re
import logging
from typing import Any
import httpx

logger = logging.getLogger("yt_mcp")


def _load_dotenv():
    """Load .env file if present in workspace without extra dependencies."""
    for path in [".env", os.path.join(os.path.dirname(__file__), "..", "..", ".env")]:
        if os.path.isfile(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#") and "=" in line:
                            k, v = line.split("=", 1)
                            k, v = k.strip(), v.strip().strip('"').strip("'")
                            if k not in os.environ:
                                os.environ[k] = v
            except Exception:
                pass


def rewrite_or_clauses(query: str) -> str:
    """Rewrite YouTrack query 'field: X OR field: Y' into valid syntax 'field: X, Y'."""
    pattern = re.compile(r'(\b\w+:)\s*([^(),]+?)\s+OR\s+\1\s*([^(),]+?)(?=[)\s]|$)', re.IGNORECASE)
    curr = query
    while True:
        rewritten = pattern.sub(r'\1 \2, \3', curr)
        if rewritten == curr:
            break
        curr = rewritten
    return curr


class YouTrackClient:
    def __init__(
        self,
        base_url: str | None = None,
        token: str | None = None,
        read_only: bool | None = None,
    ):
        _load_dotenv()
        self.base_url = (base_url or os.environ.get("YOUTRACK_URL", "")).rstrip("/")
        self.token = token or os.environ.get("YOUTRACK_TOKEN", "")
        
        if read_only is None:
            self.read_only = os.environ.get("YOUTRACK_READ_ONLY", "").lower() in ("1", "true", "yes")
        else:
            self.read_only = read_only

        if not self.base_url or not self.token:
            logger.warning("YOUTRACK_URL or YOUTRACK_TOKEN is not set. API calls will fail until configured.")

        self._client: httpx.AsyncClient | None = None

    @property
    def client(self) -> httpx.AsyncClient:
        """Lazy client instantiation to guarantee proper binding to the active async event loop."""
        if self._client is None or self._client.is_closed:
            kwargs: dict[str, Any] = {
                "headers": {
                    "Authorization": f"Bearer {self.token}",
                    "Accept": "application/json",
                },
                "timeout": 30.0,
                "http2": True,
            }
            if self.base_url:
                kwargs["base_url"] = self.base_url

            self._client = httpx.AsyncClient(**kwargs)
        return self._client

    def check_mutation_allowed(self) -> str | None:
        """Return error message if write operations are blocked."""
        if self.read_only:
            return "Error: Server is running in READ-ONLY mode (YOUTRACK_READ_ONLY=true). Modification rejected."
        return None

    async def get(self, path: str, params: dict[str, Any] | None = None) -> Any:
        if params and "query" in params and isinstance(params["query"], str):
            params["query"] = rewrite_or_clauses(params["query"])
            
        resp = await self.client.get(path, params=params)
        return self._handle_response(resp)

    async def post(self, path: str, json_data: Any = None, params: dict[str, Any] | None = None) -> Any:
        mutation_err = self.check_mutation_allowed()
        if mutation_err:
            return {"error": mutation_err}

        resp = await self.client.post(path, json=json_data, params=params)
        return self._handle_response(resp)

    async def delete(self, path: str, params: dict[str, Any] | None = None) -> Any:
        """Physical deletion is permanently forbidden."""
        return {
            "error": "Security: Physical hard-deletion is permanently disabled in this MCP server. Use soft-delete / archiving (archive_issue) instead.",
            "status_code": 403,
        }

    async def execute_command(self, issue_id: str, command: str, comment: str | None = None) -> dict[str, Any]:
        """Apply a YouTrack command to an issue (e.g. 'State Fixed Assignee alex')."""
        mutation_err = self.check_mutation_allowed()
        if mutation_err:
            return {"error": mutation_err}

        payload: dict[str, Any] = {
            "query": command,
            "issues": [{"idReadable": issue_id}],
        }
        if comment:
            payload["comment"] = comment

        resp = await self.client.post("/api/commands", json=payload)
        return self._handle_response(resp)

    def _handle_response(self, resp: httpx.Response) -> Any:
        if resp.is_success:
            if resp.status_code == 204 or not resp.content:
                return {"success": True}
            try:
                return resp.json()
            except Exception:
                return resp.text

        # Error handling
        try:
            data = resp.json()
            error_msg = data.get("error_description") or data.get("error") or str(data)
        except Exception:
            error_msg = resp.text or f"HTTP {resp.status_code}"

        return {
            "error": f"YouTrack API error ({resp.status_code}): {error_msg}",
            "status_code": resp.status_code,
        }

    async def close(self):
        await self._client.aclose()
