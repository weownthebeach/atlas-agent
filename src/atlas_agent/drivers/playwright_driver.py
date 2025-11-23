"""Playwright browser driver implementation."""

from typing import Tuple
from playwright.async_api import async_playwright, Browser, Page, BrowserContext

from atlas_agent.drivers.base import BrowserDriver
from atlas_agent.config import AtlasConfig


class PlaywrightDriver(BrowserDriver):
    """Playwright-based browser driver."""

    def __init__(self, config: AtlasConfig):
        self.config = config
        self._playwright = None
        self._browser: Browser | None = None
        self._context: BrowserContext | None = None
        self._page: Page | None = None

    async def start(self) -> None:
        """Start the Playwright browser."""
        self._playwright = await async_playwright().start()

        browser_type = getattr(self._playwright, self.config.browser)
        self._browser = await browser_type.launch(headless=self.config.headless)

        self._context = await self._browser.new_context(
            viewport={
                "width": self.config.viewport_width,
                "height": self.config.viewport_height
            }
        )
        self._page = await self._context.new_page()
        self._page.set_default_timeout(self.config.timeout)

    async def stop(self) -> None:
        """Stop the Playwright browser."""
        if self._browser:
            await self._browser.close()
        if self._playwright:
            await self._playwright.stop()

    async def navigate(self, url: str) -> None:
        """Navigate to a URL."""
        if self._page:
            await self._page.goto(url, wait_until="domcontentloaded")

    async def screenshot(self) -> bytes:
        """Take a screenshot and return as bytes."""
        if self._page:
            return await self._page.screenshot(type="png")
        return b""

    async def click(self, x: int, y: int) -> None:
        """Click at coordinates."""
        if self._page:
            await self._page.mouse.click(x, y)

    async def type_text(self, text: str) -> None:
        """Type text."""
        if self._page:
            await self._page.keyboard.type(text)

    async def press_key(self, key: str) -> None:
        """Press a keyboard key."""
        if self._page:
            await self._page.keyboard.press(key)

    async def scroll(self, x: int, y: int, delta_x: int, delta_y: int) -> None:
        """Scroll at position."""
        if self._page:
            await self._page.mouse.move(x, y)
            await self._page.mouse.wheel(delta_x, delta_y)

    async def get_page_info(self) -> dict:
        """Get current page information."""
        if self._page:
            return {
                "url": self._page.url,
                "title": await self._page.title(),
            }
        return {}

    async def move_mouse(self, x: int, y: int) -> None:
        """Move mouse to coordinates."""
        if self._page:
            await self._page.mouse.move(x, y)

    async def drag(self, start_x: int, start_y: int, end_x: int, end_y: int) -> None:
        """Drag from start to end coordinates."""
        if self._page:
            await self._page.mouse.move(start_x, start_y)
            await self._page.mouse.down()
            await self._page.mouse.move(end_x, end_y)
            await self._page.mouse.up()

    def get_viewport_size(self) -> Tuple[int, int]:
        """Get viewport dimensions."""
        return (self.config.viewport_width, self.config.viewport_height)
