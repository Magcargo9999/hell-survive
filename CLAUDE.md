# 지옥의 생존자 (hell survive) — 작업 인수인계

한 파일짜리 HTML5 서바이버류 게임. 사용자(편규빈, GitHub Magcargo9999)가 도트 시트를 주고 기능·밸런스를 요청하면 Claude가 구현한다.
**이 문서를 먼저 다 읽고 작업할 것.** 답변은 한국어로 짧고 간결하게.

## 꼭 지킬 규칙 (사용자 지시)
1. **파일 이름:** 매 빌드 `hell survive v.N.NN.html`, 버전은 매번 올린다. 마지막 배포 = **v7.15** → 다음은 v7.16. (v6.01부터 번호 체계가 6대로 바뀜 · v7.01부터 7대: 지하 10층·버섯 맵 개편 기준)
   - 끝자리: 작은 수정 · 가운데 자리: 캐릭터·보스 추가 같은 큰 변화.
2. **도트는 절대 수정·재색칠 금지.** 자르기·배경 제거·마스크·배율 조정만 허용.
3. 기능은 **단순하게**. 서로 복사한 듯한 중복 스킬/카드 금지.
4. **규격표 ①~⑩**(`docs/hell survive 규격표 v4.15.pdf`)을 따른다. 규칙을 깨야 하면 먼저 허락받는다.
   - 소폭 ±6~10% · 중폭 ±11~20% · 대폭 ±21~35% · 재설계급 35%+ (스탯별 보정 배율은 규격표 ②).
   - 소개 문구는 역할 하나 + 약점 하나 (규칙 ⑤).
5. **1진화에는 스킬을 넣지 않는다** (사용자가 직접 요청한 경우만 예외: 연보라 총령 차지샷, 문어 마법사 코끼리 돌진).
6. **매 버전 GitHub 커밋 + 푸시** (아래 배포 절차). 커밋 메시지에 변경점 한 줄.
7. **티어 결과를 줄 때는 항상 보스별 상성 + 티어표 사이트에 들어갈 값(s2/s1 JSON) 전부 포함**해서 PDF로 준다 (`docs/`의 기존 "티어표 추가" PDF 형식 참고).
8. 오래 걸리는 시뮬레이션은 사용자가 원할 때만. "오래 걸리면 하지 마" 라고 한 적 있음.
9. **화면·보스방 전체를 덮어 어디에도 안전한 곳이 없는 패턴(무조건 못 피하는 패턴)은 넣지 않는다.** 이속 강화를 안 찍어서 못 피하는 건 괜찮지만, 이속을 끝까지 찍어도 피할 안전 구역·통로·시간이 없는 패턴은 안 된다. 새 패턴·난이도 배율을 넣을 때 최고 단계(5단계)에서도 안전 구역이 남는지 확인한다. (예: 흡혈 고리의 안전 통로 `inTeleGap`)
10. **설명 문구는 항상 구현을 따라간다.** 스킬·카드·조합·진화 소개·난이도 안내·보스 안내 배너·도감·상점 등 화면에 적힌 수치·효과 문구가 구현과 다르게 바뀌면(밸런스·기믹 수정 포함) 같은 작업 안에서 문구도 전부 고친다. 기능을 고칠 때마다 이름·수치로 템플릿을 grep해 남은 옛 문구가 없는지 확인하고, 무엇을 고쳤는지 사용자에게 보고한다.
11. **딜 미터기 이름은 화면의 이름과 항상 같게.** 스킬은 `skillName()`(변형 이름 포함), 카드·조합은 `upName()`/`altOf()`를 쓴다. 새 스킬·카드·피해 출처(`DSRC` 키)를 만들면 `dmName`이 영문 id·옛 이름을 내지 않는지 확인한다 (`tools/tests/dmeter22.py`).

## 폴더 구조
```
index.html              배포본 (GitHub Pages가 서비스하는 실제 게임, 약 75MB — 100MB 넘으면 푸시 거부되니 이미지를 따로 불러오는 구조로 바꿔야 함)
src/game_template.html  ★ 실제로 고치는 원본 (이미지 자리는 '__XXX__' 토큰)
src/build.py            템플릿 + src/assets 이미지 → build/hell_survive.html
src/assets/             모든 도트 아틀라스(webp/png). 경로는 build.py 표 참고
tools/check.py          문법 확인 (node --check)
tools/smoke.py          진화 경로 15개 자동 테스트 (정상이면 15줄 모두 끝이 [] )
tools/tests/*.py        유령 · 문어 · 수호 리저드 · 챌린지(chal.py) · 타락천사(angel.py) · 악마 총잡이(gun.py) · 오류 찾기(fuzz.py: 전 캐릭터 무작위로 오래 돌려 콘솔 오류 수집)
tools/h301.py           playwright 공용 헬퍼 (__lv, __run, __s 등 테스트용 전역 함수 주입)
tools/sim600.py         봇 시뮬레이터 (B=보스전, L=필드) · tools/bal_run30.sh <빌드> <폴더> <단계> <N> [보스...] → tools/bal_cmp30.py <폴더> <단계> (보스별 승률·깎은 체력)
tools/perf.py           프레임 측정 (실제 루프 + CPU 프로파일, 장면 field·boss·angel·dream·chal)
tools/tier_run.sh       새 캐릭터 티어 측정 / tools/tier_an.py 결과 분석
tools/atlas/*_build.py  각 캐릭터 시트 → 아틀라스 만들 때 썼던 스크립트 (참고용, 원본 시트는 사용자가 다시 첨부)
                        shroom_build.py = 히든 마물 대형 버섯 괴물(sh, 시트 알파 그대로)
                        mush_build.py = 지하 6~10층 버섯 세트(바닥·소품·버섯형 악마·보스맵, 소품 좌표 mprops.json)
                        ch_build.py = 챌린지 맵 · 절단안의 짐승(cm) · 심연의 촉수마왕(ab) · an_build.py = 타락천사(an·anfx·amap) · gun_build.py = 악마 총잡이(gun)
data/tier_v501.json     기준 티어표 (s0/s1/s2), data/tier_additions.json 이후 추가분
docs/                   규격표 · 티어표 · 기획서 PDF
build/                  (git 무시) 빌드 결과·스크린샷
```

## 작업 절차
```bash
pip install playwright --break-system-packages  # 없으면 (Chromium은 보통 미리 설치됨)
python3 tools/check.py                 # 1) 문법
python3 src/build.py                   # 2) 빌드 → build/hell_survive.html  (+ python3 tools/mkmap.py 로 docs/MAP.md 갱신)
timeout 900 python3 tools/smoke.py | grep -c "\[\]$"   # 3) 15 이어야 정상 (약 5분)
PYTHONPATH=tools python3 tools/tests/octo.py        # 필요할 때 캐릭터별 테스트
# 4) 새 UI·이펙트는 playwright로 스크린샷 찍어 직접 눈으로 확인
cp build/hell_survive.html "hell survive v.6.09.html"   # 사용자에게 보낼 파일 (SendUserFile)
cp build/hell_survive.html index.html
git add -A && git commit -m "v6.10: 변경점 한 줄" && git push origin main
```
- 커밋 작성자: `-c user.name="Magcargo9999" -c user.email="gyubinpyeon@gmail.com"`
- 템플릿 수정은 python 문자열 치환(정확히 1회 일치 assert)으로 하는 게 안전했다. 주석을 줄 중간에 넣으면 뒤 코드가 주석 처리되니 주의 (실제로 한 번 깨졌음 → check.py로 잡힘).
- 테스트 훅: 게임은 `window.__G` 로 내부 노출 (startGame, tick, addExp, spawnEnemy, enterArena, raiseCastle, cast, pick, hurt, DMETER, fwStart …). 새 기능 테스트에 필요하면 `__G`에 추가.

## 게임 구조 요약 (src/game_template.html, 약 6,500줄)
- **캐릭터** `CHARS`: wolf, snail, archer, chimera, lizard, twins(사슬 악마, 벨리아·셀리아 처치 해금), ghost(연보라 구슬 유령), octo(문어 마법사, 히든: 난이도 2+ 유니크 몹 처치 해금), gun(악마 총잡이, 지하 6층 마왕 처치 해금 · 예전에 깬 기록 `chOpen()`도 인정). 각 `role`/`weak` 필드 = 카드 앞면 문구.
- **진화:** Lv.10 루트 선택 → Lv.20 최종 (용암 달팽이는 Lv.25 3단계). `applyEvo(to)` 에 캐릭터별 스탯. 폼 데이터: `ROUTE_FORMS`, `SNAIL_FORMS/VENOM_FORMS/LAVA_FORMS/BOMB_FORMS`, `ARCHER_*`, `CHIM_FORMS`, `LIZ_FORMS`, `TWIN_FORMS`, `GHOST_FORMS`, `OCTO_FORMS`. 프레임별 사각형 `anim.X.fr=[[x,y,w,h,ax,ay]…]`.
  - 달팽이 루트: venom(맹독) / lava(용암) / **bomb(폭탄, v5.13 추가)**: 기본 공격 폭탄 1→4번째 점점 커짐, 폭발 자리 불웅덩이, 최종 스킬 megabomb.
  - 리자드 루트: sword(→ rage/water) / guard(수호의 길 → 수호의 리저드, 스킬 shell 반격의 갑주).
  - 늑대 혈랑 최종: blood / holy / fallen(타락한 혈랑, 숨은 보스 처치 시 열림, 스킬 bsigil 혈왕의 진).
- **악마 총잡이** (템플릿 'v6.40 악마 총잡이' 블록, `GUN_FORMS` · 아틀라스 `GUNA`, 그리기는 `drawGun`): 0진화 악마 총잡이 → Lv.10 지옥의 무법자 → Lv.20 악마처형자(스킬 `roll` 구르기). 리볼버 6발(`P.mag`/`P.magI`) — 평타 한 번 = 한 발(`gunShot`), 6발을 다 쓰면 재장전 `gunReload()`(1초, 빠른 장전 카드 −15%씩). 재장전할 때 6발이 하나씩 무작위(`GUN_AMMO`): 일반탄 55% 100% · 도탄 25% 100%(적에게 최대 3번 · 화면 끝 2번 튕김 `gunEdge`) · 불씨탄 15% 200% + 관통 + 화상 3초(`burnSrc`) · 공포탄 5% 10%. 고유 카드 `UNIQUE.gun`: 빠른 장전(gReload) · 특수탄 강화(gSpec, 불씨·도탄 +15%) · 불씨 각인(gEmber, 불씨 +5%p / 일반 −5%p) · 현상금 사냥(gBounty, 처치마다 1.5초 이속 +2% 중첩, 최대 3/5/7). 구르기(`rollQ`): 4초 안에 SPACE로 3번 짧게(약 210px, 무적), 첫 구르기 때 남은 탄을 가까운 적들에게 전부 쏘고 재장전(`gunDump`), 시간이 지나면 남은 횟수 증발. 0·1진화는 스킬 없음. 머리 위 탄창 표시(`drawGunMag`). 딜미터기 키 `g:N/R/F/B`.
- **스킬:** `SKILLS`, `SKILL_CD`(쿨타임 초), `uniqueSkill(s)()`, `castSkill()`.
- **카드:** `UPGRADES`(공용, `alt: {캐릭터/루트: [이름, 문구]}`로 캐릭터별 이름), `UNIQUE`(캐릭터 전용), `SYNERGIES`(★조합, 재료 2장 Lv.3, `only:` 전용). `cardView`, `openChoice`(카드 앞면=효과, 누르면 뒷면=조합 / 진화 갈림길이면 이후 최종 진화), `openUpgrade`(기본 3장, 상점 '넓어진 선택지'면 4장).
- **강화 상점** `PERKS` (캐릭터 상점과 분리): hp/spd/dmg/exp/magnet 각 10, banish 5, regen 3(초당 +0.1), shard 5(+5%), critd 5(+10%p), choice 1(5000), revive 1.
- **재생:** 기본 재생 없음(상점 구매). 캐릭터별 P.regen만 (1.2초 이상 정지 시 25%).
- **보스:** 원숭이 / 마안군주(eye) / 스켈레톤(skel) — 마왕성 보스방 `ARENA` (배율 `AS=1.25`), 타락천사(angel) — 전용 보스맵 `AMAP`(받은 그림 1672×941을 정수 2배, 다각형 `AMAP.poly`, 아래 통로가 출구 `arenaExit()`), 숨은 보스 타락한 혈랑왕(fw) — 제단 `BMAP`(s 1.65). 흡혈 고리 패턴에 안전 통로(`inTeleGap`).
  - **보스 등장 확률** `pickBossK(t)` / `BOSS_TBL`: 층마다 그 층에서 처음 나오는 보스 70% + 앞 층까지의 보스가 나머지 30% 균등 (지하 1층 원숭이 100 · 2층 마안 70 · 3층 스켈레톤 70 · 4층 타락천사 70 · 5·6층 4종 25%씩). 다음 층부터 나오는 보스는 그 전 층에 안 나온다.
  - **타락천사** (템플릿 'v6.30 타락천사' 블록, 조절값 `AN = {hp, dm, ph}`, 미니보스는 원숭이 전사): 1페이즈 근접 — 베기 3연속 · 리듬 함정(박자마다 4개씩 터지고 마지막 붉은 원은 엇박으로 0.46초 늦게, 방금 터진 자리에 다시 깔림) · 성스러운 방패(정면 ±69° 피해 0 `anFront` → `hurtEnemy`에서 막음, 등 뒤만 들어감, 끝나면 깨지고 휘청) · 추적 빛기둥. 체력 70% `anTrans` 흑화(2.6초 무적 + 충격파) → 2페이즈 원거리 — 흑백 구체(`anOrbs`: 검은 = 닿으면 피해, 흰 = 0.7초씩 엇갈려 시간 안에 닿지 않으면 피해) · 빛의 창 · 순간이동(가까이 1.5초 붙으면). 바닥 원은 비스듬히 본 타원(`AN_RY` 0.62, 예고 `t.ry`). 도트는 2배 nearest, 이펙트는 시트 조각을 'lighter'로.
  - 마안군주 기둥은 장식만(충돌 없음).
- **유니크 몹** `UNIQ`: 한 판에 종류별 1회, 난이도 3+ 은 동시에 2마리까지.
- **난이도:** 이름은 **지하 1층~15층** (`floorName(t)`, 내부 값 `P.tier` 0~14 · 세이브 `SAVE.diff`는 그대로 · 6~10층 버섯 · 11~15층 어인섬 세트 `floorSet`). 몹 체력 층당 +15%, 몹 공격 +10%, 보스·미니·유니크 체력 +30%. 정예 구슬은 4층부터.
- **HUD:** 체력바 아래 획득 카드 칩, 캐릭터 머리 위 체력바, 설정의 딜 미터기(`DSRC` 태그 → `DMETER`), 성유물·슬롯 화면밖 화살표.
- **그림·성능 (v6.30):** `loadImg`가 ImageBitmap으로 바꿔 둔다(처음 그릴 때 해독 끊김 방지). `hq()` 확대 캔버스는 `HQ_MAX` 4096px 이하. 필드 바닥은 512px 덩어리 캐시(`groundChunk`, 용암 칸·키 큰 소품만 매 프레임), 비네트는 캐시(`drawVignette`), 화면 밖 잡몹·구슬은 안 그린다. 이미지 목록은 `SRC` 이름 = `IMG` 이름 (나중에 불러와도 되는 것은 `LAZY_IMG`).
- **세이브:** localStorage `hellSurvivorSave1` (기기·브라우저별). 키를 바꾸면 사용자 진행이 날아가니 절대 바꾸지 말 것.
- **∞ 챌린지 모드 (v6.20, 템플릿 'v6.20 ∞ 챌린지 모드' 블록):** 난이도 5단계 마왕 처치 시 해금(`SAVE.ch.open`, 예전 5단계 클리어 스펙 `fw.snap.tier>=5`도 인정). 시작 화면 [∞ 챌린지 모드] 버튼 → `chMode` → `startChallenge`. 전역 `chal`(판 상태), `CHM`(맵 그림 3.5배 · 다각형 `inCh` · 밖은 `chPull`).
  - `P.tier=2`(마왕 패턴 기믹 약화). 잡몹 체력 `chTime()`(10분까지 원래 속도, 이후 **분당 ×1.07 기하급수**) · 생성량/상한 천천히 · 공격력 `chDmgT`(**5분부터 1분마다 +12%**, v6.41).
  - 5레벨마다 강적 1마리(`chEvent`): Lv%15=5 `CH_EV_A`(미니·히든·유니크) / =10 `CH_EV_B`(미니·히든) / =0 `CH_BOSS`(원숭이·마안·스켈레톤·혈랑왕·촉수마왕). 사이클 `chal.cyc`마다 강해짐. **마왕 5종 모두 챌린지 맵(필드)에서 싸운다**(v6.41: `chEnterBoss` → `chFieldPlace`로 플레이어 앞 560px에 세움, `inPoly`가 챌린지에서는 `inCh`, 필드 잡몹은 그대로 남고 계속 나옴(촉수마왕전만 신규 생성 중단), 스켈레톤 첨탑 `skpPts()`·혈랑왕 질주 목표는 마왕 첫 자리 `chal.fbC` 기준). 처치 후 쉼터(`chShelter` 10초 + 안식/어둠의 계약).
  - 룬 조각 `chFrag`(**3개=룬 1개**, v6.41 · 강적/황금 도망자 1개·마왕 2개 기본, `chRew` 최대 ×2.1, 8종 스탯 각 5단계, 챌린지에서만 적용, `SAVE.ch.rune/frag`). 보물 `TREASURES`(사망 시 버틴 시간 10/15/20분, 모든 모드에서 효과, `SAVE.ch.tr`): 쥐 이빨 목걸이 · 도깨비 주머니(`dropChest`) · 깨진 거울.
  - 황금 도망자(`chGoldSpawn`, v6.41: 체력 ×8.1(+35%) · 이속 플레이어의 0.6배) · 엘리트 접두사 20분~(`chPrefix` 빠름/분열/보호막 `e.shd`) · 심연 추격자 25분~(`chal.chaser`, 이속 100, 불사).
  - 신규 미니보스 절단안의 짐승(`mini.bk='cut'`, 원본 대기·이동은 왼쪽/공격 줄은 오른쪽을 봄) · 신규 마왕 심연의 촉수마왕(`boss.bk='ab'`, 하수인 kind `abm`, 추종하는 눈 = ebul k `abeye`). 둘 다 챌린지 전용.
- **쿠폰:** 설정에서 `ai소프트웨어학과` 입력 → 문어 마법사 최종 스킨 (접속마다 재입력).

## 티어 측정 방법
- (v6.30) sim600은 이제 단계 인자가 실제로 적용된다 — 예전엔 해금(`SAVE.diff.max`)·영혼 조각이 없어 startGame이 항상 0단계로 낮췄다(v6.22까지의 '5단계' 측정도 실제로는 0단계였을 수 있음). 옵션 ANJ(타락천사 조절값 JSON) · NOEX(난이도 추가 패턴 끔) · TANK(죽지 않게 체력만 크게, 받은 피해를 그대로 잰다) · BIGHP.
- `tools/sim600.py` 의 `VAR` 표에 변형 키(예 `'snail:bomb':('snail','bomb','')`)가 있어야 한다.
- `tools/tier_run.sh "<키>" <이름>` (약 30분) → `python3 tools/tier_an.py build/tier/<이름>_boss.txt build/tier/<이름>_field.txt "최종 이름" "1진화 이름"`
- 점수 = 보스 평균 깎은 체력 75% + Lv.24 필드 처치 25%, 기존 1등 = 100. S≥92 · A≥80 · B≥64 · C≥56 · D.
- 보고서: 보스별(원숭이/마안/스켈레톤/혈랑왕) 깎은 체력·승리·평균 대비 상성 + s2/s1 JSON → PDF.

## 참고 자료
- **변경 이력은 `docs/CHANGELOG.md`** (전체를 읽지 말고 grep). 매 버전 거기에 항목을 추가한다.
- **코드 위치 지도 `docs/MAP.md`** — 작업 전에 이것부터 보고 `grep -n`으로 필요한 부분만 읽는다. 새 기능을 만들면 `tools/mkmap.py`의 ANCHORS에 한 줄 추가하고, 빌드 때마다 `python3 tools/mkmap.py`를 돌린다.
- 패턴 기획서: `docs/hell survive 보스 패턴 추가 기획서.pdf` (하데스·엘든링·세키로·건전·메이플 110개 표본, 신규 패턴 15개 안, 구현 전 — E4 안식처는 규칙 9 경계 사례라 허락 필요). 생성 스크립트 `tools/pattern_plan.py·pattern_data.py·pattern_html.py`
- 밸런스 시뮬: `python3 tools/bal_make.py` → `tools/sim_bal.py` → `tools/bal_an.py` → `tools/bal_report.py`
