"""
CRONUS Vision Tool — Screen capture + visual analysis.

Captures the screen (or a region), encodes it, and sends it to the
configured vision model (gpt-4o by default) for analysis.

Used primarily by Curiosity (C) and User (U) totems for:
- Inspecting running applications in the Dream Caesar workspace
- Visual QA and layout verification
- Reading on-screen text when OCR is needed
- Capturing evidence of bugs or UI issues
"""

from __future__ import annotations

import base64
import io
import os
from typing import Any, Dict, Optional

import mss
from PIL import Image


def _capture_screen(
    monitor: int = 0,
    region: Optional[Dict[str, int]] = None,
) -> bytes:
    """
    Capture the screen (or a region) and return PNG bytes.

    Args:
        monitor: Monitor index (0 = all monitors combined, 1 = primary, etc.)
        region: Optional dict with {left, top, width, height} for a sub-region.
    """
    with mss.mss() as sct:
        if region:
            grab_area = {
                "left": region.get("left", 0),
                "top": region.get("top", 0),
                "width": region.get("width", 800),
                "height": region.get("height", 600),
            }
        else:
            grab_area = sct.monitors[monitor]

        screenshot = sct.grab(grab_area)
        img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")

        # Resize if huge (keep under ~1600px wide for vision model efficiency)
        max_width = 1600
        if img.width > max_width:
            ratio = max_width / img.width
            img = img.resize(
                (max_width, int(img.height * ratio)),
                Image.LANCZOS,
            )

        buf = io.BytesIO()
        img.save(buf, format="PNG", optimize=True)
        return buf.getvalue()


def _encode_image(png_bytes: bytes) -> str:
    """Base64-encode PNG bytes for vision API."""
    return base64.b64encode(png_bytes).decode("utf-8")


async def _analyze_with_vision(
    image_b64: str,
    prompt: str,
    model: str = "gpt-4o",
    base_url: str = "https://api.openai.com/v1",
    api_key: Optional[str] = None,
) -> str:
    """Send image + prompt to a vision-capable model and return the response."""
    from openai import AsyncOpenAI

    key = api_key or os.getenv("OPENAI_API_KEY") or "none"
    client = AsyncOpenAI(base_url=base_url, api_key=key)

    response = await client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{image_b64}",
                            "detail": "high",
                        },
                    },
                ],
            }
        ],
        max_tokens=1024,
    )

    return response.choices[0].message.content or ""


def handle_screenshot(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """
    Capture the screen and return base64 PNG.

    Args (in arguments dict):
        monitor: int (0=all, 1=primary, etc.) — default 0
        region: optional {left, top, width, height}
        save_path: optional file path to save the PNG
    """
    try:
        monitor = arguments.get("monitor", 0)
        region = arguments.get("region")
        save_path = arguments.get("save_path")

        png_bytes = _capture_screen(monitor=monitor, region=region)
        b64 = _encode_image(png_bytes)

        result: Dict[str, Any] = {
            "success": True,
            "image_base64": b64,
            "size_bytes": len(png_bytes),
        }

        if save_path:
            with open(save_path, "wb") as f:
                f.write(png_bytes)
            result["saved_to"] = save_path

        return result

    except Exception as e:
        return {"success": False, "error": str(e)}


def handle_vision_analyze(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """
    Capture the screen and analyze it with the vision model.

    Args (in arguments dict):
        prompt: str — what to look for / analyze
        monitor: int — default 0
        region: optional {left, top, width, height}
        image_base64: optional — skip capture, use this image instead
    """
    import asyncio

    try:
        prompt = arguments.get("prompt", "Describe what you see on screen.")
        image_b64 = arguments.get("image_base64")

        if not image_b64:
            monitor = arguments.get("monitor", 0)
            region = arguments.get("region")
            png_bytes = _capture_screen(monitor=monitor, region=region)
            image_b64 = _encode_image(png_bytes)

        # Get vision model config
        model = os.getenv("CRONUS_VISION_MODEL") or "gpt-4o"
        base_url = os.getenv("CRONUS_VISION_BASE_URL") or "https://api.openai.com/v1"
        api_key = os.getenv("CRONUS_VISION_API_KEY") or os.getenv("OPENAI_API_KEY")

        # Run the async analysis
        loop = asyncio.get_event_loop()
        if loop.is_running():
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as pool:
                analysis = pool.submit(
                    asyncio.run,
                    _analyze_with_vision(image_b64, prompt, model, base_url, api_key),
                ).result()
        else:
            analysis = asyncio.run(
                _analyze_with_vision(image_b64, prompt, model, base_url, api_key)
            )

        return {
            "success": True,
            "analysis": analysis,
            "model": model,
        }

    except Exception as e:
        return {"success": False, "error": str(e)}
