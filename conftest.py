import pytest

from api.auth_client import login
from api.projects_client import ProjectsClient
from config import TENANTS
from utils.data_factory import unique_project_name


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    return {**browser_context_args, "viewport": {"width": 1440, "height": 900}}


@pytest.fixture(scope="session")
def api_token():
    creds = TENANTS["company1"]
    return login(creds["email"], creds["password"])


@pytest.fixture
def test_project(api_token):
    """Creates a uniquely-named company1 project via API; always cleans up after."""
    client = ProjectsClient(api_token, tenant="company1")
    project = client.create(name=unique_project_name(), description="Created by automated test")
    yield project
    client.delete(project["id"])
