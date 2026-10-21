"""v6.22 카드 티어 시뮬: 시너지·스킬카드·캐릭터별 궁합. 판마다 build/card/raw.jsonl 에 1줄 append (이어 돌리기 가능).
환경변수: PAR(3) SEEDS(3) BOSSES(monkey,eye) STOP(epoch 초, 이후 새 판 시작 안 함)"""
import asyncio, json, os, sys, time, random
from playwright.async_api import async_playwright
import tier2 as T2
ROOT = T2.ROOT; FN = os.path.join(ROOT, 'build', 'card', 'raw.jsonl')
JS = T2.JS_BOSS.replace("(up[id]||0)<3&&idx(id)!==undefined", "(up[id]||0)<(POL.mm||3)&&idx(id)!==undefined")
assert 'POL.mm' in JS
x1="const sy=ok.find(i=>c[i].cls==='syn'); if(sy!==undefined) return sy;"
assert JS.count(x1)==1
JS=JS.replace(x1,"const sy=POL.only1?undefined:ok.find(i=>c[i].cls==='syn'); if(sy!==undefined) return sy;")
x2="const good=ok.filter(i=>!bad.has(c[i].id)&&String(c[i].id)[0]!=='_');"
assert JS.count(x2)==1
JS=JS.replace(x2,"const good=ok.filter(i=>!bad.has(c[i].id)&&String(c[i].id)[0]!=='_'&&!(POL.only1&&c[i].cls==='syn'&&c[i].id!==POL.syn));")
TG = {t['variant']: t for t in T2.T['targets'] if t['stage'] == 2}
BASE = ['wolf:crimson', 'snail:venom', 'snail:bomb', 'archer:red', 'chimera', 'lizard:rage', 'twins', 'ghost', 'octo', 'snail:lava']
AUX = ['claw', 'armor', 'heart', 'speed', 'range', 'move']
NOPOOL = ['exp', 'magnet', 'knock', 'orb', 'shard', 'crit', 'move', 'range']
COMMON = {'fireBone': ['shard', 'orb'], 'soulStorm': ['orb', 'magnet'], 'rush': ['move', 'speed'], 'lifeOrb': ['heart', 'magnet'], 'tstorm': ['thunder', 'speed'], 'bstorm': ['blade', 'range'],
          'dnova': ['nova', 'knock'], 'inferno': ['aura', 'armor'], 'deadeye': ['crit', 'claw'], 'iron': ['armor', 'heart'], 'harvest': ['exp', 'magnet']}
ONLY = {'wolf:crimson': {'vamp': ['claw', 'heart'], 'frenzy': ['claw', 'move']},
        'snail:venom': {'corpse': ['range', 'claw'], 'spore': ['shard', 'spread'], 'snare': ['sticky', 'knock']},
        'snail:bomb': {'corpse': ['range', 'claw'], 'spore': ['shard', 'spread'], 'snare': ['sticky', 'knock']},
        'archer:red': {'ricochet': ['claw', 'shard'], 'mark': ['snipe', 'crit'], 'gust': ['kite', 'move']},
        'chimera': {'galeWing': ['airA', 'airB']}, 'chimera:flame': {'blaze': ['flameA', 'flameB']}, 'chimera:dream': {'gaze': ['dreamA', 'dreamB']},
        'lizard:rage': {'regen': ['scale', 'heart'], 'quake': ['smash', 'knock']}, 'twins': {'pendulum': ['heavy', 'knock'], 'vortex': ['whirl', 'move']},
        'octo': {'oBig': ['range', 'claw'], 'oReso': ['knock', 'speed'], 'oDrain': ['exp', 'heart']}}
SKILLC = {'thunder': 'thunder', 'blade': 'blade', 'nova': 'nova', 'aura': 'aura'}


def pol(cfg, v):
    kind, _, key = cfg.partition(':')
    syn = None; mat = []; mm = 3
    if kind == 'syn': syn = key; mat = COMMON.get(key) or ONLY[v][key]
    elif kind == 'skill': mat = [key]; mm = 5
    aux = [a for a in AUX if a not in mat]
    no = [n for n in NOPOOL if n not in mat and n not in aux]
    return {'cond': T2.COND.get(v, {}), 'syn': syn or '__none__', 'mat': mat, 'aux': aux, 'no': no, 'mm': mm, 'only1': True}


def cells():
    out = []
    for v in BASE + ['chimera:flame', 'chimera:dream']: out.append((v, 'ctrl'))
    for v in BASE:
        for s in COMMON:
            if v == 'octo' and s in ('fireBone', 'soulStorm'): continue
            out.append((v, 'syn:' + s))
        for k in SKILLC: out.append((v, 'skill:' + k))
    for v, d in ONLY.items():
        for s in d: out.append((v, 'syn:' + s))
    return out

SEM = asyncio.Semaphore(int(os.environ.get('PAR', 3)))
STOP = float(os.environ.get('STOP', 0)) or 1e18


async def one(b, v, cfg, boss, seed):
    if time.time() > STOP: return
    t = TG[v]; ch, rt, fin = T2.rt_of(t); p = pol(cfg, v)
    async with SEM:
        if time.time() > STOP: return
        t0 = time.time()
        try:
            pg = await T2.newpage(b, seed, {'__DUR': 420, '__POL': p})
            r = await pg.evaluate(T2.wrap(JS, seed), [ch, rt, fin, 'std', 25, 0, 0, True, seed, 0, False, boss])
            await pg.close()
        except Exception as e:
            print('ERR', v, cfg, boss, seed, str(e)[:120], flush=True); return
    x = r['t2']; bo = r['boss']; mx = x['bmx'] or bo.get('mx') or 0
    dead = bo['dead']; won = bool(x['won'] and not dead)
    rem = 0.0 if won else (100 * bo['left'] / mx if mx else None)
    rec = dict(v=v, cfg=cfg, boss=boss, seed=seed, win=won, dead=dead, t=round(bo['t'], 1), removed=round(100 - rem, 2) if rem is not None else None, loss=bo['loss'],
               dm={k: round(val) for k, val in x['dm'].items()}, up=x['up'], syn=list(x['syn'].keys()), synl=x['synl'], lv=x['lv1'], casts=bo['casts'], err=x.get('err'), sec=round(time.time() - t0, 1))
    with open(FN, 'a', encoding='utf8') as f: f.write(json.dumps(rec, ensure_ascii=False) + '\n')
    print(v, cfg, boss, seed, 'W' if won else 'D' if dead else 'T', rec['removed'], flush=True)


async def main():
    done = set()
    if os.path.exists(FN):
        for l in open(FN, encoding='utf8'):
            try: d = json.loads(l); done.add((d['v'], d['cfg'], d['boss'], d['seed']))
            except Exception: pass
    seeds = int(os.environ.get('SEEDS', 3)); bosses = os.environ.get('BOSSES', 'monkey,eye').split(',')
    cl = cells(); print('cells', len(cl), flush=True)
    async with async_playwright() as pw:
        b = await pw.chromium.launch()
        for s in range(1, seeds + 1):          # 시드 바깥 루프: 언제 멈춰도 균형 잡힌 데이터
            jobs = [(v, c, bk) for (v, c) in cl for bk in bosses if (v, c, bk, s) not in done]
            random.Random(s).shuffle(jobs)
            print('seed', s, 'jobs', len(jobs), flush=True)
            await asyncio.gather(*[one(b, v, c, bk, s) for v, c, bk in jobs])
        await b.close()
    print('ALLDONE', flush=True)
asyncio.run(main())
