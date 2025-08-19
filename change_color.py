import os
from PIL import Image
from collections import Counter
from typing import List, Tuple

# -------------------------
# Configurazione
# -------------------------
DEFAULT_NEW_COLOR_HEX = "#2e84bd"  # new_color
HUE_TOLERANCE_DEG = 18             # tolleranza intorno al colore dominante
MIN_SATURATION_PERC = 0.3          # minimo 30% di saturazione (0–1)
IMAGES_DIR = "./images"            # cartella input
OUTPUT_DIR = "./output"            # cartella output

# -------------------------
# Utility
# -------------------------
def hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
    hex_color = hex_color.strip().lstrip("#")
    if len(hex_color) == 3:
        hex_color = "".join([c*2 for c in hex_color])
    if len(hex_color) != 6:
        raise ValueError(f"Colore hex non valido: {hex_color}")
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    return (r, g, b)

def deg_to_hbyte(deg: float) -> int:
    """Converte gradi (0–360) in scala [0–255]."""
    return int(round((deg % 360) * 255.0 / 360.0))

def hue_distance_byte(h1: int, h2: int) -> int:
    """Distanza circolare tra due hue su [0..255]."""
    d = abs(h1 - h2)
    return min(d, 256 - d)

# -------------------------
# Core
# -------------------------
def recolor_image_detecting_dominant(
    path: str,
    new_color_hex: str = DEFAULT_NEW_COLOR_HEX,
    hue_tolerance_deg: int = HUE_TOLERANCE_DEG,
    min_saturation_perc: float = MIN_SATURATION_PERC
) -> str:
    img_rgba = Image.open(path).convert("RGBA")
    img_hsv  = img_rgba.convert("HSV")

    rgba = list(img_rgba.getdata())   # (R,G,B,A)
    hsv  = list(img_hsv.getdata())    # (H,S,V) con H,S,V in [0..255]

    # 1) Trova colore dominante tra i pixel "utili"
    min_saturation = int(255 * min_saturation_perc)
    hue_values = [h for (h, s, v), (_, _, _, a) in zip(hsv, rgba)
                  if a > 0 and s >= min_saturation]

    if not hue_values:
        out_path = os.path.join(OUTPUT_DIR, os.path.basename(path).rsplit(".", 1)[0] + "_recolored.png")
        img_rgba.save(out_path, "PNG")
        return out_path

    dominant_h = Counter(hue_values).most_common(1)[0][0]

    # 2) Prepara nuovo colore
    new_r, new_g, new_b = hex_to_rgb(new_color_hex)
    tol_byte = deg_to_hbyte(hue_tolerance_deg)

    # 3) Ricolorazione
    new_pixels = []
    for (h, s, v), (r, g, b, a) in zip(hsv, rgba):
        if a > 0 and s >= min_saturation and hue_distance_byte(h, dominant_h) <= tol_byte:
            new_pixels.append((new_r, new_g, new_b, a))
        else:
            new_pixels.append((r, g, b, a))

    # 4) Salva in OUTPUT_DIR
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    out_name = os.path.basename(path).rsplit(".", 1)[0] + "_recolored.png"
    out_path = os.path.join(OUTPUT_DIR, out_name)

    img_out = Image.new("RGBA", img_rgba.size)
    img_out.putdata(new_pixels)
    img_out.save(out_path, "PNG")
    return out_path

def recolor_batch(
    file_paths: List[str],
    new_color_hex: str = DEFAULT_NEW_COLOR_HEX
) -> List[str]:
    return [recolor_image_detecting_dominant(p, new_color_hex=new_color_hex) for p in file_paths]

# -------------------------
# Esempio d’uso
# -------------------------
if __name__ == "__main__":
    # Prende tutti i file immagine dalla cartella images
    valid_ext = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tiff"}
    file_paths = [
        os.path.join(IMAGES_DIR, f)
        for f in os.listdir(IMAGES_DIR)
        if os.path.splitext(f)[1].lower() in valid_ext
    ]

    outputs = recolor_batch(file_paths, new_color_hex=DEFAULT_NEW_COLOR_HEX)
    print("Immagini salvate in:", OUTPUT_DIR)
    print(outputs)
