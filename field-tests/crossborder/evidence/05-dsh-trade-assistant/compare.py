"""逐封对比：dsh-trade-assistant vs 03 锁定关键词脚本。用法: python3 compare.py mapping.json truth.csv plugin.json ours.tsv 批次名"""
import json, csv, sys
m = json.load(open(sys.argv[1])); truth = {r["id"]: r["正确分类"] for r in csv.DictReader(open(sys.argv[2]))}
plug = {r["id"]: r for r in json.load(open(sys.argv[3]))}
ours = {l.split("\t")[0]: l.split("\t")[1] for l in open(sys.argv[4]).read().strip().splitlines()}
ids = sorted(truth); po = oo = pa = oa = 0
print("id\t正确\t插件原类\t插件映射\t插件对?\t插件报警\t我们\t我们对?\t我们报警\t该报警")
for i in ids:
    t = truth[i]; p = plug[i]; pm = m["type_map"].get(p["inquiry_type"], "无对应")
    palarm = p["inquiry_type"] == "钓鱼/诈骗" or any(f["level"] in ("高危", "中危") for f in p["red_flags"])
    oalarm = ours[i] == "诈骗/钓鱼风险"; should = t == "诈骗/钓鱼风险"
    po += pm == t; oo += ours[i] == t; pa += palarm == should; oa += oalarm == should
    print(f"{i}\t{t}\t{p['inquiry_type']}\t{pm}\t{'Y' if pm==t else 'N'}\t{'Y' if palarm else '-'}\t{ours[i]}\t{'Y' if ours[i]==t else 'N'}\t{'Y' if oalarm else '-'}\t{'Y' if should else '-'}")
n = len(ids)
print(f"[{sys.argv[5]}] 分类对：插件 {po}/{n}，我们 {oo}/{n}；报警判断对（该报/不该报都算）：插件 {pa}/{n}，我们 {oa}/{n}")
