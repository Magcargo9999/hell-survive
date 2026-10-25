"""v9.23 릴세르카 이펙트 도트 — 결정화 영역 · 샹들리에 · 스포트라이트 · 시선 · 바늘 · 무도회 바닥 · 금 가는 효과 스크린샷 + 콘솔 오류"""
import asyncio,sys,json
sys.path.insert(0,'/home/claude/hell-survive/tools')
from playwright.async_api import async_playwright
import h301
B='/home/claude/hell-survive/build/'
async def main():
    async with async_playwright() as pw:
        b=await pw.chromium.launch(); pg=await h301.newpage(b,1280,720); errs=[]
        pg.on('pageerror',lambda e:errs.append(str(e))); pg.on('console',lambda m:errs.append(m.text) if m.type=='error' else None)
        await pg.wait_for_function('__G.IMG&&__G.IMG.ifloor&&__G.IMG.lil&&__G.IMG.lfx',timeout=90000)
        print(await pg.evaluate("""()=>{const G=__G;G.SAVE.diff.max=24;G.SAVE.diff.sel=24;G.SAVE.shards=1e7;G.startGame('archer');const P=G.P;__lv(28);G.raiseCastle();G.enterArena();
          for(let i=0;i<40;i++)G.tick(1/30);__s();const e=G.boss,AI=G.ls;for(const k in AI.cd)AI.cd[k]=99;e.st='glide';e.stT=99;
          for(let i=0;i<330;i++){P.hp=P.max;P.inv=1;P.stunT=0;e.x=G.IMAP.cx;e.y=G.IMAP.cy;P.x=e.x+120;P.y=e.y+250;G.tick(1/30)}return e.bk}"""))
        async def shot(n,js=None,steps=3):
            if js: await pg.evaluate(js)
            for i in range(steps): await pg.evaluate("()=>{const G=__G,P=G.P,e=G.boss;P.hp=P.max;P.inv=1;P.stunT=0;G.tick(1/30)}")
            await pg.screenshot(path=B+'lf3_%s.png'%n)
        await shot('zone',"()=>{const G=__G,P=G.P,e=G.boss;G.LSW.frost=70;P.x=e.x+160;P.y=e.y+250}",2)
        await shot('chand',"()=>{const G=__G,P=G.P,e=G.boss;G.LSW.chand=[{x:e.x-300,y:e.y+200,t:0.9,done:false},{x:e.x+250,y:e.y+120,t:1.25,done:false}]}",2)
        await shot('chand2',None,10)
        await shot('gaze',"()=>{const G=__G,P=G.P,e=G.boss;G.LSW.gz=[{t:0.3,bx:e.x,by:e.y-150,px:P.x,py:P.y}]}",1)
        await shot('needle',"()=>{const G=__G,P=G.P,e=G.boss;for(let i=0;i<5;i++){G.LSW.bolts.push({x:e.x-100+i*60,y:e.y-50,vx:20,vy:80,a:0,dm:0,k:i%2?'refl':'needle',life:3})}}",1)
        await shot('spot',"()=>{const G=__G,P=G.P,e=G.boss;G.ls.waltzStart();P.x=G.LSW.spot.x;P.y=G.LSW.spot.y;}",50)
        await shot('crack',"()=>{const G=__G;G.LSW.white=0.9;G.LSW.crack=0.9}",1)
        print('errs',errs[:5]); await b.close()
asyncio.run(main())
