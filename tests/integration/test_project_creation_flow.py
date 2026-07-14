"""
Business flow under test:
  1. API creates the project (fast, deterministic setup)
  2. Web UI is asserted to reflect that same project
  3. Mobile viewport (emulated; swap for BrowserStack CDP in real CI) reflects it too
  4. A second tenant's token is asserted to be denied access to it
"""
from playwright.sync_api import Page, expect

from api.projects_client import ProjectsClient
from config import API_BASE_URL, TENANTS, UI_BASE_URL
from pages.login_page import LoginPage
from pages.project_page import ProjectsPage


class TestProjectCreationFlow:
    def test_project_visible_in_web_ui(self, page: Page, test_project):
        creds = TENANTS["company1"]
        LoginPage(page).goto().login(creds["email"], creds["password"])
        ProjectsPage(page).goto().expect_card_with_name(test_project["name"])

    def test_tenant_isolation(self, api_token, test_project):
        """A company2-scoped token must never see a company1 project."""
        wrong_tenant_client = ProjectsClient(api_token, tenant="company2")
        resp = wrong_tenant_client.get(test_project["id"])
        assert resp.status_code in (403, 404), (
            f"Tenant isolation breach: company2 token got {resp.status_code} "
            "for a company1 project"
        )

    def test_mobile_accessibility_emulated(self, browser, test_project):
        """
        Real BrowserStack device session in CI; here substituted with a
        Chromium context configured with an iPhone viewport/UA/touch profile
        (this sandbox has no network access to browserstack.com).
        Swap `browser.new_context(**mobile)` for
        `playwright.chromium.connect(browserstack_cdp_url)` to run for real.
        """
        mobile = {
            "viewport": {"width": 390, "height": 844},
            "user_agent": (
                "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) "
                "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1"
            ),
            "is_mobile": True,
            "has_touch": True,
        }
        context = browser.new_context(**mobile)
        page = context.new_page()
        try:
            creds = TENANTS["company1"]
            LoginPage(page).goto().login(creds["email"], creds["password"])
            ProjectsPage(page).goto().expect_card_with_name(test_project["name"], timeout=15000)
        finally:
            context.close()
