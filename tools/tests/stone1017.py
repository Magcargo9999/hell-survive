"""v10.17 마석 전부 합산: 레어+에픽+레전더리 = +9%, 일반·보스 러시 모두 적용, 심장은 러시 제외"""
import asyncio, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from playwright.async_api import async_playwright
import h301
async def main():
    async with async_playwright() as pw:
        b = await pw.chromium.launch(); pg = await h301.newpage(b, 1280, 720); await pg.wait_for_timeout(1500)
        r = await pg.evaluate("""()=>{const G=__G,S=G.SAVE;S.diff.clr=29;S.diff.max=5;S.heart.inv=[];S.heart.eq=[];S.stone={inv:[],eq:null,n:0};
          G.startGame('wolf');const d0=G.P.dmg,h0=G.P.max;
          G.stoneGain('rare');G.stoneGain('epic');G.stoneGain('legend');
          G.startGame('wolf');const n=[+(G.P.dmg/d0).toFixed(3),+(G.P.max/h0).toFixed(3),G.runBonus().shard];
          G.startRush('wolf');const u=[G.runBonus().atk,G.runBonus().aspd];
          G.openHeart();G.renderHeart&&G.renderHeart();const t=document.getElementById('hStone').textContent;
          return {n,u,ui:t.indexOf('합계')>=0&&t.indexOf('+9%')>=0}}""")
        print(r, pg.errs[:3]); print('OK' if r['n']==[1.09,1.09,9] and r['u']==[9,9] and r['ui'] else 'FAIL'); await b.close()
asyncio.run(main())
