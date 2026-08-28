from typing import Any

ISSUE_TEMPLATES: dict[str, dict[str, Any]] = {
    "bug": {
        "name": "Bug Report",
        "description": "Standard bug report structure with steps to reproduce and environment.",
        "sections": [
            ("Summary", "Brief description of the bug"),
            ("Steps to Reproduce", "1. Step one\n2. Step two\n3. Step three"),
            ("Expected Result", "What should happen"),
            ("Actual Result", "What actually happens"),
            ("Environment", "OS, browser, service version, branch"),
            ("Severity", "Critical / Major / Minor / Trivial"),
            ("Logs & Screenshots", "Attach or paste stack traces / screenshots if available"),
        ],
    },
    "feature": {
        "name": "Feature Request",
        "description": "Standard user story or feature specification with acceptance criteria.",
        "sections": [
            ("Problem / Context", "What problem are we solving and for whom?"),
            ("Proposed Solution", "Detailed description of the proposed feature"),
            ("Acceptance Criteria (DoD)", "- [ ] Criterion 1\n- [ ] Criterion 2\n- [ ] Unit & integration tests added"),
            ("Alternatives Considered", "Other approaches evaluated"),
            ("Priority", "Must Have / Should Have / Nice to Have"),
        ],
    },
    "task": {
        "name": "Technical Task",
        "description": "Standard engineering task with technical notes and definition of done.",
        "sections": [
            ("Objective", "What needs to be implemented or refactored?"),
            ("Technical Details", "Architecture notes, classes, endpoints, schemas to modify"),
            ("Definition of Done", "- [ ] Implementation complete\n- [ ] Tests passing\n- [ ] Documentation updated"),
        ],
    },
    "incident": {
        "name": "Incident / Postmortem",
        "description": "Production incident analysis and action items.",
        "sections": [
            ("Incident Summary", "Brief description of what went wrong and business impact"),
            ("Root Cause", "Technical root cause analysis"),
            ("Timeline", "- HH:MM Event detected\n- HH:MM Mitigation applied"),
            ("Action Items", "- [ ] Preventive measure 1\n- [ ] Monitoring alert added"),
        ],
    },
    "spike": {
        "name": "Research / Spike",
        "description": "Time-boxed technical research or proof of concept.",
        "sections": [
            ("Research Goal", "What question or hypothesis are we investigating?"),
            ("Scope & Constraints", "Time limit and boundaries of research"),
            ("Deliverables", "- Technical recommendation / ADR\n- Proof of concept code"),
        ],
    },
    "daily": {
        "name": "Daily Standup",
        "description": "Standup status sync item.",
        "sections": [
            ("Done Yesterday", "- Task 1\n- Task 2"),
            ("Planned Today", "- Task 1\n- Task 2"),
            ("Blockers", "None"),
        ],
    },
    "release": {
        "name": "Release Notes",
        "description": "Version release plan and changelog checklist.",
        "sections": [
            ("Release Scope", "Version number, targeted services and components"),
            ("Key Changes", "- New Features\n- Bug Fixes\n- Breaking Changes"),
            ("Deployment Checklist", "- [ ] Migrations executed\n- [ ] Smoke tests passed\n- [ ] Monitored metrics healthy"),
        ],
    },
}


def list_templates_summary() -> str:
    """Format available templates into a clear markdown guide for the LLM."""
    lines = ["### 📋 Available Issue Templates (Cross-LLM Standard)", ""]
    for key, tpl in ISSUE_TEMPLATES.items():
        sec_names = ", ".join(f"`{s[0]}`" for s in tpl["sections"])
        lines.append(f"* **`{key}`** ({tpl['name']}): {tpl['description']}")
        lines.append(f"  * Sections: {sec_names}")
    lines.append("")
    lines.append("Use `create_issue_from_template` with the template key to generate standardized issues.")
    return "\n".join(lines)


def build_template_description(template_key: str, section_data: dict[str, str] | None = None) -> str:
    """Generate Markdown description from template sections and provided values."""
    tpl = ISSUE_TEMPLATES.get(template_key.lower())
    if not tpl:
        available = ", ".join(ISSUE_TEMPLATES.keys())
        raise ValueError(f"Unknown template '{template_key}'. Available: {available}")

    data = section_data or {}
    # Lowercase lookup map for flexible matching
    lookup = {k.lower().replace(" ", "").replace("_", ""): v for k, v in data.items()}

    lines = []
    for title, default_hint in tpl["sections"]:
        key_norm = title.lower().replace(" ", "").replace("_", "")
        content = lookup.get(key_norm, default_hint)
        lines.append(f"## {title}\n{content}\n")

    return "\n".join(lines).strip()
