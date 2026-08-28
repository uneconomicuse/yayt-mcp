import json
import logging
from typing import Any
from mcp.server.fastmcp import FastMCP

from yt_mcp.client import YouTrackClient
from yt_mcp.templates import list_templates_summary, build_template_description

logger = logging.getLogger("yt_mcp")

# Initialize FastMCP Server
mcp = FastMCP("youtrack")
client = YouTrackClient()


# ==========================================
# 1. 📚 База знаний (Articles / Knowledge Base)
# ==========================================

@mcp.tool()
async def search_articles(query: str, project: str | None = None, limit: int = 10) -> Any:
    """Search YouTrack Knowledge Base articles using full-text query and optional project filter."""
    q = query
    if project:
        q = f"project: {project} {query}".strip()
    
    fields = (
        "id,idReadable,summary,content,project(id,name,shortName),"
        "parentArticle(id,idReadable,summary),hasChildren,updated,reporter(name,login)"
    )
    return await client.get("/api/articles", params={"query": q, "$top": limit, "fields": fields})


@mcp.tool()
async def get_article(article_id: str) -> Any:
    """Get full details of a Knowledge Base article (Markdown content, author, attachments, sub-articles, comments)."""
    fields = (
        "id,idReadable,summary,content,project(id,name,shortName),"
        "parentArticle(id,idReadable,summary),childArticles(id,idReadable,summary),"
        "attachments(id,name,url,size),comments(id,text,created,author(name,login)),"
        "tags(id,name),updated,created,reporter(name,login)"
    )
    return await client.get(f"/api/articles/{article_id}", params={"fields": fields})


@mcp.tool()
async def create_article(
    project_id: str,
    summary: str,
    content: str,
    parent_article_id: str | None = None,
) -> Any:
    """Create a new article or sub-article in YouTrack Knowledge Base.
    
    Args:
        project_id: Project shortName or ID (e.g. 'DOC' or 'PROJ').
        summary: Title/headline of the article.
        content: Full Markdown content of the article.
        parent_article_id: Optional parent article ID/idReadable to place this article under.
    """
    payload: dict[str, Any] = {
        "summary": summary,
        "content": content,
        "project": {"id": project_id} if "-" not in project_id else {"shortName": project_id},
    }
    if parent_article_id:
        payload["parentArticle"] = {"id": parent_article_id}

    return await client.post("/api/articles", json_data=payload, params={"fields": "id,idReadable,summary"})


@mcp.tool()
async def update_article(
    article_id: str,
    summary: str | None = None,
    content: str | None = None,
) -> Any:
    """Update title and/or Markdown content of an existing article."""
    payload: dict[str, Any] = {}
    if summary is not None:
        payload["summary"] = summary
    if content is not None:
        payload["content"] = content

    if not payload:
        return {"error": "Nothing to update: provide either 'summary' or 'content'."}

    return await client.post(f"/api/articles/{article_id}", json_data=payload, params={"fields": "id,idReadable,summary,updated"})


@mcp.tool()
async def delete_article(article_id: str) -> Any:
    """Delete a Knowledge Base article (protected by Safe Mode: requires YOUTRACK_ALLOW_DELETE=true)."""
    return await client.delete(f"/api/articles/{article_id}")


@mcp.tool()
async def list_child_articles(article_id: str) -> Any:
    """List child articles (sub-articles) of a given article for knowledge tree navigation."""
    fields = "id,idReadable,summary,hasChildren,updated"
    return await client.get(f"/api/articles/{article_id}/childArticles", params={"fields": fields})


@mcp.tool()
async def add_article_comment(article_id: str, text: str) -> Any:
    """Add a Markdown comment to a Knowledge Base article."""
    payload = {"text": text}
    return await client.post(f"/api/articles/{article_id}/comments", json_data=payload, params={"fields": "id,text,created,author(name,login)"})


# ==========================================
# 2. 🎯 Задачи, Шаблоны и Мониторинг (Issues)
# ==========================================

@mcp.tool()
async def search_issues(query: str, limit: int = 20) -> Any:
    """Search YouTrack issues using YouTrack query syntax (e.g. '#Unresolved Assignee: me Priority: Critical')."""
    fields = (
        "id,idReadable,summary,description,project(id,name,shortName),"
        "created,updated,resolved,reporter(name,login),"
        "customFields(id,name,value(name,login,text,minutes,presentation)),"
        "tags(id,name),links(direction,linkType(name,sourceToTarget,targetToSource),issues(idReadable,summary))"
    )
    return await client.get("/api/issues", params={"query": query, "$top": limit, "fields": fields})


@mcp.tool()
async def get_issue(issue_id: str) -> Any:
    """Get full details of a specific issue by ID (e.g. 'PROJ-123')."""
    fields = (
        "id,idReadable,summary,description,project(id,name,shortName),"
        "created,updated,resolved,reporter(name,login),"
        "customFields(id,name,value(name,login,text,minutes,presentation)),"
        "tags(id,name),links(direction,linkType(name,sourceToTarget,targetToSource),issues(idReadable,summary)),"
        "attachments(id,name,url,size),comments(id,text,created,author(name,login))"
    )
    return await client.get(f"/api/issues/{issue_id}", params={"fields": fields})


@mcp.tool()
async def create_issue(project_id: str, summary: str, description: str = "") -> Any:
    """Create a new YouTrack issue in a project.
    
    Args:
        project_id: Project shortName or ID (e.g. 'PROJ').
        summary: Title/Summary of the issue.
        description: Markdown description of the issue.
    """
    payload = {
        "project": {"id": project_id} if len(project_id) > 10 else {"shortName": project_id},
        "summary": summary,
        "description": description,
    }
    return await client.post("/api/issues", json_data=payload, params={"fields": "id,idReadable,summary"})


@mcp.tool()
async def create_issue_from_template(
    project_id: str,
    template: str,
    summary: str,
    section_data: dict[str, str] | None = None,
) -> Any:
    """Create an issue using a standardized cross-LLM template (bug, feature, task, incident, spike, daily, release).
    
    Args:
        project_id: Target project (e.g. 'PROJ').
        template: Template key ('bug', 'feature', 'task', 'incident', 'spike', 'daily', 'release').
        summary: Short summary of the task.
        section_data: Dictionary mapping section names (e.g. 'steps_to_reproduce', 'expected_result') to content.
    """
    try:
        description = build_template_description(template, section_data)
    except ValueError as e:
        return {"error": str(e)}

    return await create_issue(project_id, summary, description)


@mcp.tool()
async def list_templates() -> str:
    """List all available standardized issue templates and their required sections."""
    return list_templates_summary()


@mcp.tool()
async def update_issue(issue_id: str, command: str, comment: str | None = None) -> Any:
    """Update issue fields, status, priority, or assignee using YouTrack Command syntax (e.g. 'State In Progress Assignee alex Priority Critical')."""
    return await client.execute_command(issue_id, command, comment)


@mcp.tool()
async def archive_issue(issue_id: str, reason: str = "Archived via MCP") -> Any:
    """Safely archive / soft-delete an issue (moves to 'State Obsolete' / 'State Cancelled' preserving all history and attachments)."""
    return await client.execute_command(issue_id, "State Obsolete", comment=f"Archived: {reason}")


@mcp.tool()
async def delete_issue(issue_id: str) -> Any:
    """Safely delete an issue via soft-delete / archiving (moves to 'State Obsolete' preserving history and attachments). Physical deletion is permanently disabled."""
    res = await archive_issue(issue_id, reason="Soft-deleted via delete_issue")
    if isinstance(res, dict) and "error" in res:
        return res
    return {
        "success": True,
        "message": f"Issue '{issue_id}' was safely archived (Soft-Delete: State Obsolete). All history, files, and links are preserved.",
        "details": res,
    }


@mcp.tool()
async def link_issues(source_id: str, target_id: str, link_type: str = "relates to") -> Any:
    """Link two issues together (e.g. 'subtask of', 'parent for', 'relates to', 'depends on', 'duplicates').
    
    Args:
        source_id: Origin issue (e.g. 'PROJ-101').
        target_id: Target issue (e.g. 'PROJ-100').
        link_type: Type of relation ('subtask of', 'parent for', 'relates to', 'depends on', 'duplicates').
    """
    cmd = f"{link_type} {target_id}"
    return await client.execute_command(source_id, cmd)


@mcp.tool()
async def get_issue_history(issue_id: str, limit: int = 15) -> Any:
    """Get audit trail and change history of an issue (who changed status, fields, assignees and when)."""
    fields = "id,timestamp,author(name,login),category(id),added,removed,target(id,name,idReadable)"
    categories = "CustomFieldActivityItem,CommentsActivityItem,IssueCreatedActivityItem,IssueResolvedActivityItem"
    return await client.get(
        f"/api/issues/{issue_id}/activities",
        params={"categories": categories, "$top": limit, "fields": fields},
    )


@mcp.tool()
async def poll_changes(query: str = "", since_minutes: int = 60) -> Any:
    """Poll recently changed issues within the last N minutes. Great for status tracking, daily catch-ups, and unblocking alerts."""
    time_query = f"updated: -{since_minutes}m"
    full_query = f"{time_query} {query}".strip() if query else time_query
    
    fields = (
        "id,idReadable,summary,updated,reporter(name,login),"
        "customFields(name,value(name,presentation))"
    )
    return await client.get("/api/issues", params={"query": full_query, "fields": fields})


# ==========================================
# 3. 💬 Комментарии к задачам (Comments)
# ==========================================

@mcp.tool()
async def add_comment(issue_id: str, text: str) -> Any:
    """Add a Markdown comment to an issue."""
    payload = {"text": text}
    return await client.post(
        f"/api/issues/{issue_id}/comments",
        json_data=payload,
        params={"fields": "id,text,created,author(name,login)"},
    )


@mcp.tool()
async def update_comment(issue_id: str, comment_id: str, text: str) -> Any:
    """Update an existing comment on an issue."""
    payload = {"text": text}
    return await client.post(
        f"/api/issues/{issue_id}/comments/{comment_id}",
        json_data=payload,
        params={"fields": "id,text,created,author(name,login)"},
    )


@mcp.tool()
async def delete_comment(issue_id: str, comment_id: str) -> Any:
    """Delete a comment from an issue (subject to Safe Mode)."""
    return await client.delete(f"/api/issues/{issue_id}/comments/{comment_id}")


# ==========================================
# 4. ⏱️ Учет времени (Time Tracking)
# ==========================================

@mcp.tool()
async def get_work_items(issue_id: str) -> Any:
    """Get logged time work items for an issue."""
    fields = "id,date,duration(minutes,presentation),text,type(name),author(name,login)"
    return await client.get(f"/api/issues/{issue_id}/timeTracking/workItems", params={"fields": fields})


@mcp.tool()
async def add_work_item(
    issue_id: str,
    duration: str,
    description: str = "",
    work_type: str | None = None,
    date: str | None = None,
) -> Any:
    """Log work time to an issue (e.g. duration: '1h 30m' or '45m')."""
    cmd = f"work {duration} {description}".strip()
    return await client.execute_command(issue_id, cmd)


# ==========================================
# 5. 👥 Agile, Команда и Проекты
# ==========================================

@mcp.tool()
async def get_agile_boards() -> Any:
    """List all agile (Scrum/Kanban) boards with their sprints and projects."""
    fields = "id,name,sprints(id,name,archived),projects(id,name,shortName)"
    return await client.get("/api/agiles", params={"fields": fields})


@mcp.tool()
async def get_sprint_board(board_id: str, sprint_id: str | None = None) -> Any:
    """Get issues on an agile board/sprint grouped by columns and statuses."""
    if not sprint_id:
        # Fetch current sprint
        board_data = await client.get(f"/api/agiles/{board_id}", params={"fields": "sprints(id,name,archived)"})
        if isinstance(board_data, dict) and "sprints" in board_data:
            active_sprints = [s for s in board_data["sprints"] if not s.get("archived")]
            if active_sprints:
                sprint_id = active_sprints[-1]["id"]

    path = f"/api/agiles/{board_id}/sprints/{sprint_id}" if sprint_id else f"/api/agiles/{board_id}"
    fields = "id,name,agile(id,name),issues(id,idReadable,summary,customFields(name,value(name,presentation)))"
    return await client.get(path, params={"fields": fields})


@mcp.tool()
async def find_users(query: str, limit: int = 10) -> Any:
    """Search YouTrack users by name, login, or email (useful for finding assignees)."""
    fields = "id,login,name,email"
    return await client.get("/api/users", params={"query": query, "$top": limit, "fields": fields})


@mcp.tool()
async def list_projects(limit: int = 50) -> Any:
    """List accessible projects (id, name, shortName, description)."""
    fields = "id,name,shortName,description,archived"
    return await client.get("/api/admin/projects", params={"$top": limit, "fields": fields})


@mcp.tool()
async def get_current_user() -> Any:
    """Get current authenticated user profile and verify connection to YouTrack."""
    fields = "id,login,name,email,guest"
    return await client.get("/api/users/me", params={"fields": fields})


def main():
    """Run the FastMCP server via stdio transport."""
    mcp.run()


if __name__ == "__main__":
    main()
