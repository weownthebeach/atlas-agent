"""Base browser driver interface."""

from abc import ABC, abstractmethod
from typing import Optional, Tuple


class BrowserDriver(ABC):
    """Abstract base class for browser drivers."""

    @abstractmethod
    async def start(self) -> None:
        """Start the browser."""
        pass

    @abstractmethod
    async def stop(self) -> None:
        """Stop the browser."""
        pass

    @abstractmethod
    async def navigate(self, url: str) -> None:
        """Navigate to a URL."""
        pass

    @abstractmethod
    async def screenshot(self) -> bytes:
        """Take a screenshot and return as bytes."""
        pass

    @abstractmethod
    async def click(self, x: int, y: int) -> None:
        """Click at coordinates."""
        pass

    @abstractmethod
    async def type_text(self, text: str) -> None:
        """Type text."""
        pass

    @abstractmethod
    async def press_key(self, key: str) -> None:
        """Press a keyboard key."""
        pass

    @abstractmethod
    async def scroll(self, x: int, y: int, delta_x: int, delta_y: int) -> None:
        """Scroll at position."""
        pass

    @abstractmethod
    async def get_page_info(self) -> dict:
        """Get current page information."""
        pass

    @abstractmethod
    async def move_mouse(self, x: int, y: int) -> None:
        """Move mouse to coordinates."""
        pass

    @abstractmethod
    async def drag(self, start_x: int, start_y: int, end_x: int, end_y: int) -> None:
        """Drag from start to end coordinates."""
        pass

    @abstractmethod
    def get_viewport_size(self) -> Tuple[int, int]:
        """Get viewport dimensions."""
        pass
