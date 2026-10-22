"""v8.15 칠흑의 대궁(해골 궁수 스킬) · 해골 궁수 평타 넉백: 4발 · 몹이 많은 쪽 · 밀려난 거리 · 딜미터기 이름"""
import asyncio, os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from playwright.async_api import async_playwright
from h301 import newpage
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'build', 'shots')
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--disable-gpu']); pg = await newpage(b, 1280, 720)
        R = {}
        R['setup'] = await pg.evaluate("""()=>{const G=__G;G.startGame('archer');const P=G.P;__lv(9);P.route='skel';P.form=1;__lv(12);
          P.route='skel';P.form=1;P.hp=P.max;return {skills:G.uniqueSkills(),name:G.skillName(G.uniqueSkills()[0]),route:P.route}}""")
        R['cast'] = await pg.evaluate("""()=>{const G=__G,P=G.P;G.enemies.length=0;P.skill='darkarrow';P.x=0;P.y=0;P.face=1;
          // 오른쪽에 12마리 뭉쳐 두고 왼쪽에 2마리
          for(let i=0;i<12;i++){G.spawnEnemy(0,300+(i%4)*40);}
          const es=G.enemies.slice(); es.forEach((e,i)=>{e.x=320+(i%4)*45;e.y=-60+Math.floor(i/4)*60;e.vx=e.vy=0;e.hp=e.max=9999;e.kx=e.ky=0;e.frz=0});
          const x0=es.map(e=>e.x);
          G.cast&&G.cast();
          let shots=0,seen=0;for(let i=0;i<90;i++){P.inv=99;G.tick(1/30);}
          const moved=es.map((e,i)=>e.x-x0[i]);
          return {dir:'right', avgMove:Math.round(moved.reduce((a,b)=>a+b,0)/moved.length), maxMove:Math.round(Math.max(...moved)), dealt:Math.round(es.reduce((a,e)=>a+(e.max-e.hp),0)/es.length), dm:Object.keys(G.DMETER)};}""")
        R['dmname'] = await pg.evaluate("()=>Object.keys(__G.DMETER).map(k=>__G.dmName?__G.dmName(k):k)")
        await pg.wait_for_timeout(100); await pg.screenshot(path=os.path.join(OUT,'darkarrow815.png'))
        print(R); await b.close()
asyncio.run(main())
