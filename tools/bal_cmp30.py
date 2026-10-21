"""v6.30: bal_run30.sh 결과 표 — 사용: python3 tools/bal_cmp30.py <폴더> <단계>  (보스별 승률 · 평균 깎은 체력% · 변형별 승률)"""
import sys, json, glob, os, collections
D, T = sys.argv[1], sys.argv[2]
rows = collections.OrderedDict(); bosses = []
for f in sorted(glob.glob(os.path.join(D, f't{T}_*.txt'))):
    bk = os.path.basename(f)[len(f't{T}_'):-4]; bosses.append(bk)
    for l in open(f, encoding='utf8', errors='replace'):
        if not l.startswith('RAW'): continue
        r = json.loads(l[l.index('{'):]); b = r['boss']; win = b['left'] == 0 and not b['dead']
        mx = b['mx'] or 1; cut = 1.0 if win else (b['mx'] - b['left']) / mx
        rows.setdefault(r['v'], {}).setdefault(bk, []).append((win, cut, b['t']))
print('변형'.ljust(14), ''.join(k.rjust(16) for k in bosses))
tot = {k: [] for k in bosses}
for v, m in rows.items():
    cells = []
    for k in bosses:
        L = m.get(k, []); tot[k] += L
        cells.append((f"{sum(w for w, _, _ in L)}/{len(L)} {round(100 * sum(c for _, c, _ in L) / max(1, len(L)))}%").rjust(16))
    print(v.ljust(14), ''.join(cells))
print('합계'.ljust(14), ''.join((f"{round(100 * sum(w for w, _, _ in L) / max(1, len(L)))}%승 {round(100 * sum(c for _, c, _ in L) / max(1, len(L)))}%").rjust(16) for L in tot.values()))
if '--god' in sys.argv:   # GOD=1 로 잰 결과: 처치 시간(초) · 초당 받은 피해 — 체력 영향 없이 '얼마나 오래 · 얼마나 아프게' 싸우는지
    G = collections.defaultdict(list)
    for f in sorted(glob.glob(os.path.join(D, f't{T}_*.txt'))):
        bk = os.path.basename(f)[len(f't{T}_'):-4]
        for l in open(f, encoding='utf8', errors='replace'):
            if l.startswith('RAW'): r = json.loads(l[l.index('{'):]); b = r['boss']; G[bk].append((b['t'], b['loss'] / max(1, b['t']), b['left'] == 0))
    for k, L in G.items(): print(f"{k:8s} 처치 {sum(1 for x in L if x[2])}/{len(L)}  평균 {sum(x[0] for x in L) / len(L):5.0f}초  초당 피해 {sum(x[1] for x in L) / len(L):5.2f}")
if '--json' in sys.argv: print(json.dumps({k: {'win': sum(w for w, _, _ in L) / max(1, len(L)), 'cut': sum(c for _, c, _ in L) / max(1, len(L))} for k, L in tot.items()}))
