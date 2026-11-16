import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter
out = Path(sys.argv[1]); dark = Image.open(out / "transynq-logo-dark.png").convert("RGBA")
W, H, R = 1600, 400, 36
base = Image.new("RGBA", (W, H), (11, 18, 32, 255))
glow = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(glow)
d.ellipse((1050, -350, 1850, 350), fill=(37, 99, 235, 80)); d.ellipse((-350, 150, 450, 750), fill=(139, 92, 246, 55))
base = Image.alpha_composite(base, glow.filter(ImageFilter.GaussianBlur(110)))
lw = 1000; logo = dark.resize((lw, round(dark.height * lw / dark.width)), Image.LANCZOS)
base.alpha_composite(logo, ((W - lw) // 2, (H - logo.height) // 2))
s = 4; m = Image.new("L", (W * s, H * s), 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, W * s - 1, H * s - 1), radius=R * s, fill=255)
base.putalpha(m.resize((W, H), Image.LANCZOS))
base.save(out / "transynq-readme-banner.png", optimize=True); print((out / "transynq-readme-banner.png").stat().st_size)
