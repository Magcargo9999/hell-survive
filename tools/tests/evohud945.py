"""v9.45 진화 조건 HUD: 체력바 아래에 조건 패널 + 카드 칩이 그 아래 (스크린샷 build/evohud_*.png)"""
import asyncio,sys
sys.path.insert(0,'/home/claude/hell-survive/tools')
from playwright.async_api import async_playwright
import h301
STEP="if(G.state!=='play')__s();"
async def main():
    async with async_playwright() as pw:
        b=await pw.chromium.launch(); pg=await h301.newpage(b,1280,720); errs=[]
        pg.on('pageerror',lambda e:errs.append(str(e)[:160]))
        await pg.wait_for_function('__G.IMG&&__G.IMG.boss',timeout=90000)
        for ch,lv in [('wolf',3),('lizard',12),('archer',5),('snail',4),('chimera',3),('ghost',3)]:
            n=await pg.evaluate("""([ch,lv])=>{const G=__G;G.startGame(ch);__lv(lv);const P=G.P;P.up.speed=2;P.up.thirst=1;for(let i=0;i<20;i++){G.tick(1/30);"""+STEP+"""}return G.pendingConds().map(x=>x.name+'|'+x.c.prog())}""",[ch,lv])
            print(ch,n)
            await pg.screenshot(path=f'/home/claude/hell-survive/build/evohud_{ch}.png',clip={'x':0,'y':0,'width':520,'height':260})
        print('errs',errs); await b.close()
asyncio.run(main())
