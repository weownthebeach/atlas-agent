"""Screenshot utilities for ATLAS Agent."""

import base64
import os
from datetime import datetime
from pathlib import Path
from PIL import Image
import io


def encode_screenshot(screenshot_bytes: bytes) -> str:
    """Encode screenshot bytes to base64 string."""
    return base64.standard_b64encode(screenshot_bytes).decode("utf-8")


def decode_screenshot(base64_string: str) -> bytes:
    """Decode base64 string to screenshot bytes."""
    return base64.standard_b64decode(base64_string)


def save_screenshot(
    screenshot_bytes: bytes,
    directory: str = "./screenshots",
    filename: str | None = None
) -> str:
    """Save screenshot to file and return the path."""
    Path(directory).mkdir(parents=True, exist_ok=True)

    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        filename = f"screenshot_{timestamp}.png"

    filepath = os.path.join(directory, filename)

    with open(filepath, "wb") as f:
        f.write(screenshot_bytes)

    return filepath


def resize_screenshot(screenshot_bytes: bytes, max_width: int = 1280, max_height: int = 800) -> bytes:
    """Resize screenshot if larger than max dimensions."""
    img = Image.open(io.BytesIO(screenshot_bytes))

    if img.width <= max_width and img.height <= max_height:
        return screenshot_bytes

    ratio = min(max_width / img.width, max_height / img.height)
    new_size = (int(img.width * ratio), int(img.height * ratio))

    img = img.resize(new_size, Image.Resampling.LANCZOS)

    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    return buffer.getvalue()
