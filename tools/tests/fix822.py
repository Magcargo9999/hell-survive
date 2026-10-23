"""v8.22 버그 6건 확인"""
import asyncio, sys
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as pw:
        b=await pw.chromium.launch(); pg=await b.new_page(viewport={'width':900,'height':600}); errs=[]
        pg.on('pageerror',lambda e:errs.append(str(e)))
        await pg.goto('file:///home/claude/hell-survive/build/hell_survive.html'); await pg.wait_for_function('window.__G&&__G.ready',timeout=90000)
        r=await pg.evaluate('''()=>{const G=__G; Object.assign(G.SAVE.chars,{ghost:true,lizard:true}); G.SAVE.diff.max=5; G.SAVE.shards=99999; G.SAVE.diff.sel=0; G.startGame('ghost');
          const out={}; const P=G.P;
          // 3 정예 체력: 100번 뽑아 최대 체력 비교 (정예 강제)
          const orig=Math.random; let mx=0, mx2=0; G.setT(200);
          for(let i=0;i<300;i++){ const q=G.shkAdd({},0,0); mx=Math.max(mx,q.max); const q2=G.toxAdd(0,0); mx2=Math.max(mx2,q2.max); G.enemies.length=0; }
          out.shkMax=mx; out.toxMax=mx2; const base=G.spawnEnemy(0,10); out.baseHp=base.max; out.baseElite=base.elite;
          // 6 딜미터
          for(const k of Object.keys(G.DMETER)) delete G.DMETER[k];
          G.enemies.length=0; const e=G.spawnEnemy(0,10); e.x=P.x+40; e.y=P.y; e.hp=e.max=1e6;
          P.rel.phoenix=true; P.phxUsed=false; G.phoenixRevive(); G.mirrorBlock(10); P.pals=[1,2]; G.palPop();
          P.shellT=5; P.inv=0; P.shield=0; G.hurt && G.hurt(20);
          out.dm=Object.fromEntries(Object.entries(G.DMETER).map(([k,v])=>[G.dmName(k),Math.round(v)]));
          return out}''')
        print(r); print('errs',errs)
        await b.close()
asyncio.run(main())
