"""sim_bal 결과 분석 → build/bal/summary.json
사용: python3 tools/bal_an.py build/bal/main.jsonl [추가 jsonl ...]"""
import json, sys, statistics as st, collections, os
NAMES = {'wolf:abyss': '심연의 늑대', 'wolf:twin': '쌍두 늑대', 'wolf:blood': '혈랑', 'wolf:holy': '성혈랑', 'wolf:fallen': '타락한 혈랑',
         'snail:venom': '맹독 달팽이', 'snail:lava': '용암 달팽이', 'snail:bomb': '폭탄 달팽이',
         'archer:red': '진화한 지옥엘프', 'archer:holy': '성화된 지옥엘프', 'archer:skel': '해골 궁수',
         'chimera:wind': '바람 키메라', 'chimera:flame': '업화 키메라', 'chimera:dream': '몽환 키메라',
         'lizard:rage': '버서커 리자드', 'lizard:water': '물의 도마뱀 전사', 'lizard:guard': '수호의 리저드',
         'twins': '사슬의 폭군', 'ghost': '수호령의 총령', 'octo': '문어 마법사'}
BOSS = ['monkey', 'eye', 'skel', 'fw']
BNAME = {'monkey': '원숭이 마왕', 'eye': '마안군주', 'skel': '스켈레톤 마왕', 'fw': '타락한 혈랑왕'}
rows = []
for fn in sys.argv[1:]:
    for l in open(fn):
        d = json.loads(l)
        if 'err' in d: continue
        rows.append(d)
# 보스 최대 체력 (살아남은 판의 mx로 확인)
BMX = {'monkey': 20000, 'eye': 22000, 'skel': 20000, 'fw': 23500}
for d in rows:
    b = d.get('boss') or {}
    if b.get('mx'): BMX[d['bk']] = max(BMX[d['bk']], b['mx'])
out = {'bmx': BMX, 'n': len(rows), 'v': {}}
by = collections.defaultdict(list)
for d in rows: by[d['v']].append(d)
for v, ds in by.items():
    F = [d['field'] for d in ds if d.get('field')]
    ok = [f for f in F if f['res'] == 'lv25']
    t25 = [f['lt']['25'] for f in ok if '25' in f['lt']]
    lv = lambda f, L: f['lt'].get(str(L))
    t10 = [lv(f, 10) for f in F if lv(f, 10)]; t20 = [lv(f, 20) for f in F if lv(f, 20)]
    fail = [f for f in F if f['rs'] or f['res'] != 'lv25']
    first = [f['rs'][0][0] if f['rs'] else f['lvl'] for f in fail]
    buck = collections.Counter('1~9' if x < 10 else '10~14' if x < 15 else '15~19' if x < 20 else '20~24' for x in first)
    dmgsrc = collections.Counter()
    for f in F:
        for k, x in (f.get('dc') or {}).items(): dmgsrc[k.replace('~far', '')] += x
    tot = sum(dmgsrc.values()) or 1
    V = {'name': NAMES.get(v, v), 'n': len(F), 'lv25': len(ok),
         't25': round(st.median(t25)) if t25 else None, 't25m': round(st.mean(t25)) if t25 else None,
         't25sd': round(st.pstdev(t25)) if len(t25) > 1 else 0, 't25min': min(t25) if t25 else None, 't25max': max(t25) if t25 else None,
         't10': round(st.median(t10)) if t10 else None, 't20': round(st.median(t20)) if t20 else None,
         'failRate': round(100 * len(fail) / max(1, len(F))), 'failLv': round(st.mean(first), 1) if first else None,
         'failBuck': dict(buck), 'rescues': round(st.mean(len(f['rs']) for f in F), 2),
         'loss': round(st.mean(f['loss'] for f in F)), 'kills': round(st.mean(f['kills'] for f in F)),
         'dmgsrc': {k: round(100 * x / tot) for k, x in dmgsrc.most_common(4)}, 'boss': {}}
    for bk in BOSS:
        B = [d['boss'] for d in ds if d['bk'] == bk and d.get('boss') and d['boss'].get('t', 0) >= 1]
        if not B: continue
        mx = BMX[bk]
        won = [b for b in B if not b['dead'] and (b['mx'] == 0 or b['left'] <= 0)]
        dmg = [mx if (not b['dead'] and (b['mx'] == 0 or b['left'] <= 0)) else (b['mx'] - b['left']) for b in B]
        dps = [x / max(1, b['t']) for x, b in zip(dmg, B)]
        dead = [b for b in B if b['dead']]
        V['boss'][bk] = {'n': len(B), 'win': len(won), 'winRate': round(100 * len(won) / len(B)),
                         'clearT': round(st.mean(b['t'] for b in won)) if won else None,
                         'dmg': round(st.mean(dmg)), 'pct': round(100 * st.mean(dmg) / mx),
                         'dps': round(st.mean(dps)), 'need': round(mx / 180), 'dead': len(dead),
                         'deadT': round(st.mean(b['t'] for b in dead)) if dead else None,
                         'timeout': sum(1 for b in B if not b['dead'] and b not in won)}
    bs = list(V['boss'].values())
    V['bossWin'] = round(100 * sum(x['win'] for x in bs) / max(1, sum(x['n'] for x in bs)))
    V['bossPct'] = round(st.mean(x['pct'] for x in bs)) if bs else None
    out['v'][v] = V
allt = [x['t25'] for x in out['v'].values() if x['t25']]
out['t25all'] = round(st.median(allt)) if allt else None
os.makedirs('build/bal', exist_ok=True)
json.dump(out, open('build/bal/summary.json', 'w'), ensure_ascii=False, indent=1)
print('rows', len(rows), 'median t25', out['t25all'], 'bmx', BMX)
for v, V in sorted(out['v'].items(), key=lambda x: x[1]['t25'] or 9999):
    print(V['name'].ljust(10), 'n', V['n'], 't25', V['t25'], '±', V['t25sd'], 'fail%', V['failRate'], 'failLv', V['failLv'], V['failBuck'],
          '| boss win%', V['bossWin'], 'pct', V['bossPct'], {k: (b['win'], b['n'], b['dps'], b['need']) for k, b in V['boss'].items()})
