import re,json,sys,glob,os
key=json.load(open('answer_key.json'))
def sections(body):
    # english listing = text before the Chinese compliance section
    m=re.search(r'(中文说明|资料中不能|这份资料里)',body)
    eng=body[:m.start()] if m else body
    zh=body[m.start():] if m else ''
    def grab(label_re, nxt_re):
        mm=re.search(label_re,eng,re.I|re.S)
        if not mm: return None
        rest=eng[mm.end():]
        n=re.search(nxt_re,rest,re.I)
        return (rest[:n.start()] if n else rest).strip(' \n*-#:')
    title=grab(r'Title\W*?\)?\**\s*\n',r'\n\s*(#+|\*\*|---)')
    st=grab(r'Search Terms\W*?\)?\**\s*\n',r'\n\s*(#+|---|\n)')
    return eng,zh,title,st
out={}
for f in sorted(glob.glob('answers/*.txt')):
    t=os.path.basename(f)[:-4]
    if 'blocked' in t: continue
    body=open(f).read().split('\n---\n',1)[1]
    eng,zh,title,st=sections(body)
    r={'chars':len(body)}
    if len(eng)<300: r['note']='no listing produced'; out[t]=r; continue
    title=(title or '').replace('**','').strip()
    r['title']=title; r['title_len']=len(title)
    words=[w.lower() for w in re.findall(r"[A-Za-z]+",title) if w.lower() not in {'a','an','the','and','or','for','with','of','to','in','on','by'}]
    stem=lambda w: re.sub(r'(es|s)$','',w)
    from collections import Counter
    c=Counter(stem(w) for w in words)
    r['title_repeats_over2']={k:v for k,v in c.items() if v>2}
    r['title_banned_chars']=[ch for ch in '!$?_{}^¬¦' if ch in title]
    st=(st or '').replace('**','').strip()
    r['search_terms']=st; r['search_terms_bytes']=len(st.encode())
    hits={}
    for k in key['traps']:
        hits[k['id']]=sorted(set(m.group(0) for m in re.finditer(k['regex'],eng,re.I)))
    r['english_hits']=hits
    r['zh_flags']={w:(w in zh) for w in ['抗菌','环保','无毒','防摔','爆款','必备','密封','认证','FDA','EPA','FTC']}
    out[t]=r
json.dump(out,open('scoring_auto.json','w'),ensure_ascii=False,indent=1)
print(json.dumps(out,ensure_ascii=False,indent=1))
