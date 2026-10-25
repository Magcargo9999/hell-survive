# 인수인계서 — 지옥의 생존자 (hell survive) v9.23 기준

작성: 2026-10-25 · 마지막 배포 **v9.23** (커밋 386c196, origin/main 푸시 완료) → 다음은 **v9.24**.
저장소: GitHub `Magcargo9999/hell-survive` · 사용자 편규빈 · **답변은 한국어로 짧고 간결하게.**
새 환경에서는 **먼저 `CLAUDE.md`를 끝까지 읽을 것**(규칙 ①~⑮·게임 구조·절차가 전부 있음). 이 문서는 그 위에 "최근 작업 + 바로 이어갈 정보"만 정리한 것.

## 1. 새 환경 시작 순서
```bash
git clone https://github.com/Magcargo9999/hell-survive && cd hell-survive   # 또는 기존 폴더 git pull
pip install playwright --break-system-packages    # 없으면
python3 tools/check.py && python3 src/build.py    # 빌드가 되는지 확인 (build/hell_survive.html 약 100MB)
```
- 이어서 할 기능은 `docs/MAP.md`에서 위치를 찾고 `grep -n`으로 필요한 부분만 읽는다. 변경 이력은 `docs/CHANGELOG.md`(grep).
- 템플릿 수정은 python 문자열 치환(정확히 1회 일치 assert). 주석을 줄 중간에 넣지 말 것(뒤 코드가 주석 처리됨).
- 테스트는 `PYTHONPATH=tools python3 tools/tests/<이름>.py`, 헬퍼 `tools/h301.py`(`__G`, `__lv`, `__s`, `newpage`).

## 2. 지켜야 할 규칙 요약 (전문은 CLAUDE.md)
1. 파일명 `hell survive v.N.NN.html`, 매 빌드 버전 +1. 끝자리 = 작은 수정, 가운데 = 캐릭터·보스 추가급.
2. **도트는 절대 수정·재색칠 금지** (자르기·배경 제거·마스크·배율만).
3. 매 버전 **커밋+푸시**. 작성자 `-c user.name="Magcargo9999" -c user.email="gyubinpyeon@gmail.com"`, 커밋 끝에 트레일러(이 환경 기준):
   `Co-Authored-By: Claude … <noreply@anthropic.com>` / `Claude-Session: <세션 URL>` (새 환경이 지시하는 형식을 따를 것).
4. 규칙 9: 화면·보스방 전체를 덮어 안전 구역이 없는 패턴 금지(최고 5단계에서도 안전 구역 확인).
5. 규칙 10: 화면에 적힌 설명·수치는 구현을 따라간다. 고칠 때마다 grep으로 옛 문구 확인 + 보고.
6. 규칙 11: 딜 미터기 이름 = 화면 이름(`skillName()`/`upName()`/`altOf()`), `tools/tests/dmeter22.py`.
7. 규칙 15: 새 캐릭터·보스·미니·마물은 도감(`openDex`)에 등록, 열린 창에서 Enter/Space 시작 막기.
8. 규칙 12: 검색 노출 태그·robots·sitemap 금지. 규칙 14: 미니 보스 자가복제 금지. 규칙 5: 1진화 스킬 금지(예외 있음).
9. 배포 때마다 `ls -l index.html` 크기 보고, 단일 파일(`build/hell_survive.html`, 약 100MB)은 GitHub에 올리지 않음(.gitignore). 사용자에게는 `hell survive v.N.NN.html`을 파일로 전달.
10. 버전마다 해야 할 문서 작업: 템플릿 `GAME_VER` + `PATCH` 목록 맨 앞에 항목, `docs/CHANGELOG.md` 한 줄, `CLAUDE.md`의 "마지막 배포 → 다음" 숫자와 해당 블록 메모, `tools/mkmap.py` ANCHORS + `python3 tools/mkmap.py`.
11. 도트 받으면: `tools/atlas/<이름>_build.py` 작성 → `src/assets/<폴더>/*.webp+json` → `src/build.py` 토큰 표 → 템플릿 `SRC`·`LAZY_IMG`·JSON 상수. 반드시 미리보기 PNG를 눈으로 보고(라벨 줄·테두리 잔여물 확인) 테스트 스크린샷으로 확인.
12. 사용자 지시 반복: "더 필요한 도트가 있으면 적용한 뒤에 다시 말해줘" — 적용 후 남은 필요 도트를 마지막에 보고.

## 3. 이번 구간에 한 일 (v9.21 ~ v9.23)
| 버전 | 내용 | 핵심 위치 |
|---|---|---|
| v9.21 | 마하칼 루드라 **이펙트 도트**: 염주·폭발·가시/기둥·룬·최종 형태·사망 | 아틀라스 `IMG.rudfx`/`RDX`, `tools/atlas/rudfx_build.py`, `rdFx()`. `ring` 4칸 미사용 |
| v9.22 | 릴세르카 **캐릭터 도트**: idle·move·atk·cast·hit·death·mirror | `IMG.lil`/`LILF`, `tools/atlas/lil_build.py`, `lilSpr`, `drawLilBody`, `drawLilBoss`, `FrostMirror.draw`, `lilDexArt`. hit 줄·거울 피격 칸 미사용 |
| v9.23 | 릴세르카 **이펙트 도트**: 샹들리에·바늘·반사탄·스포트라이트·시선(눈·광선·가시)·결정화 영역 바닥·무도회 마법진·화이트아웃 금 | `IMG.lfx`/`LFX`, `tools/atlas/lilfx_build.py`, 헬퍼 `lfx(key,i,x,y,k,alpha,rot,add,ky)`, `lfxK`, `LSW.gz`/`cfx`/`mirfx`, 테스트 `tools/tests/lilfx923.py` |

v9.23 상세:
- 안 쓴 그룹: `nstar`·`rstar`(바늘·반사탄 터지는 별), `bliz`(무도회 눈보라 테두리), `bpat` 3번 외 프레임 — 필요하면 `drawLilTop`/`drawLilFloor`에 붙이면 됨.
- 화이트아웃 금(`drawLilScreen`): 크랙 프레임이 어두운 배경 + 밝은 금이라 `globalCompositeOperation='difference'` + `ctx.filter='grayscale(1) contrast(1.3)'`로 흰 화면 위에 검은 금으로 보이게 함(처음엔 노랗게 번졌음).
- 눈으로 직접 확인한 것: 결정화 영역, 샹들리에 낙하·충돌, 시선, 스포트라이트, 금. **바늘·반사탄·무도회 바닥은 스크린샷으로 따로 확인하지 못함**(콘솔 오류 없음만 확인) — 다음 작업 때 한 번 보면 좋음.
- v9.23은 `smoke.py`(진화 15개)를 돌리지 않았다. 다음 배포 전에 `timeout 900 python3 tools/smoke.py | grep -c "\[\]$"` = 15 확인 권장.
- 회귀 확인: `lil920.py`(A/Z/W/M/B/X, errs []), `dex824.py`, v9.21의 `rud910.py`.

## 4. 알아둘 함정(이번에 겪은 것)
- 시트 라벨·밑줄·패널 선이 프레임에 섞임 → 박스 좌표(y0/y1)를 조정하거나 패널 제거. 스프라이트 시트는 칸 경계를 머리 위치 등으로 직접 지정.
- `lil_build.py`: 한 줄 끝 `# 주석; Lf = []`가 코드까지 주석 처리해 개수가 틀어짐 → 주석은 코드 뒤에.
- 릴세르카 도트 방향: idle·cast·atk는 오른쪽, **move 줄은 왼쪽**(`drawLilBody`가 뒤집음). 보스는 ×3 nearest(`LS_K`=3), 효과는 부드러운 알파(`lighter` 가산).
- 스크린샷 테스트: 보스가 화면 밖일 수 있음 → 약 330틱을 먼저 돌려 배너를 지우고, 스프라이트 확인은 오프스크린 캔버스(`build/lil_sheet.py`)로. 보스 전투를 강제 상태로 만들 때는 `G.ls.waltzStart()`, `G.ls.ballStart()`, `G.LSW.chand/bolts/gz/crack/white/frost`를 직접 채움.

## 5. 이어서 할 수 있는 일(대기 중·선택)
- 릴세르카 hit 줄·거울 피격 칸 적용, `nstar`·`rstar`·`bliz` 적용(원하면).
- 바늘·반사탄·무도회 바닥 시각 확인, smoke 15/15 확인.
- 마하칼 루드라 `ring` 4칸 미사용 정리 여부.
- 사용자가 새로 요청하는 캐릭터·보스·밸런스 작업 (티어 결과는 규칙 7: 보스별 상성 + s2/s1 JSON PDF).
- 5지옥 팔한지옥(지하 21~25층) 완성(`OPEN_TIER`=`TOP_TIER`=24). 6지옥을 만들면 `TOP_TIER`·`HELL_SET`도 늘리고, 이전 기록 인정 한 줄(`loadSave`)을 같이 넣는다.

## 6. 세이브·배포 주의
- 세이브 키 `hellSurvivorSave1`은 절대 바꾸지 말 것(진행 소실). 새 환경에서 사용자가 쓰던 세이브는 설정의 [파일로 저장]/[코드 복사]로 옮긴다.
- 분리 배포: `python3 src/build.py --split` → `index.html`(약 1.3MB) + `src/assets/`. 로컬 테스트는 `GAME_URL=http://localhost:포트/index.html` + `python3 -m http.server`. 저장소 `.git`이 이미 1GB를 넘은 상태.
