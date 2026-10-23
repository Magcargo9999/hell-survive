"""코드 지도 생성: src/game_template.html 에서 주요 기능의 위치(줄 번호)를 찾아 docs/MAP.md 를 쓴다.
사용: python3 tools/mkmap.py   (빌드할 때마다 돌리면 줄 번호가 최신으로 유지된다)
새 기능을 만들면 아래 ANCHORS 에 (이름, 정규식) 한 줄만 추가."""
import re, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'src', 'game_template.html')
ANCHORS = [
 ('● 데이터·설정', None),
 ('캐릭터 목록(소개·역할·약점)', r'^const CHARS = '),
 ('스킬 목록(이름·설명)', r'^const SKILLS = '), ('스킬 쿨타임·스킬 이름 함수', r'^const SKILL_CD|^const skillName'),
 ('공용 카드', r'^const UPGRADES = '), ('캐릭터 전용 카드', r'^const UNIQUE = '), ('조합 카드', r'^const SYNERGIES = '),
 ('강화 상점', r'^const PERKS = '), ('진화 루트 데이터', r'^const ROUTE_FORMS|^const CHIM_ROUTES|^const GUN_FORMS'),
 ('진화 스탯 적용', r'^function applyEvo'), ('진화 조건(ROUTE_COND)', r'^const ROUTE_COND'),
 ('● 플레이어·전투', None),
 ('플레이어 생성(기본 스탯)', r'^function newPlayer'), ('게임 시작', r'^function startGame'), ('메인 틱', r'^function tick'),
 ('피해 처리(적/플레이어)', r'^function hurtEnemy|^function hurtPlayer'), ('딜 미터기 이름', r'^const dmName'),
 ('적 생성·체력 배율', r'^function spawnEnemy'), ('정예 구슬', r'^function updateEliteShots'),
 ('사슬 악마(회전·길이)', r'^const twLen|^function updateTwins'), ('사슬 휘두르기', r'^function whipHit|^function updateWhip'),
 ('악마 총잡이 탄·재장전', r'^const GUN_AMMO|^function gunShot|^function gunReload'),
 ('● 보스·미니보스', None),
 ('보스 등장 확률', r'^function pickBossK|^const BOSS_TBL'), ('미니보스 생성', r'^function spawnMini|^function spawnCut|^function spawnHorse|^function spawnMiniPick'),
 ('미니보스 갱신·그리기', r'^function updateMini|^function drawMini\b|^function updateHorse|^function drawHorse\b'),
 ('유니크 몹', r'^const UNIQ = '), ('스켈레톤 첨탑 결계', r'skSpawnPair|function skpPts'), ('타락천사', r'^const AN = |v6\.30 타락천사'),
 ('거대 버섯마귀', r'v7\.20 거대 버섯마귀|^function updateShkBoss|^function shkStart|^function shkSummon'),
 ('악마 식물원(16~20층)', r'v8\.30 지하 16~20층|^const GMAP|^function gardTile|^const isGard'),
 ('이독버섯 마왕', r'v8\.20 이독버섯 마왕|^function updateToxBoss|^function toxPick|^const DEBUFF'),
 ('● 층·맵', None),
 ('층 세트(지옥/버섯/어인섬)', r'^function floorSet|^const isSea|^const isMush'), ('버섯 세트', r'^const MSPECIES|^const MMAP'), ('어인섬 세트', r'^const SSPECIES|^const SMAP|^function warmSea'),
 ('챌린지 모드', r'v6\.20 ∞ 챌린지|^function startChallenge'),
 ('● 화면·UI', None),
 ('카드 선택 창', r'^function openChoice|^function openUpgrade|^function cardView'), ('HUD', r'^function drawHud'),
 ('부패한 성상(타락천사 판 미니 보스)', r'v8\.06 부패한 성상|^function spawnStat|^function sAtk|^function updateStat|^function drawStat'),
 ('보스 심장', r'v8\.01 보스 심장|^function rerollHeart|^function equipHeart|^function playUpgradeEffect|^function heartBonus'),
 ('스킨 가챠·도감', r'v7\.30 스킨 가챠|^function gachaRoll|^function renderGacha|^function skinOn|^const SKINS'),
 ('설정·쿠폰', r'ai소프트웨어학과'), ('난이도 안내문', r'diffDesc'), ('세이브(키 변경 금지)', r'hellSurvivorSave1'),
 ('이미지 목록(SRC/LAZY_IMG)', r'^const SRC = |^const LAZY_IMG'), ('테스트용 __G 노출', r'^window\.__G'),
]
lines = open(SRC, encoding='utf-8').read().split('\n')
out = ['# 코드 지도 (자동 생성: `python3 tools/mkmap.py`)', '', '`src/game_template.html` 안의 위치. 줄 번호는 생성 시점 기준이라 `grep -n "이름"`으로 다시 확인할 것.', '']
for name, pat in ANCHORS:
    if pat is None: out += ['', f'## {name}', '']; continue
    rx = re.compile(pat); hits = [i + 1 for i, l in enumerate(lines) if rx.search(l)]
    out.append(f'- {name}: ' + (', '.join(f'L{h}' for h in hits[:6]) if hits else '❓ 못 찾음 (이름이 바뀌었으면 ANCHORS 수정)'))
open(os.path.join(ROOT, 'docs', 'MAP.md'), 'w', encoding='utf-8').write('\n'.join(out) + '\n')
print('docs/MAP.md', len(out), '줄')
