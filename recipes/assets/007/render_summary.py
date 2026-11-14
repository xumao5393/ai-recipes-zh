from PIL import Image,ImageDraw,ImageFont
import os
W,H=1080,1350
im=Image.new('RGB',(W,H),'#FAFAF7');d=ImageDraw.Draw(im)
R='/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc';B='/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc'
def f(p,s): return ImageFont.truetype(p,s,index=2)
ink='#1B1B1B';mut='#6B6B6B';acc='#C2410C';grn='#15803D'
d.rectangle([0,0,W,14],fill=acc)
d.text((64,52),'ai-recipes-zh · 007 · 实测 2026-11-13',font=f(R,26),fill=mut)
d.text((64,100),'年底存个人养老金 1.2 万，谁该存？',font=f(B,56),fill=ink)
d.text((64,178),'5 个免费 AI：2 个全对，3 个算错月薪 2.3 万这档',font=f(B,38),fill=acc)
d.text((64,240),'三个收入档 · 同一段提示词 · 脚本按年度税率表算正解',font=f(R,27),fill=mut)
y=300;cols=[64,400,560,700]
for x,t in zip(cols,['AI（免登录）','小李少交','得分','问题']): d.text((x,y),t,font=f(B,27),fill=ink)
y+=48;d.line([64,y,W-64,y],fill='#D4D4D4',width=2)
rows=[('GPT-6 Luna','1800','7/7','无',grn),('元宝 Instant','1800','7/7','无',grn),('Claude Haiku 5.5','2400','4/7','没发现跨档',acc),('GPT-5.4 mini','2400','3/7','漏掉 6 万减除',acc),('Mistral Small 4','1200','3/7','劝月薪 7000 存满',acc)]
for n,a,b,c,col in rows:
    y+=14;d.text((cols[0],y),n,font=f(B,30),fill=ink)
    d.text((cols[1],y),a,font=f(B,30),fill=grn if a=='1800' else acc);d.text((cols[2],y),b,font=f(B,30),fill=ink);d.text((cols[3],y+2),c,font=f(R,27),fill=col)
    y+=50;d.line([64,y,W-64,y],fill='#E5E5E5',width=1)
y+=24
d.text((64,y),'标准答案（存满 12000，30 年后对比不存）',font=f(B,32),fill=ink);y+=50
pts=['月薪 7000：只省 180，领取交 563，30 年后少 281，别存','月薪 2.3 万：20% 掉回 10% 档，省 1800 不是 2400','月薪 4.5 万：25% 档省 3000，30 年后多 4127','12 月 31 日前到账算今年，明年 3—6 月汇算退税']
for p in pts:
    d.ellipse([70,y+14,82,y+26],fill=acc);d.text((100,y),p,font=f(R,29),fill=ink);y+=46
y+=20
d.rounded_rectangle([64,y,W-64,y+236],radius=18,fill='#FFF1E8')
d.text((92,y+20),'0 元配方（约 10 分钟）',font=f(B,32),fill=acc)
yy=y+72
for s in ['① 先算应纳税所得额：年薪−6万−社保公积金−专项附加','② 交给 GPT-6 Luna 或元宝，算存与不存各交多少税','③ 在 3% 档或所得额不到 1.2 万：不用存','④ 离分档线不到 1.2 万：省的税要分两段算']:
    d.text((92,yy),s,font=f(R,28),fill=ink);yy+=40
d.text((64,H-84),'豆包需登录（区域限制），千问、DeepSeek、Kimi 需登录，本期未测',font=f(R,22),fill=mut)
d.text((64,H-50),'github.com/xumao5393/ai-recipes-zh  ·  原始回答与截图全部公开',font=f(R,22),fill=mut)
im.save(os.path.join(os.path.dirname(os.path.abspath(__file__)),'summary.png'));print(yy,H)
