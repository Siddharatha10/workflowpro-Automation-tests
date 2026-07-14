from playwright.sync_api import Page

from config import TENANTS
from pages.dashboard_page import DashboardPage
from pages.login_page import LoginPage
from pages.project_page import ProjectsPage


def test_user_login(page: Page):
    creds = TENANTS["company1"]
    LoginPage(page).goto().login(creds["email"], creds["password"])
    DashboardPage(page).expect_welcome_message()


def test_multi_tenant_access(page: Page):
    creds = TENANTS["company2"]
    LoginPage(page).goto().login(creds["email"], creds["password"])

    projects = ProjectsPage(page).goto().wait_for_list_loaded()
    texts = projects.all_card_texts()
    assert len(texts) > 0, "Expected at least one project for company2 user"
    for text in texts:
        assert "company2" in text, f"Tenant isolation issue: found '{text}' while logged in as company2"
