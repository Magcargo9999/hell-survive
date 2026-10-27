"""잭팟 머신 '레벨 +1' → 증강 선택창이 뜨는지 (여러 캐릭터 · 레벨)"""
import asyncio, sys, os
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, HERE)
from playwright.async_api import async_playwright
import h301
async def main():
    async with async_playwright() as pw:
        b = await pw.chromium.launch(); pg = await h301.newpage(b, 1280, 720); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.wait_for_function('__G.IMG&&__G.IMG.boss', timeout=90000)
        for ch in ['wolf','snail','archer','chimera','lizard','twins','ghost','octo','gun','fish']:
            for lv in [3, 9, 19, 24]:
                r = await pg.evaluate("""([ch,lv])=>{const G=__G;G.startGame(ch);const P=G.P;__lv(lv);for(let i=0;i<5;i++)G.tick(1/30);
                  const o={ch,lv,st0:G.state};
                  G.openSlot({x:P.x,y:P.y,t:0,life:80,used:false,cool:false});G.slotSpin&&G.slotSpin();
                  G.slotUI.res=G.SLOT_FX.find(f=>f.id==='lvl');G.slotUI.t=3;G.slotResult();G.closeSlot(true);
                  o.st=G.state;o.lvl=P.lvl;o.choice=!!document.querySelector('#choiceBox:not([style*="none"])')||(getComputedStyle(document.getElementById('choice')||document.body).display);return o}""", [ch, lv])
                print(r)
        print('ERRS', errs[:5]); await b.close()
asyncio.run(main())
