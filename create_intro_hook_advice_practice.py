from pathlib import Path
from typing import Literal

from PIL import Image, ImageDraw, ImageFilter, ImageFont


BubblePosition = Literal["right_top", "right_center", "right_bottom", "left_top", "left_center", "left_bottom", "bottom_center", "center_center"]


def load_font(size: int, bold: bool = True) -> ImageFont.FreeTypeFont:
    candidates = [
        r"C:\Windows\Fonts\comicbd.ttf" if bold else r"C:\Windows\Fonts\comic.ttf",
        r"C:\Windows\Fonts\arialbd.ttf" if bold else r"C:\Windows\Fonts\arial.ttf",
        r"C:\Windows\Fonts\segoeuib.ttf" if bold else r"C:\Windows\Fonts\segoeui.ttf",
    ]
    for font_path in candidates:
        if Path(font_path).exists():
            return ImageFont.truetype(font_path, size=size)
    return ImageFont.load_default()


def text_bbox(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont, stroke_width: int = 0) -> tuple[int, int, int, int]:
    return draw.textbbox((0, 0), text, font=font, stroke_width=stroke_width)


def text_size(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont, stroke_width: int = 0) -> tuple[int, int]:
    box = text_bbox(draw, text, font, stroke_width)
    return box[2] - box[0], box[3] - box[1]


# def wrap_text(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont, max_width: int, stroke_width: int = 0) -> list[str]:
#     lines: list[str] = []
#     for raw_line in str(text).replace("\\n", "\n").splitlines():
#         words = raw_line.split()
#         if not words:
#             lines.append("")
#             continue

#         current = words[0]
#         for word in words[1:]:
#             trial = f"{current} {word}"
#             if text_size(draw, trial, font, stroke_width)[0] <= max_width:
#                 current = trial
#             else:
#                 lines.append(current)
#                 current = word
#         lines.append(current)
#     return lines

def wrap_text(
    draw: ImageDraw.ImageDraw,
    text: str,
    font: ImageFont.FreeTypeFont,
    max_width: int,
    stroke_width: int = 0,
    max_chars: int = 35
) -> list[str]:
    lines: list[str] = []

    for raw_line in str(text).replace("\\n", "\n").splitlines():
        words = raw_line.split()

        if not words:
            lines.append("")
            continue

        current = words[0]

        for word in words[1:]:
            trial = f"{current} {word}"

            if (
                len(trial) <= max_chars
                and text_size(draw, trial, font, stroke_width)[0] <= max_width
            ):
                current = trial
            else:
                lines.append(current)
                current = word

        lines.append(current)

    return lines


def fit_text(
    draw: ImageDraw.ImageDraw,
    text: str,
    max_text_width: int,
    max_text_height: int,
    start_font_size: int = 62,
    min_font_size: int = 30,
    stroke_width: int = 1,
) -> tuple[ImageFont.FreeTypeFont, list[str], int]:
    for size in range(start_font_size, min_font_size - 1, -2):
        font = load_font(size, bold=True)
        lines = wrap_text(draw, text, font, max_text_width, stroke_width)
        spacing = max(8, int(size * 0.18))
        heights = [text_size(draw, line or " ", font, stroke_width)[1] for line in lines]
        total_height = sum(heights) + spacing * max(0, len(lines) - 1)
        if total_height <= max_text_height:
            return font, lines, spacing

    font = load_font(min_font_size, bold=True)
    return font, wrap_text(draw, text, font, max_text_width, stroke_width), max(6, int(min_font_size * 0.15))


def draw_heart(draw: ImageDraw.ImageDraw, center: tuple[int, int], size: int, fill, outline) -> None:
    cx, cy = center
    s = size
    points = [
        (cx, cy + s),
        (cx - int(s * 1.25), cy - int(s * 0.12)),
        (cx - int(s * 0.62), cy - int(s * 0.9)),
        (cx, cy - int(s * 0.38)),
        (cx + int(s * 0.62), cy - int(s * 0.9)),
        (cx + int(s * 1.25), cy - int(s * 0.12)),
    ]
    draw.polygon(points, fill=outline)
    inner = [(int(cx + (x - cx) * 0.78), int(cy + (y - cy) * 0.78)) for x, y in points]
    draw.polygon(inner, fill=fill)


def draw_star(draw: ImageDraw.ImageDraw, center: tuple[int, int], radius: int, fill, outline) -> None:
    import math

    cx, cy = center
    points = []
    for i in range(10):
        angle = math.radians(-90 + i * 36)
        r = radius if i % 2 == 0 else radius * 0.45
        points.append((cx + math.cos(angle) * r, cy + math.sin(angle) * r))
    draw.polygon(points, fill=outline)

    inner = []
    for i in range(10):
        angle = math.radians(-90 + i * 36)
        r = radius * 0.78 if i % 2 == 0 else radius * 0.34
        inner.append((cx + math.cos(angle) * r, cy + math.sin(angle) * r))
    draw.polygon(inner, fill=fill)


def bubble_box_for_position(
    image_size: tuple[int, int],
    bubble_size: tuple[int, int],
    position: BubblePosition,
    margin: int,
) -> tuple[int, int, int, int]:
    image_w, image_h = image_size
    bubble_w, bubble_h = bubble_size

    if position.startswith("right"):
        x1 = image_w - bubble_w - margin
    else:
        x1 = margin

    if position.endswith("top"):
        y1 = margin
    elif position.endswith("bottom"):
        y1 = image_h - bubble_h - margin
    else:
        y1 = (image_h - bubble_h) // 2

    return x1, y1, x1 + bubble_w, y1 + bubble_h


def draw_single_cute_bubble(
    image: Image.Image,
    text: str,
    position: BubblePosition = "right_top",
    max_width_ratio: float = 0.46,
    max_height_ratio: float = 0.42,
    min_width_ratio: float = 0.28,
    padding_x: int = 72,
    padding_y: int = 48,
    font_size: int = 62,
    tail_to: tuple[int, int] | None = None,
) -> Image.Image:
    """
    Ve 1 bong bong xinh dep len anh. Bong bong tu mo rong theo do dai text.

    position:
        "right_top", "right_center", "right_bottom",
        "left_top", "left_center", "left_bottom"

    tail_to:
        Toa do dau nhon cua duoi bong bong. Neu khong truyen, ham tu dat duoi ve phia nhan vat.
    """
    base = image.convert("RGBA")
    image_w, image_h = base.size
    overlay = Image.new("RGBA", base.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    max_bubble_w = int(image_w * max_width_ratio)
    max_bubble_h = int(image_h * max_height_ratio)
    min_bubble_w = int(image_w * min_width_ratio)
    max_text_w = max_bubble_w - padding_x * 2
    max_text_h = max_bubble_h - padding_y * 2

    font, lines, spacing = fit_text(
        draw,
        text,
        max_text_width=max_text_w,
        max_text_height=max_text_h,
        start_font_size=font_size,
        min_font_size=30,
        stroke_width=1,
    )

    line_sizes = [text_size(draw, line or " ", font, 1) for line in lines]
    text_w = max((w for w, _ in line_sizes), default=0)
    text_h = sum(h for _, h in line_sizes) + spacing * max(0, len(lines) - 1)

    bubble_w = min(max_bubble_w, max(min_bubble_w, text_w + padding_x * 2))
    bubble_h = min(max_bubble_h, max(int(image_h * 0.18), text_h + padding_y * 2))
    box = bubble_box_for_position(base.size, (bubble_w, bubble_h), position, margin=42)
    x1, y1, x2, y2 = box

    if tail_to is None:
        if position.startswith("right"):
            tail_to = (max(20, x1 - 34), min(image_h - 20, y2 - int(bubble_h * 0.18)))
            tail_base = [(x1 + 52, y2 - 58), (x1 + 108, y2 - 42)]
        else:
            tail_to = (min(image_w - 20, x2 + 34), min(image_h - 20, y2 - int(bubble_h * 0.18)))
            tail_base = [(x2 - 108, y2 - 42), (x2 - 52, y2 - 58)]
    else:
        if position.startswith("right"):
            tail_base = [(x1 + 52, y2 - 58), (x1 + 108, y2 - 42)]
        else:
            tail_base = [(x2 - 108, y2 - 42), (x2 - 52, y2 - 58)]

    shadow = Image.new("RGBA", base.size, (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow)
    shadow_draw.rounded_rectangle((x1 + 8, y1 + 10, x2 + 8, y2 + 10), radius=72, fill=(0, 0, 0, 78))
    shadow_draw.polygon([tail_base[0], tail_base[1], (tail_to[0] + 8, tail_to[1] + 10)], fill=(0, 0, 0, 78))
    overlay.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(10)))

    # Tail first, then main bubble so the joint looks smooth.
    draw.polygon([tail_base[0], tail_base[1], tail_to], fill=(255, 255, 255, 244), outline=(80, 80, 80, 155))
    draw.rounded_rectangle(box, radius=72, fill=(255, 255, 255, 244), outline=(255, 255, 255, 255), width=10)
    draw.rounded_rectangle((x1 + 7, y1 + 7, x2 - 7, y2 - 7), radius=64, outline=(80, 80, 80, 150), width=3)

    # Pastel inner glow, similar to the reference image.
    glow = Image.new("RGBA", base.size, (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow)
    glow_draw.rounded_rectangle((x1 + 20, y1 + 20, x2 - 20, y2 - 18), radius=56, outline=(255, 202, 224, 115), width=7)
    glow_draw.arc((x1 + 40, y2 - 42, x2 - 40, y2 + 18), 190, 350, fill=(174, 218, 255, 115), width=5)
    overlay.alpha_composite(glow)

    text_x = x1 + (bubble_w - text_w) // 2
    text_y = y1 + (bubble_h - text_h) // 2 - 2
    for line, (_, line_h) in zip(lines, line_sizes):
        line_w = text_size(draw, line, font, 1)[0]
        draw.text(
            (x1 + (bubble_w - line_w) // 2, text_y),
            line,
            font=font,
            fill=(39, 39, 43, 255),
            stroke_width=1,
            stroke_fill=(255, 255, 255, 255),
        )
        text_y += line_h + spacing

    # Small cute stickers.
    draw_star(draw, (x1 + 46, y1 + 48), 20, (255, 218, 82, 245), (255, 255, 255, 245))
    draw_heart(draw, (x2 - 58, y2 - 48), 24, (255, 174, 197, 245), (255, 255, 255, 255))
    draw.ellipse((x2 - 78, y1 + 36, x2 - 46, y1 + 68), fill=(255, 198, 216, 245), outline=(255, 255, 255, 255), width=4)
    draw.ellipse((x2 - 48, y1 + 34, x2 - 18, y1 + 64), fill=(255, 232, 153, 245), outline=(255, 255, 255, 255), width=4)

    return Image.alpha_composite(base, overlay).convert("RGB")


def add_cute_speech_bubble(
    input_image: str | Path,
    output_image: str | Path,
    text: str,
    position: BubblePosition = "right_top",
    max_width_ratio: float = 0.46,
    max_height_ratio: float = 0.42,
    font_size: int = 62,
) -> Path:
    """
    Doc anh, ve 1 bong bong co text, roi luu thanh anh moi.
    """
    input_image = Path(input_image)
    output_image = Path(output_image)
    
    if Path.exists(output_image):
        return output_image

    image = Image.open(input_image).convert("RGB")
    result = draw_single_cute_bubble(
        image=image,
        text=text,
        position=position,
        max_width_ratio=max_width_ratio,
        max_height_ratio=max_height_ratio,
        font_size=font_size,
    )

    output_image.parent.mkdir(parents=True, exist_ok=True)
    result.save(output_image, quality=95)
    return output_image


# if __name__ == "__main__":
#     saved = add_cute_speech_bubble(
#         r"D:\VideoAI\scene_person_0.png",
#         r"D:\VideoAI\intro_bubble.png",
#         "Hello everyone!\nIt's great to be here with you.",
#         position="right_top",
#     )
#     print(f"Saved: {saved}")
