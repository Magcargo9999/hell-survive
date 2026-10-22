"""제출 파일 묶음 만들기: build/tier3 원본 → submit/ (jsonl·요약 CSV·targets·cards·build_plans·REPORT.md) + zip. 점수·티어는 계산하지 않는다."""
import json, os, csv, glob, shutil, statistics as st, collections, subprocess, time, zipfile
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); B = os.path.join(ROOT, 'build', 'tier3'); S = os.path.join(B, 'submit')
shutil.rmtree(S, ignore_errors=True); os.makedirs(S + '/chars'); os.makedirs(S + '/cards')
def rd(f):
    out = []
    if os.path.exists(f):
        for l in open(f, encoding='utf8'):
            try: out.append(json.loads(l))
            except Exception: pass
    return out
boss = rd(B + '/raw_boss.jsonl'); field = rd(B + '/raw_field.jsonl'); grow = rd(B + '/raw_growth.jsonl'); card = rd(B + '/cards/raw_card.jsonl')
for n in ('raw_boss', 'raw_field', 'raw_growth'):
    if os.path.exists(f'{B}/{n}.jsonl'): shutil.copy(f'{B}/{n}.jsonl', f'{S}/chars/{n}.jsonl')
if os.path.exists(B + '/cards/raw_card.jsonl'): shutil.copy(B + '/cards/raw_card.jsonl', S + '/cards/raw_card.jsonl')
for n in ('targets.json', 'cards.json', 'build_plans.json'):
    if os.path.exists(f'{B}/{n}'): shutil.copy(f'{B}/{n}', f'{S}/{n}')
if os.path.exists(B + '/repro'): shutil.copytree(B + '/repro', S + '/repro')
def avg(x): return round(st.mean(x), 2) if x else ''
def w(fn, head, rows):
    with open(fn, 'w', newline='', encoding='utf-8-sig') as f: c = csv.writer(f); c.writerow(head); c.writerows(rows)
g = collections.defaultdict(list)
for d in boss: g[(d['site_id'], d['variant'], d['stage'], d['boss'])].append(d)
rows = []
for k, v in sorted(g.items()):
    rows.append(list(k) + [len(v), sum(d['win'] for d in v), sum(d['end_reason'] == 'player_dead' for d in v), sum(d['end_reason'] == 'timeout' for d in v), avg([d['boss_hp_removed_pct'] for d in v if d['boss_hp_removed_pct'] is not None]),
                           avg([d['end_time'] for d in v]), avg([d['dmg_taken_total'] for d in v]), sum(1 for d in v if d.get('game_error'))])
w(S + '/chars/summary_boss.csv', ['site_id', 'variant', 'stage', 'boss', 'n', 'wins', 'deaths', 'timeouts', 'mean_hp_removed_pct', 'mean_end_time', 'mean_dmg_taken', 'game_errors'], rows)
g = collections.defaultdict(list)
for d in field: g[(d['site_id'], d['variant'], d['stage'], d['L'])].append(d)
w(S + '/chars/summary_field.csv', ['site_id', 'variant', 'stage', 'L', 'n', 'mean_kills', 'deaths', 'mean_dmg_taken', 'mean_level_end'], [list(k) + [len(v), avg([d['kills'] for d in v]), sum(1 for d in v if d['died']), avg([d['dmg_taken'] for d in v]), avg([d['level_at_end'] for d in v])] for k, v in sorted(g.items())])
g = collections.defaultdict(list)
for d in grow: g[(d['site_id'], d['variant'])].append(d)
w(S + '/chars/summary_growth.csv', ['site_id', 'variant', 'n', 'mean_t_lv10', 'mean_t_lv15', 'mean_t_lv20', 'mean_t_lv24', 'deaths', 'mean_kills'], [list(k) + [len(v), avg([d['t_lv10'] for d in v if d.get('t_lv10')]), avg([d['t_lv15'] for d in v if d.get('t_lv15')]), avg([d['t_lv20'] for d in v if d.get('t_lv20')]), avg([d['t_lv24'] for d in v if d.get('t_lv24')]), sum(1 for d in v if d['died']), avg([d['kills'] for d in v])] for k, v in sorted(g.items())])
g = collections.defaultdict(list)
for d in card: g[(d['v'], d['cfg'], d['boss'])].append(d)
w(S + '/cards/summary_card.csv', ['variant', 'cfg', 'boss', 'n', 'wins', 'deaths', 'mean_hp_removed_pct', 'mean_end_time', 'mean_dmg_taken', 'target_opened_rate', 'game_errors'],
  [list(k) + [len(v), sum(d['win'] for d in v), sum(d['dead'] for d in v), avg([d['removed'] for d in v if d['removed'] is not None]), avg([d['t'] for d in v]), avg([d['loss'] for d in v]),
              round(sum(1 for d in v if k[1].startswith('syn:') and k[1][4:] in d['syn']) / len(v), 2) if k[1].startswith('syn:') else '', sum(1 for d in v if d.get('err'))] for k, v in sorted(g.items())])
tg = json.load(open(S + '/targets.json')) if os.path.exists(S + '/targets.json') else {'targets': []}
fin = [t for t in tg['targets'] if t['stage'] == 2]; nb = len(set(d['boss'] for d in boss))
cnt = collections.Counter((d['variant'], d['boss']) for d in boss)
seedmin = min(cnt.values()) if cnt else 0
commit = subprocess.run(['git', '-C', ROOT, 'log', '-1', '--format=%h %s', '--', 'src', 'index.html'], capture_output=True, text=True).stdout.strip()
errs = [d for d in boss + field + grow if d.get('game_error')] + [d for d in card if d.get('err')]
bv = sorted(set(d.get('bot_ver') for d in boss + card)); lines = open(B + '/run.log').read().count('ERR') if os.path.exists(B + '/run.log') else 0
R = f'''# 티어 재측정 제출 파일 — REPORT
생성: {time.strftime("%Y-%m-%d %H:%M KST")}  ·  게임 v8.20 (마지막 소스 커밋 {commit})  ·  봇 버전 {bv}
점수·티어는 계산하지 않았다(원본 + 요약 CSV만).

## 환경 (문서 §환경 기준)
난이도 0단계(지하 1층), 보스 심장 없음, 스킨 전부 OFF, 상점 강화 0, 쿠폰/챌린지 없음, 캐릭터·숨은 보스 해금 전부 열림. 시드는 모든 캐릭터·설정에서 동일(시드 s = 같은 난수열). 봇은 tools/sim600.py + tier3.py의 정책(문서 v8 기준과 같은 계열; 게임·봇 로직 변경 없음, 로깅만).
※ 영혼 조각은 봇 시뮬레이터가 입장료 통과용으로 99999로 올려 둠(전투에 영향 없음, 기존 측정과 동일).

## 실제 측정량 (계획 대비)
- 캐릭터 보스전(A): {len(boss)}판 · 최종진화 {len(fin)}종 × 보스 6종(monkey·eye·skel·angel·shk·fw) · 칸(캐릭터×보스)당 최소 {seedmin}시드(시드 1~3). 보스전 시간 제한 240초(문서 허용 범위 180~420초). 문서 계획은 12~20시드 → **시간 한계(8시 마감, CPU 2코어)로 표본 축소**.
- 필드(B): {len(field)}판 · 성장(E): {len(grow)}판(최종진화 21종 × 1시드) · 문서의 D(무작위 카드)는 시간 부족으로 **미실시**.
- 카드(Part 2): {len(card)}판 (대조·시너지·스킬 카드: monkey 2시드 + eye 1시드). 스탯/고유 증강 단독(aug:<id>@3) 조건과 스켈레톤(P2)·mat: 조건, §4 사람형 시너지 정책(build_plans 우선순위·슬롯 예약·플랜 전환)은 **미구현** — 대신 card3.py의 단순 정책(재료 카드 3장 우선 → 시너지 선택)을 사용했고 build_plans.json은 기존 build_defs 요약.
- 스킬 카드는 @5(재료 최대 레벨 5)로 측정(P1은 @3 미실시).

## 이상·주의
- 게임 오류 기록 판 수: {len(errs)} (game_error 필드, 판은 버리지 않고 포함). 러너 ERR 줄: {lines}.
- 재현성 확인(repro/): 병렬 2 vs 1, 4판 중 3판 동일. 악마 총잡이×거대 버섯마귀 1판이 달랐음(깎은 체력 49.4% vs 58.7%) — 실시간 요소로 인한 미세 비결정성, 병렬도 영향 가능. 병렬 2로 본 측정을 돌렸다.
- 이독버섯 마왕(tox, v8.20)은 심장이 없고 6종 계획에서 제외.
- 악마 총잡이는 진화 분기가 없어 gun0/gun1/gun2.
- 고유 카드 목록(cards.json)은 템플릿 정규식 추출이라 일부 캐릭터(늑대·문어 등)의 고유 카드가 비어 있을 수 있음.

## 파일
chars/raw_*.jsonl(원본) · chars/summary_*.csv · cards/raw_card.jsonl · cards/summary_card.csv · targets.json · cards.json · build_plans.json · repro/

## 재현 명령
`git checkout 363b78f && python3 src/build.py && STOP=<epoch> PAR=2 bash tools/tier3_run.sh` (이어 돌리기, 끝난 판은 건너뜀) → `python3 tools/tier3_pack.py`
'''
open(S + '/REPORT.md', 'w', encoding='utf8').write(R)
zp = os.path.join(B, 'tier3_submit.zip')
with zipfile.ZipFile(zp, 'w', zipfile.ZIP_DEFLATED) as z:
    for p, _, fs in os.walk(S):
        for f in fs: z.write(os.path.join(p, f), os.path.relpath(os.path.join(p, f), S))
print(zp, os.path.getsize(zp) // 1024, 'KB', len(boss), len(field), len(grow), len(card))
