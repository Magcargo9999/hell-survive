import sys, math, collections, html, json, re
sys.path.insert(0, '/home/claude/hell-survive/tools')
from pattern_data import C
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
OUT = '/home/claude/hell-survive/build/plan/'
for f in fm.findSystemFonts():
    if 'NotoSansCJK-Regular' in f: fm.fontManager.addfont(f)
plt.rcParams['font.family'] = 'Noto Sans CJK KR'; plt.rcParams['axes.unicode_minus'] = False
e = html.escape

# ---------- 표본 통계 ----------
N = len(C)
cnt_fun = collections.Counter(c[4] for c in C); cnt_mech = collections.Counter(c[3] for c in C)
byg = collections.Counter(c[0] for c in C)
FUNN = {'가독성':'가독성(읽고 피함)','리듬':'리듬(박자 변주)','처벌창':'처벌 창(틈=공격 기회)','환경':'환경·주도권','위험보상':'위험↔보상','연출':'연출·스펙터클','적응':'적응(규칙 변화)','학습':'학습·공유'}
# 이 게임의 현재 패턴 (코드 기준) 을 같은 태그로 분류
CUR = [('원숭이','연타(combo)','지연','리듬'),('원숭이','꼬리 휘두르기(tail)','장판','가독성'),('원숭이','돌진(dash)','돌진','가독성'),('원숭이','도약 내려찍기(jump)','장판','가독성'),
 ('원숭이','지진(quake)','장판','가독성'),('원숭이','충격파 줄(wave)','장판','가독성'),('원숭이','휩쓸기(sweep, 분노)','장판','리듬'),('원숭이','분노 전환(체력 50%/60%)','페이즈','연출'),
 ('마안','부채꼴 탄(fan)','탄막','가독성'),('마안','나선(spiral)','탄막','리듬'),('마안','낙하 구체(rain)','장판','가독성'),('마안','구체(orbs)','탄막','가독성'),
 ('마안','심판 빔(judge)','장판','가독성'),('마안','촉수 도넛(tent)','장판','리듬'),('마안','폭발(burst, 분노)','탄막','연출'),('마안','분노 전환','페이즈','연출'),
 ('스켈레톤','내려찍기(slam)','장판','가독성'),('스켈레톤','콤보+참격파','지연','리듬'),('스켈레톤','첨탑 결계→깨면 기절','상태','처벌창'),('스켈레톤','해골병 소환','소환','적응'),('스켈레톤','1·2 단계 페이즈(66%·33%)','페이즈','적응'),
 ('혈랑왕','물어뜯기/베기','돌진','가독성'),('혈랑왕','광란 질주(rampage)','돌진','리듬'),('혈랑왕','피의 흡수(drain, 안전 통로)','장판','위험보상'),('혈랑왕','도약(pounce)','돌진','가독성'),
 ('혈랑왕','혈인(sigil)','장판','가독성'),('혈랑왕','거대화(grow)→발구르기/쓸기/돌격','페이즈','연출'),
 ('공통','5단계 보너스: 낙석·십자 균열·고리·세 줄 균열·마력 폭발','장판','연출')]
curf = collections.Counter(c[3] for c in CUR)

def bar_fun():
    ks = [k for k,_ in cnt_fun.most_common()]
    fig, ax = plt.subplots(figsize=(7.2,3.1), dpi=170)
    ys = range(len(ks))
    ax.barh(ys, [cnt_fun[k]/N*100 for k in ks], color='#2a78d6', height=0.36, label=f'조사 표본 (n={N})')
    ax.barh([y+0.38 for y in ys], [curf.get(k,0)/len(CUR)*100 for k in ks], color='#d9a21b', height=0.36, label=f'우리 게임 현재 패턴 (n={len(CUR)})')
    ax.set_yticks([y+0.19 for y in ys]); ax.set_yticklabels([FUNN[k] for k in ks], fontsize=9); ax.invert_yaxis()
    for y,k in zip(ys,ks):
        ax.text(cnt_fun[k]/N*100+0.6, y, f'{cnt_fun[k]}', va='center', fontsize=8, color='#184f95')
        ax.text(curf.get(k,0)/len(CUR)*100+0.6, y+0.38, f'{curf.get(k,0)}', va='center', fontsize=8, color='#8a6410')
    ax.set_xlabel('비율 (%) — 막대 옆 숫자는 개수', fontsize=8); ax.legend(fontsize=8, frameon=False, loc='lower right')
    for s in ('top','right'): ax.spines[s].set_visible(False)
    plt.tight_layout(); plt.savefig(OUT+'fun.png'); plt.close()
bar_fun()
def bar_mech():
    ks = [k for k,_ in cnt_mech.most_common()]
    cm = collections.Counter(c[2] for c in CUR)
    fig, ax = plt.subplots(figsize=(7.2,2.8), dpi=170)
    x = range(len(ks))
    ax.bar([i-0.2 for i in x], [cnt_mech[k]/N*100 for k in ks], 0.38, color='#2a78d6', label='조사 표본')
    ax.bar([i+0.2 for i in x], [cm.get(k,0)/len(CUR)*100 for k in ks], 0.38, color='#d9a21b', label='우리 게임')
    ax.set_xticks(list(x)); ax.set_xticklabels(ks, fontsize=9); ax.set_ylabel('%', fontsize=8); ax.legend(fontsize=8, frameon=False)
    for s in ('top','right'): ax.spines[s].set_visible(False)
    plt.tight_layout(); plt.savefig(OUT+'mech.png'); plt.close()
bar_mech()

# ---------- 회피 가능성 검증 (5단계, 최악) ----------
SPD = {'리자드(최저)':163,'달팽이':175,'늑대·키메라':200,'사슬악마':212,'궁수(최고)':215}
REACT = 0.16; PRMAX = 10; TOL = 10
MK = {'monkey':0.8*0.7/1.22,'eye':0.8*0.7/1.22,'skel':0.82*0.75/1.22,'fw':0.8*0.75/1.22}
# 형식 F: 따라오다 고정(이동 중이면 반응시간 불필요) -> 고정 시간 T 동안 R+PR 이상 이동해야  | 여유 = spd*T/(R+PR)
# 형식 S: 이미 보이는 정지 장판(서 있다 발견) -> (T-REACT)*spd/(R+PR+TOL)
# 형식 L: 선형(띠) -> 옆으로 w/2+PR+TOL 이동  | (T-REACT)*spd/(w/2+PR+TOL)
# 형식 G: 이동하는 벽+틈 -> 틈까지 가로 거리 / 도착 시간
def F(R,T,s): return s*T/(R+PRMAX)
def S(R,T,s): return (T-REACT)*s/(R+PRMAX+TOL)
def L(w,T,s): return (T-REACT)*s/(w/2+PRMAX+TOL)
def G(lat,arr,s): return (arr-REACT)*s/lat
D = []  # id, boss, name, ref, how, tele, fun, safe, cost, checks[(label, formula-desc, func)]
def chk(label, desc, fn): return (label, desc, fn)
D.append(dict(id='M1', boss='원숭이 마왕', name='지연 내려찍기(속임수 이중 장판)', ref='엘든링 마르기트 지연타 · 하데스 알렉토 따라오는 원',
 how='기존 도약 내려찍기에 "한 박 쉬기"를 넣는다. ①빨간 원(반경 140)이 플레이어를 따라오다 고정 → ②보스가 공중에서 멈춘 채 채움 막대가 0.3초 멈춤 → ③내리찍기. 이어서 ④착지 직전 작은 두 번째 원이 현재 위치를 다시 노림. 일찍 구르면 두 번째 원에 걸리고, 박자를 기다리면 안 맞는다.',
 tele='원 테두리+채움 막대(멈춤 구간은 막대 색이 노랑으로 바뀜). 기존 도약과 같은 빨강 원이라 학습 필요 없음.',
 fun='리듬 변주(박자 속임) · 읽고 피함. 기다리는 용기가 보상.', safe='원 반경 140·110, 점유 합계 약 11%(원 두 개). 두 원 사이는 겹치지 않게 배치(중심 ≥ 260px).',
 cost='낮음(bossStart "jump" 변형, 텔레 객체 2개)', 
 checks=[chk('1번 원(고정 1.05초, R140)','F: 이속×T / (R+PR)',lambda s:F(140,1.05,s)),chk('2번 원(고정 0.9초, R110)','F',lambda s:F(110,0.9,s))]))
D.append(dict(id='M2', boss='원숭이 마왕', name='졸개 원숭이 호출(75% · 25%)', ref='하데스 메가이라 HP 구간 소환 · 건전 아모콘다',
 how='체력 75%·25%에서 마왕이 포효하고 졸개 원숭이 6마리를 화면 밖 둘레에서 부른다. 졸개를 처치하면 필드 경험치 구슬이 나오고, 마왕은 졸개가 3마리 이상 살아 있는 동안 받는 피해 -15%(소환 방치 불이익).',
 tele='포효 연출 1.0초 + 졸개가 나올 위치에 보라 연기.', fun='적응(규칙 변화) · 서바이버 장르 정체성(몹 학살의 맛).',
 safe='졸개는 일반 몹과 동일. 플레이어 반경 320px 안에는 생성하지 않음(갑툭튀 금지). 보스 패턴과 동시 발생 시 졸개는 장판을 만들지 않음.',
 cost='낮음(기존 spawnEnemy + 규칙)', checks=[]))
D.append(dict(id='M3', boss='원숭이 마왕', name='바위 분열(던졌다 쪼개짐)', ref='건전 총알왕 분열탄 · 하데스 쪼갠 장판',
 how='마왕이 바위를 던져 플레이어 앞쪽(이동 방향 0.35초 앞)에 큰 원(R130)이 뜨고, 착지 후 0.5초 뒤 큰 원에서 바깥 반경 270px 위치로 작은 원(R70) 6개가 터진다. 원 사이 틈(130px) 또는 중앙 안전 고리(반경 150~200)로 피한다.',
 tele='큰 원과 작은 원 6개를 처음부터 모두 표시(작은 원은 옅은 색 → 터지기 직전 진해짐).', fun='읽고 피함 · 쪼개지는 연출 → "큰 한 방"을 작은 위험 여러 개로 쪼개 공정하게(설계 글).',
 safe='점유 합계 ≈ 큰 원 5.3万 + 작은 원 6×1.5万 = 약 14.4万px² = 아레나 16%. 틈 폭 130px ≥ 피격 지름(2×(PR+TOL)=40).',
 cost='중간(복합 텔레 7개, 지연 폭발)', checks=[chk('큰 원(R130, 고정 1.0초)','F',lambda s:F(130,1.0,s)),chk('틈 통과: 130px / 피격 지름 40px','틈폭÷지름',lambda s:130/40)]))
D.append(dict(id='E1', boss='마안군주', name='소등(어둠의 눈꺼풀)', ref='건전 하이 프리스트 소등 · 캐논발로그 어두운 방',
 how='마안군주가 눈을 감으면 4초 동안 화면이 어두워지고 플레이어 반경 340px만 보인다. 이 동안 보스는 새 장판을 만들지 않고 이미 깔린 예고만 처리. 눈을 다시 뜨는 순간 "섬광 부채꼴 탄"이 한 번 나가며 끝난다.',
 tele='어두운 구간에서도 모든 예고선(빨강/보라)은 밝게 덧그려 보이게 한다(가독성 보장). 끝나기 1초 전 눈꺼풀 깜빡임 연출.', fun='연출·긴장(분위기). 위험이 늘지 않고 "보이지 않는 불안"만 늘려 공정.',
 safe='새 판정 면적 0. 섬광 부채꼴 1회(반각 0.45rad, 반경 520) — 부채꼴 점유 약 13%(반각 0.45rad×반경 520), 예고 1.1초.', cost='낮음(렌더 마스크 + 상태 1개)',
 checks=[chk('섬광 부채꼴 예고 1.1초(옆 이동 거리 필요 ≈ 부채 호폭/2)','L(폭 220)',lambda s:L(220,1.1,s))]))
D.append(dict(id='E2', boss='마안군주', name='튕기는 구체', ref='건전 캐논발로그 튕기는 탄 · 하데스 알렉토 회전 칼날',
 how='큰 구체 2개(분노 3개)가 느리게(150px/s, 가장 느린 리자드 163보다 느림) 날아가 벽에서 최대 1번 튕긴다. 경로는 얇은 점선으로 끝까지 미리 보인다. 구체는 6초 뒤 사라진다.',
 tele='경로 점선(튕김 지점까지 포함) + 구체 발광. 예고 1.1초 뒤 출발.', fun='경로를 읽는 퍼즐감 · 환경(벽) 활용. 마안군주에 "벽 모서리 사용"이라는 새 축 추가.',
 safe='구체 지름 56 + 피격 여유 → 폭 76px 띠. 동시 구체 ≤3, 순간 점유 ≈ 3×π×38² = 1.4万px² (1.5%). 상향: 속도 240→150, 예고 0.8→1.1초, 튕김 2→1회, 동시 3→2(분노 3).', cost='중간(반사 계산, 벽 폴리곤 교차)',
 checks=[chk('경로 위에서 옆으로 빠지기(예고 1.1초, 폭 76)','L',lambda s:L(76,1.1,s)),chk('구체 속도 150 대비 이속비(1.0 이상 = 달려서도 따돌림)','이속÷150',lambda s:s/150)]))
D.append(dict(id='E3', boss='마안군주', name='아레나 가장자리 잠식(분노 전환)', ref='하데스 티시포네 방이 좁아짐 · 건전 올드 킹 아레나 분할',
 how='분노로 바뀌는 순간 아레나 가장자리 폭 50px가 3초에 걸쳐 보라 불길로 변해 끝까지 유지된다(닿으면 틱 피해). 전투 공간은 영구히 약 27% 감소.',
 tele='변하기 전 3초 동안 경계선이 점선으로 먼저 깜빡이고, 진행 방향(시계) 표시.', fun='연출 · 페이즈 전환이 "숫자 상승"이 아니라 "공간 변화"로 느껴짐(설계 글).',
 safe='남는 공간 ≈ 73% (아레나 면적 89.7万px², 둘레 4849px × 50px 근사). 마안 도넛(바깥 반경 360)이 겹쳐도 중앙 고리가 열려 있음.', cost='중간(폴리곤 오프셋 + 판정)',
 checks=[chk('3초 전조: 가장자리 50px 밖으로 이동','S',lambda s:(3.0-REACT)*s/(50+PRMAX+TOL))]))
D.append(dict(id='S1', boss='스켈레톤 마왕', name='정면 방패', ref='하데스 테세우스 방패 · 세키로 자세 시스템(정면 대응)',
 how='스켈레톤 마왕이 방패를 든 채 바라보는 방향의 ±70° 호에서 오는 피해를 -35% 받는다. 마왕은 느리게 몸을 돌리므로(기존 turnT 0.55초, 분노 0.32초) 옆·뒤로 돌아 때리는 보상이 생긴다. 새 장판 없음.',
 tele='방패 아이콘 호 표시(바라보는 방향 부채꼴, 옅은 은색). 맞으면 "막힘" 스파크.', fun='위치 선정(환경·주도권). 원거리 캐릭터도 이동 한 번으로 보상.',
 safe='새 판정 없음 = 회피 문제 없음. 대신 딜 밸런스: 근접 정면 딜 -35% → 시뮬로 보정 필요.', cost='낮음(피해 계산 한 곳 + 그리기)',
 checks=[chk('위험 면적 증가','없음',lambda s:99)]))
D.append(dict(id='S2', boss='스켈레톤 마왕', name='뼈 파도(틈 있는 벽)', ref='건전 하이 드래군 틈 있는 탄막 · 방사형 줄 + 안전 통로(우리 inTeleGap)',
 how='가로(또는 세로) 뼈 벽이 220px/s로 아레나를 쓸고 지나간다. 벽에는 폭 240px의 틈이 1개(분노 시 2개) 있다. 틈의 위치는 시작 순간 플레이어의 가로 위치에서 ±200px 이내로 고정해 반드시 닿을 거리에 둔다.',
 tele='벽이 지나갈 띠 전체를 0.9초 동안 옅게 표시, 틈은 초록 윤곽. 출발은 아레나 끝(플레이어까지 ≥ 700px).', fun='가독성 + 리듬(틈으로 쓱 지나가는 맛) · 건전 틈 있는 탄막의 쾌감.',
 safe='순간 점유: 두께 90×(1320−240)=9.7万px² ≈ 11%, 통과 후 100% 해소. 틈은 항상 플레이어 쪽 ±200px.', cost='중간(이동 판정 + 틈 배치 규칙)',
 checks=[chk('틈까지 최악 가로 거리 260px, 도착 3.2초','G',lambda s:G(260,3.2,s)),chk('틈 통과 폭 240px / 피격 지름 40px','폭÷지름',lambda s:240/40)]))
D.append(dict(id='S3', boss='스켈레톤 마왕', name='룬 원 맥동', ref='하데스 테세우스 올림포스 가호(주기 장판)',
 how='플레이어 주변(250~400px)에 룬 원(R90) 3개가 7초간 떠 있고 1.6초마다 한 번씩 맥동 피해. 첫 맥동은 1.4초 뒤. 마왕이 직접 쫓아오며 압박하므로 룬 위에서 싸우지 못하게 하는 역할.',
 tele='룬 테두리가 처음부터 계속 보이며 채움 시계가 맥동 직전 차오름(소리 동반).', fun='리듬(박자 장판) · 환경 압박. 기존 도약/내려찍기와 달리 "시간 지속 장판".',
 safe='점유 합계 3×2.5万 = 7.6万px² ≈ 8.5%. 룬 사이 간격 ≥ 200px.', cost='낮음',
 checks=[chk('첫 맥동 1.4초(정지 상태에서 원 밖으로)','S',lambda s:S(90,1.4,s))]))
D.append(dict(id='F1', boss='타락한 혈랑왕', name='무리 사냥(새끼 늑대 돌진 줄)', ref='하데스 아스테리오스 돌진 · 건전 방사형 줄(틈)',
 how='핏빛 안개 속에서 새끼 늑대 4마리가 서로 평행한 가로 줄을 따라 맵 끝에서 끝까지 순차 돌진(0.35초 간격). 줄 폭 100, 줄 사이 간격 260 → 틈 160. 혈랑왕은 정지(처벌 창 1.2초).',
 tele='줄 4개가 0.9초 동안 붉게 표시, 돌진 방향 화살표.', fun='처벌 창(보스가 멈춘 시간 = 공격 기회) · 가독성.',
 safe='줄 점유 4×100×(맵 폭 1438) ≈ 57.5万px² = 맵의 약 45%지만 순차 통과 + 줄 사이 틈 160px 상시. 플레이어가 줄 안이면 옆 70px만 이동하면 탈출.', cost='중간',
 checks=[chk('줄 안에서 옆으로 탈출(예고 0.9초, 폭 100)','L',lambda s:L(100,0.9,s)),chk('줄 사이 틈 160px / 피격 지름 40px','폭÷지름',lambda s:160/40)]))
D.append(dict(id='F2', boss='타락한 혈랑왕', name='혈월 구역(위험 ↔ 보상)', ref='엘든링 말레니아 흡혈 · 건전 아모콘다 먹이 버프',
 how='맵 한 곳에 반경 260의 붉은 달빛 원이 10초 생긴다. 안에서는 내 공격력 +25%, 이속 -15%, 혈랑왕이 내 쪽으로 오는 속도 +20%. 들어갈지 말지는 플레이어의 선택. 원 자체는 피해가 없다.',
 tele='달빛이 내려오며 윤곽 선명, 효과 문구 표시.', fun='위험↔보상(선택의 재미) · 연출.',
 safe='판정 면적 0(피해 장판 아님). 원 점유 ≈ 21.2万/129万 ≈ 16%. 강제 효과 없음.', cost='낮음',
 checks=[chk('피해 장판 아님 → 회피 요구 없음','-',lambda s:99)]))
D.append(dict(id='F3', boss='타락한 혈랑왕', name='질주 벽 박치기 기절', ref='하데스 아스테리오스 기둥 충돌 기절 · 세키로 체간 무너뜨리기',
 how='광란 질주 구간이 맵 가장자리에 닿으면 충돌 충격파(R100)가 터지고 혈랑왕이 1.2초(5단계는 1.0초) 기절한다. 플레이어가 가장자리를 등지고 서서 돌진 경로를 유도하면 큰 딜 창이 열린다.',
 tele='기존 질주 예고 띠 끝에 "충돌 표시(X)"와 충격파 원을 미리 그린다.', fun='처벌 창 + 환경 활용 + 주도권(보스를 이용).',
 safe='새 판정은 충돌 지점 원 R100(1.0초 예고) 하나. 점유 약 2.4%.', cost='낮음(rampage 구간 끝 판정)',
 checks=[chk('충돌 지점 원 R100(예고 1.0초, 정지 상태)','S',lambda s:S(100,1.0,s))]))
for d in D:
    t = []
    for lab,desc,fn in d['checks']:
        row = {k:round(fn(v),2) for k,v in SPD.items()}
        t.append((lab,row))
    d['res'] = t
json.dump([{ 'id':d['id'],'res':d['res']} for d in D], open(OUT+'check.json','w'), ensure_ascii=False, indent=1)
# 아레나 가장자리 50px 면적 (E3)
poly = None
s = open('/home/claude/hell-survive/src/game_template.html').read()
i = s.index('const ARENA = {'); j = s.index('};', i)
poly = [(x*1.25,y*1.25) for x,y in eval(re.search(r'poly:\s*(\[\[.*?\]\]),', s[i:j], re.S).group(1))]
def area(p): return 0.5*abs(sum(p[k][0]*p[(k+1)%len(p)][1]-p[(k+1)%len(p)][0]*p[k][1] for k in range(len(p))))
per = sum(math.dist(poly[k], poly[(k+1)%len(poly)]) for k in range(len(poly)))
A0 = area(poly); band = per*50 - 0  # 근사(코너 중복 무시)
print('area',A0,'perimeter',per,'band50 ratio',band/A0)
E3RATIO = band/A0
json.dump({'A0':A0,'per':per,'e3':E3RATIO}, open(OUT+'arena.json','w'))
print(len(D), N, cnt_fun.most_common())

# =================== HTML ===================
exec(open('/home/claude/hell-survive/tools/pattern_html.py').read())
