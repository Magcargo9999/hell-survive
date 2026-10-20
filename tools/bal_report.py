import json, statistics as st, collections, html
B = '/home/claude/hell-survive/build/bal/'
S = json.load(open(B + 'summary.json')); IQR = json.load(open(B + 'iqr.json'))
V = S['v']
rows = []
for f in ['main', 'main2', 'main3', 'main4']:
    for l in open(B + f + '.jsonl'):
        d = json.loads(l); b = d.get('boss') or {}
        if 'err' in d or b.get('t', 0) < 1: continue
        if not b.get('dead') and b.get('left', 0) > 0 and b.get('mx', 0) > 0 and b.get('t', 0) < 179: continue
        rows.append(d)
NROWS = len(rows)
ORDER = ['wolf:blood', 'wolf:holy', 'wolf:fallen', 'wolf:abyss', 'wolf:twin', 'snail:venom', 'snail:lava', 'snail:bomb',
         'archer:red', 'archer:holy', 'archer:skel', 'chimera:wind', 'chimera:flame', 'chimera:dream',
         'lizard:rage', 'lizard:water', 'lizard:guard', 'twins', 'ghost', 'octo']
CHN = {'wolf': '늑대', 'snail': '달팽이', 'archer': '궁수', 'chimera': '키메라', 'lizard': '리자드', 'twins': '사슬 악마', 'ghost': '구슬 유령', 'octo': '문어 마법사'}
BK = ['monkey', 'eye', 'skel', 'fw']; BN = {'monkey': '원숭이', 'eye': '마안군주', 'skel': '스켈레톤', 'fw': '혈랑왕'}
MED = S['t25all']; LO, HI = round(MED * 0.85), round(MED * 1.15)
mmss = lambda s: f'{int(s) // 60}:{int(s) % 60:02d}'
e = html.escape
SEQ = ['#f0efec', '#cde2fb', '#9ec5f4', '#6da7ec', '#3987e5', '#256abf', '#184f95', '#0d366b']
def seq(p):   # 0..100 -> 단색 파랑 단계
    i = min(7, int(p / 100 * 7.999)); return SEQ[i], ('#fff' if i >= 4 else '#0b0b0b')

# ---------- 1. Lv.25 도달 시간 차트 ----------
def chart_t25():
    vs = sorted(ORDER, key=lambda v: V[v]['t25'])
    W, rowh, L, R = 700, 21, 132, 92; H = rowh * len(vs) + 40
    x0, x1 = 200, 820; sx = lambda t: L + (t - x0) / (x1 - x0) * (W - L - R)
    o = [f'<svg viewBox="0 0 {W} {H}" width="100%" font-family="Noto Sans CJK KR" font-size="11">']
    o.append(f'<rect x="{sx(LO):.1f}" y="6" width="{sx(HI) - sx(LO):.1f}" height="{H - 34}" fill="#eef4fc"/>')
    o.append(f'<line x1="{sx(MED):.1f}" x2="{sx(MED):.1f}" y1="6" y2="{H - 28}" stroke="#86b6ef" stroke-dasharray="3 3"/>')
    for t in range(240, 821, 120):
        o.append(f'<line x1="{sx(t):.1f}" x2="{sx(t):.1f}" y1="6" y2="{H - 28}" stroke="#e1e0d9" stroke-width="0.6"/>')
        o.append(f'<text x="{sx(t):.1f}" y="{H - 14}" text-anchor="middle" fill="#898781">{mmss(t)}</text>')
    o.append(f'<text x="{sx(MED):.1f}" y="{H - 2}" text-anchor="middle" fill="#256abf" font-weight="700">전체 중앙값 {mmss(MED)} · 목표 구간 {mmss(LO)}~{mmss(HI)}</text>')
    for i, v in enumerate(vs):
        y = 18 + i * rowh; t = V[v]['t25']; q = IQR[v]; out = t > HI or t < LO
        o.append(f'<text x="{L - 8}" y="{y + 4}" text-anchor="end" fill="#0b0b0b">{e(V[v]["name"])}</text>')
        o.append(f'<line x1="{sx(max(x0, q[0])):.1f}" x2="{sx(min(x1, q[1])):.1f}" y1="{y}" y2="{y}" stroke="{"#9ec5f4"}" stroke-width="6" stroke-linecap="round"/>')
        o.append(f'<circle cx="{sx(t):.1f}" cy="{y}" r="5" fill="{"#d03b3b" if t > HI else "#eda100" if t < LO else "#2a78d6"}" stroke="#fff" stroke-width="2"/>')
        dv = round(100 * (t - MED) / MED)
        o.append(f'<text x="{W - R + 8}" y="{y + 4}" fill="{"#0b0b0b" if out else "#52514e"}" font-weight="{"700" if out else "400"}">{mmss(t)} ({dv:+d}%)</text>')
    o.append('</svg>'); return ''.join(o)

# ---------- 2. 실패 지점 (첫 위기 레벨) 막대 ----------
BUCK = ['1~9', '10~14', '15~19', '20~24']; BC = ['#0d366b', '#256abf', '#6da7ec', '#b7d3f6']
def chart_fail():
    vs = sorted(ORDER, key=lambda v: -V[v]['failRate'])
    W, rowh, L, R = 700, 20, 132, 60; H = rowh * len(vs) + 36
    sx = lambda p: L + p / 100 * (W - L - R)
    o = [f'<svg viewBox="0 0 {W} {H}" width="100%" font-family="Noto Sans CJK KR" font-size="11">']
    for p in range(0, 101, 25):
        o.append(f'<line x1="{sx(p):.1f}" x2="{sx(p):.1f}" y1="4" y2="{H - 26}" stroke="#e1e0d9" stroke-width="0.6"/><text x="{sx(p):.1f}" y="{H - 12}" text-anchor="middle" fill="#898781">{p}%</text>')
    for i, v in enumerate(vs):
        y = 8 + i * rowh; n = V[v]['n']; x = sx(0)
        o.append(f'<text x="{L - 8}" y="{y + 11}" text-anchor="end">{e(V[v]["name"])}</text>')
        for b, c in zip(BUCK, BC):
            w = (V[v]['failBuck'].get(b, 0) / n) * (W - L - R)
            if w > 0: o.append(f'<rect x="{x:.1f}" y="{y + 2}" width="{max(0, w - 2):.1f}" height="12" rx="2" fill="{c}"/>'); x += w
        o.append(f'<text x="{x + 6:.1f}" y="{y + 12}" fill="#0b0b0b">{V[v]["failRate"]}%</text>')
    o.append('</svg>'); return ''.join(o)

def chart_failtime():
    fs = [d['field']['rs'][0][1] for d in rows if d['field']['rs']]
    c = collections.Counter(min(9, x // 60) for x in fs); tot = len(fs)
    W, H, L = 330, 170, 34; bw = (W - L - 10) / 10
    mx = max(c.values())
    o = [f'<svg viewBox="0 0 {W} {H}" width="100%" font-family="Noto Sans CJK KR" font-size="10">']
    for i in range(10):
        h = c.get(i, 0) / mx * (H - 50); x = L + i * bw
        o.append(f'<rect x="{x + 1:.1f}" y="{H - 30 - h:.1f}" width="{bw - 3:.1f}" height="{h:.1f}" rx="2" fill="{"#d03b3b" if i == 2 else "#6da7ec"}"/>')
        o.append(f'<text x="{x + bw / 2:.1f}" y="{H - 17}" text-anchor="middle" fill="#898781">{i}{"+" if i == 9 else ""}분</text>')
        if c.get(i): o.append(f'<text x="{x + bw / 2:.1f}" y="{H - 34 - h:.1f}" text-anchor="middle" fill="#0b0b0b">{round(100 * c[i] / tot)}%</text>')
    o.append(f'<line x1="{L}" x2="{W - 8}" y1="{H - 30}" y2="{H - 30}" stroke="#c3c2b7"/>')
    o.append(f'<text x="{L}" y="{H - 3}" fill="#52514e">첫 위기 시각 (게임 시간) · 위기 {tot}판 기준</text></svg>')
    return ''.join(o), round(100 * c.get(2, 0) / tot), round(100 * sum(1 for d in rows if d['field']['rs'] and d['field']['rs'][0][0] < 10) / max(1, tot))

# ---------- 3. 보스 히트맵 ----------
def heat():
    h = ['<table class="heat"><tr><th>캐릭터</th>' + ''.join(f'<th>{BN[b]}</th>' for b in BK) + '<th>3종 승률</th></tr>']
    for v in ORDER:
        r = [f'<td class="nm">{e(V[v]["name"])}</td>']
        for b in BK:
            x = V[v]['boss'][b]; p = x['winRate']; bg, fg = seq(p)
            sub = f'{x["clearT"]}초' if x['clearT'] else f'딜 {x["pct"]}%'
            r.append(f'<td style="background:{bg};color:{fg}"><b>{x["win"]}/{x["n"]}</b><span>{sub}</span></td>')
        w3 = V[v]['bossWin3']; bg, fg = seq(w3)
        r.append(f'<td style="background:{bg};color:{fg}"><b>{w3}%</b></td>')
        h.append('<tr>' + ''.join(r) + '</tr>')
    h.append('</table>'); return ''.join(h)

def chart_outcome():
    vs = sorted(ORDER, key=lambda v: V[v]['bossWin'])
    W, rowh, L, R = 700, 20, 132, 10; H = rowh * len(vs) + 50
    sx = lambda p: L + p / 100 * (W - L - R)
    C = [('승리', '#2a78d6'), ('사망', '#eb6834'), ('3분 초과', '#1baf7a')]
    o = [f'<svg viewBox="0 0 {W} {H}" width="100%" font-family="Noto Sans CJK KR" font-size="11">']
    for i, (n, c) in enumerate(C):
        o.append(f'<rect x="{L + i * 110}" y="2" width="10" height="10" rx="2" fill="{c}"/><text x="{L + 14 + i * 110}" y="11">{n}</text>')
    for i, v in enumerate(vs):
        y = 22 + i * rowh; x = sx(0)
        o.append(f'<text x="{L - 8}" y="{y + 11}" text-anchor="end">{e(V[v]["name"])}</text>')
        for p, (n, c) in zip([V[v]['bossWin'], V[v]['bossDead'], V[v]['bossTO']], C):
            w = p / 100 * (W - L - R)
            if w > 0:
                o.append(f'<rect x="{x:.1f}" y="{y + 2}" width="{max(0, w - 2):.1f}" height="13" rx="2" fill="{c}"/>')
                if w > 26: o.append(f'<text x="{x + 5:.1f}" y="{y + 12.5}" fill="#fff" font-size="10">{p}%</text>')
                x += w
    o.append(f'<text x="{L}" y="{H - 6}" fill="#898781">보스 4종 × 5판 = 20판 기준 (혈랑왕 포함)</text></svg>')
    return ''.join(o)

def boss_tbl():
    t = ['<table class="tb"><tr><th>보스</th><th>체력</th><th>3분 클리어에 필요한 초당 딜</th><th>승률</th><th>사망</th><th>사망 시점(평균)</th><th>평균 클리어</th></tr>']
    for b in BK:
        B2 = [d['boss'] for d in rows if d['bk'] == b]
        won = [x for x in B2 if not x['dead'] and (x.get('mx') == 0 or x['left'] <= 0)]; dead = [x for x in B2 if x['dead']]
        t.append(f'<tr><td>{BN[b]}{" 마왕" if b != "fw" else ""}</td><td>{S["bmx"][b]:,}</td><td>{round(S["bmx"][b] / 180)}</td><td><b>{round(100 * len(won) / len(B2))}%</b></td><td>{round(100 * len(dead) / len(B2))}%</td><td>{round(st.mean(x["t"] for x in dead))}초</td><td>{round(st.mean(x["t"] for x in won))}초</td></tr>')
    t.append('</table>'); return ''.join(t)

def level_tbl():
    t = ['<table class="tb small"><tr><th>캐릭터</th>' + ''.join(f'<th>Lv.{L}</th>' for L in (5, 10, 15, 20, 25)) + '<th>위기 없이 완주</th><th>판수</th></tr>']
    for v in ORDER:
        F = [d['field'] for d in rows if d['v'] == v]
        m = lambda L: mmss(st.median([f['lt'][str(L)] for f in F if str(L) in f['lt']]))
        t.append(f'<tr><td class="nm">{e(V[v]["name"])}</td>' + ''.join(f'<td>{m(L)}</td>' for L in (5, 10, 15, 20, 25)) + f'<td>{100 - V[v]["failRate"]}%</td><td>{len(F)}</td></tr>')
    t.append('</table>'); return ''.join(t)

# ---------- 밸런싱안 ----------
P = [
 ('A', 'Lv.25 도달 시간 맞추기'),
 (1, '수호령의 총령', f'Lv.25 {mmss(V["ghost"]["t25"])} (+75%) · Lv.15→25 구간이 다른 캐릭터의 2배', '1진화 공격력 ×1.15 → ×1.30<br>최종 공격력 ×1.03 → ×1.10 (v5.11 너프 전 값)', '중폭 · 소폭', 'Lv.25 −20~25% (약 8분대). 보스 승률 75% → 80%대'),
 (2, '사슬 악마 / 사슬의 폭군', f'Lv.25 {mmss(V["twins"]["t25"])} (+47%) · 보스전 55%가 3분 초과(딜 부족), 사망은 10%', '0진화 공격력 16 → 17.5<br>1진화 공격력 ×1.0 → ×1.15', '소폭 · 중폭', 'Lv.25 −15% · 보스 초당 딜 +15% → 시간 초과 대부분 해소'),
 (3, '궁수 공통 (0진화)', f'Lv.10 도달 {mmss(S["t10base"]["archer"])} (8종 중 가장 느림) · 세 루트 모두 느림', '0진화 공격 속도 +10% (간격 0.56 → 0.51초)', '소폭', 'Lv.10 −10%, 세 루트 Lv.25 −5~8%'),
 (4, '해골 궁수', f'Lv.25 {mmss(V["archer:skel"]["t25"])} (+35%) · 보스 승률 {V["archer:skel"]["bossWin3"]}%', '1진화 공격력 ×2.95 → ×3.15', '소폭', '3번과 합쳐 Lv.25 −12% 안팎 · 보스 승률 60% → 70%대'),
 (5, '달팽이 공통 (0진화)', f'Lv.10 도달 {mmss(S["t10base"]["snail"])} · 세 루트 Lv.25 +14~19%', '0진화 공격 속도 +8% (간격 0.92 → 0.85초)', '소폭', '세 루트 Lv.25 −6~8% → 목표 구간 안'),
 (6, '리자드 공통 (0진화) — 하향', f'Lv.10 도달 {mmss(S["t10base"]["lizard"])} (가장 빠름) · 세 루트 Lv.25 −13~−20%', '0진화 공격 범위 −8% (100 → 92)', '소폭 하향', 'Lv.25 +5~8%. 보스는 몸집이 커서 영향 적음'),
 ('B', '보스전 (원숭이·마안·스켈레톤 3분 클리어)'),
 (7, '쌍두 늑대', f'3종 승률 {V["wolf:twin"]["bossWin3"]}% (20판 중 사망 75%) · 3분 딜 60%', '최종 받는 피해 −8%<br>최종 공격력 +8%', '소폭 · 소폭', '승률 13% → 40~50%. 체력은 예산(최종 +60) 꽉 차서 피해 감소로'),
 (8, '업화 키메라', f'3종 승률 {V["chimera:flame"]["bossWin3"]}% (사망 55%)', '최종 받는 피해 −8%', '소폭', '승률 40% → 55~60%'),
 (9, '타락한 혈랑', f'3종 승률 {V["wolf:fallen"]["bossWin3"]}% · 딜은 충분한데 사망 70%', '받는 피해 +8% 페널티 삭제<br>최종 체력 +10 → +25', '소폭 · 소폭', '승률 40% → 60%대. 숨은 진화 보상답게'),
 (10, '심연의 늑대', f'3종 승률 {V["wolf:abyss"]["bossWin3"]}% (사망 55%)', '최종 회피 12% → 16%', '중폭', '승률 53% → 65% 안팎'),
 (11, '성화된 지옥엘프', f'3종 승률 {V["archer:holy"]["bossWin3"]}% · 이기면 1분대로 빠른데 사망 55%', '최종 받는 피해 ×0.90 → ×0.84', '소폭', '승률 53% → 65% 안팎'),
 (12, '버서커 리자드', f'3종 승률 {V["lizard:rage"]["bossWin3"]}% (사망 50%)', '최종 체력 +40 → +55', '소폭', '승률 53% → 65%. 6번(범위 하향)과 같이 쓰면 필드 속도는 그대로'),
 (13, '성혈랑 — 하향', f'3종 승률 {V["wolf:holy"]["bossWin3"]}% · 필드 위기 25%로 가장 안전', '최종 재생 초당 0.8 → 0.65', '소폭 하향', '보스 승률 100% → 90%대, 필드 위기 조금 증가'),
 ('C', '보스 · 시스템 (선택)'),
 (14, '스켈레톤 마왕', '보스 3종 중 가장 어려움 (승률 58% · 사망 38%)', '마왕 공격 피해 −8%', '보스 소폭 하향', '스켈레톤 승률 58% → 65~70% (원숭이 74 · 마안 69와 비슷하게)'),
 (15, '초반 2분대 벽 (전 캐릭터)', 'FAILTXT', '초반 몹 생성 완화 구간 150초 → 200초<br>(2분대 몹 생성 간격 약 +10%)', '소폭', '2분대 위기 감소 · Lv.25 시간 −3% 안팎 (모두 같은 비율)'),
]

def prop_tbl(failtxt):
    t = ['<table class="prop"><tr><th>#</th><th>대상</th><th>근거 (시뮬)</th><th>조정안</th><th>단계</th><th>예상 효과</th></tr>']
    for p in P:
        if isinstance(p[0], str):
            t.append(f'<tr class="grp"><td colspan="6">{p[0]}. {e(p[1])}</td></tr>'); continue
        n, who, why, what, lvl, eff = p
        if why == 'FAILTXT': why = failtxt
        t.append(f'<tr><td class="no">{n}</td><td class="who">{e(who)}</td><td>{e(why)}</td><td class="what">{what}</td><td><span class="pill{" down" if "하향" in lvl else ""}">{e(lvl)}</span></td><td>{e(eff)}</td></tr>')
    t.append('</table>'); return ''.join(t)

ft_svg, ft2, ftlv = chart_failtime()
failtxt = f'첫 위기의 {ftlv}%가 Lv.10 전, {ft2}%가 2:00~2:59 (모든 캐릭터 공통)'
wins3 = [d for d in rows if d['bk'] != 'fw']
win3 = round(100 * sum(1 for d in wins3 if not d['boss']['dead'] and (d['boss'].get('mx') == 0 or d['boss']['left'] <= 0)) / len(wins3))
fwr = [d for d in rows if d['bk'] == 'fw']
fwwin = round(100 * sum(1 for d in fwr if not d['boss']['dead'] and (d['boss'].get('mx') == 0 or d['boss']['left'] <= 0)) / len(fwr))
fwdead = round(100 * sum(1 for d in fwr if d['boss']['dead']) / len(fwr))
fwdt = round(st.mean(d['boss']['t'] for d in fwr if d['boss']['dead']))
slow = sorted([v for v in ORDER if V[v]['t25'] > HI], key=lambda v: -V[v]['t25'])
fast = sorted([v for v in ORDER if V[v]['t25'] < LO], key=lambda v: V[v]['t25'])
weak = sorted([v for v in ORDER if V[v]['bossWin3'] < 60], key=lambda v: V[v]['bossWin3'])

CSS = """
@page{size:A4;margin:13mm 12mm 12mm}
*{box-sizing:border-box}
body{font-family:'Noto Sans CJK KR',sans-serif;color:#0b0b0b;font-size:10.2px;line-height:1.5;margin:0}
.pg{page-break-after:always;position:relative;min-height:268mm}
.pg:last-child{page-break-after:auto}
h1{font-size:22px;margin:0 0 2px;font-weight:900}
h2{font-size:14px;margin:12px 0 6px;font-weight:800;display:flex;align-items:center;gap:7px}
h2 .n{background:#3a2a5a;color:#fff;border-radius:50%;width:20px;height:20px;display:inline-flex;align-items:center;justify-content:center;font-size:11px}
.sub{color:#52514e;font-size:10.5px}
.kpis{display:grid;grid-template-columns:repeat(4,1fr);gap:8px;margin:10px 0}
.kpi{border:1px solid #e1e0d9;border-radius:8px;padding:8px 10px}
.kpi b{display:block;font-size:20px;font-weight:800}
.kpi span{color:#52514e;font-size:9.5px}
.box{border:1px solid #e1e0d9;border-radius:8px;padding:8px 11px;margin:6px 0;background:#fcfcfb}
.box.hl{border-color:#c9b8f0;background:#f7f3ff}
.box h3{margin:0 0 4px;font-size:11.5px}
ul{margin:3px 0;padding-left:16px} li{margin:1px 0}
table{border-collapse:collapse;width:100%}
.tb th,.tb td{border-bottom:1px solid #e1e0d9;padding:3px 6px;text-align:center;font-variant-numeric:tabular-nums}
.tb th{background:#3a2a5a;color:#fff;font-weight:700;font-size:9.5px}
.tb.small td{font-size:9.5px;padding:2px 5px}
td.nm{text-align:left!important;font-weight:600;white-space:nowrap}
.heat th{background:#3a2a5a;color:#fff;font-size:9.5px;padding:4px}
.heat td{border:2px solid #fff;text-align:center;padding:2px 4px;font-variant-numeric:tabular-nums;border-radius:4px}
.heat td.nm{background:#fff}
.heat td b{font-size:11px;margin-right:4px}
.heat td span{font-size:8.5px;opacity:.85}
.prop th{background:#3a2a5a;color:#fff;font-size:9.5px;padding:4px 5px;text-align:left}
.prop td{border-bottom:1px solid #e1e0d9;padding:5px 5px;vertical-align:top;font-size:9.6px}
.prop tr.grp td{background:#f0ecf8;font-weight:800;font-size:10.5px;color:#3a2a5a;padding:4px 6px}
.prop td.no{font-weight:900;font-size:13px;color:#3a2a5a;text-align:center;width:24px}
.prop td.who{font-weight:700;width:96px}
.prop td.what{font-weight:600;width:150px}
.pill{display:inline-block;border-radius:10px;padding:0 7px;font-size:9px;font-weight:700;background:#e6f0fc;color:#1c5cab;white-space:nowrap}
.pill.down{background:#fbe9e9;color:#a52a2a}
.legend{display:flex;gap:12px;font-size:9.5px;color:#52514e;margin:2px 0 4px}
.legend i{display:inline-block;width:10px;height:10px;border-radius:2px;margin-right:4px;vertical-align:-1px}
.two{display:grid;grid-template-columns:1.25fr 1fr;gap:12px}
.foot{position:absolute;bottom:0;left:0;right:0;font-size:8.5px;color:#898781;display:flex;justify-content:space-between;border-top:1px solid #e1e0d9;padding-top:3px}
.q{border:2px solid #ffc247;background:#fff8e6;border-radius:8px;padding:8px 11px;margin:8px 0}
"""
def foot(i, n): return f'<div class="foot"><span>hell survive 밸런스 시뮬레이션 리포트 · v5.25 기준 · {NROWS}판</span><span>{i} / {n}</span></div>'
NP = 6
nm = lambda vs: ', '.join(f'{V[v]["name"]}' for v in vs)
H = f"""<!doctype html><html><head><meta charset="utf-8"><style>{CSS}</style></head><body>
<section class="pg">
<h1>지옥의 생존자 · 전체 밸런싱 시뮬레이션</h1>
<div class="sub">v5.25 배포본 · 최종 진화형 20종 × 보스 4종 × 5판 = {NROWS}판 · 2026-10-21 · 다음 버전 v5.26 반영용</div>
<div class="kpis">
<div class="kpi"><b>{mmss(MED)}</b><span>Lv.25 도달 시간 (전체 중앙값)</span></div>
<div class="kpi"><b>{len(slow)}종 / {len(fast)}종</b><span>목표 구간({mmss(LO)}~{mmss(HI)})보다 느림 / 빠름</span></div>
<div class="kpi"><b>{win3}%</b><span>마왕 3종 3분 클리어율 (원숭이·마안·스켈레톤)</span></div>
<div class="kpi"><b>{fwwin}%</b><span>타락한 혈랑왕 3분 클리어율 (사망 {fwdead}%)</span></div>
</div>
<h2><span class="n">1</span>한눈에 보는 결론</h2>
<ul>
<li><b>Lv.25가 너무 늦은 캐릭터:</b> {nm(slow)} — 특히 <b>수호령의 총령(+75%)·진화한 지옥엘프(+54%)·사슬의 폭군(+47%)</b></li>
<li><b>너무 빠른 캐릭터:</b> {nm(fast) or '없음'} — 리자드는 Lv.10까지 {mmss(S['t10base']['lizard'])}로 8종 중 가장 빠름</li>
<li><b>마왕 3종 승률 60% 미만:</b> {nm(weak)} — 사슬의 폭군만 <b>딜 부족(3분 초과)</b>, 나머지는 <b>버티지 못해 사망</b></li>
<li><b>스켈레톤 마왕</b>이 3종 중 가장 어렵고(승률 58%), <b>혈랑왕</b>은 평균 {fwdt}초 만에 사망 — 3분 기준이면 거의 못 깸</li>
<li><b>필드 위기의 {ftlv}%가 Lv.10 전</b>, {ft2}%가 <b>2:00~2:59</b>에 몰림 — 캐릭터 문제가 아니라 초반 공통 구간</li>
</ul>
<h2><span class="n">2</span>판정 기준</h2>
<div class="box"><ul>
<li><b>Lv.25 시간:</b> 전체 중앙값 {mmss(MED)} ±15% = <b>{mmss(LO)}~{mmss(HI)}</b> 안이면 정상</li>
<li><b>보스전:</b> 3분 안에 클리어. 원숭이·마안·스켈레톤 합산 <b>승률 60% 이상</b>이면 "깰 수 있다"로 판정 (혈랑왕은 4쪽 질문 참고)</li>
<li><b>조정 폭:</b> 규격표 ①②③⑤ — 한 번에 스탯 1~2개, 소폭(6~10%)·중폭(11~20%) 위주, 최종 진화 예산(공격력 ×1.1~1.3 · 체력 +35~60) 안에서</li>
</ul></div>
<h2><span class="n">3</span>측정 방법</h2>
<div class="box">
<ul>
<li>판마다 <b>Lv.1부터 실제 필드 플레이</b>로 Lv.25(마왕성 등장)까지 → 체력을 채우고 <b>바로 마왕전, 3분 제한</b></li>
<li>카드는 <b>무작위 선택</b>(★조합은 60% 확률로 우선) = 평균적인 플레이. 난이도 0단계, 상점 강화 없음, 화면 1600×900</li>
<li>진화 조건은 원하는 루트로 맞춰 줌 (용암 체류·독약·이공벌레·체력 10 이하 등)</li>
<li>봇이 체력 20% 아래로 떨어지면 <b>'위기'</b>로 기록하고 체력을 채워 계속 진행 → 그 레벨이 <b>실패 지점</b>, 위기가 한 번이라도 있으면 <b>실패</b>로 셈</li>
<li>보스전은 무적·회복 없이 실제로 피하면서 싸움 (경고 범위·탄환 회피, 결계·소환물 처리)</li>
</ul>
<div style="margin-top:4px;color:#52514e">⚠ 봇은 사람보다 피하는 게 서툴러 <b>실패율 절대값은 높게</b> 나옵니다. <b>캐릭터끼리 비교</b>하는 용도로 봐 주세요. 판마다 편차가 커서(Lv.25 시간 표준편차 1~3분) 5% 안팎 차이는 의미 없습니다.</div>
</div>
<h2><span class="n">4</span>이 리포트 보는 법</h2>
<div class="box hl">2쪽 Lv.25 시간 → 3쪽 실패율·실패 지점 → 4쪽 보스전 → <b>5쪽 밸런싱안(번호 1~15)</b>. 빼고 싶은 번호만 알려 주시면 나머지를 v5.26에 반영하고, 반영본으로 같은 시뮬을 한 번 더 돌려 확인할게요.</div>
{foot(1, NP)}</section>

<section class="pg">
<h2><span class="n">5</span>Lv.25 도달 시간 (마왕성 등장까지)</h2>
<div class="legend"><span><i style="background:#2a78d6"></i>목표 구간 안</span><span><i style="background:#d03b3b"></i>느림</span><span><i style="background:#eda100"></i>빠름</span><span><i style="background:#9ec5f4"></i>가운데 50% 판 범위</span><span><i style="background:#eef4fc;border:1px solid #cde2fb"></i>목표 구간</span></div>
{chart_t25()}
<h2><span class="n">6</span>레벨 구간별 도달 시간 (중앙값)</h2>
{level_tbl()}
<div class="sub" style="margin-top:4px">Lv.5까지는 모두 1:10~1:30으로 비슷하고, 차이는 Lv.5~10(기본형 사냥 속도)과 Lv.15 이후(진화형 사냥 속도)에서 벌어집니다. Lv.10 도달: {' · '.join(f'{CHN[k]} {mmss(t)}' for k, t in sorted(S['t10base'].items(), key=lambda x: x[1]))}</div>
{foot(2, NP)}</section>

<section class="pg">
<h2><span class="n">7</span>Lv.25 실패율 · 실패 지점</h2>
<div class="sub">실패 = 체력 20% 아래로 떨어진 '위기'가 1번 이상. 막대 색 = 첫 위기가 온 레벨 구간 (진할수록 이른 레벨)</div>
<div class="legend">{''.join(f'<span><i style="background:{c}"></i>Lv.{b}</span>' for b, c in zip(BUCK, BC))}</div>
{chart_fail()}
<div class="two" style="margin-top:6px">
<div><h2><span class="n">8</span>위기가 오는 시간대</h2>{ft_svg}</div>
<div><h2><span class="n">9</span>읽을 거리</h2><div class="box"><ul>
<li>첫 위기의 <b>{ftlv}%가 Lv.10 전</b>, <b>{ft2}%가 게임 시간 2분대</b>. 2분대에 몹이 한 번에 4마리씩 약 0.3초마다 나오기 시작하고, 150초에 초반 완화가 끝남</li>
<li>피해의 <b>85~95%는 일반 몹 접촉</b>. 용암은 원거리 캐릭터(수호령·지옥엘프 20%대)에서만 큼</li>
<li>가장 안전: 성혈랑(25%) · 타락한 혈랑(35%) · 진화한 지옥엘프(40%)</li>
<li>가장 위험: 리자드 세 루트·몽환 키메라(85~95%) · 사슬의 폭군(90%, 대부분 Lv.10 전)</li>
</ul></div></div></div>
{foot(3, NP)}</section>

<section class="pg">
<h2><span class="n">10</span>보스전 결과 (3분 제한)</h2>
<div class="sub">칸 = 승리/판수 · 이긴 판이 있으면 평균 클리어 시간, 없으면 3분 동안 깎은 체력 % · 색이 진할수록 승률 높음</div>
{heat()}
<h2><span class="n">11</span>보스별 요약</h2>
{boss_tbl()}
<div class="q"><b>❓ 질문 — 타락한 혈랑왕도 "3분 안에 클리어" 기준에 넣을까요?</b><br>
규격표 ⑦은 숨은 보스 목표를 <b>3~4분</b>으로 잡고 있어서, 지금은 거의 모든 캐릭터가 3분 안에 못 깹니다(승률 {fwwin}%). 다만 원인은 시간보다 <b>평균 {fwdt}초 만에 죽는 것</b>(사망 {fwdead}%)이라 체력만 깎아서는 안 풀립니다.<br>
<b>(가) 그대로 두기 (추천)</b> — 숨은 보스는 도전용, 3분 기준에서 제외 &nbsp;·&nbsp; <b>(나) 혈랑왕 공격 피해 −15% (중폭)</b> — 3~4분 클리어를 목표로 버틸 시간 확보</div>
{foot(4, NP)}</section>

<section class="pg">
<h2><span class="n">12</span>보스전 패배 원인</h2>
{chart_outcome()}
<div class="box" style="margin-top:6px"><ul>
<li><b>사망형</b>(딜은 되는데 죽음): 쌍두 늑대 · 타락한 혈랑 · 업화 키메라 · 성화된 지옥엘프 · 심연의 늑대 · 버서커 리자드 → <b>생존 스탯</b>으로 보강</li>
<li><b>딜 부족형</b>(살아 있는데 3분 초과): 사슬의 폭군(55%) · 물의 도마뱀 전사(30%, 승률은 73%로 합격) → <b>공격력</b>으로 보강</li>
<li>문어 마법사 · 진화한 지옥엘프 · 성혈랑은 마왕 3종을 거의 다 깸 (성혈랑은 필드도 가장 안전 → 13번 소폭 하향)</li>
</ul></div>
{foot(5, NP)}</section>

<section class="pg">
<h2><span class="n">13</span>밸런싱안 — 빼고 싶은 번호만 알려 주세요</h2>
{prop_tbl(failtxt)}
<div class="box" style="margin-top:6px"><b>그대로 두는 캐릭터:</b> 혈랑 · 맹독/용암/폭탄 달팽이(5번 공통만) · 바람/몽환 키메라 · 물의 도마뱀 전사 · 수호의 리저드(6번 공통만) · 문어 마법사 · 진화한 지옥엘프(3번 공통만). 진화한 지옥엘프는 Lv.25가 느리지만(+54%) 판마다 편차가 가장 커서(±3분) 3번 효과를 보고 다시 판단할게요.<br>
<b>반영 후:</b> v5.26 빌드 → 진화 경로 15개 테스트 → 바뀐 캐릭터만 같은 방식으로 다시 시뮬(사용자가 원할 때) → 결과 비교표 전달.</div>
{foot(6, NP)}</section>
</body></html>"""
open('/home/claude/hell-survive/build/bal/report.html', 'w').write(H)
print('ok', NROWS, MED, LO, HI, win3, fwwin, fwdead, fwdt, ft2, ftlv)
