"""v9.49 마계 물고기 진화 확인 — 마계 미꾸라지(물방울) · 공허의 마해룡(절대 수압 3구역 · 포식자의 파도) · 도감 · 오류.
사용: GAME_URL=http://localhost:8765/index.html PYTHONPATH=tools python3 tools/tests/fish949.py [스크린샷 폴더]"""
import asyncio, sys
from h301 import *
from playwright.async_api import async_playwright
OUT = sys.argv[1] if len(sys.argv) > 1 else None
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); pg = await newpage(b, 1280, 720)
        print('상점:', await pg.evaluate("()=>[__G.CHARS? __G.CHARS.fish.price : 'n/a', __G.SAVE.chars.fish]"))
        await pg.evaluate("()=>{__G.SAVE.chars.fish=true; __G.startGame('fish')}"); await pg.wait_for_timeout(1500)
        await pg.evaluate("()=>{__lv(10); __run(70)}")
        r = await pg.evaluate("""()=>{const G=__G,P=G.P;G.enemies.length=0;G.shards.length=0;
          const e=G.spawnEnemy(0,300); e.hp=e.max=1e6; let n=0; for(let i=0;i<90;i++){P.inv=99;G.tick(1/30); n=Math.max(n,G.shards.filter(s=>s.fsh).length)}
          return {form:P.form, name:G.FD().name, R:Math.round(G.fishR()), orbs:n, dmg:Math.round(e.max-e.hp)}}""")
        print('1진화:', r)
        if OUT:
            await pg.evaluate("()=>{const G=__G;for(let i=0;i<6;i++){const e=G.spawnEnemy(i,260);e.hp=e.max=1e6;} __run(20)}")
            await pg.screenshot(path=OUT + '/fish1.png')
        await pg.evaluate("()=>{__lv(20); __run(40)}")
        r = await pg.evaluate("""()=>{const G=__G,P=G.P;return {form:P.form, name:G.FD().name, skill:P.skill, R:Math.round(G.fishR()), state:G.state}}""")
        print('최종:', r)
        r = await pg.evaluate("""()=>{const G=__G,P=G.P;G.enemies.length=0;G.shards.length=0;const R=G.fishR();
          const mk=(d)=>{const e=G.spawnEnemy(0,d);e.x=P.x+d;e.y=P.y;e.hp=e.max=1e7;e.spd=0;e.vx=e.vy=0;return e};
          const a=mk(R*0.15), b=mk(R*0.5), c=mk(R*0.85); const cx=c.x;
          P.fishT=0; P.fishOrbT=99; G.tick(1/30); P.fishOrbT=99;
          return {inner:Math.round(a.max-a.hp), mid:Math.round(b.max-b.hp), outer:Math.round(c.max-c.hp), pushed:Math.round(c.x-cx)}}""")
        print('절대 수압 (안·중·밖 피해, 밀림):', r)
        r = await pg.evaluate("""()=>{const G=__G,P=G.P;G.enemies.length=0;G.shards.length=0;P.skT=0;
          const x0=P.x,y0=P.y; P.lastX=1;P.lastY=0; const es=[]; for(let i=1;i<=6;i++){const e=G.spawnEnemy(0,100);e.x=x0+i*100;e.y=y0+(i%2?30:-30);e.hp=e.max=1e7;e.spd=0;es.push(e)}
          const off=G.spawnEnemy(0,100); off.x=x0+300; off.y=y0+400; off.hp=off.max=1e7; off.spd=0;
          G.castSkill(); let inv=1; for(let i=0;i<30;i++){G.tick(1/30); if(!(P.inv>0)) inv=0}
          return {moved:Math.round(P.x-x0), dy:Math.round(P.y-y0), hit:es.filter(e=>e.hp<e.max).length, offHit:off.hp<off.max, per:Math.round((es[0].max-es[0].hp)/P.dmg*100)+'%', inv, cd:P.skT.toFixed(1), dm:Object.keys(G.DMETER).map(k=>G.dmName(k)).join('/')}}""")
        print('포식자의 파도:', r)
        if OUT:
            await pg.evaluate("()=>{const G=__G,P=G.P;for(let i=0;i<10;i++){const e=G.spawnEnemy(i*0.6,180+i*10);e.hp=e.max=1e6;} __run(30)}")
            await pg.screenshot(path=OUT + '/fish2_aura.png')
            await pg.evaluate("()=>{const G=__G,P=G.P;P.skT=0;P.lastX=0.7;P.lastY=-0.7;G.castSkill();for(let i=0;i<8;i++)G.tick(1/30)}")
            await pg.screenshot(path=OUT + '/fish2_wave.png')
            await pg.evaluate("()=>{const G=__G,P=G.P;__run(30);P.skT=0;P.lastX=-1;P.lastY=0.2;G.castSkill();for(let i=0;i<9;i++)G.tick(1/30)}")
            await pg.screenshot(path=OUT + '/fish2_wave_l.png')
        # 보스방 끝에서 멈춤
        r = await pg.evaluate("""()=>{const G=__G,P=G.P; __run(30); try{G.enterArena()}catch(e){return 'arena err '+e} for(let i=0;i<60;i++){P.inv=99;P.hp=P.max;G.tick(1/30)}
          P.skT=0; P.lastX=1; P.lastY=0; G.castSkill(); for(let i=0;i<40;i++){P.inv=99;P.hp=P.max;G.tick(1/30)} return {inPoly:G.inPoly? G.inPoly(P.x,P.y):'n/a', arena:!!G.arena}}""")
        print('보스방 파도:', r)
        print('도감:', await pg.evaluate("()=>{const s=__G.SAVE.dex.seen;return ['fish:0','fish:1','fish:2'].map(k=>!!s[k])}"))
        print('오류:', pg.errs)
        await b.close()
asyncio.run(main())
