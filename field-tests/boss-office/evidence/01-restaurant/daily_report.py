# 读订单流水+到账记录，生成每日日结简报（Markdown），并标出应收与实收差异。
# 佣金率是老板必须提供/确认的参数，这里是虚构值。
import csv, sys, collections
RATE={"堂食-微信":0.0,"堂食-支付宝":0.0,"现金":0.0,"美团外卖":0.18,"抖音团购":0.08}
TOL=1.0  # 允许误差（元），老板可调
orders=list(csv.DictReader(open("orders_week.csv",encoding="utf-8")))
settle={(r["date"],r["channel"]):float(r["received"]) for r in csv.DictReader(open("settlement_week.csv",encoding="utf-8"))}
days=sorted({o["date"] for o in orders})
out=["# 一周日结简报（虚构数据）",""]
alerts=[]
for d in days:
    od=[o for o in orders if o["date"]==d]
    valid=[o for o in od if o["refunded"]=="0"]
    gross=sum(int(o["amount"]) for o in valid)
    refunds=[o for o in od if o["refunded"]=="1"]
    bych=collections.defaultdict(float)
    for o in valid: bych[o["channel"]]+=int(o["amount"])
    dish=collections.Counter()
    for o in valid:
        for i in o["items"].split("|"): dish[i]+=1
    lunch=sum(1 for o in valid if int(o["time"].split(":")[0])<15)
    out+= [f"## {d}",f"- 有效订单 {len(valid)} 单，营业额（未扣佣金）{gross} 元，客单价 {gross/len(valid):.1f} 元",
           f"- 午市 {lunch} 单 / 晚市 {len(valid)-lunch} 单；退款 {len(refunds)} 单，金额 {sum(int(o['amount']) for o in refunds)} 元",
           f"- 出现次数前三的菜：{'、'.join(f'{k}({v})' for k,v in dish.most_common(3))}",
           "","| 渠道 | 应收(扣佣金后) | 实收 | 差额 |","|---|---|---|---|"]
    for ch in RATE:
        exp=round(bych.get(ch,0)*(1-RATE[ch]),2)
        if exp==0 and (d,ch) not in settle: continue
        got=settle.get((d,ch))
        diff=None if got is None else round(got-exp,2)
        flag=""
        if got is None: flag=" ⚠️未到账"; alerts.append(f"{d} {ch} 应收 {exp} 元，没有到账记录")
        elif abs(diff)>TOL: flag=" ⚠️"; alerts.append(f"{d} {ch} 应收 {exp}，实收 {got}，差 {diff} 元")
        out.append(f"| {ch} | {exp} | {'—' if got is None else got} | {'—' if diff is None else diff}{flag} |")
    out.append("")
out=out[:2]+["## 需要老板看的异常",""]+[f"- {a}" for a in alerts]+(["- 无"] if not alerts else [])+[""]+out[2:]
open("report_output.md","w",encoding="utf-8").write("\n".join(out))
print("alerts:",len(alerts)); print("\n".join(alerts))
