
import os
import shutil
import subprocess
import textwrap
import asyncio
import cv2
import edge_tts
from PIL import Image, ImageDraw, ImageFont
from pydub import AudioSegment

BASE_DIR = "Ep4/output"
DOWNLOAD_DIR = "Ep4/download"

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
("Sophia", "Hi Ethan! Do you smell that delicious food from the canteen?", "Chào Ethan! Bạn có ngửi thấy mùi đồ ăn thơm ngon từ căng tin không?", "female"),
("Ethan", "Hi Sophia! Yes, I do. It smells wonderful!", "Chào Sophia! Có chứ. Mùi thật tuyệt vời!", "male"),
("Sophia", "The smell is making me hungry.", "Mùi hương đó làm mình thấy đói bụng rồi.", "female"),
("Ethan", "Me too! Let's go to the canteen for lunch.", "Mình cũng vậy! Chúng ta đi căng tin ăn trưa nhé.", "male"),
("Sophia", "Great idea! What would you like to eat today?", "Ý hay đấy! Hôm nay bạn muốn ăn gì?", "female"),
("Ethan", "I think I'll get some sandwiches.", "Mình nghĩ mình sẽ ăn vài chiếc bánh sandwich.", "male"),
("Sophia", "That sounds tasty. I want a salad and some fruit.", "Nghe ngon đấy. Mình muốn ăn salad và một ít trái cây.", "female"),
("Ethan", "Those are healthy choices.", "Đó là những lựa chọn rất tốt cho sức khỏe.", "male"),
("Sophia", "Look! The lunch line is not too long today.", "Nhìn kìa! Hàng chờ ăn trưa hôm nay không quá dài.", "female"),
("Ethan", "That's good. We can get our food quickly.", "Tốt quá. Chúng ta có thể lấy đồ ăn nhanh chóng.", "male"),
("Sophia", "My salad looks fresh, and the fruit looks sweet.", "Salad của mình trông rất tươi và trái cây có vẻ rất ngọt.", "female"),
("Ethan", "My sandwiches look delicious.", "Những chiếc bánh sandwich của mình trông rất ngon.", "male"),
("Sophia", "Let's try our food.", "Hãy thử món ăn của chúng ta nào.", "female"),
("Ethan", "Wow! These sandwiches taste wonderful!", "Wow! Những chiếc bánh sandwich này có hương vị thật tuyệt vời!", "male"),
("Sophia", "My salad and fruit taste wonderful too!", "Salad và trái cây của mình cũng có hương vị thật tuyệt vời!", "female"),
("Ethan", "I'm glad we came here for lunch today.", "Mình rất vui vì hôm nay chúng ta đã đến đây ăn trưa.", "male")
]

KICH_BAN = [
    {
        "nhan_vat": character,
        "thoai": dialogue,
        "translation": translation,
        "sex": sex,
        "file_audio": f"{BASE_DIR}/audio/voice{i}.mp3",
    }
    for i, (character, dialogue, translation, sex) in enumerate(dialogues, start=1)
]

INTRO = "Chào mừng các bạn đã quay trở lại!\nRất vui được ở đây cùng các bạn.\nChúc các bạn có một ngày thật tốt lành.\nVà bây giờ, cùng bắt đầu nào!"
topic_vi = "Bài 4: Cùng ăn trưa ở căng tin."
topic_us = "Lesson 4: Let's Have Lunch at the Canteen."
OUT_TRO = "Cám ơn các bạn đã xem hết video, nếu các bạn thấy hay, hãy nhấn nút Đăng ký để ủng hộ kênh và đón xem những video tiếp theo nhé. Cảm ơn các bạn rất nhiều!"

VOICE_MALE = "en-GB-RyanNeural"
VOICE_FEMALE = "en-US-JennyNeural"
VOICE_VN_FELMALE = "vi-VN-HoaiMyNeural"
VOICE_VN_MALE = "vi-VN-NamMinhNeural"

FONT = ImageFont.truetype("arialbd.ttf", 36)

# =========================
# 2. Chuẩn bị thư mục
# =========================
os.makedirs(f"{DOWNLOAD_DIR}/image", exist_ok=True)
os.makedirs(f"{BASE_DIR}/image", exist_ok=True)
os.makedirs(f"{BASE_DIR}/audio", exist_ok=True)
os.makedirs(f"{BASE_DIR}/scenes", exist_ok=True)
os.makedirs(f"{BASE_DIR}/videos", exist_ok=True)

# =========================
# 3. Các hàm xử lý
# =========================

# Copy các ảnh base_scene/intro/topic từ download/image vào ouput/image

if not (os.path.exists(f"{BASE_DIR}/image/base_scene.png")
        and os.path.exists(f"{BASE_DIR}/image/intro.png")
        and  os.path.exists(f"{BASE_DIR}/image/topic.png")):
    downloads = ["base_scene.png", "intro.png", "topic.png"]
    for f in downloads:
        shutil.copy(f"{DOWNLOAD_DIR}/image/{f}", f"{BASE_DIR}/image/{f}")


base_scene = (Image.open(f"{BASE_DIR}/image/base_scene.png")
              .resize((1280, 720))
              .save(f"{BASE_DIR}/image/base_scene.png"))

intro = (Image.open(f"{BASE_DIR}/image/intro.png")
         .resize((1280, 720))
         .save(f"{BASE_DIR}/image/intro.png"))

topic = (Image.open(f"{BASE_DIR}/image/topic.png")
              .resize((1280, 720))
              .save(f"{BASE_DIR}/image/topic.png"))

# Hàm tạo audio intro-outtro
async def create_audio_intro_outtro(text, file_out):
    if os.path.exists(file_out):
        return file_out

    try:
        communicate = edge_tts.Communicate(
            text = text,
            voice = VOICE_VN_FELMALE,
            rate="+22%",
            pitch="+0Hz"
        )
        await communicate.save(file_out)
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
async def create_audio_topic(topic_vi, topic_us, file_out):
    if os.path.exists(file_out):
        return file_out

    file_vi = file_out.replace(".mp3", "_vi.mp3")
    try:
        communicate = edge_tts.Communicate(
            text = topic_vi,
            voice = VOICE_VN_MALE,
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

    # Ghép audio: lần 1 + lần 2
    final_audio = clip_vi + clip_us
    final_audio.export(file_out, format="mp3")
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
def draw_text_on_topic(file_img, topic_us):
    # Vẽ topic lên ảnh:
    img = Image.open(file_img)
    ve_text_wrap(img, topic_us, FONT)
    img.save(file_img, quality=90)

# Cần sửa phần phan["nhan_vat"] ==
async def create_audio_fsf(phan):

    # Tạo audio tiếng Việt
    file_out = phan["file_audio"]
    if os.path.exists(file_out):
        return True

    if not phan["translation"].strip():
        print("Translation text is empty")
        return False

    vi_file = file_out.replace(".mp3", "_vi.mp3")
    try:
        communicate = edge_tts.Communicate(
            text=phan["translation"],
            voice=VOICE_VN_FELMALE if phan["sex"] == "female" else VOICE_VN_MALE,
            rate="+20%",
            pitch="+0Hz"
        )
        await communicate.save(vi_file)
    except Exception as e:
        print("Error generating Vietnamese audio:", e)
        return False

    clip_vi = AudioSegment.from_file(vi_file, format="mp3")

    # Lần 1: đọc nhanh tự nhiên
    fast_file = file_out.replace(".mp3", "_fast.mp3")
    await edge_tts.Communicate(
        text=phan["thoai"],
        voice=VOICE_FEMALE if phan["sex"] == "female" else VOICE_MALE,
        rate="+0%", pitch="+0Hz").save(fast_file)
    clip1 = AudioSegment.from_file(fast_file, format="mp3")

    # Lần 2: đọc chậm, rõ từng từ
    slow_file = file_out.replace(".mp3", "_slow.mp3")
    await edge_tts.Communicate(
        text=phan["thoai"],
        voice=VOICE_FEMALE if phan["sex"] == "female" else VOICE_MALE,
        rate="-40%", pitch="+2Hz").save(slow_file)
    clip2 = AudioSegment.from_file(slow_file, format="mp3")
    clip2 = clip2.high_pass_filter(100)

    # Lần 3: đọc nhanh lại
    fast2_file = file_out.replace(".mp3", "_fast2.mp3")
    await edge_tts.Communicate(
        text=phan["thoai"],
        voice=VOICE_FEMALE if phan["sex"] == "female" else VOICE_MALE,
        rate="+0%", pitch="+0Hz").save(fast2_file)
    clip3 = AudioSegment.from_file(fast2_file, format="mp3")

    # Tạo đoạn silence 2 giây
    silence = AudioSegment.silent(duration= 1000)  # 2000 ms = 2 giây

    # Ghép audio: lần 1 + lần 2 + silence + lần 3
    final_audio = clip_vi + silence + clip1 +silence + clip2 + silence + clip3
    final_audio.export(file_out, format="mp3")
    temp_files = [
        vi_file,
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

def add_speech_bubble(base_image_path, output_path,text, scene):

    img = Image.open(base_image_path).convert("RGBA")
    draw = ImageDraw.Draw(img)

    font = ImageFont.truetype(
        "arialbd.ttf",
        24
    )

    # ==========================
    # Tự động xuống dòng
    # ==========================

    wrapped_text = textwrap.fill(
        text,
        width=25
    )

    bbox = draw.multiline_textbbox(
        (0, 0),
        wrapped_text,
        font=font
    )

    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]

    # ==========================
    # Kích thước bong bóng
    # ==========================

    bubble_width = max(
        260,
        text_w + 40
    )

    bubble_height = max(
        120,
        text_h + 30
    )

    # ==========================
    # Vị trí bong bóng
    # ==========================

    # Tìm tọa độ nhân vật:
    img_cv = cv2.imread(f"{BASE_DIR}/image/base_scene.png")
    gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    # faces = face_cascade.detectMultiScale(gray, 1.1, 3)
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.05, minNeighbors=4)

    for i, (a, b, w, h) in enumerate(faces):
        print(
            i,
            "head=",
            a + w // 2,
            b + h // 3
        )
    faces = sorted(faces, key=lambda f: f[1])  # sắp xếp theo y (trên → dưới)

    print(faces)

    if scene["sex"] == "female":
        (a, b, w, h) =  faces[1]
        head_x = a + w // 2
        head_y = b + h // 3  # lấy điểm gần trán

        x = head_x - bubble_width  - 60
        y = head_y - bubble_height - 50

        # Vị trí đuôi thoại hướng về Sophia
        tail1 = (
            x + bubble_width - 80,
            y + bubble_height - 10,
            x + bubble_width - 45,
            y + bubble_height + 25
        )

        tail2 = (
            x + bubble_width - 55,
            y + bubble_height + 30,
            x + bubble_width - 30,
            y + bubble_height + 55
        )

        tail3 = (
            x + bubble_width - 20,
            y + bubble_height + 55,
            x + bubble_width + 5,
            y + bubble_height + 70
        )
    elif scene["sex"] == "male":
        # Đẩy bong bóng sang phải hơn
        (a, b, w, h) = faces[0]
        head_x = a + w // 2
        head_y = b + h // 3  # lấy điểm gần trán

        x = head_x - bubble_width + 400
        y = head_y - bubble_height - 50

        # Đuôi thoại hướng xuống đầu Tommy
        tail1 = (
            x + 110,
            y + bubble_height - 5,
            x + 140,
            y + bubble_height + 25
        )

        tail2 = (
            x + 90,
            y + bubble_height + 10,
            x + 110,
            y + bubble_height + 30
        )

        tail3 = (
            x + 65,
            y + bubble_height + 20,
            x + 80,
            y + bubble_height + 35
        )

    else:

        x, y = 400, 40

        tail1 = (
            x + 90,
            y + bubble_height - 10,
            x + 120,
            y + bubble_height + 20
        )

        tail2 = (
            x + 110,
            y + bubble_height + 10,
            x + 130,
            y + bubble_height + 30
        )

        tail3 = (
            x + 125,
            y + bubble_height + 30,
            x + 140,
            y + bubble_height + 45
        )

    # ==========================
    # Bong bóng chính
    # ==========================

    draw.ellipse(
        (
            x,
            y,
            x + bubble_width,
            y + bubble_height
        ),
        fill="white" ,
        outline="black",
        width=1
    )

    # ==========================
    # Đuôi thoại cong
    # ==========================

    draw.ellipse(
        tail1,
        fill="white",
        outline="black"
    )

    draw.ellipse(
        tail2,
        fill="white",
        outline="black"
    )

    draw.ellipse(
        tail3,
        fill="white",
        outline="black"
    )

    # ==========================
    # Text
    # ==========================

    text_x = x + (bubble_width - text_w) / 2
    text_y = y + (bubble_height - text_h) / 2

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

    img.save(output_path)

    print(f"Saved {output_path}")

    return img

async def create_all_image_and_audio():
    for i, scene in enumerate(KICH_BAN, start=1):

        await create_audio_fsf(scene)

        output_image = f"{BASE_DIR}/image/scene_{i}.png"

        if not os.path.exists(output_image):

            img = add_speech_bubble(
                base_image_path=f"{BASE_DIR}/image/base_scene.png",
                output_path=output_image,
                text=scene["thoai"],
                scene = scene,
            )

            ve_text_wrap(img, scene["translation"], FONT)

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
            # dùng đường dẫn tuyệt đối để chắc chắn đúng
            f.write(f"file '{os.path.abspath(v)}'\n")

    run_ffmpeg([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0",
        "-i", list_file, "-c", "copy", output
    ])


def create_main_video():

    main_path = f"{BASE_DIR}/videos/main.mp4"
    if os.path.exists(main_path):
        print(f"Skip {main_path}, already exists.")
        return

    scene_videos = [f"{BASE_DIR}/scenes/scene_{i}.mp4" for i in range(1, len(KICH_BAN)+1)]
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
    outtro_img = "for_youtube/logo_outtro/outtro.png"

    intro_audio = f"{BASE_DIR}/audio/intro.mp3"
    topic_audio = f"{BASE_DIR}/audio/topic.mp3"
    outtro_audio = f"{BASE_DIR}/audio/outtro.mp3"
    bg_music = "for_youtube/nhac_nen.mp3"

    intro_video = f"{BASE_DIR}/videos/intro.mp4"
    topic_video = f"{BASE_DIR}/videos/topic.mp4"
    main_video  = f"{BASE_DIR}/videos/main.mp4"
    outtro_video = f"{BASE_DIR}/videos/outtro.mp4"
    final_video = f"{BASE_DIR}/videos/final_video.mp4"
    final_with_music = f"{BASE_DIR}/videos/final_with_music.mp4"

    # Tạo intro/topic/outtro
    if not (os.path.exists(intro_video)
            and os.path.exists(topic_video)
            and os.path.exists(outtro_video)):
        make_scene_video(intro_img, intro_audio, intro_video)
        make_scene_video(topic_img, topic_audio, topic_video)
        make_scene_video(outtro_img, outtro_audio, outtro_video)

    # Tạo main.mp4
    create_main_video()

    # Ghép intro + topic + main + outtro
    concat_videos([intro_video, topic_video, main_video, outtro_video], final_video)

    # Thêm nhạc nền
    add_background_music(final_video, bg_music, final_with_music)

    print("✅ Final video created:", final_with_music)

# =========================
# 5. Main
# =========================
async def main():
    # Tạo audio intro/topic/outtro
    print("----AUDIO----")
    await create_audio_intro_outtro(INTRO, f"{BASE_DIR}/audio/intro.mp3")
    await create_audio_topic(topic_vi, topic_us, f"{BASE_DIR}/audio/topic.mp3")
    await create_audio_intro_outtro(OUT_TRO, f"{BASE_DIR}/audio/outtro.mp3")

    print("----TOPIC----")
    draw_text_on_topic(f"{BASE_DIR}/image/topic.png", topic_us)

    # Tạo ảnh:
    print("----CREATE ALL IMAGE AND AUDIO----")
    await create_all_image_and_audio()

    print("----SCENES----")
    # giả sử audio + image đã được tạo trước
    for i, scene in enumerate(KICH_BAN, start=1):
        make_scene_video(f"{BASE_DIR}/image/scene_{i}.png", scene["file_audio"], f"{BASE_DIR}/scenes/scene_{i}.mp4")

    print("----FINAL VIDEO----")
    await build_final_video()
    print("DONE")

if __name__ == "__main__":
    asyncio.run(main())
