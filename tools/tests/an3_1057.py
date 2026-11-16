"""v10.57 타락천사 새 버전(보스전 체험): 입장 · 패턴 전부 · 페이즈 · 처치 · 오류 + 화면"""
import asyncio, sys
from playwright.async_api import async_playwright
from h301 import newpage
START = """async (c)=>{const G=__G;G.startBossTrial('an3',c);let n=0;
  while(n++<4000){ if(__s())continue; if(G.arena&&G.boss&&G.boss.bk==='angel'&&G.boss.st!=='intro')break; G.P.hp=G.P.max;G.P.inv=9;G.tick(1/30); if(n%40===0)await new Promise(r=>setTimeout(r,30)); }
  const b=G.boss;return b?{bk:b.bk,v2:!!b.v2,anV:G.anV,hp:Math.round(b.hp),lvl:G.P.lvl,tier:G.P.tier,trial:!!G.rush.trial}:{st:G.state,n,lv:G.P.lvl}}"""
FORCE = """([k,ph,secs])=>{const G=__G,P=G.P,e=G.boss;e.tele=[];e.ph=ph;e.hp=e.max*(ph===1?0.9:ph===2?0.45:0.2);e.st='chase';e.stT=0;e.shT=0;e.orbCd=0;e.jgCd=0;e.wvCd=0;e.shCd=0;
 const d=Math.hypot(P.x-e.x,P.y-e.y);e.last='';const ks={};let hit=0;const h0=P.hp;
 // 강제로 원하는 패턴만 고르게
 const R=Math.random;for(let i=0;i<60*secs;i++){P.inv=0;P.hp=P.max;if(e.st==='chase'&&e.stT<=0){Math.random=()=>0;}G.tick(1/60);Math.random=R;}
 return {st:e.st,last:e.last,tele:e.tele.length}}"""
async def shot(pg, name): await pg.wait_for_timeout(120); await pg.screenshot(path=f'build/an3/{name}.png')
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); pg = await newpage(b, 1280, 720)
        print(await pg.evaluate(START, sys.argv[1] if len(sys.argv) > 1 else 'wolf'))
        # 패턴별: 시작시켜 놓고 몇 프레임 진행 → 화면
        for k, ph, t, name in (('slash', 1, 0.5, 'p1_slash'), ('slash', 1, 1.9, 'p1_lunge'), ('dash', 1, 0.6, 'p1_dash'), ('dash', 1, 1.05, 'p1_dashgo'), ('rhythm', 1, 1.0, 'p1_rhythm'), ('shield', 1, 1.6, 'p1_shield'), ('pillars', 1, 0.9, 'p1_pillars'),
                               ('spears', 2, 1.0, 'p2_spears'), ('judge', 2, 1.2, 'p2_judge'), ('judge', 2, 2.2, 'p2_judge2'), ('orbs', 2, 1.6, 'p2_orbs'), ('waves', 3, 1.1, 'p3_waves')):
            r = await pg.evaluate("""([k,ph,t])=>{const G=__G,P=G.P,e=G.boss;e.tele=[];e.beat=null;e.ph=ph;e.hp=e.max*(ph===1?0.9:ph===2?0.45:0.2);e.shT=0;e.orbCd=0;e.jgCd=0;e.wvCd=0;e.shCd=0;e.invul=false;e.alpha=1;
              const A=G.AMAP;e.x=A.cx;e.y=A.cy;P.x=A.cx+(k==='dash'?520:k==='judge'?330:200);P.y=A.cy+60;e.last='';
              e.last=k;G.an3Start(e,k);const got=k;
              let hits=0;for(let i=0;i<Math.round(t*60);i++){P.inv=1;P.hp=P.max;G.tick(1/60)}return {want:k,got,st:e.st,tele:e.tele.map(q=>(q.an||q.k)+(q.k==='rect'?':'+q.rgb+':'+(q.t|0)+':'+q.dur:'')).join(',')}}""", [k, ph, t])
            print(name, r); await shot(pg, name)
        # 실제 전투: 무적 상태로 자동 공격하며 끝까지 (패턴 기록)
        r = await pg.evaluate("""async()=>{const G=__G,P=G.P,e=G.boss;e.hp=e.max;e.ph=1;e.st='chase';e.tele=[];const seen={};let n=0,ph3=0;const B=e;
          while(n++<60*400&&G.state==='play'&&B.hp>0){P.inv=1;P.hp=P.max;if(B.last)seen[B.last]=(seen[B.last]||0)+1;if(B.ph===3)ph3=1;
            if(n%15===0&&!B.invul){B.hp-=B.max*0.0012;} if(B.hp<=0){G.bossDefeated(B);break;} G.tick(1/60); if(n%600===0)await new Promise(r=>setTimeout(r,5));}
          return {n,state:G.state,hp:Math.round(B.hp),ph:B.ph,ph3,seen:Object.keys(seen)}}""")
        print('fight', r)
        await pg.evaluate("()=>{for(let i=0;i<70;i++)__G.tick(1/30)}"); await shot(pg, 'death')
        print('errs', pg.errs); await b.close()
if __name__ == "__main__": asyncio.run(main())
