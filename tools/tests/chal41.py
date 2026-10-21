"""v6.41 챌린지 테스트: PYTHONPATH=tools python3 tools/tests/chal41.py  (마왕 필드전 · 시간 배율 · 룬 3개 · 황금 도망자)"""
import asyncio, os, json
from playwright.async_api import async_playwright
from h301 import newpage, ROOT
OUT = os.path.join(ROOT, 'build', 'shots'); os.makedirs(OUT, exist_ok=True)
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--disable-gpu'])
        pg = await newpage(b, 1280, 720)
        await pg.evaluate("""()=>{window.__clr=()=>{const G=__G;let g=0;while(g++<50&&((G.state==='levelup'&&!document.getElementById('levelTitle').textContent.includes('쉼터'))||G.state==='evolve')){if(!__s())break;}};
          window.__run=(n,inv)=>{const G=__G;for(let i=0;i<n;i++){__clr();if(inv!==false){G.P.inv=99;G.P.hp=G.P.max;}G.tick(1/30)}}}""")
        pg.on('console', lambda m: pg.errs.append('console: ' + m.text) if m.type == 'error' else None)
        R = {}
        await pg.evaluate("()=>{const G=__G;G.SAVE.ch.open=true;G.SAVE.ch.rune={};G.SAVE.ch.frag=0;G.SAVE.set.speed=0;G.setChMode(true);G.startGame('wolf');}")
        R['scale'] = await pg.evaluate("""()=>{const G=__G,o={};for(const m of [3,5,6,10,15,20,30,45,60]){G.setT(m*60);o[m]={hp:+G.chTime().toFixed(1),dm:+G.chDmgT().toFixed(2)}}G.setT(0);return o}""")
        R['rune'] = await pg.evaluate("()=>{const G=__G;G.chFrag(1,G.P.x,G.P.y);G.chFrag(1,G.P.x,G.P.y);const a=G.SAVE.ch.frag;G.chFrag(1,G.P.x,G.P.y);return {after2:a,after3:G.SAVE.ch.frag,runes:Object.values(G.SAVE.ch.rune).reduce((x,y)=>x+y,0)}}")
        await pg.evaluate("__run(300)")
        R['gold'] = await pg.evaluate("()=>{const G=__G;G.setT(900);G.chGoldSpawn();const e=G.chal.gold;return {hp:Math.round(e.max),gsp:Math.round(e.gsp),pspd:Math.round(G.P.spd),ratio:+(e.gsp/G.P.spd).toFixed(2)}}")
        await pg.evaluate("()=>{const G=__G;G.hurtEnemy(G.chal.gold,1e9);__run(5);while(__s());}")
        res = {}
        for k in ['monkey', 'eye', 'skel', 'fw']:
            r = await pg.evaluate("""async(k)=>{const G=__G,c=G.chal;c.ev=null;c.shelter=null;c.cyc=0;c.busyBoss=true;c.bossK=k;G.setT(1500);
               G.chEnterBoss(k);const b0=G.boss;const r={k,arena:!!G.arena,n0:G.enemies.length,d0:Math.round(Math.hypot(b0.x-G.P.x,b0.y-G.P.y)),inCh:G.inCh(b0.x,b0.y),hp:Math.round(b0.max)};
               const pats=new Set();let out=0,hurt=0;for(let i=0;i<120;i++){__run(30);const b=G.boss;if(b){pats.add(b.last||b.st);if(!G.inCh(b.x,b.y))out++;}}
               r.pats=[...pats].sort();r.out=out;r.spawned=G.enemies.filter(e=>e.kind!=='boss'&&e.kind!=='skh'&&e.kind!=='skm').length;
               r.spawnedTotal=G.enemies.length;
               // 전투 중 플레이어가 실제로 피해를 입는지 (무적 끔)
               const h0=G.P.hp;for(let i=0;i<60;i++){__clr();G.P.inv=0;G.tick(1/30)}r.hurt=Math.round(h0-G.P.hp);
               return r}""", k)
            await pg.evaluate("__G.render()"); await pg.screenshot(path=os.path.join(OUT, f'c41_{k}.png'))
            r['alive'] = await pg.evaluate("()=>!!__G.boss&&__G.boss.hp>0")
            await pg.evaluate("()=>{const G=__G;if(G.boss){G.boss.invul=false;G.boss.shield=false;G.hurtEnemy(G.boss,1e9);}__run(200);}")
            r['shelter'] = await pg.evaluate("()=>!!__G.chal.shelter||document.getElementById('levelTitle').textContent.includes('쉼터')")
            await pg.evaluate("(i)=>{__G.pick(i);}", 0); await pg.evaluate("()=>{__G.chal.shelter=null;__run(10);while(__s());}")
            r['bossN'] = await pg.evaluate("__G.chal.bossN")
            res[k] = r
        R['boss'] = res; R['errs'] = pg.errs
        print(json.dumps(R, ensure_ascii=False, indent=1))
        await b.close()
asyncio.run(main())
