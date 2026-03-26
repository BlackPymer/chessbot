import os
from playwright.sync_api import sync_playwright, Browser, BrowserContext, Page
from ..service import Service


class ChesscomService(Service):
    def __init__(self, headless: bool = False):
        super().__init__()
        self.headless = headless
        self.playwright = sync_playwright().start()
        self.browser: Browser = self.playwright.chromium.launch(headless=headless)
        self.context: BrowserContext = self.browser.new_context()
        self.page: Page = self.context.new_page()
        self.page.goto("https://www.chess.com")

    def __del__(self):
        if hasattr(self, "browser"):
            self.browser.close()
        if hasattr(self, "playwright"):
            self.playwright.stop()

    def login(self):
        self.page.locator("xpath=/html/body/div[1]/div[1]/nav/div[5]/a[2]").click()
        self.page.wait_for_load_state("networkidle")

        username = os.getenv("CHESSCOM_LOGIN")
        password = os.getenv("CHESSCOM_PASSWORD")

        self.page.locator("xpath=//*[@id='login-username']").fill(username)
        self.page.locator("xpath=//*[@id='login-password']").fill(password)
        self.page.locator("xpath=//*[@id='login']").click()

        print("Click the human verification button if prompted")
        self.page.wait_for_load_state("networkidle", timeout=60000)

    def start_game(self):
        pass

    def navigate_to_bot(self, bot_name: str):
        pass

    def get_board_pos(self):
        pass
