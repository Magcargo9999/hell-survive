"""v10.18: 러시 25층 해금 · 체력비례 계수 · 듀라한 버프 · 잃어버린 머리 쿨타임(돌아온 뒤부터)"""
import asyncio, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from playwright.async_api import async_playwright
import h301
async def main():
    async with async_playwright() as pw:
        b = await pw.chromium.launch(); pg = await h301.newpage(b, 1280, 720); await pg.wait_for_timeout(1500)
        o = await pg.evaluate("""()=>{const G=__G,S=G.SAVE,o={};
          S.diff.clr=23;S.dex.kills={};o.lock=G.rushReady();S.diff.clr=24;o.open=G.rushReady();
          S.diff.max=5;S.diff.clr=29;
          const t=(ch,fn)=>{G.startGame(ch);const P=G.P;fn&&fn(P);return [G.pctMelee(),+G.pctMul().toFixed(3)]};
          o.twins=t('twins',P=>{P.form=2});
          o.lizard1=t('lizard',P=>{P.form=1});o.lizard0=t('lizard',P=>{P.form=0});
          o.chimDream=t('chimera',P=>{P.form=2;P.route='dream'});o.chimFlame=t('chimera',P=>{P.form=2;P.route='flame'});
          o.snail=t('snail',P=>{P.form=2;P.route='venom'});
          o.fish=[G.FISH.pct,G.FISH.pctCap];o.lh=[G.KN.lh.dur,G.KN.lh.dm];
          S.chars.ghost=true;window.__rt=1;G.startGame('ghost');return o}""")
        await pg.wait_for_function("()=>!!__G.IMG.dk", timeout=60000)
        o2 = await pg.evaluate("""()=>{const G=__G,o={};__lv(22);const P=G.P;G.enemies.length=0;P.skillTipT=0;P.skT=0;
          o.kn=G.isKnight();G.castLostHead();P.skT=28;const a=P.skT;
          for(let i=0;i<60;i++){P.inv=9;P.hp=P.max;G.tick(1/30)}o.frozen=P.skT===a&&!!G.lhead;
          G.lhead.back('x');for(let i=0;i<90;i++){P.inv=9;P.hp=P.max;G.tick(1/30)}
          o.after=P.skT<a&&!G.lhead;o.dbg=[P.skT,!!G.lhead];return o}""")
        r = {**o, **o2}; print(r, pg.errs[:3])
        ok = (r['lock'] is False and r['open'] is True and r['twins']==[True,0.9] and r['lizard1']==[True,1.15] and r['lizard0'][0] is False
              and r['chimDream']==[True,1.15] and r['chimFlame']==[True,1] and r['snail'][1]==1.08 and r['fish']==[0.0078,15.6]
              and r['kn'] and r['frozen'] and r['after'] and r['lh']==[13,2.1])
        print('OK' if ok else 'FAIL'); await b.close()
asyncio.run(main())
