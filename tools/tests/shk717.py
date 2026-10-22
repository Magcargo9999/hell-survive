"""v7.17 거대 버섯마귀: 등장 확률 · 패턴 6종 · 소환/포자 갑옷/휘청 · 처치 · 안전 구역(규칙 9) · 스크린샷"""
import asyncio, os, sys, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from playwright.async_api import async_playwright
from h301 import newpage
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'build', 'shots')
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--disable-gpu']); pg = await newpage(b, 1280, 720)
        await pg.wait_for_function('window.__G && __G.IMG && __G.IMG.shk', timeout=90000)
        R = {}
        R['prob'] = await pg.evaluate("""()=>{const G=__G,o={};for(const t of [3,4,5,6,9,12]){const c={};for(let i=0;i<4000;i++){const k=G.pickBossK(t);c[k]=(c[k]||0)+1;}o[t+1+'층']=Object.fromEntries(Object.entries(c).map(([k,v])=>[k,Math.round(v/40)]));}return o;}""")
        for tier in [5, 10]:
            R['fight%d' % tier] = await pg.evaluate("""async (tier)=>{const G=__G;G.SAVE.shards=999999;G.SAVE.diff.max=14;G.SAVE.diff.sel=tier;G.startGame('wolf');const P=G.P;P.bossK='shk';__lv(20);G.raiseCastle();G.enterArena();for(let i=0;i<60;i++)G.tick(1/30);
              const b=G.boss; const seen={}; let lost=0, maxSp=0, pools=0, adds=0, guardSeen=false, stun=false;
              const run=(n,f)=>{for(let i=0;i<n;i++){P.hp=P.max;const h0=P.hp;G.tick(1/30);if(G.state!=='play')__s();lost+=Math.max(0,h0-P.hp);if(b.st)seen[b.st]=1;maxSp=Math.max(maxSp,G.shkSp.length);pools=Math.max(pools,G.zones.filter(z=>z.type==='spool').length);if(b.guard)guardSeen=true;if(b.st==='stun')stun=true;if(f)f(i);}};
              run(90);
              for(const k of ['spray','bomb','ring','spike','stomp']){b.st='chase';b.stT=0;G.shkStart(b,k);run(130);}
              b.hp=b.max*0.74; run(80); adds=G.enemies.filter(e=>e.shkAdd&&e.hp>0).length; const invulSum=b.st==='summon'||seen.summon;
              run(30); const guard=b.guard; for(const e of G.enemies) if(e.shkAdd) e.hp=0; run(10);
              const st2=b.st;
              b.hp=b.max*0.24; run(10); b.hp=b.max*0.2; run(90); const adds3=G.enemies.filter(e=>e.shkAdd&&e.hp>0).length;
              b.invul=false;b.guard=false;b.hp=1; G.hurtEnemy(b,999,0,0,0); run(30);
              return {tier:P.tier,fset:P.fset,sea:!!(G.arena&&G.arena.sea),states:Object.keys(seen),lostPerS:+(lost/((90+5*130+80+30+10+10+90)/30)).toFixed(1),maxSp,pools,adds,adds3,guard,st2,stun,dead:!G.boss,state:G.state,ph:b.ph,rage:b.rage,errsInside:0};}""", tier)
        # 규칙 9: 가장 센 폭격(11개)이 떨어지는 순간 보스방 바닥 중 안전한 비율
        R['safe'] = await pg.evaluate("""()=>{const G=__G;G.SAVE.diff.sel=9;G.startGame('wolf');const P=G.P;P.bossK='shk';__lv(20);G.raiseCastle();G.enterArena();for(let i=0;i<90;i++){P.inv=99;G.tick(1/30);}const b=G.boss;
              b.rage=true;let worst=1;for(let rep=0;rep<6;rep++){b.st='chase';G.shkStart(b,'bomb');const sp=G.shkSp.map(s=>({x:s.x,y:s.y,r:s.r}));
                let inside=0,hit=0;for(let x=P.x-700;x<=P.x+700;x+=20)for(let y=P.y-500;y<=P.y+500;y+=20){if(!G.inPoly(x,y))continue;inside++;if(sp.some(s=>{const dx=(x-s.x)/(s.r+22),dy=(y-s.y)*1.5/(s.r+22);return dx*dx+dy*dy<1;}))hit++;}
                worst=Math.min(worst,1-hit/inside); G.shkSp.length=0;}
              return {n:11,worstSafeNear:+worst.toFixed(2)};}""")
        # 스크린샷: 폭격 · 소환
        await pg.evaluate("""()=>{const G=__G;G.SAVE.diff.sel=5;G.startGame('wolf');const P=G.P;P.bossK='shk';__lv(20);G.raiseCastle();G.enterArena();for(let i=0;i<90;i++){P.inv=99;G.tick(1/30);}const b=G.boss;
           b.x=P.x+80;b.y=P.y-260;b.st='chase';G.shkStart(b,'bomb');for(let i=0;i<55;i++){P.inv=99;G.tick(1/30);} G.render();}""")
        await pg.screenshot(path=os.path.join(OUT, 'shk_bomb.png'))
        await pg.evaluate("""()=>{const G=__G,P=G.P,b=G.boss;for(let i=0;i<60;i++){P.inv=99;G.tick(1/30);} b.hp=b.max*0.74;for(let i=0;i<50;i++){P.inv=99;G.tick(1/30);} G.render();}""")
        await pg.screenshot(path=os.path.join(OUT, 'shk_summon.png'))
        await pg.evaluate("""()=>{const G=__G,P=G.P,b=G.boss;for(let i=0;i<70;i++){P.inv=99;G.tick(1/30);} for(const e of G.enemies) if(e.shkAdd) e.hp=0; b.st='chase';G.shkStart(b,'spike');for(let i=0;i<20;i++){P.inv=99;G.tick(1/30);} G.render();}""")
        await pg.screenshot(path=os.path.join(OUT, 'shk_spike.png'))
        print(json.dumps(R, ensure_ascii=False, indent=1)); print('errs', pg.errs); await b.close()
asyncio.run(main())
