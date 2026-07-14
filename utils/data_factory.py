import uuid


def unique_project_name(prefix: str = "QA-Test-Project") -> str:
    """UUID-suffixed name so parallel CI runs never collide."""
    return f"{prefix}-{uuid.uuid4().hex[:8]}"
