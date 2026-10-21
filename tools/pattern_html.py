import base64
def img(f): return 'data:image/png;base64,' + base64.b64encode(open(OUT+f,'rb').read()).decode()
SPDK = list(SPD.keys())
def verdict(row):
    m = min(row.values())
    return ('통과' if m >= 1.10 else '주의' if m >= 1.0 else '실패'), m
def chk_tbl(d):
    rows = ''
    for lab, r in d['res']:
        if min(r.values()) >= 99: rows += f'<tr><td>{e(lab)}</td><td colspan="6" class="c">해당 없음 (피해 판정 증가 없음)</td></tr>'; continue
        v, m = verdict(r) if '이속÷150' not in lab else ('참고', min(r.values()))
        cls = {'통과':'ok','주의':'wn','실패':'ng','참고':'nt'}[v]
        rows += f'<tr><td>{e(lab)}</td>' + ''.join(f'<td class="c">{r[k]:.2f}</td>' for k in SPDK) + f'<td class="c {cls}">{v}</td></tr>'
    return rows
BOSSES = ['원숭이 마왕','마안군주','스켈레톤 마왕','타락한 혈랑왕']
def design_cards():
    o = ''
    for b in BOSSES:
        o += f'<h3>{b}</h3>'
        for d in D:
            if d['boss'] != b: continue
            o += f'''<div class="card"><div class="ch"><span class="id">{d['id']}</span><b>{e(d['name'])}</b><span class="ref">참고: {e(d['ref'])}</span></div>
<table class="kv"><tr><th>동작</th><td>{e(d['how'])}</td></tr><tr><th>예고</th><td>{e(d['tele'])}</td></tr><tr><th>재미</th><td>{e(d['fun'])}</td></tr><tr><th>안전·면적</th><td>{e(d['safe'])}</td></tr><tr><th>구현</th><td>{e(d['cost'])}</td></tr></table></div>'''
    return o
def check_all():
    o = '<table class="ck"><tr><th>#</th><th>검증 항목</th>' + ''.join(f'<th>{k}<br><span class="sm">{v}</span></th>' for k,v in SPD.items()) + '<th>판정</th></tr>'
    for d in D:
        for i,(lab, r) in enumerate(d['res']):
            if min(r.values()) >= 99: o += f'<tr><td>{d["id"]}</td><td>{e(lab)}</td><td colspan="6" class="c">해당 없음</td></tr>'; continue
            v, m = verdict(r) if '이속÷150' not in lab else ('참고', min(r.values()))
            cls = {'통과':'ok','주의':'wn','실패':'ng','참고':'nt'}[v]
            o += f'<tr><td>{d["id"]}</td><td>{e(lab)}</td>' + ''.join(f'<td class="c">{r[k]:.2f}</td>' for k in SPDK) + f'<td class="c {cls}">{v}</td></tr>'
    return o + '</table>'
def catalog():
    o = ''
    for g in ['Hades','Elden Ring','Sekiro','Gungeon','Maple','설계 글']:
        rows = [c for c in C if c[0] == g]
        o += f'<h3>{g} <span class="sm">({len(rows)}개)</span></h3><table class="cat"><tr><th>보스</th><th>패턴</th><th>유형</th><th>재미</th><th>출처</th></tr>'
        for c in rows: o += f'<tr><td>{e(c[1])}</td><td>{e(c[2])}</td><td>{c[3]}</td><td>{FUNN[c[4]].split("(")[0]}</td><td class="c">{c[5]}</td></tr>'
        o += '</table>'
    return o
cur_rows = ''.join(f'<tr><td>{e(a)}</td><td>{e(b)}</td><td>{c}</td><td>{FUNN[dd].split("(")[0]}</td></tr>' for a,b,c,dd in CUR)
nv = sum(1 for c in C if c[5]=='★'); ns = N - nv
AUD = [  # (보스, 패턴, 모델, 필요거리 px, 이전 고정시간 s, 현재 고정시간 s) — 5단계 분노(최악), 리자드 163
 ('원숭이','도약 내려찍기 R140','F',150,0.95,1.05),('원숭이','돌진 띠 w150','F',85,0.23,0.60),('원숭이','분노 연속 돌진','F',85,0.32,0.60),
 ('원숭이','꼬리 휘두르기 R195','F',145,0.46,0.95),('원숭이','꼬리 연속(분노)','F',145,0.50,0.90),('원숭이','충격파 줄 w76','F',48,0.19,0.32),
 ('원숭이','휩쓸기 w86(분노)','F',53,0.28,0.48),('원숭이','지진 R96','S',116,0.82,0.98),('원숭이','착지 고리 140~300','S',145,0.70,1.15),('원숭이','연타 후속 R112','S',132,0.17,0.98),
 ('마안','낙하 구체 R64','S',84,0.44,0.75),('마안','심판 빔 w118','F',69,0.28,0.50),('마안','촉수 도넛','S',115,0.44,0.95),('공통','5단계: 마력 폭발 R230','F',180,1.10,1.50),
 ('혈랑왕','질주 첫 구간','F',75,0.39,0.65),('혈랑왕','질주 다음 구간','F',75,0.30,0.50),('혈랑왕','물어뜯기','F',75,0.23,0.52),('혈랑왕','광폭 베기','F',110,0.27,0.77),
 ('혈랑왕','도약 R150','F',160,0.85,1.05),('혈랑왕','혈인 R108','S',128,0.78,1.00),('혈랑왕','광폭 마무리 R165','F',115,0.30,0.80),
 ('혈랑왕','거대 발구르기 R200','F',210,0.22,1.45),('혈랑왕','거대 쓸기 1타(반경 480→420)','F',186,0.25,1.33),('혈랑왕','거대 쓸기 2타','F',186,0.15,1.33),('혈랑왕','거대 돌격 w240','F',130,0.28,0.90),
 ('스켈레톤','내려찍기 R150','F',160,0.63,1.08),('스켈레톤','분노 재내려찍기','F',160,0.56,0.99),('스켈레톤','베기 부채꼴','F',110,0.20,0.72),('스켈레톤','돌진 띠 w150','F',85,0.18,0.60),
 ('스켈레톤','영혼 불기둥 R92','S',112,0.78,0.95),('스켈레톤','참격파 w110','F',65,0.14,0.50)]
def aud_margin(m,need,T,spd=163): return (T*spd/need) if m=='F' else ((T-REACT)*spd/need)
def aud_tbl():
    o='<table class="ck"><tr><th>보스</th><th>패턴</th><th>모델</th><th>필요 거리</th><th>이전 고정시간</th><th>이전 여유</th><th>현재 고정시간</th><th>현재 여유</th></tr>'
    for b,n,m,need,t0,t1 in AUD:
        a0,a1=aud_margin(m,need,t0),aud_margin(m,need,t1)
        c0='ng' if a0<1 else 'wn' if a0<1.1 else 'ok'; c1='ng' if a1<1 else 'wn' if a1<1.1 else 'ok'
        o+=f'<tr><td>{b}</td><td>{e(n)}</td><td class="c">{m}</td><td class="c">{need}</td><td class="c">{t0:.2f}</td><td class="c {c0}">{a0:.2f}</td><td class="c">{t1:.2f}</td><td class="c {c1}">{a1:.2f}</td></tr>'
    return o+'</table>'
n_old_bad=sum(1 for x in AUD if aud_margin(x[2],x[3],x[4])<1.0); n_new_bad=sum(1 for x in AUD if aud_margin(x[2],x[3],x[5])<1.0); n_new_wn=sum(1 for x in AUD if 1.0<=aud_margin(x[2],x[3],x[5])<1.1)
AUDSEC=f"""<section class="pg"><h2>9. 기존 패턴 회피 상향 · 보스 확률 · 공격력 (v6.07 반영)</h2>
<div class="box"><b>무엇을 바꿨나</b> — 5단계 분노(최악) · 리자드 이속 163 기준으로 기존 패턴 {len(AUD)}개를 점검해, 락온 후 <b>고정 시간(예고가 멈춘 뒤 맞기까지)</b>이 짧은 패턴의 예고를 늘렸습니다. 여유 = (이속×시간) ÷ 필요 거리 (S는 반응 0.16초 포함). 이전 <b>{n_old_bad}개</b>가 1.0 미만(이속 강화 없이는 사실상 회피 불가)이었고 현재 1.0 미만 <b>{n_new_bad}개</b>, 1.00~1.10 <b>{n_new_wn}개</b>.<br>
<b>대신 보스 공격력 상향</b>: 원숭이·마안·혈랑왕 공통 피해식 1.08 → 1.19 (<b>+10%</b>, 소폭), 스켈레톤 마왕 피해 배율 ×1.10. 예고가 길어져 쉬워진 만큼의 보정이며 <b>시뮬 미실행</b>이라 체감은 실측 후 조정이 필요합니다.<br>
<b>보스 확률</b>: 0단계 원숭이 100% · 1단계 원숭이 30/마안 70 · 2단계 원숭이 15/마안 15/스켈레톤 70 · 3단계 이상은 기존(균등 1/3). (이전에는 0단계도 원숭이/마안 반반)</div>
{aud_tbl()}
<div class="box warn" style="margin-top:6px">거대화 쓸기는 반경을 480→420으로 줄여(<b>판정 축소</b>) 필요 거리를 낮췄습니다. 마안군주 탄막류(부채·나선·구체·폭발)는 탄 속도 기반이라 이번 점검에서 제외했습니다. 수치는 모델 계산이며 실제 봇/사람 플레이로 검증한 값은 아닙니다.</div></section>"""

CSS = """
@page{size:A4;margin:14mm 13mm 16mm}
*{box-sizing:border-box}body{font-family:'Noto Sans CJK KR';font-size:10pt;line-height:1.5;color:#1a1a1a;margin:0}
h1{font-size:22pt;margin:0 0 4px}h2{font-size:15pt;margin:0 0 8px;border-bottom:2px solid #2a78d6;padding-bottom:4px}h3{font-size:11.5pt;margin:12px 0 5px;color:#184f95}
.sub{color:#666;font-size:10pt}.pg{page-break-after:always}.sm{font-size:8pt;color:#777;font-weight:400}.c{text-align:center}
table{border-collapse:collapse;width:100%}th,td{border:1px solid #d6d4cd;padding:3px 6px;vertical-align:top}th{background:#eef4fc;font-weight:700;text-align:left}
.cat td,.cat th{font-size:8.3pt;padding:2px 5px}.ck td,.ck th{font-size:8.6pt}
.card{border:1px solid #bcd3f2;border-radius:6px;margin:6px 0;padding:6px 8px;break-inside:avoid}.ch{display:flex;gap:8px;align-items:baseline;margin-bottom:3px}
.id{background:#2a78d6;color:#fff;border-radius:4px;padding:0 6px;font-weight:700;font-size:9pt}.ref{margin-left:auto;font-size:8pt;color:#666;text-align:right}
.kv th{width:62px;font-size:8.6pt}.kv td{font-size:9pt}
.box{background:#f4f8fd;border-left:4px solid #2a78d6;padding:7px 10px;margin:8px 0;border-radius:3px}.warn{background:#fff7e5;border-left-color:#d9a21b}
.ok{background:#e1f4e4;color:#1b6b2c;font-weight:700}.wn{background:#fff1d1;color:#8a5a00;font-weight:700}.ng{background:#fbdada;color:#9b1c1c;font-weight:700}.nt{background:#eee}
ul{margin:3px 0 3px 18px;padding:0}li{margin:1px 0}img{width:100%}
.pri td:first-child{font-weight:700;text-align:center}
"""
HTML = f"""<!doctype html><html lang="ko"><head><meta charset="utf-8"><style>{CSS}</style></head><body>
<section class="pg"><h1>보스 패턴 추가 기획서</h1><div class="sub">지옥의 생존자 · Hades · Elden Ring · Sekiro · Enter the Gungeon · MapleStory 연구 기반 · v6.07(기존 패턴 상향) 반영판</div>
<h2 style="margin-top:14px">한눈에 보기</h2>
<div class="box"><ul>
<li><b>조사 표본 {N}개</b> (Hades {byg['Hades']} · Gungeon {byg['Gungeon']} · Elden Ring {byg['Elden Ring']} · Sekiro {byg['Sekiro']} · MapleStory {byg['Maple']} · 설계 글 원칙 {byg['설계 글']}). 이 중 <b>{nv}개</b>는 이번에 실제로 페이지를 읽어 확인(★), <b>{ns}개</b>는 일반 지식(☆, 이번 조사에서 재확인 못 함).</li>
<li><b>재미가 나오는 곳</b>은 한 가지가 아니라 ① 읽을 수 있는 예고 ② 박자 변주(지연타) ③ 틈 = 공격 기회 ④ 규칙·공간 변화(페이즈) ⑤ 위험↔보상 선택 ⑥ 보스·환경을 이용하는 주도권 — 6가지로 정리됩니다.</li>
<li><b>우리 게임 진단</b>: 예고 가독성은 강점(28개 중 13개가 "읽고 피함"). 반면 <b>처벌 창 1 · 위험↔보상 1 · 환경 0 · 학습 0</b>으로 비어 있음 → 신규 패턴은 이 빈칸을 채우는 쪽으로 설계.</li>
<li><b>신규 패턴 {len(D)}개</b> (보스당 3~4개, 메이플에서 영감받은 E4·S4·F4 포함). 전부 "새 장판 하나 더"가 아니라 <b>리듬·선택·공간·보상</b> 중 하나를 추가하는 형태이며, 서로 복사본이 되지 않게 구분했습니다.</li>
<li><b>규칙 9 검증</b>: 5단계 최악 조건(분노 배율 + 가장 느린 리자드 이속 163)에서 모든 신규 패턴이 안전 구역·통로·시간을 확보합니다. 단 하나(F3 충돌 원)는 1차 설계가 실패해 반경 120→100, 예고 0.7→1.0초로 고쳤습니다. 기존 패턴도 같은 기준으로 점검해 예고를 늘렸습니다(9장, v6.07).</li>
</ul></div>
<h2>구성</h2><table><tr><td>1</td><td>조사 방법과 표본의 한계</td><td>5</td><td>우리 게임 패턴 진단</td></tr><tr><td>2</td><td>재미 요소 분석 (어디서 재미가 오는가)</td><td>6</td><td>신규 패턴 15개 기획</td></tr><tr><td>3</td><td>게임별 핵심 통찰</td><td>7</td><td>5단계 회피 가능성 검증</td></tr><tr><td>4</td><td>패턴 표본 {N}개 목록 (부록)</td><td>8</td><td>도입 순서·시뮬 검증 계획</td></tr><tr><td>9</td><td colspan="3">기존 패턴 회피 상향(v6.07 반영) · 보스 확률 · 공격력</td></tr></table>
</section>

<section class="pg"><h2>1. 조사 방법과 표본의 한계</h2>
<ul><li><b>수집</b>: Hades(프리마게임즈 푸리·테세우스/아스테리오스 공략), Elden Ring(지연 공격 분석 기사), Sekiro(잇신 공략), Gungeon(총알왕 위키, 게임랜서 보스 가이드, 루도 가이드), 설계 글(itch.io, 게임 디벨로퍼, 유카이 초우) 페이지를 읽고 패턴·메커니즘을 추출.</li>
<li><b>접근 실패</b>: Gungeon 팬덤 위키·Fextralife 일부·Red Bull 등은 접근 차단/내용 없음으로 읽지 못함 → 해당 보스(예: 개틀링 갈매기·드래군 세부)는 가이드 기사 수준의 요약만 사용.</li>
<li><b>분류</b>: 모든 표본에 ① 메커니즘 유형(장판·탄막·돌진·지연·소환·페이즈·환경·상태·반격·추적) ② <b>재미 원천 1개</b>(가독성·리듬·처벌 창·환경·위험보상·연출·적응·학습)를 붙임.</li></ul>
<div class="box warn"><b>한계</b> — 재미 원천 태그는 제가 붙인 <b>주관 분류</b>(패턴당 대표 1개)라 같은 패턴이 두 요소를 동시에 만족하는 경우가 많습니다. 통계는 "경향"으로만 읽어 주세요. 플레이어 만족도 설문·방송 지표는 이번 조사에 없습니다.</div>
<h2 style="margin-top:14px">2. 재미 요소 분석 — 어디서 재미가 오는가</h2>
<img src="{img('fun.png')}"><div class="sm">파랑 = 조사 표본 분포 · 노랑 = 우리 게임 현재 패턴 {len(CUR)}개(부록 5장 분류)</div>
<table style="margin-top:6px"><tr><th style="width:105px">재미 원천</th><th>왜 재미있나 (조사에서 나온 근거)</th><th style="width:150px">대표 사례</th></tr>
<tr><td>가독성</td><td>예고(모양·색·소리)가 일관되면 "내가 졌다"가 아니라 "내가 못 읽었다"가 되어 재도전 의지가 생김. 미세한 모션만으로 구분하는 건 함정(설계 글).</td><td>하데스 그림자 불꽃 원, 폭발 경로, 테세우스 조준점</td></tr>
<tr><td>리듬 변주</td><td>정해진 박자를 일부러 어겨 "조급한 회피"를 처벌. 엘든링 지연타는 짜증과 웃음(공유된 고난)을 동시에 만들고 밈이 됨.</td><td>마르기트, 잇신 권총 4연사 마지막 발</td></tr>
<tr><td>처벌 창</td><td>피한 대가로 열리는 틈. 알렉토 분노 충전·아스테리오스 기둥 충돌·잇신 반사처럼 "내 선택이 만든 틈"일수록 쾌감이 큼.</td><td>기둥 기절, 갈매기 미사일 틈</td></tr>
<tr><td>환경·주도권</td><td>보스 AI/환경을 이용하는 해법이 있고 보상이 크면 학습이 즐거움이 됨(설계 글). 단, 월드 규칙은 공정해야 함.</td><td>트레드노트 기둥, 방패 뒤잡기</td></tr>
<tr><td>위험↔보상</td><td>더 위험한 위치·행동을 고르면 이득. 억지 부담이 아니라 선택이어야 함.</td><td>티시포네 채찍(스턴), 아모콘다 먹이</td></tr>
<tr><td>적응(규칙 변화)</td><td>숫자 상승이 아닌 새 위협·새 규칙 추가. 같은 전술 재사용을 막음(설계 글).</td><td>메가이라 소환, 하데스 2페이즈</td></tr>
<tr><td>연출</td><td>큰 연출은 작은 위험 여러 개로 쪼개 공정하게 유지. 연출만으로는 퍼즐이 되지 않으므로 메커니즘과 짝을 이룸.</td><td>총알왕 분열탄, 방 축소</td></tr></table>
</section>

<section class="pg"><h2>3. 게임별 핵심 통찰</h2>
<table><tr><th style="width:90px">게임</th><th>가져올 것</th><th style="width:210px">우리 게임에 맞추는 법</th></tr>
<tr><td>Hades</td><td>① 따라오다 고정되는 원/선 예고 ② HP 구간마다 소환·장판 추가 ③ 방이 좁아지는 페이즈 ④ 기둥 충돌 기절 ⑤ 두 보스 협공 후 한쪽이 죽으면 광폭</td><td>마안군주 분노 때 가장자리 잠식(E3), 혈랑왕 질주 벽 충돌(F3), 졸개 소환(M2). 2인 협공은 중복 우려로 보류.</td></tr>
<tr><td>Elden Ring</td><td>지연타(박자 속임), 흡혈로 위험 유도, 페이즈 변신. 지연을 쓸 땐 "홀드 자세"가 눈에 보여야 공정.</td><td>원숭이 지연 내려찍기(M1) — 장판은 고정이라 일찍 구르면 다음 원에서 처벌, 기다리면 무피해.</td></tr>
<tr><td>Sekiro</td><td>공격마다 확실한 징조, 막기/피하기/반격 중 정답이 정해진 위험 공격, 페이즈마다 새 규칙.</td><td>정답 있는 반격은 조작 체계가 달라 직접 이식 불가 → "정면 방패(S1)"처럼 위치 선택으로 번역.</td></tr>
<tr><td>Gungeon</td><td>분열탄, 방사형 줄, 틈 있는 탄막, 어둠, 튕기는 탄, 아레나 분할. 기본 철학: "예고가 읽히면 아무리 빽빽해도 틈이 있다".</td><td>뼈 파도(S2), 튕기는 구체(E2), 소등(E1), 바위 분열(M3), 무리 사냥(F1).</td></tr>
<tr><td>MapleStory</td><td>① 경고 후 안전지대(눈 이펙트·용 뒤·고정 위치) ② 같은 자리 반복 금지 등 <b>배울 수 있는 규칙</b>(윌 거미 다리) ③ 색·모션으로 변형 구분(윌 눈 색) ④ 추적 구체·폭발 구체 ⑤ 맵 축소(비명의 벽) ⑥ 게이지/면역 같은 선택 기믹. 단점: 파티 의존(폭탄 분산)·최대 체력 비례 즉사기는 이 게임엔 부적합.</td><td>안식처(E4), 규칙 있는 3연 내려찍기(S4), 추적 도깨비불(F4). 즉사기·파티 분산은 제외.</td></tr>
<tr><td>설계 글</td><td>페이즈마다 행동·공간 변화, 일관된 예고, 큰 효과를 작은 위험 여러 개로, 플레이어 주도권.</td><td>규칙 9(안전 구역 보장)와 방향이 같음.</td></tr></table>
<h2 style="margin-top:14px">5. 우리 게임 패턴 진단</h2>
<img src="{img('mech.png')}">
<table class="cat"><tr><th>보스</th><th>패턴</th><th>유형</th><th>재미</th></tr>{cur_rows}</table></section>

<section class="pg"><h2>6. 신규 패턴 15개 기획</h2>
<div class="box">설계 원칙: ① 예고는 항상 보임(기존 빨강·보라 체계 유지) ② 1진화 이하엔 영향 없음(보스전 전용) ③ 규칙 9: 5단계 최악 이속(163)으로 안전 구역·시간 확보 ④ 같은 보스 안에서 서로 다른 재미 축(리듬/선택/공간/보상)을 하나씩. 아래 카드는 보스별 3~4개(E4·S4·F4가 메이플 연구로 추가된 분).</div>
{design_cards()}
</section>

<section class="pg"><h2>7. 5단계 회피 가능성 검증 (규칙 9)</h2>
<div class="box"><b>가정</b>: 5단계 분노 배율 — 원숭이·마안 0.8×(1−0.06×5)/1.22=<b>0.459</b>, 스켈레톤 0.82×0.75/1.22=<b>0.504</b>, 혈랑왕 0.8×0.75/1.22=<b>0.492</b>. 반응 0.16초, 피격 반경 PR 최대 10 + 여유 10. 이속은 리자드 163 ~ 궁수 215.<br>
<b>여유 비율</b> = (이동 가능 거리) ÷ (필요 거리). 1.10 이상 <span class="ok">통과</span> · 1.00~1.10 <span class="wn">주의</span> · 1.00 미만 <span class="ng">실패</span>. 틈 항목은 틈 폭 ÷ 피격 지름(40px).<br>
형식 — F: 따라오다 고정되는 원(움직이는 중이면 반응 시간 불필요, 여유 = 이속×T ÷ (R+PR)) · S/L: 이미 떠 있는 원/띠 위에 서 있다가 발견(반응 시간 포함) · G: 움직이는 벽의 틈.</div>
{check_all()}
<h3>결과 해석</h3><ul>
<li>신규 {len(D)}개 중 판정 대상 항목 모두 최저 이속(리자드)에서도 <b>1.10 이상</b>으로 설계 (F3는 1차 설계 0.63~0.83로 <b>실패</b> → R120/0.7초 → R100/1.0초로 수정해 통과).</li>
<li><b>기존 패턴 점검</b>: 기존 패턴도 같은 기준으로 점검해 예고를 늘렸습니다(9장 표, v6.07 반영). 예: 도약 내려찍기는 여유 1.03 → 1.14.</li>
<li>E2 상향: 구체 속도 240→150(리자드 163보다 느려 달려서도 따돌림, 이속÷150 ≥ 1.09), 예고 0.8→1.1초(옆 이동 여유 1.80→2.64), 튕김 2→1회, 동시 3→2개(분노 3). 참고 행은 판정 제외.</li>
<li>면적 비교(순간 점유): M1 11% · M3 16% · E1 13%(섬광 1회) · E2 1.5% · E3 영구 27% · S2 11%(이동) · S3 8.5% · F1 45%(순차·틈 160 상시) · F2 16%(피해 없음) · F3 2.4%. 어느 것도 화면 전체를 덮지 않으며 틈/통로가 항상 남음.</li></ul>
</section>

<section class="pg"><h2>8. 도입 순서 · 시뮬 검증 계획</h2>
<table class="pri"><tr><th style="width:36px">순서</th><th>패턴</th><th>이유</th></tr>
<tr><td>1</td><td>S1 정면 방패 · F2 혈월 구역 · F3 질주 벽 박치기 · E1 소등</td><td>판정 면적이 늘지 않아 안전. 비어 있던 "환경·위험보상·처벌 창"을 바로 채움. 구현 비용 낮음.</td></tr>
<tr><td>2</td><td>M1 지연 내려찍기 · S3 룬 원 맥동 · M2 졸개 호출</td><td>기존 코드의 변형으로 구현. M1은 박자 변주의 효과 검증용.</td></tr>
<tr><td>3</td><td>S2 뼈 파도 · E2 튕기는 구체 · M3 바위 분열 · F1 무리 사냥 · E3 가장자리 잠식</td><td>새 판정(이동 벽·반사·복합 텔레)이 필요해 구현/버그 위험이 큼 → 앞 단계 반응을 보고 선택.</td></tr></table>
<h3>검증 방법 (원하실 때만 실행 — 규칙 8)</h3><ul>
<li>패턴 하나 추가할 때마다 <b>smoke 15/15</b> + 해당 보스 봇 시뮬 (난이도 0 · 3 · 5, 캐릭터 5종 × 20판) — 사망 원인 로그에서 신규 패턴 비중, 평균 클리어 시간 변화(규격표 ⑦ 목표 구간 유지) 확인.</li>
<li>피해 환산: 규격표 ② 보정 배율에 맞춰 신규 패턴의 피해는 기존 패턴과 같은 급(26~36)으로 시작, 기존 패턴 가중치를 낮춰 <b>보스 총 위험도는 ±10% 이내</b> 유지.</li>
<li>스크린샷으로 예고 가독성(색·윤곽·깜빡임) 육안 확인, 소등(E1)은 모든 예고선이 밝게 남는지 확인.</li></ul>
<div class="box warn"><b>사용자 확인이 필요한 항목</b> — ① S1 정면 방패는 근접 캐릭터 딜에 영향(-35% 호) → 도입 시 소폭 보정(규격표 ②)이 필요한지 ② E3 가장자리 잠식은 공간 27% 영구 감소라 "재설계급" 변화에 가까움 → 허락 필요(규격표 규칙) ③ 신규 패턴을 난이도 몇 단계부터 켤지(제안: S1·F2·F3은 전 난이도, 나머지는 2단계+).</div>
<h3>Sources</h3><div style="font-size:8.3pt;line-height:1.35">
<a>primagames.com/gaming/hades-boss-guide-furies-megaera-alecto-and-tisiphone</a> · <a>primagames.com/tips/hades-boss-guide-how-beat-theseus-and-asterius</a> · <a>automaton-media.com/en/news/20220316-10577/</a> · <a>sekiroshadowsdietwice.wiki.fextralife.com/Isshin,_the_Sword_Saint</a> · <a>enterthegungeon.wiki.gg/wiki/Bullet_King</a> · <a>gameranx.com/features/id/47856/article/enter-the-gungeon-boss-guide/</a> · <a>ludo.guide/guide/enter-the-gungeon/boss-guides/all-bosses-strategies-and-weaknesses</a> · <a>itch.io/blog/1024105/designing-the-perfect-boss-battle-a-game-developers-holy-grail</a> · <a>gamedeveloper.com/design/creating-cool-boss-fights</a> · <a>yukaichou.com/advanced-gamification/game-design-technique-14-mastering-the-boss-fight/</a><br>
메이플: <a>namu.wiki 윌 공격 패턴</a> · <a>strategywiki.org/wiki/MapleStory/Lucid</a> · <a>strategywiki.org/wiki/MapleStory/Will</a> · <a>digitaltq.com/maplestory-lucid-boss-guide</a> · <a>dexless.com/guides/black-mage-boss-guide-and-genesis-weapons.366/</a><br>검색으로 목록만 확인(내용 미열람): speedrun.com Gungeon 가이드, dualshockers/cbr Malenia 가이드, fextralife Perilous Attacks. ☆ 표시 표본은 일반 지식.</div>
</section>

<section class="pg"><h2>체크리스트 — 신규 패턴 15개 전체에 적용된 항목만 ✔</h2>
<table><tr><th style="width:34px">✔</th><th>항목</th><th>근거</th></tr>
<tr><td class="c ok">✔</td><td>예고가 항상 보임(기존 빨강·보라 체계, 소등 중에도 예고선 유지)</td><td>6장 각 카드 "예고" 칸</td></tr>
<tr><td class="c ok">✔</td><td>규칙 9: 5단계 최악 조건(분노 배율 + 리자드 163)에서 안전 구역·통로·시간 확보 (판정 증가 없는 S1·F2는 해당 없음)</td><td>7장 표: 판정 대상 전 항목 여유 1.10 이상</td></tr>
<tr><td class="c ok">✔</td><td>안전 구역 없는 전체 덮기 없음 (최대 순간 점유 F1 45% 틈 160px 상시, E4는 안식처 지정형 — <b>E4는 도입 전 허락 필요</b>)</td><td>7장 면적 비교</td></tr>
<tr><td class="c ok">✔</td><td>보스전 전용 — 1진화 이하 캐릭터 스킬·스탯 변경 없음</td><td>모든 카드(보스 코드만 수정)</td></tr>
<tr><td class="c ok">✔</td><td>기존 패턴과 재미 축이 겹치지 않게 구분(리듬·선택·공간·보상)</td><td>6장 설계 원칙 ④</td></tr>
<tr><td class="c ok">✔</td><td>E2 회피 가능성 상향 반영(속도 150·예고 1.1초·튕김 1회)</td><td>7장</td></tr>
<tr><td class="c nt">☐</td><td>규격표 ② 피해·배율 보정 확인 — <b>미적용</b>(도입 시 확인)</td><td>8장</td></tr>
<tr><td class="c nt">☐</td><td>봇 시뮬·smoke 15/15 검증 — <b>미실행</b>(원하실 때만)</td><td>8장, 규칙 8</td></tr>
<tr><td class="c nt">☐</td><td>스크린샷 가독성 확인 — <b>미실행</b>(코드 미구현)</td><td>8장</td></tr></table></section>
{AUDSEC}
<section><h2>부록 A. 패턴 표본 {N}개 (★ 이번에 읽음 · ☆ 일반 지식)</h2>{catalog()}</section>
</body></html>"""
open(OUT+'report.html','w').write(HTML)
print('html ok')
