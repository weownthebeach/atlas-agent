"""Configuration management for ATLAS Agent."""

import os
from typing import Literal
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()


class AtlasConfig(BaseModel):
    """Configuration for ATLAS Agent."""

    # API Configuration
    anthropic_api_key: str = Field(
        default_factory=lambda: os.getenv("ANTHROPIC_API_KEY", "")
    )
    model: str = Field(default="claude-sonnet-4-20250514")

    # Browser Configuration
    driver_type: Literal["playwright", "selenium"] = Field(default="playwright")
    headless: bool = Field(default=False)
    browser: Literal["chromium", "firefox", "webkit"] = Field(default="chromium")
    viewport_width: int = Field(default=1280)
    viewport_height: int = Field(default=800)

    # Test Configuration
    screenshot_dir: str = Field(default="./screenshots")
    timeout: int = Field(default=30000)
    max_iterations: int = Field(default=50)

    # Computer Use Configuration
    display_width: int = Field(default=1280)
    display_height: int = Field(default=800)

    def validate_api_key(self) -> bool:
        """Check if API key is configured."""
        return bool(self.anthropic_api_key)
