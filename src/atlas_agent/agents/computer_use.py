"""Claude Computer Use Agent for web testing."""

import json
from typing import Any
from anthropic import Anthropic
from anthropic.types.beta import (
    BetaMessage,
    BetaContentBlockParam,
    BetaToolResultBlockParam,
)

from atlas_agent.config import AtlasConfig
from atlas_agent.drivers.base import BrowserDriver
from atlas_agent.utils.screenshot import encode_screenshot


class ComputerUseAgent:
    """Agent that uses Claude's computer-use capability for web testing."""

    def __init__(self, config: AtlasConfig, driver: BrowserDriver):
        self.config = config
        self.driver = driver
        self.client = Anthropic(api_key=config.anthropic_api_key)
        self.messages: list = []

    def _get_tools(self) -> list[dict]:
        """Get the computer use tool definition."""
        width, height = self.driver.get_viewport_size()
        return [
            {
                "type": "computer_20250124",
                "name": "computer",
                "display_width_px": width,
                "display_height_px": height,
                "display_number": 1,
            }
        ]

    async def _handle_tool_use(self, tool_name: str, tool_input: dict) -> dict:
        """Handle a computer use tool call."""
        action = tool_input.get("action", "")
        result = {"type": "text", "text": ""}

        try:
            if action == "screenshot":
                screenshot = await self.driver.screenshot()
                return {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": "image/png",
                        "data": encode_screenshot(screenshot),
                    }
                }

            elif action == "mouse_move":
                x = tool_input.get("coordinate", [0, 0])[0]
                y = tool_input.get("coordinate", [0, 0])[1]
                await self.driver.move_mouse(x, y)
                result["text"] = f"Moved mouse to ({x}, {y})"

            elif action == "left_click":
                x = tool_input.get("coordinate", [0, 0])[0]
                y = tool_input.get("coordinate", [0, 0])[1]
                await self.driver.click(x, y)
                result["text"] = f"Clicked at ({x}, {y})"

            elif action == "left_click_drag":
                start = tool_input.get("start_coordinate", [0, 0])
                end = tool_input.get("coordinate", [0, 0])
                await self.driver.drag(start[0], start[1], end[0], end[1])
                result["text"] = f"Dragged from {start} to {end}"

            elif action == "right_click":
                x = tool_input.get("coordinate", [0, 0])[0]
                y = tool_input.get("coordinate", [0, 0])[1]
                await self.driver.click(x, y)  # Simplified
                result["text"] = f"Right clicked at ({x}, {y})"

            elif action == "double_click":
                x = tool_input.get("coordinate", [0, 0])[0]
                y = tool_input.get("coordinate", [0, 0])[1]
                await self.driver.click(x, y)
                await self.driver.click(x, y)
                result["text"] = f"Double clicked at ({x}, {y})"

            elif action == "type":
                text = tool_input.get("text", "")
                await self.driver.type_text(text)
                result["text"] = f"Typed: {text[:50]}..."

            elif action == "key":
                key = tool_input.get("key", "")
                await self.driver.press_key(key)
                result["text"] = f"Pressed key: {key}"

            elif action == "scroll":
                x = tool_input.get("coordinate", [640, 400])[0]
                y = tool_input.get("coordinate", [640, 400])[1]
                direction = tool_input.get("direction", "down")
                amount = tool_input.get("amount", 3)

                delta_y = -100 * amount if direction == "up" else 100 * amount
                delta_x = -100 * amount if direction == "left" else 100 * amount if direction == "right" else 0

                if direction in ["up", "down"]:
                    delta_x = 0
                else:
                    delta_y = 0

                await self.driver.scroll(x, y, delta_x, delta_y)
                result["text"] = f"Scrolled {direction} by {amount}"

            else:
                result["text"] = f"Unknown action: {action}"

        except Exception as e:
            result["text"] = f"Error executing {action}: {str(e)}"
            result["is_error"] = True

        return result

    async def run(self, task: str, url: str | None = None) -> dict:
        """Run a test task using computer use."""
        # Navigate to URL if provided
        if url:
            await self.driver.navigate(url)

        # Take initial screenshot
        screenshot = await self.driver.screenshot()

        # Build initial message
        initial_content: list[BetaContentBlockParam] = [
            {
                "type": "text",
                "text": f"""You are a web testing agent. Your task is to test a web application.

Task: {task}

Current page URL: {url or 'Not specified'}

Use the computer tool to interact with the browser. Start by taking a screenshot to see the current state, then perform the necessary actions to complete the test.

Report your findings clearly, including:
- What you tested
- What you observed
- Whether the test passed or failed
- Any issues or bugs found"""
            },
            {
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": "image/png",
                    "data": encode_screenshot(screenshot),
                }
            }
        ]

        self.messages = [{"role": "user", "content": initial_content}]

        # Run agent loop
        iteration = 0
        final_response = ""

        while iteration < self.config.max_iterations:
            response: BetaMessage = self.client.beta.messages.create(
                model=self.config.model,
                max_tokens=4096,
                tools=self._get_tools(),
                messages=self.messages,
                betas=["computer-use-2025-01-24"],
            )

            # Process response
            assistant_content = []
            tool_results = []

            for block in response.content:
                if block.type == "text":
                    final_response = block.text
                    assistant_content.append({"type": "text", "text": block.text})
                elif block.type == "tool_use":
                    assistant_content.append({
                        "type": "tool_use",
                        "id": block.id,
                        "name": block.name,
                        "input": block.input,
                    })

                    # Execute tool
                    result = await self._handle_tool_use(block.name, block.input)

                    tool_result: BetaToolResultBlockParam = {
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": [result] if result.get("type") == "image" else result.get("text", ""),
                    }
                    if result.get("is_error"):
                        tool_result["is_error"] = True
                    tool_results.append(tool_result)

            self.messages.append({"role": "assistant", "content": assistant_content})

            # Check if we're done
            if response.stop_reason == "end_turn" and not tool_results:
                break

            # Add tool results
            if tool_results:
                self.messages.append({"role": "user", "content": tool_results})

            iteration += 1

        return {
            "success": True,
            "iterations": iteration,
            "response": final_response,
            "task": task,
            "url": url,
        }
