from playwright.sync_api import Page, expect

from config import UI_BASE_URL


class ProjectsPage:
    def __init__(self, page: Page):
        self.page = page

    def goto(self):
        self.page.goto(f"{UI_BASE_URL}/projects")
        return self

    def wait_for_list_loaded(self, timeout: int = 10000):
        expect(self.page.locator(".project-list")).to_be_visible(timeout=timeout)
        expect(self.page.locator(".project-card").first).to_be_visible(timeout=timeout)
        return self

    def all_card_texts(self):
        return [c.text_content() for c in self.page.locator(".project-card").all()]

    def expect_card_with_name(self, name: str, timeout: int = 10000):
        card = self.page.locator(".project-card", has_text=name)
        expect(card).to_be_visible(timeout=timeout)
        return self
