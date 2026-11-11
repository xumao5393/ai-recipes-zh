import json
def annual(x):
    for lim,r,q in [(36000,.03,0),(144000,.10,2520),(300000,.20,16920),(420000,.25,31920),(660000,.30,52920),(960000,.35,85920),(1e18,.45,181920)]:
        if x<=lim: return max(0,round(x*r-q,2))
def monthly_bonus(b):
    m=b/12
    for lim,r,q in [(3000,.03,0),(12000,.10,210),(25000,.20,1410),(35000,.25,2660),(55000,.30,4410),(80000,.35,7160),(1e18,.45,15160)]:
        if m<=lim: return round(b*r-q,2)
salary=15000*12; ded=60000+3000*12+5000*12
base_taxable=salary-ded; base_tax=annual(base_taxable)
out={'salary_taxable':base_taxable,'salary_only_tax':base_tax,'plans':{}}
for name,b in [('A',36000),('B',38000)]:
    sep=base_tax+monthly_bonus(b); mer=annual(base_taxable+b)
    best=min(('单独计税',sep),('并入综合所得',mer),key=lambda t:t[1])
    out['plans'][name]={'bonus':b,'separate_total_tax':sep,'merged_total_tax':mer,'best_method':best[0],'best_total_tax':best[1],'bonus_net':round(b-(best[1]-base_tax),2),
      'bonus_net_if_separate':round(b-(sep-base_tax),2)}
out['answer']={'choose':'B','method':'并入综合所得','B_minus_A_net':round(out['plans']['B']['bonus_net']-out['plans']['A']['bonus_net'],2),
 'naive_trap':'只看单独计税会觉得A更好：A净到手%s，B单独计税净到手%s'%(out['plans']['A']['bonus_net_if_separate'],out['plans']['B']['bonus_net_if_separate']),
 'q4':'可以：在次年（2027年）3月1日至6月30日综合所得年度汇算时，在个人所得税App里重新选择计税方式（反过来，预扣时已并入的想改单独计税，要找单位更正预扣申报）'}
# sweep: bonus amounts 30000-50000 where 1 more yuan of pretax gives less net, for both methods
print(json.dumps(out,ensure_ascii=False,indent=1))
json.dump(out,open('answer_key.json','w'),ensure_ascii=False,indent=1)
