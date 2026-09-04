"""Process the EduPilot logo: crop icon only, recolor blue->green, resize, save."""
from PIL import Image
import numpy as np

img = Image.open("assets/logo.png").convert("RGBA")
data = np.array(img)
w, h = img.size
print(f"Original: {w}x{h}")

# ── Step 1: Crop out text ─────────────────────────────────────────────
# Top text ("LOGO PROMPT 4") occupies rows ~0-30
# Icon occupies rows ~40-145
# Bottom text ("EduPilot AI") occupies rows ~148-180
# We want ONLY the icon portion
icon_top = 38
icon_bottom = 148
icon = data[icon_top:icon_bottom, :, :]

# Trim transparent/white margins on sides
alpha = icon[:, :, 3]
rgb_mean = np.mean(icon[:, :, :3], axis=2)
# Find columns that have non-white content
non_white = (rgb_mean < 240) & (alpha > 128)
cols_with_content = np.any(non_white, axis=0)
col_indices = np.where(cols_with_content)[0]
if len(col_indices) > 0:
    left = max(0, col_indices[0] - 2)
    right = min(icon.shape[1], col_indices[-1] + 3)
    icon = icon[:, left:right, :]

icon_img = Image.fromarray(icon)
print(f"Cropped icon: {icon_img.size}")

# ── Step 2: Recolor blue pixels -> green ────────────────────────────────
# Green target: #2E7D32 = RGB(46, 125, 50)
# Dark navy: #1B2A4A-ish -> dark green
# Medium blue: various blues -> medium green
# Light blue: circuit nodes -> light green
icon_data = np.array(icon_img).astype(np.float64)
r, g, b, a = icon_data[:, :, 0], icon_data[:, :, 1], icon_data[:, :, 2], icon_data[:, :, 3]

# Detect blue-dominant pixels: where blue > red and blue > green
is_blue = (b > r * 1.1) & (b > g * 1.05) & (a > 50)
is_dark = (np.mean(icon_data[:, :, :3], axis=2) < 100) & (a > 50)
is_medium_blue = is_blue & ~is_dark
is_light_blue = is_blue & (b > 150)

# Dark blue -> dark green (#1B5E20 = 27, 94, 32)
icon_data[is_dark & is_blue, 0] = 27
icon_data[is_dark & is_blue, 1] = 94
icon_data[is_dark & is_blue, 2] = 32

# Medium blue -> primary green (#2E7D32 = 46, 125, 50)
icon_data[is_medium_blue & ~is_light_blue, 0] = 46
icon_data[is_medium_blue & ~is_light_blue, 1] = 125
icon_data[is_medium_blue & ~is_light_blue, 2] = 50

# Light blue -> light green (#81C784 = 129, 199, 132)
icon_data[is_light_blue, 0] = 129
icon_data[is_light_blue, 1] = 199
icon_data[is_light_blue, 2] = 132

# Also catch any remaining blue-ish dark pixels (navy) that weren't caught
# Navy: low R, low G, moderate B
is_navy = (b > 60) & (r < 80) & (g < 80) & (a > 50) & ~is_blue
icon_data[is_navy, 0] = 27
icon_data[is_navy, 1] = 94
icon_data[is_navy, 2] = 32

icon_data = np.clip(icon_data, 0, 255).astype(np.uint8)
icon_recolored = Image.fromarray(icon_data)

# ── Step 3: Resize for login page usage ─────────────────────────────────
# Target: icon height ~40-50px for login page (matches heading height)
# Keep aspect ratio
orig_w, orig_h = icon_recolored.size
target_h = 48
target_w = int(orig_w * (target_h / orig_h))
icon_final = icon_recolored.resize((target_w, target_h), Image.LANCZOS)
print(f"Final icon: {icon_final.size}")

# ── Step 4: Save ─────────────────────────────────────────────────────────
icon_final.save("assets/logo_icon.png", "PNG")
print("Saved: assets/logo_icon.png")

# Also save a slightly larger version for the sidebar
sidebar_h = 36
sidebar_w = int(orig_w * (sidebar_h / orig_h))
icon_sidebar = icon_recolored.resize((sidebar_w, sidebar_h), Image.LANCZOS)
icon_sidebar.save("assets/logo_icon_sidebar.png", "PNG")
print(f"Sidebar icon: {icon_sidebar.size} -> assets/logo_icon_sidebar.png")
