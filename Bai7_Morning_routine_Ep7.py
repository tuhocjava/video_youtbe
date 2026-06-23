import os
import shutil
import subprocess
import textwrap
import asyncio
import cv2
import edge_tts
from PIL import Image, ImageDraw, ImageFont
from pydub import AudioSegment
from pathlib import Path
from seperate_overlay import detect_faces_and_overlay, split_people_direct
from create_sweet_heart_hook_advice import tao_anh_trai_tim_sticker_v4
from create_thumbnail_topic import make_thumbnail_with_text

BASE_DIR = "Ep7/output"
DOWNLOAD_DIR = "Ep7/download"

# =========================
# 1. Kịch bản hội thoại
# =========================
dialogues = [
("Lily", "Good morning, Noah! What do you usually do in the morning?", "Chào buổi sáng, Noah! Bạn thường làm gì vào buổi sáng?", "female"),
("Noah", "Good morning, Lily! I usually wake up early.", "Chào buổi sáng, Lily! Mình thường thức dậy sớm.", "male"),
("Lily", "That's great! What do you do after waking up?", "Tuyệt đấy! Bạn làm gì sau khi thức dậy?", "female"),
("Noah", "I clean up my bedroom and make my bed.", "Mình dọn dẹp phòng ngủ và gấp chăn gối gọn gàng.", "male"),
("Lily", "That is a good habit. I do the same every morning.", "Đó là một thói quen tốt. Mình cũng làm như vậy mỗi sáng.", "female"),
("Noah", "After that, I brush my teeth and wash my face.", "Sau đó, mình đánh răng và rửa mặt.", "male"),
("Lily", "I take care of my personal hygiene too.", "Mình cũng chăm sóc vệ sinh cá nhân như vậy.", "female"),
("Noah", "Then I go for a walk in the park near my house.", "Sau đó mình đi bộ trong công viên gần nhà.", "male"),
("Lily", "That sounds relaxing. Do you enjoy the fresh air?", "Nghe thật thư giãn. Bạn có thích tận hưởng không khí trong lành không?", "female"),
("Noah", "Yes! The fresh air makes me feel happy and energetic.", "Có chứ! Không khí trong lành làm mình cảm thấy vui vẻ và tràn đầy năng lượng.", "male"),
("Lily", "I love morning walks too. They help me start the day well.", "Mình cũng thích đi bộ buổi sáng. Nó giúp mình bắt đầu ngày mới thật tốt.", "female"),
("Noah", "After my walk, I have a healthy breakfast.", "Sau khi đi bộ, mình ăn một bữa sáng lành mạnh.", "male"),
("Lily", "Breakfast is important. It gives us energy for the day.", "Bữa sáng rất quan trọng. Nó cung cấp năng lượng cho cả ngày.", "female"),
("Noah", "That's right! After breakfast, I get ready for a new day.", "Đúng vậy! Sau bữa sáng, mình chuẩn bị sẵn sàng cho một ngày mới.", "male"),
("Lily", "Me too! A good morning routine makes every day better.", "Mình cũng vậy! Một thói quen buổi sáng tốt giúp mỗi ngày trở nên tuyệt vời hơn.", "female")
]


KICH_BAN = [
    {
        "nhan_vat": character,
        "thoai": dialogue,
        "translation": translation,
        "sex": sex,
        "audio_preview": f"{BASE_DIR}/audio/preview/voice{i}.mp3",
        "audio_repeat": f"{BASE_DIR}/audio/repeat/voice{i}.mp3",
    }
    for i, (character, dialogue, translation, sex) in enumerate(dialogues, start=1)
]

INTRO = "Chào mừng các bạn đã quay trở lại!\nChúc các bạn một ngày tốt lành.\nCùng bắt đầu nào!"
INTRO_EN = "Welcome back everyone!\nHave a wonderful day.\n Let's begin!"

hook_vi = "Thói quen buổi sáng của bạn là gì? Hãy nói thói quen buổi sáng của bạn bằng tiếng anh nhé"
hook_us = "What's your morning routine? Let's say it in English"

topic_vi = """Bài 7: Thói quen buổi sáng\n

Hôm nay bạn sẽ học:\n
Cách nói về các hoạt động buổi sáng hằng ngày bằng tiếng Anh.
"""
topic_us = """Lesson 7: Morning Routine\n
"""
topic_us_text= "You will learn:\n"
topic_us_main = """
How to talk about daily morning activities in English."""

lesson_text = "Lesson 7:"
main_text = "Morning Routine"
OUT_TRO = "Cám ơn các bạn đã xem hết video, nếu các bạn thấy hay, hãy nhấn nút Đăng ký để ủng hộ kênh và đón xem những video tiếp theo nhé. Cảm ơn các bạn rất nhiều!"

#Các câu nói quan trọng của bài:
important_saying_vi = "Đây là các câu trọng tâm của bài, các bạn ghi nhớ nhé."
important_saying_us = """
I usually wake up early.\n
I clean up my bedroom and make my bed.\n
I brush my teeth and wash my face.\n
I go for a walk in the park near my house.\n
I have a healthy breakfast.\n
Breakfast gives us energy for the day.\n
A good morning routine makes every day better.
"""

practice_vi = "Đây là mẫu bài luyện tập. Các bạn có thể dừng video để làm nhé"
practice_us = """
1. I usually ______ up early.
2. I ______ my bedroom and make my bed.
3. After that, I ______ my teeth and wash my face.
4. Then I go for a ______ in the park near my house.
5. After my walk, I have a ______ breakfast.
6. ______ is important. It gives us energy for the day.
7. A good morning ______ makes every day better.
"""

VOICE_MALE = "en-US-ChristopherNeural"
VOICE_FEMALE = "en-US-JennyNeural"

VOICE_VN_FEMALE = "vi-VN-HoaiMyNeural"
VOICE_VN_MALE = "vi-VN-NamMinhNeural"

FONT = ImageFont.truetype(r"C:/Windows/Fonts/arial.ttf", 30)
FONT_VI = ImageFont.truetype(r"C:/Windows/Fonts/arial.ttf", 20)

# =========================
# 2. Chuẩn bị thư mục
# =========================
dir_list = ["image", "image/preview", "image/repeat", "audio", "audio/preview", "audio/repeat",
            "scenes", "scenes/preview", "scenes/repeat", "videos"]
for d in dir_list:
    os.makedirs(f"{BASE_DIR}/{d}", exist_ok=True)

# =========================
# 3. Các hàm xử lý
# =========================

# Copy các ảnh base_scene/intro.txt/topic từ download/image vào ouput/image

files = ["base_scene.png", "background.png"]
for f in files:
    if not os.path.exists(f"{BASE_DIR}/image{f}"):
        shutil.copy(f"{DOWNLOAD_DIR}/image/{f}", f"{BASE_DIR}/image/{f}")
        resized = (Image.open(f"{BASE_DIR}/image/{f}")
                .resize((1280, 720))
                .save(f"{BASE_DIR}/image/{f}"))
        
        
async def create_tts_audio(
    file_out,
    vi_text=None,
    us_text=None,
    voice_vi=None,
    voice_us=None,
    vi_rate="+20%",
    us_rate="+0%",
    start_silence=500,
    between_silence=500,
    end_silence=1000,
    ting_path=None,
    ting_before_tick=False,
    is_hook = False
):
    if os.path.exists(file_out):
        return file_out

    temp_files = []

    try:
        final_audio = AudioSegment.silent(duration=start_silence)

        if vi_text:
            vi_file = file_out.replace(".mp3", "_vi.mp3")
            await edge_tts.Communicate(
                text=vi_text,
                voice=voice_vi or VOICE_VN_FEMALE,
                rate=vi_rate,
                pitch="+0Hz"
            ).save(vi_file)

            temp_files.append(vi_file)
            final_audio += AudioSegment.from_file(vi_file, format="mp3")
            final_audio += AudioSegment.silent(duration=between_silence)

        if us_text:
            lines = [
                line.strip()
                for line in str(us_text).replace("\\n", "\n").splitlines()
                if line.strip()
            ] if not is_hook else [str(us_text).replace("\n", " ").strip()]

            ting = None
            if ting_path and os.path.exists(ting_path):
                ting = AudioSegment.from_file(ting_path)

            for index, line in enumerate(lines):
                has_tick = line.startswith("✓")
                clean_line = line.replace("✓", "").strip()

                if ting_before_tick and has_tick and ting is not None:
                    final_audio += ting + AudioSegment.silent(duration=250)

                us_file = file_out.replace(".mp3", f"_us_{index}.mp3")
                await edge_tts.Communicate(
                    text=clean_line,
                    voice=voice_us or VOICE_FEMALE,
                    rate=us_rate,
                    pitch="+0Hz"
                ).save(us_file)

                temp_files.append(us_file)
                final_audio += AudioSegment.from_file(us_file, format="mp3")
                final_audio += AudioSegment.silent(duration=between_silence)

        final_audio += AudioSegment.silent(duration=end_silence)
        final_audio.export(file_out, format="mp3")

        return file_out

    except Exception as e:
        print(f"Lỗi tạo audio: {e}")
        return None

    finally:
        for f in temp_files:
            if os.path.exists(f):
                os.remove(f)

#Hàm tạo audio intro/outtro/practice

async def audio_intro_outtro_practice(text, file_out, is_practice=False):
    return await create_tts_audio(
        file_out=file_out,
        vi_text=text,
        vi_rate="+22%",
        start_silence=0,
        between_silence=0,
        end_silence=4000 if is_practice else 1000,
    )

# Hàm tạo advice

async def audio_advice(text_vi, text_us, file_out):
    return await create_tts_audio(
        file_out=file_out,
        vi_text=text_vi,
        us_text=text_us,
        vi_rate="+20%",
        us_rate="+0%",
        start_silence=500,
        between_silence=500,
        end_silence=500,
    )

# Hàm tạo audio topic/hook/important_saying

async def audio_topic_hook_importantSaying(topic_vi, topic_us, file_out, ting_path=None, is_importantSaying = False, is_hook = False):
    return await create_tts_audio(
        file_out=file_out,
        vi_text=topic_vi,
        us_text=topic_us,
        vi_rate="+20%",
        us_rate="+0%",
        start_silence=500,
        between_silence=100,
        end_silence=3000 if is_importantSaying else 800,
        ting_path=ting_path,
        ting_before_tick=True,
        is_hook=False
    )

# Hàm vẽ text lên ảnh:
def ve_text_wrap(img, text, font):
    draw = ImageDraw.Draw(img)

    # Giới hạn số ký tự mỗi dòng (tùy chỉnh theo độ rộng ảnh)
    wrapped_text = textwrap.fill(text, width=40)

    # Đo kích thước block text
    bbox = draw.multiline_textbbox((0, 0), wrapped_text, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]

    # Vị trí vẽ text (ví dụ: gần đáy ảnh)
    x = (img.width - text_w) // 2
    y = img.height - text_h - 30

    # Vẽ text với viền đen để nổi bật
    draw.multiline_text(
        (x, y),
        wrapped_text,
        font=font,
        fill="white",
        align="center",
        stroke_width=3,
        stroke_fill="black"
    )

# Hàm vẽ topic lên ảnh topic:
def draw_text_on_topic_ad(file_img, topic_us):
    # Vẽ topic lên ảnh:
    if os.path.exists(file_img):
        img = Image.open(file_img)
        ve_text_wrap(img, topic_us, FONT)
        img.save(file_img, quality=90)
    else:
        print("Ảnh topic chưa tồn tại")

async def audio_preview(scene):
    
    file_out = scene["audio_preview"]
    if os.path.exists(file_out):
        return file_out

    try:
        communicate = edge_tts.Communicate(
            text = scene["thoai"],
            voice = VOICE_FEMALE if scene["sex"] == "female"
            else VOICE_MALE,
            rate="+22%",
            pitch="+0Hz"
        )
        await communicate.save(file_out)
        
        audio = AudioSegment.from_mp3(file_out)
        silence = AudioSegment.silent(duration=500)  # 2000 ms = 2 giây
        audio = audio + silence
        audio.export(file_out, format="mp3")

        return file_out
    except Exception as e:
        print(f"Lỗi tạo Intro: {e}")
        return None

# Hàm lọc giọng: 
from pydub.effects import normalize

def enhance_voice(audio):
    audio = audio.high_pass_filter(80)

    # tăng nhẹ độ rõ
    audio = audio.high_pass_filter(80)
    audio = normalize(audio)

    # tăng âm lượng nhẹ
    audio += 2

    return audio

async def audio_repeat(phan):

    # Tạo audio tiếng Việt
    file_out = phan["audio_repeat"]
    if os.path.exists(file_out):
        return True

    # Lần 1: đọc nhanh tự nhiên
    fast_file = file_out.replace(".mp3", "_fast.mp3")
    await edge_tts.Communicate(
        text=phan["thoai"],
        voice=VOICE_FEMALE if phan["sex"] == "female" else VOICE_MALE,
        rate="+0%", pitch="+0Hz").save(fast_file)
    clip1 = AudioSegment.from_file(fast_file, format="mp3")
    clip1 = enhance_voice(clip1)

    # Lần 2:
    slow_file = file_out.replace(".mp3", "_slow.mp3")
    await edge_tts.Communicate(
        text=phan["thoai"],
        voice=VOICE_FEMALE if phan["sex"] == "female" else VOICE_MALE,
        rate="-5%", pitch="+0Hz").save(slow_file)
    clip2 = AudioSegment.from_file(slow_file, format="mp3")
    clip2 = enhance_voice(clip2)

    # Lần 3: đọc nhanh lại
    fast2_file = file_out.replace(".mp3", "_fast2.mp3")
    await edge_tts.Communicate(
        text=phan["thoai"],
        voice=VOICE_FEMALE if phan["sex"] == "female" else VOICE_MALE,
        rate="+0%", pitch="+0Hz").save(fast2_file)
    clip3 = AudioSegment.from_file(fast2_file, format="mp3")
    clip3 = enhance_voice(clip3)

    # Tạo đoạn silence 2 giây
    silence = AudioSegment.silent(duration= 1000)  # 2000 ms = 2 giây

    # Ghép audio: lần 1 + lần 2 + silence + lần 3
    final_audio = silence + clip1 + silence + clip2 + silence + clip3 + silence
    temp_files = [
        # vi_file,
        fast_file,
        slow_file,
        fast2_file
    ]

    try:
        final_audio.export(file_out, format="mp3")

    finally:
        for f in temp_files:
            if os.path.exists(f):
                os.remove(f)

    return file_out

def wrap_keep_newlines(text, width=30):
    lines = text.split("\n")

    wrapped_lines = [
        textwrap.fill(line.strip(), width=width)
        for line in lines
    ]

    return "\n".join(wrapped_lines)

def add_speech_bubble(base_image_path, output_path, text_us, scene, text_vi=None, show_vi=True):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    text_us = text_us or ""
    has_vi = show_vi and bool(text_vi)

    img = Image.open(base_image_path).convert("RGBA")
    draw = ImageDraw.Draw(img)

    font = ImageFont.truetype("arial.ttf", 30)

    wrapped_text = textwrap.fill(
        text_us,
        width = 40)
    
    bbox = draw.multiline_textbbox((0, 0), wrapped_text, font=font)

    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]

    if has_vi:
        font_vi = FONT_VI
        wrapped_vi = textwrap.fill(text_vi, width=45)
        
        bbox_vi = draw.multiline_textbbox((0, 0), wrapped_vi, font=font_vi)

        text_vi_w = bbox_vi[2] - bbox_vi[0]
        text_vi_h = bbox_vi[3] - bbox_vi[1]
    else:
        font_vi = None
        wrapped_vi = ""
        text_vi_w = 0
        text_vi_h = 0

    bubble_width = max(
        260,
        text_w + 60,
        text_vi_w + 60
    )

    if has_vi:
        bubble_height = max(120, text_h + text_vi_h + 60)
    else:
        bubble_height = max(90, text_h + 50)

    img_cv = cv2.imread(f"{BASE_DIR}/image/base_scene.png")

    if img_cv is not None:
        gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
        face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        )

        try:
            faces = face_cascade.detectMultiScale(gray, 1.1, 3)
        except Exception as e:
            print("Lỗi detectMultiScale:", e)
            faces = []

        faces = sorted(faces, key=lambda f: f[1])
    else:
        print("Không đọc được ảnh base_scene.png để dò khuôn mặt.")
        faces = []

    y = img.height - bubble_height - 600

    if scene["sex"] == "female" and len(faces) >= 1:
        a, b, w, h = faces[0]
        x = (a + img.width + w - bubble_width) / 2 + 100

    elif scene["sex"] == "male" and len(faces) >= 2:
        a, b, w, h = faces[1]
        x = (a - bubble_width) / 2 + 0 * w

    else:
        x = (img.width - bubble_width) / 2
        y = 40

    draw.rounded_rectangle(
        (
            x,
            y,
            x + bubble_width,
            y + bubble_height
        ),
        radius=20,
        fill="white",
        outline="blue",
        width=1
    )

    text_x = x + (bubble_width - text_w) / 2

    if has_vi:
        text_y = y + (bubble_height - text_h - text_vi_h - 20) / 2 - 5
    else:
        text_y = y + (bubble_height - text_h) / 2 - 5

    draw.multiline_text(
        (text_x, text_y),
        wrapped_text,
        font=font,
        fill="black",
        align="center"
    )

    if has_vi:
        vi_x = x + (bubble_width - text_vi_w) / 2
        vi_y = text_y + text_h + 20

        draw.multiline_text(
            (vi_x, vi_y),
            wrapped_vi,
            font=font_vi,
            fill=(0, 70, 220),
            align="center"
        )

    img.save(output_path)
    print(f"Saved {output_path}")

    return img

def draw_text_preview(base_image_path, output_path,text_vi, text_us):

    img = Image.open(base_image_path).convert("RGBA")
    draw = ImageDraw.Draw(img)


    # ==========================
    # Tự động xuống dòng
    # ==========================

    wrapped_text = textwrap.fill(
        text_us,
        width=50
    )

    bbox = draw.multiline_textbbox(
        (0, 0),
        wrapped_text,
        font=FONT
    )

    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]

    wrapped_vi = textwrap.fill(text_vi, width=55)  # Tiếng Việt có thể để width rộng hơn chút
    font_vi =FONT_VI  # Fon
    bbox_vi = draw.multiline_textbbox((0, 0), wrapped_vi, font=font_vi)
    text_vi_w = bbox_vi[2] - bbox_vi[0]
    text_vi_h = bbox_vi[3] - bbox_vi[1]

    # ==========================
    # Kích thước bong bóng
    # ==========================

    bubble_width = max(
        260,
        text_vi_w + 60, text_w +60
    )

    bubble_height = max(
        120,
        text_h + text_vi_h + 60
    )

    # ==========================
    # Bong bóng chính
    # ==========================
    x = (img.width - bubble_width)/2
    y = img.height - bubble_height - 30

    draw.rounded_rectangle(
        (
            x,
            y,
            x + bubble_width,
            y + bubble_height
        ),
        radius=20,
        fill="white" ,
        outline="blue",
        width=1
    )

    text_x = x + (bubble_width - text_w) / 2
    text_y = y + (bubble_height - text_h - text_vi_h) / 2 - 5

    # 2. Tính vị trí tiếng Việt dựa trên khối tiếng Anh
    # Chiều cao của khối tiếng Anh
    text_en_h = bbox[3] - bbox[1]

    # Tọa độ Y cho tiếng Việt = Y khối trên + chiều cao khối trên + khoảng cách
    vi_y = text_y + text_en_h + 20

    # Tọa độ X cho tiếng Việt:
    # Vì tiếng Việt có độ rộng khác, ta cần tính lại X để nó căn giữa bong bóng

    vi_x = x + (bubble_width - text_vi_w) / 2

    draw.multiline_text(
        (
            text_x,
            text_y

        ),
        wrapped_text,
        font=FONT,
        fill="black",
        align="center"
    )

    # 3. Vẽ tiếng Việt
    draw.multiline_text(
        (vi_x, vi_y), wrapped_vi, font=font_vi, fill=(0, 70, 220), align="center")

    img.save(output_path)

    print(f"Saved {output_path}")

    return img

def draw_text_importantSaying_practice(base_image_path, output_path, text_us):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    img = Image.open(base_image_path).convert("RGBA")
    draw = ImageDraw.Draw(img)

    # Giữ xuống dòng theo \n, dòng nào dài quá thì tự bẻ theo width
    wrapped_text = wrap_keep_newlines(text_us, width=35)

    bbox = draw.multiline_textbbox(
        (0, 0),
        wrapped_text,
        font=FONT,
        spacing=8
    )

    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]

    bubble_width = max(320, text_w + 60)
    bubble_height = max(120, text_h + 50)

    # Nằm giữa bên phải ảnh
    margin_right = 50
    x = img.width - bubble_width - margin_right
    y = (img.height - bubble_height) / 2

    draw.rounded_rectangle(
        (
            x,
            y,
            x + bubble_width,
            y + bubble_height
        ),
        radius=20,
        fill="white",
        outline="blue",
        width=1
    )

    # Text canh trái trong bong bóng
    padding_x = 30
    padding_y = 25

    text_x = x + padding_x
    text_y = y + padding_y

    draw.multiline_text(
        (text_x, text_y),
        wrapped_text,
        font=FONT,
        fill="black",
        align="left",
        spacing=8
    )

    img.save(output_path)
    print(f"Saved {output_path}")

    return img

async def all_preview_audio_imge():
    for i, scene in enumerate(KICH_BAN, start=1):

        await audio_preview(scene)

        output_image = f"{BASE_DIR}/image/preview/scene_{i}.png"

        if not os.path.exists(output_image):
            draw_text_preview(base_image_path=f"{BASE_DIR}/image/base_scene.png",
                output_path=output_image,
                text_vi=scene["translation"],
                text_us = scene["thoai"]
            )

async def all_repeat_image_and_audio():
    for i, scene in enumerate(KICH_BAN, start=1):

        await audio_repeat(scene)

        output_image = f"{BASE_DIR}/image/repeat/scene_{i}.png"

        if not os.path.exists(output_image):

            add_speech_bubble(
                base_image_path=f"{BASE_DIR}/image/male.png"
                if scene["sex"] == "male" else f"{BASE_DIR}/image/female.png",
                output_path=output_image,
                text_us=scene["thoai"],
                scene = scene,
                text_vi=scene["translation"]
            )

async def create_image_important_saying(text_vi, text_us):
    
    output_image = f"{BASE_DIR}/image/important_saying.png"
    if os.path.exists(output_image):
        return
    
    await audio_topic_hook_importantSaying(text_vi, text_us, output_image)
    
    draw_text_importantSaying_practice(f"{BASE_DIR}/image/female.png",
                                       output_path= output_image,
                                       text_us = text_us)

async def create_image_practice(text_us, text_vi):
    
    output_image = f"{BASE_DIR}/image/practice.png"
    
    if os.path.exists(output_image):
        return
    await audio_intro_outtro_practice(text_vi, f"{BASE_DIR}/audio/practice.mp3")
    
    draw_text_importantSaying_practice(base_image_path=f"{BASE_DIR}/image/female.png",
                                       output_path = output_image,
                                       text_us = text_us)

def run_ffmpeg(cmd):
    print(" ".join(cmd))
    subprocess.run(cmd, check=True)

def get_audio_duration(audio_path):
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", audio_path],
        capture_output=True, text=True
    )
    return float(result.stdout.strip())

def make_scene_video(image_path, audio_path, output_path):
    if os.path.exists(output_path):
        return

    run_ffmpeg([
        "ffmpeg", "-y",
        "-loop", "1",
        "-i", image_path,
        "-i", audio_path,
        "-shortest",

        "-c:v", "h264_qsv",
        "-global_quality", "28",

        "-c:a", "aac",
        "-pix_fmt", "yuv420p",

        output_path
    ])

def concat_videos(video_list, output):
    if os.path.exists(output):
        print(f"Skip {output}, already exists.")
        return

    list_file = os.path.join(BASE_DIR, "list.txt")

    with open(list_file, "w", encoding="utf-8") as f:
        for v in video_list:
            f.write(f"file '{os.path.abspath(v)}'\n")

    temp_output = output.replace(".mp4", "_temp.mp4")

    # Ghép video và tạo lại timestamp
    run_ffmpeg([
        "ffmpeg", "-y",
        "-fflags", "+genpts",
        "-avoid_negative_ts", "make_zero",
        "-f", "concat",
        "-safe", "0",
        "-i", list_file,

        "-c:v", "h264_qsv",
        "-global_quality", "28",

        "-c:a", "aac",
        "-b:a", "192k",

        temp_output
    ])

    duration = get_audio_duration(temp_output)

    fade_duration = 1.0

    # Thêm fade đầu/cuối
    run_ffmpeg([
        "ffmpeg", "-y",
        "-i", temp_output,

        "-vf",
        f"fade=t=in:st=0:d={fade_duration},"
        f"fade=t=out:st={max(0, duration-fade_duration)}:d={fade_duration}",

        "-c:v", "h264_qsv",
        "-global_quality", "28",

        "-c:a", "aac",
        "-b:a", "192k",

        output
    ])

    if os.path.exists(temp_output):
        os.remove(temp_output)

def creat_preview():
    previe_path = f"{BASE_DIR}/videos/preview.mp4"
    if os.path.exists(previe_path):
        print(f"Skip {previe_path}, already exists.")
        return

    scene_videos = [f"{BASE_DIR}/scenes/preview/scene_{i}.mp4" for i in range(1, len(KICH_BAN) + 1)]
    concat_videos(scene_videos, previe_path)

def create_main_video():

    main_path = f"{BASE_DIR}/videos/main.mp4"
    if os.path.exists(main_path):
        print(f"Skip {main_path}, already exists.")
        return

    scene_videos = [f"{BASE_DIR}/scenes/repeat/scene_{i}.mp4" for i in range(1, len(KICH_BAN)+1)]
    concat_videos(scene_videos, main_path)

def add_background_music(video, music, output):
    run_ffmpeg([
        "ffmpeg", "-y",
        "-i", video,
        "-stream_loop", "-1", "-i", music,   # lặp vô hạn nhạc nền
        "-filter_complex", "[1:a]volume=0.03[a1];[0:a][a1]amix=inputs=2:duration=first[a]",
        "-map", "0:v", "-map", "[a]",
        "-c:v", "copy", "-c:a", "aac",
        output
    ])

# =========================
# 4. Build video cuối
# =========================
async def build_final_video():
    intro_img = f"{BASE_DIR}/image/intro.png"
    topic_img = f"{BASE_DIR}/image/topic.png"
    hook_img = f"{BASE_DIR}/image/hook.png"
    ad_img1 = f"{BASE_DIR}/image/advice1.png"
    ad_img2 = f"{BASE_DIR}/image/advice2.png"
    
    practice_img = f"{BASE_DIR}/image/practice.png"
    importantSaying_img = f"{BASE_DIR}/image/important_saying.png"
    outtro_img = "for_youtube/logo_outtro/outtro.png"

    intro_audio = f"{BASE_DIR}/audio/intro.mp3"
    topic_audio = f"{BASE_DIR}/audio/topic.mp3"
    outtro_audio = f"{BASE_DIR}/audio/outtro.mp3"
    hook_audio = f"{BASE_DIR}/audio/hook.mp3"
    ad_audio1 = f"{BASE_DIR}/audio/ad_audio1.mp3"
    ad_audio2 = f"{BASE_DIR}/audio/ad_audio2.mp3"
    bg_music = "for_youtube/nhac_nen.mp3"
    practice_audio = f"{BASE_DIR}/audio/practice.mp3"
    importantSaying_audio = f"{BASE_DIR}/audio/important_saying.mp3"

    intro_video = f"{BASE_DIR}/videos/intro.mp4"
    topic_video = f"{BASE_DIR}/videos/topic.mp4"
    hook_video = f"{BASE_DIR}/videos/hook.mp4"
    ad_video1 = f"{BASE_DIR}/videos/ad_video1.mp4"
    ad_video2 = f"{BASE_DIR}/videos/ad_video2.mp4"
    practice_video = f"{BASE_DIR}/videos/practice.mp4"
    importantSaying_video = f"{BASE_DIR}/videos/important_saying.mp4"

    preview_video = f"{BASE_DIR}/videos/preview.mp4"
    main_video  = f"{BASE_DIR}/videos/main.mp4"
    outtro_video = f"{BASE_DIR}/videos/outtro.mp4"
    final_video = f"{BASE_DIR}/videos/final_video.mp4"
    final_with_music = f"{BASE_DIR}/videos/final_with_music.mp4"

    # Tạo intro.txt/topic/outtro
    if not (os.path.exists(intro_video)
            and os.path.exists(topic_video)
            and os.path.exists(hook_video)
            and os.path.exists(ad_video1)
            and os.path.exists(ad_video2)
            and os.path.exists(outtro_video)
            and os.path.exists(practice_video)
            and os.path.exists(importantSaying_video)):
        make_scene_video(intro_img, intro_audio, intro_video)
        make_scene_video(hook_img, hook_audio, hook_video)
        make_scene_video(ad_img1, ad_audio1, ad_video1)
        make_scene_video(ad_img2, ad_audio2, ad_video2)
        make_scene_video(topic_img, topic_audio, topic_video)
        make_scene_video(outtro_img, outtro_audio, outtro_video)
        make_scene_video(practice_img, practice_audio, practice_video)
        make_scene_video(importantSaying_img, importantSaying_audio, importantSaying_video)

    # Tạo main.mp4
    print("Tạo repeat video")
    create_main_video()
    print("Đã tạo xong repeat video\n")

    # Ghép intro.txt + topic + main + outtro
    print("Ghép toàn bộ video")
    concat_videos(
        [intro_video,
                 hook_video,
                 topic_video,
                 ad_video1,
                 preview_video,
                 ad_video2,
                 main_video,
                 importantSaying_video,
                 practice_video,
                 outtro_video], final_video)
    print("Đã ghép xong video")

    # Thêm nhạc nền
    print("Ghép nhạc")
    add_background_music(final_video, bg_music, final_with_music)

    print("✅ Final video created:", final_with_music)

# =========================
# 5. Main
# =========================
async def main():
    # Tạo ảnh thumbnail
    print("---Thumbnail----")
    
    # Nọi dung thumbnail: Easy English Conversation #04 | First Day at School
    make_thumbnail_with_text(
    input_image = Path(f'{BASE_DIR}/image/base_scene.png'),
    output_image = Path(f"{BASE_DIR}/image/thumbnail.png"),
    lesson_text = lesson_text,
    main_text = main_text,
    text_side = "left",
    is_thumbnail=True)
    
    print("Đã tạo xong ảnh thumbnail.\n")
    
    # Tách ảnh base_scene thành 2 ảnh male và female:
    print("---Tách và tạo ảnh male.png và feemale.png----")
    female_path = f"{BASE_DIR}/image/female.png"
    male_path = f"{BASE_DIR}/image/male.png"

    if os.path.exists(female_path) and os.path.exists(male_path):
        print("Đã tách và ghép nhân vật rồi, bỏ qua bước này.")
    else:
        people_paths = split_people_direct(
            f"{BASE_DIR}/image/base_scene.png",
            f"{BASE_DIR}/image/"
        )

        detect_faces_and_overlay(
            f"{BASE_DIR}/image/background.png",
            people_paths,
            f"{BASE_DIR}/image/"
        )
        print("Đã tách ảnh xong.\n")
        
    # Tạo audio intro.txt/topic/outtro/hook
    print("----AUDIO----")
    #Intro
    print("Tạo audio intro")
    await audio_intro_outtro_practice(INTRO, f"{BASE_DIR}/audio/intro.mp3")
    print("Đã tạo audio intro.\n")
    
    # Tạo ảnh iNtro
    print("Tạo ảnh intro")
    tao_anh_trai_tim_sticker_v4(Path(f"{BASE_DIR}/image/female.png"),
                                     Path(f"{BASE_DIR}/image/intro.png"),
                                     INTRO_EN,
                                     "right_center")
    print("Tạo xong ảnh intro\n")

    #Hook
    # Tạo hook audio
    await audio_topic_hook_importantSaying(hook_vi, hook_us, f"{BASE_DIR}/audio/hook.mp3", is_hook=True)
    
    # Tạo ảnh hook
    print("Tạo ảnh hook")
    tao_anh_trai_tim_sticker_v4(Path(f"{BASE_DIR}/image/female.png"),
                                     Path(f"{BASE_DIR}/image/hook.png"),
                                     hook_us,
                                     "right_center")
    print("Tạo xong ảnh intro\n")
    
    #Topic
    print("Tạo audio Topic")
    await audio_topic_hook_importantSaying(topic_vi,
                                       topic_us + topic_us_text + topic_us_main, 
                                       f"{BASE_DIR}/audio/topic.mp3",
                                       )
    
    
    print("Tạo ảnh topic")
    if not os.path.exists(f'{BASE_DIR}/image/topic.png'):
       make_thumbnail_with_text(
            input_image = Path(f'{BASE_DIR}/image/base_scene.png'),
            output_image = Path(f"{BASE_DIR}/image/topic.png"),
            lesson_text = topic_us_text,
            main_text = topic_us_main,
            text_side = "right")
    print("Đã vẽ text lên topic.\n")
    
    # Tạo audio các câu nói trọng tâm bài học:
    print("Tạo audio các câu nói trọng tâm bài")
    await audio_topic_hook_importantSaying(important_saying_vi,
                                           important_saying_us,
                                           f"{BASE_DIR}/audio/important_saying.mp3",
                                           is_importantSaying=True)
    # Tạo ảnh các câu nói trọng tâm bài học
    print("Tạo ảnh các câu nói trọng tâm trong bài")
    await create_image_important_saying(important_saying_vi, important_saying_us)
    
    # Tạo audio luyện tập:
    
    print("Tạo audio practice")
    await audio_intro_outtro_practice(practice_vi,
                                           f"{BASE_DIR}/audio/practice.mp3",
                                           is_practice=True)
    # Tạo ảnh chèn nội dung luyện tập:(nên lấy ảnh cô gái và chèn bong bóng bình thường)
    print("Tạo ảnh practice")
    await create_image_practice(practice_us, practice_vi)
    print("Đã tạo xong ảnh practice\n")

    #Outtro
    await audio_intro_outtro_practice(OUT_TRO, f"{BASE_DIR}/audio/outtro.mp3")

    #Listen_carefully
    ad_vi1 = "Lắng nghe thật kĩ nhé"
    ad_us1 = "Listen carefully"

    await audio_advice(ad_vi1, ad_us1, f"{BASE_DIR}/audio/ad_audio1.mp3")

    # Listen and repeat:
    ad_vi2 = "Lắng nghe và lặp lại theo mình nhé"
    ad_us2 = "Listen and repeat"

    await audio_advice(ad_vi2, ad_us2, f"{BASE_DIR}/audio/ad_audio2.mp3")
    

    print("Tạo ảnh advice")

    if not os.path.exists(f"{BASE_DIR}/image/advice.png"):
        shutil.copy(f"{BASE_DIR}/image/female.png", f"{BASE_DIR}/image/advice.png")

    tao_anh_trai_tim_sticker_v4(Path(f"{BASE_DIR}/image/advice.png"),
                                     Path(f"{BASE_DIR}/image/advice1.png"),
                                     ad_us1,
                                     "right_center")
    tao_anh_trai_tim_sticker_v4(Path(f"{BASE_DIR}/image/advice.png"),
                                     Path(f"{BASE_DIR}/image/advice2.png"),
                                     ad_us2,
                                     "right_center")
    print("Đã tạo ảnh advice1 và advice2")


    # Tạo ảnh preview và repeat:
    print("Tạo ảnh privew và repeat")
    await all_preview_audio_imge()
    await all_repeat_image_and_audio()
    print("Đã tạo xong ảnh privew và repeat\n")
    
    print("----SCENES----")
    # giả sử audio + image đã được tạo trước
    print("Tạo secne")
    for i, scene in enumerate(KICH_BAN, start=1):
        make_scene_video(f"{BASE_DIR}/image/preview/scene_{i}.png", scene["audio_preview"], f"{BASE_DIR}/scenes/preview/scene_{i}.mp4")

        make_scene_video(f"{BASE_DIR}/image/repeat/scene_{i}.png", scene["audio_repeat"], f"{BASE_DIR}/scenes/repeat/scene_{i}.mp4")

    print("Đã tạo toàn bộ scene\n")
    #Tao preview

    print("---Preview video---")
    creat_preview()
    print("Đã tạo xong preview video")
    
    print("----FINAL VIDEO----")
    await build_final_video()
    print("DONE")

if __name__ == "__main__":
    asyncio.run(main())
