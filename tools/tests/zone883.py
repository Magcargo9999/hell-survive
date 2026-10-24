"""v8.83 달팽이 장판 빙결/점화(쿨 1.2초) · 용암 대분출이 흔적을 안 터뜨림 · 토끼 후드 늑대 0진화만 · 러시 시작 증강"""
import asyncio,sys,json
sys.path.insert(0,'/home/claude/hell-survive/tools')
from playwright.async_api import async_playwright
import h301
h301.URL='file:///home/claude/hell-survive/build/hell_survive.html'
async def main():
    async with async_playwright() as pw:
        b=await pw.chromium.launch(); pg=await h301.newpage(b,1280,720)
        await pg.wait_for_function('__G.IMG&&__G.IMG.boss',timeout=60000)
        r=await pg.evaluate("""()=>{const G=__G;G.SAVE.chars.snail=true;G.startGame('snail');const P=G.P;P.up.freeze=3;P.up.ignite=3;
          const mk=()=>{G.spawnEnemy&&0;};
          G.enemies.length=0;const e={kind:'mob',x:P.x+50,y:P.y,kx:0,ky:0,sp:0,spec:null,sc:1,r:14,hp:1e9,max:1e9,dmg:0,exp:0,elite:false,flash:0,slowT:0,t:0};G.enemies.push(e);
          G.zones.push({type:'lavapool',x:e.x,y:e.y,r:200,life:30,max:30,tick:0,dm:0.3,sp:0});
          let fz=0,ig=0,ticks=0;const seen=new Set();for(let i=0;i<30*20;i++){e.hp=1e9;G.tick(1/30);if(e.frzT>G.gt&&!seen.has('f'+Math.floor(e.frzT*10))){seen.add('f'+Math.floor(e.frzT*10));fz++}if(e.ignT>0&&!e.counted){e.counted=1;ig++}if(e.ignT<=0)e.counted=0}
          return {freezes:fz,ignites:ig}}""")
        print(json.dumps(r))
        r=await pg.evaluate("""()=>{const G=__G;const s=G.SKINS.find(q=>q.id==='wolfB');return [s.forms,s.where]}""")
        print(json.dumps(r,ensure_ascii=False))
        r=await pg.evaluate("""()=>{const G=__G;G.SAVE.chars.wolf=true;G.startRush('wolf');const P=G.P;let g=0,ch=0;while(g++<600&&(G.state==='levelup'||G.state==='evolve'||G.rush.init)){if(G.state==='play')G.tick(1/30);else{if(G.state==='levelup')ch++;__s()}}
          return {lvl:P.lvl,auto:G.rush.got,chosen:ch,left:G.rush.autoN}}""")
        print(json.dumps(r,ensure_ascii=False)); print('errs',pg.errs[:5]); await b.close()
asyncio.run(main())
