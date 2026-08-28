import pytest
from unittest.mock import AsyncMock, patch
from yt_mcp.client import rewrite_or_clauses, YouTrackClient
from yt_mcp.templates import build_template_description, list_templates_summary
from yt_mcp.server import mcp, create_issue_from_template, delete_issue


def test_rewrite_or_clauses():
    # Simple replacement
    query = "summary: Foo OR summary: Bar"
    assert rewrite_or_clauses(query) == "summary: Foo, Bar"

    # Multi-term replacement
    query = "tag: Bug OR tag: Feature"
    assert rewrite_or_clauses(query) == "tag: Bug, Feature"

    # Complex query
    query = "#Unresolved AND (summary: A OR summary: B)"
    assert rewrite_or_clauses(query) == "#Unresolved AND (summary: A, B)"


def test_template_rendering():
    # Bug template
    desc = build_template_description(
        "bug",
        {
            "summary": "Login page fails",
            "steps_to_reproduce": "1. Go to /login\n2. Click Submit",
            "expected_result": "Logged in",
            "actual_result": "500 Internal Server Error",
        },
    )
    assert "## Summary\nLogin page fails" in desc
    assert "## Steps to Reproduce\n1. Go to /login\n2. Click Submit" in desc
    assert "## Expected Result\nLogged in" in desc
    assert "## Actual Result\n500 Internal Server Error" in desc
    assert "## Environment" in desc  # Default section should still exist!


def test_list_templates_summary():
    summary = list_templates_summary()
    assert "bug" in summary
    assert "feature" in summary
    assert "task" in summary
    assert "incident" in summary


@pytest.mark.asyncio
async def test_safe_mode_soft_delete():
    client = YouTrackClient(
        base_url="https://example.youtrack.cloud",
        token="perm:dummy",
    )
    # Check that client.delete permanently blocks hard deletion
    res = await client.delete("/api/issues/TEST-1")
    assert "error" in res
    assert "permanently disabled" in res["error"]


@pytest.mark.asyncio
async def test_read_only_mode():
    client = YouTrackClient(
        base_url="https://example.youtrack.cloud",
        token="perm:dummy",
        read_only=True,
    )
    err = client.check_mutation_allowed()
    assert err is not None
    assert "READ-ONLY" in err


def test_tools_registered():
    # FastMCP should have all our tools registered
    tool_names = [tool.name for tool in mcp._tool_manager.list_tools()]
    assert "search_articles" in tool_names
    assert "get_article" in tool_names
    assert "create_article" in tool_names
    assert "update_article" in tool_names
    assert "list_child_articles" in tool_names
    assert "add_article_comment" in tool_names
    assert "search_issues" in tool_names
    assert "get_issue" in tool_names
    assert "create_issue" in tool_names
    assert "create_issue_from_template" in tool_names
    assert "list_templates" in tool_names
    assert "update_issue" in tool_names
    assert "archive_issue" in tool_names
    assert "delete_issue" in tool_names
    assert "link_issues" in tool_names
    assert "get_issue_history" in tool_names
    assert "poll_changes" in tool_names
    assert "add_comment" in tool_names
    assert "get_work_items" in tool_names
    assert "add_work_item" in tool_names
    assert "get_agile_boards" in tool_names
    assert "get_sprint_board" in tool_names
    assert "find_users" in tool_names
    assert "list_projects" in tool_names
    assert "get_current_user" in tool_names
    assert len(tool_names) >= 27


@pytest.mark.asyncio
async def test_tool_mocks_articles_and_issues():
    from yt_mcp.server import (
        client,
        search_articles,
        create_article,
        get_article,
        search_issues,
        create_issue,
        update_issue,
        archive_issue,
        poll_changes,
        add_work_item,
        link_issues,
    )

    with patch.object(client, "get", new_callable=AsyncMock) as mock_get, \
         patch.object(client, "post", new_callable=AsyncMock) as mock_post, \
         patch.object(client, "execute_command", new_callable=AsyncMock) as mock_cmd:

        # Test search_articles
        mock_get.return_value = [{"id": "art-1", "summary": "Architecture Doc"}]
        res = await search_articles("Architecture", project="DOC")
        assert len(res) == 1
        mock_get.assert_called_with(
            "/api/articles",
            params={
                "query": "project: DOC Architecture",
                "$top": 10,
                "fields": "id,idReadable,summary,content,project(id,name,shortName),parentArticle(id,idReadable,summary),hasChildren,updated,reporter(name,login)",
            },
        )

        # Test create_article
        mock_post.return_value = {"id": "art-2", "idReadable": "DOC-A-2", "summary": "API Guidelines"}
        res = await create_article("DOC", "API Guidelines", "# Content", parent_article_id="art-1")
        assert res["idReadable"] == "DOC-A-2"

        # Test update_issue
        mock_cmd.return_value = {"success": True}
        res = await update_issue("PROJ-10", "State Fixed Assignee alex", comment="Fixed in branch main")
        mock_cmd.assert_called_with("PROJ-10", "State Fixed Assignee alex", "Fixed in branch main")

        # Test archive_issue
        await archive_issue("PROJ-10", "Duplicate")
        mock_cmd.assert_called_with("PROJ-10", "State Obsolete", comment="Archived: Duplicate")

        # Test link_issues
        await link_issues("PROJ-11", "PROJ-10", "subtask of")
        mock_cmd.assert_called_with("PROJ-11", "subtask of PROJ-10")

        # Test add_work_item
        await add_work_item("PROJ-10", "2h", "Code review")
        mock_cmd.assert_called_with("PROJ-10", "work 2h Code review")

        # Test poll_changes
        mock_get.return_value = [{"idReadable": "PROJ-10", "summary": "Task"}]
        res = await poll_changes(query="project: PROJ", since_minutes=30)
        assert len(res) == 1
        mock_get.assert_called_with(
            "/api/issues",
            params={
                "query": "updated: -30m project: PROJ",
                "fields": "id,idReadable,summary,updated,reporter(name,login),customFields(name,value(name,presentation))",
            },
        )

