import os
import sys

def generate_info_card(output_path="info-card.svg"):
    # Check if STATIC=1 environment variable is set for frozen preview
    is_static = os.environ.get("STATIC") == "1"

    width = 520
    height = 290
    padding = 20

    # Neofetch rows data
    user_header = "manyakalia1@github"
    separator = "-------------------"

    rows = [
        ("Now", "Building web apps & exploring AI tools", "#c084fc"),
        ("Prev", "Full-Stack Dev, DBMS & CS Fundamentals", "#60a5fa"),
        ("Stack", "C++, React, Node.js, Python, Java, SQL, Vercel", "#4ade80"),
        ("Highlights", "Open Source, Web Apps & CS Concepts", "#facc15"),
    ]

    color_palette = ["#1e293b", "#ef4444", "#22c55e", "#eab308", "#3b82f6", "#a855f7", "#06b6d4", "#f8fafc"]

    svg_lines = []
    svg_lines.append('<?xml version="1.0" encoding="UTF-8"?>')
    svg_lines.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">')
    svg_lines.append('  <style>')
    svg_lines.append('    .card-bg { fill: #0d1117; stroke: #30363d; stroke-width: 1.5; }')
    svg_lines.append('    .title-bar { fill: #161b22; }')
    svg_lines.append('    .title-text { font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Courier New", monospace; font-size: 12px; fill: #8b949e; font-weight: 600; }')
    svg_lines.append('    .term-text { font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Courier New", monospace; font-size: 13px; font-weight: 500; }')
    svg_lines.append('    .user-head { fill: #38bdf8; font-weight: bold; }')
    svg_lines.append('    .sep { fill: #475569; }')
    svg_lines.append('    .val-text { fill: #e2e8f0; }')
    svg_lines.append('  </style>')

    # Background card with rounded corners
    svg_lines.append(f'  <rect width="{width}" height="{height}" rx="10" class="card-bg" />')

    # Top title bar
    svg_lines.append(f'  <rect width="{width}" height="34" rx="10" class="title-bar" />')
    # Fix bottom corners of title bar so it merges smoothly
    svg_lines.append(f'  <rect y="24" width="{width}" height="10" class="title-bar" />')

    # Terminal dots (Red, Yellow, Green)
    svg_lines.append('  <circle cx="20" cy="17" r="5.5" fill="#ff5f56" />')
    svg_lines.append('  <circle cx="38" cy="17" r="5.5" fill="#ffbd2e" />')
    svg_lines.append('  <circle cx="56" cy="17" r="5.5" fill="#27c93f" />')

    # Title text
    svg_lines.append(f'  <text x="{width // 2}" y="21" text-anchor="middle" class="title-text">manyakalia1@sysinfo ~ neofetch</text>')

    # Content section
    start_y = 65
    line_height = 26

    line_idx = 0

    # Line 0: Header prompt
    t_start_0 = 0.1
    dur = 0.4
    init_opacity = "1" if is_static else "0"

    svg_lines.append(f'  <g class="term-text" opacity="{init_opacity}">')
    if not is_static:
        svg_lines.append(f'    <animate attributeName="opacity" from="0" to="1" begin="{t_start_0:.2f}s" dur="{dur:.2f}s" fill="freeze" />')
        svg_lines.append(f'    <animateTransform attributeName="transform" type="translate" from="0 10" to="0 0" begin="{t_start_0:.2f}s" dur="{dur:.2f}s" fill="freeze" />')
    svg_lines.append(f'    <text x="25" y="{start_y}" class="user-head">{user_header}</text>')
    svg_lines.append(f'  </g>')

    # Line 1: Separator
    line_idx += 1
    t_start_1 = t_start_0 + 0.12
    y_pos = start_y + (line_idx * line_height) - 10

    svg_lines.append(f'  <g class="term-text" opacity="{init_opacity}">')
    if not is_static:
        svg_lines.append(f'    <animate attributeName="opacity" from="0" to="1" begin="{t_start_1:.2f}s" dur="{dur:.2f}s" fill="freeze" />')
        svg_lines.append(f'    <animateTransform attributeName="transform" type="translate" from="0 10" to="0 0" begin="{t_start_1:.2f}s" dur="{dur:.2f}s" fill="freeze" />')
    svg_lines.append(f'    <text x="25" y="{y_pos}" class="sep">{separator}</text>')
    svg_lines.append(f'  </g>')

    # Neofetch Key-Value Rows
    for key, val, color in rows:
        line_idx += 1
        t_start = t_start_0 + (line_idx * 0.14)
        y_pos = start_y + (line_idx * line_height) - 5

        svg_lines.append(f'  <g class="term-text" opacity="{init_opacity}">')
        if not is_static:
            svg_lines.append(f'    <animate attributeName="opacity" from="0" to="1" begin="{t_start:.2f}s" dur="{dur:.2f}s" fill="freeze" />')
            svg_lines.append(f'    <animateTransform attributeName="transform" type="translate" from="0 10" to="0 0" begin="{t_start:.2f}s" dur="{dur:.2f}s" fill="freeze" />')
        # Colored Key
        svg_lines.append(f'    <text x="25" y="{y_pos}" fill="{color}" font-weight="bold">{key}:</text>')
        # Value text aligned
        svg_lines.append(f'    <text x="125" y="{y_pos}" class="val-text">{val}</text>')
        svg_lines.append(f'  </g>')

    # Palette blocks at bottom
    line_idx += 1
    t_start_blocks = t_start_0 + (line_idx * 0.14)
    y_pos_blocks = start_y + (line_idx * line_height) + 5

    svg_lines.append(f'  <g opacity="{init_opacity}">')
    if not is_static:
        svg_lines.append(f'    <animate attributeName="opacity" from="0" to="1" begin="{t_start_blocks:.2f}s" dur="{dur:.2f}s" fill="freeze" />')
        svg_lines.append(f'    <animateTransform attributeName="transform" type="translate" from="0 10" to="0 0" begin="{t_start_blocks:.2f}s" dur="{dur:.2f}s" fill="freeze" />')

    block_w = 24
    block_h = 14
    start_x = 25
    for idx, col in enumerate(color_palette):
        x_block = start_x + (idx * (block_w + 6))
        svg_lines.append(f'    <rect x="{x_block}" y="{y_pos_blocks}" width="{block_w}" height="{block_h}" rx="3" fill="{col}" />')
    svg_lines.append(f'  </g>')

    svg_lines.append('</svg>')

    output_content = "\n".join(svg_lines)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(output_content)

    print(f"[+] Successfully generated Neofetch info card: '{output_path}' (Static: {is_static})")

if __name__ == "__main__":
    generate_info_card()
