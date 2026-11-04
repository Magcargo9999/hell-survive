"""v10.28 QA: 마안군주 탄막 도중 바닥 장판(낙하·심판·촉수·난이도 추가 패턴)이 겹치는지 — 내 둘레 760 안에 마안탄 4발 이상 + 예고 장판이 동시에 있는 프레임 수
사용: PYTHONPATH=tools GAME_URL=... python3 tools/tests/eye1028.py [단계=9] [초=120]"""
import asyncio, sys, os, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from playwright.async_api import async_playwright
import h301
async def main():
    tier = int(sys.argv[1]) if len(sys.argv) > 1 else 9; secs = float(sys.argv[2]) if len(sys.argv) > 2 else 120
    async with async_playwright() as pw:
        b = await pw.chromium.launch(); pg = await h301.newpage(b, 960, 600)
        await pg.wait_for_function("__G.IMG&&__G.IMG.boss", timeout=90000)
        r = await pg.evaluate("""async([tier,secs])=>{const G=__G;G.SAVE.diff.max=40;G.SAVE.shards=1e7;G.SAVE.diff.sel=tier;G.startGame('wolf');for(let i=0;i<80&&G.state!=='play';i++)await new Promise(r=>setTimeout(r,250));
          __lv(22);G.P.bossK='eye';G.raiseCastle();G.enterArena();for(let i=0;i<300;i++){G.P.inv=9;G.tick(1/30);if(G.boss&&G.boss.st!=='intro')break;if(i%10===0)await new Promise(r=>setTimeout(r,40))}
          let both=0,fr=0,rage=false;const P=G.P;for(let i=0;i<secs*30;i++){P.inv=9;P.hp=P.max;if(G.boss){G.boss.hp=Math.max(G.boss.hp,G.boss.max*0.3);if(i===secs*15){G.boss.hp=G.boss.max*0.45}}
            G.tick(1/30);const e=G.boss;if(!e)break;fr++;const nb=G.ebul.filter(q=>Math.hypot(q.x-P.x,q.y-P.y)<760).length,fl=e.tele.some(t=>t.t>=0&&!t.done&&(t.k==='circle'||t.k==='rect'||t.k==='donut'));if(nb>=4&&fl)both++;}
          return {frames:fr,overlap:both,pct:+(both/fr*100).toFixed(1),ex:G.boss&&G.boss.ex}}""", [tier, secs])
        print(json.dumps(r)); await b.close()
asyncio.run(main())
