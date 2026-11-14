# 007 标准答案：个人养老金 12000 元该不该存（Python 3，无第三方依赖）
import json
BR=[(36000,.03,0),(144000,.10,2520),(300000,.20,16920),(420000,.25,31920),(660000,.30,52920),(960000,.35,85920),(float('inf'),.45,181920)]
def tax(t):
    if t<=0: return 0.0
    for lim,r,q in BR:
        if t<=lim: return round(t*r-q,2)
def rate(t):
    if t<=0: return 0.0
    for lim,r,q in BR:
        if t<=lim: return r
people={'小王':(7000,1500,0),'小李':(23000,4000,1500),'小张':(45000,6000,2000)}
g=1.015**30; out={'growth_30y':round(g,6)}
for n,(s,si,sp) in people.items():
    ti=12*s-60000-12*si-12*sp
    t0=tax(ti); t1=tax(ti-12000); save=round(t0-t1,2)
    fv=12000*g; wtax=round(fv*.03,2)
    net=round(save*g-wtax,2)
    # 最优缴费额：扣除只在应纳税所得额>0 的部分有效
    best=0 if save/12000<=0.03 else 12000
    out[n]={'taxable_income':ti,'marginal_rate':rate(ti),'tax_without':t0,'tax_with_12000':t1,'tax_saved_2026':save,
            'pension_value_30y':round(fv,2),'withdrawal_tax_30y':wtax,'net_gain_vs_not_30y':net,'recommended_contribution':best}
out['dec28']='12 月 31 日前缴费计入 2026 年度扣除；未在预扣环节扣的，在 2027 年 3 月 1 日—6 月 30 日综合所得汇算清缴时申报退税'
print(json.dumps(out,ensure_ascii=False,indent=1))
json.dump(out,open('answer_key.json','w'),ensure_ascii=False,indent=1)
