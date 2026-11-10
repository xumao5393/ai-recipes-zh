import itertools,json
items=[('四件套','甲',359),('收纳箱','甲',129),('床垫保护罩','甲',99),('坚果礼盒','乙',129),('咖啡豆','乙',89),('耳机','丙',399),('移动电源','丙',249)]
opt=('记忆枕','甲',169)
coup={'甲':(500,40),'乙':(200,20),'丙':(600,50)}
VQ=[(200,25),(480,60),(480,60),(1500,180),(1500,180),(3000,400),(5000,650)]
def evalp(orders):
    n=len(orders)
    # shop coupon: each shop to at most one order; choose best placement jointly with vouchers -> brute force placements
    best=None
    shops=list(coup)
    for pl in itertools.product(range(n),repeat=3):
        amt=[]
        for i,o in enumerate(orders):
            s=sum(p for _,_,p in o)
            for sh,oi in zip(shops,pl):
                th,v=coup[sh]
                if oi==i and sum(p for _,x,p in o if x==sh)>=th: s-=v
            amt.append(s)
        # assign vouchers: each order at most one, each voucher once; brute force via permutations of voucher index or none
        vb=0
        idx=list(range(len(VQ)))
        def rec(k,used):
            if k==n: return 0
            b=rec(k+1,used)
            for j in idx:
                if j not in used and amt[k]>=VQ[j][0]:
                    b=max(b,VQ[j][1]+rec(k+1,used|{j}))
            return b
        vb=rec(0,frozenset())
        t=round(sum(amt)-vb,2)
        if best is None or t<best: best=t
    return best
def partitions(lst):
    if not lst: yield [];return
    f=lst[0]
    for p in partitions(lst[1:]):
        for i in range(len(p)): yield p[:i]+[[f]+p[i]]+p[i+1:]
        yield [[f]]+p
out={}
for name,L in [('不加记忆枕',items),('加记忆枕',items+[opt])]:
    allr=sorted(((evalp(p),p) for p in partitions(L)),key=lambda r:(r[0],len(r[1])))
    one=[r for r in allr if len(r[1])==1][0][0]
    print(name,'标价合计',sum(i[2] for i in L),'partitions',len(allr),'一单',one)
    for r in allr[:10]: print(' ',r[0],[[i[0] for i in o] for o in r[1]],[sum(i[2] for i in o) for o in r[1]])
    out[name]={'n_partitions':len(allr),'one_order':one,'best':allr[0][0],'top':[(r[0],[[i[0] for i in o] for o in r[1]]) for r in allr[:20]]}
json.dump(out,open('bf_out.json','w'),ensure_ascii=False,indent=1)
