import os
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
URL=os.environ.get('GAME_URL','file://'+os.path.join(ROOT,'build','hell_survive.html'))
HELP="""()=>{const G=__G;window.__rt=1;window.__fin=0;
 Object.assign(G.SAVE.chars,{wolf:true,snail:true,archer:true,chimera:true,lizard:true,twins:true});
 const cond=()=>{const P=G.P;if(P.lvl>=3){P.up.thirst=Math.max(1,P.up.thirst||0);P.up.speed=Math.max(2,P.up.speed||0);P.up.heart=Math.max(2,P.up.heart||0);P.lavaT=Math.max(5,P.lavaT);P.poisoned=true;P.bugF0=true;P.low10=true;P.taken10=Math.max(P.taken10||0,9999);}};
 window.__cond=cond;
 window.__s=()=>{const s=G.state;const t=document.getElementById('levelTitle').textContent;
 if(s==='levelup'){const c=G.choices;let i=t.indexOf('갈림길')>=0?window.__rt:t.indexOf('최종')>=0?window.__fin:0;if(c[i]&&c[i].locked)i=c.findIndex(u=>!u.locked);G.pick(i);return true}if(s==='evolve'){G.tick(1/30);return true}return false};
 window.__lv=(n)=>{let g=0;while(G.P.lvl<n&&g++<9000){if(__s())continue;if(G.state==='play'){cond();G.P.hp=G.P.max;G.P.inv=9;G.addExp(G.P.need);G.tick(1/30)}else break}while(__s());};
 window.__run=(n)=>{for(let i=0;i<n;i++){G.P.inv=99;G.P.hp=G.P.max;G.tick(1/30)}}}"""
async def newpage(b,w=1000,h=620):
    pg=await b.new_page(viewport={'width':w,'height':h}); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e))); pg.errs=errs
    await pg.goto(URL); await pg.wait_for_function('window.__G&&__G.ready',timeout=60000); await pg.wait_for_timeout(300); await pg.evaluate(HELP); return pg
