"""v7.13 말 미니보스: 두 마리 모두 출현·공격 각각 실행·사망 처리 + 스크린샷  PYTHONPATH=tools python3 tools/tests/horse713.py"""
import asyncio, os, json
from playwright.async_api import async_playwright
from h301 import newpage, ROOT
OUT = os.path.join(ROOT, 'build', 'shots'); os.makedirs(OUT, exist_ok=True)
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--disable-gpu']); pg = await newpage(b, 1280, 720)
        await pg.wait_for_function('window.__G && __G.IMG.horse', timeout=60000)
        for bk in ['rig', 'nerk']:
            R = await pg.evaluate("""(bk)=>{const G=__G;G.startGame('wolf');const P=G.P;__lv(12);G.enemies.length=0;G.spawnHorse(bk);const m=G.mini;m.x=P.x+330;m.y=P.y;
              const seen={},ks=bk==='rig'?['rdash','rslash','rcurse']:['nsum','nspike','nhowl'];let hits=0,h0=P.hp;
              for(const k of ks){ m.st='chase';m.cd=99;G.hAtk(m,k); for(let i=0;i<90;i++){P.inv=0;G.tick(1/30);if(G.state!=='play')__s(); if(m.st==='atk'&&m.at)seen[k]=(seen[k]||0)+1; if(i===25)window['__snap'+k]=1;} m.x=P.x+330;m.y=P.y;m.at=null;m.st='chase'; }
              m.hp=1; const hp=P.hp; G.hurtEnemy(m,1e9,1,0,0); for(let i=0;i<60;i++){P.inv=99;G.tick(1/30);}
              return {seen,lost:Math.round(h0-hp),dead:!G.mini,state:G.state,ebul:G.ebul.length}}""", bk)
            print(bk, json.dumps(R))
        await pg.evaluate("""()=>{const G=__G;G.startGame('wolf');const P=G.P;G.enemies.length=0;G.spawnHorse('rig');G.mini.x=P.x+260;G.mini.y=P.y;G.hAtk(G.mini,'rcurse');for(let i=0;i<20;i++){P.inv=99;G.tick(1/30);}G.render()}""")
        await pg.screenshot(path=os.path.join(OUT, 'horse_rig.png'))
        await pg.evaluate("""()=>{const G=__G;G.startGame('wolf');const P=G.P;G.enemies.length=0;G.spawnHorse('nerk');G.mini.x=P.x+260;G.mini.y=P.y;G.hAtk(G.mini,'nspike');for(let i=0;i<20;i++){P.inv=99;G.tick(1/30);}G.render()}""")
        await pg.screenshot(path=os.path.join(OUT, 'horse_nerk.png'))
        print('errs', pg.errs); await b.close()
asyncio.run(main())
