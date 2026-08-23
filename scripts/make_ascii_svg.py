import os
import sys
import xml.sax.saxutils as saxutils
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageEnhance
import numpy as np

# Specification Density Ramp: bright (sparse) -> dark (dense)
RAMP = " .`:-=+*cs#%@"

def create_sample_photo(filename="source-photo.jpg"):
    """Generates a sample portrait image if user hasn't provided one yet."""
    w, h = 400, 500
    img = Image.new("L", (w, h), 255)
    draw = ImageDraw.Draw(img)
    # Draw background gradient/shapes
    draw.ellipse([80, 60, 320, 380], fill=40)   # head
    draw.ellipse([60, 260, 340, 520], fill=60)  # shoulders
    draw.ellipse([130, 150, 180, 180], fill=240) # left eye
    draw.ellipse([220, 150, 270, 180], fill=240) # right eye
    draw.polygon([(200, 180), (180, 240), (220, 240)], fill=160) # nose
    draw.arc([150, 260, 250, 310], start=0, end=180, fill=220, width=8) # smile
    img.save(filename)
    print(f"[+] Created sample photo '{filename}'")

def make_ascii_svg(input_path="source-prepped.png", output_path="manya-ascii.svg", cols=100):
    if not os.path.exists(input_path):
        if os.path.exists("source-photo.jpg"):
            input_path = "source-photo.jpg"
        else:
            create_sample_photo("source-photo.jpg")
            input_path = "source-photo.jpg"

    print(f"[+] Reading image for ASCII conversion: '{input_path}'...")
    img = Image.open(input_path).convert("L")

    # Downsample to character grid (~100 cols x ~53 rows)
    w, h = img.size
    aspect_ratio = h / w
    # Monospace character aspect ratio ~0.55 (height is ~1.8x width)
    char_aspect = 0.55
    rows = int(cols * aspect_ratio * char_aspect)
    
    img_resized = img.resize((cols, rows), Image.Resampling.LANCZOS)
    img_np = np.array(img_resized)

    # Map pixels to density ramp
    # Bright pixels -> space / sparse chars; Dark pixels -> dense chars (@, %, #)
    ramp_len = len(RAMP)
    ascii_rows = []
    for r in range(rows):
        row_chars = []
        for c in range(cols):
            val = img_np[r, c]
            # Normalize 0..255 to index 0..ramp_len-1
            idx = int((val / 255.0) * (ramp_len - 1))
            row_chars.append(RAMP[idx])
        ascii_rows.append("".join(row_chars))

    # SVG layout configuration
    char_w = 6.8
    char_h = 12.0
    font_size = 10.0
    padding_x = 20.0
    padding_y = 20.0

    line_w = cols * char_w
    svg_w = int(line_w + padding_x * 2)
    svg_h = int(rows * char_h + padding_y * 2)

    # SMIL Animation parameters
    sec_per_row = 0.045
    wipe_dur = 0.35
    total_dur = rows * sec_per_row + wipe_dur

    svg_lines = []
    svg_lines.append('<?xml version="1.0" encoding="UTF-8"?>')
    svg_lines.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {svg_w} {svg_h}" width="{svg_w}" height="{svg_h}">')
    svg_lines.append('  <style>')
    svg_lines.append('    .bg { fill: #0d1117; }')
    svg_lines.append('    .ascii-text { font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace; font-size: 10px; font-weight: 500; fill: #e2e8f0; white-space: pre; }')
    svg_lines.append('    .cursor { fill: #6366f1; }')
    svg_lines.append('  </style>')
    svg_lines.append(f'  <rect width="100%" height="100%" class="bg" rx="8" />')

    # Add clipPaths for row wipes
    svg_lines.append('  <defs>')
    for r in range(rows):
        t_start = r * sec_per_row
        y_pos = padding_y + r * char_h
        svg_lines.append(f'    <clipPath id="clip-row-{r}">')
        svg_lines.append(f'      <rect x="{padding_x}" y="{y_pos}" width="0" height="{char_h}">')
        svg_lines.append(f'        <animate attributeName="width" from="0" to="{line_w:.2f}" begin="{t_start:.3f}s" dur="{wipe_dur:.3f}s" fill="freeze" />')
        svg_lines.append(f'      </rect>')
        svg_lines.append(f'    </clipPath>')
    svg_lines.append('  </defs>')

    # Add text rows & animated cursors
    for r in range(rows):
        t_start = r * sec_per_row
        y_pos = padding_y + r * char_h
        baseline_y = y_pos + font_size - 1.5
        escaped_str = saxutils.escape(ascii_rows[r])

        # Clipped ASCII text row
        svg_lines.append(f'  <text x="{padding_x}" y="{baseline_y:.2f}" class="ascii-text" clip-path="url(#clip-row-{r})">{escaped_str}</text>')

        # Block cursor riding the wipe edge
        svg_lines.append(f'  <rect y="{y_pos:.2f}" width="{char_w:.2f}" height="{char_h:.2f}" class="cursor" opacity="0">')
        svg_lines.append(f'    <animate attributeName="opacity" values="1;1;0" keyTimes="0;0.95;1" begin="{t_start:.3f}s" dur="{wipe_dur:.3f}s" fill="freeze" />')
        svg_lines.append(f'    <animate attributeName="x" from="{padding_x:.2f}" to="{padding_x + line_w - char_w:.2f}" begin="{t_start:.3f}s" dur="{wipe_dur:.3f}s" fill="freeze" />')
        svg_lines.append(f'  </rect>')

    svg_lines.append('</svg>')

    output_content = "\n".join(svg_lines)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(output_content)
    
    # Save standard ascii.svg alias as well
    with open("ascii.svg", "w", encoding="utf-8") as f:
        f.write(output_content)

    print(f"Successfully generated animated SVG: '{output_path}' and 'ascii.svg' ({svg_w}x{svg_h}px, {rows} rows)")

if __name__ == "__main__":
    make_ascii_svg()
