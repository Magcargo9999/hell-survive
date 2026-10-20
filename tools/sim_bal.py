"""v5.26 밸런스 측정: 실제 필드 플레이(Lv.1→25) + Lv.25 도달 시 바로 마왕전(3분 제한).
필드에서 실패하면 같은 시드로 즉시 Lv.25까지 올린 빌드로 마왕전만 따로 측정(sim600 방식).
사용: python3 tools/sim_bal.py '<변형 json 리스트>' <보스 json 리스트> <반복 N> <출력 jsonl> [시드 오프셋]
"""
import asyncio, sys, json, os
from playwright.async_api import async_playwright
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
URL = 'file://' + os.path.join(ROOT, 'build', 'hell_survive.html')
JS = open(os.path.join(ROOT, 'tools', 'bal_js.js'), encoding='utf8').read()
S6 = open(os.path.join(ROOT, 'tools', 'sim600.py'), encoding='utf8').read()
JS6 = S6.split('JS="""', 1)[1].split('"""', 1)[0].replace('G.startGame(ch);', 'G.SAVE.fw.open=true; G.SAVE.fw.cleared=true; G.startGame(ch);', 1).replace('let i=c.findIndex(u=>u.key===want&&!u.locked);', 'let i=c.findIndex(u=>u.key===want); if(i>=0&&c[i].locked) c[i].locked=false;', 1)
VAR = {'wolf:abyss': ('wolf', 'abyss', ''), 'wolf:twin': ('wolf', 'twin', ''), 'wolf:blood': ('wolf', 'crimson', 'blood'), 'wolf:holy': ('wolf', 'crimson', 'holy'), 'wolf:fallen': ('wolf', 'crimson', 'fallen'),
       'snail:venom': ('snail', 'venom', ''), 'snail:lava': ('snail', 'lava', ''), 'snail:bomb': ('snail', 'bomb', ''),
       'archer:red': ('archer', 'elf', 'red'), 'archer:holy': ('archer', 'elf', 'holy'), 'archer:skel': ('archer', 'skel', ''),
       'chimera:wind': ('chimera', 'wind', ''), 'chimera:flame': ('chimera', 'flame', ''), 'chimera:dream': ('chimera', 'dream', ''),
       'lizard:rage': ('lizard', 'sword', 'rage'), 'lizard:water': ('lizard', 'sword', 'water'), 'lizard:guard': ('lizard', 'guard', 'guard'),
       'twins': ('twins', '', ''), 'ghost': ('ghost', '', ''), 'octo': ('octo', '', '')}
SEM = asyncio.Semaphore(int(os.environ.get('PAR', '2')))
SEEDJS = "(()=>{let a=%d>>>0;Math.random=function(){a|=0;a=a+0x6D2B79F5|0;let t=Math.imul(a^a>>>15,1|a);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296;};})()"

async def page(b, seed, fw):
    pg = await b.new_page(viewport={'width': int(os.environ.get('VW', 1600)), 'height': int(os.environ.get('VH', 900))})
    await pg.add_init_script(SEEDJS % ((seed * 2654435761) & 0xffffffff))
    await pg.goto(URL, timeout=180000); await pg.wait_for_function('window.__G&&__G.ready', timeout=90000)
    await pg.evaluate('(fw)=>{window.__RANDPICK=1;window.__RESCUE=1;window.__DUR=180;window.__LIM=1800;if(fw)window.__FW=1;}', fw)
    for k in ('DW','OW'):
        if os.environ.get(k): await pg.evaluate('([k,v])=>{window["__"+k]=v}', [k, float(os.environ[k])])
    return pg

async def job(b, v, bk, seed, out):
    ch, rt, fin = VAR[v]; fw = bk == 'fw'
    async with SEM:
        r = {}
        try:
            pg = await page(b, seed, fw)
            r = await pg.evaluate(JS, [ch, rt, fin, 'std', 25, 0, 0, True, seed, 0, False, '' if fw else bk])
            await pg.close()
            if os.environ.get('NOBOSS'): pass
            elif 'boss' not in r:   # 필드 실패 → 즉시 Lv.25 빌드로 보스전만
                pg = await page(b, seed + 5000, fw)
                r6 = await pg.evaluate(JS6, [ch, rt, fin, 'std', 25, 0, 0, True, seed, 0, False, '' if fw else bk])
                await pg.close()
                r['boss'] = r6.get('boss'); r['bossSrc'] = 'instant'
            else: r['bossSrc'] = 'field'
        except Exception as e:
            r = {'err': str(e)[:800]}
        r.update(v=v, bk=bk, seed=seed)
        with open(out, 'a') as f: f.write(json.dumps(r, ensure_ascii=False) + '\n')
        print(v, bk, seed, (r.get('field') or {}).get('res'), (r.get('field') or {}).get('gt'), (r.get('boss') or {}).get('left'), flush=True)

async def main():
    if sys.argv[1] == 'JOBS':   # JOBS <jobs.json [[v,bk,seed],...]> <출력>
        jl = json.load(open(sys.argv[2])); out = sys.argv[3]
        async with async_playwright() as pw:
            b = await pw.chromium.launch()
            await asyncio.gather(*[job(b, v, bk, sd, out) for v, bk, sd in jl])
            await b.close()
        return
    vs = json.loads(sys.argv[1]); bks = json.loads(sys.argv[2]); N = int(sys.argv[3]); out = sys.argv[4]; off = int(sys.argv[5]) if len(sys.argv) > 5 else 0
    async with async_playwright() as pw:
        b = await pw.chromium.launch()
        jobs = [job(b, v, bk, 101 + off + i * 13 + j * 997, out) for i in range(N) for j, bk in enumerate(bks) for v in vs]
        await asyncio.gather(*jobs)
        await b.close()
asyncio.run(main())
