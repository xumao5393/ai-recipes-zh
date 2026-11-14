# 008 标准答案：被裁 N+1 补偿与个税（Python 3，无第三方依赖）
# 规则：劳动合同法第47条（满1年1个月；6个月以上不满1年按1年；不满6个月半个月；
# 月工资高于当地上年职工月平均工资3倍的按3倍计、年限最高12年）；第40条+实施条例第20条（代通知金=上月工资）；
# 财税〔2018〕164号第五条第（一）项（当地上年职工平均工资3倍以内免税，超过部分单独适用综合所得税率表，不并入当年综合所得）。
import json
BR=[(36000,.03,0),(144000,.10,2520),(300000,.20,16920),(420000,.25,31920),(660000,.30,52920),(960000,.35,85920),(float('inf'),.45,181920)]
def tax(t):
    if t<=0: return 0.0
    for lim,r,q in BR:
        if t<=lim: return round(t*r-q,2)
AVG_M=8000; AVG_Y=96000; CAP_M=3*AVG_M; FREE=3*AVG_Y
def months(y,m):
    return y + (1 if m>=6 else (0.5 if m>0 else 0))
people={'小周':(8000,3,4),'小吴':(22000,12,9),'小郑':(50000,15,2)}
out={'cap_monthly_base':CAP_M,'tax_free_threshold':FREE}
for n,(w,y,m) in people.items():
    nm=months(y,m); base=w
    if w>CAP_M: base=CAP_M; nm=min(nm,12)
    N=nm*base; plus1=w; tot=N+plus1
    excess=max(0,tot-FREE); t=tax(excess)
    out[n]={'N_months':nm,'N_base':base,'N':N,'plus1':plus1,'total':tot,'taxable_excess':excess,'tax':t,'net':tot-t}
out['merge_with_salary']='不合并：超过免税额的部分单独适用综合所得税率表计税'
out['hr_claim_xiaozheng']='HR 对：月工资超当地月平均工资3倍，按24000元/月计且最多12年，法定N=288000（公司自愿多给不违法）'
print(json.dumps(out,ensure_ascii=False,indent=1))
json.dump(out,open('answer_key.json','w'),ensure_ascii=False,indent=1)

# 第 2 轮（prompt2.txt）：HR 明细核对（小吴同款数据：2014-03-10 入职，2026-12-31 解除，12 年 9 个月 21 天）
hr={'N':12.5*18000,'plus1':18000,'total':243000,'tax':40580,'net':202420}
legal_N=months(12,9)*22000; legal_total=legal_N+22000; legal_tax=tax(max(0,legal_total-FREE))
out['round2']={'hr':hr,'legal_N_months':months(12,9),'legal_N':legal_N,'legal_plus1':22000,'legal_total':legal_total,
  'legal_tax':legal_tax,'legal_net':legal_total-legal_tax,'pre_tax_shortfall':legal_total-hr['total'],
  'over_withheld_tax':round(hr['tax']-legal_tax,2),'net_shortfall':round(legal_total-legal_tax-hr['net'],2)}
print(json.dumps(out['round2'],ensure_ascii=False,indent=1))
json.dump(out,open('answer_key.json','w'),ensure_ascii=False,indent=1)
