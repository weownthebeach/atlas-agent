# ATLAS Agent

**AI Testing and Automation System** - Use Claude's computer-use capability to test web applications with natural language.

## Features

- **Natural Language Testing**: Describe tests in plain English
- **Claude Computer-Use**: Leverages Claude's vision and computer control capabilities
- **Multiple Drivers**: Support for Playwright and Selenium
- **Interactive Mode**: Real-time testing sessions
- **Batch Testing**: Run multiple tests from JSON files

## Installation

```bash
pip install atlas-agent
```

Or install from source:

```bash
git clone https://github.com/weownthebeach/atlas-agent.git
cd atlas-agent
pip install -e .
```

### Install Browser Drivers

For Playwright:
```bash
playwright install
```

For Selenium, the WebDriver Manager will automatically download drivers.

## Configuration

Set your Anthropic API key:

```bash
export ANTHROPIC_API_KEY=your-api-key
```

Or create a `.env` file:

```bash
ANTHROPIC_API_KEY=your-api-key
```

## Usage

### Single Test

```bash
atlas run "Click the login button and verify a form appears" -u https://example.com
```

### Interactive Mode

```bash
atlas interactive -u https://example.com
```

Then enter test commands interactively:

```
Test> Click on the navigation menu
Test> Verify all links are visible
Test> exit
```

### Batch Testing

Create a JSON file with tests:

```json
[
  {"task": "Verify homepage loads correctly", "url": "https://example.com"},
  {"task": "Test the contact form submission", "url": "https://example.com/contact"}
]
```

Run:

```bash
atlas batch tests.json
```

### Options

- `--driver, -d`: Browser driver (`playwright` or `selenium`)
- `--headless/--no-headless`: Run browser headlessly
- `--browser, -b`: Browser type (`chromium`, `firefox`, `webkit`)
- `--model, -m`: Claude model to use

## Python API

```python
import asyncio
from atlas_agent import AtlasAgent, AtlasConfig

async def main():
    config = AtlasConfig(
        driver_type="playwright",
        headless=False,
    )

    async with AtlasAgent(config) as agent:
        result = await agent.run_test(
            task="Fill in the search box and click submit",
            url="https://example.com"
        )
        print(result.response)

asyncio.run(main())
```

## How It Works

1. ATLAS navigates to the specified URL using Playwright/Selenium
2. Takes a screenshot and sends it to Claude with your test description
3. Claude uses computer-use tools to interact with the page (click, type, scroll)
4. The agent continues until the test is complete or max iterations reached
5. Returns a detailed report of what was tested and the results

## Requirements

- Python 3.10+
- Anthropic API key with computer-use access
- Chrome/Chromium (for Selenium) or Playwright browsers

## License

MIT
