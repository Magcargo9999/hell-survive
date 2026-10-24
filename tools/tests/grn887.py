"""v8.87 영원의 온실주(챌린지 전용 마왕) · 시련의 제단 · 챌린지 난이도 +15% 테스트
PYTHONPATH=tools python3 tools/tests/grn887.py   (스크린샷: build/shots/grn887_*.png)"""
import asyncio, os, json
from playwright.async_api import async_playwright
from h301 import newpage, ROOT
OUT = os.path.join(ROOT, 'build', 'shots'); os.makedirs(OUT, exist_ok=True)
async def shot(pg, n):
    await pg.evaluate('__G.render()'); await pg.screenshot(path=os.path.join(OUT, f'grn887_{n}.png'))
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--disable-gpu'])
        pg = await newpage(b, 1280, 720)
        pg.on('console', lambda m: pg.errs.append('console: ' + m.text) if m.type == 'error' else None)
        await pg.evaluate("""()=>{
          window.__clr=()=>{const G=__G;let g=0;while(g++<50&&((G.state==='levelup'&&!document.getElementById('levelTitle').textContent.includes('시련'))||G.state==='evolve')){if(!__s())break;}}
          window.__go=(n,safe)=>{const G=__G;for(let i=0;i<n;i++){__clr();if(safe){G.P.inv=99;G.P.hp=G.P.max}G.tick(1/30)}}
          window.__hit0=()=>{const G=__G;G.P.inv=0;G.P.hp=G.P.max=99999;}}""")
        R = {}
        await pg.evaluate("()=>{const G=__G;G.SAVE.ch.open=true;G.setChMode(true);G.startGame('wolf');}")
        await pg.evaluate("__go(30,true)")
        # --- 난이도 +15% ---
        R['hard'] = await pg.evaluate("()=>{const G=__G;return {hard:G.CH_HARD,ratio:+(G.chTime()/G.chTime0()).toFixed(3),dm:+G.chDmgT().toFixed(3),boss:G.CH_BOSS}}")
        # --- 영원의 온실주 입장 ---
        await pg.evaluate("()=>{const G=__G;G.P.lvl=Math.max(G.P.lvl,15);G.chEnterBoss('grn');}")
        await pg.evaluate("__go(10,true)")
        R['spawn'] = await pg.evaluate("()=>{const G=__G,b=G.boss;return {bk:b.bk,hp:Math.round(b.max),inCh:G.inCh(b.x,b.y),st:b.st,dex:G.SAVE.dex.seen&&G.SAVE.dex.seen.boss13}}")
        await pg.evaluate("()=>{const G=__G,b=G.boss;b.invul=false;b.st='chase';b.stT=99;}")
        await pg.evaluate("__go(60,true)")
        await shot(pg, '1_boss')
        # --- ① 최면의 화분 ---
        await pg.evaluate("()=>{const G=__G,b=G.boss;b.tele=[];b.at=null;b.st='chase';b.stT=99;b.x=G.P.x+250;b.y=G.P.y;G.grnStart(b,'pollen');}")
        await pg.evaluate("__hit0()")
        hy = []
        for i in range(90):
            await pg.evaluate("()=>{__G.P.inv=0;__G.tick(1/30)}")
            if i == 50: await shot(pg, '2_pollen')
            hy.append(await pg.evaluate("()=>[+(__G.P.hypT||0).toFixed(2),+(__G.P.hypImm||0).toFixed(2)]"))
        R['pollen'] = {'hypMax': max(h[0] for h in hy), 'immMax': max(h[1] for h in hy)}
        # 반전 확인: D키를 누르면 왼쪽으로 가야 한다
        await pg.evaluate("()=>{__G.P.hypT=1.0;}")
        x0 = await pg.evaluate("()=>__G.P.x"); await pg.keyboard.down('KeyD'); await pg.evaluate("__go(20,true)"); await pg.keyboard.up('KeyD')
        x1 = await pg.evaluate("()=>__G.P.x"); R['reverse'] = {'dx': round(x1 - x0), 'ok': x1 < x0}
        # 바깥(꽃가루 반경 밖)에서는 맞지 않는다
        await pg.evaluate("()=>{const G=__G,b=G.boss;G.P.hypT=0;G.P.hypImm=0;b.tele=[];b.at=null;b.st='chase';b.stT=99;b.x=G.P.x+470;b.y=G.P.y;G.grnStart(b,'pollen');}")
        for i in range(70): await pg.evaluate("()=>{__G.P.inv=0;__G.tick(1/30)}")
        R['pollenOut'] = await pg.evaluate("()=>({hyp:__G.P.hypT||0})")
        # --- ② 가시 덩굴 채찍 ---
        await pg.evaluate("()=>{const G=__G,b=G.boss;G.P.hypT=0;G.P.hypImm=0;b.tele=[];b.at=null;b.st='chase';b.stT=99;b.x=G.P.x+250;b.y=G.P.y;G.P.hp=G.P.max;G.grnStart(b,'lash');}")
        hp0 = await pg.evaluate("()=>__G.P.hp"); mn = hp0
        for i in range(80):
            await pg.evaluate("()=>{__G.P.inv=0;__G.tick(1/30)}"); mn = min(mn, await pg.evaluate("()=>__G.P.hp"))
            if i == 20: await shot(pg, '3_lash')
        R['lashStand'] = {'lost': round(hp0 - mn)}
        # 옆으로 비키면 피한다 (예고가 고정된 뒤 수직으로 이동)
        await pg.evaluate("()=>{const G=__G,b=G.boss;b.tele=[];b.at=null;b.st='chase';b.stT=99;b.x=G.P.x+250;b.y=G.P.y;G.P.hp=G.P.max;G.grnStart(b,'lash');}")
        hp0 = await pg.evaluate("()=>__G.P.hp"); mn = hp0
        await pg.keyboard.down('KeyD')   # 보스 반대쪽(오른쪽→보스는 오른쪽에 있으니 왼쪽이 뒤)… 반대 방향으로 물러난다
        await pg.keyboard.up('KeyD'); await pg.keyboard.down('KeyA')
        for i in range(80):
            await pg.evaluate("()=>{__G.P.inv=0;__G.tick(1/30)}"); mn = min(mn, await pg.evaluate("()=>__G.P.hp"))
        await pg.keyboard.up('KeyA'); R['lashRetreat'] = {'lost': round(hp0 - mn)}
        # --- ③ 유리 씨앗 비 ---
        await pg.evaluate("()=>{const G=__G,b=G.boss;b.tele=[];b.at=null;b.st='chase';b.stT=99;b.x=G.P.x+250;b.y=G.P.y-60;G.P.hp=G.P.max;G.GRW.frost=[];G.grnStart(b,'seed');}")
        for i in range(30): await pg.evaluate("__go(1,true)")
        await shot(pg, '4_seed_fall')
        await pg.evaluate("__go(75,true)")
        await shot(pg, '5_seed_frost')
        R['seed'] = await pg.evaluate("()=>({frost:__G.GRW.frost.length})")
        # 냉기 장판: 안에 서 있으면 느려진다
        await pg.evaluate("()=>{const G=__G;if(G.GRW.frost[0]){G.P.x=G.GRW.frost[0].x;G.P.y=G.GRW.frost[0].y;}G.P.slowT=0;}")
        await pg.evaluate("__go(12,true)")
        R['frostSlow'] = await pg.evaluate("()=>({slow:+(__G.P.slowT||0).toFixed(2)})")
        # 규칙 9: 만개(8개) + 장판 최대일 때도 내 주변 260px 바닥이 대부분 안전한가
        await pg.evaluate("()=>{const G=__G,b=G.boss;b.rage=true;b.tele=[];b.at=null;b.st='chase';b.stT=99;G.GRW.frost=[];G.grnStart(b,'seed');}")
        R['safe9_peakTele'] = await pg.evaluate("__go(30,true);(()=>{const G=__G,P=G.P;let n=0,ok=0;for(let a=0;a<360;a+=10)for(let r=20;r<=260;r+=40){const x=P.x+Math.cos(a*Math.PI/180)*r,y=P.y+Math.sin(a*Math.PI/180)*r;if(!G.inCh(x,y))continue;n++;let bad=false;for(const z of G.GRW.frost)if(Math.hypot(x-z.x,(y-z.y)*1.15)<z.r)bad=true;for(const t of G.boss.tele)if(t.k==='circle'&&t.t>=0&&Math.hypot(x-t.x,y-t.y)<t.r)bad=true;if(!bad)ok++;}return +(ok/n*100).toFixed(0)})()")
        await pg.evaluate("__go(60,true)")
        R['safe9'] = await pg.evaluate("""()=>{const G=__G,P=G.P;let n=0,ok=0;for(let a=0;a<360;a+=10)for(let r=20;r<=260;r+=40){const x=P.x+Math.cos(a*Math.PI/180)*r,y=P.y+Math.sin(a*Math.PI/180)*r;if(!G.inCh(x,y))continue;n++;
          let bad=false;for(const z of G.GRW.frost)if(Math.hypot(x-z.x,(y-z.y)*1.15)<z.r)bad=true;for(const t of G.boss.tele)if(t.k==='circle'&&Math.hypot(x-t.x,y-t.y)<t.r)bad=true;if(!bad)ok++;}
          return {frost:G.GRW.frost.length,safePct:+(ok/n*100).toFixed(0)}}""")
        # --- ④ 뿌리의 종복 ---
        await pg.evaluate("()=>{const G=__G,b=G.boss;b.rage=false;b.tele=[];b.at=null;b.st='chase';b.stT=99;b.x=G.P.x+250;b.y=G.P.y;G.GRW.frost=[];G.grnStart(b,'bud');}")
        await pg.evaluate("__go(75,true)")
        await shot(pg, '6_bud')
        R['bud'] = await pg.evaluate("()=>({n:__G.enemies.filter(e=>e.kind==='grb'&&e.hp>0).length})")
        # 먼저 죽이면 터지지 않는다
        r = await pg.evaluate("""()=>{const G=__G,L=G.enemies.filter(e=>e.kind==='grb'&&e.hp>0);const e=L[0];e.pop=0;e.x=G.P.x+30;e.y=G.P.y;G.P.hp=G.P.max;const h0=G.P.hp;
          e.fuse=0;G.hurtEnemy(e,1e9);const fx0=G.GRW.fx.filter(q=>q.k==='boom').length;for(let i=0;i<40;i++){G.P.inv=0;G.tick(1/30)}return {killedNoBoom:fx0===0}}""")
        R['budKill'] = r
        # 붙으면 터진다
        r = await pg.evaluate("""()=>{const G=__G,L=G.enemies.filter(e=>e.kind==='grb'&&e.hp>0);if(!L.length)return {n:0};const e=L[0];e.pop=0;e.x=G.P.x+20;e.y=G.P.y;for(const q of L)if(q!==e){q.hp=0}
          G.P.hp=G.P.max;let boom=0,h0=G.P.hp,mn=h0;for(let i=0;i<60;i++){G.P.inv=0;G.tick(1/30);mn=Math.min(mn,G.P.hp);if(G.GRW.fx.some(q=>q.k==='boom'))boom=1}return {boom,lost:Math.round(h0-mn)}}""")
        R['budBoom'] = r
        await pg.evaluate("()=>{__G.enemies.filter(e=>e.kind==='grb').forEach(e=>e.hp=0)}")
        # --- ⑤ 의식의 꽃 원 ---
        await pg.evaluate("()=>{const G=__G,b=G.boss;b.tele=[];b.at=null;b.st='chase';b.stT=99;b.x=G.P.x+250;b.y=G.P.y;G.GRW.ring=null;G.grnStart(b,'ring');}")
        await pg.evaluate("__go(110,true)")
        await shot(pg, '7_ring')
        R['ring'] = await pg.evaluate("()=>({ring:!!__G.GRW.ring,slow:+(__G.P.slowT||0).toFixed(2)})")
        # 밖으로 나가면 끝: 원 밖에서는 느려지지 않는다
        await pg.evaluate("()=>{const G=__G,r=G.GRW.ring;if(r){G.P.x=r.x+r.r+80;G.P.y=r.y;}G.P.slowT=0;}")
        await pg.evaluate("__go(12,true)")
        R['ringOut'] = await pg.evaluate("()=>({slow:+(__G.P.slowT||0).toFixed(2)})")
        # 패턴 순환: 40초 동안 5가지가 모두 나온다
        await pg.evaluate("()=>{const G=__G,b=G.boss;b.tele=[];b.at=null;b.st='chase';b.stT=0.5;b.rage=false;G.GRW.ring=null;}")
        seen = set()
        for i in range(80):
            await pg.evaluate("__go(30,true)")
            k = await pg.evaluate("()=>{const b=__G.boss;return b&&b.at?b.at.k:''}")
            if k: seen.add(k)
        R['patterns'] = sorted(seen)
        # 만개 전환
        await pg.evaluate("()=>{const G=__G,b=G.boss;b.hp=b.max*0.49;}")
        await pg.evaluate("__go(60,true)")
        R['rage'] = await pg.evaluate("()=>({rage:__G.boss.rage})")
        # --- 처치 → 정리 · 쉼터 · 도감 ---
        await pg.evaluate("()=>{const G=__G,b=G.boss;b.invul=false;b.hp=1;G.hurtEnemy(b,1e9);}")
        await pg.evaluate("__go(20,true)")
        await shot(pg, '8_death')
        R['dead'] = await pg.evaluate("()=>({boss:!!__G.boss,death:!!__G.GRW.death,grb:__G.enemies.filter(e=>e.kind==='grb').length,ring:!!__G.GRW.ring,frost:__G.GRW.frost.length,hyp:__G.P.hypT||0,kill:__G.SAVE.dex.kills.boss13,retT:__G.chal.retT>0||!!__G.chal.shelter})")
        await pg.evaluate("__go(240,true)")
        R['shelter'] = await pg.evaluate("()=>({shelter:!!__G.chal.shelter,bossN:__G.chal.bossN,frag:__G.chal.frag,state:__G.state})")
        await pg.evaluate("()=>{while(__s());}")
        # --- 시련의 제단 ---
        await pg.evaluate("()=>{const G=__G,c=G.chal;c.shelter=null;c.busyBoss=false;c.ev=null;c.altar=null;c.altarT=0;c.evCd=1e9;c.goldT=1e9;}")
        await pg.evaluate("__go(10,true)")
        R['altar'] = await pg.evaluate("()=>{const G=__G,A=G.chal.altar;return A?{ok:true,inCh:G.inCh(A.x,A.y),d:Math.round(Math.hypot(A.x-G.P.x,A.y-G.P.y)),life:A.life}:{ok:false}}")
        await shot(pg, '9_altar_far')
        await pg.evaluate("()=>{const G=__G,A=G.chal.altar;G.P.x=A.x-340;G.P.y=A.y+40;}")
        await pg.evaluate("__go(5,true)"); await shot(pg, '10_altar_near')
        await pg.evaluate("()=>{const G=__G,A=G.chal.altar;G.P.x=A.x;G.P.y=A.y;}")
        await pg.evaluate("__go(20,true)")
        R['hold'] = await pg.evaluate("()=>({hold:+__G.chal.altar.hold.toFixed(2),trial:!!__G.chal.trial})")
        await pg.evaluate("__go(30,true)")
        R['trial'] = await pg.evaluate("()=>{const G=__G;return {trial:!!G.chal.trial,hp:+(G.chTime()/G.chTime0()).toFixed(3),dm:+G.chDmgT().toFixed(3)}}")
        await pg.evaluate("__go(60,true)"); await shot(pg, '11_trial')
        # 시련 중에는 강적 호출이 미뤄진다
        await pg.evaluate("()=>{const G=__G,c=G.chal;c.evCd=0;G.P.lvl=Math.max(G.P.lvl,c.next);}")
        await pg.evaluate("__go(10,true)")
        R['evBlocked'] = await pg.evaluate("()=>({ev:!!__G.chal.ev,busy:__G.chal.busyBoss})")
        f0 = await pg.evaluate("()=>__G.chal.frag")
        for i in range(60): await pg.evaluate("__go(30,true)")   # 40초 넘게
        R['win'] = await pg.evaluate("()=>({state:__G.state,title:document.getElementById('levelTitle').textContent,trial:!!__G.chal.trial})")
        await shot(pg, '12_reward')
        await pg.evaluate("()=>{__G.pick(0)}")
        R['after'] = await pg.evaluate("()=>{const c=__G.chal;return {state:__G.state,altar:!!c.altar,altarT:Math.round(c.altarT),frag:c.frag,trialN:c.trialN}}")
        R['fragGain'] = R['after']['frag'] - f0
        # --- 새 판: 정리 ---
        await pg.evaluate("()=>{__G.setChMode(true);__G.startGame('wolf');}")
        R['reset'] = await pg.evaluate("()=>({frost:__G.GRW.frost.length,ring:!!__G.GRW.ring,hyp:__G.P.hypT||0,death:!!__G.GRW.death,altar:__G.chal.altar,trial:__G.chal.trial})")
        # 도감
        R['dex'] = await pg.evaluate("""()=>{document.getElementById('dexBtn').click();document.querySelector('.dextabs button[data-dt=mon]').click();const t=document.getElementById('dexList').innerText;document.getElementById('dexClose').click();return {boss:t.includes('영원의 온실주'),bud:t.includes('뿌리 꽃봉오리')}}""")
        R['errs'] = pg.errs
        print(json.dumps(R, ensure_ascii=False, indent=1))
        await b.close()
asyncio.run(main())
