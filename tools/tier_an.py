import os,json,statistics as st,collections,sys
bf,ff,name,n1=sys.argv[1],sys.argv[2],sys.argv[3],sys.argv[4]
B=collections.defaultdict(list)
for l in open(bf):
    if not l.startswith('RAW '): continue
    _,bk,js=l.split(' ',2); d=json.loads(js); b=d['boss']; win=(b['mx']==0 or b['left']<=0) and not b['dead']
    B[bk].append((1 if win else (b['mx']-b['left'])/b['mx'],win,b['loss']))
F=collections.defaultdict(list)
for l in open(ff):
    if l.startswith('RAWL'): d=json.loads(l[5:]); F[d['L']].append(d['win'])
bb={k:(round(100*st.mean(x[0] for x in v)),sum(x[1] for x in v),len(v)) for k,v in B.items()}
bavg=st.mean(v[0] for v in bb.values())
T=json.load(open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),'data','tier_v501.json'))); s2=T['s2']; mk=max(x['fk'] for x in s2)
fk=st.mean(w['kills'] for w in F[24]); fs=100*fk/mk
mxraw=max(0.75*x['bavg']+0.25*x['field'] for x in s2)
score=round(100*(0.75*bavg+0.25*fs)/mxraw,1); tier='S' if score>=92 else 'A' if score>=80 else 'B' if score>=64 else 'C' if score>=56 else 'D'
print('boss',bb,'bavg',round(bavg,1),'f24',round(fk),'score',score,tier)
rank=sorted([(x['score'],x['name']) for x in s2]+[(score,'★'+name)],reverse=True)
print([ (i+1,n,s) for i,(s,n) in enumerate(rank)])
g=F[15]; k,lo=st.mean(w['kills'] for w in g),st.mean(w['loss'] for w in g)
L=[dict(name=x['name'],kills=x['kills'],loss=x['loss']) for x in T['s1']]+[dict(name='★'+n1,kills=k,loss=lo)]
mk1=max(x['kills'] for x in L); ml=min(x['loss'] for x in L)
for x in L: x['raw']=70*x['kills']/mk1+30*ml/x['loss']
m=max(x['raw'] for x in L)
print('s1',[(i+1,x['name'],round(x['kills']),round(x['loss']),round(100*x['raw']/m,1)) for i,x in enumerate(sorted(L,key=lambda x:-x['raw']))])
