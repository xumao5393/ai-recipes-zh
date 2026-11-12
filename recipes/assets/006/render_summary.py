from PIL import Image,ImageDraw,ImageFont
import os
W,H=1080,1350
im=Image.new('RGB',(W,H),'#FAFAF7');d=ImageDraw.Draw(im)
R='/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc';B='/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc'
def f(p,s): return ImageFont.truetype(p,s,index=2)
ink='#1B1B1B';mut='#6B6B6B';acc='#C2410C';grn='#15803D'
d.rectangle([0,0,W,14],fill=acc)
d.text((64,52),'ai-recipes-zh · 006 · 实测 2026-11-12',font=f(R,26),fill=mut)
d.text((64,100),'分期“每期 0.6%”，真实年化 13%',font=f(B,56),fill=ink)
d.text((64,178),'5 个免费 AI，只有 1 个全对，1 个劝你选“免息”',font=f(B,38),fill=acc)
d.text((64,240),'7999 元手机 · 立减 300 · 同一段提示词 · 脚本算正解：一次付清',font=f(R,27),fill=mut)
y=300;cols=[64,400,560,700]
for x,t in zip(cols,['AI（免登录）','选择','得分','问题']): d.text((x,y),t,font=f(B,27),fill=ink)
y+=48;d.line([64,y,W-64,y],fill='#D4D4D4',width=2)
rows=[('Claude Haiku 5.5','D 付清','5/5','无',grn),('GPT-6 Luna','D 付清','3/5','A、C 年化算偏',acc),('元宝 Instant','D 付清','2/5','“免息”算成 0%',acc),('GPT-5.4 mini','D 付清','1/5','前后排序矛盾',acc),('Mistral Small 4','C 免息','1/5','0.6%×12=7.2%',acc)]
for n,a,b,c,col in rows:
    y+=14;d.text((cols[0],y),n,font=f(B,30),fill=ink)
    d.text((cols[1],y),a,font=f(B,30),fill=grn if a.startswith('D') else acc);d.text((cols[2],y),b,font=f(B,30),fill=ink);d.text((cols[3],y+2),c,font=f(R,27),fill=col)
    y+=50;d.line([64,y,W-64,y],fill='#E5E5E5',width=1)
y+=24
d.text((64,y),'标准答案（真实年化，IRR 名义）',font=f(B,32),fill=ink);y+=50
pts=['信用卡分期 0.6%/期 → 13.0%，不是 7.2%','“免息但不立减” → 7.1%，不是 0%','消费贷写明 15% → 15.0%（5 个 AI 全对）','一次付清比第二名多剩 247 元']
for p in pts:
    d.ellipse([70,y+14,82,y+26],fill=acc);d.text((100,y),p,font=f(R,29),fill=ink);y+=46
y+=20
d.rounded_rectangle([64,y,W-64,y+236],radius=18,fill='#FFF1E8')
d.text((92,y+20),'0 元配方（约 10 分钟）',font=f(B,32),fill=acc)
yy=y+72
for s in ['① 把每种付法写成“哪天付多少钱”','② duck.ai 选 Claude Haiku 5.5 算 IRR 年化','③ 自己核：每期费率×12 再乘约 1.8 才是真年化','④ 免息不立减，年化一定不是 0']:
    d.text((92,yy),s,font=f(R,28),fill=ink);yy+=40
d.text((64,H-84),'千问、DeepSeek、Kimi、ChatGPT、Grok 需登录，智谱超时，本期未测',font=f(R,22),fill=mut)
d.text((64,H-50),'github.com/xumao5393/ai-recipes-zh  ·  原始回答与截图全部公开',font=f(R,22),fill=mut)
im.save(os.path.join(os.path.dirname(os.path.abspath(__file__)),'summary.png'));print(yy,H)
