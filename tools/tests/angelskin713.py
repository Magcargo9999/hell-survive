"""v7.13 쿠폰 타락천사 여자 스킨 스크린샷  PYTHONPATH=tools python3 tools/tests/angelskin713.py"""
import asyncio, os
from playwright.async_api import async_playwright
from h301 import newpage, ROOT
OUT = os.path.join(ROOT, 'build', 'shots')
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--disable-gpu']); pg = await newpage(b, 1280, 720)
        await pg.wait_for_function('window.__G && __G.IMG.an2', timeout=60000)
        for sk in [False, True]:
            await pg.evaluate("""(sk)=>{const G=__G;G.setAngelSkin(sk);G.SAVE.diff.max=5;G.SAVE.shards=999;G.SAVE.diff.sel=4;G.startGame('wolf');const P=G.P;P.bossK='angel';__lv(25);G.enemies.length=0;G.raiseCastle();G.enterArena();
              for(let i=0;i<150;i++){P.inv=99;P.hp=P.max;G.tick(1/30);if(G.state!=='play')__s();} const b=G.boss;P.x=b.x;P.y=b.y+150;b.y=P.y-170;b.st='idle';for(let i=0;i<10;i++){P.inv=99;G.tick(1/30);} G.render();}""", sk)
            await pg.screenshot(path=os.path.join(OUT, f'angel_skin_{int(sk)}.png'))
        await pg.evaluate("""()=>{const G=__G;const b=G.boss;G.P.x=b.x;G.P.y=b.y+150;b.y=G.P.y-170;b.hp=b.max*0.69;for(let i=0;i<120;i++){G.P.inv=99;G.tick(1/30);} G.render();}""")
        await pg.screenshot(path=os.path.join(OUT, 'angel_skin_trans.png'))
        await pg.evaluate("()=>{const G=__G;G.hurtEnemy(G.boss,1e12,1,0,0);for(let i=0;i<60;i++){G.P.inv=99;G.tick(1/30);}G.render();}")
        await pg.screenshot(path=os.path.join(OUT, 'angel_skin_death.png')); print('errs', pg.errs); await b.close()
asyncio.run(main())
