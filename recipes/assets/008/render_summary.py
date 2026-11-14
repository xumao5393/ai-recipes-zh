from PIL import Image,ImageDraw,ImageFont
import os
W,H=1080,1350
im=Image.new('RGB',(W,H),'#FAFAF7');d=ImageDraw.Draw(im)
R='/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc';B='/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc'
def f(p,s): return ImageFont.truetype(p,s,index=2)
ink='#1B1B1B';mut='#6B6B6B';acc='#C2410C';grn='#15803D'
d.rectangle([0,0,W,14],fill=acc)
d.text((64,52),'ai-recipes-zh · 008 · 实测 2026-11-14',font=f(R,26),fill=mut)
d.text((64,100),'年底被裁 N+1，HR 明细能签吗？',font=f(B,56),fill=ink)
d.text((64,178),'示例明细少给 104980 元，AI 能不能挑出来',font=f(B,38),fill=acc)
d.text((64,240),'同一份明细 · 不提示错在哪 · 脚本按法条和税率表算正解',font=f(R,27),fill=mut)
y=300;cols=[64,420,600,760]
for x,t in zip(cols,['AI','算账题','审 HR 明细','问题']): d.text((x,y),t,font=f(B,27),fill=ink)
y+=48;d.line([64,y,W-64,y],fill='#D4D4D4',width=2)
rows=[('元宝（访客）','7/7','6/6','无大错',grn),('ChatGPT（访客）','7/7','要登录','第 2 次被拦',mut),('GLM-5.3-Flash','7/7','没出字','卡在思考',mut),('Gemini Flash-Lite','7/7','4/6','税 600 估成 1–2 万',acc)]
for n,a,b,c,col in rows:
    y+=14;d.text((cols[0],y),n,font=f(B,30),fill=ink)
    d.text((cols[1],y),a,font=f(B,30),fill=grn);d.text((cols[2],y),b,font=f(B,30),fill=grn if b=='6/6' else (acc if b=='4/6' else mut));d.text((cols[3],y+2),c,font=f(R,27),fill=col)
    y+=50;d.line([64,y,W-64,y],fill='#E5E5E5',width=1)
y+=24
d.text((64,y),'HR 明细里的三招（月薪 2.2 万、干了 12 年 9 个月）',font=f(B,32),fill=ink);y+=50
pts=['基数按基本工资 18000，应按应发平均 22000','12 年 9 个月算 12.5，零头满 6 个月应算 13','免税线说成 2.4 万并入工资，应为 28.8 万单独算','实发 202420 → 法定 307400，税只该交 600']
for p in pts:
    d.ellipse([70,y+14,82,y+26],fill=acc);d.text((100,y),p,font=f(R,29),fill=ink);y+=46
y+=20
d.rounded_rectangle([64,y,W-64,y+236],radius=18,fill='#FFF1E8')
d.text((92,y+20),'0 元配方（约 15 分钟）',font=f(B,32),fill=acc)
yy=y+72
for s in ['① 备好：12 个月平均应发工资、入离职日期、当地社平','② 明细原文贴给元宝，问能不能签、税后多少','③ 自己核：基数、零头、12 年上限只管高薪、免税线','④ 有差额书面提出，别当天签']:
    d.text((92,yy),s,font=f(R,28),fill=ink);yy+=40
d.text((64,H-84),'Gemini 为已登录账号；duck.ai 打不开，豆包、Kimi 等需登录，本期未测',font=f(R,22),fill=mut)
d.text((64,H-50),'github.com/xumao5393/ai-recipes-zh  ·  原始回答与截图全部公开',font=f(R,22),fill=mut)
im.save(os.path.join(os.path.dirname(os.path.abspath(__file__)),'summary.png'));print(yy,H)
