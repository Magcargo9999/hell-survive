"""보스 러시 2라운드 산소 진단: 마왕마다 산소가 실제로 줄어드는지 (가만히 서서 6초)"""
import asyncio, sys, json, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from playwright.async_api import async_playwright
import h301
async def main():
    async with async_playwright() as pw:
        b = await pw.chromium.launch(); pg = await h301.newpage(b, 1280, 720)
        await pg.wait_for_timeout(1500)
        bad = []; bosses = sys.argv[1:] or None
        if not bosses:
            bosses = await pg.evaluate("()=>__G.BR_ORDER||[]")
        for bk in bosses:
            await pg.evaluate("""(bk)=>{const G=__G;G.SAVE.diff.clr=29;G.SAVE.diff.max=5;G.SAVE.diff.sel=0;G.SAVE.shards=1e6;G.startRush('wolf')}""", bk)
            await pg.evaluate("""()=>{const G=__G;let g=0;while(g++<900){const t=document.getElementById('levelTitle').textContent;if(G.state==='levelup'&&t.indexOf('몇 개')>=0){G.pick(0);continue}if(__s())continue;if(G.state==='play'&&G.rush.init){G.tick(1/30);continue}break}}""")
            r = await pg.evaluate("""async(bk)=>{const G=__G,r=G.rush;r.ord=[bk,bk,bk,bk];r.i=1;r.wait=0;
              for(let i=0;i<1500;i++){G.P.inv=99;G.P.hp=G.P.max;G.tick(1/30);if(G.boss&&G.boss.st!=='intro'&&r.ph==='fight')break;if(i%20===0)await new Promise(q=>setTimeout(q,30))}
              if(!G.boss)return {err:'noboss',state:G.state,ph:r.ph};
              const P=G.P;G.boss.invul=true;const o0=P.o2;let paused=0,N=360;
              for(let i=0;i<N;i++){P.inv=99;P.hp=P.max;G.tick(1/30);if(r.paused())paused++}
              return {bk:G.boss.bk,has:r.has('o2'),mods:r.modifiers.join('+'),o2:[Math.round(o0),Math.round(P.o2)],paused:Math.round(paused/N*100)+'%',gey:r.gey.length,ph:r.ph}}""", bk)
            print(bk, json.dumps(r, ensure_ascii=False))
            if bk != 'kng' and (r.get('err') or r['o2'][0] - r['o2'][1] < 30): bad.append(bk)
        print('errs', pg.errs[:5]); print('FAIL' if bad else 'OK'); await b.close()
asyncio.run(main())
