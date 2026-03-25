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
        self.page.click("/html/body/div[1]/div[1]/nav/div[5]/a[2]")
        self.page.wait_for_load_state("networkidle")

        username = os.getenv("CHESSCOM_LOGIN")
        password = os.getenv("CHESSCOM_PASSWORD")

        self.page.fill("//*[@id='login-username']", username)
        self.page.fill("//*[@id='login-password']", password)
        self.page.click("//*[@id='login']")

        print("Нажми кнопку подтверждения что ты человек, если потребуется")
        self.page.wait_for_load_state("networkidle", timeout=60000)

    def start_game(self):
        pass

    def navigate_to_bot(self, bot_name: str):
        pass

    def get_board_pos(self):
        pass
