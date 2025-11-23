"""CLI interface for ATLAS Agent."""

import asyncio
import json
import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from atlas_agent.core import AtlasAgent
from atlas_agent.config import AtlasConfig


console = Console()


@click.group()
@click.version_option(version="0.1.0", prog_name="atlas")
def main():
    """ATLAS - AI Testing and Automation System.

    Use Claude's computer-use capability to test web applications.
    """
    pass


@main.command()
@click.argument("task")
@click.option("--url", "-u", help="URL to test")
@click.option("--driver", "-d", type=click.Choice(["playwright", "selenium"]), default="playwright")
@click.option("--headless/--no-headless", default=False, help="Run browser in headless mode")
@click.option("--browser", "-b", type=click.Choice(["chromium", "firefox", "webkit"]), default="chromium")
@click.option("--model", "-m", default="claude-sonnet-4-20250514", help="Claude model to use")
def run(task: str, url: str | None, driver: str, headless: bool, browser: str, model: str):
    """Run a test task.

    TASK is the test description in natural language.

    Examples:

        atlas run "Click the login button and verify it shows a form" -u https://example.com

        atlas run "Fill in the contact form with test data" -u https://example.com/contact
    """
    config = AtlasConfig(
        driver_type=driver,
        headless=headless,
        browser=browser,
        model=model,
    )

    async def execute():
        async with AtlasAgent(config) as agent:
            result = await agent.run_test(task, url)

            if result.success:
                console.print(Panel(
                    result.response,
                    title="[green]Test Result[/green]",
                    border_style="green"
                ))
            else:
                console.print(Panel(
                    result.error or "Test failed",
                    title="[red]Test Failed[/red]",
                    border_style="red"
                ))

            console.print(f"\n[dim]Iterations: {result.iterations}[/dim]")

    asyncio.run(execute())


@main.command()
@click.argument("file", type=click.Path(exists=True))
@click.option("--driver", "-d", type=click.Choice(["playwright", "selenium"]), default="playwright")
@click.option("--headless/--no-headless", default=False)
def batch(file: str, driver: str, headless: bool):
    """Run tests from a JSON file.

    FILE should be a JSON file with an array of test objects:

    [
        {"task": "Test description", "url": "https://example.com"},
        {"task": "Another test", "url": "https://example.com/page"}
    ]
    """
    with open(file) as f:
        tests = json.load(f)

    config = AtlasConfig(driver_type=driver, headless=headless)

    async def execute():
        async with AtlasAgent(config) as agent:
            results = await agent.run_tests(tests)

            # Display results table
            table = Table(title="Test Results")
            table.add_column("Task", style="cyan")
            table.add_column("URL", style="blue")
            table.add_column("Status", style="green")
            table.add_column("Iterations")

            for result in results:
                status = "[green]PASS[/green]" if result.success else "[red]FAIL[/red]"
                table.add_row(
                    result.task[:50] + "..." if len(result.task) > 50 else result.task,
                    result.url or "-",
                    status,
                    str(result.iterations)
                )

            console.print(table)

            # Summary
            passed = sum(1 for r in results if r.success)
            console.print(f"\n[bold]Summary:[/bold] {passed}/{len(results)} tests passed")

    asyncio.run(execute())


@main.command()
@click.option("--url", "-u", required=True, help="URL to test")
@click.option("--driver", "-d", type=click.Choice(["playwright", "selenium"]), default="playwright")
@click.option("--headless/--no-headless", default=False)
def interactive(url: str, driver: str, headless: bool):
    """Start an interactive testing session.

    Enter test tasks interactively and see results in real-time.
    """
    config = AtlasConfig(driver_type=driver, headless=headless)

    async def execute():
        async with AtlasAgent(config) as agent:
            console.print(f"[green]Interactive session started[/green]")
            console.print(f"[blue]URL:[/blue] {url}")
            console.print("[dim]Type 'exit' to quit[/dim]\n")

            # Navigate to URL
            if agent._driver:
                await agent._driver.navigate(url)

            while True:
                task = console.input("[bold cyan]Test> [/bold cyan]")
                if task.lower() in ("exit", "quit", "q"):
                    break

                if not task.strip():
                    continue

                result = await agent.run_test(task, url)

                if result.success:
                    console.print(f"\n[green]Result:[/green] {result.response}\n")
                else:
                    console.print(f"\n[red]Error:[/red] {result.error}\n")

    asyncio.run(execute())


@main.command()
def config():
    """Show current configuration."""
    cfg = AtlasConfig()

    table = Table(title="ATLAS Configuration")
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="green")

    table.add_row("API Key", "****" + cfg.anthropic_api_key[-4:] if cfg.anthropic_api_key else "[red]Not set[/red]")
    table.add_row("Model", cfg.model)
    table.add_row("Driver", cfg.driver_type)
    table.add_row("Browser", cfg.browser)
    table.add_row("Headless", str(cfg.headless))
    table.add_row("Viewport", f"{cfg.viewport_width}x{cfg.viewport_height}")
    table.add_row("Timeout", f"{cfg.timeout}ms")
    table.add_row("Max Iterations", str(cfg.max_iterations))

    console.print(table)


@main.command()
@click.option("--host", "-h", default="0.0.0.0", help="Host to bind to")
@click.option("--port", "-p", default=8000, help="Port to bind to")
def web(host: str, port: int):
    """Start the web interface.

    Access ATLAS through your browser at http://localhost:8000
    """
    from atlas_agent.web import run_server
    console.print(f"[green]Starting ATLAS Web Interface[/green]")
    console.print(f"[blue]Open http://localhost:{port} in your browser[/blue]")
    run_server(host=host, port=port)


if __name__ == "__main__":
    main()
