"""v6.01 티어 신뢰도 측정 하네스 (원본 로그 수집). 판이 끝날 때마다 JSONL 1줄을 append, 이미 끝난 판은 건너뛴다.
사용: python3 tools/tier2.py <실험 A|B|D|E|PILOT> [옵션]
  환경변수: PAR(병렬, 기본 2) NA(A 판수, 기본 20) NB(B 판수 12) NE(E 판수 10) ND(D 판수 6) BATCH(1) ONLY(variant 쉼표목록)
로그: build/tier2/raw_boss.jsonl(A·D·F) raw_field.jsonl(B) raw_growth.jsonl(E)
게임 로직·봇 로직은 건드리지 않고 로그만 붙인다."""
import asyncio, sys, json, os, hashlib, subprocess, time
from playwright.async_api import async_playwright
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'build', 'tier3')
URL = 'file://' + os.path.join(ROOT, 'build', 'hell_survive.html')
T = json.load(open(os.path.join(OUT, 'targets.json')))
BD = {b['variant']: b for b in json.load(open(os.path.join(OUT, 'build_defs.json')))['builds']}
COND = {'wolf:crimson': {'thirst': 1}, 'wolf:holy': {'thirst': 1, 'heart': 2}, 'wolf:fallen': {'thirst': 1}, 'wolf:twin': {'speed': 2}, 'archer:holy': {'snipe': 1}}
VAR = {'gun': ('gun','',''), 'wolf:fallen': ('wolf', 'crimson', 'fallen')}
S6 = open(os.path.join(ROOT, 'tools', 'sim600.py'), encoding='utf8').read()
BLOODS = {'wolf:crimson': ('wolf', 'crimson', 'blood')}
GAME_COMMIT = subprocess.run(['git', '-C', ROOT, 'log', '-1', '--format=%h', '--', 'src', 'index.html'], capture_output=True, text=True).stdout.strip()
GAME_VER = '8.20'

CHOOSE = r""" function choose(){ const c=G.choices, title=document.getElementById('levelTitle').textContent;
   if(title.indexOf('갈림길')>=0||title.indexOf('최종')>=0){ const want=title.indexOf('최종')>=0?fin:route; let i=c.findIndex(u=>u.key===want); if(i>=0&&c[i].locked) c[i].locked=false; if(i<0)i=c.findIndex(u=>!u.locked); return i<0?0:i; }
   if(title.indexOf('특수')>=0) return 0;
   const ok=c.map((u,i)=>i).filter(i=>!c[i].locked);
   if(window.__RANDPICK){ const sy=ok.filter(i=>c[i].cls==='syn'); if(sy.length&&rnd()<0.6) return sy[0]; const nn=ok.filter(i=>c[i].cls!=='syn'); const pool=nn.length?nn:ok; return pool.length?pool[Math.floor(rnd()*pool.length)]:0; }
   const POL=window.__POL, up=P.up, idx=id=>ok.find(i=>c[i].id===id); let i;
   for(const [id,mn] of Object.entries(POL.cond||{})){ if((up[id]||0)<mn){ i=idx(id); if(i!==undefined) return i; } }
   i=idx(POL.syn); if(i!==undefined) return i;
   const mats=POL.mat.filter(id=>(up[id]||0)<3&&idx(id)!==undefined).sort((a,b)=>(up[a]||0)-(up[b]||0)); if(mats.length) return idx(mats[0]);
   for(const id of POL.aux){ i=idx(id); if(i!==undefined) return i; }
   const sy=ok.find(i=>c[i].cls==='syn'); if(sy!==undefined) return sy;
   const bad=new Set(POL.no||[]); const good=ok.filter(i=>!bad.has(c[i].id)&&String(c[i].id)[0]!=='_'); if(good.length) return good[0];
   const any=ok.find(i=>String(c[i].id)[0]!=='_'); return any!==undefined?any:(ok[0]||0); }
"""
PUMP = r""" function pump(){ const x=G.state; if(x==='levelup'){G.pick(choose());for(const k of Object.keys(P.syn)) if(P.syn[k]&&!(k in SYNT)){SYNT[k]=Math.round(G.gt*10)/10;SYNL[k]=P.lvl;} return true;} if(x==='evolve'){G.tick(dt);return true;} return false; }
"""


def build_js():
    js = S6.split('JS="""', 1)[1].split('"""', 1)[0]
    a, b = js.index(' function choose(){'), js.index(' function pump(){')
    c = js.index(' let guard=0;')
    js = js[:a] + ' const SYNT={},SYNL={};\n' + CHOOSE + PUMP + js[c:]
    js = js.replace("G.SAVE.diff.sel=tier||0; G.startGame(ch);", "G.SAVE.fw.open=true; G.SAVE.fw.cleared=true; G.SAVE.diff.sel=tier||0; G.startGame(ch);", 1)
    R = [("let edmg=0; let expGain=0,", "let nx15=15; const KB=[],HB=[]; let firstNear=null; let edmg=0; let expGain=0,"),
         ("G.tick(dt); t+=dt; G.setT(gt0+t);", "G.tick(dt); t+=dt; if(t>=nx15){nx15+=15;KB.push(P.kills-k0);HB.push(Math.round(100*Math.max(0,P.hp)/P.max));} G.setT(gt0+t);"),
         ("if(P.hp<P.max*0.15){ deaths++;", "if(P.hp<P.max*0.15){ if(firstNear===null)firstNear=Math.round(t*10)/10; deaths++;"),
         ("dead:G.state==='dead'};", "dead:G.state==='dead',kb:KB,hb:HB,firstNear:firstNear,lvl:P.lvl,syn:SYNT,synl:SYNL};"),
         ("const HL={}; const hp0=P.hp;", "const BMX0=G.boss?G.boss.max:0, LV0=P.lvl; let dW=0,nx10=10,nxS=30; const HPP=[],DTK=[],BAT={}; for(const k of Object.keys(G.DMETER)) delete G.DMETER[k]; const HL={}; const hp0=P.hp;"),
         ("G.tick(dt); bt+=dt; if(P.hp<hb){bloss+=hb-P.hp; HL[st0]=(HL[st0]||0)+Math.round(hb-P.hp);}",
          "G.tick(dt); bt+=dt; if(P.hp<hb){bloss+=hb-P.hp; dW+=hb-P.hp; HL[st0]=(HL[st0]||0)+Math.round(hb-P.hp);} if(bt>=nx10){nx10+=10;HPP.push(Math.round(100*Math.max(0,P.hp)/P.max));DTK.push(Math.round(dW));dW=0;} if(bt>=nxS&&nxS<=240){BAT[nxS]=G.boss?Math.round(1000*Math.max(0,G.boss.hp)/G.boss.max)/10:0;nxS+=30;}"),
         ("hl:HL};", "hl:HL}; rec.t2={bmx:BMX0,hpp:HPP,dtk:DTK,bat:BAT,dm:Object.assign({},G.DMETER),syn:SYNT,synl:SYNL,lv0:LV0,lv1:P.lvl,bt:bt,up:JSON.parse(JSON.stringify(P.up)),won:!G.boss&&G.state!=='dead',st:G.state};")]
    for x, y in R:
        assert js.count(x) == 1, x[:50]; js = js.replace(x, y)
    return js


def build_growth_js():
    head = open(os.path.join(ROOT, 'tools', 'bal_head.js'), encoding='utf8').read()
    bot = open(os.path.join(ROOT, 'tools', 'bal_bot.js'), encoding='utf8').read()
    a, b = head.index(' function choose(){'), head.index(' function pump(){')
    c = head.index(' let guard=0, casts=0;') if ' let guard=0, casts=0;' in head else None
    tail = head[head.index('\n', head.index(' function pump(){')):]   # pump 뒤 (빈 줄 + let guard=0, casts=0;)
    head2 = head[:a] + ' const SYNT={},SYNL={};\n' + CHOOSE + PUMP + tail
    grow = r"""
 const LIM=1200; const TL={}; const KS=[],ES=[]; let nx=60, lastL=P.lvl, res='timeout', dl=null, dt0=null; const k00=P.kills;
 const tot=()=>{ let s=0; for(let l=1;l<P.lvl;l++) s+=G.needFor(l); return s+P.exp; };
 while(guard++<400000){
   if(pump()) continue;
   if(G.state==='dead'){res='dead';break;}
   if(G.state!=='play'){res='state:'+G.state;break;}
   if(P.lvl>=8){ if(route==='lava')P.lavaT=Math.max(P.lavaT,5); if(route==='skel')P.poisoned=true; if(route==='dream')P.bugF0=true; if(fin==='rage')P.low10=true; if(fin==='holy'&&ch==='archer'){P.up.snipe=Math.max(1,P.up.snipe||0);P.potions=Math.max(6,P.potions||0);} }
   botMove(); G.tick(dt);
   while(lastL<P.lvl){ lastL++; TL[lastL]=Math.round(G.gt*10)/10; }
   while(G.gt>=nx){ KS.push(P.kills-k00); ES.push(Math.round(tot())); nx+=60; }
   if(G.state==='dead'){res='dead';break;}
   if(P.lvl>=24){res='lv24';break;}
   if(G.gt>LIM){res='timeout';break;}
 }
 return {res:res,TL:TL,KS:KS,ES:ES,lvl:P.lvl,gt:Math.round(G.gt*10)/10,died:G.state==='dead',deathT:G.state==='dead'?Math.round(G.gt*10)/10:null,kills:P.kills,syn:SYNT,synl:SYNL,up:JSON.parse(JSON.stringify(P.up))};
}"""
    return head2 + bot + grow


JS_BOSS = build_js(); JS_GROW = build_growth_js()
BOT_VER = hashlib.sha1((JS_BOSS + JS_GROW + open(__file__, encoding='utf8').read().split('CHOOSE')[0]).encode()).hexdigest()[:8]
# 보스가 막 죽은 틱에 b=null 이면 터지는 것만 막는 널 가드 (BOT_VER 해시에는 포함하지 않음, 게임 결과 불변)
JS_BOSS = JS_BOSS.replace('const TLs=b.tele.slice();', 'const TLs=(b&&b.tele?b.tele:[]).slice();')
assert JS_BOSS.count('G.tick(dt); bt+=dt;') == 1
JS_BOSS = JS_BOSS.replace('G.tick(dt); bt+=dt;', 'try{G.tick(dt);}catch(e){window.__ERRM=String(e).slice(0,100);} bt+=dt;').replace('rec.t2={', 'rec.t2={err:window.__ERRM||null,')
S_FIELD = JS_BOSS
SEEDJS = "(()=>{let a=%d>>>0;window.__rs=function(n){a=n>>>0};Math.random=function(){a|=0;a=a+0x6D2B79F5|0;let t=Math.imul(a^a>>>15,1|a);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296;};})()"
STOP = float(os.environ.get('STOP', 0)) or 1e18
SEM = asyncio.Semaphore(int(os.environ.get('PAR', '2')))
BATCH = int(os.environ.get('BATCH', '1'))


def wrap(js, seed):
    return '(a)=>{window.__rs(%d);return (%s)(a)}' % ((seed * 7 + 17) * 2654435761 & 0xffffffff, js)


def vkey(v):
    return BLOODS.get(v) or VAR.get(v)


def rt_of(t):   # (ch, route, fin) from targets entry
    fam, rt, fin = t['family'], t['route'] or '', t['fin'] or ''
    if t['stage'] == 2 and t['variant'] == 'wolf:crimson': fin = 'blood'
    if t['stage'] == 2 and t['variant'] == 'chimera': rt = 'wind'
    return fam, rt, fin


def policy_of(variant):   # build_defs 항목 -> JS용 정책 (0·1진화는 계열 대표 정책)
    rep = {'wolf': 'wolf:crimson', 'snail': 'snail:venom', 'archer': 'archer:red', 'chimera': 'chimera', 'lizard': 'lizard:rage', 'twins': 'twins', 'ghost': 'ghost', 'octo': 'octo',
           'archer:elf': 'archer:red', 'wolf:crimson': 'wolf:crimson', 'gun': 'gun'}
    v = variant if variant in BD else rep.get(variant, variant)
    b = BD[v]
    return {'cond': COND.get(v, {}), 'syn': b['목표시너지'], 'mat': b['재료카드'], 'aux': b['보조카드우선순위'], 'no': b['비추천카드']}


def load_done(fn):
    done = set()
    if os.path.exists(fn):
        for l in open(fn, encoding='utf8'):
            try: d = json.loads(l)
            except Exception: continue
            done.add((d['exp'], d['variant'], d.get('boss'), d.get('L'), d['seed'], d['policy'], d['bot_mode'], d['batch']))
    return done


async def newpage(b, seed, extra):
    pg = await b.new_page(viewport={'width': 800, 'height': 500})
    await pg.add_init_script(SEEDJS % ((seed * 7 + 17) * 2654435761 & 0xffffffff))
    await pg.goto(URL, timeout=180000); await pg.wait_for_function('window.__G&&__G.ready', timeout=90000)
    await pg.evaluate('(x)=>{Object.assign(window,x)}', extra)
    return pg


def common(exp, t, seed, policy):
    return dict(game_ver=GAME_VER, commit=GAME_COMMIT, bot_ver=BOT_VER, exp=exp, policy=policy, bot_mode='normal', variant=t['variant'], stage=t['stage'], site_id=t['site_id'], seed=seed, batch=BATCH)


async def run_boss(b, exp, t, boss, seed, policy, fn):
    ch, rt, fin = rt_of(t)
    pol = policy_of(t['variant']); fw = boss == 'fw'
    extra = {'__DUR': 420, '__POL': pol}
    if policy == 'random': extra['__RANDPICK'] = 1
    if fw: extra['__FW'] = 1
    t0 = time.time()
    async with SEM:
        if time.time() > STOP: return
        try:
            pg = await newpage(b, seed, extra)
            r = await pg.evaluate(wrap(JS_BOSS, seed), [ch, rt, fin, 'std', 25, 0, 0, True, seed, 0, False, '' if fw else boss])
            await pg.close()
        except Exception as e:
            print('ERR', t['variant'], boss, seed, str(e)[:200], flush=True); return
    x = r['t2']; bo = r['boss']; mx = x['bmx'] or bo.get('mx') or 0
    dead = bo['dead']; won = bool(x['won'] and not dead); et = round(bo['t'], 1)
    rem = 0.0 if won else round(100 * (bo['left'] / mx), 2) if mx else None
    reason = 'player_dead' if dead else ('boss_dead' if won else 'timeout')
    hpa = {}
    for s in range(30, 241, 30):
        v = x['bat'].get(str(s))
        hpa[str(s)] = v if v is not None else (0.0 if won and s >= et else None)
    dm = x['dm']; tot = sum(dm.values()) or 1
    src = {k: round(v) for k, v in sorted(dm.items(), key=lambda kv: -kv[1])}
    rec = common(exp, t, seed, policy)
    rec.update(boss=boss, win=won, end_reason=reason, end_time=et, boss_hp_max=round(mx), boss_hp_removed_pct=round(100 - rem, 2) if rem is not None else None,
               player_death_time=et if dead else None, boss_hp_pct_at=hpa, dmg_taken_total=bo['loss'], dmg_taken_by_10s=x['dtk'], hp_pct_by_10s=x['hpp'],
               dmg_by_source=src, skill_casts=bo['casts'], cards_final=x['up'], synergy_obtained={k: x['syn'].get(k) for k in set([pol['syn']] + list(x['syn']))},
               synergy_level={k: x['synl'].get(k) for k in x['synl']}, target_synergy=pol['syn'], target_synergy_opened=pol['syn'] in x['syn'],
               level_at_start=x['lv0'], level_at_end=x['lv1'], sim_seconds=round(time.time() - t0, 1), game_error=x.get('err'))
    with open(fn, 'a', encoding='utf8') as f: f.write(json.dumps(rec, ensure_ascii=False) + '\n')
    print(exp, t['variant'], boss, seed, reason, et, rem, flush=True)


async def run_field(b, t, seed, fn):
    ch, rt, fin = rt_of(t); L = t['field_L']; gt0 = {8: 150, 15: 360, 24: 600}[L]
    pol = policy_of(t['variant'])
    async with SEM:
        if time.time() > STOP: return
        t0 = time.time()
        try:
            pg = await newpage(b, seed, {'__POL': pol})
            r = await pg.evaluate(wrap(S_FIELD, seed), [ch, rt, fin, 'std', L, gt0, 90, False, seed, 0, False, ''])
            await pg.close()
        except Exception as e:
            print('ERR', t['variant'], L, seed, str(e)[:200], flush=True); return
    w = r['win']
    rec = common('B', t, seed, 'standard'); rec['L'] = L
    rec.update(kills=w['kills'], kills_by_15s=w['kb'], dmg_taken=w['loss'], hp_pct_by_15s=w['hb'], died=w['dead'], death_time=w['t'] if w['dead'] else None,
               near_death_count=w['near'], near_death_first_time=w['firstNear'], exp_gained=w['exp'], level_at_end=r['lvl'], cards_final=r['cards'], skill_casts=w['casts'], damage_dealt=w['edmg'], sim_seconds=round(time.time() - t0, 1))
    with open(fn, 'a', encoding='utf8') as f: f.write(json.dumps(rec, ensure_ascii=False) + '\n')
    print('B', t['variant'], L, seed, w['kills'], w['dead'], flush=True)


async def run_growth(b, t, seed, fn):
    ch, rt, fin = rt_of(t); pol = policy_of(t['variant']); t0 = time.time()
    async with SEM:
        if time.time() > STOP: return
        try:
            pg = await newpage(b, seed, {'__POL': pol})
            r = await pg.evaluate(wrap(JS_GROW, seed), [ch, rt, fin, 'std', 24, 0, 0, False, seed, 0, False, ''])
            await pg.close()
        except Exception as e:
            print('ERR', t['variant'], seed, str(e)[:200], flush=True); return
    rec = common('E', t, seed, 'standard')
    TL = r['TL']
    for L in (5, 10, 15, 20, 24): rec['t_lv%d' % L] = TL.get(str(L))
    rec.update(kills_by_60s=r['KS'], exp_by_60s=r['ES'], died=r['died'], death_time=r['deathT'], death_level=r['lvl'] if r['died'] else None, end_reason={'lv24': 'lv24', 'dead': 'dead', 'timeout': 'timeout'}.get(r['res'], r['res']),
               end_time=r['gt'], level_at_end=r['lvl'], kills=r['kills'], cards_final=r['up'], synergy_level=r['synl'], sim_seconds=round(time.time() - t0, 1))
    with open(fn, 'a', encoding='utf8') as f: f.write(json.dumps(rec, ensure_ascii=False) + '\n')
    print('E', t['variant'], seed, rec['end_reason'], r['gt'], flush=True)


S_FIELD = JS_BOSS   # L 모드(필드)도 같은 JS (boss=False 경로)


async def main():
    exp = sys.argv[1]; only = [x for x in os.environ.get('ONLY', '').split(',') if x]
    tg = T['targets']; finals = [t for t in tg if t['stage'] == 2]
    if only: finals = [t for t in finals if t['variant'] in only]
    BK = os.environ.get('BK','monkey,eye,skel,angel,shk,fw').split(',')
    jobs = []
    fb, ff, fg = [os.path.join(OUT, x) for x in ('raw_boss.jsonl', 'raw_field.jsonl', 'raw_growth.jsonl')]
    if exp in ('A', 'PILOT'):
        pil = ['wolf:crimson', 'snail:lava', 'archer:red', 'ghost']
        fl = [t for t in finals if exp == 'A' or t['variant'] in pil]
        n = int(os.environ.get('NA', 20)) if exp == 'A' else 8
        done = load_done(fb)
        for s in range(1, n + 1):
            for bk in BK:
                for t in fl:
                    if ('A', t['variant'], bk, None, s, 'standard', 'normal', BATCH) not in done: jobs.append(('A', t, bk, s))
    elif exp == 'D':
        sel = [x for x in os.environ.get('DSEL', '').split(',') if x]; fl = [t for t in finals if t['variant'] in sel]; done = load_done(fb)
        for s in range(1, int(os.environ.get('ND', 6)) + 1):
            for bk in BK:
                for t in fl:
                    if ('D', t['variant'], bk, None, s, 'random', 'normal', BATCH) not in done: jobs.append(('D', t, bk, s))
    elif exp == 'B':
        done = load_done(ff); sel = tg if not only else [t for t in tg if t['variant'] in only]
        for s in range(1, int(os.environ.get('NB', 12)) + 1):
            for t in sel:
                if ('B', t['variant'], None, t['field_L'], s, 'standard', 'normal', BATCH) not in done: jobs.append(('B', t, None, s))
    elif exp == 'E':
        done = load_done(fg)
        for s in range(1, int(os.environ.get('NE', 10)) + 1):
            for t in finals:
                if ('E', t['variant'], None, None, s, 'standard', 'normal', BATCH) not in done: jobs.append(('E', t, None, s))
    print('jobs', len(jobs), 'bot_ver', BOT_VER, 'commit', GAME_COMMIT, flush=True)
    async with async_playwright() as pw:
        b = await pw.chromium.launch()
        cs = []
        for e, t, bk, s in jobs:
            if e == 'A' or e == 'D': cs.append(run_boss(b, e, t, bk, s, 'standard' if e == 'A' else 'random', fb))
            elif e == 'B': cs.append(run_field(b, t, s, ff))
            else: cs.append(run_growth(b, t, s, fg))
        await asyncio.gather(*cs)
        await b.close()
    print('ALLDONE', flush=True)

if __name__ == '__main__': asyncio.run(main())
