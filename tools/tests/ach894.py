import asyncio
from playwright.async_api import async_playwright
from h301 import newpage
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(args=['--disable-gpu']); pg=await newpage(b,1000,700)
        r=await pg.evaluate("""()=>{const G=__G,S=G.SAVE,o={};S.heart={inv:[],eq:[],n:0,got:{}};S.ach={done:{},got:{}};
          S.dex.kills.boss3=299;G.achSync();o.a299=!!S.ach.done.hb_fw;
          S.dex.kills.boss3=300;G.achSync();o.a300=!!S.ach.done.hb_fw;
          G.openAch();const btn=[...document.querySelectorAll('#achList .achrow')].find(r=>r.textContent.includes('혈랑왕 사냥꾼')).querySelector('button');btn.click();
          const h=S.heart.inv[0];o.h=h&&{b:h.b,g:h.g,n:G.hOpt(h).split(' · ').length,t:G.hTitle(h)};o.got=!!S.ach.got.hb_fw;
          S.shards=5000;const rr=G.rerollHeart(h.id);o.re=!!(rr.after.st3);o.dropOk=S.heart.got.fw;
          document.getElementById('heartBtn').click();return o}""")
        await pg.wait_for_timeout(400); await pg.screenshot(path='build/a894.png'); print(r,pg.errs); await b.close()
asyncio.run(main())
