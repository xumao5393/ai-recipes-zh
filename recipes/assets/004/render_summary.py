from PIL import Image,ImageDraw,ImageFont
W,H=1080,1350
im=Image.new('RGB',(W,H),'#FAFAF7');d=ImageDraw.Draw(im)
R='/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc';B='/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc'
def f(p,s): return ImageFont.truetype(p,s,index=2)
ink='#1B1B1B';mut='#6B6B6B';acc='#C2410C';grn='#15803D'
d.rectangle([0,0,W,14],fill=acc)
d.text((64,52),'ai-recipes-zh · 004 · 实测 2026-11-10',font=f(R,26),fill=mut)
d.text((64,100),'双11 拆单用券，让 AI 算',font=f(B,60),fill=ink)
d.text((64,180),'4 个免费 AI，只有 1 个算到最省',font=f(B,42),fill=acc)
d.text((64,246),'同一车货 · 今年的消费券 · 电脑穷举答案 1218 元',font=f(R,28),fill=mut)
y=304;cols=[64,450,620,790]
for x,t in zip(cols,['AI（duck.ai 免登录）','总实付','得分','问题']): d.text((x,y),t,font=f(B,27),fill=ink)
y+=48;d.line([64,y,W-64,y],fill='#D4D4D4',width=2)
rows=[('Claude Haiku 5.5','1218','6/6','无',grn),('GPT-6 Luna','1223','2/6','丢了 25 元券',acc),('GPT-5.4 mini','1223','2/6','丢了 25 元券',acc),('Mistral Small 4','1198','1/6','违反门槛 2 处',acc)]
for n,a,b,c,col in rows:
    y+=16;d.text((cols[0],y),n,font=f(B,30),fill=ink)
    d.text((cols[1],y),a,font=f(B,32),fill=grn if a=='1218' else ink);d.text((cols[2],y),b,font=f(B,32),fill=ink);d.text((cols[3],y+2),c,font=f(R,28),fill=col)
    y+=52;d.line([64,y,W-64,y],fill='#E5E5E5',width=1)
y+=26
d.text((64,y),'发现',font=f(B,32),fill=ink);y+=52
pts=['正解拆 3 单 1218 元，全放一单要 1283 元','乙店少用 20 元店铺券，才够得上满200减25','比正解还低的 1198 是假省：它违反了门槛','为凑满1500买枕头，总价反而多 114 元']
for p in pts:
    d.ellipse([70,y+14,82,y+26],fill=acc);d.text((100,y),p,font=f(R,29),fill=ink);y+=46
y+=22
d.rounded_rectangle([64,y,W-64,y+236],radius=18,fill='#FFF1E8')
d.text((92,y+20),'0 元配方（约 10 分钟）',font=f(B,32),fill=acc)
yy=y+72
for s in ['① 把券的门槛、每单几张写清楚','② duck.ai 选 Claude Haiku 5.5 算','③ 自己核：用完店铺券还够不够消费券门槛','④ 以结算页数字为准再付钱']:
    d.text((92,yy),s,font=f(R,28),fill=ink);yy+=40
d.text((64,H-84),'券面额来自 2026 年 10 月新闻报道（非实测）；千问、豆包、Kimi 等需登录，本期未测',font=f(R,22),fill=mut)
d.text((64,H-50),'github.com/xumao5393/ai-recipes-zh  ·  原始回答与截图全部公开',font=f(R,22),fill=mut)
import os;im.save(os.path.join(os.path.dirname(os.path.abspath(__file__)),'summary.png'));print(yy)
