# 티어 신뢰도 측정 – 원본 로그 수집 REPORT

## 버전
- 게임: v6.01 (game_ver "6.01"), 게임 커밋 `14fdb3a` (측정 중 게임 파일 변경 없음)
- 봇/하네스: `tools/tier2.py`, bot_ver `20a318d3` (sim600 봇 + 표준 빌드 정책 선택기)
- 측정 날짜: 2026-10-20 ~ 2026-10-21 (Asia/Seoul)
- 병렬 수: 보통 PAR=3 (D·A재실행은 3/2), 헤드리스 Chromium

## 재현성 테스트
- sim600 원봇: wolf:crimson 3시드 두 번 돌려 결과 동일 (repro1.txt = repro2.txt).
- 새 하네스(wolf:crimson × 원숭이, 시드 1~5): **병렬 3 vs 병렬 1 결과 5판 모두 동일** (처치 시각·깎은 체력·카드 구성).
- 처음에는 시드 1·2·5가 달랐다. 원인: 메뉴 화면 프레임이 `Math.random`을 소모해서 판 시작 시점의 난수 위치가 부하에 따라 달라짐. 해결: 판 평가 코드 맨 앞에서 난수 상태를 시드로 다시 맞춤. 고치기 전에 돌린 파일럿 128판은 `pilot_prefix_nondeterministic.jsonl`로 따로 남기고 **본 측정에는 쓰지 않음**.

## 실제로 돌린 판 수
| 실험 | 계획 | 실제 | 비고 |
|---|---|---|---|
| A 보스전 | 1,600 | 1600 | 20종×4보스×시드1~20, 최대 420초, 전부 기록 |
| B 필드 | 528 | 528 | 44형태×12시드 (Lv.8/15/24 구간 90초) |
| E 성장 | 200 | 200 | 20경로×10시드, Lv.1 시작, Lv.24/사망/1200초에 종료 |
| D 무작위 카드 | 288 | 288 | policy="random", 12종×4보스×6시드 |
| 파일럿 | 128 | A의 시드 1~8로 재사용 | 재현성 수정 전 파일럿은 폐기(위 참고) |
| 적응형 추가 | – | 0 | 점수·구간 계산을 하지 않아 이번에는 안 돌림 (batch=1만 존재) |
| F, G (P2) | – | 0 | 선택 항목이라 이번에는 생략 |

D 대상 12종: 하위 4(snail:venom, chimera:flame, wolf:fallen, archer:skel) + 상위 4(twins, lizard:guard, wolf:holy, lizard:water) + 최근 추가형 4(snail:bomb, octo, ghost, chimera:dream). 하위·상위는 A 요약의 보스 평균 깎은 체력 기준.

## 소요 시간
- 보스전 1판 실제 처리량: PAR=3에서 분당 약 11판 (판당 약 16초/워커). 필드(B) 판당 약 10~25초, 성장(E) 판당 약 20~60초.
- 주의: raw_boss.jsonl의 `sim_seconds`는 병렬 대기시간이 섞여 **부정확**(세마포어 대기 포함). B·E의 `sim_seconds`는 정확. 게임 내 시간은 `end_time`을 볼 것.

## A 요약 수치
- 종료 사유: 보스 처치 776 / 플레이어 사망 811 / 제한시간(420초) 초과 13 (0.8%)
- 판당 깎은 체력% 표준편차: 변형×보스 80칸 평균 10.2%p (최소 0.0, 최대 27.3)
- 목표 시너지 열림 비율(전체 63%, 파일럿 8시드 구간 77%): archer:holy 80%, archer:red 72%, archer:skel 69%, chimera 18%, chimera:dream 16%, chimera:flame 16%, ghost 69%, lizard:guard 56%, lizard:rage 59%, lizard:water 62%, octo 76%, snail:bomb 74%, snail:lava 75%, snail:venom 79%, twins 66%, wolf:abyss 72%, wolf:crimson 100%, wolf:fallen 71%, wolf:holy 69%, wolf:twin 61%
  - **정정:** 이전 초안은 '파일럿 통과로 유지'라고 적었는데 잘못된 기준이었다. 규칙은 파일럿에서 70% 미만이면 고치라는 것이고, 파일럿(4변형) 77%는 통과였지만 본 측정 전체는 63%로 70% 미만이다. 특히 키메라 3종 등 아래 변형은 기준 미달이다. 측정 중 정책을 바꾸지 않는 것이 규정이라 그대로 두었고, 결과 해석 시 `target_synergy_opened`로 나눠 봐야 한다.
- **주의: 키메라 3종(chimera, chimera:flame, chimera:dream)은 목표 시너지 열림이 16~18%뿐이다.** 원인은 재료 카드 두 장이 Lv.3까지 못 오르는 것이다(세 변형 모두 두 재료가 동시에 Lv.3인 판이 20% 안팎, 중앙값 Lv.2). 원인으로 보이는 것: 서로 다른 증강은 10개(`AUG_CAP`)까지만 고를 수 있고, 10개가 차면 가진 카드만 나온다. 키메라는 판의 절반(80판 중 47판)에서 10개가 차는데, 그 전에 재료 카드를 얻지 못한 판에서는 재료가 아예 안 나온다. 보조 카드(발톱·방어·이동 등)가 슬롯을 먼저 채우는 것도 영향을 준다. (추정이며 3판 확인 실험으로만 뒷받침됨 — 레벨업 기록이 판당 5~14회로 적게 잡혀 확정은 아님.) 따라서 키메라 결과는 '목표 시너지 없는 빌드' 값으로 해석하고, 정책 수정 후 재측정이 필요하다.
- 시너지 획득 시각(`synergy_obtained`)은 보스전 준비를 즉시 레벨업으로 하기 때문에 게임 시간이 0에 가깝다. 의미 있는 값은 `synergy_level`(획득한 레벨).

## 값이 비어 있는 항목과 이유
- `boss_hp_pct_at`: 보스가 죽었거나 플레이어가 먼저 죽은 시각 이후 칸은 null (처치했으면 0.0).
- `player_death_time`: 사망하지 않은 판은 null. 필드 `death_time`도 동일.
- `dmg_by_source`: 딜 미터기(DMETER)에 태그된 효과만 집계 — 태그 없는 카드 효과·반사 피해는 빠질 수 있음.
- B의 `near_death_*`: 체력 15% 미만으로 내려간 횟수/첫 시각 (사망과 별개). E의 `t_lv*`: 도달 못 하면 null.
- `hp_pct_by_10s`/`dmg_taken_by_10s`: 판이 10초보다 빨리 끝나면 짧은 배열.

## 이상한 점
- **게임 버그 발견**: lizard:guard × 원숭이 마왕 시드 11, 19에서 보스가 도약 착지 직전에 죽으면 `bossLand → bossTele`(game_template.html 약 1075·1161행)에서 `boss`가 null이라 `TypeError: reading 'tele'` 가 난다. 하네스가 이 오류를 잡아 `game_error` 필드에 기록하고 판을 이어갔다(둘 다 보스 처치로 기록). 게임은 수정하지 않았다.
- 같은 이유로 처음 A를 돌릴 때 4판이 중단(lizard:guard monkey 11·19·fw 17, lizard:water monkey 20) → 널 가드(봇 `esc`)와 try/catch를 넣어 재실행. 이 4판 외 판은 영향 없음(해당 패치는 오류가 나는 경우에만 작동).
- bot_ver 해시는 위 패치 전 기준으로 고정하여 모든 행이 같은 값이다.
- 제한시간 초과 13판(0.8%): 보스 생존 + 플레이어 생존.
  - 변형별: lizard:water 12, chimera:flame 1
- 필드(B) 사망률: Lv.8 0%, Lv.15 2%, Lv.24 1%
- 성장(E)은 사망 종료가 65%(131/200)로 많음: Lv.1부터 시작하는 필드 봇이 Lv.24 전에 죽는 경우다. `death_level`·`death_time`으로 분석 가능.
- 성장(E) 종료 사유: dead 131, lv24 69
- 시드 간 편차가 큰 곳(깎은 체력 SD 상위 5): lizard:rage/fw 27, wolf:holy/fw 26, lizard:rage/monkey 23, lizard:water/fw 21, wolf:fallen/skel 21 (%p)
- wolf:fallen은 sim600 `VAR`에 없어 하네스에 직접 정의(혈랑→fallen, 혈랑왕 해금 상태로 측정). 숨은 보스(fw)는 제단 맵에서 따로 진행.

## 게임 파일 수정
- 없음. 기존 `window.__G` 훅만 사용했고, 해금 플래그(`SAVE.fw.open/cleared`)와 난수 시드는 페이지 쪽에서 주입. `src/`는 v6.01(커밋 14fdb3a) 그대로.

## 파일
- 원본 로그: raw_boss.jsonl(A·D), raw_field.jsonl(B), raw_growth.jsonl(E)
- 요약(검산용): summary_boss.csv, summary_field.csv, summary_growth.csv — 점수·티어는 계산하지 않음
- targets.json, build_defs.json, pilot_prefix_nondeterministic.jsonl(폐기 파일럿, 참고용)
- 재현 코드: tools/tier2.py, tools/tier2_sum.py
