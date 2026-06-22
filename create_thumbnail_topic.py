import math
from pathlib import Path
from typing import Iterable

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont

THUMBNAIL_SIZE = (1280, 720)


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


def center_crop(image: Image.Image, target_size: tuple[int, int]) -> Image.Image:
    target_w, target_h = target_size
    src_w, src_h = image.size
    target_ratio = target_w / target_h
    src_ratio = src_w / src_h

    if src_ratio > target_ratio:
        crop_w = int(src_h * target_ratio)
        left = (src_w - crop_w) // 2
        box = (left, 0, left + crop_w, src_h)
    else:
        crop_h = int(src_w / target_ratio)
        top = (src_h - crop_h) // 2
        box = (0, top, src_w, top + crop_h)

    return image.crop(box).resize(target_size, Image.Resampling.LANCZOS)


def text_size(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont, stroke: int = 0) -> tuple[int, int]:
    box = draw.textbbox((0, 0), text, font=font, stroke_width=stroke)
    return box[2] - box[0], box[3] - box[1]


def wrap_text(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont, max_width: int, stroke: int = 0) -> list[str]:
    lines: list[str] = []
    for raw_line in str(text).replace("\\n", "\n").splitlines():
        words = raw_line.split()
        if not words:
            lines.append("")
            continue

        current = words[0]
        for word in words[1:]:
            trial = f"{current} {word}"
            if text_size(draw, trial, font, stroke)[0] <= max_width:
                current = trial
            else:
                lines.append(current)
                current = word
        lines.append(current)
    return lines


def fit_wrapped_text(
    draw: ImageDraw.ImageDraw,
    text: str,
    max_width: int,
    max_height: int,
    start_size: int,
    min_size: int = 24,
    stroke: int = 10,
) -> tuple[ImageFont.FreeTypeFont, list[str], int]:
    for size in range(start_size, min_size - 1, -2):
        font = load_font(size, bold=True)
        lines = wrap_text(draw, text, font, max_width, stroke)
        line_heights = [text_size(draw, line or " ", font, stroke)[1] for line in lines]
        spacing = max(8, int(size * 0.16))
        total_h = sum(line_heights) + spacing * max(0, len(lines) - 1)
        if total_h <= max_height and all(text_size(draw, line, font, stroke)[0] <= max_width for line in lines):
            return font, lines, spacing

    font = load_font(min_size, bold=True)
    return font, wrap_text(draw, text, font, max_width, stroke), max(6, int(min_size * 0.12))


def draw_dashed_rounded_rectangle(
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    radius: int,
    fill: tuple[int, int, int, int],
    dash: int = 26,
    gap: int = 14,
) -> None:
    x1, y1, x2, y2 = box
    points: list[tuple[int, int]] = []

    for x in range(x1 + radius, x2 - radius):
        points.append((x, y1))
    for angle in range(270, 360):
        points.append((x2 - radius + int(radius * math.cos(math.radians(angle))), y1 + radius + int(radius * math.sin(math.radians(angle)))))
    for y in range(y1 + radius, y2 - radius):
        points.append((x2, y))
    for angle in range(0, 90):
        points.append((x2 - radius + int(radius * math.cos(math.radians(angle))), y2 - radius + int(radius * math.sin(math.radians(angle)))))
    for x in range(x2 - radius, x1 + radius, -1):
        points.append((x, y2))
    for angle in range(90, 180):
        points.append((x1 + radius + int(radius * math.cos(math.radians(angle))), y2 - radius + int(radius * math.sin(math.radians(angle)))))
    for y in range(y2 - radius, y1 + radius, -1):
        points.append((x1, y))
    for angle in range(180, 270):
        points.append((x1 + radius + int(radius * math.cos(math.radians(angle))), y1 + radius + int(radius * math.sin(math.radians(angle)))))

    step = dash + gap
    for start in range(0, len(points), step):
        segment = points[start : start + dash]
        if len(segment) > 1:
            draw.line(segment, fill=fill, width=3)


def draw_star(draw: ImageDraw.ImageDraw, center: tuple[int, int], radius: int, fill, outline) -> None:
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


def draw_heart(draw: ImageDraw.ImageDraw, center: tuple[int, int], size: int, fill, outline) -> None:
    cx, cy = center
    s = size
    outer = [
        (cx, cy + s),
        (cx - int(s * 1.25), cy - int(s * 0.15)),
        (cx - int(s * 0.68), cy - int(s * 0.95)),
        (cx, cy - int(s * 0.45)),
        (cx + int(s * 0.68), cy - int(s * 0.95)),
        (cx + int(s * 1.25), cy - int(s * 0.15)),
    ]
    inner = [(int(cx + (x - cx) * 0.82), int(cy + (y - cy) * 0.82)) for x, y in outer]
    draw.polygon(outer, fill=outline)
    draw.polygon(inner, fill=fill)


# 🎨 TĂNG CƯỜNG MÀU SẮC: Gradient chuyển đổi đậm đà, hiện rõ khối hình
def generate_vibrant_gradient(
    width: int, height: int, 
    color_left: tuple[int, int, int], color_right: tuple[int, int, int], 
    alpha_left: int, alpha_right: int
) -> Image.Image:
    gradient = Image.new("RGBA", (width, height))
    pixels = gradient.load()
    
    for x in range(width):
        t = x / max(1, width - 1)
        r = int((1 - t) * color_left[0] + t * color_right[0])
        g = int((1 - t) * color_left[1] + t * color_right[1])
        b = int((1 - t) * color_left[2] + t * color_right[2])
        a = int((1 - t) * alpha_left + t * alpha_right)
        
        for y in range(height):
            pixels[x, y] = (r, g, b, a)
    return gradient




def draw_panel_cloud_gradient(image: Image.Image, overlay: Image.Image, box: tuple[int, int, int, int]) -> None:
    x1, y1, x2, y2 = box
    w = x2 - x1
    h = y2 - y1

    cloud_mask = Image.new("L", (w, h), 0)
    mask_draw = ImageDraw.Draw(cloud_mask)
    
    circles = [
        (12, 25, int(w * 0.36), 145),
        (int(w * 0.22), 0, int(w * 0.65), 142),
        (int(w * 0.52), 25, w, 158),
        (2, h - 185, int(w * 0.36), h - 5),
        (int(w * 0.25), h - 150, int(w * 0.68), h + 10),
        (int(w * 0.58), h - 182, w + 16, h - 5),
    ]
    mask_draw.rounded_rectangle((10, 45, w - 10, h - 28), radius=54, fill=255)
    for circle in circles:
        mask_draw.ellipse(circle, fill=255)

    # 💧 TĂNG BLUE MẠNH MẼ: Đẩy Alpha lên cao (240 -> 160) để bong bóng mây hiện rõ nét sắc xanh Pastel nịnh mắt
    cloud_color_left = (50, 200, 225)
    cloud_color_right = (80, 220, 255)
    cloud_gradient = generate_vibrant_gradient(
        w, h,
        color_left=cloud_color_left, color_right=cloud_color_right,
        alpha_left=250, alpha_right=180
    )
    
    temp_layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    temp_layer.paste(cloud_gradient, (0, 0), mask=cloud_mask)
    
    bg_crop = image.crop(box).convert("RGBA")
    final_box = Image.alpha_composite(bg_crop, temp_layer)
    image.paste(final_box, (x1, y1))

    draw_draw = ImageDraw.Draw(overlay)
    draw_dashed_rounded_rectangle(
        draw_draw, 
        (x1 + 22, y1 + 54, x2 - 16, y2 - 34), 
        42, 
        (255, 255, 255, 200), 
        dash=14, 
        gap=10
    )


def draw_lesson_ribbon_gradient(image: Image.Image, overlay: Image.Image, lesson_text: str, side: str) -> None:
    draw = ImageDraw.Draw(overlay)
    if side == "right":
        ribbon = [(776, 116), (1178, 97), (1198, 238), (790, 229), (832, 187), (794, 149)]
        text_x = 842
    else:
        ribbon = [(90, 116), (395, 116), (460, 177), (395, 238), (90, 238)]
        text_x = 166

    rx1 = min(p[0] for p in ribbon)
    ry1 = min(p[1] for p in ribbon)
    rx2 = max(p[0] for p in ribbon)
    ry2 = max(p[1] for p in ribbon)
    rw, rh = rx2 - rx1, ry2 - ry1

    shadow = [(x + 6, y + 8) for x, y in ribbon]
    draw.polygon(shadow, fill=(180, 80, 130, 50))

    ribbon_mask = Image.new("L", (rw, rh), 0)
    local_poly = [(x - rx1, y - ry1) for x, y in ribbon]
    ImageDraw.Draw(ribbon_mask).polygon(local_poly, fill=255)
    
    # 🎀 SỬA ĐỔI CHUẨN: Giữ hồng đậm ngọt ngào bên trái, chuyển dần sang tông Blue nhẹ ở sát bạn nữ
    # Giữ Alpha cao (255 -> 200) để chiếc ruy băng hiện lên rõ ràng, chắc chắn và cực xinh!
    pink_color = (244, 111, 171)
    blue_blend_color = (0, 0, 255) 
    ribbon_gradient = generate_vibrant_gradient(
        width=rw, height=rh,
        color_left=pink_color, color_right=blue_blend_color,
        alpha_left=255, alpha_right=200
    )
    
    temp_layer = Image.new("RGBA", (rw, rh), (0, 0, 0, 0))
    temp_layer.paste(ribbon_gradient, (0, 0), mask=ribbon_mask)
    
    bg_crop = image.crop((rx1, ry1, rx2, ry2)).convert("RGBA")
    final_ribbon = Image.alpha_composite(bg_crop, temp_layer)
    image.paste(final_ribbon, (rx1, ry1))

    draw.polygon(ribbon, outline=(255, 255, 255, 220), width=3)

    max_w = 300 if side == "left" else 330
    for size in range(48, 27, -2):
        font = load_font(size, bold=True)
        if text_size(draw, lesson_text, font, 2)[0] <= max_w:
            break

    draw.text(
        (text_x, 127),
        lesson_text,
        font=font,
        fill=(255, 255, 255, 255),
        stroke_width=3,
        stroke_fill=(255, 75, 135, 200),
    )


def draw_channel_badge(draw, lesson_text: str):
    lesson_text = str(lesson_text).strip()[:30]
    font_size = 28
    font = load_font(font_size, bold=True)
    w, h = text_size(draw, lesson_text, font)

    badge_w = max(170, w + 60)
    badge_h = 86
    thumb_w, thumb_h = THUMBNAIL_SIZE

    padding_right = 45
    padding_bottom = 35
    cx = thumb_w - padding_right - badge_w // 2
    cy = thumb_h - padding_bottom - badge_h // 2

    draw.ellipse((cx - badge_w // 2 + 5, cy - badge_h // 2 + 7, cx + badge_w // 2 + 5, cy + badge_h // 2 + 7), fill=(0, 0, 0, 40))
    draw.ellipse((cx - badge_w // 2, cy - badge_h // 2, cx + badge_w // 2, cy + badge_h // 2), fill=(255, 255, 255), outline=(255, 150, 190), width=4)
    draw.text((cx - w // 2, cy - h // 2 - 3), lesson_text, font=font, fill=(50, 50, 50))


def compose_shrunk_photo(photo: Image.Image, text_side: str) -> Image.Image:
    background = photo.filter(ImageFilter.GaussianBlur(14))
    background = ImageEnhance.Brightness(background).enhance(1.15)
    background = ImageEnhance.Contrast(background).enhance(0.94).convert("RGBA")
    background = Image.alpha_composite(background, Image.new("RGBA", THUMBNAIL_SIZE, (255, 230, 205, 75)))

    if text_side == "right":
        photo_box = (15, 60, 990, 660)
    else:
        photo_box = (290, 60, 1265, 660)

    x1, y1, x2, y2 = photo_box
    photo_w = x2 - x1
    photo_h = y2 - y1
    resized = photo.resize((photo_w, photo_h), Image.Resampling.LANCZOS).convert("RGBA")

    shadow = Image.new("RGBA", THUMBNAIL_SIZE, (0, 0, 0, 0))
    ImageDraw.Draw(shadow).rounded_rectangle((x1 + 12, y1 + 15, x2 + 12, y2 + 15), radius=36, fill=(0, 0, 0, 65))
    background = Image.alpha_composite(background, shadow.filter(ImageFilter.GaussianBlur(10)))

    mask = Image.new("L", (photo_w, photo_h), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, photo_w, photo_h), radius=34, fill=255)
    background.paste(resized, (x1, y1), mask)

    ImageDraw.Draw(background).rounded_rectangle((x1 - 4, y1 - 4, x2 + 4, y2 + 4), radius=38, outline=(255, 255, 255, 240), width=7)
    return background


def draw_title_text(image: Image.Image, overlay: Image.Image, text: str | Iterable[str], side: str) -> None:
    draw = ImageDraw.Draw(overlay)
    title = text if isinstance(text, str) else "\n".join(str(line) for line in text)

    if side == "right":
        panel_box = (812, 195, 1248, 620)
        center_x = 1030
    else:
        panel_box = (35, 180, 500, 640) 
        center_x = 255

    draw_panel_cloud_gradient(image, overlay, panel_box)

    font, lines, spacing = fit_wrapped_text(
        draw,
        title,
        max_width=(panel_box[2] - panel_box[0]) - 110,
        max_height=(panel_box[3] - panel_box[1]) - 110,
        start_size=76,
        min_size=34,
        stroke=8,
    )

    palette = [
        (255, 105, 155, 255),
        (255, 165, 35, 255),
        (45, 155, 240, 255),
    ]
    
    line_heights = [text_size(draw, line or " ", font, 8)[1] for line in lines]
    total_h = sum(line_heights) + spacing * max(0, len(lines) - 1)
    y = panel_box[1] + ((panel_box[3] - panel_box[1]) - total_h) // 2 + 6
    
    for index, line in enumerate(lines):
        w, h = text_size(draw, line, font, 8)
        draw.text(
            (center_x - w // 2, y),
            line,
            font=font,
            fill=palette[index % len(palette)],
            stroke_width=8,
            stroke_fill=(255, 255, 255, 255),
        )
        y += h + spacing


def make_thumbnail_with_text(
    input_image: Path | str,
    output_image: Path | str,
    lesson_text: str,
    main_text: str | Iterable[str],
    text_side: str = "left",
    is_thumbnail = False
) -> Path:
    input_image = Path(input_image)
    output_image = Path(output_image)
    
    side = text_side.strip().lower()
    photo = Image.open(input_image).convert("RGB")
    photo = center_crop(photo, THUMBNAIL_SIZE)
    photo = ImageEnhance.Color(photo).enhance(1.16)
    photo = ImageEnhance.Brightness(photo).enhance(1.06)

    image = compose_shrunk_photo(photo, side)
    overlay = Image.new("RGBA", THUMBNAIL_SIZE, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    draw.rounded_rectangle((0, 0, 1279, 719), radius=0, fill=(255, 231, 187, 45))
    draw.rounded_rectangle((20, 25, 1260, 703), radius=45, outline=(255, 255, 255, 240), width=12)
    draw_dashed_rounded_rectangle(draw, (33, 38, 1248, 691), 36, (255, 215, 226, 230), dash=30, gap=14)

    for box in [(-70, 627, 205, 790), (400, 677, 650, 790), (1148, 680, 1365, 802)]:
        draw.ellipse(box, fill=(150, 220, 255, 120))
        draw.ellipse((box[0] - 70, box[1] + 24, box[2] - 135, box[3] + 42), fill=(255, 170, 210, 120))

    if is_thumbnail:
        draw_channel_badge(draw, "Easy English Conversation")
        
    draw_lesson_ribbon_gradient(image, overlay, lesson_text, side)
    draw_title_text(image, overlay, main_text, side)

    draw_star(draw, (107, 124), 42, (255, 211, 91, 255), (255, 255, 255, 255))
    draw_star(draw, (1160, 612), 31, (255, 210, 74, 255), (255, 255, 255, 245))
    draw_star(draw, (1060, 112), 25, (255, 210, 74, 255), (255, 255, 255, 245))
    draw_heart(draw, (1174, 82), 37, (247, 119, 180, 245), (255, 255, 255, 255))
    draw_heart(draw, (87, 396), 28, (247, 119, 180, 235), (255, 255, 255, 245))
    draw_heart(draw, (484, 640), 22, (247, 119, 180, 235), (255, 255, 255, 245))

    result = Image.alpha_composite(image, overlay)
    result = ImageEnhance.Sharpness(result.convert("RGB")).enhance(1.04)

    output_image.parent.mkdir(parents=True, exist_ok=True)
    result.save(output_image, quality=95)
    return output_image


# if __name__ == "__main__":
#     INPUT_PATH = r"thumbnail.png"  
#     OUTPUT_PATH = Path(__file__).with_name("thumbnail_vibrant_gradient.png")
    
#     saved = make_thumbnail_with_text(
#         input_image=INPUT_PATH,
#         output_image=OUTPUT_PATH,
#         lesson_text="Lesson 1:",
#         main_text="Making\nnew\nfriends",
#         text_side="left",
#         is_thumbnail=True
#     )
#     print(f"✨ Màu sắc đã lên chuẩn chỉnh và đậm đà! Ảnh mới lưu tại: {saved}")