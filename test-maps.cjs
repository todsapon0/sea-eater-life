// Directional topology, population and spawn safety from the shipped map tables.
const fs=require('fs'),assert=require('assert'),html=fs.readFileSync('index.html','utf8');
const source=html.slice(html.indexOf('let curMap=0;'),html.indexOf('const sandTex='));
const {MAPS,MAP_ROUTES,PORTALS,SPAWN,monsterMeta,monsterRoster,portalDeeper,mapExit,mapEdge}=new Function(source+';return {MAPS,MAP_ROUTES,PORTALS,SPAWN,monsterMeta,monsterRoster,portalDeeper,mapExit,mapEdge};')();
assert.equal(MAPS.length,14);assert.equal(PORTALS.length,26);assert.equal(MAPS.filter(d=>d.safe).length,1);
const inside=(d,p)=>Math.abs(p.x)<d.w/2&&Math.abs(p.z)<d.d/2;
for(const [i,d] of MAPS.entries()){assert.equal(d.id,i);assert(['town','shallows','kelp','cave','lair'].includes(d.music));assert(d.hpScale>0&&d.xpScale>0);}
const axes={poison:[0,-1],spike:[-1,0],normal:[0,1],weird:[1,0]};
for(const [theme,[dx,dz]] of Object.entries(axes)){
 const branch=MAPS.filter(d=>d.theme===theme).sort((a,b)=>a.tier-b.tier);
 assert.equal(branch.length,3);let from=MAPS[0];
 for(const [i,d] of branch.entries()){
  assert.equal(d.tier,i+1);assert.equal(d.gx,dx*(i+1));assert.equal(d.gy,dz*(i+1));
  assert(d.rec>from.rec&&d.hpScale>=from.hpScale&&d.xpScale>=from.xpScale);
  assert(MAP_ROUTES.some(([a,b])=>a===from.id&&b===d.id));from=d;
 }
}
const reached=new Set([0]);for(let i=0;i<MAPS.length;i++)for(const p of PORTALS)if(reached.has(p.map))reached.add(p.to.map);assert.equal(reached.size,14,'all maps reachable');
for(const p of PORTALS){
 const A=MAPS[p.map],B=MAPS[p.to.map],dx=Math.sign(B.gx-A.gx),dz=Math.sign(B.gy-A.gy);
 assert(inside(A,p));assert.equal(Math.sign(p.x),dx);assert.equal(Math.sign(p.z),dz);
 const back=PORTALS.find(q=>q.map===p.to.map&&q.to.map===p.map);assert(back,'return portal');
 assert.equal(p.dx,dx);assert.equal(p.dz,dz);
 const e=mapEdge(p);assert(inside(A,{x:e.x1,z:e.z1})&&inside(A,{x:e.x2,z:e.z2}));
 for(const f of [-1,-.8,-.3,0,.3,.8,1]){
  const x=dx?dx*(A.w/2-1):f*(A.w/2-2),z=dz?dz*(A.d/2-1):f*(A.d/2-2);
  const arrival=mapExit(A.id,x,z);assert.equal(arrival.map,B.id);assert(inside(B,arrival));
  assert.equal(mapExit(B.id,arrival.x,arrival.z),null,'no automatic bounce');
  const returnPoint={x:dx?-dx*(B.w/2-1):arrival.x,z:dz?-dz*(B.d/2-1):arrival.z};
  const returned=mapExit(B.id,returnPoint.x,returnPoint.z);assert.equal(returned.map,A.id);
  assert(Math.abs((dx?returned.z:returned.x)-(dx?z:x))<1e-9,'lateral position survives round trip');
 }
 assert.equal(mapExit(A.id,p.x,p.z),null,'old center portal never teleports');
 assert.equal(portalDeeper(p),B.tier>A.tier);
}
for(const d of MAPS){
 assert.equal(mapExit(d.id,0,0),null);
 for(const [dx,dz] of [[-1,0],[1,0],[0,-1],[0,1]]){
  const p=PORTALS.find(p=>p.map===d.id&&p.dx===dx&&p.dz===dz);
  const result=mapExit(d.id,dx*(d.w/2+10),dz*(d.d/2+10));
  assert.equal(result?.map,p?.to.map,'only connected sides open');
 }
 for(const [x,z] of [[999,999],[-999,999],[999,-999],[-999,-999]]){
  const result=mapExit(d.id,x,z);if(result){assert(inside(MAPS[result.map],result));assert.equal(mapExit(result.map,result.x,result.z),null,'corner does not chain exits');}
 }
}
const allowed={normal:['ray','shark','whale'],poison:['eel','crb2'],spike:['puffer','chp2','chp3','shrimp'],weird:['chp1','crb1','hnd1','srp1','hnd2','swm1','tub1','crb3','hnd3','srp2','srp3','swm2','tub2'],boss:['boss']};
for(const sp of SPAWN){assert(allowed[MAPS[sp.map].theme].includes(sp.t),'theme: '+sp.t);assert(sp.n>=sp.c&&sp.c>0);}
for(const d of MAPS)assert.equal(SPAWN.some(sp=>sp.map===d.id),!d.safe,'every field populated, town safe');
assert.equal(monsterRoster.length,90);assert.equal(new Set(monsterRoster).size,23);assert.equal(monsterRoster.filter(n=>n==='boss').length,1);
for(const m of monsterMeta){const d=MAPS[m.map];assert(inside(d,m.home));for(const p of PORTALS.filter(p=>p.map===m.map))assert(Math.hypot(m.home.x-p.x,m.home.z-p.z)>7,'home clear of portal');}
// New topology has no persisted map field: legacy saves always return to town.
const save=html.slice(html.indexOf('const save=()=>'),html.indexOf('const say='));assert(!/curMap|map:/.test(save));assert(html.includes('setMap(0);'));
console.log('PASS: 14 maps, four levelled branches, 26 full-edge links, lateral round trips and closed world boundaries, 90 themed monsters, spawn safety and unchanged save schema');
