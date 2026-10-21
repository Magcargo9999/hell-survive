"""v6.30 프레임 측정: 실제 게임 루프(그리기 포함)를 돌리며 프레임 시간과 CPU 사용 함수를 잰다.
사용: python3 tools/perf.py [장면...]  (장면: field · boss · angel · dream · chal · 기본 = 전부)  결과: 프레임 ms 평균/95%/최대 + 함수별 자기 시간 상위"""
import asyncio, sys, os, json, collections
from playwright.async_api import async_playwright
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from h301 import newpage
SCENES = {
    'field': "()=>{const G=__G;G.startGame('wolf');window.__rt=1;__lv(22);G.setT(560);for(let i=0;i<260;i++)G.spawnEnemy();}",
    'boss': "()=>{const G=__G;G.SAVE.diff.max=5;G.SAVE.shards=999;G.SAVE.diff.sel=5;G.startGame('ghost');G.P.bossK='skel';__lv(25);G.enemies.length=0;G.raiseCastle();G.enterArena();}",
    'angel': "()=>{const G=__G;G.SAVE.diff.max=5;G.SAVE.shards=999;G.SAVE.diff.sel=4;G.startGame('snail');window.__rt=2;G.P.bossK='angel';__lv(25);G.enemies.length=0;G.raiseCastle();G.enterArena();}",
    'dream': "()=>{const G=__G;G.startGame('chimera');window.__rt=2;__lv(22);G.setT(500);for(let i=0;i<200;i++)G.spawnEnemy();}",
    'chal': "()=>{const G=__G;G.SAVE.ch.open=true;G.setChMode(true);G.startGame('octo');__lv(20);G.setT(900);for(let i=0;i<220;i++)G.spawnEnemy();}",
}
HOOK = """()=>{window.__ft=[];let l=performance.now();const f=t=>{window.__ft.push(t-l);l=t;requestAnimationFrame(f)};requestAnimationFrame(f);
  window.__keep=setInterval(()=>{const G=__G;if(!G.P)return;G.P.inv=99;G.P.hp=G.P.max;if(G.state==='levelup'||G.state==='evolve')__s();},100);}"""
async def scene(b, name, js, secs):
    pg = await newpage(b, 1280, 720)
    await pg.evaluate(js); await pg.evaluate("()=>{const G=__G;G.SAVE.set.speed=1;}")
    await pg.wait_for_timeout(1500)
    cdp = await pg.context.new_cdp_session(pg)
    await cdp.send('Profiler.enable'); await cdp.send('Profiler.setSamplingInterval', {'interval': 200}); await cdp.send('Profiler.start')
    await pg.evaluate(HOOK); await pg.wait_for_timeout(int(secs * 1000))
    prof = (await cdp.send('Profiler.stop'))['profile']
    ft = sorted(await pg.evaluate("window.__ft.slice(3)"))
    n = len(ft); info = await pg.evaluate("()=>({en:__G.enemies.length,st:__G.state,boss:__G.boss&&__G.boss.bk})")
    nodes = {x['id']: x for x in prof['nodes']}; self_t = collections.Counter()
    dts = prof['timeDeltas']; samples = prof['samples']
    for sid, dt in zip(samples, dts):
        cf = nodes[sid]['callFrame']; self_t[(cf['functionName'] or '(anon)') + ':' + str(cf['lineNumber'])] += dt
    tot = sum(self_t.values()) or 1
    print(f"== {name}: 프레임 {n}개  평균 {sum(ft) / max(1, n):.1f}ms  95% {ft[int(n * 0.95)] if n else 0:.1f}ms  최대 {ft[-1] if n else 0:.1f}ms  적 {info['en']} {info}")
    for k, v in self_t.most_common(18): print(f"   {100 * v / tot:5.1f}%  {k}")
    print('   errs', pg.errs[:3]); await pg.close()
async def main():
    names = sys.argv[1:] or list(SCENES)
    async with async_playwright() as p:
        b = await p.chromium.launch(args=os.environ.get('PERF_ARGS', '--enable-gpu-rasterization --ignore-gpu-blocklist').split())
        for n in names: await scene(b, n, SCENES[n], float(os.environ.get('SECS', '6')))
        await b.close()
asyncio.run(main())
