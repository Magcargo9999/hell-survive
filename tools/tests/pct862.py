"""v8.62 체력비례 피해: 대상 캐릭터 판정 · 보스 타격 추가분 · 0.25초 쿨 · 상한 · 달팽이 장판"""
import asyncio,sys,json
sys.path.insert(0,'/home/claude/hell-survive/tools')
from playwright.async_api import async_playwright
import h301
h301.URL='file:///home/claude/hell-survive/build/hell_survive.html'
async def main():
    async with async_playwright() as pw:
        b=await pw.chromium.launch(); pg=await h301.newpage(b,1280,720)
        await pg.wait_for_function('__G.IMG&&__G.IMG.boss',timeout=90000)
        R=await pg.evaluate("""()=>{const G=__G,o={};Object.assign(G.SAVE.chars,{wolf:true,snail:true,archer:true,chimera:true,lizard:true,twins:true,ghost:true,octo:true,gun:true});
          const cases=[['twins',null,null,2],['wolf','twin',null,2],['wolf','abyss',null,2],['wolf','crimson','blood',2],['wolf','crimson','holy',2],['wolf','crimson','fallen',2],['chimera','flame',null,2],['chimera','wind',null,2],['lizard','sword','water',2],['lizard','sword','rage',2],['lizard','guard','guard',2],['wolf','crimson','blood',1],['archer','red',null,2],['snail','venom',null,2]];
          o.who=cases.map(([c,r,f,fm])=>{G.startGame(c);const P=G.P;P.route=r;P.fin=f;P.form=fm;return c+':'+(r||'')+':'+(f||'')+':'+fm+'='+G.pctMelee()});
          // 보스 타격: 지옥 군주 늑대
          G.startGame('wolf');let P=G.P;P.route='abyss';P.form=2;P.crit=0;
          const mk=(k)=>({kind:k,x:P.x+50,y:P.y,hp:134000,max:134000,r:30,kx:0,ky:0,flash:0,t:0});
          const e=mk('boss');G.enemies.push(e);const h0=e.hp;G.hurtEnemy(e,100,0,0,0,false);o.bossHit1=h0-e.hp;   // 100 + min(134, 400)=234
          const h1=e.hp;G.hurtEnemy(e,100,0,0,0,false);o.bossHit2=h1-e.hp;   // 쿨 안: 100
          const e2=mk('boss');e2.max=e2.hp=134000;G.enemies.push(e2);const g0=e2.hp;G.hurtEnemy(e2,10,0,0,0,false);o.cap=g0-e2.hp;   // 10 + min(134,40)=50
          const m=mk('mob');m.hp=m.max=5000;G.enemies.push(m);const m0=m.hp;G.hurtEnemy(m,100,0,0,0,false);o.mob=m0-m.hp;   // 100 (잡몹 제외)
          // 달팽이 장판 (유니크에게 한 틱: 기본 장판 피해 ×0.6 + 체력비례분)
          const zt=(route,type)=>{G.startGame('snail');const P=G.P;P.route=route;P.form=2;G.enemies.length=0;G.spawnUniq(Object.keys(G.UNIQ)[0]);const u=G.enemies.find(q=>q.kind==='uniq');u.x=P.x;u.y=P.y;u.hp=u.max=134000;u.invul=false;
            const z=G.zonesRef;z.length=0;z.push(type==='trail'?{type:'trail',x:P.x,y:P.y,r:200,life:5,max:5,tick:0,dm:1,sp:0}:{type:'lavapool',x:P.x,y:P.y,r:200,life:5,max:5,tick:0,dm:0.35,sp:0});const h=u.hp;G.tick(1/30);return +(h-u.hp).toFixed(2)};
          o.lava_pool=zt('lava','pool');o.lava_trail=zt('lava','trail');o.venom_trail=zt('venom','trail');o.bomb_pool=zt('bomb','pool');o.dmg=G.P.dmg;
          o.pctRate=134;return o}""")
        print(json.dumps(R,ensure_ascii=False,indent=0)); print('errs',pg.errs); await b.close()
asyncio.run(main())
