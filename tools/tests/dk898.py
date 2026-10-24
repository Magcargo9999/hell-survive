import asyncio
from playwright.async_api import async_playwright
from h301 import newpage
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(args=['--disable-gpu']); pg=await newpage(b,1000,620)
        await pg.evaluate("()=>{window.__rt=1;__G.SAVE.chars.ghost=true;__G.startGame('ghost')}")
        await pg.wait_for_function("()=>!!__G.IMG.dk",timeout=60000)
        R={}
        R['k1']=await pg.evaluate("""()=>{const G=__G,P=G.P;__lv(12);P.skillTipT=0;G.enemies.length=0;for(let i=0;i<10;i++)G.spawnEnemy(Math.random()*6.28,90);
          const hp0=G.enemies.map(e=>e.hp).reduce((a,b)=>a+b,0);for(let i=0;i<60;i++){P.inv=9;P.hp=P.max;G.tick(1/30)}
          const hp1=G.enemies.filter(e=>e.hp>0).map(e=>e.hp).reduce((a,b)=>a+b,0);
          return {route:P.route,form:P.form,name:G.FD?0:0,skill:P.skill,dodge:P.dodge,spd:Math.round(P.spd),dealt:Math.round(hp0-hp1),src:G.FD?1:0,kn:G.isKnight(),cards:G.cardDefs().map(u=>u.id).filter(x=>/^(gmore|kStep|kHead)$/.test(x))}}""")
        await pg.screenshot(path='build/dk_t1.png')
        R['k2']=await pg.evaluate("""()=>{const G=__G,P=G.P;__lv(22);P.skillTipT=0;G.enemies.length=0;for(let i=0;i<30;i++){P.inv=9;G.tick(1/30)}
          return {form:P.form,skill:P.skill,dodge:P.dodge,cards:G.cardDefs().map(u=>u.id).filter(x=>/^(gmore|kStep|kHead)$/.test(x))}}""")
        # 머리 소환: 적 하나 멀리 + 하나 가까이 → 가까운 적 / 보스 흉내(kind boss) 있으면 보스
        R['head']=await pg.evaluate("""()=>{const G=__G,P=G.P;G.enemies.length=0;G.spawnEnemy(0,200);G.spawnEnemy(3.14,420);G.enemies.forEach(e=>{e.hp=e.max=1e7;e.spd=0;e.sp=0});
          P.skT=0;G.cast();const out={made:!!G.lhead,cast:P.lhCast>0};for(let i=0;i<45;i++){P.inv=9;G.tick(1/30)}
          const h=G.lhead;out.st=h&&h.st;out.tgtNear=h&&h.tgt===G.enemies.reduce((a,e)=>Math.hypot(e.x-h.x,e.y-h.y)<Math.hypot(a.x-h.x,a.y-h.y)?e:a);
          const T=G.enemies[1];const k0=T.kind;T.kind='boss';out.boss=h.pick()===T;T.kind=k0;h.pick=()=>T;
          T.x=P.x+1100;T.y=P.y;h.retarget=0;for(let i=0;i<120;i++){P.inv=9;T.hp=999999;T.x=P.x+1100;T.y=P.y;if(!G.enemies.includes(T))G.enemies.push(T);G.tick(1/30)}
          out.leash=[Math.round(h.x-P.x),Math.round(h.y-P.y)];out.view=[G.W,G.H];out.tdist=Math.round(Math.hypot(T.x-P.x,T.y-P.y));out.tg=h.tgt===T;
          const dm=G.DMETER;out.dm=Object.keys(dm).filter(k=>k.includes('lhead')).map(k=>[k,G.dmName(k),Math.round(dm[k])]);
          h.hurt(h.max*2);out.back=h.st;for(let i=0;i<60;i++){P.inv=9;G.tick(1/30)};out.gone=!G.lhead;
          return out}""")
        await pg.evaluate("()=>{const G=__G,P=G.P;G.enemies.length=0;for(let i=0;i<6;i++)G.spawnEnemy(Math.random()*6.28,250);P.skT=0;G.cast();for(let i=0;i<25;i++){P.inv=9;G.tick(1/30)}}")
        await pg.screenshot(path='build/dk_t2.png')
        print(R, pg.errs[:5]); await b.close()
asyncio.run(main())
