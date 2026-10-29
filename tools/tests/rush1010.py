"""v10.10 보스 러시 개편: 30층 해금 · 처치한 마왕 풀 · 4라운드 · 시작 증강 직접 선택 · 2/5 선택 · 전용 증강 · 심장 드랍/옵션 미적용 · 이속 하한/상한 · 산소/십자가/바람 · 보상 정산 · 마석 · 주사기 · 뽑기권"""
import asyncio, sys, json, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from playwright.async_api import async_playwright
import h301
B = os.path.join(h301.ROOT, 'build') + '/'
PICK = """(want)=>{const G=__G;let g=0;while(g++<900){const t=document.getElementById('levelTitle').textContent;
  if(G.state==='levelup'&&t.indexOf('몇 개')>=0){G.pick(want===5?1:0);continue}
  if(__s())continue; if(G.state==='play'&&G.rush&&G.rush.init){G.tick(1/30);continue} break}
  return [G.state,G.P.lvl,G.rush.totalCardsPicked]}"""
async def main():
    async with async_playwright() as pw:
        b = await pw.chromium.launch(); pg = await h301.newpage(b, 1280, 720); R = {}
        await pg.wait_for_timeout(1500)
        R['lock'] = await pg.evaluate("""()=>{const G=__G;G.SAVE.diff.clr=19;G.SAVE.dex.kills={};const a=G.rushReady();G.SAVE.diff.clr=29;const b2=G.rushReady();
          Object.assign(G.SAVE.dex.kills,{boss:3,boss2:1,boss14:2,boss19:1,boss21:1,boss20:1});return [a,b2,G.brPool().join(',')]}""")
        # 심장 옵션 미적용: 공격력 +50% 심장을 장착한 채 시작
        R['heartOff'] = await pg.evaluate("""()=>{const G=__G,S=G.SAVE.heart;S.inv=[{id:7001,g:'legend',b:'monkey',st:'atk',v:50}];S.eq=[7001];G.SAVE.stone={inv:[],eq:null,n:0};
          G.SAVE.diff.max=5;G.SAVE.diff.sel=0;G.SAVE.shards=1e6;G.startGame('wolf');const d1=G.P.dmg;G.startRush('wolf');const d2=G.P.dmg;S.inv=[];S.eq=[];return [+(d1/d2).toFixed(3), G.rush.applyHeartOptions]}""")
        R['prep'] = await pg.evaluate(PICK, 2)
        R['prep'].append(await pg.evaluate("()=>[Object.keys(__G.P.up).length, __G.rush.ord.join(','), __G.P.skill]"))
        rounds = []
        for k in range(4):
            ent = await pg.evaluate("""async()=>{const G=__G;for(let i=0;i<1500;i++){G.P.inv=99;G.P.hp=G.P.max;G.tick(1/30);if(G.boss&&G.boss.st!=='intro'&&G.rush.ph==='fight')break;if(i%20===0)await new Promise(r=>setTimeout(r,30))}
              const P=G.P,r=G.rush;return {bk:G.boss&&(G.boss.bk||'monkey'),round:r.round,tier:P.tier,mods:r.modifiers.join('+'),txt:r.modTxt()}}""")
            # 기믹 확인: 4초 서 있기
            mod = await pg.evaluate("""()=>{const G=__G,P=G.P,r=G.rush,e=G.boss;e.invul=true;const o2a=P.o2,x0=P.x,y0=P.y;let paused=0;
              for(let i=0;i<120;i++){P.inv=99;P.hp=P.max;G.tick(1/30);if(r.paused())paused++}
              return {o2:[Math.round(o2a),Math.round(P.o2)],gey:r.gey.length,cross:!!r.cr,arms:r.crossArms().length,wind:!!r.wind,moved:Math.round(Math.hypot(P.x-x0,P.y-y0)),paused}}""")
            if k == 3: await pg.screenshot(path=B + 'rush1010_r4.png')
            if k == 2: await pg.screenshot(path=B + 'rush1010_r3.png')
            # 처치 (첫 라운드는 심장 드랍 강제)
            kill = await pg.evaluate("""(k)=>{const G=__G,P=G.P,e=G.boss;e.invul=false;e.shield=0;if(e.st==='guard'||e.st==='intro')e.st='chase';const mr=Math.random;if(k===0){G.SAVE.heart.inv=[];Math.random=()=>0.001}
              G.hurtEnemy(e,1e13,0,0,0);Math.random=mr;for(let i=0;i<3;i++)G.tick(1/30);return {state:G.state,kills:G.rush.kills,hearts:G.rush.hearts.length,title:document.getElementById('levelTitle').textContent}}""", k)
            want = [2, 5, 2][k] if k < 3 else 2
            pk = await pg.evaluate(PICK, want) if k < 3 else None
            rounds.append({'ent': ent, 'mod': mod, 'kill': kill, 'pick': pk}); print(k, json.dumps(rounds[-1], ensure_ascii=False))
        R['final'] = await pg.evaluate("""()=>{const G=__G;for(let i=0;i<60;i++)G.tick(1/30);const r=G.rush;return {state:G.state,reward:r.reward,tix:G.SAVE.rush.tix,syr:G.SAVE.rush.syr,stone:G.SAVE.stone,picks:r.picks,total:r.totalCardsPicked}}""")
        await pg.evaluate("()=>{try{__G.showOver&&0}catch(_){}}")
        # 이속 하한/상한
        await pg.evaluate("()=>__G.startRush('wolf')"); await pg.evaluate(PICK, 2)
        R['spd'] = await pg.evaluate("""()=>{const G=__G;const P=G.P,o=[];P.spd=1000;G.tick(1/30);o.push(Math.round(P.espd));P.spd=100;G.tick(1/30);o.push(Math.round(P.espd));G.startGame('wolf');G.P.spd=1000;G.tick(1/30);o.push(Math.round(G.P.espd));return o}""")
        # 전용 증강: 보스 러시 + 스킬이 있을 때만
        R['card'] = await pg.evaluate("""()=>{const G=__G;G.startGame('wolf');G.P.skill='cerb';const a=G.cardDefs().some(u=>u.id==='brCool');G.startRush('wolf');G.P.skill='cerb';const b2=G.cardDefs().some(u=>u.id==='brCool');const c0=G.skillCd();G.P.up.brCool=2;const c1=G.skillCd();return [a,b2,+(c1/c0).toFixed(2)]}""")
        # 마석 (일반 판 적용 · 보스 러시 미적용)
        R['stone'] = await pg.evaluate("""()=>{const G=__G;G.SAVE.heart.inv=[];G.SAVE.heart.eq=[];G.SAVE.stone={inv:[],eq:null,n:0};G.startGame('wolf');const d0=G.P.dmg,a0=G.P.aspd,h0=G.P.max;
          G.stoneGain('rare');G.stoneGain('legend');G.stoneGain('epic');const eq=G.SAVE.stone.inv.find(q=>q.id===G.SAVE.stone.eq).g;G.startGame('wolf');const o=[eq,+(G.P.dmg/d0).toFixed(3),+(G.P.aspd-a0).toFixed(2),G.P.max/h0,G.runBonus().shard];G.startRush('wolf');o.push(G.runBonus().atk);return o}""")
        # 주사기
        R['syr'] = await pg.evaluate("""()=>{const G=__G,S=G.SAVE.heart;S.inv=[{id:801,g:'rare',b:'fuse3',st:'atk',v:2,st2:'hp',v2:2,st3:'aspd',v3:2},{id:802,g:'rare',b:'monkey',st:'atk',v:2}];G.SAVE.rush.syr=40;
          const e1=G.useSyringe(802).err;const adds=[];let n=0,r;do{r=G.useSyringe(801);if(r.add)adds.push(r.add);n++}while(!r.open&&!r.err&&n<60);const h=S.inv[0];
          return {e1:!!e1,uses:n,min:Math.min(...adds),max:Math.max(...adds),lines:G.hOpt(h),st4:!!h.st4,after:G.useSyringe(801).err||'',left:G.SAVE.rush.syr}}""")
        # 뽑기권
        R['tix'] = await pg.evaluate("""()=>{const G=__G;G.SAVE.rush.tix=1;G.SAVE.shards=0;G.openGacha&&G.openGacha();G.renderGacha();const dis=document.getElementById('gOne').disabled;G.gachaPull(1);return [dis,G.SAVE.rush.tix,G.SAVE.shards]}""")
        await pg.evaluate("()=>{__G.openHeart();}")
        await pg.evaluate("()=>{const S=__G.SAVE.heart;__G.renderHeart&&0}")
        await pg.screenshot(path=B + 'rush1010_heart.png')
        print(json.dumps(R, ensure_ascii=False))
        ok = (R['lock'][:2] == [False, True] and R['heartOff'][0] > 1.4 and R['heartOff'][1] is False and R['final']['state'] in ('win', 'over')
              and R['final']['total'] == 9 and R['final']['reward']['name'] == '하드' and R['final']['tix'] >= 3 and R['spd'][0] <= 290 and R['spd'][1] >= 250 and R['spd'][2] > 500
              and R['card'] == [False, True, 0.8] and R['stone'][0] == 'legend' and R['stone'][1] == 1.06 and R['stone'][-1] == 0 and R['syr']['e1'] and R['syr']['st4'] and 3 <= R['syr']['min'] and R['syr']['max'] <= 10
              and R['tix'][1] == 0 and R['tix'][2] == 0 and rounds[0]['kill']['hearts'] == 1 and all(r['mod']['o2'][0] - r['mod']['o2'][1] >= 20 for r in rounds[1:] if r['ent']['bk'] != 'kng') and rounds[2]['mod']['cross'] and rounds[3]['mod']['wind'])
        print('OK' if ok else 'FAIL'); print('errs', pg.errs[:6]); await b.close()
asyncio.run(main())
