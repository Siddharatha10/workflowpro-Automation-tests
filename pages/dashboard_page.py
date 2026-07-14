from playwright.sync_api import Page, expect


class DashboardPage:
    def __init__(self, page: Page):
        self.page = page

    def expect_welcome_message(self, timeout: int = 10000):
        expect(self.page.locator(".welcome-message")).to_be_visible(timeout=timeout)
        return self
