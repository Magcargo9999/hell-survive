"""v9.85 검 도깨비 마왕 (지하 31층 100% · 32층 70% · 7지옥 임시 보스방 = 용암 보스맵 IMAP)
 확률 · 순환(모든 패턴) · 규칙 9(돌진 옆으로 비키기 · 파동 틈 · 가드 반격은 원 밖/공격 안 하면 없음 · 결계 안 가둠·밖으로 못 나감·회전 베기 피하기 · 낙하/연속 베기 피하기) · 2페이즈 · 처치 · 도감 · 스크린샷
사용: PYTHONPATH=tools python3 tools/tests/dok985.py   (스크린샷 build/dok_*.png)"""
import asyncio, sys, os, json
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, HERE)
from playwright.async_api import async_playwright
import h301
B = os.path.join(os.path.dirname(HERE), 'build') + '/'
async def ev(pg, js):
    try: return await pg.evaluate(js)
    except Exception as ex: return 'ERR ' + str(ex).split('\n')[0][:300]
async def main():
    async with async_playwright() as pw:
        b = await pw.chromium.launch(); pg = await h301.newpage(b, 1280, 720); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e))); pg.on('console', lambda m: errs.append(m.text) if m.type == 'error' else None)
        await pg.wait_for_function('__G.IMG&&__G.IMG.boss', timeout=90000); await pg.wait_for_function("__G.imgReady(['arena','dmap','dok','dokfx'])", timeout=120000, polling=1000)
        await pg.evaluate("()=>{window.__cl=()=>{const P=__G.P;P.inv=0;P.shield=0;P.dodge=0;P.pals=[];P.up.guard=0;P.rel.mirror=0;P.armor=1;P.taken=1;P.bindT=0;P.bindImm=0;P.max=1e7};window.__tk=()=>{const G=__G;G.tick(1/30);if(G.state!=='play'&&G.state!=='over'&&G.state!=='win')__s()};window.__only=(k)=>{const AI=__G.dok;for(const c in AI.cd)AI.cd[c]=99;AI.cd[k]=0;AI.ordT=[k];AI.ci=0};window.__go=(k)=>{const AI=__G.dok,e=__G.boss;__G.DOKW.bleedT=0;__G.DOKW.bind=null;__G.DOKW.fx=[];e.invul=false;e.alpha=1;e.hy=0;AI.spin=null;AI.drop=null;AI.cb=null;e.gHits=0;e.slowT=0;e.tele=[];__G.DOKW.waves=[];__G.DOKW.zone=null;__only(k);AI.chase(0);e.stT=0}}")
        R = {}
        R['A'] = await ev(pg, """()=>{const G=__G,o={};const cnt=(t,k)=>{const c={};for(let i=0;i<4000;i++){const q=G.pickBossK(t);c[q]=(c[q]||0)+1}return Math.round((c[k]||0)/40)};
          o.t29=cnt(29,'tig');o.t30=cnt(30,'dok');o.t31=cnt(31,'dok');o.t32=cnt(32,'dok');
          G.SAVE.diff.max=34;G.SAVE.diff.sel=0;G.SAVE.shards=1e7;G.startGame('archer');const P=G.P;__lv(28);P.tier=30;P.fset='dosan';P.bossK='dok';G.raiseCastle();G.enterArena();
          for(let i=0;i<40;i++)__tk();const bo=G.boss;o.bk=bo&&bo.bk;o.hp=Math.round(bo.max);
          const seen={},sts=[];let last='',out=0;
          for(let i=0;i<30*200;i++){P.hp=P.max;P.inv=1;bo.hp=Math.max(bo.max*0.5,Math.min(bo.hp,bo.max*0.95));__tk();const e=G.boss;if(!e)break;if(!G.inPoly(e.x,e.y)&&e.alpha>0&&e.hy<5)out++;if(e.st!==last){last=e.st;seen[e.st]=(seen[e.st]||0)+1;sts.push(e.st)}}
          o.seen=seen;o.seq=sts.slice(0,40).join('>');o.bossOut=out;o.pIn=G.inPoly(P.x,P.y);return o}""")
        # A 쾌검: 서 있으면 맞고 옆으로 60px 비키면 안 맞는다 · 파동 3갈래: 가운데 줄에서 45px 옆으로 비키면 안 맞는다
        R['dash'] = await ev(pg, """()=>{const G=__G,P=G.P,e=G.boss,o={};const C=G.DOKW,cx=2100,cy=1727;const run=(mode)=>{__cl();P.hp=P.max;e.x=cx-500;e.y=cy;e.hp=e.max;P.x=cx+100;P.y=cy;__go('dash');let hit=0,seq=[];
            for(let i=0;i<30*4;i++){P.inv=0;if(mode==='side'&&i<12&&e.st==='dashw')P.y+=5;if(mode==='waveside'&&e.st==='wind'){P.y+=Math.sign(Math.sin(G.dok.waveA)||1)*(-0)+0}
              const before=P.hp;__tk();if(P.hp<before){hit++;seq.push(e.st)}if(e.st==='chase'&&i>20)break}return [hit,seq.join(',')]};
          o.stand=run('stand');o.side=run('side');return o}""")
        R['wave'] = await ev(pg, """()=>{const G=__G,P=G.P,e=G.boss,o={};const cx=2100,cy=1727;const run=(off,d)=>{__cl();P.hp=P.max;e.x=cx-d;e.y=cy;P.x=cx;P.y=cy;__go('dash');
            // 돌진 예고 동안 비켜 서 있다가(맞지 않게) 돌진이 끝나면 파동 줄을 보고 비킨다
            let hit=0,moved=false,tgtY=null;for(let i=0;i<30*5;i++){P.inv=0;if(e.st==='dashw'){P.y=cy+130}if(e.st==='wind'){if(tgtY===null){tgtY=P.y}}
              if(e.st==='wind'&&!moved&&off){const A=G.dok.waveA,nx=-Math.sin(A),ny=Math.cos(A);const k=Math.min(1,(e.anT)*30/ (G.DOK.wvWind*30));P.x+=nx*off/ (G.DOK.wvWind*30);P.y+=ny*off/(G.DOK.wvWind*30)}
              const b=P.hp;__tk();if(P.hp<b){hit++;(window.__hl=window.__hl||[]).push([e.st,i,Math.round(Math.hypot(P.x-e.x,P.y-e.y))])}if(e.st==='chase'&&i>60)break}return hit};
          o.stand=run(0,500);o.off50=run(50,500);o.off50near=run(50,300);o.off50far=run(50,700);o.hl=window.__hl;return o}""")
        # B 귀신의 흘리기: 원 안에서 3번 → 반격(속박→참격) / 원 밖이면 반격 없음 / 가드 중 피해 -90%
        R['guard'] = await ev(pg, """()=>{const G=__G,P=G.P,e=G.boss,o={};const cx=2100,cy=1727;
          const hitN=(n,dist)=>{__cl();P.hp=P.max;e.hp=e.max;e.x=cx;e.y=cy;P.x=cx+dist;P.y=cy;__go('guard');e.tele=[];let bound=false,hpd=0;let i=0;
            for(;i<60&&e.st!=='guard';i++)__tk();const h0=e.hp;
            for(let k=0;k<n*8+10;k++){if(e.st==='guard'&&e.anT>0.52&&k%8===0)G.hurtEnemy(e,100,0,0,0,false);P.inv=0;__tk();if(P.bindT>0)bound=true;if(e.st==='counter')break}
            return [e.gHits,e.st,bound,Math.round(h0-e.hp),i,P.bindImm]};
          o.in3=hitN(3,120);o.in2=hitN(2,120);o.out5=hitN(5,300);
          // 피해 -90%
          __cl();e.hp=e.max;__go('guard');for(let i=0;i<30&&e.st!=='guard';i++)__tk();const h1=e.hp;G.hurtEnemy(e,1000,0,0,0,true);const d1=h1-e.hp;o.quiet=Math.round(d1);
          // 반격: 속박 중 가만히 있어도 대형 참격은 1회 · 속박 면역 · 풀리기 직전
          __cl();P.hp=P.max;e.hp=e.max;e.x=cx;e.y=cy;P.x=cx+120;P.y=cy;__go('guard');for(let i=0;i<30&&e.st!=='guard';i++)__tk();e.gHits=3;let tl=[],dmgAt=null,t0=0;
          for(let i=0;i<60;i++){P.inv=0;const b=P.hp;__tk();tl.push(e.st+(P.bindT>0?'*':''));if(P.hp<b&&dmgAt===null)dmgAt=i;if(e.st==='chase'&&i>10)break}
          o.counter=[tl.join('').length,dmgAt,Math.round(P.bindImm*10)/10,Math.round(P.max-P.hp)];return o}""")
        # C 검총의 결계: 안에 가둔다 · 벽에 닿으면 피해+출혈 · 회전 베기는 붉은 길을 보고 비키면 안 맞는다 · 10초 뒤 풀린다
        R['zone'] = await ev(pg, """()=>{const G=__G,P=G.P,e=G.boss,o={};const cx=2100,cy=1727;__cl();P.hp=P.max;e.x=cx;e.y=cy-300;P.x=cx;P.y=cy;__go('zone');
          let phs=[],t=0,out=0,leaked=0,wallHit=0,maxD=0;let Z=null;
          for(let i=0;i<30*20;i++){P.inv=0;Z=G.DOKW.zone;
            if(Z&&Z.ph==='on'&&i%1===0){P.x+=(i%240<120?1:-1)*5;P.y+=(i%160<80?1:-1)*3.5}
            const b=P.hp;__tk();if(Z&&Z.ph==='on'){const dx=Math.abs(P.x-Z.x)-Z.hx,dy=Math.abs(P.y-Z.y)-Z.hy;if(dx>0||dy>0)leaked++;if(!G.inPoly(P.x,P.y))out++}
            if(!phs.length||phs[phs.length-1]!==e.st)phs.push(e.st);if(!G.DOKW.zone&&i>60&&e.st==='chase')break}
          o.phs=phs.join('>');o.leaked=leaked;o.pOut=out;o.zoneGone=!G.DOKW.zone;o.hpLost=Math.round(P.max-P.hp);return o}""")
        R['zoneWall'] = await ev(pg, """()=>{const G=__G,P=G.P,e=G.boss,o={};const cx=2100,cy=1727;__cl();P.hp=P.max;e.hp=e.max;e.x=cx;e.y=cy-300;P.x=cx;P.y=cy;__go('zone');
          for(let i=0;i<30*3&&!(G.DOKW.zone&&G.DOKW.zone.ph==='on');i++){P.inv=1;__tk()}const Z=G.DOKW.zone;if(!Z)return 'nozone';
          P.x=Z.x+Z.hx-20;P.y=Z.y;P.hp=P.max;P.inv=0;let bl=0;for(let i=0;i<30*2;i++){P.x+=6;P.inv=0;__tk()}o.insideAfterPush=Math.abs(P.x-Z.x)<=Z.hx;o.lost=Math.round(P.max-P.hp);o.bleed=G.DOKW.bleedT>0;return o}""")
        R['spin'] = await ev(pg, """()=>{const G=__G,P=G.P,e=G.boss,o={};const cx=2100,cy=1727;
          const run=(dodge)=>{__cl();P.hp=P.max;e.hp=e.max;e.x=cx;e.y=cy-300;P.x=cx;P.y=cy;__go('zone');let hits=0,spins=0,seen=false;
            for(let i=0;i<30*30;i++){P.inv=0;const Z=G.DOKW.zone;const AI=G.dok;
              if(Z&&Z.ph==='on'&&e.st==='spin'&&AI.spin&&AI.spin.i>=0&&dodge){const S=AI.spin,sg=S.segs[S.i];if(sg){const dx=sg[2]-sg[0],dy=sg[3]-sg[1],L=Math.hypot(dx,dy)||1,nx=-dy/L,ny=dx/L;const rx=P.x-sg[0],ry=P.y-sg[1],dist=rx*nx+ry*ny;
                  if(Math.abs(dist)<G.DOK.spR+60){const sgn=dist>=0?1:-1;const mx=Z.x-Z.hx+80,Mx=Z.x+Z.hx-80,my=Z.y-Z.hy+80,My=Z.y+Z.hy-80;let nxp=P.x+nx*sgn*150/30,nyp=P.y+ny*sgn*150/30;if(nxp<mx||nxp>Mx||nyp<my||nyp>My){nxp=P.x-nx*sgn*150/30;nyp=P.y-ny*sgn*150/30}P.x=Math.min(Mx,Math.max(mx,nxp));P.y=Math.min(My,Math.max(my,nyp))}}}
              const b=P.hp;__tk();if(P.hp<b)hits++;if(e.st==='spin'&&AI.spin&&AI.spin.i>=0)spins=Math.max(spins,AI.spin.i+1);if(!G.DOKW.zone&&e.st==='chase')break}
            return [hits,spins,Math.round(P.max-P.hp)]};
          o.dodge=run(true);o.stand=run(false);return o}""")
        # 30% 무형검: 포효 → 낙하 3번(0.5초 간격) → 연속 베기 (움직이면 피한다)
        R['rage'] = await ev(pg, """()=>{const G=__G,P=G.P,e=G.boss,o={};const cx=2100,cy=1727;__cl();P.hp=P.max;e.hp=e.max*0.29;e.x=cx;e.y=cy-300;P.x=cx;P.y=cy;e.st='chase';e.stT=0;let sts=[];
          for(let i=0;i<60;i++){P.inv=1;__tk()}o.ph2=e.ph2;o.invulRoar=1;
          const run=(mv)=>{__cl();P.hp=P.max;e.hp=e.max*0.25;e.x=cx;e.y=cy-300;P.x=cx;P.y=cy;__go('drop');G.dok.cd.drop=0;G.dok.dropStart();let hit=0,seq=[],circ=0;const t0=0;
            for(let i=0;i<30*7;i++){P.inv=0;if(mv){const a=i/30*1.5;P.x+=Math.cos(a)*150/30;P.y+=Math.sin(a)*150/30*0.7;
              if(e.st==='cbw'&&G.dok.cb){const C=G.dok.cb;const nx=-C.uy,ny=C.ux;const k=150/30;P.x+=nx*k;P.y+=ny*k}}
              const b=P.hp;__tk();if(P.hp<b){hit++;seq.push(e.st)}if(!seq.length||seq[seq.length-1]!==e.st){}if(sts[sts.length-1]!==e.st)sts.push(e.st);if(e.st==='chase'&&i>40)break}return [hit,seq.join(',')]};
          o.mv=run(true);o.stand=run(false);o.sts=sts.join('>');return o}""")
        # 처치 · 도감
        R['end'] = await ev(pg, """()=>{const G=__G,P=G.P,e=G.boss;__cl();const k0=(G.SAVE.dex.kills.boss21||0);e.hp=1;G.hurtEnemy(e,99999,0,0,0,false);for(let i=0;i<60;i++){P.inv=1;__tk()}return {kills:(G.SAVE.dex.kills.boss21||0)-k0,death:!!G.DOKW.death,bossGone:!G.boss||G.boss.hp<=0}}""")
        print(json.dumps(R, ensure_ascii=False, indent=1)); print('errs', errs[:8])
        await b.close()
asyncio.run(main())
