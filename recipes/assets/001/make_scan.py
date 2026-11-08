# 生成一份"模拟扫描件"：中文文字渲染成图片，加噪点、轻微倾斜、灰底，再存成纯图片PDF
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import random, pymupdf as fitz
random.seed(1)
F="/usr/share/fonts/opentype/noto/NotoSerifCJK-Regular.ttc"
font=ImageFont.truetype(F,34)
text=open("ground_truth.txt",encoding="utf-8").read().strip().split("\n")
pages=[text[:14],text[14:]]
doc=fitz.open()
for i,lines in enumerate(pages):
    im=Image.new("L",(1654,2339),235); d=ImageDraw.Draw(im)
    y=160
    for l in lines: d.text((150,y),l,font=font,fill=30); y+=70
    im=im.rotate(float(__import__("os").environ.get("ROT","1.2")),fillcolor=235,expand=False)
    px=im.load()
    for _ in range(60000):
        x,yy=random.randrange(1654),random.randrange(2339); px[x,yy]=random.choice([60,120,200])
    im=im.filter(ImageFilter.GaussianBlur(float(__import__("os").environ.get("BLUR","0.8"))))
    im.convert("RGB").save(f"scan_page{i+1}.jpg",quality=70)
    p=doc.new_page(width=595,height=842); p.insert_image(p.rect,filename=f"scan_page{i+1}.jpg")
doc.save(__import__("os").environ.get("OUT","input_scanned.pdf"))
print("ok")
