"""v6.40 악마 총잡이 자동 테스트: PYTHONPATH=tools python3 tools/tests/gun.py  (스크린샷: build/shots/gun_*.png)
탄창 6발 · 재장전 · 탄 4종 확률/피해 · 도탄 튕김 · 불씨 화상 · 고유 카드 4장 · 진화 · 최종 스킬 구르기 · 해금 조건"""
import asyncio, os, json
from playwright.async_api import async_playwright
from h301 import newpage, ROOT
OUT = os.path.join(ROOT, 'build', 'shots'); os.makedirs(OUT, exist_ok=True)
async def shot(pg, n, clip=None):
    await pg.evaluate('__G.render()'); await pg.screenshot(path=os.path.join(OUT, f'gun_{n}.png'), clip=clip)
CL = {'x': 440, 'y': 170, 'width': 400, 'height': 300}
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--disable-gpu'])
        pg = await newpage(b, 1280, 720)
        pg.on('console', lambda m: pg.errs.append('console: ' + m.text) if m.type == 'error' else None)
        R = {}
        R['locked'] = await pg.evaluate("()=>{const G=__G;G.SAVE.chars.gun=false;G.SAVE.ch.open=false;G.SAVE.fw.snap=null;G.buildCards();return {gun:G.SAVE.chars.gun,txt:[...document.querySelectorAll('#charCards .card b')].map(x=>x.textContent).filter(t=>t.includes('총잡이'))}}")
        R['prob'] = await pg.evaluate("""()=>{const G=__G;G.SAVE.chars.gun=true;G.SAVE.set.speed=0;G.startGame('gun');const P=G.P,c={N:0,R:0,F:0,B:0};for(let i=0;i<4000;i++){G.gunLoad();for(const k of P.mag)c[k]++;}
          P.up.gEmber=3;const c2={N:0,R:0,F:0,B:0};for(let i=0;i<4000;i++){G.gunLoad();for(const k of P.mag)c2[k]++;}P.up.gEmber=0;G.gunLoad();
          const f=o=>Object.fromEntries(Object.entries(o).map(([k,v])=>[k,+(v/240).toFixed(1)]));return {base:f(c),ember3:f(c2),hp:P.max,spd:P.spd,dmg:P.dmg,range:Math.round(G.gunRange())}}""")
        # 탄창: 6발 쏘면 재장전 1초 (빠른 장전 카드 3장이면 0.55초)
        R['mag'] = await pg.evaluate("""()=>{const G=__G,P=G.P;G.enemies.length=0;G.spawnEnemy(0,200);const e=G.enemies[0];e.hp=e.max=1e7;let shots=0,first=-1,reloadAt=-1;const t0=G.gt;
          for(let i=0;i<150;i++){P.inv=99;P.hp=P.max;e.x=P.x+220;e.y=P.y;const n=P.magI;G.tick(1/30);if(P.magI!==n&&P.magI>n)shots++;if(P.reloadT>0&&reloadAt<0)reloadAt=+(G.gt-t0).toFixed(2);}
          return {shots,reloadAt,magI:P.magI,reloadT:+P.reloadT.toFixed(2)}}""")
        await shot(pg, '0_shoot', CL)
        R['reload'] = await pg.evaluate("""()=>{const G=__G,P=G.P;const r=[];for(const n of [0,1,3]){P.up.gReload=n;r.push(+(G.GUN.reload*(1-0.15*n)).toFixed(2));}P.up.gReload=0;return r}""")
        # 탄 피해: 일반 100% · 불씨 200% + 관통 + 화상 · 공포 10% · 도탄은 다른 적에게 튕긴다
        R['ammo'] = await pg.evaluate("""()=>{const G=__G,P=G.P,o={};P.crit=0;
          for(const k of ['N','F','B','R']){G.enemies.length=0;G.shards.length=0;for(let j=0;j<3;j++){G.spawnEnemy(0,300);const e=G.enemies[j];e.hp=e.max=1e6;e.x=P.x+180+j*70;e.y=P.y-0;e.sp=0;e.noKB=true;}
            P.mag=[k,k,k,k,k,k];P.magI=0;P.reloadT=0;const E=G.enemies.slice();if(k==='R'){E[1].y=P.y+200;E[1].x=P.x+260;E[2].y=P.y-220;E[2].x=P.x+300;}
            P.atkCd=0;let n=0;for(let i=0;i<40&&n<1;i++){P.inv=99;const m=P.magI;G.tick(1/30);if(P.magI>m){n++;}}for(let i=0;i<30;i++){P.atkCd=9;P.inv=99;G.tick(1/30);}
            o[k]={hits:E.map(e=>Math.round(1e6-e.hp)),burn:E.map(e=>+(e.burnT||0).toFixed(1)),dmg:Math.round(P.dmg)};}
          return o}""")
        # 도탄: 화면 끝에서 튕긴다
        R['edge'] = await pg.evaluate("""()=>{const G=__G,P=G.P;G.enemies.length=0;G.shards.length=0;P.mag=['R','R','R','R','R','R'];P.magI=0;
          G.shards.push({src:'g:R',x:G.P.x+G.W/2-30,y:G.P.y,vx:900,vy:0,life:2,pierce:4,hit:new Set(),dmg:1,gun:'R',kb:1,sz:1,eb:0});const s=G.shards[G.shards.length-1];
          for(let i=0;i<6;i++){P.atkCd=9;G.tick(1/30);}return {vx:Math.round(s.vx),eb:s.eb}}""")
        # 현상금 사냥: 처치마다 이속 중첩
        R['bounty'] = await pg.evaluate("""()=>{const G=__G,P=G.P;P.up.gBounty=2;G.enemies.length=0;for(let j=0;j<8;j++){G.spawnEnemy(0,100);}const s0=P.spd;
          for(const e of G.enemies){e.hp=1;G.hurtEnemy(e,10,0,0,0);}const n=P.bountyN,t=P.bountyT;for(let i=0;i<60;i++){P.atkCd=9;G.tick(1/30);}return {stacks:n,t:+t.toFixed(1),after:P.bountyN,max:1+2*2}}""")
        # 카드 이름 (고유 4장 + 공용 이름)
        R['cards'] = await pg.evaluate("()=>{const G=__G;return ['gReload','gSpec','gEmber','gBounty','claw','speed','range'].map(id=>{const u=G.choices;return id})}")
        R['cardNames'] = await pg.evaluate("()=>{const G=__G,c=[];for(let i=0;i<40;i++){G.P.lvl=5;G.addExp(G.P.need);if(G.state==='levelup'){c.push(...G.choices.map(u=>u.name));G.pick(0);}}return [...new Set(c)]}")
        # 진화 Lv.10 · Lv.20 + 스킬
        await pg.evaluate("()=>{const G=__G;G.enemies.length=0;G.shards.length=0;__lv(10);__run(30)}")
        R['evo1'] = await pg.evaluate("()=>{const P=__G.P;return {form:P.form,skill:P.skill,max:P.max,dmg:Math.round(P.dmg),spd:Math.round(P.spd)}}")
        await pg.evaluate("()=>{const G=__G;G.enemies.length=0;G.P.reloadT=0.6;G.P.reloadMax=1;G.P.magI=6;for(let i=0;i<8;i++){G.P.inv=99;G.P.atkCd=9;G.tick(1/30)}}"); await shot(pg, '1_reload', CL)
        await pg.evaluate("()=>{const G=__G;__lv(20);__run(30)}")
        R['evo2'] = await pg.evaluate("()=>{const P=__G.P;return {form:P.form,skill:P.skill,max:P.max,dmg:Math.round(P.dmg),spd:Math.round(P.spd)}}")
        # 구르기: 3회 · 첫 번째에 남은 탄 전부 발사 + 재장전 · 시간 지나면 증발
        R['roll'] = await pg.evaluate("""()=>{const G=__G,P=G.P;G.enemies.length=0;G.shards.length=0;for(let j=0;j<5;j++){G.spawnEnemy(j,260);const e=G.enemies[j];e.hp=e.max=1e6;e.sp=0;}
          P.mag=['N','R','F','N','B','N'];P.magI=2;P.reloadT=0;P.skT=0;const x0=P.x;G.cast();const dumped=G.shards.filter(s=>s.src==='sk:roll').length;const q=G.rollQ;const r1={n:q.n,reload:+P.reloadT.toFixed(2),dumped};
          for(let i=0;i<12;i++){G.tick(1/30);}const d1=Math.round(Math.abs(P.x-x0));G.cast();for(let i=0;i<12;i++)G.tick(1/30);G.cast();const n3=G.rollQ?G.rollQ.n:'end';for(let i=0;i<12;i++)G.tick(1/30);
          const after3=!!G.rollQ;G.cast();const blockCd=+P.skT.toFixed(1);
          P.skT=0;G.cast();for(let i=0;i<140;i++)G.tick(1/30);const expired=!G.rollQ;return {r1,d1,n3,after3,blockCd,expired}}""")
        await pg.evaluate("()=>{const G=__G,P=G.P;G.enemies.length=0;P.skT=0;G.cast();for(let i=0;i<3;i++)G.tick(1/30)}"); await shot(pg, '2_roll', CL)
        await pg.evaluate("()=>{const G=__G;for(let i=0;i<150;i++)G.tick(1/30);G.enemies.length=0;for(let j=0;j<6;j++)G.spawnEnemy(j,240);G.P.reloadT=0;G.gunLoad();for(let i=0;i<9;i++){G.P.inv=99;G.tick(1/30)}}"); await shot(pg, '3_final_shoot', CL)
        R['dm'] = await pg.evaluate("()=>Object.keys(__G.DMETER).map(k=>__G.dmName(k))")
        # 해금: 지하 6층 마왕 처치
        R['unlock'] = await pg.evaluate("""()=>{const G=__G;G.SAVE.chars.gun=false;G.SAVE.ch.open=false;G.SAVE.fw.snap=null;G.SAVE.diff.max=5;G.SAVE.shards=999;G.SAVE.diff.sel=4;G.startGame('wolf');G.bossDefeated.call?0:0;
          G.enemies.length=0;G.raiseCastle();G.enterArena();for(let i=0;i<40;i++)G.tick(1/30);G.hurtEnemy(G.boss,1e9,0,0,0);const t4=G.SAVE.chars.gun;
          G.SAVE.diff.sel=5;G.startGame('wolf');G.enemies.length=0;G.raiseCastle();G.enterArena();for(let i=0;i<40;i++)G.tick(1/30);G.boss.invul=false;G.boss.shield=false;G.hurtEnemy(G.boss,1e9,0,0,0);return {after4:t4,after6:G.SAVE.chars.gun}}""")
        R['errs'] = pg.errs[:6]
        print(json.dumps(R, ensure_ascii=False, indent=1)); await b.close()
asyncio.run(main())
