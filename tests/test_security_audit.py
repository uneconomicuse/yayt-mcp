import pytest
from unittest.mock import AsyncMock, patch
from yt_mcp.client import YouTrackClient
from yt_mcp import server


@pytest.fixture
def mock_httpx():
    """Mock underlying httpx AsyncClient methods to verify zero unauthorized network calls."""
    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get, \
         patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post, \
         patch("httpx.AsyncClient.delete", new_callable=AsyncMock) as mock_delete:
        yield {"get": mock_get, "post": mock_post, "delete": mock_delete}


# ============================================================================
# 1. Direct Client Flag & Gatekeeper Tests
# ============================================================================

def test_client_read_only_parsing(monkeypatch):
    """Verify robust parsing of read_only flag."""
    for val in ("true", "True", "TRUE", "1", "yes", "YES"):
        monkeypatch.setenv("YOUTRACK_READ_ONLY", val)
        c = YouTrackClient(base_url="https://yt.example.com", token="perm:test")
        assert c.read_only is True, f"Failed for YOUTRACK_READ_ONLY={val}"

    for val in ("false", "False", "0", "no", "", "random"):
        monkeypatch.setenv("YOUTRACK_READ_ONLY", val)
        c = YouTrackClient(base_url="https://yt.example.com", token="perm:test")
        assert c.read_only is False, f"Failed for YOUTRACK_READ_ONLY={val}"


@pytest.mark.asyncio
async def test_client_delete_permanently_blocked(mock_httpx):
    """Verify physical HTTP DELETE is permanently blocked regardless of settings."""
    c = YouTrackClient(base_url="https://yt.example.com", token="perm:test", read_only=False)
    res = await c.delete("/api/issues/TEST-1")
    assert "error" in res
    assert "permanently disabled" in res["error"]
    assert mock_httpx["delete"].call_count == 0


@pytest.mark.asyncio
async def test_client_post_blocked_in_read_only(mock_httpx):
    """Ensure client.post in read-only mode makes 0 HTTP calls and returns error."""
    c = YouTrackClient(base_url="https://yt.example.com", token="perm:test", read_only=True)
    res = await c.post("/api/issues", json_data={"summary": "Test"})
    assert "error" in res
    assert "READ-ONLY" in res["error"]
    assert mock_httpx["post"].call_count == 0


@pytest.mark.asyncio
async def test_client_execute_command_blocked_in_read_only(mock_httpx):
    """Ensure client.execute_command in read-only mode makes 0 HTTP calls."""
    c = YouTrackClient(base_url="https://yt.example.com", token="perm:test", read_only=True)
    res = await c.execute_command("TEST-1", "State Fixed")
    assert "error" in res
    assert "READ-ONLY" in res["error"]
    assert mock_httpx["post"].call_count == 0


# ============================================================================
# 2. Tool-Level Security Tests: Zero Mutations Under READ_ONLY
# ============================================================================

@pytest.mark.asyncio
async def test_all_mutating_tools_blocked_under_read_only(mock_httpx, monkeypatch):
    """Verify that all 14 mutating tools are strictly blocked when read_only=True."""
    monkeypatch.setattr(server.client, "read_only", True)

    # 1. create_article
    res = await server.create_article("PROJ", "Title", "Body")
    assert "error" in res and "READ-ONLY" in res["error"]

    # 2. update_article
    res = await server.update_article("ART-1", summary="New")
    assert "error" in res and "READ-ONLY" in res["error"]

    # 3. delete_article
    res = await server.delete_article("ART-1")
    assert "error" in res and "disabled" in res["error"]

    # 4. add_article_comment
    res = await server.add_article_comment("ART-1", "Comment")
    assert "error" in res and "READ-ONLY" in res["error"]

    # 5. create_issue
    res = await server.create_issue("PROJ", "Title")
    assert "error" in res and "READ-ONLY" in res["error"]

    # 6. create_issue_from_template
    res = await server.create_issue_from_template("PROJ", "bug", "Bug title")
    assert "error" in res and "READ-ONLY" in res["error"]

    # 7. update_issue
    res = await server.update_issue("TEST-1", "State In Progress")
    assert "error" in res and "READ-ONLY" in res["error"]

    # 8. archive_issue
    res = await server.archive_issue("TEST-1")
    assert "error" in res and "READ-ONLY" in res["error"]

    # 9. delete_issue
    res = await server.delete_issue("TEST-1")
    assert "error" in res and "READ-ONLY" in res["error"]

    # 10. link_issues
    res = await server.link_issues("TEST-1", "TEST-2", "relates to")
    assert "error" in res and "READ-ONLY" in res["error"]

    # 11. add_comment
    res = await server.add_comment("TEST-1", "Comment")
    assert "error" in res and "READ-ONLY" in res["error"]

    # 12. update_comment
    res = await server.update_comment("TEST-1", "C-1", "Updated comment")
    assert "error" in res and "READ-ONLY" in res["error"]

    # 13. delete_comment
    res = await server.delete_comment("TEST-1", "C-1")
    assert "error" in res and "disabled" in res["error"]

    # 14. add_work_item
    res = await server.add_work_item("TEST-1", "1h", "Dev work")
    assert "error" in res and "READ-ONLY" in res["error"]

    # Ensure 0 network egress
    assert mock_httpx["post"].call_count == 0
    assert mock_httpx["delete"].call_count == 0


@pytest.mark.asyncio
async def test_delete_issue_always_performs_soft_delete(monkeypatch):
    """Verify that delete_issue strictly performs soft-delete (State Obsolete) and NEVER hard delete."""
    monkeypatch.setattr(server.client, "read_only", False)
    with patch.object(server.client, "execute_command", new_callable=AsyncMock) as mock_cmd:
        mock_cmd.return_value = {"value": "OK"}
        res = await server.delete_issue("TEST-100")
        assert res.get("success") is True
        assert "Soft-Delete" in res.get("message", "")
        mock_cmd.assert_called_once_with("TEST-100", "State Obsolete", comment="Archived: Soft-deleted via delete_issue")
