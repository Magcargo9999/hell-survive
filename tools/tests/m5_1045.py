"""v10.45 Lv.5 숙련: 5레벨 카드 20장 모두 5장째에 보상이 한 번만 적용되는지 · 문구 · 런타임 효과"""
import asyncio, json
from playwright.async_api import async_playwright
from h301 import newpage
JS_START = "(c)=>{const G=__G;G.SAVE.diff.max=0;document.querySelector(`#charCards .card[data-c=${c}]`).click();G.startGame();for(let i=0;i<30;i++)G.tick(1/30);}"
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); pg = await newpage(b)
        await pg.evaluate(JS_START, 'wolf')
        r = await pg.evaluate("""()=>{const G=__G,P=G.P,out={};const defs=G.UPGRADES.concat(G.UNIQUE.wolf);
          const card=id=>{const u=defs.find(u=>u.id===id);return G.cardView(u)};
          for(const id of Object.keys(G.MASTER)){const u=defs.find(u=>u.id===id);if(!u){out[id]='nodef';continue}
            const snap=()=>({dmg:P.dmg,aspd:P.aspd,spd:P.spd,max:P.max,pick:P.pickup,rng:P.rng,orb:P.orbsN,knock:P.knock,crit:P.crit,armor:P.armor,exp:P.expMul,kh:P.killHeal});
            const v4=card(id); const s0=snap(); for(let i=0;i<4;i++)G.takeCard(card(id)); const v5=card(id); const s4=snap(); G.takeCard(v5); const s5=snap(); const vx=card(id);
            const d=k=>+(s5[k]-s4[k]).toFixed(3), d0=k=>+((s4[k]-s0[k])/4).toFixed(3);
            out[id]={lv:P.up[id], backHint:(v4.syn||'').includes('Lv.5 숙련'), front5:(v5.desc||'').includes('Lv.5 숙련'), sub5:v5.sub,
              step4:{dmg:d0('dmg'),aspd:d0('aspd'),max:d0('max'),crit:d0('crit'),exp:d0('exp'),knock:d0('knock'),kh:d0('kh')},
              step5:{dmg:d('dmg'),aspd:d('aspd'),max:d('max'),crit:d('crit'),exp:d('exp'),knock:d('knock'),kh:d('kh'),orb:s5.orb-s4.orb,spd:+(s5.spd/s4.spd).toFixed(3),pick:+(s5.pick/s4.pick).toFixed(2),rng:+(s5.rng/s4.rng).toFixed(3),armor:+(s5.armor/s4.armor).toFixed(3)},
              hpFull:P.hp===P.max, m5:G.m5on(id)};
          }
          // 런타임: 빙결 지속 · 점화 지속 · 뼈 튕김 2회 · 방어막 밀침
          const e=G.spawnEnemy(0,600);G.freezeE(e,true);out.frzDur=+(e.frzT-G.gt).toFixed(2);G.igniteX(e,true);out.ignT=e.ignT;
          const e2=G.spawnEnemy(0,600);e2.x=P.x+120;e2.y=P.y;const e3=G.spawnEnemy(0,600);e3.x=P.x+400;e3.y=P.y;
          P.guardT=0;P.inv=0;P.shield=0;const bx=e2.x;G.hurt(10);out.guardPush=+(e2.x-bx).toFixed(0);out.guardFar=+(e3.x-(P.x+400)).toFixed(0);
          return out}""")
        print(json.dumps(r, ensure_ascii=False, indent=0))
        bad=[k for k,v in r.items() if isinstance(v,dict) and (v['lv']!=5 or not v['backHint'] or not v['front5'] or not v['m5'])]
        print('BAD', bad, 'errs', pg.errs)
        # 두 번 더 올려도(챌린지 한계 돌파 가정) 숙련이 다시 적용되지 않는지
        r2 = await pg.evaluate("""()=>{const G=__G,P=G.P;const u=G.UPGRADES.find(u=>u.id==='claw');const d=P.dmg;P.up.claw=6;G.takeCard(G.cardView(u));return +(P.dmg/d).toFixed(3)}""")
        print('claw lv7 ratio (1.14 expected)', r2)
        await b.close()
asyncio.run(main())
