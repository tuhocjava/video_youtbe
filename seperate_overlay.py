import os
from pathlib import Path
import cv2
import numpy as np
from ultralytics import YOLO

def split_people_direct(
    image_path,
    output_path,
    model_path="yolov8x-seg.pt",
    conf=0.3,
    max_people=None,
    pad_x_ratio=0.03,
    pad_y_ratio=0.03,
):

    image = cv2.imread(image_path, cv2.IMREAD_COLOR)
    if image is None:
        raise ValueError(f"Không đọc được ảnh: {image_path}")

    h, w = image.shape[:2]

    model = YOLO(model_path)
    results = model.predict(source=image, conf=conf, verbose=False)
    result = results[0]

    if result.masks is None or result.boxes is None:
        raise ValueError("Không tìm thấy người")

    people = []

    boxes = result.boxes.xyxy.cpu().numpy().astype(int)
    classes = result.boxes.cls.cpu().numpy().astype(int)
    masks = result.masks.data.cpu().numpy()

    person_indexes = [i for i, cls in enumerate(classes) if cls == 0]
    
    person_indexes = [i for i, cls in enumerate(classes) if cls == 0]

    areas = [(i, (boxes[i][2] - boxes[i][0]) * (boxes[i][3] - boxes[i][1])) for i in person_indexes]

    # Lọc bỏ nhân vật nhỏ: ví dụ chỉ giữ những nhân vật có diện tích > 10% diện tích ảnh
    min_area = 0.1 * (image.shape[0] * image.shape[1])
    filtered = [i for i, area in areas if area > min_area]

    # Nếu muốn chỉ lấy 2 nhân vật lớn nhất
    filtered = sorted(filtered, key=lambda i: (boxes[i][2] - boxes[i][0]) * (boxes[i][3] - boxes[i][1]), reverse=True)[:2]

    # Cuối cùng sắp xếp từ trái sang phải để tên file ổn định
    person_indexes = sorted(filtered, key=lambda i: boxes[i][0])


    if max_people is not None:
        person_indexes = person_indexes[:max_people]
        
    all_person_masks = []

    for idx in person_indexes:
        m = masks[idx]
        m = cv2.resize(m, (w, h), interpolation=cv2.INTER_NEAREST)
        m = (m > 0.5).astype(np.uint8)
        all_person_masks.append((idx, m))

    for person_count, i in enumerate(person_indexes):
        x1, y1, x2, y2 = boxes[i]

        box_w = x2 - x1
        box_h = y2 - y1

        pad_x = int(box_w * pad_x_ratio)
        pad_y = int(box_h * pad_y_ratio)

        x1e = max(0, x1 - pad_x)
        y1e = max(0, y1 - pad_y)
        x2e = min(w, x2 + pad_x)
        y2e = min(h, y2 + pad_y)

        # Mask người từ YOLO
        person_mask = masks[i]
        person_mask = cv2.resize(person_mask, (w, h), interpolation=cv2.INTER_NEAREST)
        person_mask = (person_mask > 0.5).astype(np.uint8)
        
        # Mask của các nhân vật khác
        other_people_mask = np.zeros((h, w), dtype=np.uint8)

        for other_idx, other_mask in all_person_masks:
            if other_idx == i:
                continue

            # Nới mask người khác một chút để tránh ăn sát biên/cánh tay
            other_dilated = cv2.dilate(
                other_mask,
                np.ones((17, 17), np.uint8),
                iterations=1
            )

            other_people_mask = np.maximum(other_people_mask, other_dilated)

        # Vùng chắc chắn là người
        sure_fg = cv2.erode(
            person_mask,
            np.ones((5, 5), np.uint8),
            iterations=1
        )

        # Vùng có thể là người + phụ kiện: mở rộng quanh bounding box
        prob_fg = np.zeros((h, w), dtype=np.uint8)
        prob_fg[y1e:y2e, x1e:x2e] = 1


        grab_mask = np.full((h, w), cv2.GC_BGD, dtype=np.uint8)

        # Vùng mở rộng quanh người hiện tại là probable foreground
        grab_mask[prob_fg == 1] = cv2.GC_PR_FGD

        # Người hiện tại là foreground chắc chắn
        grab_mask[sure_fg == 1] = cv2.GC_FGD

        # Người khác là background chắc chắn
        grab_mask[other_people_mask == 1] = cv2.GC_BGD
        
        bgd_model = np.zeros((1, 65), np.float64)
        fgd_model = np.zeros((1, 65), np.float64)

        cv2.grabCut(
            image,
            grab_mask,
            None,
            bgd_model,
            fgd_model,
            5,
            cv2.GC_INIT_WITH_MASK
        )

        final_mask = np.where(
            (grab_mask == cv2.GC_FGD) | (grab_mask == cv2.GC_PR_FGD),
            1,
            0
        ).astype(np.uint8)
        
        final_mask[other_people_mask == 1] = 0

        # Chỉ giữ các vùng dính/gần với người để giảm lấy nhầm background
        dilated_person = cv2.dilate(
            person_mask,
            np.ones((3, 3), np.uint8),
            iterations=1
        )

        num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(
            final_mask,
            connectivity=8
        )

        keep_mask = np.zeros_like(final_mask)

        for label in range(1, num_labels):
            component = (labels == label).astype(np.uint8)
            overlap = cv2.bitwise_and(component, dilated_person)

            area = stats[label, cv2.CC_STAT_AREA]

            if overlap.sum() > 0 and area > 30:
                keep_mask[component == 1] = 1

        final_mask = keep_mask

        # Làm kín nhẹ để giữ phụ kiện nhỏ như tai nghe, túi, sách
        final_mask = cv2.morphologyEx(
            final_mask,
            cv2.MORPH_CLOSE,
            np.ones((3, 3), np.uint8)
        )

        final_mask = cv2.GaussianBlur(
            final_mask.astype(np.float32),
            (3, 3),
            0
        )
        
        final_mask = cv2.erode(final_mask, np.ones((3,3), np.uint8), iterations=1)


        final_mask = (final_mask > 0.8).astype(np.uint8)
        
        # Xuất PNG cùng kích thước ảnh gốc
        rgba = cv2.cvtColor(image, cv2.COLOR_BGR2BGRA)

        # Không overlay, không nhân màu ảnh với mask.
        # Chỉ đổi alpha: người giữ nguyên màu gốc, nền trong suốt.
        rgba[:, :, 3] = final_mask * 255

        person_path = os.path.join(output_path, f"person_{person_count}.png")
        cv2.imwrite(person_path, rgba)

        people.append(person_path)
    print("Số người phát hiện:", len(results[0].boxes))
        

    if len(people) == 0:
        raise ValueError("Không có người nào")
    
    return people


def overlay_keep_position(bg, fg, x=0, y=0):
    """
    Ghép nhân vật vào nền giữ nguyên vị trí gốc.
    """
    h_fg, w_fg = fg.shape[:2]

    # Nếu vượt khỏi nền thì crop
    if y + h_fg > bg.shape[0] or x + w_fg > bg.shape[1]:
        h_fg = min(h_fg, bg.shape[0] - y)
        w_fg = min(w_fg, bg.shape[1] - x)
        fg = fg[:h_fg, :w_fg]

    
    # Tăng độ sắc nét, giảm mờ
    alpha = fg[:, :, 3].astype(np.float32) / 255.0
    alpha = cv2.GaussianBlur(alpha, (5, 5), 0)  # blur nhẹ hơn
    alpha = np.clip(alpha, 0, 1)

    roi = bg[y:y+h_fg, x:x+w_fg]
    blended = (alpha[..., None] * fg[:, :, :3] + (1 - alpha[..., None]) * roi).astype(np.uint8)
    bg[y:y+h_fg, x:x+w_fg] = blended

    return bg


# def detect_faces_and_overlay(background_path, people_paths, output_path):
#     """
#     Ghép nhân vật vào nền nhưng giữ nguyên vị trí gốc.
#     """
#     bg = cv2.imread(background_path)
#     if bg is None:
#         raise ValueError(f"Không đọc được ảnh nền: {background_path}")

#     for i, person_path in enumerate(people_paths):
#         fg = cv2.imread(person_path, cv2.IMREAD_UNCHANGED)
#         if fg is None:
#             raise ValueError(f"Không đọc được ảnh nhân vật: {person_path}")
        
#         bg_copy = bg.copy()
#         # Ghép nhân vật vào nền tại vị trí (0,0) hoặc vị trí gốc
#         result = overlay_keep_position(bg_copy, fg, x=0, y=0)

#         sex_path = "female.png" if i == 0 else "male.png"
#         person_path = os.path.join(output_path, sex_path)
#         cv2.imwrite(person_path, result)
#         print(f"Ảnh nhân vật {i} đã lưu tại: {person_path}")
#         os.remove(people_paths[i])

#     return bg

def detect_faces_and_overlay(background_path, people_paths, output_path):
    """
    Ghép nhân vật vào nền nhưng giữ nguyên vị trí gốc.
    """
    bg = cv2.imread(background_path)
    if bg is None:
        raise ValueError(f"Không đọc được ảnh nền: {background_path}")

    for i, input_person_path in enumerate(people_paths):
        sex_path = "female.png" if i == 0 else "male.png"
        person_path = os.path.join(output_path, sex_path)

        if os.path.exists(person_path):
            print(f"Ảnh đã tồn tại, bỏ qua: {person_path}")
            continue

        fg = cv2.imread(input_person_path, cv2.IMREAD_UNCHANGED)
        if fg is None:
            raise ValueError(f"Không đọc được ảnh nhân vật: {input_person_path}")

        bg_copy = bg.copy()
        result = overlay_keep_position(bg_copy, fg, x=0, y=0)

        cv2.imwrite(person_path, result)
        print(f"Ảnh nhân vật {i} đã lưu tại: {person_path}")

        os.remove(input_person_path)

    return bg

# people = split_people_direct("base_scene.png")
# print(people)

# detect_faces_and_overlay("background.png", people)
# print("OK")