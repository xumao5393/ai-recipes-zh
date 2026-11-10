# 自动预检：检查每份回答里是否出现关键正确数字与“乙店不用店铺券”的判断；最终评分以人工逐句核对的 scoring.json 为准
import re,json,glob,os
D=os.path.dirname(os.path.abspath(__file__))
res={}
for f in sorted(glob.glob(os.path.join(D,'answers','duckai-*.txt'))):
    if f.endswith('.export.txt'): continue
    t=open(f,encoding='utf-8').read().split('---',1)[1]
    t=re.sub(r'<!--.*?-->','',t,flags=re.S)  # 去掉界面隐藏的思考注释
    res[os.path.basename(f)[:-4]]={
     '提到1218':'1218' in t,'提到1283':'1283' in t,'提到省65':bool(re.search(r'省\D{0,6}65|65\s*元',t)),
     '提到1332':'1332' in t,'提到114':'114' in t,'乙店不用店铺券':bool(re.search(r'不用乙店券|乙店.{0,6}不用|不用.{0,4}乙店',t)),
     '出现198减25(违反门槛)':bool(re.search(r'198\s*-\s*25',t))}
json.dump(res,open(os.path.join(D,'scoring_auto.json'),'w'),ensure_ascii=False,indent=1);print(json.dumps(res,ensure_ascii=False,indent=1))
