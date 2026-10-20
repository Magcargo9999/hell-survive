import asyncio,sys,os
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
os.makedirs('build/audit',exist_ok=True)
from playwright.async_api import async_playwright
from h301 import newpage
from PIL import Image
CASES=[('wolf','crimson','blood','wolf_blood'),('wolf','crimson','holy','wolf_holy'),('wolf','abyss','','wolf_abyss'),('wolf','twin','','wolf_twin'),
('snail','venom','','snail_venom'),('snail','lava','','snail_lava'),
('archer','elf','red','arch_red'),('archer','elf','holy','arch_holy'),('archer','skel','','arch_skel'),
('chimera','flame','','chim_flame'),('chimera','dream','','chim_dream'),('lizard','','rage','liz_rage'),('lizard','','water','liz_water'),('chimera','','','chim_wind'),('twins','','','twins')]
JS="""([ch,route,fin])=>{const G=__G; Object.assign(G.SAVE.chars,{wolf:true,snail:true,archer:true,chimera:true,lizard:true,twins:true}); G.startGame(ch); const P=G.P;
 const pick=()=>{const t=document.getElementById('levelTitle').textContent;const c=G.choices; let i=0;
   if(t.indexOf('갈림길')>=0||t.indexOf('최종')>=0){const want=t.indexOf('최종')>=0?fin:route; i=c.findIndex(u=>u.key===want&&!u.locked); if(i<0)i=c.findIndex(u=>!u.locked); if(i<0)i=0;}
   G.pick(i)};
 let g=0; while(P.lvl<26&&g++<12000){ if(G.state==='levelup'){pick();continue} if(G.state==='evolve'){G.tick(1/30);continue}
   if(G.state==='play'){ if(P.lvl>=3){P.up.thirst=Math.max(1,P.up.thirst||0);P.up.speed=Math.max(2,P.up.speed||0);P.up.heart=Math.max(2,P.up.heart||0);P.lavaT=Math.max(5,P.lavaT);P.bugF0=true;P.low10=true; if(ch==='archer'&&route==='skel')P.poisoned=true; if(ch==='archer'&&fin==='holy'){P.up.snipe=Math.max(1,P.up.snipe||0);P.potions=Math.max(8,P.potions||0);}} P.hp=P.max;P.inv=9;G.addExp(P.need);G.tick(1/30)} else break }
 while(G.state==='levelup'||G.state==='evolve'){ if(G.state==='levelup')pick(); else G.tick(1/30);}
 return {route:P.route,fin:P.fin,form:P.form,skill:P.skill,lvl:P.lvl,max:P.max,dmg:Math.round(P.dmg)}}"""
JS2="""()=>{const G=__G,P=G.P; G.enemies.length=0; P.inv=0; G.enterArena(); for(let i=0;i<90;i++){G.tick(1/30)}
 let n=0; for(let i=0;i<1500;i++){ P.hp=P.max; P.skT=0; if(P.skill) G.cast(); G.tick(1/30); n++; if(G.state==='dead')break; }
 return {boss:G.boss?Math.round(G.boss.hp):0,state:G.state,hp:Math.round(P.hp)}}"""
async def main():
    only=sys.argv[1:] 
    async with async_playwright() as pw:
        b=await pw.chromium.launch()
        for ch,rt,fin,name in CASES:
            if only and name not in only: continue
            pg=await newpage(b,900,560)
            r=await pg.evaluate(JS,[ch,rt,fin])
            await pg.evaluate("()=>{const G=__G;G.enemies.length=0;for(let i=0;i<40;i++){G.P.inv=9;G.tick(1/30)}}")
            await pg.screenshot(path='build/audit/sm_%s.png'%name,clip={'x':330,'y':190,'width':240,'height':180})
            r2=await pg.evaluate(JS2)
            print(name,r,r2,pg.errs[:2]); await pg.close()
        await b.close()
asyncio.run(main())
