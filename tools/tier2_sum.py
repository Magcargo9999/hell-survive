"""raw_*.jsonl -> summary_*.csv (검산용, 점수·티어 계산 없음)"""
import json, csv, os, math, statistics as st, collections
O = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'build', 'tier2')
def rd(fn):
    p = os.path.join(O, fn)
    return [json.loads(l) for l in open(p, encoding='utf8')] if os.path.exists(p) else []
def ms(x):
    n = len(x)
    if n == 0: return ('', '', '', '')
    m = st.mean(x); sd = st.stdev(x) if n > 1 else 0
    h = 1.96 * sd / math.sqrt(n) if n > 1 else 0
    return (round(m, 2), round(sd, 2), round(m - h, 2), round(m + h, 2))
def avg(x): return round(st.mean(x), 2) if x else ''
def W(fn, head, rows):
    with open(os.path.join(O, fn), 'w', newline='', encoding='utf-8-sig') as f:
        w = csv.writer(f); w.writerow(head); w.writerows(rows)
B = rd('raw_boss.jsonl'); g = collections.defaultdict(list)
for r in B:
    if r['exp'] == 'A': g[(r['variant'], r['boss'])].append(r)
rows = []
for (v, bk), L in sorted(g.items()):
    p = [r['boss_hp_removed_pct'] for r in L]; wn = [r for r in L if r['win']]; dd = [r for r in L if r['end_reason'] == 'player_dead']
    rows.append([v, bk, len(L), round(len(wn) / len(L), 3)] + list(ms(p)) + [avg([r['end_time'] for r in wn]), round(sum(1 for r in wn if r['end_time'] <= 180) / len(L), 3), round(sum(1 for r in wn if r['end_time'] <= 240) / len(L), 3),
                avg([r['dmg_taken_total'] for r in L]), avg([r['player_death_time'] for r in dd]), round(len(dd) / len(L), 3), round(sum(1 for r in L if r['target_synergy_opened']) / len(L), 3)])
W('summary_boss.csv', ['variant', 'boss', '판수', '승률', '깎은체력평균%', 'SD', '95%하한', '95%상한', '이긴판_평균처치시간', '180초내처치율', '240초내처치율', '평균받은피해', '진판_평균사망시점', '사망률', '목표시너지_열림율'], rows)
F = collections.defaultdict(list)
for r in rd('raw_field.jsonl'): F[(r['variant'], r['stage'], r['L'])].append(r)
rows = []
for (v, s, Lv), L in sorted(F.items()):
    rows.append([v, s, Lv, len(L)] + list(ms([r['kills'] for r in L])) + [round(sum(r['died'] for r in L) / len(L), 3), avg([r['dmg_taken'] for r in L])])
W('summary_field.csv', ['variant', 'stage', 'L', '판수', '처치평균', 'SD', '95%하한', '95%상한', '사망률', '받은피해평균'], rows)
G = collections.defaultdict(list)
for r in rd('raw_growth.jsonl'): G[r['variant']].append(r)
rows = []
for v, L in sorted(G.items()):
    rows.append([v, len(L)] + [avg([r['t_lv%d' % k] for r in L if r.get('t_lv%d' % k) is not None]) for k in (5, 10, 15, 20, 24)] + [round(sum(r['died'] for r in L) / len(L), 3)])
W('summary_growth.csv', ['variant', '판수', 'Lv5', 'Lv10', 'Lv15', 'Lv20', 'Lv24', '사망률'], rows)
print('boss rows', len(B), 'field', sum(len(v) for v in F.values()), 'growth', sum(len(v) for v in G.values()))
