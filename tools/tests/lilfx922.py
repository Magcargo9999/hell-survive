"""v9.22 릴세르카 도트 — 대기·이동·시전·공격(부채)·거울·사망 스크린샷 + 콘솔 오류"""
import asyncio,sys,json
sys.path.insert(0,'/home/claude/hell-survive/tools')
from playwright.async_api import async_playwright
import h301
B='/home/claude/hell-survive/build/'
async def main():
    async with async_playwright() as pw:
        b=await pw.chromium.launch(); pg=await h301.newpage(b,1280,720); errs=[]
        pg.on('pageerror',lambda e:errs.append(str(e))); pg.on('console',lambda m:errs.append(m.text) if m.type=='error' else None)
        await pg.wait_for_function('__G.IMG&&__G.IMG.ifloor&&__G.IMG.lil',timeout=90000)
        print(await pg.evaluate("""()=>{const G=__G;G.SAVE.diff.max=24;G.SAVE.diff.sel=24;G.SAVE.shards=1e7;G.startGame('archer');const P=G.P;__lv(28);G.raiseCastle();G.enterArena();
          for(let i=0;i<40;i++)G.tick(1/30);__s();const e=G.boss,AI=G.ls;for(const k in AI.cd)AI.cd[k]=99;e.st='glide';e.stT=99;P.x=G.IMAP.cx;P.y=G.IMAP.cy+150;e.x=G.IMAP.cx;e.y=G.IMAP.cy+30;
          for(let i=0;i<330;i++){P.hp=P.max;P.inv=1;e.x=G.IMAP.cx;e.y=G.IMAP.cy+30;P.x=e.x+30;P.y=e.y+400;G.tick(1/30)}return e.bk}"""))
        async def shot(n,js=None,steps=6):
            if js: await pg.evaluate(js)
            for i in range(steps): await pg.evaluate("()=>{const G=__G;G.P.hp=G.P.max;G.P.inv=1;G.tick(1/30)}")
            await pg.screenshot(path=B+'lfx_%s.png'%n)
        await shot('idle',"()=>{const G=__G,e=G.boss;e.st='glide';e.stT=99;e.an='';G.P.x=e.x+30;G.P.y=e.y+400}",8)
        await shot('cast',"()=>{const G=__G,e=G.boss;e.an='cast';e.anT=0.8}",1)
        await shot('fan',"()=>{const G=__G,e=G.boss;e.an='fan';e.anT=G.LS.fWarn+0.25}",1)
        await shot('mirror',"()=>{const G=__G,e=G.boss,P=G.P;e.an='';G.rd;const AI=G.ls;AI.mirror&&AI.mirror()}",40)
        await shot('death',"()=>{const G=__G,e=G.boss;G.LSW.death={x:e.x,y:e.y,t:1.2,face:1}}",1)
        print('errs',errs[:5]); await b.close()
asyncio.run(main())
