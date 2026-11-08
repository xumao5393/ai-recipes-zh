# 验收：1) 字符准确率  2) 在PDF里搜索关键词  3) 关键数字是否识别对
import difflib, re, sys, pymupdf
gt = re.sub(r"\s", "", open("ground_truth.txt", encoding="utf-8").read())
doc = pymupdf.open(sys.argv[1] if len(sys.argv)>1 else "output_searchable.pdf")
got = re.sub(r"\s", "", "".join(p.get_text() for p in doc))
sm = difflib.SequenceMatcher(None, gt, got, autojunk=False)
print(f"原文 {len(gt)} 字，识别 {len(got)} 字，字符匹配率 {sm.ratio()*100:.1f}%")
for kw in ["押金", "违约金", "4200", "8400", "优先承租权", "李晓梅"]:
    hits = [(i+1) for i,p in enumerate(doc) if p.search_for(kw)]
    print(f"搜索「{kw}」: 命中页 {hits}")
P = r"[\s，。：；、．.,:;￥（）()➀]"
a = re.sub(P, "", gt); b = re.sub(P, "", got)
r = difflib.SequenceMatcher(None, a, b, autojunk=False)
print(f"去掉标点后：原文 {len(a)} 字，汉字/数字匹配率 {r.ratio()*100:.1f}%")
for tag,i1,i2,j1,j2 in r.get_opcodes():
    if tag!="equal": print(f"  错字[{tag}] 原文「{a[i1:i2]}」-> 识别「{b[j1:j2]}」")
