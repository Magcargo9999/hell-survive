"""v10.42 분열체 슬라임 왕(bk 'slm', 지하 3층)
 층 배치(3층 slm · 4층 skel · 5층 angel) · 질량 합 = 체력 · 대리 히트박스 · 광역 감쇠(100/60/45) · 75/50/25% 포효(무적·tierEx 멈춤) 뒤 분열 · 최대 6마리
 · 몸 하나 처치 · 합체 성공(회복·거대화) / 실패(넉백·경직) · 패턴 A/B/D 발동 · 장판 12개 상한 · 처치·도감·업적 · 스크린샷
사용: PYTHONPATH=tools GAME_URL=... python3 tools/tests/slm1042.py   (스크린샷 build/slm_*.png)"""
import asyncio, sys, os, json
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, HERE)
from playwright.async_api import async_playwright
import h301
B = os.path.join(os.path.dirname(HERE), 'build') + '/'
async def ev(pg, js):
    try: return await pg.evaluate(js)
    except Exception as ex: return 'ERR ' + str(ex).split('\n')[0][:300]
async def main():
    async with async_playwright() as pw:
        b = await pw.chromium.launch(); pg = await h301.newpage(b, 1280, 720); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e))); pg.on('console', lambda m: errs.append(m.text) if m.type == 'error' else None)
        await pg.wait_for_function('__G.IMG&&__G.IMG.boss', timeout=90000); await pg.wait_for_function("__G.imgReady(['arena','slm','slmfx'])", timeout=120000, polling=1000)
        await pg.evaluate("""()=>{window.__cl=()=>{const P=__G.P;P.inv=0;P.shield=0;P.dodge=0;P.pals=[];P.up.guard=0;P.rel.mirror=0;P.armor=1;P.taken=1;P.stunT=99;P.slowT=0;P.max=1e7;P.hp=P.max;P.exitLeft=0};
          window.__tk=()=>{const G=__G;G.tick(1/30);if(G.state!=='play'&&G.state!=='over'&&G.state!=='win')__s()}}""")
        R = {}
        R['floor'] = await ev(pg, """()=>{const G=__G,o={};o.f=[0,1,2,3,4].map(t=>G.pickBossK(t));
          G.SAVE.diff.max=4;G.SAVE.diff.sel=2;G.startGame('archer');return o}""")
        for i in range(40):
            if await ev(pg, "()=>__G.state") == 'play': break
            await asyncio.sleep(0.5)
        await ev(pg, """()=>{const G=__G,P=G.P;__lv(30);__cl();P.tier=2;P.bossK='slm';G.raiseCastle();G.enterArena();return 1}""")
        await asyncio.sleep(2.5)
        R['enter'] = await ev(pg, """()=>{const G=__G,P=G.P,o={};P.exitLeft=0;if(G.arena)G.arena.sealed=true;for(let i=0;i<5;i++)__tk();const e=G.boss;o.bk=e&&e.bk;o.st=e.st;o.tier=P.tier;o.hp=Math.round(e.hp);o.mass=Math.round(G.slmMass());o.n=G.SLW.bodies.length;o.inv=e.invul;
          o.exP=G.bossExPaused(e);for(let i=0;i<80;i++)__tk();o.st2=e.st;o.exP2=G.bossExPaused(e);return o}""")
        await pg.screenshot(path=B + 'slm_1.png')
        S = "const G=__G,P=G.P,e=G.boss,W=G.SLW,A=G.slm,o={};"
        # 분열: 실제 피해로 체력을 깎아 75% · 50% · 25%
        R['split'] = await ev(pg, "()=>{" + S + """const W2=[];const cut=q=>{let n=0;while(e.hp>e.max*q&&n++<200){const L=G.slm.lead;const px=G.enemies.find(z=>z.kind==='slb'&&z.b.mass>1);G.hurtEnemy(px||e,Math.min(e.hp-e.max*q+5,(px?px.b.mass:L.mass)*0.9),0,0,0,true);}};
          for(const q of [0.74,0.49,0.24]){__cl();cut(q);__tk();const r={st:e.st,inv:e.invul,exP:G.bossExPaused(e),pxInv:G.enemies.filter(z=>z.kind==='slb').every(z=>z.invul)};for(let i=0;i<80;i++){__cl();__tk()}
            r.n=W.bodies.length;r.sz=W.bodies.map(b=>b.sz).sort();r.sumOk=Math.abs(G.slmMass()-e.hp)<1;r.px=G.enemies.filter(z=>z.kind==='slb').length;W2.push(r)}
          return W2}""")
        await pg.screenshot(path=B + 'slm_2.png')
        R['aoe'] = await ev(pg, "()=>{" + S + """__cl();for(let i=0;i<40;i++){__cl();__tk()}const Bs=W.bodies.slice();for(const b of Bs)if(b.st!=='move')b.go('move');const L=G.slm.lead;const px=G.enemies.filter(q=>q.kind==='slb'&&!q.invul);
          const order=[L].concat(px.map(q=>q.b)),m0=order.map(b=>b.mass),h0=e.hp;G.tick(1/30);const D=1000;G.hurtEnemy(e,D,0,0,0,true);for(const q of px)G.hurtEnemy(q,D,0,0,0,true);
          o.drop=order.map((b,i)=>Math.round(m0[i]-b.mass));o.hpDrop=Math.round(h0-e.hp);o.sumOk=Math.abs(G.slmMass()-e.hp)<1;return o}""")
        R['bodyDie'] = await ev(pg, "()=>{" + S + """__cl();P.inv=99;const n0=W.bodies.length,px=G.enemies.find(q=>q.kind==='slb'),b=px.b,m=b.mass;for(let k=0;k<40&&W.bodies.includes(b);k++){G.hurtEnemy(px,m,0,0,0,false);G.tick(1/30)}
          o.n0=n0;o.n=W.bodies.length;o.gone=!W.bodies.includes(b);o.alive=!!G.boss&&G.boss.hp>0;o.sumOk=Math.abs(G.slmMass()-e.hp)<1;return o}""")
        # 합체: 성공 / 실패
        R['merge'] = await ev(pg, "()=>{" + S + """__cl();P.inv=99;P.x=e.x+600;W.cT=0;let start=-1,first=null,heal=0;for(let i=0;i<30*14;i++){__cl();P.inv=99;const h=e.hp;__tk();
            if(W.gather&&start<0){start=i;o.exP=G.bossExPaused(e);o.tele=e.tele.filter(t=>t.rgb==='255,205,80').length}
            if(W.gather&&W.gather.pairs.length&&!first){first=W.gather.pairs[0]}
            if(e.hp>h+1)heal+=e.hp-h;if(start>=0&&!W.gather)break}
          o.gathered=start>=0;o.paired=!!first;o.heal=Math.round(heal);o.giant=W.bodies.some(b=>b.gT>0);o.n=W.bodies.length;o.sumOk=Math.abs(G.slmMass()-e.hp)<1;return o}""")
        await pg.screenshot(path=B + 'slm_3.png')
        R['mergeFail'] = await ev(pg, "()=>{" + S + """__cl();P.inv=99;P.x=e.x+600;W.cT=0;let pr=null;for(let i=0;i<30*10&&!pr;i++){__cl();__tk();if(W.gather&&W.gather.pairs.length)pr=W.gather.pairs[0]}
          if(!pr)return 'no pair';const a=pr.a,c=pr.b;const tq=G.enemies.find(q=>q.kind==='slb'&&q.b===c)||e;
          for(let i=0;i<30;i++){__cl();const ang=Math.atan2(c.y-a.y,c.x-a.x)||0;G.hurtEnemy(tq===e?e:tq,1,Math.cos(ang),Math.sin(ang),900,false);__tk();if(!W.gather||!W.gather.pairs.includes(pr))break}
          o.cancelled=!W.gather||!W.gather.pairs.includes(pr);o.stun=[a.st,c.st];return o}""")
        # 패턴 발동 · 장판 상한
        R['patterns'] = await ev(pg, "()=>{" + S + """__cl();P.inv=99;const seen={};let pudMax=0,slowHit=0;for(let i=0;i<30*40;i++){__cl();P.inv=99;P.x=e.x+Math.cos(i/60)*300;P.y=e.y+Math.sin(i/60)*200;if(!G.inPoly(P.x,P.y)){P.x=e.x;P.y=e.y+150}__tk();
            for(const b of W.bodies)seen[b.st]=(seen[b.st]||0)+1;if(!G.boss&&!o.why)o.why='gone@'+i+' state '+G.state+' arena '+!!G.arena;pudMax=Math.max(pudMax,W.pud.length);if(P.slowT>0)slowHit++;if(!G.boss)break}
          o.seen=Object.keys(seen).join(',');o.pudMax=pudMax;o.slow=slowHit>0;o.globs=W.globs.length;return o}""")
        await pg.screenshot(path=B + 'slm_4.png')
        R['kill'] = await ev(pg, """()=>{const G=__G,P=G.P,W=G.SLW;__cl();P.inv=99;let n=0;const had=!!G.boss,k0=G.SAVE.dex.kills.boss27|0;while(G.boss&&n++<400){const e=G.boss;for(const q of [e].concat(G.enemies.filter(q=>q.kind==='slb')))G.hurtEnemy(q,5e5,0,0,0,false);__tk()}
          return {had,dead:!G.boss,killsAdded:(G.SAVE.dex.kills.boss27|0)-k0,proxies:G.enemies.filter(q=>q.kind==='slb').length,state:G.state}}""")
        for i in range(30): await ev(pg, "()=>__tk()")
        await pg.screenshot(path=B + 'slm_5.png')
        R['dexAch'] = await ev(pg, "()=>{const G=__G;return {ach:!!G.ACH.find(a=>a.id==='k_slm')}}")
        for k, v in R.items(): print(k, json.dumps(v, ensure_ascii=False))
        print('errs', errs[:5])
        await b.close()
asyncio.run(main())
