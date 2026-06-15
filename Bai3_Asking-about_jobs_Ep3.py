import os
import shutil
import subprocess
import textwrap
import asyncio
import cv2
import edge_tts
from PIL import Image, ImageDraw, ImageFont
from pydub import AudioSegment

BASE_DIR = "Ep3/output"
DOWNLOAD_DIR = "Ep3/download"

# Chuyển watermark  thành nền trong suốt và resize 250x250 và đổi tên thành logo

if not os.path.exists("for_youtube/logo_outtro/wartermark.png"):
    # Mở ảnh tạo từ chatGPT
    img = (Image
           .open("for_youtube/logo_outtro/ChatGPT Image 08_41_18 9 thg 6, 2026.png")
           .convert("RGBA")
           .resize((250, 250)))

    new_data = []

    for item in img.getdata():
        # Nếu pixel gần màu trắng thì chuyển thành trong suốt
        if item[0] > 240 and item[1] > 240 and item[2] > 240:
            new_data.append((255, 255, 255, 0))
        else:
            new_data.append(item)

    img.putdata(new_data)

    # Lưu ảnh PNG nền trong suốt
    img.save("for_youtube/logo_outtro/wartermark.png")

    print("WATREMARK: Done!")

# Chuyển logo thành nền trong suốt và resize 800x800 và đổi tên thành logo

if not os.path.exists("for_youtube/logo_outtro/logo.png"):
    # Mở ảnh tạo từ chatGPT
    img = (Image
           .open("for_youtube/logo_outtro/ChatGPT Image 07_37_09 9 thg 6, 2026.png")
           .convert("RGBA")
           .resize((800, 800)))

    new_data = []

    for item in img.getdata():
        # Nếu pixel gần màu trắng thì chuyển thành trong suốt
        if item[0] > 240 and item[1] > 240 and item[2] > 240:
            new_data.append((255, 255, 255, 0))
        else:
            new_data.append(item)

    img.putdata(new_data)

    # Lưu ảnh PNG nền trong suốt
    img.save("for_youtube/logo_outtro/logo.png")

    print("LOGO: Done!")

# Resize outtro về kích thước 1280x720
if not os.path.exists("for_youtube/logo_outtro/outtro.png"):
    outtro = (Image
              .open("for_youtube/logo_outtro/ChatGPT Image 07_41_09 9 thg 6, 2026.png")
              .resize((1280, 720))
              .save("for_youtube/logo_outtro/outtro.png"))
print("OUTTRO: Done!")

# =========================
# 1. Kịch bản hội thoại
# =========================
dialogues = [
    ("Susan", "Hi Paul, how are you today?", "Chào Paul, hôm nay bạn khỏe không?", "female"),
    ("Paul", "I’m good, thanks. How about you?", "Mình khỏe, cảm ơn. Còn bạn thì sao?", "male"),
    ("Susan", "I’m fine too. By the way, can I ask you something?", "Mình cũng khỏe. Nhân tiện, mình có thể hỏi bạn một điều không?", "female"),
    ("Paul", "Sure, go ahead.", "Được chứ, bạn cứ hỏi.", "male"),
    ("Susan", "What does your dad do?", "Ba bạn làm nghề gì vậy?", "female"),
    ("Paul", "My dad is a mechanic. He fixes cars in a garage.", "Ba mình là thợ sửa xe. Ông sửa ô tô ở một gara.", "male"),
    ("Susan", "That’s cool. He must be very good with machines.", "Hay quá. Chắc ba bạn rất giỏi về máy móc.", "female"),
    ("Paul", "Yes, he really enjoys his work. How about your mom?", "Đúng vậy, ông rất thích công việc của mình. Còn mẹ bạn thì sao?", "male"),
    ("Susan", "My mom is a teacher. She teaches math at a middle school.", "Mẹ mình là giáo viên. Bà dạy toán ở một trường trung học cơ sở.", "female"),
    ("Paul", "Wow, teaching math sounds difficult but important.", "Ồ, dạy toán nghe khó nhưng rất quan trọng.", "male"),
    ("Susan", "Yes, sometimes it’s hard, but she loves helping students learn.", "Đúng vậy, đôi khi khá khó, nhưng mẹ mình rất thích giúp học sinh học tập.", "female"),
    ("Paul", "That’s great. And what about your dad?", "Tuyệt quá. Thế còn ba bạn thì sao?", "male"),
    ("Susan", "My dad is a farmer. He grows rice and vegetables.", "Ba mình là nông dân. Ông trồng lúa và rau.", "female"),
    ("Paul", "Nice! So both of our parents work hard in different ways.", "Hay thật! Vậy là ba mẹ chúng ta đều làm việc chăm chỉ theo những cách khác nhau.", "male")
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

INTRO = "Chào mừng các bạn đã quay trở lại!\nRất vui được ở đây cùng các bạn.\nChúc các bạn có một ngày thật tốt lành.\nCùng bắt đầu nào!"
hook_vi = "Ba mẹ bạn làm nghề gì? bạn đã từng hỏi bạn bè câu hỏi này bằng tiếng anh chưa?"
hook_us = "What jobs do your parents do? Have you ever asked your friends this question in English?"
topic_vi = "Bài 3: Hỏi về nghề nghiệp"
topic_us = "Lesson 3: Asking about jobs"
OUT_TRO = "Cám ơn các bạn đã xem hết video, nếu các bạn thấy hay, hãy nhấn nút Đăng ký để ủng hộ kênh và đón xem những video tiếp theo nhé. Cảm ơn các bạn rất nhiều!"

# VOICE_MALE = "en-GB-RyanNeural"
VOICE_MALE = "en-US-ChristopherNeural"
VOICE_FEMALE = "en-US-JennyNeural"

VOICE_VN_FEMALE = "vi-VN-HoaiMyNeural"
VOICE_VN_MALE = "vi-VN-NamMinhNeural"

FONT = ImageFont.truetype("arialbd.ttf", 36)

# =========================
# 2. Chuẩn bị thư mục
# =========================
os.makedirs(f"{BASE_DIR}/image", exist_ok=True)
os.makedirs(f"{BASE_DIR}/image/preview", exist_ok=True)
os.makedirs(f"{BASE_DIR}/image/repeat", exist_ok=True)
os.makedirs(f"{BASE_DIR}/audio", exist_ok=True)
os.makedirs(f"{BASE_DIR}/audio/preview", exist_ok=True)
os.makedirs(f"{BASE_DIR}/audio/repeat", exist_ok=True)
os.makedirs(f"{BASE_DIR}/scenes", exist_ok=True)
os.makedirs(f"{BASE_DIR}/scenes/preview", exist_ok=True)
os.makedirs(f"{BASE_DIR}/scenes/repeat", exist_ok=True)
os.makedirs(f"{BASE_DIR}/videos", exist_ok=True)

# =========================
# 3. Các hàm xử lý
# =========================

# Copy các ảnh base_scene/intro.txt/topic từ download/image vào ouput/image

if not (os.path.exists(f"{BASE_DIR}/image/base_scene.png")
        and os.path.exists(f"{BASE_DIR}/image/intro.png")
        and  os.path.exists(f"{BASE_DIR}/image/topic.png")
        and os.path.exists(f"{BASE_DIR}/image/female.png")
        and os.path.exists(f"{BASE_DIR}/image/male.png")
        and os.path.exists(f"{BASE_DIR}/image/hook.png")
        and os.path.exists(f"{BASE_DIR}/image/advice.png")
):
    downloads = ["base_scene.png", "intro.png", "topic.png", "female.png", "male.png", "hook.png", "advice.png"]
    for f in downloads:
        shutil.copy(f"{DOWNLOAD_DIR}/image/{f}", f"{BASE_DIR}/image/{f}")
        resized = (Image.open(f"{BASE_DIR}/image/{f}")
              .resize((1280, 720))
              .save(f"{BASE_DIR}/image/{f}"))

# Hàm tạo audio intro-outtro
async def audio_intro_outtro_hook(text, file_out):
    if os.path.exists(file_out):
        return file_out
    try:
        communicate = edge_tts.Communicate(
            text = text,
            voice = VOICE_VN_FEMALE,
            rate="+22%",
            pitch="+0Hz"
        )
        await communicate.save(file_out)
        # Thêm 2 giây im lặng
        audio = AudioSegment.from_mp3(file_out)
        silence = AudioSegment.silent(duration=300)  # 2000 ms = 2 giây
        audio = audio + silence
        audio.export(file_out, format="mp3")

        return file_out
    except Exception as e:
        print(f"Lỗi tạo Intro: {e}")
        return None

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

# Hàm tạo audio giới thiệu đề tài:
async def audio_topic(topic_vi, topic_us, file_out):
    if os.path.exists(file_out):
        return file_out

    file_vi = file_out.replace(".mp3", "_vi.mp3")
    try:
        communicate = edge_tts.Communicate(
            text = topic_vi,
            voice = VOICE_VN_FEMALE,
            rate="+20%",
            pitch="+0Hz"
        )
        await communicate.save(file_vi)

    except Exception as e:
        print(f"Lỗi tạo tiếng Việt cho topic: ")
        print(f"{e}")
        return None

    clip_vi = AudioSegment.from_file(file_vi, format="mp3")

    file_us = file_out.replace(".mp3", "_us.mp3")
    try:
        communicate = edge_tts.Communicate(
            text = topic_us,
            voice = VOICE_FEMALE,
            rate="+0%",
            pitch="+0Hz"
        )
        await communicate.save(file_us)
    except Exception as e:
        print(f"Lỗi tạo tiếng Anh cho topic: ")
        print(f"{e}")
        return None

    clip_us = AudioSegment.from_file(file_us, format="mp3")

    silence = AudioSegment.silent(duration=200)  # 2000 ms = 2 giây

    # Ghép audio: lần 1 + lần 2
    final_audio = silence + clip_vi + silence+ clip_us + silence
    temp_files = [
        file_vi,
        file_us,
    ]

    try:
        final_audio.export(file_out, format="mp3")

    finally:
        for f in temp_files:
            if os.path.exists(f):
                os.remove(f)

    return file_out

# Hàm vẽ topic lên ảnh topic:
def draw_text_on_topic_ad(file_img, topic_us):
    # Vẽ topic lên ảnh:
    img = Image.open(file_img)
    ve_text_wrap(img, topic_us, FONT)
    img.save(file_img, quality=90)

async def audio_listen_advice(text_vi, text_us, file_out):
    if os.path.exists(file_out):
        return file_out

    vi_file = file_out.replace(".mp3", "_vi.mp3")
    try:
        communicate = edge_tts.Communicate(
            text=text_vi,
            voice=VOICE_VN_FEMALE,
            rate="+20%",
            pitch="+0Hz"
        )
        await communicate.save(vi_file)
    except Exception as e:
        print("Error generating Vietnamese audio:", e)
        return False

    clip_vi = AudioSegment.from_file(vi_file, format="mp3")

    us_file = file_out.replace(".mp3", "_fast.mp3")
    await edge_tts.Communicate(
        text=text_us,
        voice=VOICE_FEMALE,
        rate="+0%", pitch="+0Hz").save(us_file)
    clip_us = AudioSegment.from_file(us_file, format="mp3")

    silence = AudioSegment.silent(duration= 500)  # 2000 ms = 2 giây

    final_audio = silence +  clip_vi + silence + clip_us + silence

    temp_files = [
        vi_file,
        us_file
    ]

    try:
        final_audio.export(file_out, format="mp3")

    finally:
        for f in temp_files:
            if os.path.exists(f):
                os.remove(f)

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

        return file_out
    except Exception as e:
        print(f"Lỗi tạo Intro: {e}")
        return None

# Cần sửa phần phan["nhan_vat"] ==
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
        rate="-10%", pitch="+0Hz").save(fast_file)
    clip1 = AudioSegment.from_file(fast_file, format="mp3")

    # Lần 2:
    slow_file = file_out.replace(".mp3", "_slow.mp3")
    await edge_tts.Communicate(
        text=phan["thoai"],
        voice=VOICE_FEMALE if phan["sex"] == "female" else VOICE_MALE,
        rate="-20%", pitch="+0Hz").save(slow_file)
    clip2 = AudioSegment.from_file(slow_file, format="mp3")

    # Lần 3: đọc nhanh lại
    fast2_file = file_out.replace(".mp3", "_fast2.mp3")
    await edge_tts.Communicate(
        text=phan["thoai"],
        voice=VOICE_FEMALE if phan["sex"] == "female" else VOICE_MALE,
        rate="-10%", pitch="+0Hz").save(fast2_file)
    clip3 = AudioSegment.from_file(fast2_file, format="mp3")


    # Tạo đoạn silence 2 giây
    silence = AudioSegment.silent(duration= 1500)  # 2000 ms = 2 giây

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

def add_speech_bubble(base_image_path, output_path,text_vi, text_us, scene):

    img = Image.open(base_image_path).convert("RGBA")
    draw = ImageDraw.Draw(img)

    font = ImageFont.truetype(
        "arialbd.ttf",
        30
    )

    # ==========================
    # Tự động xuống dòng
    # ==========================

    wrapped_text = textwrap.fill(
        text_us,
        width=30
    )

    bbox = draw.multiline_textbbox(
        (0, 0),
        wrapped_text,
        font=font
    )

    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]

    wrapped_vi = textwrap.fill(text_vi, width=35)  # Tiếng Việt có thể để width rộng hơn chút
    font_vi = ImageFont.truetype("arial.ttf", 26)  # Fon
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
    # Vị trí bong bóng
    # ==========================

    # Tìm tọa độ nhân vật:

    img_cv = cv2.imread(f"{BASE_DIR}/image/base_scene.png")
    gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    faces = face_cascade.detectMultiScale(gray, 1.1, 3)

    for i, (a, b, w, h) in enumerate(faces):
        print(
            i,
            "head=",
            a + w // 2,
            b + h // 3
        )
    # ======
    faces = sorted(faces, key=lambda f: f[1])  # sort theo y

    y = img.height - text_h - 550

    if scene["sex"] == "female":
        (a, b, w, h) = faces[0]
        x  = (a + img.width + w - bubble_width)/2
    elif scene["sex"] == "male":
        (a, b, w, h) = faces[1]
        x = (a - bubble_width)/2 + 1.2 *  w
    else:
        x, y = 400, 40

    # Bong bóng chính
    # ==========================

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
        font=font,
        fill="black",
        align="center"
    )

    # 3. Vẽ tiếng Việt
    draw.multiline_text(
        (vi_x, vi_y), wrapped_vi, font=font_vi, fill=(0, 70, 220), align="center")

    img.save(output_path)

    print(f"Saved {output_path}")

    return img

def draw_text_preview_hook(base_image_path, output_path,text_vi, text_us):

    img = Image.open(base_image_path).convert("RGBA")
    draw = ImageDraw.Draw(img)

    font = ImageFont.truetype(
        "arialbd.ttf",
        30
    )

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
        font=font
    )

    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]

    wrapped_vi = textwrap.fill(text_vi, width=55)  # Tiếng Việt có thể để width rộng hơn chút
    font_vi = ImageFont.truetype("arial.ttf", 26)  # Fon
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
        font=font,
        fill="black",
        align="center"
    )

    # 3. Vẽ tiếng Việt
    draw.multiline_text(
        (vi_x, vi_y), wrapped_vi, font=font_vi, fill=(0, 70, 220), align="center")

    img.save(output_path)

    print(f"Saved {output_path}")

    return img

async def all_preview_audio_imge():
    for i, scene in enumerate(KICH_BAN, start=1):

        await audio_preview(scene)

        output_image = f"{BASE_DIR}/image/preview/scene_{i}.png"

        if not os.path.exists(output_image):
            img = draw_text_preview_hook(base_image_path=f"{BASE_DIR}/image/base_scene.png",
                output_path=output_image,
                text_vi=scene["translation"],
                text_us = scene["thoai"],
            )
            img.save(output_image, quality=90)

async def all_repeat_image_and_audio():
    for i, scene in enumerate(KICH_BAN, start=1):

        await audio_repeat(scene)

        output_image = f"{BASE_DIR}/image/repeat/scene_{i}.png"

        if not os.path.exists(output_image):

            img = add_speech_bubble(
                base_image_path=f"{BASE_DIR}/image/male.png"
                if scene["sex"] == "male" else f"{BASE_DIR}/image/female.png",
                output_path=output_image,
                text_vi=scene["translation"],
                text_us=scene["thoai"],
                scene = scene,
            )

            img.save(output_image, quality=90)

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
        print(f"Skip {output_path}, already exists.")
        return

    run_ffmpeg([
        "ffmpeg", "-y",
        "-loop", "1", "-i", image_path, "-i", audio_path,
        "-shortest", "-c:v", "libx264", "-r", "24", "-c:a", "aac",
        "-pix_fmt", "yuv420p", output_path
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

    # concat
    # run_ffmpeg([
    #     "ffmpeg", "-y",
    #     "-f", "concat",
    #     "-safe", "0",
    #     "-i", list_file,
    #     "-c", "copy",
    #     temp_output
    # ])
    run_ffmpeg([
        "ffmpeg", "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", list_file,
        "-c:v", "libx264",
        "-c:a", "aac",
        "-fflags", "+genpts",
        temp_output
    ])

    duration = get_audio_duration(temp_output)

    fade_duration = 1.0

    run_ffmpeg([
        "ffmpeg", "-y",
        "-i", temp_output,
        "-vf",
        f"fade=t=in:st=0:d={fade_duration},"
        f"fade=t=out:st={duration-fade_duration}:d={fade_duration}",
        "-c:v", "libx264",
        "-c:a", "aac",
        output
    ])

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

    outtro_img = "for_youtube/logo_outtro/outtro.png"

    intro_audio = f"{BASE_DIR}/audio/intro.mp3"
    topic_audio = f"{BASE_DIR}/audio/topic.mp3"
    outtro_audio = f"{BASE_DIR}/audio/outtro.mp3"
    hook_audio = f"{BASE_DIR}/audio/hook.mp3"
    ad_audio1 = f"{BASE_DIR}/audio/ad_audio1.mp3"
    ad_audio2 = f"{BASE_DIR}/audio/ad_audio2.mp3"
    bg_music = "for_youtube/nhac_nen.mp3"

    intro_video = f"{BASE_DIR}/videos/intro.mp4"
    topic_video = f"{BASE_DIR}/videos/topic.mp4"
    hook_video = f"{BASE_DIR}/videos/hook.mp4"
    ad_video1 = f"{BASE_DIR}/videos/ad_video1.mp4"
    ad_video2 = f"{BASE_DIR}/videos/ad_video2.mp4"

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
            and os.path.exists(outtro_video)):
        make_scene_video(intro_img, intro_audio, intro_video)
        make_scene_video(hook_img, hook_audio, hook_video)
        make_scene_video(ad_img1, ad_audio1, ad_video1)
        make_scene_video(ad_img2, ad_audio2, ad_video2)
        make_scene_video(topic_img, topic_audio, topic_video)
        make_scene_video(outtro_img, outtro_audio, outtro_video)


    # Tạo main.mp4
    create_main_video()

    # Ghép intro + topic + main + outtro
    concat_videos(
        [intro_video,
                 hook_video,
                 topic_video,
                 ad_video1,
                 preview_video,
                 ad_video2,
                 main_video,
                 outtro_video], final_video)

    # Thêm nhạc nền
    add_background_music(final_video, bg_music, final_with_music)

    print("✅ Final video created:", final_with_music)

# =========================
# 5. Main
# =========================
async def main():
    # Tạo audio intro.txt/topic/outtro/hook
    print("----AUDIO----")
    #Intro
    await audio_intro_outtro_hook(INTRO, f"{BASE_DIR}/audio/intro.mp3")

    #Hook
    await audio_topic(hook_vi, hook_us, f"{BASE_DIR}/audio/hook.mp3")

    #Topic
    await audio_topic(topic_vi, topic_us, f"{BASE_DIR}/audio/topic.mp3")

    #Outtro
    await audio_intro_outtro_hook(OUT_TRO, f"{BASE_DIR}/audio/outtro.mp3")

    #Listen_carefully
    ad_vi1 = "Lắng nghe thật kĩ nhé"
    ad_us1 = "Listen carefully"

    await audio_listen_advice(ad_vi1, ad_us1, f"{BASE_DIR}/audio/ad_audio1.mp3")

    # Listen and repeat:
    ad_vi2 = "Lắng nghe và lặp lại theo mình nhé"
    ad_us2 = "Listen and repeat"

    await audio_listen_advice(ad_vi2, ad_us2, f"{BASE_DIR}/audio/ad_audio2.mp3")

    print("----TOPIC----")
    draw_text_on_topic_ad(f"{BASE_DIR}/image/topic.png", topic_us)

    print("----AdVICE----")

    if (os.path.exists(f"{BASE_DIR}/image/advice.png") ):
        if not os.path.exists(f"{BASE_DIR}/image/advice1.png"):
            shutil.copy(f"{BASE_DIR}/image/advice.png", f"{BASE_DIR}/image/advice1.png")

        if not os.path.exists(f"{BASE_DIR}/image/advice2.png"):
            shutil.copy(f"{BASE_DIR}/image/advice.png", f"{BASE_DIR}/image/advice2.png")

    draw_text_on_topic_ad(f"{BASE_DIR}/image/advice1.png", ad_us1)

    draw_text_on_topic_ad(f"{BASE_DIR}/image/advice2.png", ad_us2)

    # Tạo ảnh:
    print("----CREATE ALL IMAGE AND AUDIO----")
    await all_preview_audio_imge()
    await all_repeat_image_and_audio()

    print("----SCENES----")
    # giả sử audio + image đã được tạo trước
    for i, scene in enumerate(KICH_BAN, start=1):
        make_scene_video(f"{BASE_DIR}/image/preview/scene_{i}.png", scene["audio_preview"], f"{BASE_DIR}/scenes/preview/scene_{i}.mp4")

        make_scene_video(f"{BASE_DIR}/image/repeat/scene_{i}.png", scene["audio_repeat"], f"{BASE_DIR}/scenes/repeat/scene_{i}.mp4")

    print("Preview Video")
    # Tao preview
    creat_preview()

    print("----FINAL VIDEO----")
    await build_final_video()
    print("DONE")

if __name__ == "__main__":
    asyncio.run(main())
