"""把一段文字（AI 的原始输出）原样渲染成 PNG 截图，方便放进文章。用法：python render_text_png.py 输入.md 输出.png "标题" "#颜色" """
import sys, textwrap
from PIL import Image, ImageDraw, ImageFont
F = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
FB = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"
src, out, title = sys.argv[1], sys.argv[2], sys.argv[3]
color = sys.argv[4] if len(sys.argv) > 4 else "#334155"
W = 1400; PAD = 40
font = ImageFont.truetype(F, 22, index=2); ft = ImageFont.truetype(FB, 30, index=2)
d0 = ImageDraw.Draw(Image.new("RGB", (10, 10)))
lines = []
for raw in open(src, encoding="utf-8").read().splitlines():
    cur = ""
    for ch in raw:
        if d0.textlength(cur + ch, font=font) > W - 2 * PAD:
            lines.append(cur); cur = ""
        cur += ch
    lines.append(cur)
H = 110 + len(lines) * 32 + PAD
img = Image.new("RGB", (W, H), "#ffffff"); d = ImageDraw.Draw(img)
d.rectangle([0, 0, W, 80], fill=color)
d.text((PAD, 20), title, font=ft, fill="#ffffff")
y = 100
for l in lines:
    d.text((PAD, y), l, font=font, fill="#111827"); y += 32
img.save(out); print(out, img.size)
