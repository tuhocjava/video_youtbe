# Chuyển watermark  thành nền trong suốt và resize 250x250 và đổi tên thành logo

import os
from PIL import Image


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