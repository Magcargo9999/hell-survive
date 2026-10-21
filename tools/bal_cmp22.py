"""v6.22 밸런스 비교: bal_run22.sh 결과 폴더 두 개(전/후)를 읽어 변형·보스별 지표를 비교한다.
사용: python3 tools/bal_cmp22.py <전 폴더> <후 폴더> [json 출력]"""
import json, sys, os, glob, collections, statistics as st
NAMES = {'wolf:abyss': '심연의 늑대', 'wolf:twin': '삼두 늑대', 'wolf:blood': '피의 혈랑', 'wolf:holy': '성혈랑', 'wolf:fallen': '타락한 혈랑',
         'snail:venom': '맹독 달팽이', 'snail:lava': '용암 달팽이', 'snail:bomb': '폭탄 달팽이',
         'archer:red': '진화한 지옥엘프', 'archer:holy': '성화된 지옥엘프', 'archer:skel': '해골 궁수',
         'chimera:wind': '조류형 키메라', 'chimera:flame': '맹수형 키메라', 'chimera:dream': '천안의 군주',
         'lizard:rage': '버서커 리자드', 'lizard:water': '물의 도마뱀 전사', 'lizard:guard': '수호의 리저드',
         'twins': '사슬의 폭군', 'ghost': '수호령의 총령', 'octo': '문어 마법사'}
BH = {'monkey': 20000, 'eye': 22000, 'skel': 20000, 'fw': 23500, 'angel': 24000}
def load(d):
    out = collections.defaultdict(list)   # (tier, boss, variant) -> [boss rec]
    for fn in glob.glob(os.path.join(d, 't*_*.txt')):
        tag = os.path.basename(fn)[:-4]; tier = int(tag[1]); bk = tag.split('_')[1]
        for l in open(fn, encoding='utf8'):
            if not l.startswith('RAW '): continue
            _, b, js = l.split(' ', 2); r = json.loads(js)
            out[(tier, bk, r['v'])].append(r['boss'])
    return out
def metrics(rs, tier, bk):
    n = len(rs); mx = max([r['mx'] for r in rs] + [BH[bk] * (1 + 0.3 * tier)])
    won = [r for r in rs if not r['dead'] and (r['mx'] == 0 or r['left'] <= 0)]
    dmg = [mx if (not r['dead'] and (r['mx'] == 0 or r['left'] <= 0)) else (r['mx'] - r['left']) for r in rs]
    return {'n': n, 'win': round(100 * len(won) / n), 'pct': round(100 * st.mean(dmg) / mx), 'dead': round(100 * sum(r['dead'] for r in rs) / n),
            'loss': round(st.mean(r['loss'] for r in rs)), 'hp0': round(st.mean(r['hp0'] for r in rs)), 't': round(st.mean(r['t'] for r in rs))}
def table(d):
    D = load(d); res = {}
    for (tier, bk, v), rs in D.items(): res.setdefault(v, {})[f't{tier}_{bk}'] = metrics(rs, tier, bk)
    return res
if __name__ == '__main__':
    A = table(sys.argv[1]); B = table(sys.argv[2]) if len(sys.argv) > 2 and os.path.isdir(sys.argv[2]) else {}
    keys = sorted({k for v in A.values() for k in v} | {k for v in B.values() for k in v})
    for v in NAMES:
        if v not in A and v not in B: continue
        print(NAMES[v])
        for k in keys:
            a = A.get(v, {}).get(k); b = B.get(v, {}).get(k)
            f = lambda m: '-' if not m else f"win{m['win']:>3}% dmg{m['pct']:>3}% dead{m['dead']:>3}% loss{m['loss']:>4}"
            print(f"  {k:10s} {f(a):48s} {('→ ' + f(b)) if b else ''}")
    if len(sys.argv) > 3: json.dump({'A': A, 'B': B}, open(sys.argv[3], 'w'), ensure_ascii=False, indent=1)
