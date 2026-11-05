"""v10.31 챌린지 전용 맵(바닥·소품·불바닥·가시·제단·푸른 기운) 확인 + 스크린샷
사용: PYTHONPATH=tools GAME_URL=http://localhost:8765/build/hell_survive.html python3 tools/tests/chmap1031.py"""
import asyncio, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from playwright.async_api import async_playwright
import h301
B = os.path.join(h301.ROOT, 'build', 'qa') + '/'
SETUP = """()=>{const G=__G,S=G.SAVE;S.ch.open=true;S.diff.max=39;S.diff.clr=38;S.shards=99999;for(const k of ['boss','boss2','boss4','boss6','boss14','boss19'])S.dex.kills[k]=1}"""
async def ev(pg, js, a=None):
    try: return await pg.evaluate(js, a)
    except Exception as ex: return 'ERR ' + str(ex).split('\n')[0][:300]
async def main():
    async with async_playwright() as pw:
        b = await pw.chromium.launch(); pg = await h301.newpage(b, 1280, 760); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e))); pg.on('console', lambda m: errs.append(m.text) if m.type == 'error' else None)
        await ev(pg, SETUP); await ev(pg, "()=>__G.startChallenge('wolf')")
        for i in range(160):
            if await ev(pg, "()=>__G.state==='play'&&!!__G.chal"): break
            await pg.wait_for_timeout(250)
        print('chmOn', await ev(pg, "()=>__G.chmOn()"))
        await ev(pg, "()=>{const G=__G,P=G.P;P.x=1400;P.y=900;P.inv=99;__run(40)}"); await pg.screenshot(path=B + 'chm_field.png')
        # 타일 분포
        print('tiles', await ev(pg, "()=>{const G=__G,h={};for(let y=-60;y<60;y++)for(let x=-60;x<60;x++){const t=G.chmTile(x,y);h[t]=(h[t]||0)+1}return h}"))
        # 불바닥 · 가시 · 제단
        await ev(pg, """()=>{const G=__G,c=G.chal,P=G.P;P.x=0;P.y=0;P.inv=99;c.fires.push({x:P.x+150,y:P.y+30,r:100,t:2,life:9});c.fires.push({x:P.x-200,y:P.y+60,r:80,t:0.4,life:9});
           c.spikes.push({x:P.x+60,y:P.y-120,t:0.6,hit:false});c.spikes.push({x:P.x-60,y:P.y-120,t:G.CH.spikeWarn+0.2,hit:true});c.altar={x:P.x,y:P.y+230,life:30,hold:0.4};G.banner=null;__run(2);G.banner=null}""")
        await pg.screenshot(path=B + 'chm_haz.png')
        await ev(pg, "()=>{__G.chal.siren=2}"); await pg.wait_for_timeout(300); await pg.screenshot(path=B + 'chm_siren.png')
        await ev(pg, "()=>__run(900)")
        print('errs', errs[:5])
        await b.close()
asyncio.run(main())
