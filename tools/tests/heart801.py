"""v8.01 보스 심장: 드랍 확률 · 재설정 등급업/스탯 · 장착 5개 제한 · 게임 반영 · 처치 드랍 · 화면/연출 스크린샷"""
import asyncio, os, sys, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from playwright.async_api import async_playwright
from h301 import newpage
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'build', 'shots')
FRESH = "G.SAVE.heart={inv:[],eq:[],n:0};"
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--disable-gpu']); pg = await newpage(b, 1280, 800)
        await pg.wait_for_function('window.__G && __G.IMG', timeout=90000)
        R = {}
        R['drop'] = await pg.evaluate("()=>{const G=__G,c={none:0,rare:0,legend:0},N=200000;for(let i=0;i<N;i++){const r=G.rollHeartDrop();c[r||'none']++;}return {dropPct:+((c.rare+c.legend)/N*100).toFixed(2),legendOfDrops:+(c.legend/(c.rare+c.legend)*100).toFixed(2)};}")
        R['reroll'] = await pg.evaluate("()=>{const G=__G,o={};for(const g of ['rare','epic','unique','legend']){" + FRESH + "let up=0,st={atk:0,hp:0,aspd:0},bad=0,N=60000;const h=G.heartGain(g);for(let i=0;i<N;i++){h.g=g;G.SAVE.shards=1000;const r=G.rerollHeart(h.id);if(r.up)up++;st[r.after.st]++;const H=G.HG[r.after.g];if(r.after.v<H.min||r.after.v>H.max)bad++;if(G.SAVE.shards!==500)bad++;}o[g]={upPct:+(up/N*100).toFixed(2),atk:+(st.atk/N*100).toFixed(1),hp:+(st.hp/N*100).toFixed(1),aspd:+(st.aspd/N*100).toFixed(1),bad};}"
                                   + FRESH + "const h=G.heartGain('rare');G.SAVE.shards=499;o.noMoney=G.rerollHeart(h.id).err||'';return o;}")
        R['equip'] = await pg.evaluate("()=>{const G=__G;" + FRESH + "const ids=[];for(let i=0;i<7;i++)ids.push(G.heartGain('rare').id);const auto=G.SAVE.heart.eq.length;const sixth=G.equipHeart(ids[5]);G.unequipHeart(ids[0]);const after=G.equipHeart(ids[5]);return {auto,sixth,after,eq:G.SAVE.heart.eq.length};}")
        R['apply'] = await pg.evaluate("()=>{const G=__G;" + FRESH + "G.SAVE.chars.wolf=true;G.startGame('wolf');const d0=G.P.dmg,m0=G.P.max,a0=G.P.aspd;G.SAVE.heart={inv:[{id:1,g:'legend',st:'atk',v:20},{id:2,g:'unique',st:'hp',v:9},{id:3,g:'epic',st:'aspd',v:5}],eq:[1,2,3],n:3};G.startGame('wolf');return {dmg:+(G.P.dmg/d0).toFixed(3),max:+(G.P.max/m0).toFixed(3),aspd:+(G.P.aspd-a0).toFixed(3),bonus:G.heartBonus()};}")
        R['bossDrop'] = await pg.evaluate("""()=>{const G=__G;G.SAVE.heart={inv:[],eq:[],n:0};G.HEART.drop=1;G.HEART.legend=1;G.SAVE.shards=99999;G.SAVE.diff.max=14;G.SAVE.diff.sel=3;G.startGame('wolf');const P=G.P;P.bossK='monkey';__lv(12);G.raiseCastle();G.enterArena();for(let i=0;i<60;i++){P.inv=99;G.tick(1/30);}
           const b=G.boss;b.invul=false;b.hp=1;G.hurtEnemy(b,99999,0,0,0);for(let i=0;i<20;i++)G.tick(1/30);G.render();const it=G.items.filter(x=>x.type==='bheart').length;return {item:it,state:G.state};}""")
        await pg.screenshot(path=os.path.join(OUT, 'heart_drop.png'))
        R['bossDrop2'] = await pg.evaluate("""()=>{const G=__G;for(let i=0;i<150;i++)G.tick(1/30);G.HEART.drop=0.2;G.HEART.legend=0.01;return {inv:G.SAVE.heart.inv.map(h=>h.g+':'+h.st+':'+h.v),eq:G.SAVE.heart.eq};}""")
        # 화면
        await pg.evaluate("""()=>{const G=__G;G.SAVE.shards=12000;G.SAVE.heart={inv:[{id:1,g:'legend',st:'atk',v:18},{id:2,g:'unique',st:'hp',v:8},{id:3,g:'epic',st:'aspd',v:5},{id:4,g:'rare',st:'atk',v:2},{id:5,g:'rare',st:'hp',v:3},{id:6,g:'rare',st:'aspd',v:1},{id:7,g:'epic',st:'atk',v:6}],eq:[1,2,3],n:7};document.querySelectorAll('.overlay.show').forEach(o=>o.classList.remove('show'));G.openHeart();}""")
        await pg.wait_for_timeout(400); await pg.screenshot(path=os.path.join(OUT, 'heart_ui.png'))
        await pg.evaluate("""()=>{const G=__G;G.HG.unique.up=1;document.querySelectorAll('.hslot')[1].click();document.getElementById('hReroll').click();G.HG.unique.up=0.05;}""")
        await pg.wait_for_timeout(450); await pg.screenshot(path=os.path.join(OUT, 'heart_fx_legend.png'))
        await pg.wait_for_timeout(3200); await pg.screenshot(path=os.path.join(OUT, 'heart_after.png'))
        await pg.evaluate("()=>__G.playUpgradeEffect('unique')"); await pg.wait_for_timeout(350); await pg.screenshot(path=os.path.join(OUT, 'heart_fx_unique.png'))
        print(json.dumps(R, ensure_ascii=False)); print('errs', pg.errs); await b.close()
asyncio.run(main())
