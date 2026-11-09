from PIL import Image,ImageDraw,ImageFont
W,H=1080,1350
im=Image.new('RGB',(W,H),'#FAFAF7');d=ImageDraw.Draw(im)
R='/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc';B='/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc'
def f(p,s): return ImageFont.truetype(p,s,index=2)
ink='#1B1B1B';mut='#6B6B6B';acc='#C2410C';grn='#15803D'
d.rectangle([0,0,W,14],fill=acc)
d.text((64,52),'ai-recipes-zh · 003 · 实测 2026-11-09',font=f(R,26),fill=mut)
d.text((64,100),'义乌货上亚马逊，让 AI 写 listing',font=f(B,58),fill=ink)
d.text((64,178),'“抗菌”没人写进去，坑在数字和标题',font=f(B,40),fill=acc)
d.text((64,242),'同一份带坑资料 · 全部免登录 · 0 元',font=f(R,28),fill=mut)
y=298;cols=[64,440,610,800]
for x,t in zip(cols,['AI（界面显示名）','违规词','该删的点出','细节问题']): d.text((x,y),t,font=f(B,27),fill=ink)
y+=48;d.line([64,y,W-64,y],fill='#D4D4D4',width=2)
rows=[('Claude Haiku 5.5','duck.ai','0','6/6','无',grn),('GPT-6 Luna','duck.ai','0','6/6','漏重量、温度',acc),('GPT-5.4 mini','duck.ai','0','5/6','“Cup”3次违规',acc),('Gemini Flash-Lite','网页版','0','3/6','2.8 写成 2.7',acc),('千问 Qwen-快速','网页版','—','—','没给出 listing',mut)]
for n,s,a,b,c,col in rows:
    y+=14;d.text((cols[0],y),n,font=f(B,29),fill=ink);d.text((cols[0],y+38),s,font=f(R,21),fill=mut)
    d.text((cols[1],y+6),a,font=f(B,32),fill=grn if a=='0' else mut);d.text((cols[2],y+6),b,font=f(B,32),fill=ink);d.text((cols[3],y+8),c,font=f(R,27),fill=col)
    y+=60;d.line([64,y,W-64,y],fill='#E5E5E5',width=1)
y+=26
d.text((64,y),'发现',font=f(B,32),fill=ink);y+=52
pts=['亚马逊把“抗菌/防霉”当农药类宣称，没 EPA 注册可能被下架','4 家都没把抗菌、无毒、爆款写进英文','资料给少了，千问自己加上“BPA Free”“防漏”','豆包、Kimi、DeepSeek 被登录挡住，本期未测']
for p in pts:
    d.ellipse([70,y+14,82,y+26],fill=acc);d.text((100,y),p,font=f(R,28),fill=ink);y+=44
y+=20
d.rounded_rectangle([64,y,W-64,y+236],radius=18,fill='#FFF1E8')
d.text((92,y+20),'0 元配方（约 10 分钟）',font=f(B,32),fill=acc)
yy=y+72
for s in ['① 资料写全：含“无检测报告”“盖子会漏”','② duck.ai 选 Claude 写（免登录）','③ 新对话选 GPT-6 Luna 交叉检查','④ 自己核：单位换算、同词≤2次、违规词']:
    d.text((92,yy),s,font=f(R,28),fill=ink);yy+=40
d.text((64,H-84),'违规规则出处：亚马逊卖家论坛官方帖与 2025 标题新规（网上资料，非实测）',font=f(R,22),fill=mut)
d.text((64,H-50),'github.com/xumao5393/ai-recipes-zh  ·  原始回答与截图全部公开',font=f(R,22),fill=mut)
im.save('/workspace/r003/pub/recipes/assets/003/summary.png');print(yy)
