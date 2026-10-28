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
 ('마계 물고기 진화(v9.49: 미꾸라지 물방울·마해룡 절대 수압·포식자의 파도)', r'^const FISH_AURA|^const FWAVE|^function updateFish|^function fishOrb|^function startFishWave|^function stepFishWave|^function drawFishWave|^function drawFishAura'),
 ('검 도깨비 마왕(v9.85: 쾌검 돌진·귀신의 흘리기·검총의 결계·무형검)', r'^const DOK = |^class DokkaebiAI|^function dokGuardHit|^function updateDokBoss|^function drawDokBoss|^function dokDefeated'),
 ('시체고래(v9.80: 해류·뼈·몸통박치기·소용돌이·잠수·죽음의 파도)', r'^const WH = |^class WhaleAI|^function whRoom|^function whLane|^function updateWhBoss|^function drawWhBoss|^function whDefeated'),
 ('화염 호랑이(v9.63: 불의 십자가·완벽 회피 기절·가드 반격·연속 돌진·멸옥 수플렉스·포식자의 추적)', r'^const TG = |^function tgCrossUpdate|^function tgPatEnd|^function tgGuardHit|^function tgSafeSpot|^function tgRwPlan|^class TigerAI|^function updateTgFx|^function tgPushP|^function drawTgFloor|^function drawTgBoss'),
 ('불구렁이(v9.46: 다관절 마디·파열하는 대지·탐욕의 용광로·환영 포위·종말의 똬리)', r'^const SN = |^class SnakeNode|^function snPath|^function snEscapeR|^function snCrackPush|^function snSuckOrb|^class SerpentAI|^function updateSnFx|^function drawSnFloor'),
 ('영벌의 화염죄수(v9.40: 불길 궤적·쇠사슬 도넛·용광로 구슬·속죄 반사·족쇄 해방 돌진)', r'^const CV = |^class HellfirePatch|^function cvChainStep|^function cvTetherStep|^function cvFurnace|^function cvAtone|^class ConvictAI|^function updateCvFx'),
 ('팔한지옥의 대공작 릴세르카(v9.20: 결정화 영역·왈츠·거울·무도회)', r'^const LS = |^class FrostMirror|^class LilserkaAI|^function lsZone|^function updateLilFx'),
 ('마하칼 루드라(v9.10: 업보 염주·침묵 진언·만트라·청련·8자 해탈)', r'^const RD = |^class KarmaBead|^function rdPull|^class FrostMantra|^class IceLotus|^class RudraAI|^function updateRudFx'),
 ('황금 악마 임프(v9.03: 21층~ 돌진·도망·10000조각)', r'^const IMP = |^class GoldImp|^function trySpawnImp|^function impDefeated'),
 ('팔한지옥의 백곰 마왕(v9.02: 빙결 투기장·장벽·눈보라·균열·핀볼)', r'^const PB = |^const IMAP = |^class IceWall|^const FrostMgr|^class Fissure|^class PolarBearAI|^function updateBearFx'),
 ('보스방 열기(v9.72: 팔열지옥 26~29층 보스방 휴식존 4곳)', r'^const HEAT_ARENA_MAX|^function updateHeat|^function arenaRests'),
 ('진화 루트 그림 스킬 보기(v9.72: DEX_SKILL · 형태를 누르면 스킬 설명)', r'^const DEX_SKILL|^function routeSkillShow|^function openRoutePic'),
 ('7지옥 도산과 업경의 심판정(v9.71: 지하 31~35층 필드, 잠김 — 바닥·칼날 지대 출혈·잡몹 8종)', r'^const DF = |^function dosanTile|^const BLADE = |^function updateBlade|^function buildDosanSpecies|^const SET_IMGS'),
 ('팔열지옥 세트·열기·휴식존(v9.24: 지하 26~30층, 잠김)', r'^const FF = |^function fireTile|^const HEAT = |^function updateHeat|^function drawRestZones|^function drawHeatHud'),
 ('팔한지옥 세트(v8.99: 바닥·소품·미끄러운 얼음·잡몹)', r'^const IF = |^function iceTile|^function isIceSlip|^function buildIceSpecies|^const OPEN_TIER'),
 ('유령 기사·듀라한 폼(v8.98)', r'^const KNIGHT_FORMS'), ('유령 기사·잃어버린 머리 로직', r'^class SeveredHeadSummon|^function knightSlash|^function openGhostRoute'),
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
 ('해저좀비 (미니 보스)', r'v8\.50 해저좀비|^function updateZom|^function zAtk'),
 ('가시관 무당벌레 (미니 보스)', r'v9\.54 가시관 무당벌레|^function updateLad|^function lAtk'),
 ('서리혈랑 (미니 보스)', r'v9\.55 서리혈랑|^function updateFrw|^function frwAtk'),
 ('식물원 잡몹·네임드(가시덩굴·식인 꽃·거대 달팽이)', r'^let GSPECIES|v8\.53 악마 식물원|^function plantStep|^function drawPlantMob'),
 ('⚔ 보스 러시', r'v8\.50 ⚔ 보스 러시|^function startRush|^function rushWin'),
 ('썩어버린 해군 제독', r'v8\.40 썩어버린 해군 제독|^function updateAdmBoss|^function applyPull|^function updateAdmCannon|^const ADM_L'),
 ('파리지옥 마왕', r'v8\.70 파리지옥 마왕|^class VenusAI|^class VfTrap|^class VfSkull|^class VfHeart|^function updateVfFx|^function drawVfScreen'),
 ('타락한 원예의 여왕', r'v8\.63 타락한 원예의 여왕|^class QueenAI|^class RootBind|^class SporeSack|^class QnMush|^function drawQnScreen'),
 ('● 층·맵', None),
 ('층 세트(지옥/버섯/어인섬)', r'^function floorSet|^const isSea|^const isMush'), ('버섯 세트', r'^const MSPECIES|^const MMAP'), ('어인섬 세트', r'^const SSPECIES|^const SMAP|^function warmSea'),
 ('챌린지 모드', r'v6\.20 ∞ 챌린지|^function startChallenge'),
 ('챌린지: 시련의 제단(v8.87)', r'v8\.87 시련의 제단|^function chAltarTick'), ('챌린지 마왕: 영원의 온실주(v8.87)', r'v8\.87 마왕: 영원의 온실주|^function updateGrnBoss'),
 ('● 화면·UI', None),
 ('카드 선택 창', r'^function openChoice|^function openUpgrade|^function cardView'), ('HUD', r'^function drawHud'),
 ('부패한 성상(타락천사 판 미니 보스)', r'v8\.06 부패한 성상|^function spawnStat|^function sAtk|^function updateStat|^function drawStat'),
 ('보스 심장', r'v8\.01 보스 심장|^function rerollHeart|^function equipHeart|^function playUpgradeEffect|^function heartBonus'),
 ('스킨 가챠·도감', r'v7\.30 스킨 가챠|^function gachaRoll|^function renderGacha|^function skinOn|^const SKINS'),
 ('설정·쿠폰', r'pyeon\(\)'), ('난이도 안내문', r'diffDesc'), ('세이브(키 변경 금지)', r'hellSurvivorSave1'),
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
