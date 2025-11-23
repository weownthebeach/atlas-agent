"""Core ATLAS Agent orchestrator."""

from dataclasses import dataclass
from typing import Literal
from rich.console import Console

from atlas_agent.config import AtlasConfig
from atlas_agent.agents.computer_use import ComputerUseAgent
from atlas_agent.drivers.playwright_driver import PlaywrightDriver
from atlas_agent.drivers.selenium_driver import SeleniumDriver
from atlas_agent.drivers.base import BrowserDriver


@dataclass
class TestResult:
    """Result of a test execution."""
    success: bool
    task: str
    url: str | None
    response: str
    iterations: int
    error: str | None = None


class AtlasAgent:
    """Main ATLAS Agent orchestrator."""

    def __init__(self, config: AtlasConfig | None = None):
        self.config = config or AtlasConfig()
        self.console = Console()
        self._driver: BrowserDriver | None = None
        self._agent: ComputerUseAgent | None = None

    def _create_driver(self) -> BrowserDriver:
        """Create the appropriate browser driver."""
        if self.config.driver_type == "playwright":
            return PlaywrightDriver(self.config)
        else:
            return SeleniumDriver(self.config)

    async def start(self) -> None:
        """Start the ATLAS agent."""
        if not self.config.validate_api_key():
            raise ValueError("ANTHROPIC_API_KEY not configured")

        self._driver = self._create_driver()
        await self._driver.start()
        self._agent = ComputerUseAgent(self.config, self._driver)
        self.console.print("[green]ATLAS Agent started[/green]")

    async def stop(self) -> None:
        """Stop the ATLAS agent."""
        if self._driver:
            await self._driver.stop()
        self.console.print("[yellow]ATLAS Agent stopped[/yellow]")

    async def run_test(self, task: str, url: str | None = None) -> TestResult:
        """Run a single test task."""
        if not self._agent:
            raise RuntimeError("Agent not started. Call start() first.")

        self.console.print(f"[blue]Running test:[/blue] {task}")
        if url:
            self.console.print(f"[blue]URL:[/blue] {url}")

        try:
            result = await self._agent.run(task, url)
            return TestResult(
                success=result["success"],
                task=result["task"],
                url=result["url"],
                response=result["response"],
                iterations=result["iterations"],
            )
        except Exception as e:
            return TestResult(
                success=False,
                task=task,
                url=url,
                response="",
                iterations=0,
                error=str(e),
            )

    async def run_tests(self, tests: list[dict]) -> list[TestResult]:
        """Run multiple tests."""
        results = []
        for test in tests:
            result = await self.run_test(
                task=test.get("task", ""),
                url=test.get("url"),
            )
            results.append(result)
        return results

    async def __aenter__(self):
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.stop()
