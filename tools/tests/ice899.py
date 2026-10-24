"""v8.99 팔한지옥(지하 21~25층): 세이브 이전(20층 클리어 기록 → 21층 개방) · 21·22층만 열림 · 새 세트(바닥·잡몹 9종·소품) · 미끄러운 얼음 관성 · 위험 균열 · 마왕 10종 보스방 · 층 고르기 UI"""
import asyncio,sys,json
sys.path.insert(0,'/home/claude/hell-survive/tools')
from playwright.async_api import async_playwright
import h301
h301.URL='file:///home/claude/hell-survive/build/hell_survive.html'
B='/home/claude/hell-survive/build/'
SAVE_OLD={"shards":99999,"perks":{},"chars":{"wolf":True},"diff":{"max":19,"sel":19,"fw":False},"rush":{"open":True,"best":0,"clears":0}}
async def main():
    async with async_playwright() as pw:
        b=await pw.chromium.launch()
        # 1) 예전 세이브(20층까지 깸 = 보스 러시 해금) → 21층 개방, 깨지 않은 세이브는 그대로
        for name,sv,exp in [('cleared20',SAVE_OLD,20),('notcleared',{**SAVE_OLD,'diff':{"max":12,"sel":12,"fw":False},'rush':{"open":False}},12),('tooHigh',{**SAVE_OLD,'diff':{"max":24,"sel":24,"fw":False}},21)]:
            ctx=await b.new_context(viewport={'width':1280,'height':720}); await ctx.add_init_script("localStorage.setItem('hellSurvivorSave1',%s)"%json.dumps(json.dumps(sv)))
            pg=await ctx.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
            await pg.goto(h301.URL); await pg.wait_for_function('window.__G&&__G.ready',timeout=60000)
            m=await pg.evaluate("__G.SAVE.diff.max"); print(name,'max',m,'expected',exp,'OK' if m==exp else 'FAIL', errs); await ctx.close()
        pg=await h301.newpage(b,1280,720)
        await pg.wait_for_function('__G.IMG&&__G.IMG.ifloor&&__G.IMG.iprops&&__G.IMG.imob&&__G.ISPECIES.length',timeout=90000)
        R=await pg.evaluate("""()=>{const G=__G,o={};G.SAVE.diff.max=21;G.SAVE.shards=1e7;
          G.renderHells();const tabs=[...document.querySelectorAll('#hellTabs button')].map(b=>b.textContent+(b.disabled?'[x]':''));o.tabs=tabs;
          G.SAVE.diff.sel=21;G.renderHells();o.floors=[...document.querySelectorAll('#hellFloors button')].map(b=>b.textContent+(b.disabled?'[x]':''));
          o.pick23=G.pickFloor(22);o.pick22=G.pickFloor(21);
          o.nspec=G.ISPECIES.length;o.names=G.ISPECIES.map(s=>s.name);
          return o}""")
        print(json.dumps(R,ensure_ascii=False))
        R=await pg.evaluate("""()=>{const G=__G,o={};G.SAVE.diff.max=21;G.SAVE.shards=1e7;
          for(const t of [19,20,21]){G.SAVE.diff.sel=t;G.startGame('wolf');let sl=0,lv=0,both=0,n=0;for(let x=-60;x<60;x++)for(let y=-60;y<60;y++){n++;const a=G.isIceSlip(x,y),l=G.isLava(x,y);if(a)sl++;if(l)lv++;if(a&&l)both++}
            o['t'+t]={fset:G.P.fset,boss:G.P.bossK,slip:+(100*sl/n).toFixed(1),lava:+(100*lv/n).toFixed(1),both}}
          const bs={};for(let i=0;i<400;i++){const k=G.pickBossK(20+(i%5));bs[k]=(bs[k]||0)+1}o.bosses=bs;return o}""")
        print(json.dumps(R))
        # 2) 미끄러운 얼음 관성: 오른쪽으로 걷다 키를 떼면 미끄러지는 거리 (얼음 위 vs 보통 바닥)
        async def slide(slip):
            T=await pg.evaluate("""(slip)=>{const G=__G;G.SAVE.diff.sel=20;G.startGame('wolf');const P=G.P;let T=null;
              for(let r=6;r<80&&!T;r++)for(let a=0;a<120&&!T;a++){const x=Math.round(Math.cos(a/16)*r),y=Math.round(Math.sin(a/16)*r);let ok=true;for(let i=-3;i<9;i++){if(G.isIceSlip(x+i,y)!==slip||G.isLava(x+i,y)||G.isLava(x+i,y+1))ok=false}if(ok)T=[x,y]}
              if(!T)return null;G.enemies.length=0;P.hp=P.max=99999;P.inv=99;P.x=(T[0]+0.5)*64;P.y=(T[1]+0.5)*64;G.tick(1/30);return T}""",slip)
            if not T: return None
            await pg.keyboard.down('KeyD')
            await pg.evaluate("()=>{for(let i=0;i<8;i++){__G.P.inv=99;__G.tick(1/30)}}")
            await pg.keyboard.up('KeyD')
            return await pg.evaluate("""()=>{const G=__G,P=G.P,x0=P.x;let n=0;for(let i=0;i<20;i++){P.inv=99;G.tick(1/30)}return {slide:Math.round(P.x-x0),slipT:+(P.slipT||0).toFixed(2)}}""")
        print('slide on ice',await slide(True)); print('slide on floor',await slide(False))
        # 3) 마왕 10종 보스방 (팔한지옥에서는 그 마왕의 원래 맵)
        R=await pg.evaluate("""()=>{const G=__G,o={};G.SAVE.diff.sel=21;
          for(const bk of G.ICE_L){G.startGame('wolf');G.P.hp=G.P.max=99999;G.P.bossK=bk;G.enterArena();for(let i=0;i<40;i++){G.P.inv=99;G.tick(1/30)}o[bk]={arena:!!G.arena,boss:!!G.boss,mush:G.arena&&G.arena.mush,gard:G.arena&&G.arena.gard,sea:G.arena&&G.arena.sea,k:G.arena&&G.arena.k}}
          return o}""")
        print(json.dumps(R))
        # 4) 스크린샷: 얼음 웅덩이 근처
        await pg.evaluate("""()=>{const G=__G,P=G.P;G.SAVE.diff.sel=20;G.startGame('wolf');let T=null;
          for(let r=6;r<80&&!T;r++)for(let a=0;a<120&&!T;a++){const x=Math.round(Math.cos(a/16)*r),y=Math.round(Math.sin(a/16)*r);if(G.isIceSlip(x,y)&&G.isIceSlip(x+1,y)&&G.isIceSlip(x,y+1)&&G.isIceSlip(x+1,y+1))T=[x,y]}
          P.x=(T[0]+1)*64;P.y=(T[1]+3)*64;G.enemies.length=0;for(let i=0;i<60;i++){P.inv=99;P.hp=P.max;G.tick(1/30)}for(let e=0;e<14;e++)G.spawnEnemy(e*0.45,260+e*10);for(let i=0;i<5;i++)G.tick(1/30);G.render()}""")
        await pg.screenshot(path=B+'ice899.png')
        print('errs',pg.errs); await b.close()
asyncio.run(main())
