"""마계 물고기(fish) 기본 로직 확인 — 잠금 상태 · 오라 피해 · 카드 · 오류 없음. 사용: PYTHONPATH=tools python3 tools/tests/fish.py [스크린샷 폴더]"""
import asyncio, sys, os
from h301 import *
from playwright.async_api import async_playwright
OUT = sys.argv[1] if len(sys.argv) > 1 else None
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); pg = await newpage(b, 1280, 720)
        print('잠금:', await pg.evaluate("()=>[__G.SAVE.chars.fish, !!document.querySelector('#charCards .card[data-c=fish].locked')]"))
        if OUT:
            await pg.evaluate("()=>{document.querySelector('#charCards').scrollIntoView()}"); await pg.screenshot(path=OUT + '/f01_menu.png')
            await pg.click('#charCards .card[data-c=fish]'); await pg.wait_for_timeout(200); await pg.screenshot(path=OUT + '/f02_locked.png')
            await pg.click('#routeClose')
        await pg.evaluate("()=>{__G.SAVE.chars.fish=true}")
        await pg.evaluate("()=>{__G.startGame('fish')}"); await pg.wait_for_timeout(300)
        print('시작:', await pg.evaluate("()=>[__G.P.char, __G.P.dmg, __G.P.rng, __G.P.cd]"))
        await pg.evaluate("()=>{__run(40)}")
        r = await pg.evaluate("""()=>{const G=__G,P=G.P;G.enemies.length=0;
          for(let i=0;i<5;i++){const e=G.spawnEnemy(i*1.2,90);e.hp=e.max=1e6;} 
          for(let i=0;i<3;i++){const e=G.spawnEnemy(i*2,600);e.hp=e.max=1e6;}
          const near=G.enemies.slice(0,5), far=G.enemies.slice(5);
          const R0=G.fishR(); G.tick(1/30); for(let i=0;i<60;i++){P.inv=99;G.tick(1/30)}
          const dn=near.map(e=>Math.round(e.max-e.hp)), df=far.map(e=>Math.round(e.max-e.hp));
          return {R0, dn, df, dm:JSON.stringify(G.DMETER)}}""")
        print('오라:', r)
        if OUT:
            await pg.screenshot(path=OUT + '/f03_aura.png')
        # 카드: 넓은 오라 → 반경
        print('카드:', await pg.evaluate("""()=>{const G=__G,P=G.P;const R=G.fishR();const u=G.UPGRADES.find(x=>x.id==='range');u.apply(P);return [R,G.fishR(),G.cards? 1:0]}"""))
        print('풀:', await pg.evaluate("()=>{const G=__G;return G.rollCards?G.rollCards(40,[]).map(c=>c.id).filter((v,i,a)=>a.indexOf(v)===i).join(','):'n/a'}"))
        await pg.evaluate("()=>{__run(1);__G.addExp(__G.P.need)}"); await pg.wait_for_timeout(300)
        if OUT: await pg.screenshot(path=OUT + '/f04_levelup.png')
        await pg.evaluate("()=>{__lv(25)}"); await pg.evaluate("()=>{__run(120)}")
        print('Lv25 상태:', await pg.evaluate("()=>[__G.state, __G.P.lvl, __G.P.form]"))
        print('오류:', pg.errs)
        await b.close()
asyncio.run(main())
