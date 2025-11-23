"""Selenium browser driver implementation."""

import asyncio
from typing import Tuple

from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager

from atlas_agent.drivers.base import BrowserDriver
from atlas_agent.config import AtlasConfig


class SeleniumDriver(BrowserDriver):
    """Selenium-based browser driver."""

    def __init__(self, config: AtlasConfig):
        self.config = config
        self._driver: webdriver.Chrome | None = None

    async def start(self) -> None:
        """Start the Selenium browser."""
        options = ChromeOptions()
        if self.config.headless:
            options.add_argument("--headless=new")
        options.add_argument(f"--window-size={self.config.viewport_width},{self.config.viewport_height}")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

        service = ChromeService(ChromeDriverManager().install())
        self._driver = await asyncio.to_thread(
            webdriver.Chrome, service=service, options=options
        )

    async def stop(self) -> None:
        """Stop the Selenium browser."""
        if self._driver:
            await asyncio.to_thread(self._driver.quit)

    async def navigate(self, url: str) -> None:
        """Navigate to a URL."""
        if self._driver:
            await asyncio.to_thread(self._driver.get, url)

    async def screenshot(self) -> bytes:
        """Take a screenshot and return as bytes."""
        if self._driver:
            return await asyncio.to_thread(self._driver.get_screenshot_as_png)
        return b""

    async def click(self, x: int, y: int) -> None:
        """Click at coordinates."""
        if self._driver:
            actions = ActionChains(self._driver)
            actions.move_by_offset(x, y).click().perform()
            actions.reset_actions()

    async def type_text(self, text: str) -> None:
        """Type text."""
        if self._driver:
            actions = ActionChains(self._driver)
            actions.send_keys(text).perform()

    async def press_key(self, key: str) -> None:
        """Press a keyboard key."""
        if self._driver:
            key_map = {
                "Enter": Keys.ENTER,
                "Tab": Keys.TAB,
                "Escape": Keys.ESCAPE,
                "Backspace": Keys.BACKSPACE,
                "Delete": Keys.DELETE,
                "ArrowUp": Keys.ARROW_UP,
                "ArrowDown": Keys.ARROW_DOWN,
                "ArrowLeft": Keys.ARROW_LEFT,
                "ArrowRight": Keys.ARROW_RIGHT,
            }
            selenium_key = key_map.get(key, key)
            actions = ActionChains(self._driver)
            actions.send_keys(selenium_key).perform()

    async def scroll(self, x: int, y: int, delta_x: int, delta_y: int) -> None:
        """Scroll at position."""
        if self._driver:
            self._driver.execute_script(f"window.scrollBy({delta_x}, {delta_y});")

    async def get_page_info(self) -> dict:
        """Get current page information."""
        if self._driver:
            return {
                "url": self._driver.current_url,
                "title": self._driver.title,
            }
        return {}

    async def move_mouse(self, x: int, y: int) -> None:
        """Move mouse to coordinates."""
        if self._driver:
            actions = ActionChains(self._driver)
            actions.move_by_offset(x, y).perform()
            actions.reset_actions()

    async def drag(self, start_x: int, start_y: int, end_x: int, end_y: int) -> None:
        """Drag from start to end coordinates."""
        if self._driver:
            actions = ActionChains(self._driver)
            actions.move_by_offset(start_x, start_y)
            actions.click_and_hold()
            actions.move_by_offset(end_x - start_x, end_y - start_y)
            actions.release()
            actions.perform()
            actions.reset_actions()

    def get_viewport_size(self) -> Tuple[int, int]:
        """Get viewport dimensions."""
        return (self.config.viewport_width, self.config.viewport_height)
