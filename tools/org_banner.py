"""Org profile hero: sunset highway photo + brand gradient + logo + headline."""
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont

BRAND = Path(sys.argv[1]); ASSETS = Path(sys.argv[2]); OUT = Path(sys.argv[3]); OUT.mkdir(parents=True, exist_ok=True)
FONTS = Path(r"C:\Windows\Fonts")


def font(names, size):
    for n in names:
        p = FONTS / n
        if p.exists():
            return ImageFont.truetype(str(p), size)
    return ImageFont.load_default()


bold = lambda s: font(["segoeuib.ttf", "arialbd.ttf"], s)
semi = lambda s: font(["seguisb.ttf", "segoeui.ttf", "arial.ttf"], s)
reg = lambda s: font(["segoeui.ttf", "arial.ttf"], s)

W, H = 1600, 520
photo = Image.open(BRAND / "Sunset Cold-Chain Highway Journey.png").convert("RGB")
scale = W / photo.width
photo = photo.resize((W, round(photo.height * scale)), Image.LANCZOS)
top = max(0, (photo.height - H) // 2 + 40)
base = photo.crop((0, top, W, top + H)).convert("RGBA")

# brand gradient: near-black on the left fading to transparent on the right
grad = Image.new("RGBA", (W, H))
gp = grad.load()
for x in range(W):
    t = min(1.0, max(0.0, (x - 380) / 900))
    a = round(250 * (1 - t) + 70 * t)
    for y in range(H):
        gp[x, y] = (11, 18, 32, a)
base = Image.alpha_composite(base, grad)
glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
ImageDraw.Draw(glow).ellipse((-260, 260, 520, 900), fill=(139, 92, 246, 60))
base = Image.alpha_composite(base, glow.filter(ImageFilter.GaussianBlur(120)))

logo = Image.open(ASSETS / "transynq-logo-dark.png").convert("RGBA")
lw = 560
logo = logo.resize((lw, round(logo.height * lw / logo.width)), Image.LANCZOS)
base.alpha_composite(logo, (72, 70))

d = ImageDraw.Draw(base)
y = 70 + logo.height + 46
d.text((76, y), "Smarter Transport.", font=bold(54), fill=(248, 250, 252))
d.text((76, y + 64), "Connected Operations.", font=bold(54), fill=(248, 250, 252))
d.text((78, y + 146), "Intelligent transport management for jobs, shipments, fleets, drivers and operations.",
       font=reg(22), fill=(203, 213, 225))

# brand bar along the bottom: primary -> secondary -> accent
bar = Image.new("RGBA", (W, 8))
bp = bar.load()
stops = [(37, 99, 235), (6, 182, 212), (139, 92, 246)]
for x in range(W):
    t = x / (W - 1) * 2
    i = min(1, int(t)); f = t - i
    c = tuple(round(stops[i][k] + (stops[i + 1][k] - stops[i][k]) * f) for k in range(3))
    for yy in range(8):
        bp[x, yy] = (*c, 255)
base.alpha_composite(bar, (0, H - 8))

# rounded corners
s = 4; R = 28
m = Image.new("L", (W * s, H * s), 0)
ImageDraw.Draw(m).rounded_rectangle((0, 0, W * s - 1, H * s - 1), radius=R * s, fill=255)
base.putalpha(m.resize((W, H), Image.LANCZOS))
base.save(OUT / "transynq-org-hero.png", optimize=True)

# footer strip: "One Platform. Every Movement."
FW, FH = 1600, 120
foot = Image.new("RGBA", (FW, FH), (11, 18, 32, 255))
fp = foot.load()
for x in range(FW):
    t = x / (FW - 1)
    for yy in range(FH):
        r, g, b, _ = fp[x, yy]
        fp[x, yy] = (round(r + (37 - r) * t * 0.55), round(g + (99 - g) * t * 0.55), round(b + (235 - b) * t * 0.55), 255)
fd = ImageDraw.Draw(foot)
txt = "One Platform. Every Movement."
f = semi(40)
tw = fd.textlength(txt, font=f)
fd.text(((FW - tw) / 2, (FH - 52) / 2), txt, font=f, fill=(248, 250, 252))
m = Image.new("L", (FW * s, FH * s), 0)
ImageDraw.Draw(m).rounded_rectangle((0, 0, FW * s - 1, FH * s - 1), radius=22 * s, fill=255)
foot.putalpha(m.resize((FW, FH), Image.LANCZOS))
foot.save(OUT / "transynq-org-footer.png", optimize=True)
print("ok")
