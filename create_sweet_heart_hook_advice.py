import math
from pathlib import Path
from typing import Literal
from PIL import Image, ImageDraw, ImageFilter, ImageFont

# Khai báo các vị trí bong bóng hỗ trợ
BubblePosition = Literal["right_top", "right_center", "right_bottom", "left_top", "left_center", "left_bottom", "bottom_center", "center_center"]

def load_font(size: int, bold: bool = True) -> ImageFont.FreeTypeFont:
    """Tự động quét tìm font chữ phù hợp trên hệ thống"""
    candidates = [
        r"C:\Windows\Fonts\comicbd.ttf" if bold else r"C:\Windows\Fonts\comic.ttf",
        r"C:\Windows\Fonts\arialbd.ttf" if bold else r"C:\Windows\Fonts\arial.ttf",
    ]
    for font_path in candidates:
        if Path(font_path).exists():
            return ImageFont.truetype(font_path, size=size)
    return ImageFont.load_default()

def get_heart_path(cx: float, cy: float, size: float) -> list[tuple[float, float]]:
    """Tạo đường cong trái tim toán học mượt mà không răng cưa"""
    points = []
    for i in range(0, 361, 1):
        t = math.radians(i)
        x = 16 * (math.sin(t) ** 3)
        y = 13 * math.cos(t) - 5 * math.cos(2*t) - 2 * math.cos(3*t) - math.cos(4*t)
        px = cx + x * (size / 16)
        py = cy - y * (size / 16)
        points.append((px, py))
    return points

def ve_ngoi_sao_lap_lanh(draw: ImageDraw.ImageDraw, x: float, y: float, r: float, color, outline_color):
    points = []
    for i in range(10):
        angle = math.radians(-90 + i * 36)
        curr_r = r if i % 2 == 0 else r * 0.4
        points.append((x + math.cos(angle) * curr_r, y + math.sin(angle) * curr_r))
    draw.polygon(points, fill=color, outline=outline_color, width=2)

def ve_lap_lanh_4_cánh(draw: ImageDraw.ImageDraw, cx: float, cy: float, r: float, color):
    pts = [
        (cx, cy - r), (cx + r*0.2, cy - r*0.2), (cx + r, cy), (cx + r*0.2, cy + r*0.2),
        (cx, cy + r), (cx - r*0.2, cy + r*0.2), (cx - r, cy), (cx - r*0.2, cy - r*0.2)
    ]
    draw.polygon(pts, fill=color, outline=(255, 255, 255, 255), width=1)

def ve_hao_quang_toa_sang(draw: ImageDraw.ImageDraw, cx: float, cy: float, heart_scale: float):
    """Vẽ các tia hào quang phát sáng tỏa ra từ tâm trái tim"""
    for angle_deg in range(0, 360, 30):
        angle = math.radians(angle_deg)
        start_dist = heart_scale * 1.12
        end_dist = heart_scale * 1.34
        
        x1 = int(cx + math.cos(angle) * start_dist)
        y1 = int(cy + math.sin(angle) * start_dist)
        x2 = int(cx + math.cos(angle) * end_dist)
        y2 = int(cy + math.sin(angle) * end_dist)
        
        draw.line((x1, y1, x2, y2), fill=(200, 240, 255, 160), width=4)
        draw.line((x1, y1, int(x1 + (x2-x1)*0.6), int(y1 + (y2-y1)*0.6)), fill=(255, 255, 255, 220), width=2)

def tinh_tam_trai_tim(image_w: int, image_h: int, heart_size: float, position: BubblePosition, margin: int = 40) -> tuple[float, float]:
    """Tính toán tọa độ tâm (cx, cy) của trái tim dựa vào tham số position truyền vào"""
    safe_margin_x = max(margin, heart_size * 1.1)
    safe_margin_y = max(margin, heart_size * 1.1)

    # Tính toán trục X
    if position.startswith("left"):
        cx = safe_margin_x
    elif position.startswith("right"):
        cx = image_w - safe_margin_x
    else: 
        cx = image_w / 2

    # Tính toán trục Y
    if position.endswith("top"):
        cy = safe_margin_y
    elif position.endswith("bottom"):
        cy = image_h - safe_margin_y
    elif position.endswith("center") and not position.startswith("center"): 
        if position.startswith("bottom"):
            cy = image_h - safe_margin_y
        else:
            cy = image_h / 2
    else: 
        cy = image_h / 2

    return cx, cy

from PIL import ImageDraw

def wrap_text_by_pixel_width(draw, text, font, max_width):

    result_lines = []

    # Giữ nguyên các dòng do người dùng nhập
    paragraphs = text.replace("\\n", "\n").split("\n")

    for paragraph in paragraphs:

        if not paragraph.strip():
            result_lines.append("")
            continue

        words = paragraph.split()
        current_line = ""

        for word in words:

            test_line = word if not current_line else current_line + " " + word

            bbox = draw.textbbox((0, 0), test_line, font=font)
            line_width = bbox[2] - bbox[0]

            if line_width <= max_width:
                current_line = test_line
            else:
                if current_line:
                    result_lines.append(current_line)

                current_line = word

        if current_line:
            result_lines.append(current_line)

    return result_lines

def tao_anh_trai_tim_sticker_v4(
    path_anh_goc: str, 
    path_anh_ket_qua: str, 
    text_noi_dung: str, 
    position: BubblePosition = "right_top",
    font_size: int = 36
):
    base_img = Image.open(path_anh_goc).convert("RGBA")
    overlay = Image.new("RGBA", base_img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    font = load_font(font_size, bold=True)
    
    # -------------------------------------------------------------
    # BƯỚC 1: XỬ LÝ TEXT (CHỈ WRAP KHI CÓ DẤU \n)
    # -------------------------------------------------------------
    # lines = text_noi_dung.replace("\\n", "\n").split('\n')
    
    lines = wrap_text_by_pixel_width(
    draw,
    text_noi_dung,
    font,
    max_width=500
)

    line_widths = []
    line_heights = []
    for l in lines:
        bb = draw.textbbox((0, 0), l or " ", font=font)
        line_widths.append(bb[2] - bb[0])
        line_heights.append(bb[3] - bb[1])
        
    actual_max_w = max(line_widths) if line_widths else 50
    total_text_h = sum(line_heights) + (len(lines) - 1) * 10

    # 🌟 ĐIỀU CHỈNH ĐỘ PHÌNH TO: Thu gọn hệ số nhân từ 0.85 xuống 0.65 để trái tim ôm sát text hơn
    heart_scale = max(actual_max_w * 0.65, total_text_h * 0.85, 100)
    
    # Khoảng đệm nhỏ vừa vặn, giúp trái tim không bị phình quá lớn
    heart_scale += 20 

    # -------------------------------------------------------------
    # BƯỚC 2: TỰ ĐỘNG ĐỊNH VỊ (POSITIONING SYSTEM)
    # -------------------------------------------------------------
    cx, cy = tinh_tam_trai_tim(base_img.width, base_img.height, heart_scale, position)

    # -------------------------------------------------------------
    # BƯỚC 3: VẼ ÁNH HÀO QUANG TOẢ SÁNG (GLOW RAYS)
    # -------------------------------------------------------------
    ve_hao_quang_toa_sang(draw, cx, cy, heart_scale)

    # -------------------------------------------------------------
    # BƯỚC 4: PHỐI LAYER MÀU TRÁI TIM (BLUE-PINK PASTEL)
    # -------------------------------------------------------------
    shadow_layer = Image.new("RGBA", base_img.size, (0, 0, 0, 0))
    s_draw = ImageDraw.Draw(shadow_layer)
    s_draw.polygon(get_heart_path(cx + 6, cy + 10, heart_scale), fill=(0, 0, 0, 30))
    overlay.alpha_composite(shadow_layer.filter(ImageFilter.GaussianBlur(12)))

    blue_pink_gradient = [
        (160, 215, 255, 120),  # Rìa ngoài xanh sky blue
        (180, 235, 255, 150),  # Xanh ngọc Cyan ngọt ngào
        (215, 210, 255, 180),  # Tím xanh dịu mát
        (255, 195, 230, 200),  # Hồng pastel kẹo bông
        (255, 220, 240, 235),  # Hồng mọng nước sáng
        (245, 245, 255, 255),  # Tâm sáng trắng ánh xanh
    ]

    num_steps = len(blue_pink_gradient)
    for idx, color in enumerate(blue_pink_gradient):
        current_scale = heart_scale * (1.0 - (idx * (0.16 / num_steps)))
        pts = get_heart_path(cx, cy, current_scale)
        draw.polygon(pts, fill=color)

    draw.polygon(get_heart_path(cx, cy, heart_scale + 2), outline=(255, 255, 255, 240), width=5)
    draw.polygon(get_heart_path(cx, cy, heart_scale - 4), outline=(135, 206, 250, 110), width=2)

    # -------------------------------------------------------------
    # BƯỚC 5: THÊM CÁC STICKER VÀ TRANG TRÍ XUNG QUANH TRÁI TIM
    # -------------------------------------------------------------
    ve_ngoi_sao_lap_lanh(draw, cx - heart_scale * 0.85, cy - heart_scale * 0.55, 16, (255, 240, 150, 255), (255, 255, 255, 255))
    
    bx1, by1 = int(cx + heart_scale * 0.8 - 12), int(cy - heart_scale * 0.6 - 12)
    bx2, by2 = int(cx + heart_scale * 0.8 + 12), int(cy - heart_scale * 0.6 + 12)
    draw.ellipse((bx1, by1, bx2, by2), fill=(150, 220, 255, 200), outline=(255, 255, 255, 255), width=2)
    
    bx3, by3 = int(cx + heart_scale * 0.92 - 6), int(cy - heart_scale * 0.45 - 6)
    bx4, by4 = int(cx + heart_scale * 0.92 + 6), int(cy - heart_scale * 0.45 + 6)
    draw.ellipse((bx3, by3, bx4, by4), fill=(175, 240, 255, 180), outline=(255, 255, 255, 255), width=1)
    
    ve_lap_lanh_4_cánh(draw, cx + heart_scale * 0.82, cy + heart_scale * 0.6, 12, (160, 220, 255, 255))
    ve_lap_lanh_4_cánh(draw, cx + heart_scale * 0.65, cy + heart_scale * 0.8, 10, (255, 185, 215, 255))
    ve_lap_lanh_4_cánh(draw, cx - heart_scale * 0.7, cy + heart_scale * 0.7, 11, (180, 255, 220, 255))
    ve_lap_lanh_4_cánh(draw, cx - heart_scale * 0.95, cy + heart_scale * 0.1, 13, (255, 235, 165, 255))

    # -------------------------------------------------------------
    # BƯỚC 6: IN CHỮ MÀU ĐEN VIỀN TRẮNG RÕ NÉT (NHÍCH LÊN TRÊN TÂM)
    # -------------------------------------------------------------
    # Trừ đi một khoảng (heart_scale * 0.08) để đẩy khối văn bản nhích lên phía trên
    start_y = cy - (total_text_h / 2) - (heart_scale * 0.08)
    
    curr_y = start_y
    for line, h in zip(lines, line_heights):
        if not line:
            curr_y += h + 10
            continue
        bb = draw.textbbox((0, 0), line, font=font)
        line_w = bb[2] - bb[0]
        x_pos = cx - (line_w / 2)
        
        draw.text(
            (x_pos, curr_y), 
            line, 
            font=font, 
            fill=(0, 0, 0, 255),       
            stroke_width=4,            
            stroke_fill=(255, 255, 255, 255)
        )
        curr_y += h + 10

    # Hợp nhất layer vẽ nghệ thuật lên ảnh gốc
    final_img = Image.alpha_composite(base_img, overlay).convert("RGB")
    final_img.save(path_anh_ket_qua, quality=95)
    print(f"🚀 Hoàn tất! Trái tim bóp gọn vừa vặn, chữ nhích lên trên đẹp mắt: {path_anh_ket_qua}")


# # --- KHU VỰC CHẠY KIỂM THỬ ---
# if __name__ == "__main__":
#     ANH_GOC = "thumbnail.png" 
#     ANH_XUAT = "output_perfect_balanced_heart.jpg"
    
#     TEXT_TEST = "Have you made any\nfriends on your first day\nat the new school\n Than you very much?"
#     VITRI = "left_bottom"
    
#     tao_anh_trai_tim_sticker_v4(ANH_GOC, ANH_XUAT, TEXT_TEST, position=VITRI, font_size=36)