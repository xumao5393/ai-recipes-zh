from PIL import Image,ImageDraw,ImageFont
import os
W,H=1080,1350
im=Image.new('RGB',(W,H),'#FAFAF7');d=ImageDraw.Draw(im)
R='/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc';B='/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc'
def f(p,s): return ImageFont.truetype(p,s,index=2)
ink='#1B1B1B';mut='#6B6B6B';acc='#C2410C';grn='#15803D'
d.rectangle([0,0,W,14],fill=acc)
d.text((64,52),'ai-recipes-zh · 005 · 实测 2026-11-11',font=f(R,26),fill=mut)
d.text((64,100),'年终奖 3.6 万还是 3.8 万？',font=f(B,60),fill=ink)
d.text((64,180),'5 个免费 AI，2 个踩了“3000 元雷区”',font=f(B,42),fill=acc)
d.text((64,246),'月薪 1.5 万 · 同一段提示词 · 电脑算出正解：选 B 并入，多 120 元',font=f(R,27),fill=mut)
y=304;cols=[64,420,600,740]
for x,t in zip(cols,['AI（免登录）','推荐','得分','问题']): d.text((x,y),t,font=f(B,27),fill=ink)
y+=48;d.line([64,y,W-64,y],fill='#D4D4D4',width=2)
rows=[('Claude Haiku 5.5','B 并入','5/5','无',grn),('GPT-6 Luna','B 并入','5/5','无（自动联网）',grn),('元宝 Instant','B 并入','5/5','无（自动联网）',grn),('GPT-5.4 mini','B 单独','1/5','3166 元放进 3% 档',acc),('Mistral Small 4','B 单独','1/5','税率档+工资税都错',acc)]
for n,a,b,c,col in rows:
    y+=14;d.text((cols[0],y),n,font=f(B,30),fill=ink)
    d.text((cols[1],y),a,font=f(B,30),fill=grn if a=='B 并入' else acc);d.text((cols[2],y),b,font=f(B,30),fill=ink);d.text((cols[3],y+2),c,font=f(R,27),fill=col)
    y+=50;d.line([64,y,W-64,y],fill='#E5E5E5',width=1)
y+=24
d.text((64,y),'发现',font=f(B,32),fill=ink);y+=50
pts=['38000 单独计税要交 3590，并入只多交 2960','“别超 36000”只看了单独计税，换并入就不成立','照错的 AI 选 B+单独，到手 34410，比 A 还少','单位已按单独扣了也能改：次年 3-6 月汇算']
for p in pts:
    d.ellipse([70,y+14,82,y+26],fill=acc);d.text((100,y),p,font=f(R,29),fill=ink);y+=46
y+=20
d.rounded_rectangle([64,y,W-64,y+236],radius=18,fill='#FFF1E8')
d.text((92,y+20),'0 元配方（约 10 分钟）',font=f(B,32),fill=acc)
yy=y+72
for s in ['① 把月薪、五险一金、专项附加、两档奖金写清','② duck.ai 选 Claude Haiku 5.5，或元宝免登录','③ 自己核：奖金÷12 超过 3000 就不是 3%','④ 次年汇算在个税 App 里两种方式都点一遍']:
    d.text((92,yy),s,font=f(R,28),fill=ink);yy+=40
d.text((64,H-84),'千问、Kimi、DeepSeek、豆包需登录，智谱超时，本期未测；税务规则出处见正文',font=f(R,22),fill=mut)
d.text((64,H-50),'github.com/xumao5393/ai-recipes-zh  ·  原始回答与截图全部公开',font=f(R,22),fill=mut)
im.save(os.path.join(os.path.dirname(os.path.abspath(__file__)),'summary.png'));print(yy,H)
