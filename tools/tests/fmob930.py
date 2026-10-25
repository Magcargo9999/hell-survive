"""v9.30 팔열지옥 잡몹 10종 · 영혼 심장 레전더리 조각 15~25 이전 · 임프 공격력 · 루드라 2페이즈"""
import asyncio,sys,json
sys.path.insert(0,'/home/claude/hell-survive/tools')
from playwright.async_api import async_playwright
import h301
STEP="if(G.state!=='play'&&G.state!=='over'&&G.state!=='win')__s();"
async def main():
    async with async_playwright() as pw:
        b=await pw.chromium.launch(); pg=await h301.newpage(b,1280,720); errs=[]
        pg.on('pageerror',lambda e:errs.append(str(e)[:160]))
        await pg.wait_for_function('__G.IMG&&__G.IMG.boss&&__G.IMG.fmob&&__G.FSPECIES&&__G.FSPECIES.length',timeout=90000)
        R=await pg.evaluate("""()=>{const G=__G,o={};o.n=G.FSPECIES.length;o.names=G.FSPECIES.map(s=>s.name).join(',');
          G.SAVE.diff.max=24;G.SAVE.diff.sel=0;G.SAVE.shards=1e7;G.startGame('wolf');const P=G.P;P.fset='fire';P.tier=26;G.clearGround&&G.clearGround();__lv(24);
          for(let i=0;i<60*30;i++){G.tick(1/30);"""+STEP+"""}
          const sp=new Set(G.enemies.filter(e=>e.kind==='mob').map(e=>e.spec.name));o.field=sp.size;o.list=[...sp].join(',');o.fireOK=G.enemies.every(e=>e.kind!=='mob'||G.FSPECIES.includes(e.spec));
          for(let i=0;i<600;i++){G.tick(1/30);"""+STEP+"""}G.render();o.hp=Math.round(P.hp);return o}""")
        print('A',json.dumps(R,ensure_ascii=False)); await pg.screenshot(path='/home/claude/hell-survive/build/fire_mobs.png')
        R=await pg.evaluate("""()=>{const G=__G,o={};const S=G.SAVE;S.heart.inv=[{id:'h1',g:'legend',b:'fuse',st:'shard',v:38,st2:'atk',v2:17,st3:'shard',v3:31},{id:'h2',g:'unique',st:'shard',v:27},{id:'h3',g:'legend',st:'shard',v:18}];
          G.heartMigrate();o.v=S.heart.inv.map(h=>[h.v,h.v2,h.v3].join('/'));
          o.roll=G.hRange('legend','shard');o.imp=G.IMP.hitDm;return o}""")
        print('B',json.dumps(R,ensure_ascii=False))
        print('errs',errs[:5]); await b.close()
asyncio.run(main())
