import os
import cv2
import numpy as np
from PIL import Image
from collections import Counter

# -------------------------
# Configurazione
# -------------------------
DEFAULT_NEW_COLOR_HEX = "#000000"
HUE_TOLERANCE_DEG = 18
MIN_SATURATION_PERC = 0.3
IMAGES_DIR = "./images"
OUTPUT_DIR = "./output"

# -------------------------
# Utility
# -------------------------
def hex_to_bgr(hex_color: str):
    hex_color = hex_color.strip().lstrip("#")
    if len(hex_color) == 3:
        hex_color = "".join([c*2 for c in hex_color])
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    return (b, g, r)  # OpenCV usa BGR

def deg_to_hbyte(deg: float) -> int:
    return int(round((deg % 360) * 179 / 360.0))  # OpenCV H in [0,179]

def hue_distance(h1, h2):
    """Distanza circolare tra due hue [0,179]"""
    d = abs(h1 - h2)
    return min(d, 180 - d)

# -------------------------
# Core
# -------------------------
def recolor_image(path, new_color_hex=DEFAULT_NEW_COLOR_HEX, hue_tol_deg=HUE_TOLERANCE_DEG, min_sat_perc=MIN_SATURATION_PERC):
    # --- PIL per leggere RGBA e HSV ---
    pil_img = Image.open(path).convert("RGBA")
    rgba = np.array(pil_img)
    
    pil_hsv = pil_img.convert("HSV")
    hsv = np.array(pil_hsv)

    alpha = rgba[..., 3]
    min_saturation = int(min_sat_perc * 255)

    # --- Trova colore dominante sul canale H dei pixel "utili" ---
    mask_useful = (alpha > 0) & (hsv[..., 1] >= min_saturation)
    hue_values = hsv[..., 0][mask_useful]
    if len(hue_values) == 0:
        out_path = os.path.join(OUTPUT_DIR, os.path.basename(path).rsplit(".", 1)[0] + "_recolored.png")
        pil_img.save(out_path)
        return out_path

    dominant_h = Counter(hue_values).most_common(1)[0][0]

    # --- OpenCV per maschera veloce e sostituzione colore ---
    img_bgr = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGBA2BGR)
    new_color_bgr = hex_to_bgr(new_color_hex)

    # Calcola tolleranza hue
    hue_tol = deg_to_hbyte(hue_tol_deg)

    # Maschera considerando wrap-around
    lower = (dominant_h - hue_tol) % 180
    upper = (dominant_h + hue_tol) % 180
    h_channel = hsv[..., 0]

    if lower <= upper:
        hue_mask = (h_channel >= lower) & (h_channel <= upper)
    else:
        hue_mask = (h_channel >= lower) | (h_channel <= upper)

    sat_mask = hsv[..., 1] >= min_saturation
    alpha_mask = alpha > 0

    final_mask = (hue_mask & sat_mask & alpha_mask)

    # Applica il nuovo colore
    recolored_bgr = img_bgr.copy()
    recolored_bgr[final_mask] = new_color_bgr

    # Ricostruisci RGBA
    recolored_rgba = cv2.cvtColor(recolored_bgr, cv2.COLOR_BGR2RGBA)
    recolored_rgba[..., 3] = alpha  # mantieni alpha originale

    # Salva
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    out_name = os.path.basename(path).rsplit(".", 1)[0] + "_recolored.png"
    out_path = os.path.join(OUTPUT_DIR, out_name)
    Image.fromarray(recolored_rgba).save(out_path, "PNG")
    return out_path

def recolor_batch(file_paths, new_color_hex=DEFAULT_NEW_COLOR_HEX):
    return [recolor_image(p, new_color_hex=new_color_hex) for p in file_paths]

# -------------------------
# Esempio d’uso
# -------------------------
if __name__ == "__main__":
    valid_ext = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tiff"}
    file_paths = [os.path.join(IMAGES_DIR, f) for f in os.listdir(IMAGES_DIR) if os.path.splitext(f)[1].lower() in valid_ext]
    outputs = recolor_batch(file_paths, new_color_hex=DEFAULT_NEW_COLOR_HEX)
    print("Immagini salvate in:", OUTPUT_DIR)
    print(outputs)

