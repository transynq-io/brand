"""Build web-sized Transynq brand assets for the SDK repos from the brand kit (read-only)."""
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter

BRAND = Path(sys.argv[1])
OUT = Path(sys.argv[2])
OUT.mkdir(parents=True, exist_ok=True)

# ---- wordmark (light mode: dark text on transparent) ----
src = Image.open(BRAND / "Transynq_Extracted_Logos/01_Primary/Transynq_Primary_Logo_Transparent_4x.png").convert("RGBA")
print("corner alpha", src.getpixel((2, 2))[3], src.getpixel((src.width - 3, src.height - 3))[3])
bbox = src.getchannel("A").point(lambda a: 255 if a > 24 else 0).getbbox()
src = src.crop(bbox)
r_, g_, b_, a_ = src.split()
src = Image.merge("RGBA", (r_, g_, b_, a_.point(lambda a: 0 if a < 40 else a)))
W = 1200
light = src.resize((W, round(src.height * W / src.width)), Image.LANCZOS)
light.save(OUT / "transynq-logo-light.png", optimize=True)

# ---- wordmark (dark mode): navy text -> off-white, dark navy parts of the symbol -> brand blue ----
icon_edge = round(light.width * 0.255)   # the symbol ends ~25% across the lockup
dark = light.copy()
px = dark.load()
for y in range(dark.height):
    for x in range(dark.width):
        r, g, b, a = px[x, y]
        if a == 0:
            continue
        mx, mn = max(r, g, b), min(r, g, b)
        sat = mx - mn
        lum = 0.2126 * r + 0.7152 * g + 0.0722 * b
        if x > icon_edge and sat < 90:
            # navy wordmark/tagline -> off-white; the light glow/matte around it -> transparent
            k = max(0.0, min(1.0, (200 - lum) / 130))
            px[x, y] = (248, 250, 252, round(a * k))
        elif x <= icon_edge:
            if sat < 40 and lum > 150:          # white matte fringe -> transparent
                px[x, y] = (r, g, b, round(a * max(0.0, (230 - lum) / 80)))
            elif lum < 90:                      # navy part of the stem -> brand blue
                t = 1 - lum / 90
                px[x, y] = (round(r + (59 - r) * t), round(g + (130 - g) * t), round(b + (246 - b) * t), a)
dark.save(OUT / "transynq-logo-dark.png", optimize=True)

# ---- app icon: crop the rounded tile from the master, transparent corners ----
m = Image.open(BRAND / "Transynq_Mobile_App_and_App_Icons/02_App_Icons/Master/Transynq_App_Icon_Master_1024.png").convert("RGB")
gray = m.convert("L")
tile_bbox = gray.point(lambda v: 255 if v < 70 else 0).getbbox()
x0, y0, x1, y1 = tile_bbox
side = max(x1 - x0, y1 - y0)
cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
tile = m.crop((cx - side // 2, cy - side // 2, cx + side // 2, cy + side // 2)).convert("RGBA")
S = tile.width
scale = 4
mask = Image.new("L", (S * scale, S * scale), 0)
inset = round(S * 0.045) * scale
ImageDraw.Draw(mask).rounded_rectangle((inset, inset, S * scale - inset, S * scale - inset), radius=round(S * 0.21) * scale, fill=255)
mask = mask.resize((S, S), Image.LANCZOS)
tile.putalpha(mask)
for n in (512, 256, 128, 64, 48, 32, 16):
    tile.resize((n, n), Image.LANCZOS).save(OUT / f"transynq-icon-{n}.png", optimize=True)
tile.resize((256, 256), Image.LANCZOS).save(OUT / "favicon.ico", sizes=[(16, 16), (32, 32), (48, 48), (64, 64)])

# ---- social preview / README banner 1280x640 on brand near-black ----
banner = Image.new("RGBA", (1280, 640), (11, 18, 32, 255))
g = Image.new("RGBA", (1280, 640), (0, 0, 0, 0))
d = ImageDraw.Draw(g)
d.ellipse((780, -260, 1560, 520), fill=(37, 99, 235, 70))
d.ellipse((-300, 360, 420, 1000), fill=(139, 92, 246, 50))
banner = Image.alpha_composite(banner, g.filter(ImageFilter.GaussianBlur(120)))
lw = 900
logo = dark.resize((lw, round(dark.height * lw / dark.width)), Image.LANCZOS)
banner.alpha_composite(logo, ((1280 - lw) // 2, (640 - logo.height) // 2))
banner.convert("RGB").save(OUT / "transynq-social-preview.png", optimize=True)

for f in sorted(OUT.iterdir()):
    print(f.name, f.stat().st_size)
