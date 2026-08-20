from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


W, H = 1600, 900
BG = (15, 23, 42)
PANEL = (30, 41, 59)
WHITE = (241, 245, 249)
MUTED = (148, 163, 184)
GREEN = (74, 222, 128)
BLUE = (96, 165, 250)
PURPLE = (192, 132, 252)
YELLOW = (250, 204, 21)


def font(size):
    for path in ("C:/Windows/Fonts/segoeui.ttf", "C:/Windows/Fonts/arial.ttf"):
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def node(draw, box, label, color, diamond=False):
    x1, y1, x2, y2 = box
    if diamond:
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
        points = [(cx, y1), (x2, cy), (cx, y2), (x1, cy)]
        draw.polygon(points, fill=PANEL, outline=color)
    else:
        draw.rounded_rectangle(box, radius=18, fill=PANEL, outline=color, width=3)
    left = x1 + 20
    width = max(1, (x2 - x1 - 40) // 12)
    lines = []
    words = label.split()
    current = ""
    for word in words:
        if len(current) + len(word) + 1 > width:
            lines.append(current)
            current = word
        else:
            current = f"{current} {word}".strip()
    if current:
        lines.append(current)
    bbox = draw.multiline_textbbox((0, 0), "\n".join(lines), font=font(25), spacing=5, align="center")
    tx = (x1 + x2 - (bbox[2] - bbox[0])) // 2
    ty = (y1 + y2 - (bbox[3] - bbox[1])) // 2
    draw.multiline_text((tx, ty), "\n".join(lines), font=font(25), fill=WHITE, spacing=5, align="center")


def arrow(draw, start, end, color=GREEN):
    draw.line((start, end), fill=color, width=4)
    x1, y1 = start
    x2, y2 = end
    if abs(x2 - x1) >= abs(y2 - y1):
        points = [(x2, y2), (x2 - 14, y2 - 8), (x2 - 14, y2 + 8)] if x2 > x1 else [(x2, y2), (x2 + 14, y2 - 8), (x2 + 14, y2 + 8)]
    else:
        points = [(x2, y2), (x2 - 8, y2 + 14), (x2 + 8, y2 + 14)] if y2 < y1 else [(x2, y2), (x2 - 8, y2 - 14), (x2 + 8, y2 - 14)]
    draw.polygon(points, fill=color)


def main():
    image = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, W, 12), fill=GREEN)
    draw.text((75, 55), "SELF-HEALING TECHNICAL DOCUMENTATION", font=font(22), fill=GREEN)
    draw.text((75, 95), "How the GitHub Action works", font=font(46), fill=WHITE)

    boxes = {
        "a": (80, 300, 330, 390), "b": (430, 300, 680, 390), "c": (780, 300, 1050, 390),
        "d": (430, 560, 680, 650), "e": (1130, 300, 1430, 390), "f": (1130, 455, 1430, 535),
        "g": (1120, 590, 1440, 720), "h": (780, 770, 1050, 860), "i": (1130, 770, 1480, 860),
    }
    node(draw, boxes["a"], "Pull request changes", BLUE)
    node(draw, boxes["b"], "Python parser", BLUE)
    node(draw, boxes["c"], "Code-to-doc index", GREEN)
    node(draw, boxes["d"], "Markdown parser", PURPLE)
    node(draw, boxes["e"], "Rules-first diff detector", GREEN)
    node(draw, boxes["f"], "PR summary", BLUE)
    node(draw, boxes["g"], "Optional Ollama review", YELLOW, True)
    node(draw, boxes["h"], "Validated repair", GREEN)
    node(draw, boxes["i"], "Draft repair PR", GREEN)

    arrow(draw, (330, 345), (430, 345), BLUE)
    arrow(draw, (680, 345), (780, 345), GREEN)
    arrow(draw, (680, 605), (780, 390), PURPLE)
    arrow(draw, (1050, 345), (1130, 345), GREEN)
    arrow(draw, (1280, 390), (1280, 455), BLUE)
    arrow(draw, (1280, 390), (1280, 590), YELLOW)
    arrow(draw, (1200, 720), (1020, 770), GREEN)
    arrow(draw, (1050, 815), (1130, 815), GREEN)

    output = Path(__file__).resolve().parents[1] / "docs" / "architecture.png"
    output.parent.mkdir(parents=True, exist_ok=True)
    image.save(output, optimize=True)
    print(output)


if __name__ == "__main__":
    main()
