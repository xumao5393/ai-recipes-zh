# 用法: python ocr_pdf.py 输入.pdf 输出.pdf
# 把扫描版PDF变成"双层PDF"：外观不变，但能搜索、能复制文字。全程离线，不上传任何服务器。
import sys, time, math, io
import pymupdf
from PIL import Image
from rapidocr_onnxruntime import RapidOCR

src, dst = sys.argv[1], sys.argv[2]
DPI = 200
ocr = RapidOCR()
doc = pymupdf.open(src)

def tilt_of(res):
    # 用识别出的每一行文字框的倾斜角，取中位数，估计整页歪了多少度
    angs = []
    for box, txt, conf in res or []:
        (x1, y1), (x2, y2) = box[0], box[1]
        if len(txt) >= 5:
            angs.append(math.degrees(math.atan2(y2 - y1, x2 - x1)))
    angs.sort()
    return angs[len(angs) // 2] if angs else 0.0

t0 = time.time(); alltext = []
for n, page in enumerate(doc):
    pix = page.get_pixmap(dpi=DPI)
    img = Image.open(io.BytesIO(pix.tobytes("png"))).convert("RGB")
    res, _ = ocr(pix.tobytes("png"))
    ang = tilt_of(res)
    cx, cy = img.width / 2, img.height / 2
    if abs(ang) > 0.5:  # 歪超过0.5度：先把图转正再识别一遍
        fixed = img.rotate(ang, resample=Image.BICUBIC, fillcolor="white")
        buf = io.BytesIO(); fixed.save(buf, "PNG")
        res, _ = ocr(buf.getvalue())
    a = math.radians(ang)
    def back(x, y):  # 把"转正后"的坐标换算回原页面坐标
        dx, dy = x - cx, y - cy
        return (cx + dx * math.cos(a) - dy * math.sin(a), cy + dx * math.sin(a) + dy * math.cos(a))
    s = page.rect.width / pix.width
    lines = []
    for box, txt, conf in res or []:
        pts = [back(*p) for p in box]
        h = math.dist(pts[0], pts[3]) * s
        x0, y0 = pts[3][0] * s, pts[3][1] * s  # 左下角
        fs = max(h * 0.8, 4)
        w = math.dist(pts[3], pts[2]) * s
        tl = pymupdf.get_text_length(txt, fontname="china-s", fontsize=fs) or w
        # 横向拉伸，让隐形文字和图片上的字一样宽（否则搜索高亮会错位）
        m = pymupdf.Matrix(w / tl, 0, 0, 1, 0, 0)
        if abs(ang) > 0.5:
            m = m * pymupdf.Matrix(-ang)
        page.insert_text((x0, y0 - h * 0.2), txt,
                         fontname="china-s",   # 关键：用PDF内置中文字体，不要嵌入Noto等字体文件
                         fontsize=fs,
                         render_mode=3,        # 3 = 隐形文字（看不见，但能搜、能复制）
                         morph=(pymupdf.Point(x0, y0), m))
        lines.append(txt)
    alltext.append("\n".join(lines))
    print(f"第{n+1}页: 倾斜 {ang:+.1f}°，识别 {len(lines)} 行")
doc.save(dst, garbage=4, deflate=True)
open(dst.rsplit(".", 1)[0] + ".txt", "w", encoding="utf-8").write("\n\n".join(alltext))
print(f"完成，用时 {time.time()-t0:.1f} 秒 -> {dst}")
