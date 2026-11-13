"""v10.46 [기타] → 각성한 원숭이 마왕 도전 버튼 · 다시 도전(R) = 체험 다시 · 다른 모드로 나가면 풀림"""
import asyncio
from playwright.async_api import async_playwright
from h301 import newpage
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); pg = await newpage(b, 1280, 760)
        await pg.click('#etcBtn'); await pg.wait_for_timeout(300); await pg.screenshot(path='build/amk/ui_etc.png')
        await pg.click('#amkBtn'); await pg.wait_for_timeout(600)
        print(await pg.evaluate("()=>({st:__G.state,trial:!!(__G.rush&&__G.rush.trial),lvT:document.getElementById('levelTitle').textContent,bk:__G.P.bossK,tier:__G.P.tier})"))
        await pg.screenshot(path='build/amk/ui_pick.png')
        r = await pg.evaluate("""async()=>{const G=__G;window.__rt=0;window.__fin=0;let n=0;while(n++<4000){if(__s())continue;if(G.arena&&G.boss&&G.boss.bk==='amk')break;G.P.hp=G.P.max;G.P.inv=9;G.tick(1/30);if(n%40===0)await new Promise(r=>setTimeout(r,30))}
          const P=G.P;P.inv=0;P.shield=0;P.reviveLeft=0;P.revived=true;P.rel={};P.hp=1;for(let i=0;i<400&&G.state==='play';i++){P.inv=0;P.hp=Math.min(P.hp,1);G.tick(1/30)} for(let i=0;i<200;i++)G.tick(1/30);
          return {st:G.state,over:document.getElementById('overTitle').textContent,stats:document.getElementById('overStats').innerHTML.match(/👹[^<]*/)?.[0],earned:P.earned}}""")
        print(r); await pg.wait_for_timeout(300); await pg.screenshot(path='build/amk/ui_dead.png')
        await pg.keyboard.press('KeyR'); await pg.wait_for_timeout(500)
        print('retry →', await pg.evaluate("()=>({st:__G.state,trial:!!(__G.rush&&__G.rush.trial),lv:__G.P.lvl})"))
        print('errs', pg.errs); await b.close()
asyncio.run(main())
