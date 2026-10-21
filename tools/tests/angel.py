"""v6.30 타락천사 자동 테스트: PYTHONPATH=tools python3 tools/tests/angel.py  (스크린샷: build/shots/an_*.png)
패턴 5종 · 방패 정면 막기 · 흑화 · 흑백 구체 · 처치 · 보스 등장 확률 · 층 이름 · 출구를 확인한다"""
import asyncio, os, json
from playwright.async_api import async_playwright
from h301 import newpage, ROOT
OUT = os.path.join(ROOT, 'build', 'shots'); os.makedirs(OUT, exist_ok=True)
async def shot(pg, n):
    await pg.evaluate('__G.render()'); await pg.screenshot(path=os.path.join(OUT, f'an_{n}.png'))
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--disable-gpu'])
        pg = await newpage(b, 1280, 720)
        pg.on('console', lambda m: pg.errs.append('console: ' + m.text) if m.type == 'error' else None)
        R = {}
        R['prob'] = await pg.evaluate("""()=>{const G=__G,o={};for(let t=0;t<6;t++){const c={};for(let i=0;i<20000;i++){const k=G.pickBossK(t);c[k]=(c[k]||0)+1;}o[t]=Object.fromEntries(Object.entries(c).map(([k,v])=>[k,Math.round(v/200)]));}return o}""")
        R['floors'] = await pg.evaluate("()=>{const G=__G,o=[];G.SAVE.diff.max=5;for(let t=0;t<6;t++){G.SAVE.diff.sel=t;G.buildCards();o.push(document.getElementById('diffTxt').textContent)}G.SAVE.diff.sel=3;return o}")
        await pg.evaluate("()=>{const G=__G;G.SAVE.set.speed=0;G.SAVE.shards=999;G.SAVE.diff.max=5;G.SAVE.diff.sel=3;G.startGame('wolf');G.P.bossK='angel';window.__rt=1;__lv(25)}")
        R['start'] = await pg.evaluate("()=>({tier:__G.P.tier,lvl:__G.P.lvl,form:__G.P.form,hud:''})")
        await pg.evaluate("()=>{const G=__G;G.enemies.length=0;G.raiseCastle();G.enterArena();for(let i=0;i<40;i++)G.tick(1/30)}")
        R['arena'] = await pg.evaluate("()=>{const G=__G,b=G.boss;return {k:G.arena.k,bk:b.bk,hp:Math.round(b.max),p:[Math.round(G.P.x),Math.round(G.P.y)],inP:G.inPoly(G.P.x,G.P.y),b:[Math.round(b.x),Math.round(b.y)],bin:G.inPoly(b.x,b.y),st:b.st}}")
        await shot(pg, '0_intro')
        await pg.evaluate("()=>{__G.arena.sealed=true}")   # 패턴 테스트 중 플레이어가 아래 출구 칸에 서도 성 밖으로 나가지 않게
        await pg.evaluate("()=>{window.__run1=n=>{const G=__G;for(let i=0;i<n;i++){G.P.inv=99;G.P.hp=G.P.max;if(G.boss&&G.boss.ph===1)G.boss.hp=G.boss.max;G.tick(1/30)}}}")
        await pg.evaluate("__run1(60)")
        # 각 패턴: 플레이어는 보스 앞 200에 세워 두고 무적 해제, 맞은 피해를 센다
        H = """(k,n,shots)=>{const G=__G,P=G.P,b=G.boss;b.tele=[];b.stT=0;G.anStart(b,k);let hurt=0,hits=0;const S=[];
          for(let i=0;i<n;i++){P.inv=0;const h0=P.hp;P.hp=P.max;const before=P.hp;G.tick(1/30);if(P.hp<before){hurt+=before-P.hp;hits++;}if(shots.includes(i))S.push(i);if(b.st==='chase'||b.st==='recover')break;}
          return {hurt:Math.round(hurt),hits,st:b.st,tele:b.tele.length,fx:G.anFx.length}}"""
        await pg.evaluate("()=>{const G=__G,b=G.boss;G.P.x=b.x;G.P.y=b.y+200;}")
        for k, steps in [('slash', [20]), ('rhythm', [25, 45, 70]), ('pillars', [22, 40]), ('shield', [30, 80])]:
            await pg.evaluate("()=>{const G=__G,b=G.boss;b.tele=[];b.st='recover';b.stT=9;G.P.x=b.x+30;G.P.y=b.y+190;}")
            await pg.evaluate("(k)=>{const b=__G.boss;b.stT=0;__G.anStart(b,k)}", k)
            done = 0
            for s in steps:
                await pg.evaluate(f"__run1({s - done})"); done = s
                await shot(pg, f'1_{k}_{s}')
            R['pat_' + k] = await pg.evaluate("()=>{const b=__G.boss;return {st:b.st,tele:b.tele.length,shT:+(b.shT||0).toFixed(2),fx:__G.anFx.length}}")
            await pg.evaluate("__run1(150)")
        # 리듬 함정 피해 판정: 가만히 서 있으면 맞는다
        R['rhythm_hit'] = await pg.evaluate("""()=>{const G=__G,P=G.P,b=G.boss;b.tele=[];b.ph=1;b.st='recover';b.stT=99;P.x=b.x;P.y=b.y+260;G.anStart(b,'rhythm');let hits=0;
          for(let i=0;i<150;i++){P.inv=0;P.hp=P.max;b.hp=b.max;G.tick(1/30);if(P.hp<P.max)hits++;P.x=b.x;P.y=b.y+260;}return {hits,late:b.tele.filter(t=>t.late).length}}""")
        # 방패: 정면은 막고 등 뒤는 맞는다
        R['shield'] = await pg.evaluate("""()=>{const G=__G,P=G.P,b=G.boss;b.tele=[];b.invul=false;b.hp=b.max;b.st='shield';b.shT=3;b.sAng=0;const h0=b.hp;
          P.x=b.x+150;P.y=b.y;G.hurtEnemy(b,500,0,0,0);const front=h0-b.hp;P.x=b.x-150;P.y=b.y;G.hurtEnemy(b,500,0,0,0);const back=h0-front-b.hp;b.shT=0;b.st='recover';b.stT=0.5;return {front:Math.round(front),back:Math.round(back)}}""")
        await pg.evaluate("__run(60)")
        # 흑화
        await pg.evaluate("()=>{window.__run2=n=>{const G=__G;for(let i=0;i<n;i++){G.P.inv=99;G.P.hp=G.P.max;if(G.boss&&G.boss.ph===2)G.boss.hp=G.boss.max;G.tick(1/30)}}}")
        await pg.evaluate("()=>{const G=__G,b=G.boss;b.hp=b.max*0.69;G.P.x=b.x+420;G.P.y=b.y;__run2(30)}")
        await shot(pg, '2_trans_a')
        await pg.evaluate("__run2(30)"); await shot(pg, '2_trans_b')
        await pg.evaluate("__run2(30)"); await shot(pg, '2_trans_c')
        await pg.evaluate("__run2(40)")
        R['ph2'] = await pg.evaluate("()=>{const b=__G.boss;return {ph:b.ph,st:b.st,invul:b.invul,hp:+(b.hp/b.max).toFixed(2)}}")
        # 흑백 구체: 흰 구체를 안 먹으면 터져서 아프다 / 먹으면 안전
        await pg.evaluate("()=>{const G=__G,b=G.boss;b.tele=[];b.stT=0;G.P.x=b.x;G.P.y=b.y+380;G.anStart(b,'orbs');__run2(40)}")
        await shot(pg, '3_orbs')
        R['orbs'] = await pg.evaluate("()=>({n:__G.anOrbs.length,w:__G.anOrbs.filter(o=>o.white).length})")
        R['white_miss'] = await pg.evaluate("""()=>{const G=__G,P=G.P,b=G.boss;b.st='recover';b.stT=99;let hurt=0;const W=G.anOrbs.filter(o=>o.white).length;
          P.dodge=0;b.ex=[];const A=G.AMAP;let X=A.cx+620;if(!G.inPoly(X,A.cy))X=A.cx-620;for(let i=0;i<260;i++){P.x=X;P.y=A.cy;P.inv=0;P.hp=P.max;b.hp=b.max;G.tick(1/30);hurt+=P.max-P.hp;}return {whites:W,hurt:Math.round(hurt),left:G.anOrbs.length}}""")
        R['white_touch'] = await pg.evaluate("""()=>{const G=__G,P=G.P,b=G.boss;b.tele=[];G.anStart(b,'orbs');__run2(30);b.st='recover';b.stT=99;b.ex=[];let got=0,hurt=0;
          for(let i=0;i<200;i++){const w=G.anOrbs.find(o=>o.white);if(!w)break;P.x=w.x;P.y=w.y;P.inv=0;P.hp=P.max;b.hp=b.max;const n=G.anOrbs.length;G.tick(1/30);hurt+=P.max-P.hp;if(G.anOrbs.length<n)got++;}return {got,hurt:Math.round(hurt)}}""")
        for k, s in [('bolt', 18), ('pillars', 30), ('rhythm', 40)]:
            await pg.evaluate("(k)=>{const G=__G,b=G.boss;b.tele=[];G.anOrbs.length=0;b.stT=0;G.P.x=b.x;G.P.y=b.y+360;G.anStart(b,k)}", k)
            await pg.evaluate(f"__run2({s})"); await shot(pg, f'4_ph2_{k}')
            await pg.evaluate("__run2(120)")
        # 순간이동: 가까이 붙어 있으면 멀리 사라진다
        R['blink'] = await pg.evaluate("""()=>{const G=__G,P=G.P,b=G.boss;b.tele=[];b.st='chase';b.stT=99;b.blCd=0;const x0=b.x,y0=b.y;
          for(let i=0;i<100;i++){P.x=b.x+60;P.y=b.y+40;P.inv=99;b.hp=b.max;G.tick(1/30);}return {moved:Math.round(Math.hypot(b.x-x0,b.y-y0)),st:b.st,inP:G.inPoly(b.x,b.y)}}""")
        await shot(pg, '5_blink')
        # 처치
        await pg.evaluate("()=>{const G=__G,b=G.boss;b.invul=false;b.shT=0;G.hurtEnemy(b,1e9,0,0,0);for(let i=0;i<20;i++)G.tick(1/30)}")
        await shot(pg, '6_death')
        R['win'] = await pg.evaluate("()=>({state:__G.state,boss:!!__G.boss,dex:__G.SAVE.dex.kills.boss6||0})")
        # 출구: 봉인 전에는 아래 통로 끝에 머무르면 나간다
        await pg.evaluate("()=>{const G=__G;G.SAVE.set.speed=0;G.startGame('archer');G.P.bossK='angel';__lv(25);G.enemies.length=0;G.raiseCastle();G.enterArena();for(let i=0;i<40;i++)G.tick(1/30)}")
        R['exit'] = await pg.evaluate("""()=>{const G=__G,P=G.P,E=G.arenaExit();for(let i=0;i<70;i++){P.x=E.x;P.y=E.y+60;P.inv=99;G.tick(1/30)}return {E,arena:!!G.arena,trans:!!G.trans}}""")
        await pg.evaluate("__run(40)")
        R['after_exit'] = await pg.evaluate("()=>({arena:!!__G.arena,boss:!!__G.boss,x:Math.round(__G.P.x)})")
        R['errs'] = pg.errs[:6]
        print(json.dumps(R, ensure_ascii=False, indent=1))
        await b.close()
asyncio.run(main())
