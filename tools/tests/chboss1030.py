"""v10.30 챌린지: 마왕을 무한 맵(필드)에 세워 25초씩 싸워 본다 — 오류 · 마왕이 플레이어에게서 멀어지는지 · 피해가 들어가는지 · 처치 뒤 보상창
사용: PYTHONPATH=tools GAME_URL=http://localhost:8765/build/hell_survive.html python3 tools/tests/chboss1030.py [마왕...]"""
import asyncio, sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from playwright.async_api import async_playwright
import h301
SETUP = """()=>{const G=__G,S=G.SAVE;S.ch.open=true;S.diff.max=39;S.diff.clr=38;S.shards=99999;for(const k of ['boss','boss2','boss3','boss4','boss6','boss7','boss8','boss9','boss10','boss11','boss12','boss14','boss15','boss16','boss17','boss18','boss19','boss20','boss21','boss22','boss23','boss24'])S.dex.kills[k]=1;G.setChMode&&G.setChMode(true)}"""
async def main():
    only = sys.argv[1:]
    async with async_playwright() as pw:
        b = await pw.chromium.launch(); pg = await h301.newpage(b, 1280, 760); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e))); pg.on('console', lambda m: errs.append(m.text) if m.type == 'error' else None)
        await pg.evaluate(SETUP)
        await pg.evaluate("()=>{const G=__G;G.startChallenge('wolf')}")
        for i in range(120):
            st = await pg.evaluate("()=>__G.state+','+!!__G.chal")
            if st == 'play,true': break
            await pg.wait_for_timeout(250)
        pool = await pg.evaluate("()=>__G.chBossPool()")
        print('pool', pool)
        await pg.evaluate("()=>{__lv(30)}")
        if os.environ.get('SHOT'): await pg.evaluate("()=>{window.__shot=1}")
        R = {}
        for k in (only or pool):
            n0 = len(errs)
            r = await pg.evaluate("""async(k)=>{const G=__G,c=G.chal,P=G.P;
              for(const e of G.enemies)if(e.kind==='boss'||e.kind==='mini')e.hp=0;
              const imgs=(G.BR_IMGS&&G.BR_IMGS[k])||[];
              c.bossOn=true;c.bossK=k;c.siren=0;c.waitB=0;G.chEnterBoss(k);
              for(let i=0;i<300&&(!G.boss||G.boss.hp<=0);i++){c.siren=0;c.waitB=0;G.tick(1/30);G.chEnterBoss(k);await new Promise(r=>setTimeout(r,50))}
              const B=G.boss;if(!B)return {err:'no boss'};const bk=B.bk||'monkey',h0=B.hp;let dmax=0,dsum=0,n=0,far=0,t0=performance.now();
              const cx=P.x,cy=P.y;
              for(let i=0;i<750;i++){P.inv=99;P.hp=P.max;while(__s());const a=i/90;P.x=cx+Math.cos(a)*260;P.y=cy+Math.sin(a)*200;G.tick(1/30);
                if(!G.boss||G.boss.hp<=0)break;const d=Math.hypot(G.boss.x-P.x,G.boss.y-P.y);dmax=Math.max(dmax,d);dsum+=d;n++;if(d>1300)far++;
                if(i%60===0)await new Promise(r=>setTimeout(r,1));if(window.__shot&&i===300)break}
              const ms=performance.now()-t0,B2=G.boss;
              const out={bk,hpPct:B2?+(100*B2.hp/B2.max).toFixed(1):0,dmax:Math.round(dmax),davg:Math.round(dsum/Math.max(1,n)),far,ms:Math.round(ms),fb:c.fbC?[Math.round(c.fbC.x-cx),Math.round(c.fbC.y-cy)]:null};
              if(window.__shot)return out;
              if(B2){B2.invul=false;B2.st=B2.st==='intro'?'chase':B2.st;G.hurtEnemy(B2,B2.hp+1e9,0,0,0,false)}
              for(let i=0;i<150&&G.state==='play';i++){P.inv=99;G.tick(1/30)}
              out.after=G.state+':'+(document.getElementById('levelTitle').textContent||'').slice(0,14);
              if(G.state==='levelup'){G.pick(0)}
              for(let i=0;i<30;i++){P.inv=99;while(__s());G.tick(1/30)}
              out.left=G.enemies.filter(e=>['boss','snb','stlb','lmir','ttr'].includes(e.kind)&&e.hp>0).length;
              return out}""", k)
            if os.environ.get('SHOT'):
                await pg.screenshot(path=os.path.join(h301.ROOT, 'build', 'qa', 'chb_' + k + '.png'))
                await pg.evaluate("()=>{const G=__G,B=G.boss;if(B){B.invul=false;G.hurtEnemy(B,B.hp+1e9,0,0,0,false)}for(let i=0;i<200;i++){G.P.inv=99;while(__s());G.tick(1/30)}}")
            r['errs'] = errs[n0:n0 + 3]
            R[k] = r; print(k, json.dumps(r, ensure_ascii=False)[:400])
        await b.close()
asyncio.run(main())
