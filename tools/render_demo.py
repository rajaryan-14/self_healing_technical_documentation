from pathlib import Path
import textwrap

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont


W, H, FPS = 1280, 720, 30
BG = (15, 23, 42)
PANEL = (30, 41, 59)
MUTED = (148, 163, 184)
WHITE = (241, 245, 249)
GREEN = (74, 222, 128)
RED = (248, 113, 113)
BLUE = (96, 165, 250)
YELLOW = (250, 204, 21)


def font(size: int, mono: bool = False):
    candidates = [
        "C:/Windows/Fonts/consola.ttf" if mono else "C:/Windows/Fonts/segoeui.ttf",
        "C:/Windows/Fonts/arial.ttf",
    ]
    for candidate in candidates:
        if Path(candidate).exists():
            return ImageFont.truetype(candidate, size)
    return ImageFont.load_default()


def frame(title: str, kicker: str = "SELF-HEALING TECHNICAL DOCUMENTATION"):
    image = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, W, 12), fill=GREEN)
    draw.text((64, 48), kicker, font=font(20), fill=GREEN)
    draw.text((64, 88), title, font=font(42), fill=WHITE)
    return image, draw


def panel(draw, xy, fill=PANEL, outline=(51, 65, 85)):
    draw.rounded_rectangle(xy, radius=14, fill=fill, outline=outline, width=2)


def text(draw, xy, value, size=24, fill=WHITE, mono=False, spacing=8, width=None):
    value = "\n".join(textwrap.wrap(value, width=width)) if width else value
    draw.multiline_text(xy, value, font=font(size, mono), fill=fill, spacing=spacing)


def scene_title():
    image, draw = frame("Documentation that heals with your code")
    text(draw, (70, 205), "A rules-first GitHub Action for detecting stale Markdown docs in pull requests.", 30, width=42)
    panel(draw, (70, 390, 1210, 565))
    text(draw, (105, 430), "Python AST  →  code-to-doc links  →  diff detection  →  PR feedback", 28, GREEN, mono=True)
    text(draw, (105, 495), "No OpenAI API key required", 25, MUTED)
    return image


def scene_code():
    image, draw = frame("1. A code change is pushed")
    panel(draw, (70, 180, 610, 630))
    panel(draw, (670, 180, 1210, 630))
    text(draw, (100, 210), "demo/service.py", 22, BLUE, mono=True)
    text(draw, (100, 260), 'def start_server(\n    host="127.0.0.1",\n    port=8100\n):', 27, WHITE, mono=True)
    text(draw, (100, 470), "+ port=8100", 26, GREEN, mono=True)
    text(draw, (700, 210), "demo/README.md", 22, BLUE, mono=True)
    text(draw, (700, 270), "start_server listens on\nport 8000 by default.", 28, RED, mono=True)
    text(draw, (700, 430), "The docs are now stale.", 28, YELLOW)
    return image


def scene_action():
    image, draw = frame("2. The Action identifies the affected section")
    panel(draw, (70, 185, 1210, 625))
    draw.ellipse((110, 235, 150, 275), fill=YELLOW)
    text(draw, (175, 228), "Documentation Check", 28, WHITE)
    text(draw, (175, 275), "Rules-first analysis", 21, MUTED)
    text(draw, (115, 355), "⚠  1 documentation section may be stale", 30, YELLOW)
    text(draw, (115, 430), "demo/README.md > Starting the server", 26, BLUE, mono=True)
    text(draw, (115, 500), "Reason: linked Python symbol was changed", 24, MUTED)
    return image


def scene_repair():
    image, draw = frame("3. Optional local review and repair")
    panel(draw, (70, 190, 580, 620))
    panel(draw, (650, 190, 1210, 620))
    text(draw, (105, 225), "Ollama review", 24, GREEN)
    text(draw, (105, 285), "stale: true\nconfidence: 0.94\nreason: default changed", 27, WHITE, mono=True)
    text(draw, (685, 225), "Validated replacement", 24, GREEN)
    text(draw, (685, 285), "start_server listens on\nport 8100 by default.", 27, WHITE, mono=True)
    text(draw, (105, 500), "No cloud model required.", 24, MUTED)
    return image


def scene_green():
    image, draw = frame("4. The corrected PR passes")
    panel(draw, (150, 220, 1130, 545), fill=(22, 50, 38), outline=GREEN)
    draw.ellipse((220, 300, 300, 380), fill=GREEN)
    text(draw, (242, 312), "✓", 45, BG)
    text(draw, (345, 280), "All checks have passed", 34, WHITE)
    text(draw, (345, 340), "Documentation Check / docs", 25, GREEN)
    text(draw, (345, 405), "No linked documentation sections were affected.", 24, MUTED)
    text(draw, (150, 600), "Detect. Review. Repair. Verify.", 30, GREEN)
    return image


def scene_close():
    image, draw = frame("Built for real engineering workflows")
    text(draw, (70, 205), "GitHub Action  •  Python  •  Markdown  •  Ollama", 29, WHITE)
    text(draw, (70, 300), "github.com/rajaryan-14/self_healing_technical_documentation", 24, BLUE, mono=True)
    panel(draw, (70, 430, 1210, 560))
    text(draw, (105, 465), "No OpenAI API key required", 28, GREEN)
    return image


def write_scene(writer, image, seconds):
    array = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    for _ in range(int(seconds * FPS)):
        writer.write(array)


def main():
    output = Path(__file__).resolve().parents[1] / "docs" / "self-healing-demo.mp4"
    output.parent.mkdir(parents=True, exist_ok=True)
    writer = cv2.VideoWriter(str(output), cv2.VideoWriter_fourcc(*"mp4v"), FPS, (W, H))
    for image, seconds in [
        (scene_title(), 6), (scene_code(), 10), (scene_action(), 10),
        (scene_repair(), 10), (scene_green(), 10), (scene_close(), 6),
    ]:
        write_scene(writer, image, seconds)
    writer.release()
    print(f"Rendered {output} ({output.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()

