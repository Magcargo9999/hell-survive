"""build/card/an.json -> HTML -> PDF (+ 사이트용 JSON). 사용: python3 card_pdf.py <출력pdf>"""
import json, os, sys, math, subprocess, html
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
subprocess.run([sys.executable, os.path.join(ROOT, 'tools', 'card_an.py')], check=True, capture_output=True)
A = json.load(open(os.path.join(ROOT, 'build', 'card', 'an.json'), encoding='utf8'))
VN = A['vn']; SI = A['syninfo']; E = html.escape
CN = {'thunder': '지옥 낙뢰', 'blade': '회전 칼날', 'nova': '충격파', 'aura': '불길 오라'}
TC = {'S': '#e0457b', 'A': '#e8873a', 'B': '#c9a227', 'C': '#4b9b6e', 'D': '#5b7fa8'}
def nm(e):
    k = e['key']; return CN[k] if e['cfg'].startswith('skill') else SI.get(k, {}).get('name', k)
def cell(x):
    if not x: return '<td class=na>·</td>'
    r = x['ratio']; d = (r - 1) * 100; a = min(abs(d) / 40, 1)
    col = 'rgba(46,160,90,%.2f)' % (0.15 + 0.6 * a) if d >= 0 else 'rgba(210,70,70,%.2f)' % (0.15 + 0.6 * a)
    return '<td style="background:%s" title="n=%d">%+d%%</td>' % (col, x['n'], round(d))
def tbl(bucket, cols):
    L = sorted(A[bucket].values(), key=lambda e: -e['gm'])
    h = '<table><tr><th>카드</th><th>티어</th><th>평균 효과</th><th>열렸을 때</th><th>승률 변화</th><th>시너지 열림</th><th>판</th>' + ''.join('<th class=v>%s</th>' % E(VN[v]) for v in cols) + '</tr>'
    for e in L:
        mat = ' + '.join(SI[e['key']]['need']) if e['cfg'].startswith('syn') and e['key'] in SI else ''
        h += '<tr><td class=l><b>%s</b><br><small>%s</small></td><td><span class=t style="background:%s">%s</span></td><td><b>%+.1f%%</b></td><td>%s</td><td>%+d%%p</td><td>%d%%</td><td>%d</td>%s</tr>' % (
            E(nm(e)), E(SI.get(e['key'], {}).get('txt', '') if e['cfg'].startswith('syn') else '피해 점유율 %d%%' % round(100 * e.get('share', 0))), TC[e['tier']], e['tier'], (e['gm'] - 1) * 100, ('%+d%% (n%d)' % (round((e['gm_open'] - 1) * 100), e['n_open']) if 'gm_open' in e else '-'), round(100 * e['dwin']),
            round(100 * e['open']) if e['cfg'].startswith('syn') else 0, e['n'], ''.join(cell(e['per'].get(v)) for v in cols))
    return h + '</table>'
vs = [v for v in VN if v in A['ctrl']]
base = [v for v in ['wolf:crimson', 'snail:venom', 'snail:bomb', 'snail:lava', 'archer:red', 'chimera', 'lizard:rage', 'twins', 'ghost', 'octo'] if v in A['ctrl']]
# 캐릭터별 최고
best = {}
for v in vs:
    allc = [(e['gm'] if False else e['per'][v]['ratio'], e) for b in ('common', 'skill', 'only') for e in A[b].values() if v in e['per'] and e['per'][v]['n'] >= 4]
    allc.sort(key=lambda t: -t[0]); best[v] = allc
def tops(v, kind, n=3, rev=False):
    L = [(r, e) for r, e in best[v] if (e['cfg'].startswith('skill') if kind == 'skill' else e['cfg'].startswith('syn'))]
    L = L[::-1] if rev else L
    return ', '.join('%s %+d%%' % (nm(e), round((r - 1) * 100)) for r, e in L[:n])
chtab = '<table><tr><th>캐릭터</th><th>기준 보스 깎은 체력 (원숭이/마안)</th><th>승률 (원숭이/마안)</th><th>잘 맞는 시너지</th><th>잘 맞는 스킬카드</th><th>피해야 할 카드</th></tr>'
for v in vs:
    c = A['ctrl'][v]; g = lambda k, f: c.get(k, {}).get(f, '-')
    worst = ', '.join('%s %+d%%' % (nm(e), round((r - 1) * 100)) for r, e in best[v][::-1][:2])
    chtab += '<tr><td class=l><b>%s</b></td><td>%s%% / %s%%</td><td>%s / %s</td><td class=l>%s</td><td class=l>%s</td><td class=l>%s</td></tr>' % (E(VN[v]), g('monkey', 'rem'), g('eye', 'rem'), g('monkey', 'win'), g('eye', 'win'), E(tops(v, 'syn')), E(tops(v, 'skill', 2)), E(worst))
chtab += '</table>'
# 구조적 문제 자동 후보
iss = []
for e in A['skill'].values():
    if e.get('share', 0) >= 0.3: iss.append('%s: 이 카드를 중점으로 올린 판에서 총 피해의 %d%%를 혼자 차지 (평균 효과 %+.0f%%).' % (nm(e), round(100 * e['share']), (e['gm'] - 1) * 100))
for b in ('common', 'only'):
    for e in A[b].values():
        if e['open'] < 0.5: iss.append('%s: 재료 카드 두 장을 Lv.3까지 못 올려 시너지가 열린 비율이 %d%% (카드 선택 구조 문제 가능).' % (nm(e), round(100 * e['open'])))
        if e['gm'] < 0.9 and e['open'] >= 0.5: iss.append('%s: 시너지를 열고도 평균 %+.0f%% — 재료 카드 두 장을 올리는 비용을 못 갚음 (효과 부족).' % (nm(e), (e['gm'] - 1) * 100))
for v in vs:
    c = A['ctrl'][v]
    if all(c.get(k, {}).get('win', 0) >= 0.99 for k in ('monkey', 'eye') if k in c): iss.append('%s: 카드 구성과 무관하게 원숭이·마안 보스를 거의 100%% 처치 (기준 빌드 승률 100%%).' % VN[v])
    if all(c.get(k, {}).get('win', 1) <= 0.34 for k in ('monkey', 'eye') if k in c): iss.append('%s: 기준 빌드 승률 33%% 이하 — 보스전이 구조적으로 어려움.' % VN[v])
# 사이트 JSON
site = {'game_ver': '6.22', 'note': 'ratio = 기준 빌드 대비 보스전 초당 피해(원숭이·마안 평균, 기하평균). tier S>=1.15 A>=1.06 B>=0.97 C>=0.88 D', 'cards': [], 'by_char': {}}
for b in ('common', 'only', 'skill'):
    for e in sorted(A[b].values(), key=lambda e: -e['gm']):
        site['cards'].append(dict(id=e['key'], name=nm(e), kind={'common': '공용 시너지', 'only': '전용 시너지', 'skill': '스킬카드'}[b], tier=e['tier'], ratio=round(e['gm'], 3), n=e['n'], open=round(e['open'], 2),
                                  good=[VN[v] for v in e['best']], bad=[VN[v] for v in e['worst']], per_char={v: x['ratio'] for v, x in e['per'].items()}))
for v in vs:
    site['by_char'][v] = dict(name=VN[v], synergy=[(e['key'], round(r, 3)) for r, e in best[v] if e['cfg'].startswith('syn')][:5], skill=[(e['key'], round(r, 3)) for r, e in best[v] if e['cfg'].startswith('skill')])
json.dump(site, open(os.path.join(ROOT, 'build', 'card', 'site.json'), 'w'), ensure_ascii=False, indent=1)
css = """body{font-family:'Noto Sans CJK KR',sans-serif;font-size:10.5px;color:#222;margin:0}h1{font-size:22px;margin:0 0 4px}h2{font-size:15px;border-bottom:2px solid #e0457b;padding-bottom:3px;margin:18px 0 6px;page-break-after:avoid}
table{border-collapse:collapse;width:100%;margin:4px 0 10px;page-break-inside:auto}tr{page-break-inside:avoid}th{background:#2b2f3a;color:#fff;padding:3px 4px;font-size:9.5px}th.v{font-size:8.5px;width:52px}
td{border:1px solid #ddd;padding:3px 4px;text-align:center}td.l{text-align:left}td.na{color:#bbb}.t{color:#fff;font-weight:700;padding:1px 8px;border-radius:9px}small{color:#777}.box{background:#f5f6f8;padding:6px 10px;border-radius:6px;margin:6px 0}li{margin:2px 0}pre{font-size:8px;background:#f5f6f8;padding:6px;white-space:pre-wrap;word-break:break-all}"""
n = A['n']
body = f"<h1>hell survive v6.22 카드 티어 (시너지 · 스킬카드 · 캐릭터 궁합)</h1><div class=box>측정 판 수 <b>{n}</b>판 · 봇 시뮬레이션(원숭이 마왕·마안군주, 난이도 0) · 기준 = 같은 캐릭터가 공용 스탯 카드(발톱·방어·심장·공속·범위·이속)만 올린 빌드. <b>효과 = 기준 대비 보스전 초당 피해 비율</b>(+15% 이상 S, +6% 이상 A, -3% 이상 B, -12% 이상 C, 그 아래 D). 승률 변화는 기준 대비 %p. 열 색: 초록 = 기준보다 강함, 빨강 = 약함. 판 수가 적은 칸은 오차가 큽니다(±10%p).</div>"
body += '<h2>1. 공용 시너지 카드 티어</h2>' + tbl('common', base)
body += '<h2>2. 스킬카드(공용 공격 카드) 티어 — 해당 카드를 Lv.5까지 중점 투자</h2>' + tbl('skill', base)
body += '<h2>3. 캐릭터 전용 시너지 티어</h2>' + tbl('only', vs)
body += '<h2>4. 캐릭터별 추천 카드</h2>' + chtab
body += '<h2>5. 구조적으로 문제 있어 보이는 카드·캐릭터</h2><ul>' + ''.join('<li>%s</li>' % E(x) for x in iss) + '</ul><div class=box>※ 봇은 타이밍 스킬(수호 리저드 갑주, 천안 난무 등)을 못 맞추므로 해당 캐릭터는 실제보다 낮게 나올 수 있습니다. 자동 후보이므로 체감과 대조해 판단하세요.</div>'
body += '<h2>6. 티어사이트용 JSON</h2><pre>' + E(json.dumps(site, ensure_ascii=False)) + '</pre>'
open(os.path.join(ROOT, 'build', 'card', 'report.html'), 'w', encoding='utf8').write('<html><head><meta charset=utf8><style>%s</style></head><body>%s</body></html>' % (css, body))
from playwright.sync_api import sync_playwright
out = sys.argv[1]
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(); pg.goto('file://' + os.path.join(ROOT, 'build', 'card', 'report.html'))
    pg.pdf(path=out, format='A4', margin=dict(top='12mm', bottom='12mm', left='9mm', right='9mm'), print_background=True); b.close()
print('ok', out, n)
