#!/usr/bin/env python3
"""prep_photo.py - Remove background + boost local contrast via CLAHE."""
import sys
import numpy as np
from PIL import Image
import cv2
from rembg import remove

# ── CONFIG ────────────────────────────────────────────────────────
clipLimit = 3.0
tileGridSize = (8, 8)
# ── END CONFIG ────────────────────────────────────────────────────

def main():
    if len(sys.argv) < 3:
        print(f"Usage: {sys.argv[0]} <input_image> <output_image>")
        sys.exit(1)
    
    src, dst = sys.argv[1], sys.argv[2]
    print(f"[prep] Loading {src}...")
    img = Image.open(src).convert("RGBA")
    
    print("[prep] Removing background with rembg...")
    img_nobg = remove(img)
    
    # Composite onto white background
    white_bg = Image.new("RGBA", img_nobg.size, (255, 255, 255, 255))
    composited = Image.alpha_composite(white_bg, img_nobg)
    gray = composited.convert("L")
    
    print(f"[prep] Applying CLAHE (clipLimit={clipLimit})...")
    arr = np.array(gray)
    clahe = cv2.createCLAHE(clipLimit=clipLimit, tileGridSize=tileGridSize)
    enhanced = clahe.apply(arr)
    
    result = Image.fromarray(enhanced)
    result.save(dst)
    print(f"[prep] Saved to {dst}")

if __name__ == "__main__":
    main()
