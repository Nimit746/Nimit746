"""Process Image.jpeg: remove white background, resize, export base64 PNG."""
import base64, sys
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    print("NEED_PILLOW")
    sys.exit(1)

src = Path(__file__).parent / "Image.jpeg"
img = Image.open(src).convert("RGBA")

# Resize to max height 500px for reasonable base64 size
max_h = 500
if img.height > max_h:
    ratio = max_h / img.height
    img = img.resize((int(img.width * ratio), max_h), Image.LANCZOS)

# Remove white / near-white background
pixels = img.load()
w, h = img.size
for y in range(h):
    for x in range(w):
        r, g, b, a = pixels[x, y]
        # If pixel is near-white, make transparent
        if r > 230 and g > 230 and b > 230:
            pixels[x, y] = (r, g, b, 0)
        # Feather edges of near-white
        elif r > 200 and g > 200 and b > 200:
            alpha = int(255 * (1 - (min(r, g, b) - 200) / 55))
            pixels[x, y] = (r, g, b, min(a, alpha))

# Save PNG
out_png = Path(__file__).parent / "character.png"
img.save(out_png, "PNG", optimize=True)

# Base64 encode
b64 = base64.b64encode(out_png.read_bytes()).decode("ascii")

# Write base64 to a text file for embedding
out_b64 = Path(__file__).parent / "character_b64.txt"
out_b64.write_text(b64)

print(f"OK dims={img.width}x{img.height} png_size={out_png.stat().st_size} b64_len={len(b64)}")
