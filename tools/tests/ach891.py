# v9.01: 마왕 토벌 업적은 10번 처치 — 원숭이 10번(달성) · 타락천사 9번(미달성)
import asyncio
from playwright.async_api import async_playwright
from h301 import newpage
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(args=['--disable-gpu']); pg=await newpage(b,1100,800)
        r=await pg.evaluate("""()=>{const G=__G,S=G.SAVE;S.heart={inv:[],eq:[],n:0,got:{}};S.ach={done:{},got:{}};S.dex.kills.boss=10;S.dex.kills.boss6=9;G.openAch();
          const rows=[...document.querySelectorAll('#achList .achrow')];const done=rows.filter(r=>r.classList.contains('done')).map(r=>r.querySelector('b').textContent);
          const btn=rows.find(r=>r.textContent.includes('원숭이 마왕 토벌')).querySelector('button');btn.click();
          return {total:rows.length,done,inv:S.heart.inv.map(q=>q.b+':'+q.g),got:Object.keys(S.heart.got),ach:S.ach.got}}""")
        print(r); await pg.wait_for_timeout(300); await pg.screenshot(path='build/shots/ach891.png'); print(pg.errs); await b.close()
asyncio.run(main())
