# 自动预检：在每份回答里找关键数字（只是预检，最终以人工逐句核对 scoring.json 为准）
import os,re,json
D=os.path.join(os.path.dirname(os.path.abspath(__file__)),'answers')
keys={'A单独1800':'1800','A并入3480':'3480','B单独4310':'4310','B并入3680':'3680','B到手35040':'35040','多120':'120','汇算3月1日':'3 ?月 ?1 ?日'}
res={}
for f in sorted(os.listdir(D)):
    t=open(os.path.join(D,f)).read().replace(',','').replace('，','')
    res[f]={k:bool(re.search(r'(?<!\d)'+v+r'(?!\d)',t)) for k,v in keys.items()}
print(json.dumps(res,ensure_ascii=False,indent=1))
