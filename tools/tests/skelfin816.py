"""v8.16 해골 궁수 최종 진화형: Lv.20 진화(형태 2) · 새 도트 · 칠흑의 대궁 새 화살 · 스킬 선택"""
import asyncio, os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from playwright.async_api import async_playwright
from h301 import newpage
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'build', 'shots'); os.makedirs(OUT, exist_ok=True)
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--disable-gpu']); pg = await newpage(b, 1280, 720)
        errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
        R = {}
        R['setup'] = await pg.evaluate("""async()=>{const G=__G;G.startGame('archer');const P=G.P;__lv(9);P.route='skel';P.form=1;P.hp=P.max;
          await new Promise(r=>setTimeout(r,1500));  // lazy 그림
          __lv(19);P.route='skel';P.form=1;return {lvl:P.lvl,form:P.form}}""")
        R['evo'] = await pg.evaluate("""()=>{const G=__G,P=G.P;G.addExp(P.need-P.exp+1);for(let i=0;i<260;i++){P.inv=99;G.tick(1/30);}
          return {lvl:P.lvl,form:P.form,src:G.FD&&G.FD().src,name:G.FD&&G.FD().name,skillChoice:!!document.querySelector('.ultc')}}""")
        R['img'] = await pg.evaluate("()=>({skelF:!!__G.IMG&&!!__G.IMG.skelF,a:!!__G.IMG&&!!__G.IMG.skelFa})")
        print(R)
        await pg.screenshot(path=os.path.join(OUT,'skelfin816_choice.png'))
        R['pick'] = await pg.evaluate("""()=>{const b=[...document.querySelectorAll('button')].find(x=>x.textContent.includes('선택 [1]'));if(b)b.click();return __G.P.skill}""")
        for _ in range(25):
            await pg.evaluate("()=>{const b=[...document.querySelectorAll('button')].find(x=>x.textContent.includes('선택 [1]'));if(b)b.click()}"); await pg.wait_for_timeout(60)
        R['cast'] = await pg.evaluate("""()=>{const G=__G,P=G.P;G.enemies.length=0;P.skill='darkarrow';P.x=0;P.y=0;P.face=1;
          for(let i=0;i<10;i++){G.spawnEnemy(0,300+(i%4)*40);}
          G.enemies.forEach((e,i)=>{e.x=330+(i%4)*45;e.y=-60+Math.floor(i/4)*60;e.vx=e.vy=0;e.hp=e.max=9999});
          P.skT=0;G.cast();for(let i=0;i<9;i++){P.inv=99;G.tick(1/30);}return {anim:P.anim,form:P.form}}""")
        await pg.wait_for_timeout(50); await pg.screenshot(path=os.path.join(OUT,'skelfin816_cast.png'))
        for an in ['idle','walk','attack','hit','death']:
            await pg.evaluate("(an)=>{const G=__G,P=G.P;G.enemies.length=0;P.anim=an;P.animT=0.3;P.hp=P.max}", an)
        print(R, errs); await b.close()
asyncio.run(main())
