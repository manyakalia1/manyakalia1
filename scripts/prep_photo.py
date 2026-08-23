import sys
import os
import numpy as np
from PIL import Image, ImageOps, ImageEnhance

def prep_photo(input_path="source-photo.jpg", output_path="source-prepped.png"):
    if not os.path.exists(input_path):
        # Look for alternative image extensions if specified file doesn't exist directly
        found = False
        for ext in [".jpg", ".jpeg", ".png", ".webp"]:
            alt_path = "source-photo" + ext
            if os.path.exists(alt_path):
                input_path = alt_path
                found = True
                break
        if not found:
            print(f"Error: Input photo '{input_path}' not found.")
            print("Please place your photo as 'source-photo.jpg' or pass the filename as an argument:")
            print(f"  python scripts/prep_photo.py <your-photo.jpg>")
            sys.exit(1)

    print(f"[+] Processing photo: '{input_path}'...")
    img_pil = Image.open(input_path).convert("RGBA")

    # Step 1: Remove background with rembg so subject is isolated
    try:
        from rembg import remove
        print("[+] Removing background using rembg...")
        img_no_bg = remove(img_pil)
    except Exception as e:
        print(f"[!] Notice: rembg background removal failed or unavailable ({e}). Using image alpha mask...")
        img_no_bg = img_pil

    # Step 2: Composite onto pure white background so background becomes white (maps to spaces)
    print("[+] Compositing onto pure white background...")
    white_bg = Image.new("RGBA", img_no_bg.size, (255, 255, 255, 255))
    composited = Image.alpha_composite(white_bg, img_no_bg).convert("L")

    # Step 3: Boost local contrast with OpenCV CLAHE
    img_np = np.array(composited)
    try:
        import cv2
        print("[+] Boosting local contrast with OpenCV CLAHE...")
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        img_clahe = clahe.apply(img_np)
    except Exception as e:
        print(f"[!] Notice: OpenCV CLAHE unavailable ({e}). Using PIL contrast enhancement...")
        composited_enhanced = ImageOps.autocontrast(composited)
        enhancer = ImageEnhance.Contrast(composited_enhanced)
        img_clahe = np.array(enhancer.enhance(1.5))

    # Save output grayscale source-prepped.png
    final_img = Image.fromarray(img_clahe)
    final_img.save(output_path)
    print(f"[+] Saved prepped photo to '{output_path}'")

if __name__ == "__main__":
    input_file = sys.argv[1] if len(sys.argv) > 1 else "source-photo.jpg"
    prep_photo(input_file)
