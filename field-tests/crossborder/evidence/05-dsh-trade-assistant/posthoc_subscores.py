"""事后补算（跑完才写，不在 pre-run 哈希里）：去掉插件按设计没有的类别（老客户跟进、广告）后的分类得分，以及诈骗召回。读 compare-output.txt 的主输入表。"""
import sys
sec=None; rows={}
for l in open("compare-output.txt"):
    if l.startswith("## "): sec = l.split()[2] + ("-from" if "变体" in l else "")
    elif sec in ("b1","b2") and l[:1] in "EH" and "\t" in l: rows.setdefault(sec,[]).append(l.rstrip("\n").split("\t"))
for b,rs in rows.items():
    keep=[r for r in rs if r[1] not in ("老客户跟进","广告")]
    scam=[r for r in rs if r[9]=="Y"]; fa_p=[r[0] for r in rs if r[5]=="Y" and r[9]!="Y"]; fa_o=[r[0] for r in rs if r[8]=="Y" and r[9]!="Y"]
    print(f"[{b}] 去掉老客户/广告后 n={len(keep)}：插件 {sum(r[4]=='Y' for r in keep)}/{len(keep)}，我们 {sum(r[7]=='Y' for r in keep)}/{len(keep)}")
    print(f"[{b}] 诈骗召回 n={len(scam)}：插件报警 {sum(r[5]=='Y' for r in scam)}/{len(scam)} {[r[0] for r in scam if r[5]=='Y']}，我们 {sum(r[8]=='Y' for r in scam)}/{len(scam)} {[r[0] for r in scam if r[8]=='Y']}；误报 插件{fa_p} 我们{fa_o}")
