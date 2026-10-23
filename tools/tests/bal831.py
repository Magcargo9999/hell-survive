"""v8.31 밸런스: 문어 구슬(마왕 반복 타격) · 총잡이 구르기 6발 · 사슬 휘두르기 직접 피해 · 챌린지 비례 피해"""
import asyncio,sys
sys.path.insert(0,'/home/claude/hell-survive/tools')
from playwright.async_api import async_playwright
import h301
h301.URL='file:///home/claude/hell-survive/build/hell_survive.html'
async def main():
    async with async_playwright() as pw:
        b=await pw.chromium.launch(); pg=await h301.newpage(b)
        # 문어: 구슬 3개, 가까운 유니크/미니를 계속 맞히는지
        r=await pg.evaluate("""()=>{const G=__G;G.startGame('octo');const P=G.P;P.orbsN=4;P.orbR=60;
          G.spawnMini();const m=G.mini;m.x=P.x+60;m.y=P.y;m.hp=m.max=1e7;m.invul=false;m.sp=0;
          let h0=m.hp;for(let i=0;i<120;i++){P.inv=99;P.hp=P.max;m.x=P.x+60;m.y=P.y;m.kx=m.ky=0;G.tick(1/30)}return [h0-m.hp, G.DMETER.orb||0]}""")
        print('octo orb dmg on mini', r)
        # 총잡이
        r=await pg.evaluate("""()=>{const G=__G;G.SAVE.diff.max=0;G.SAVE.chars.gun=true;G.startGame('gun');const P=G.P;P.form=2;G.gunLoad();P.reloadT=0.5;P.magI=6;
          G.DMETER={};for(let i=0;i<6;i++){G.enemies.push({kind:'x',x:P.x+150,y:P.y,kx:0,ky:0,sp:0,r:20,hp:1e6,max:1e6,dmg:0,exp:0,flash:0,t:0,orbCd:0,slowT:0,noKB:true,face:1})}
          G.gunRollStart();const q0=G.gunDq&&G.gunDq.list.length;for(let i=0;i<40;i++){P.inv=99;G.tick(1/30)}
          const d=G.enemies.reduce((a,e)=>a+(1e6-e.hp),0);return [q0,d>0,G.DMETER['sk:roll']]}""")
        print('gun roll', r)
        # 사슬 악마
        r=await pg.evaluate("""()=>{const G=__G;G.startGame('twins');const P=G.P;P.form=2;P.skill='whip';
          const e={kind:'x',x:P.x+120,y:P.y,kx:0,ky:0,sp:0,r:20,hp:1e7,max:1e7,dmg:0,exp:0,flash:0,t:0,orbCd:0,slowT:0,noKB:true,face:1};G.enemies.push(e);
          G.startWhip();for(let i=0;i<60;i++){P.inv=99;e.x=P.x+120;e.y=P.y;G.tick(1/30)}return [1e7-e.hp, 'pct≈',1e7*0.01*6, 'P.dmg',P.dmg]}""")
        print('whip', r)
        print(await pg.evaluate("(()=>{const G=__G;G.startGame('lizard');G.P.max=1000;return [G.chPct()]})()"))
        print('errs',pg.errs[:5]); await b.close()
asyncio.run(main())
