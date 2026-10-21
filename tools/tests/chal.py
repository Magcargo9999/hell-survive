"""v6.12 ∞ 챌린지 모드 자동 테스트: PYTHONPATH=tools python3 tools/tests/chal.py  (스크린샷: build/shots/chal_*.png)"""
import asyncio, os, json
from playwright.async_api import async_playwright
from h301 import newpage, ROOT
OUT = os.path.join(ROOT, 'build', 'shots'); os.makedirs(OUT, exist_ok=True)
async def shot(pg, n):
    await pg.evaluate('__G.render()'); await pg.screenshot(path=os.path.join(OUT, f'chal_{n}.png'))
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--disable-gpu'])
        pg = await newpage(b, 1280, 720)
        await pg.evaluate("""()=>{window.__clr=()=>{const G=__G;let g=0;while(g++<50&&((G.state==='levelup'&&!document.getElementById('levelTitle').textContent.includes('쉼터'))||G.state==='evolve')){if(!__s())break;}};
          window.__run=(n)=>{const G=__G;for(let i=0;i<n;i++){__clr();G.P.inv=99;G.P.hp=G.P.max;G.tick(1/30)}}}""")
        pg.on('console', lambda m: pg.errs.append('console: ' + m.text) if m.type == 'error' else None)
        R = {}
        # 잠김 → 해금
        R['locked'] = await pg.evaluate("()=>{const G=__G;G.SAVE.ch.open=false;G.SAVE.fw.snap=null;return document.getElementById('chBtn').textContent}")
        await pg.evaluate("()=>{const G=__G;G.SAVE.ch.open=true;G.SAVE.ch.rune={dmg:2,hp:1};G.SAVE.ch.frag=13;}")
        await pg.evaluate("()=>{document.getElementById('dexBtn').click();document.getElementById('dexClose').click();}")
        await pg.evaluate("()=>{const G=__G; G.setChMode(true); G.startGame('wolf');}")
        R['start'] = await pg.evaluate("()=>{const G=__G;return {chal:!!G.chal,x:Math.round(G.P.x),y:Math.round(G.P.y),tier:G.P.tier,inCh:G.inCh(G.P.x,G.P.y),dmg:+G.P.dmg.toFixed(2),max:G.P.max}}")
        await pg.evaluate("__run(600)")
        R['field'] = await pg.evaluate("()=>{const G=__G;const E=G.enemies.filter(e=>e.hp>0);return {n:E.length,out:E.filter(e=>!G.inCh(e.x,e.y)).length,cam:[Math.round(G.P.x),Math.round(G.P.y)]}}")
        await shot(pg, '1_field')
        # 벽으로 걸어가기: 맵 밖으로 못 나간다
        await pg.evaluate("()=>{const G=__G;G.P.x=G.CHM.cx;G.P.y=G.CHM.poly[2][1]+60;}")
        await pg.keyboard.down('KeyW'); await pg.evaluate("__run(120)"); await pg.keyboard.up('KeyW')
        R['wall'] = await pg.evaluate("()=>({in:__G.inCh(__G.P.x,__G.P.y),y:Math.round(__G.P.y),top:__G.CHM.poly[2][1]})")
        await shot(pg, '2_wall')
        # Lv.5 강적
        await pg.evaluate("()=>{const G=__G;G.P.x=G.CHM.start[0];G.P.y=G.CHM.start[1];__lv(5);__run(5)}")
        R['ev5'] = await pg.evaluate("()=>{const G=__G,c=G.chal;return {evK:c.evK,ev:c.ev?c.ev.map(e=>[e.kind,e.bk||e.uk,Math.round(e.max)]):null,next:c.next}}")
        await pg.evaluate("__run(240)")
        await shot(pg, '3_ev5')
        await pg.evaluate("()=>{const G=__G;for(const e of G.chal.ev||[]){e.invul=false;G.hurtEnemy(e,1e9)}__run(10)}")
        R['ev5done'] = await pg.evaluate("()=>({frag:__G.chal.frag,ev:__G.chal.ev,evN:__G.chal.evN,state:__G.state})")
        await pg.evaluate("()=>{while(__s());}")
        # 절단안의 짐승: 20초 동안 패턴
        await pg.evaluate("()=>{const G=__G;G.spawnCut();}")
        seen = set()
        for i in range(24):
            await pg.evaluate("__run(30)")
            st = await pg.evaluate("()=>{const m=__G.mini;return m?[m.st,m.at?m.at.k:'',__G.cutSaws.length]:null}")
            if st: seen.add(st[1])
            if i == 8: await shot(pg, '4_cut')
        R['cutPatterns'] = sorted(seen)
        await pg.evaluate("()=>{const G=__G;G.mini.rage=false;G.mini.hp=G.mini.max*0.3;__run(60)}")
        await shot(pg, '5_cut_rage')
        await pg.evaluate("()=>{const G=__G;G.hurtEnemy(G.mini,1e9);__run(20)}")
        await shot(pg, '5b_cut_death')
        R['cutDead'] = await pg.evaluate("()=>({mini:!!__G.mini,mdeath:!!__G.mdeath,dex:__G.SAVE.dex.kills.cut})")
        await pg.evaluate("()=>{while(__s());__run(60);while(__s());}")
        # 다른 이벤트 종류
        out = {}
        for k in ['m:monkey', 'm:eye', 'm:skel', 'h:octo', 'u:belia', 'u:celia']:
            r = await pg.evaluate("""(k)=>{const G=__G,c=G.chal;c.ev=null;c.busyBoss=false;c.shelter=null;c.lastEv='';
              const pool=k;let n=0;const orig=Math.random;  // 원하는 것이 뽑힐 때까지 이벤트를 다시 굴린다
              for(let i=0;i<60;i++){G.P.lvl=Math.max(G.P.lvl,5);c.next=5;c.lastEv='';G.chEvent(5);if(c.evK===k)break;for(const e of (c.ev||[])){e.hp=0;}c.ev=null;G.enemies.splice(0,G.enemies.length,...G.enemies.filter(e=>e.hp>0));}
              __run(90);const L=c.ev||[];const r={k:c.evK,n:L.length,hp:L.map(e=>Math.round(e.max)),in:L.every(e=>G.inCh(e.x,e.y))};
              for(const e of L){e.invul=false;G.hurtEnemy(e,1e9);} __run(10); while(__s()); r.frag=c.frag; return r;}""", k)
            out[k] = r
        R['events'] = out
        await pg.evaluate("()=>{while(__s());}")
        # 황금 도망자
        await pg.evaluate("()=>{const G=__G;G.chal.shelter=null;G.chal.busyBoss=false;G.chGoldSpawn();}")
        d0 = await pg.evaluate("()=>{const g=__G.chal.gold;return Math.hypot(g.x-__G.P.x,g.y-__G.P.y)}")
        await pg.evaluate("__run(60)")
        d1 = await pg.evaluate("()=>{const g=__G.chal.gold;return g?Math.hypot(g.x-__G.P.x,g.y-__G.P.y):-1}")
        await shot(pg, '6_gold')
        f0 = await pg.evaluate("__G.chal.frag")
        await pg.evaluate("()=>{const G=__G;G.hurtEnemy(G.chal.gold,1e9);__run(5);while(__s());}")
        R['gold'] = {'d0': round(d0), 'd1': round(d1), 'frag+': (await pg.evaluate("__G.chal.frag")) - f0, 'got': await pg.evaluate("__G.chal.goldGot")}
        # 마왕 5종 (기믹 약화) → 쉼터
        bossR = {}
        for k in ['ab', 'monkey', 'eye', 'skel', 'fw']:
            r = await pg.evaluate("""async(k)=>{const G=__G,c=G.chal;c.ev=null;c.shelter=null;c.cyc=0;c.busyBoss=true;c.bossK=k;
               const rx=G.P.x,ry=G.P.y;G.chEnterBoss(k);__run(60);
               const b=G.boss;const r={k,boss:b?b.bk||'monkey':null,hp:b?Math.round(b.max):0,arena:!!G.arena};
               if(k==='ab'){const pats=new Set();for(let i=0;i<70;i++){__run(30);if(G.boss)pats.add(G.boss.last);}r.pats=[...pats].sort();}
               else __run(300);
               if(G.boss){G.boss.invul=false;G.hurtEnemy(G.boss,1e9);}
               for(let i=0;i<260&&!document.getElementById('levelTitle').textContent.includes('쉼터')||G.state==='play'&&i<260;i++){__run(1);if(G.state==='levelup'&&document.getElementById('levelTitle').textContent.includes('쉼터'))break;}
               r.state=G.state;r.title=document.getElementById('levelTitle').textContent;r.back=Math.round(Math.hypot(G.P.x-rx,G.P.y-ry));r.arenaAfter=!!G.arena;return r}""", k)
            if k == 'ab':
                pass
            bossR[k] = r
            # 쉼터: ab 때는 어둠의 계약, 나머지는 안식
            await pg.evaluate("(i)=>{__G.pick(i);}", 1 if k == 'ab' else 0)
            await pg.evaluate("__run(30)")
            if k == 'ab': await shot(pg, '8_shelter')
            bossR[k]['pact'] = await pg.evaluate("__G.chal.pact")
            bossR[k]['shelter'] = await pg.evaluate("!!__G.chal.shelter")
            await pg.evaluate("()=>{__G.chal.shelter=null;while(__s());}")
        R['boss'] = bossR
        # 촉수마왕 화면 (패턴 중)
        await pg.evaluate("()=>{const G=__G,c=G.chal;c.busyBoss=true;G.chEnterBoss('ab');__run(120);}")
        for i in range(6):
            await pg.evaluate("__run(25)"); await shot(pg, f'7_ab_{i}')
        await pg.evaluate("()=>{const G=__G;G.boss.invul=false;G.hurtEnemy(G.boss,1e9);for(let i=0;i<200&&G.state==='play';i++)__run(1);while(__s());G.chal.shelter=null;}")
        # 20분: 접두사 / 25분: 추격자
        await pg.evaluate("()=>{const G=__G;G.setT(1300);G.chal.goldT=1e9;for(let i=0;i<20;i++){__run(30);while(__s());}}")
        R['pfx'] = await pg.evaluate("()=>{const c={};for(const e of __G.enemies)if(e.pfx)c[e.pfx]=(c[e.pfx]||0)+1;return c}")
        await shot(pg, '9_pfx')
        await pg.evaluate("()=>{const G=__G;while(__s());G.setT(1510);__run(10);while(__s());}")
        ch0 = await pg.evaluate("()=>{const c=__G.chal.chaser;return c?Math.round(Math.hypot(c.x-__G.P.x,c.y-__G.P.y)):-1}")
        await pg.evaluate("()=>{for(let i=0;i<3;i++){__run(30);while(__s());}}")
        ch1 = await pg.evaluate("()=>{const c=__G.chal.chaser;return c?Math.round(Math.hypot(c.x-__G.P.x,c.y-__G.P.y)):-1}")
        await pg.evaluate("()=>{const G=__G,c=G.chal.chaser;c.x=G.P.x+150;c.y=G.P.y;__run(5)}")
        await shot(pg, '10_chaser')
        hp = await pg.evaluate("()=>{const G=__G,c=G.chal.chaser;__clr();G.enemies.length=0;G.P.inv=0;G.P.shield=0;G.P.up.guard=0;G.P.dodge=0;G.P.hp=G.P.max;c.x=G.P.x+10;c.y=G.P.y;c.hitCd=0;c.stun=0;G.tick(1/30);return [Math.round(G.P.hp),G.P.max,G.state]}")
        R['chaser'] = {'d0': ch0, 'd1(3s)': ch1, 'hpAfterHit': hp}
        # 사망 → 보물
        await pg.evaluate("()=>{const G=__G;G.SAVE.ch.tr={rat:false,pouch:false,mirror:false};__clr();G.setT(1250);G.P.reviveLeft=0;G.P.shield=0;G.P.up.guard=0;G.P.dodge=0;G.P.revived=true;G.P.rel={};G.P.inv=0;G.P.hp=1;G.hurt(9999);for(let i=0;i<90;i++)G.tick(1/30)}")
        R['death'] = await pg.evaluate("()=>({state:__G.state,tr:__G.SAVE.ch.tr,best:__G.SAVE.ch.best,title:document.getElementById('overTitle').textContent,stats:document.getElementById('overStats').innerText})")
        await pg.screenshot(path=os.path.join(OUT, 'chal_11_over.png'))
        # 시작 화면
        await pg.evaluate("()=>{document.getElementById('menuBtn').click()}")
        await pg.wait_for_timeout(300)
        R['menu'] = await pg.evaluate("()=>({btn:document.getElementById('chBtn').textContent,info:document.getElementById('chInfo').innerText})")
        await pg.screenshot(path=os.path.join(OUT, 'chal_12_menu.png'))
        # 일반 모드는 그대로
        await pg.evaluate("()=>{const G=__G;G.setChMode(false);G.startGame('wolf');__run(120)}")
        R['normal'] = await pg.evaluate("()=>({chal:!!__G.chal,x:Math.round(__G.P.x)})")
        R['errs'] = pg.errs
        print(json.dumps(R, ensure_ascii=False, indent=1))
        await b.close()
asyncio.run(main())
