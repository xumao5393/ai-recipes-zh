# 生成虚构数据：一家小餐馆一周（7天）的订单流水 + 渠道到账记录。全部虚构，固定随机种子可复现。
import csv, random, datetime
random.seed(20261109)
channels = {"堂食-微信":0.0,"堂食-支付宝":0.0,"现金":0.0,"美团外卖":0.18,"抖音团购":0.08}  # 后两者为虚构佣金率
dishes = [("红烧牛肉面",28),("酸菜鱼",58),("宫保鸡丁",36),("米饭",3),("凉拌黄瓜",12),("酸梅汤",8)]
start = datetime.date(2026,11,2)
orders=[]; oid=1
for d in range(7):
    day = start+datetime.timedelta(days=d)
    n = random.randint(60,95)
    for _ in range(n):
        ch = random.choices(list(channels),[30,20,8,30,12])[0]
        items = random.sample(dishes, random.randint(1,3))
        amt = sum(p*random.randint(1,2) for _,p in items)
        refund = 1 if random.random()<0.03 else 0
        hh = random.choice([11,12,12,13,17,18,18,19,20])
        orders.append([f"O{oid:05d}", day.isoformat(), f"{hh}:{random.randint(0,59):02d}", ch, "|".join(i for i,_ in items), amt, refund])
        oid+=1
with open("orders_week.csv","w",newline="",encoding="utf-8") as f:
    w=csv.writer(f); w.writerow(["order_id","date","time","channel","items","amount","refunded"]); w.writerows(orders)
# 到账记录：按天按渠道汇总，故意埋3处差异让报表去抓
settle=[]
agg={}
for o in orders:
    if o[6]: continue
    agg[(o[1],o[3])]=agg.get((o[1],o[3]),0)+o[5]
for (day,ch),gross in sorted(agg.items()):
    net = round(gross*(1-channels[ch]),2)
    settle.append([day,ch,net])
settle[3][2]=round(settle[3][2]-120,2)      # 埋点1：某渠道少到账120
settle[17][2]=round(settle[17][2]-35.5,2)   # 埋点2：现金/某渠道差35.5
del settle[25]                              # 埋点3：某天某渠道整笔未到账
with open("settlement_week.csv","w",newline="",encoding="utf-8") as f:
    w=csv.writer(f); w.writerow(["date","channel","received"]); w.writerows(settle)
print(len(orders),"orders;",len(settle),"settlement rows")
