from PIL import Image
import numpy as np
import glob, os
import cv2

# ------------------ CONFIG ------------------
INPUT_FOLDER = "hellokitty"
OUTPUT_MP4   = "hellokitty_mosaic.mp4"

PLAIN_COUNT    = 5        # эхний том зургуудын тоо (их байвал автоматаар бага нь авна)
PLAIN_DURATION = 1500     # эхний 4 зургийг ~1.5 sec удаан үзүүлэх

TILE_W = 26
TILE_H = 26
GRID_STEP = 20

FPS = 10
BASE_TILE_COUNT = 5       # жижиг tile-д ашиглах зургуудын тоо

# Zoom configs (эхний mask дээр аажмаар холдох)
ZOOM_IN_FACTOR = 5.0     # эхний zoom-in (их байх тусам илүү ойрхон)
ZOOM_OUT_STEPS = 10      # хэдэн шаттайгаар холдох
# --------------------------------------------


def find_files(folder):
    exts = ("*.jpeg", "*.jpg", "*.png")
    files = []
    for e in exts:
        files.extend(glob.glob(os.path.join(folder, e)))
    return sorted(files)


def find_mask_files(folder):
    masks = glob.glob(os.path.join(folder, "mask*"))
    return sorted(masks)


def build_base_tiles(files):
    tiles = []
    for f in files[:BASE_TILE_COUNT]:
        try:
            im = Image.open(f).convert("RGB").resize(
                (TILE_W, TILE_H), Image.LANCZOS
            )
            tiles.append(im)
        except Exception as e:
            print("⚠ base tile load error:", f, e)
    return tiles


def positions_from_mask(mask_path, grid_step=GRID_STEP):
    m = cv2.imread(mask_path, cv2.IMREAD_GRAYSCALE)
    if m is None:
        return [], (0, 0)

    h, w = m.shape
    _, bin_mask = cv2.threshold(
        m, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU
    )

    # background нь ихэнхдээ цагаан байвал урвуулна
    if (bin_mask > 0).mean() > 0.6:
        bin_mask = cv2.bitwise_not(bin_mask)

    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    bin_mask = cv2.morphologyEx(bin_mask, cv2.MORPH_CLOSE, kernel, 2)
    bin_mask = cv2.medianBlur(bin_mask, 3)

    positions = []
    for y in range(0, h, grid_step):
        for x in range(0, w, grid_step):
            cx = min(x + grid_step // 2, w - 1)
            cy = min(y + grid_step // 2, h - 1)
            if bin_mask[cy, cx] > 128:
                positions.append((cx, cy))

    return positions, (w, h)


def instant_mosaic(mask_path, base_tile):
    positions, (bw, bh) = positions_from_mask(mask_path)
    if not positions:
        return None

    out = Image.new("RGB", (bw, bh), (0, 0, 0))

    for (cx, cy) in positions:
        tx = max(0, min(cx - TILE_W // 2, bw - TILE_W))
        ty = max(0, min(cy - TILE_H // 2, bh - TILE_H))
        out.paste(base_tile, (tx, ty))

    return out


def zoom(frame, factor):
    """Төвөөс crop → resize → zoom эффект."""
    bw, bh = frame.size
    crop_w = int(bw / factor)
    crop_h = int(bh / factor)

    crop_w = max(50, min(bw, crop_w))
    crop_h = max(50, min(bh, crop_h))

    left   = (bw - crop_w) // 2
    top    = (bh - crop_h) // 2
    right  = left + crop_w
    bottom = top + crop_h

    crop = frame.crop((left, top, right, bottom))
    zoomed = crop.resize((bw, bh), Image.LANCZOS)
    return zoomed


def main():
    # --- файлуудаа цуглуулах ---
    all_files  = find_files(INPUT_FOLDER)
    mask_files = find_mask_files(INPUT_FOLDER)
    plain_files = [f for f in all_files if "mask" not in f.lower()]

    if not mask_files:
        raise RuntimeError(
            "No mask images found!\n"
            "→ 'hellokitty' хавтас дотор mask1.png, mask2.png ... гэх мэт нэртэй маскуудаа хий."
        )

    if not plain_files:
        raise RuntimeError(
            "No plain hellokitty images found!\n"
            "→ 'hellokitty' хавтас дотор энгийн kitty зургууд (.jpg/.png) байх ёстой."
        )

    # base tiles
    base_tiles = build_base_tiles(plain_files)
    if not base_tiles:
        raise RuntimeError("No base tiles loaded (kitty images).")

    # маскны хэмжээгээр бүх frame-үүдийг тааруулна
    bw, bh = Image.open(mask_files[0]).size

    # Plain frames (эхний том зургууд)
    use_plain = plain_files[:PLAIN_COUNT]
    plain_frames = [
        Image.open(f).convert("RGB").resize((bw, bh), Image.LANCZOS)
        for f in use_plain
    ]

    # Mosaic + zoom animation
    mosaic_frames = []

    for idx, mask_path in enumerate(mask_files):
        if idx == 0:
            # ЭХНИЙ MASK: zoom animation + full mosaic
            first_tile = base_tiles[0]
            frame = instant_mosaic(mask_path, first_tile)
            if frame is None:
                continue

            # 1) эхний zoom-in (маш ойроос)
            zoom_in_frame = zoom(frame, ZOOM_IN_FACTOR)
            mosaic_frames.append(zoom_in_frame)

            # 2) аажмаар холдох (ZOOM_OUT_STEPS шаттайгаар)
            for step in range(ZOOM_OUT_STEPS):
                t = ZOOM_IN_FACTOR - (ZOOM_IN_FACTOR - 1.0) * ((step + 1) / ZOOM_OUT_STEPS)
                mosaic_frames.append(zoom(frame, t))

            # 3) эцсийн бүтэн mosaic frame
            mosaic_frames.append(frame)

        else:
            # Бусад masks: зөвхөн бүтэн mosaic-ууд
            for tile in base_tiles:
                f = instant_mosaic(mask_path, tile)
                if f is not None:
                    mosaic_frames.append(f)

    # ------------------------ VIDEO FRAMES ------------------------
    base_duration_ms = int(1000 / FPS)  # 1 frame ≈ 100ms @ FPS=10
    long_repeat = max(1, PLAIN_DURATION // base_duration_ms)

    video_frames = []

    # эхний 4 plain зураг — удаан
    for i, fr in enumerate(plain_frames):
        if i < 4:
            repeat = long_repeat   # 1–4: удаан харагдана
        else:
            repeat = 1             # 5 дахь байвал хурдан
        video_frames.extend([fr] * repeat)

    # дараа нь mosaic + zoom хэсэг
    video_frames.extend(mosaic_frames)

    if not video_frames:
        raise RuntimeError("No frames generated for MP4.")

    # ------------------------ WRITE MP4 ------------------------
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # хэрэггүй бол 'a','v','c','1' гэж сольж болно
    out = cv2.VideoWriter(OUTPUT_MP4, fourcc, FPS, (bw, bh))

    if not out.isOpened():
        print("⚠ MP4 бичих боломжгүй байна (codec/ffmpeg issue).")
        return

    for f in video_frames:
        frame_bgr = cv2.cvtColor(np.array(f), cv2.COLOR_RGB2BGR)
        out.write(frame_bgr)

    out.release()
    print("Saved MP4:", OUTPUT_MP4)


if __name__ == "__main__":
    main()
