"""card_sim 결과 분석 -> build/card/an.json"""
import json, os, math, statistics as st, collections, re, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FN = os.path.join(ROOT, 'build', 'card', 'raw.jsonl')
src = open(os.path.join(ROOT, 'src', 'game_template.html'), encoding='utf8').read()
SYN = {m.group(1): (m.group(2), m.group(3), re.findall(r"'(\w+)'", m.group(4))) for m in re.finditer(r"\{ id: '(\w+)',\s+name: '([^']+)',\s+txt: '([^']+)',\s+need: \[([^\]]*)\]", src)}
CARDNAME = {'thunder': '지옥 낙뢰', 'blade': '회전 칼날', 'nova': '충격파', 'aura': '불길 오라'}
VN = {'wolf:crimson': '피의 혈랑', 'snail:venom': '독액 달팽이', 'snail:bomb': '폭탄 달팽이', 'snail:lava': '용암 달팽이', 'archer:red': '진화한 지옥엘프', 'chimera': '조류형 키메라', 'chimera:flame': '맹수형 키메라',
      'chimera:dream': '천안의 군주', 'lizard:rage': '버서커 리자드', 'twins': '사슬의 폭군', 'ghost': '연보라 총령', 'octo': '문어 마법사'}
rows = [json.loads(l) for l in open(FN, encoding='utf8') if l.strip()]
rows = [r for r in rows if r['removed'] is not None]
def m(r): return r['removed'] / max(r['t'], 20)    # 초당 깎은 체력 %p (최소 20초로 하한)
G = collections.defaultdict(list)
for r in rows: G[(r['v'], r['cfg'], r['boss'])].append(r)
def cellstat(v, cfg, only_open=False):
    out = {}
    for bk in ('monkey', 'eye'):
        L = G.get((v, cfg, bk), [])
        if only_open: L = [r for r in L if cfg[4:] in r['syn']]
        if L: out[bk] = dict(n=len(L), m=st.mean(map(m, L)), rem=st.mean(r['removed'] for r in L), win=sum(r['win'] for r in L) / len(L), t=st.mean(r['t'] for r in L),
                              open=sum(1 for r in L if cfg.startswith('syn:') and cfg[4:] in r['syn']) / len(L), loss=st.mean(r['loss'] for r in L))
    return out
def ratio(v, cfg):
    a, c = cellstat(v, cfg), cellstat(v, 'ctrl'); rs = []; n = 0; w = []; o = []
    for bk in a:
        if bk in c and c[bk]['m'] > 0: rs.append(a[bk]['m'] / c[bk]['m']); n += a[bk]['n']; w.append(a[bk]['win'] - c[bk]['win']); o.append(a[bk]['open'])
    if not rs: return None
    return dict(ratio=math.exp(st.mean(map(math.log, rs))), n=n, dwin=st.mean(w), open=st.mean(o), mon=a.get('monkey', {}).get('m'), rem=st.mean(a[b]['rem'] for b in a))
def tier(x):
    return 'S' if x >= 1.15 else 'A' if x >= 1.06 else 'B' if x >= 0.97 else 'C' if x >= 0.88 else 'D'
cfgs = sorted({r['cfg'] for r in rows}); vs = sorted({r['v'] for r in rows})
res = dict(common={}, skill={}, only={}, ctrl={}, n=len(rows))
for v in vs:
    c = cellstat(v, 'ctrl')
    if c: res['ctrl'][v] = {bk: dict(rem=round(c[bk]['rem'], 1), win=round(c[bk]['win'], 2), t=round(c[bk]['t'], 1), n=c[bk]['n']) for bk in c}
for cfg in cfgs:
    if cfg == 'ctrl': continue
    kind, _, key = cfg.partition(':')
    per = {v: ratio(v, cfg) for v in vs}
    po = {}
    if kind == 'syn':
        for v in vs:
            a, c = cellstat(v, cfg, True), cellstat(v, 'ctrl'); rr = [a[b]['m'] / c[b]['m'] for b in a if b in c and c[b]['m'] > 0]
            if rr: po[v] = (math.exp(st.mean(map(math.log, rr))), sum(a[b]['n'] for b in a))
    per = {v: x for v, x in per.items() if x}
    if not per: continue
    bucket = 'skill' if kind == 'skill' else ('common' if key in ('fireBone', 'soulStorm', 'rush', 'lifeOrb', 'tstorm', 'bstorm', 'dnova', 'inferno', 'deadeye', 'iron', 'harvest') else 'only')
    rl = [x['ratio'] for x in per.values()]
    gm = math.exp(st.mean(map(math.log, rl)))
    sd = st.pstdev(map(math.log, rl)) if len(rl) > 1 else 0
    nn = sum(x['n'] for x in per.values())
    ent = dict(cfg=cfg, key=key, gm=gm, n=nn, nch=len(per), per={v: dict(ratio=round(x['ratio'], 3), n=x['n'], dwin=round(x['dwin'], 2), open=round(x['open'], 2), rem=round(x['rem'], 1)) for v, x in per.items()},
               tier=tier(gm), open=st.mean(x['open'] for x in per.values()), dwin=st.mean(x['dwin'] for x in per.values()), best=sorted(per, key=lambda v: -per[v]['ratio'])[:3], worst=sorted(per, key=lambda v: per[v]['ratio'])[:2],
               se=(sd / math.sqrt(len(rl))) if len(rl) > 1 else None)
    if po:
        tw = sum(n for _, n in po.values()); ent['gm_open'] = math.exp(sum(math.log(r) * n for r, n in po.values()) / tw); ent['n_open'] = tw
    # 피해 점유율 (스킬/시너지 카드가 낸 피해 비율)
    sh = []
    for r in rows:
        if r['cfg'] == cfg:
            tot = sum(r['dm'].values()) or 1
            k2 = key if kind == 'skill' else None
            if k2: sh.append(r['dm'].get(k2, 0) / tot)
    if sh: ent['share'] = st.mean(sh)
    res[bucket][cfg] = ent
res['syninfo'] = {k: dict(name=v[0], txt=v[1], need=v[2]) for k, v in SYN.items()}
res['vn'] = VN
json.dump(res, open(os.path.join(ROOT, 'build', 'card', 'an.json'), 'w'), ensure_ascii=False, indent=1)
if __name__ == '__main__':
    print('rows', len(rows))
    for b in ('common', 'skill', 'only'):
        print('==', b)
        for e in sorted(res[b].values(), key=lambda e: -e['gm']):
            print('%-14s gm %.3f %s n%3d nch%2d open%.2f dwin%+.2f best %s' % (e['cfg'], e['gm'], e['tier'], e['n'], e['nch'], e['open'], e['dwin'], ','.join(e['best'])))
