import os
import sys
import json
import datetime

PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353", "#69f0a0"]

def render_heatmap_svg(json_path="data/contributions.json", output_path="contrib-heatmap.svg"):
    if not os.path.exists(json_path):
        print(f"[!] Error: '{json_path}' not found. Please run 'fetch_contributions.py' first.")
        sys.exit(1)

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    days = data.get("days", [])
    total_contributions = data.get("total_contributions", 0)
    current_streak = data.get("current_streak", 0)
    longest_streak = data.get("longest_streak", 0)

    # Grid Layout Parameters
    cell_size = 11
    gap = 3
    padding_x = 35
    padding_y = 42

    grid_cols = 53
    grid_rows = 7

    svg_w = padding_x + (grid_cols * (cell_size + gap)) + 25
    svg_h = padding_y + (grid_rows * (cell_size + gap)) + 55

    # Organize days into 53 weeks x 7 days
    # Match days to columns and rows
    # Parse dates and map to grid
    calendar_grid = [[None for _ in range(grid_rows)] for _ in range(grid_cols)]
    
    if days:
        first_date = datetime.datetime.strptime(days[0]["date"], "%Y-%m-%d").date()
        # Find weekday of first date (0=Mon in Python, convert to 0=Sun)
        # Python weekday: Mon=0 .. Sun=6 -> Sun=0 .. Sat=6
        
        for idx, day_info in enumerate(days):
            dt = datetime.datetime.strptime(day_info["date"], "%Y-%m-%d").date()
            # Sun = 0, Mon = 1 ... Sat = 6
            row = (dt.weekday() + 1) % 7
            
            # Calculate column index relative to start of calendar
            if idx == 0:
                col = 0
                start_row = row
            else:
                prev_dt = datetime.datetime.strptime(days[idx-1]["date"], "%Y-%m-%d").date()
                delta_days = (dt - first_date).days
                col = (delta_days + start_row) // 7

            if 0 <= col < grid_cols and 0 <= row < grid_rows:
                calendar_grid[col][row] = day_info

    # Month Labels Placement
    months_labels = []
    curr_month = None
    for col in range(grid_cols):
        for row in range(grid_rows):
            day_item = calendar_grid[col][row]
            if day_item:
                m_str = datetime.datetime.strptime(day_item["date"], "%Y-%m-%d").strftime("%b")
                if m_str != curr_month:
                    curr_month = m_str
                    m_x = padding_x + col * (cell_size + gap)
                    months_labels.append((m_x, m_str))
                break

    svg_lines = []
    svg_lines.append('<?xml version="1.0" encoding="UTF-8"?>')
    svg_lines.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {svg_w} {svg_h}" width="{svg_w}" height="{svg_h}">')
    svg_lines.append('  <style>')
    svg_lines.append('    .bg { fill: #0d1117; stroke: #30363d; stroke-width: 1.5; }')
    svg_lines.append('    .meta-text { font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Courier New", monospace; font-size: 11px; fill: #8b949e; }')
    svg_lines.append('    .stat-text { font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Courier New", monospace; font-size: 12px; fill: #c9d1d9; font-weight: 600; }')
    svg_lines.append('    .legend-text { font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Courier New", monospace; font-size: 10px; fill: #7d8590; }')
    svg_lines.append('    @keyframes slideDown {')
    svg_lines.append('      from { opacity: 0; transform: translateY(-8px); }')
    svg_lines.append('      to { opacity: 1; transform: translateY(0); }')
    svg_lines.append('    }')
    svg_lines.append('    .cell { animation: slideDown 0.3s ease-out forwards; opacity: 0; }')
    svg_lines.append('  </style>')

    # Background card
    svg_lines.append(f'  <rect width="{svg_w}" height="{svg_h}" rx="10" class="bg" />')

    # Month Labels
    for m_x, m_str in months_labels:
        svg_lines.append(f'  <text x="{m_x}" y="25" class="meta-text">{m_str}</text>')

    # Day of week labels (Mon, Wed, Fri)
    day_labels = [(1, "Mon"), (3, "Wed"), (5, "Fri")]
    for r_idx, d_str in day_labels:
        d_y = padding_y + r_idx * (cell_size + gap) + 9
        svg_lines.append(f'  <text x="10" y="{d_y}" class="meta-text">{d_str}</text>')

    # Grid Cells Rendering
    for col in range(grid_cols):
        for row in range(grid_rows):
            day_item = calendar_grid[col][row]
            x_pos = padding_x + col * (cell_size + gap)
            y_pos = padding_y + row * (cell_size + gap)

            if day_item:
                level = day_item.get("level", 0)
                if level >= len(PALETTE):
                    level = len(PALETTE) - 1
                color = PALETTE[level]
                count = day_item.get("count", 0)
                date_str = day_item.get("date", "")
                title_str = f"{count} contributions on {date_str}"
            else:
                color = PALETTE[0]
                title_str = "No contributions"

            # Diagonal slide-down animation delay calculation
            diag_idx = col + row
            delay = diag_idx * 0.022

            svg_lines.append(f'  <rect x="{x_pos}" y="{y_pos}" width="{cell_size}" height="{cell_size}" rx="2" fill="{color}" class="cell" style="animation-delay: {delay:.3f}s;">')
            svg_lines.append(f'    <title>{title_str}</title>')
            svg_lines.append(f'  </rect>')

    # Footer Section
    footer_y = padding_y + (grid_rows * (cell_size + gap)) + 30

    # Left Stats Footer
    stats_str = f"{total_contributions:,} contributions in the last year  •  Streak: {current_streak}d (max {longest_streak}d)"
    svg_lines.append(f'  <text x="{padding_x}" y="{footer_y}" class="stat-text">{stats_str}</text>')

    # Right Legend (Less -> More)
    legend_start_x = svg_w - 180
    svg_lines.append(f'  <text x="{legend_start_x - 30}" y="{footer_y - 1}" class="legend-text">Less</text>')

    for l_idx, p_color in enumerate(PALETTE):
        lx = legend_start_x + (l_idx * (cell_size + gap - 1))
        ly = footer_y - 10
        svg_lines.append(f'  <rect x="{lx}" y="{ly}" width="{cell_size - 1}" height="{cell_size - 1}" rx="2" fill="{p_color}" />')

    svg_lines.append(f'  <text x="{legend_start_x + (len(PALETTE) * 13) + 5}" y="{footer_y - 1}" class="legend-text">More</text>')

    svg_lines.append('</svg>')

    output_content = "\n".join(svg_lines)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(output_content)

    print(f"[+] Successfully generated heatmap SVG: '{output_path}' ({svg_w}x{svg_h}px, {total_contributions} contributions)")

if __name__ == "__main__":
    render_heatmap_svg()
