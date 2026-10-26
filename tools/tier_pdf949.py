"""v9.49 티어표 추가 PDF: 공허의 마해룡 (마계 물고기 최종) — build/tier/fish_* · gunref_* · ghref_* 결과로 만든다.
사용: python3 tools/tier_pdf949.py → docs/hell survive 티어표 추가 - 공허의 마해룡.pdf"""
import json, statistics as st, collections, os, asyncio
from playwright.async_api import async_playwright
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
T = json.load(open(os.path.join(ROOT, 'data', 'tier_v501.json')))
BN = {'monkey': '원숭이', 'eye': '마안', 'skel': '스켈', 'fw': '혈랑왕'}
def ana(n):
    B = collections.defaultdict(list)
    for l in open(os.path.join(ROOT, 'build', 'tier', n + '_boss.txt')):
        if not l.startswith('RAW '): continue
        _, bk, js = l.split(' ', 2); b = json.loads(js)['boss']; win = (b['mx'] == 0 or b['left'] <= 0) and not b['dead']
        B[bk].append((1 if win else (b['mx'] - b['left']) / b['mx'], win))
    F = collections.defaultdict(list)
    for l in open(os.path.join(ROOT, 'build', 'tier', n + '_field.txt')):
        if l.startswith('RAWL'): d = json.loads(l[5:]); F[d['L']].append(d['win'])
    bb = {k: dict(p=round(100 * st.mean(x[0] for x in v)), w=sum(x[1] for x in v), n=len(v)) for k, v in B.items()}
    fl = {L: (st.mean(w['kills'] for w in g), st.mean(w['loss'] for w in g)) for L, g in F.items()}
    bavg = st.mean(v['p'] for v in bb.values()); mk = max(x['fk'] for x in T['s2']); fk = fl[24][0]
    mxraw = max(0.75 * x['bavg'] + 0.25 * x['field'] for x in T['s2'])
    score = round(100 * (0.75 * bavg + 0.25 * 100 * fk / mk) / mxraw, 1)
    tier = 'S' if score >= 92 else 'A' if score >= 80 else 'B' if score >= 64 else 'C' if score >= 56 else 'D'
    return dict(bb=bb, fl=fl, bavg=round(bavg, 1), field=round(100 * fk / mk), fk=round(fk), score=score, tier=tier)
F, G, H = ana('fish'), ana('gunref'), ana('ghref')
s2 = dict(id='fish2', fam='fish', name='공허의 마해룡', route='', tier=F['tier'], score=F['score'], bavg=F['bavg'], field=F['field'], fk=F['fk'], boss=F['bb'], measured='v9.49')
k1, l1 = F['fl'][15]
L = [dict(name=x['name'], kills=x['kills'], loss=x['loss']) for x in T['s1']] + [dict(name='★마계 미꾸라지', kills=k1, loss=l1)]
mk1 = max(x['kills'] for x in L); ml = min(x['loss'] for x in L)
for x in L: x['raw'] = 70 * x['kills'] / mk1 + 30 * ml / x['loss']
m = max(x['raw'] for x in L); s1sc = round(100 * (70 * k1 / mk1 + 30 * ml / l1) / m, 1)
s1t = 'S' if s1sc >= 92 else 'A' if s1sc >= 80 else 'B' if s1sc >= 64 else 'C' if s1sc >= 56 else 'D'
s1 = dict(id='fish1', fam='fish', name='마계 미꾸라지', route='', kills=round(k1), loss=round(l1), n=6, score=s1sc, tier=s1t, measured='v9.49')
rank = sorted([(x['score'], x['tier'], x['name'], x['bavg'], x['fk']) for x in T['s2']] + [(F['score'], F['tier'], '공허의 마해룡 NEW', F['bavg'], F['fk'])], reverse=True)
r1 = sorted(L, key=lambda x: -x['raw'])
pos = [i for i, r in enumerate(rank) if r[2].endswith('NEW')][0] + 1
avg = lambda d: sum(v['p'] for v in d['bb'].values()) / 4
mu = lambda d, k: d['bb'][k]['p'] - avg(d)
rows = ''.join(f"<tr class='{'new' if n.endswith('NEW') else ''}'><td>{i+1}</td><td>{t}</td><td>{n}</td><td>{b:.0f}%</td><td>{k}</td><td>{s:.1f}</td></tr>" for i, (s, t, n, b, k) in enumerate(rank))
rows1 = ''.join(f"<tr class='{'new' if x['name'].startswith('★') else ''}'><td>{i+1}</td><td>{x['name']}</td><td>{x['kills']:.0f}</td><td>{x['loss']:.0f}</td><td>{100*x['raw']/m:.1f}</td></tr>" for i, x in enumerate(r1))
bossrow = ''.join(f"<tr><td>{BN[k]}</td><td>{F['bb'][k]['p']}% ({F['bb'][k]['w']}승)</td><td>{mu(F,k):+.0f}</td><td>{G['bb'][k]['p']}% ({G['bb'][k]['w']}승)</td><td>{H['bb'][k]['p']}% ({H['bb'][k]['w']}승)</td></tr>" for k in ['monkey', 'eye', 'skel', 'fw'])
js = lambda o: json.dumps(o, ensure_ascii=False)
html = f"""<!doctype html><meta charset=utf-8><style>
body{{font-family:'Noto Sans CJK KR','Noto Sans CJK SC',sans-serif;font-size:11px;color:#222;margin:24px}} h1{{font-size:18px;margin:0 0 4px}} h2{{font-size:13px;margin:16px 0 6px}}
.sub{{color:#666;margin-bottom:10px}} table{{border-collapse:collapse;width:100%}} td,th{{border:1px solid #ccc;padding:3px 6px;text-align:center}} th{{background:#f1eef8}}
tr.new td{{background:#e9e4ff;font-weight:bold}} .box{{display:flex;gap:10px}} .box div{{flex:1;border:1px solid #ccc;padding:8px;border-radius:6px}} .big{{font-size:16px;font-weight:bold}}
pre{{background:#f6f6f6;border:1px solid #ddd;padding:8px;white-space:pre-wrap;word-break:break-all;font-size:10px}}</style>
<h1>티어표 추가: 공허의 마해룡 (마계 물고기 최종 진화)</h1>
<div class=sub>측정 버전 v9.49 · v5.01 티어표와 같은 방법 (봇 시뮬 · 기본 난이도 · 카드 무작위 · 같은 시드) · 보스전 40판 (보스 4종 × 10판) + 필드 18판 · 점수 = 보스 평균 75% + Lv.24 필드 처치 25%, 기존 표 1등(물의 도마뱀 전사) = 100</div>
<div class=box><div>티어 · 순위<br><span class=big>{F['tier']} · {pos}위 ({F['score']}점)</span></div><div>보스 평균<br><span class=big>{F['bavg']:.0f}%</span><br>{' · '.join(f"{BN[k]} {F['bb'][k]['p']} ({F['bb'][k]['w']}승)" for k in ['monkey','eye','skel','fw'])}</div><div>필드 Lv.24<br><span class=big>{F['fk']} 처치</span><br>넓은 물오라로 무리를 잘 쓸지만 받는 피해가 크다 (평균 {F['fl'][24][1]:.0f})</div></div>
<h2>보스별 상성 (깎은 체력 · 승리 수 / 10판)</h2>
<table><tr><th>보스</th><th>공허의 마해룡</th><th>평균 대비</th><th>참고: 악마처형자 (같은 빌드 재측정)</th><th>참고: 수호령의 총령 (같은 빌드 재측정)</th></tr>{bossrow}
<tr><td>평균</td><td>{F['bavg']:.0f}%</td><td></td><td>{G['bavg']:.0f}% · {G['score']}점</td><td>{H['bavg']:.0f}% · {H['score']}점</td></tr></table>
<div class=sub style="margin-top:6px">가까이 붙는 원숭이에 강하고(+14), 빠르게 돌며 거리를 벌리는 혈랑왕에는 오라가 덜 닿아 약하다(-14). 마안 · 스켈레톤은 평균 수준. 같은 v9.49 빌드로 다시 잰 악마처형자 {G['score']}점 · 수호령의 총령 {H['score']}점과 비교해도 중간 위치 — 수치 조정 없이 출시.</div>
<h2>최종 진화 순위 (기존 표 + 공허의 마해룡)</h2>
<table><tr><th>순위</th><th>티어</th><th>캐릭터</th><th>보스 평균</th><th>필드 Lv.24 처치</th><th>점수</th></tr>{rows}</table>
<h2>1진화 순위 (기존 표 + 마계 미꾸라지, Lv.15 필드)</h2>
<table><tr><th>순위</th><th>캐릭터</th><th>처치</th><th>받은 피해</th><th>점수</th></tr>{rows1}</table>
<h2>사이트 반영용 값 (tier.json · s2)</h2><pre>{js(s2)}</pre>
<h2>사이트 반영용 값 (tier.json · s1)</h2><pre>{js(s1)}</pre>
<div class=sub>참고: 0진화(마계 물고기) Lv.8 필드 처치 {F['fl'][8][0]:.0f} · 받은 피해 {F['fl'][8][1]:.0f}</div>"""
open(os.path.join(ROOT, 'build', 'tier', 'fish_report.html'), 'w').write(html)
json.dump(dict(s2=s2, s1=s1), open(os.path.join(ROOT, 'build', 'tier', 'fish_tier.json'), 'w'), ensure_ascii=False)
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); pg = await b.new_page(); await pg.set_content(html); await pg.wait_for_timeout(300)
        await pg.pdf(path=os.path.join(ROOT, 'docs', 'hell survive 티어표 추가 - 공허의 마해룡.pdf'), format='A4', print_background=True, margin=dict(top='10mm', bottom='10mm', left='8mm', right='8mm'))
        await b.close()
asyncio.run(main())
print(js(s2)); print(js(s1))
