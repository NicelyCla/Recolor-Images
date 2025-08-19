# Recolor Images

This repository contains two Python scripts to recolor images by replacing the dominant color with a user-specified color. Both scripts detect the dominant color of "useful" pixels and replace it while preserving transparency and saturation.  

- `change_color.py`: Standard version using **Pillow**.  
- `change_color_fast.py`: Faster version using **OpenCV** for mask processing.

---

## Features

- Detects the dominant color in each image based on hue and saturation.
- Recolors relevant pixels with a HEX color of your choice.
- Supports images with transparency (RGBA).
- Batch processing of images in a folder.

---

## Configuration

You can customize parameters directly in the script:

```python
DEFAULT_NEW_COLOR_HEX = "#2e84bd"   # Default new color
HUE_TOLERANCE_DEG = 18              # Tolerance around dominant color in degrees
MIN_SATURATION_PERC = 0.3           # Minimum saturation of pixels to consider (0–1)
IMAGES_DIR = "./images"             # Input folder
OUTPUT_DIR = "./output"             # Output folder
