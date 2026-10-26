"""v9.50 심장 드랍: 보유 기준 (분해하면 다시 드랍, 보유·장착 중이면 안 드랍)"""
import asyncio
from h301 import *
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); pg = await newpage(b, 1280, 720)
        r = await pg.evaluate("""()=>{const G=__G,S=G.SAVE.heart;S.inv=[];S.eq=[];S.got={};const o={};
          const n=()=>{let c=0;for(let i=0;i<400;i++)if(G.rollHeartDrop('monkey'))c++;return c};
          o.empty=n()>0;
          const h=G.heartGain('rare','monkey'); o.held=n(); 
          S.got.monkey=true; o.dis=G.disHeart(h.id)>0; o.afterDis=n()>0; o.stale=!!S.got.monkey; return o}""")
        print(r, 'OK' if r['empty'] and r['held']==0 and r['afterDis'] else 'FAIL')
        print('오류:', pg.errs); await b.close()
asyncio.run(main())
