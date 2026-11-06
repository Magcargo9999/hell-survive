"""보스 러시 산소 게이지가 그려지는지: 마왕마다 2라운드에서 '🫧 산소' 글씨가 실제로 그려지는지 확인"""
import asyncio, sys, json, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from playwright.async_api import async_playwright
import h301
async def main():
    async with async_playwright() as pw:
        b = await pw.chromium.launch(); pg = await h301.newpage(b, 1280, 720)
        await pg.wait_for_timeout(1500)
        bosses = sys.argv[1:] or await pg.evaluate("()=>__G.BR_ORDER||[]")
        await pg.evaluate("""()=>{const c=__G.ctx,f=c.fillText.bind(c);window.__o2n=0;c.fillText=function(t,...a){if(typeof t==='string'&&t.indexOf('🫧')>=0)window.__o2n++;return f(t,...a)}}""")
        bad = []
        for bk in bosses:
            await pg.evaluate("""()=>{const G=__G;G.SAVE.diff.clr=29;G.SAVE.diff.max=5;G.SAVE.diff.sel=0;G.SAVE.shards=1e6;G.startRush('wolf')}""")
            await pg.evaluate("""()=>{const G=__G;let g=0;while(g++<900){const t=document.getElementById('levelTitle').textContent;if(G.state==='levelup'&&t.indexOf('몇 개')>=0){G.pick(0);continue}if(__s())continue;if(G.state==='play'&&G.rush.init){G.tick(1/30);continue}break}}""")
            for rd in (1, 2, 3):
                r = await pg.evaluate("""async([bk,rd])=>{const G=__G,r=G.rush;r.ord=[bk,bk,bk,bk];r.i=rd;r.ph='prep';r.wait=0;
                  for(let i=0;i<1500;i++){G.P.inv=99;G.P.hp=G.P.max;G.tick(1/30);if(G.boss&&G.boss.st!=='intro'&&r.ph==='fight')break;if(i%20===0)await new Promise(q=>setTimeout(q,30))}
                  if(!G.boss)return {err:'noboss',state:G.state,ph:r.ph};
                  window.__o2n=0;const P=G.P;G.boss.invul=true;let big=0;
                  for(let i=0;i<150;i++){P.inv=99;P.hp=P.max;G.tick(1/30);if(r.paused())big++;await new Promise(q=>setTimeout(q,16))}
                  return {has:r.has('o2'),o2:Math.round(P.o2),drawn:window.__o2n,paused:big,ph:r.ph,state:G.state}}""", [bk, rd])
                print(bk, rd, json.dumps(r, ensure_ascii=False))
                if r.get('err') or r['drawn'] == 0: bad.append((bk, rd))
        print('errs', pg.errs[:5]); print('BAD', bad); await b.close()
asyncio.run(main())
