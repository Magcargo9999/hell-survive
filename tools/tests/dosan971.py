"""v9.71 7지옥 도산과 업경의 심판정(지하 31~35층) — 잠금 · 바닥/소품/칼날 지대 · 잡몹 8종 실제 생성 · 까마귀 이속 · 칼날 출혈 · 시작 화면 탭 · 도감 + 스크린샷
사용: GAME_URL=... PYTHONPATH=tools python3 tools/tests/dosan971.py   (스크린샷 build/dosan971_*.png)"""
import asyncio, sys, json
sys.path.insert(0, '/home/claude/hell-survive/tools')
from playwright.async_api import async_playwright
import h301
B = '/home/claude/hell-survive/build/'
async def main():
    async with async_playwright() as pw:
        b = await pw.chromium.launch(); pg = await h301.newpage(b, 1280, 720); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e))); pg.on('console', lambda m: errs.append(m.text) if m.type == 'error' else None)
        await pg.wait_for_function("__G.imgReady(['dmob','dfloor','dprops','ffloor','fprops','fmob'])", timeout=120000, polling=1000)
        R = {}
        R['lock'] = await pg.evaluate("""()=>{const G=__G;G.SAVE.diff.max=99;G.SAVE.diff.sel=32;G.SAVE.shards=1e7;G.startGame('wolf');
          const r={top:G.TOP_TIER,open:G.OPEN_TIER,tier:G.P.tier,fset:G.P.fset,set30:G.floorSet(30),set34:G.floorSet(34),set29:G.floorSet(29)};G.state='menu';return r}""")
        R['start'] = await pg.evaluate("""()=>{const G=__G;G.buildDosanSpecies();G.SAVE.diff.max=0;G.SAVE.diff.sel=0;G.startGame('wolf');const P=G.P;P.tier=30;P.fset='dosan';G.clearGround();
          for(let i=0;i<20;i++){__s();G.tick(1/30)}return {dosan:G.isDosanSet(),sp:G.DSPECIES.map(s=>[s.name,s.idx,Math.round(s.speed),s.unlock,s.frames.length])}}""")
        await pg.screenshot(path=B + 'dosan971_field.png')
        # 잡몹: 필드 300초 — 실제로 생성된 종 집계 (무적·이동)
        R['spawn'] = await pg.evaluate("""()=>{const G=__G,P=G.P;const seen={},sp={};let t=0,ang=0;
          while(t<300){P.inv=9;P.hp=P.max;ang+=0.01;P.x+=Math.cos(ang)*2;P.y+=Math.sin(ang)*2;G.tick(1/30);__s();t+=1/30;
            if(G.state!=='play'){G.closeLevel&&G.closeLevel();G.state='play'}
            for(const e of G.enemies){if(e.spec&&e.kind==='mob'||e.spec&&!e.kind){const n=e.spec.name;seen[n]=(seen[n]||0)+1;sp[n]=Math.round(e.spec.speed)}}}
          const all=G.DSPECIES.map(s=>s.name);return {missing:all.filter(n=>!seen[n]),seen:Object.fromEntries(Object.entries(seen).map(([k,v])=>[k,v>0])),speed:sp,
            other:Object.keys(seen).filter(n=>!all.includes(n))}}""")
        await pg.screenshot(path=B + 'dosan971_mobs.png')
        # 칼날 지대: 칼날 칸 찾아 서 있기 → 출혈 중첩, 벗어나면 3초 뒤 사라짐
        R['blade'] = await pg.evaluate("""()=>{const G=__G,P=G.P;for(const e of G.enemies)e.hp=0;let f=null;
          for(let r=3;r<80&&!f;r++)for(let a=0;a<64&&!f;a++){const tx=Math.round(Math.cos(a/64*6.283)*r),ty=Math.round(Math.sin(a/64*6.283)*r);if(G.isLava(tx,ty)&&G.isLava(tx+1,ty)&&G.isLava(tx,ty+1))f=[tx,ty]}
          if(!f)return 'no blade';P.x=f[0]*64+40;P.y=f[1]*64+40;P.shield=0;P.inv=0;P.hp=P.max*10;const h0=P.hp;let t=0;
          while(t<2.6){P.x=f[0]*64+40;P.y=f[1]*64+40;G.tick(1/30);t+=1/30}
          const on={st:P.bladeSt,bt:+P.bladeT.toFixed(2),lost:Math.round(h0-P.hp)};
          return {tile:f,on}}""")
        await pg.evaluate("()=>{__G.tick(1/30)}"); await pg.screenshot(path=B + 'dosan971_blade.png')
        R['bleedOff'] = await pg.evaluate("""()=>{const G=__G,P=G.P;let q=null;for(let r=2;r<30&&!q;r++)for(let a=0;a<32&&!q;a++){const x=P.x+Math.cos(a/32*6.283)*r*64,y=P.y+Math.sin(a/32*6.283)*r*64;
            let ok=true;for(let i=-2;i<=2;i++)for(let j=-2;j<=2;j++)if(G.isLava(Math.floor(x/64)+i,Math.floor(y/64)+j))ok=false;if(ok)q=[x,y]}
          P.x=q[0];P.y=q[1];P.inv=9;const s1=P.bladeSt;const h0=P.hp;let t=0;while(t<1){P.x=q[0];P.y=q[1];G.tick(1/30);t+=1/30}const mid={st:P.bladeSt,lost:Math.round(h0-P.hp)};
          while(t<3.6){P.x=q[0];P.y=q[1];G.tick(1/30);t+=1/30}return {s1,mid,after:P.bladeSt}}""")
        R['tabs'] = await pg.evaluate("""()=>{const G=__G;G.state='menu';G.SAVE.diff.max=29;G.SAVE.diff.sel=29;G.updateDiff&&G.updateDiff();return [...document.querySelectorAll('#hellTabs button')].map(b=>[b.textContent,b.disabled])}""")
        R['errs'] = errs[:6]
        print(json.dumps(R, ensure_ascii=False, indent=1)); await b.close()
asyncio.run(main())
