import asyncio

from datetime import datetime

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from pydoll.browser.chrome import Chrome
from pydoll.browser.page import Page
from pydoll.browser.options import Options

from .models import ExecuteScriptResult

from ..logger import logger
from .utils import decode_jwt


class Browser:
    browser: Chrome
    page: Page

    def __init__(self, browser: Chrome, page: Page) -> None:
        self.browser = browser
        self.page = page

    @staticmethod
    @asynccontextmanager
    async def init(options: Options | None = None) -> AsyncGenerator["Browser", None]:
        async with Chrome(options=options) as browser:
            await browser.start()

            page = await browser.get_page()

            yield Browser(browser=browser, page=page)


class G2GBrowser(Browser):
    def __init__(self, browser: Chrome, page: Page) -> None:
        super().__init__(browser, page)

    @staticmethod
    @asynccontextmanager
    async def init(
        options: Options | None = None,
    ) -> AsyncGenerator["G2GBrowser", None]:
        async with Browser.init(options=options) as g2g_browser:
            await g2g_browser.page.go_to("https://g2g.com")

            yield G2GBrowser(g2g_browser.browser, g2g_browser.page)

    async def get_access_token(self) -> str | None:
        script: str = """localStorage.getItem("accessToken")"""

        script_result = await self.page.execute_script(script=script)

        execute_script_result = ExecuteScriptResult.model_validate(script_result)

        return execute_script_result.result.result.value

    async def waiting_for_login(self, sleep_interval: int = 10) -> None:
        while True:
            if await self.get_access_token():
                return
            await asyncio.sleep(sleep_interval)

    async def is_valid_token(self, token) -> bool:
        decoded = decode_jwt(token)
        logger.info(f"Token expired at: {datetime.fromtimestamp(decoded.exp)}")
        now_timestampe = datetime.now().timestamp()
        if decoded.exp > now_timestampe:
            return True
        await self.page.refresh()
        await asyncio.sleep(5)
        return False

    async def get_access_token_in_safe(
        self,
        sleep_interval: int = 10,
    ) -> str:
        token: str | None = await self.get_access_token()
        if token:
            if await self.is_valid_token(token):
                return token
            return await self.get_access_token_in_safe(sleep_interval)

        logger.info("Waiting for login")
        await self.waiting_for_login(sleep_interval)
        return await self.get_access_token_in_safe(sleep_interval)
