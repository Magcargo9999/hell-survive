"""v10.28 QA: 보스 러시 1라운드엔 호랑이 불의 십자가·어인왕 산소 기믹이 없고, 2라운드에선 있다 (보스 러시 전용 빌드로 큐를 정해 확인)
사용: PYTHONPATH=tools GAME_URL=http://localhost:8765/bossrush.html python3 tools/tests/r1028.py"""
import asyncio, sys, os, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from playwright.async_api import async_playwright
import h301
async def main():
    async with async_playwright() as pw:
        b = await pw.chromium.launch(); pg = await h301.newpage(b, 960, 600); R = {}
        await pg.wait_for_function("__G.IMG&&__G.IMG.boss", timeout=90000)
        for q in (['tig', 'monkey'], ['kng', 'tig'], ['monkey', 'kng']):
            R['/'.join(q)] = await pg.evaluate("""async(q)=>{const G=__G;G.broQ=q;G.BRO_OPT.mods='off';G.buildCards();document.querySelector('#charCards .card[data-c="wolf"]').click();document.getElementById('startBtn').click();
              let g=0;while(g++<900){if(__s())continue;if(G.state==='play'&&G.rush&&G.rush.init){G.tick(1/30);continue}break}const out=[];
              for(let k=0;k<2;k++){for(let i=0;i<4000;i++){G.P.inv=99;G.P.hp=G.P.max;while(__s());G.tick(1/30);if(G.boss&&G.boss.st!=='intro'&&G.rush.ph==='fight')break;if(i%10===0)await new Promise(r=>setTimeout(r,60))}
                for(let i=0;i<300;i++){G.P.inv=99;G.P.hp=G.P.max;G.tick(1/30)}
                out.push({bk:G.boss&&(G.boss.bk||'monkey'),round:G.rush.round,cross:!!(G.TGW&&G.TGW.cr),o2:Math.round(G.P.o2)});
                const e=G.boss;for(let t=0;t<40&&e&&e.hp>0;t++){e.invul=false;e.st=e.st==='guard'?'chase':e.st;e.hp=1;G.hurtEnemy(e,1e9,0,0,0,false);for(let i=0;i<10;i++){G.P.inv=99;while(__s());G.tick(1/30)}}for(let i=0;i<60;i++){G.P.inv=99;while(__s());G.tick(1/30)}}
              G.state='menu';return out}""", q)
        print(json.dumps(R))
        a, c, d = R['tig/monkey'], R['kng/tig'], R['monkey/kng']
        ok = a[0]['bk'] == 'tig' and not a[0]['cross'] and c[0]['bk'] == 'kng' and c[0]['o2'] == 100 and c[1]['bk'] == 'tig' and c[1]['cross'] and d[1]['bk'] == 'kng' and d[1]['o2'] < 100
        print('OK' if ok else 'FAIL'); await b.close()
asyncio.run(main())
