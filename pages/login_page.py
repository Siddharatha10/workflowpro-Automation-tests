from playwright.sync_api import Page, expect

from config import TEST_OTP, UI_BASE_URL


class LoginPage:
    """Encapsulates the login + optional 2FA flow so tests never touch selectors."""

    def __init__(self, page: Page):
        self.page = page

    def goto(self):
        self.page.goto(f"{UI_BASE_URL}/login")
        return self

    def login(self, email: str, password: str):
        self.page.fill("#email", email)
        self.page.fill("#password", password)
        self.page.click("#login-btn")

        otp_input = self.page.locator("#otp-code")
        try:
            otp_input.wait_for(state="visible", timeout=3000)
            otp_input.fill(TEST_OTP)
            self.page.click("#verify-otp-btn")
        except Exception:
            pass  # this account doesn't require 2FA -- not an error

        expect(self.page).to_have_url(f"{UI_BASE_URL}/dashboard", timeout=15000)
        return self
