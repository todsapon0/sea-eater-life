// Deterministic tests of shipped monster attack timings and habitat bounds.
const fs=require('fs'),assert=require('assert'),html=fs.readFileSync('index.html','utf8');
const ai=html.slice(html.indexOf('function specialMonsterAI('),html.indexOf('function assignPursuers('));
const P={hp:100};
const {MAPS,SPAWN}=new Function(html.slice(html.indexOf('let curMap=0;'),html.indexOf('const monsterRoster='))+';return {MAPS,SPAWN};')();
const {specialMonsterAI:step,clampNewHabitat:clamp}=new Function('hurtP','MAPS',ai+';return {specialMonsterAI,clampNewHabitat};')(n=>P.hp-=n,MAPS);
const monster=n=>({ty:{n,s:1,d:9,sp:2},g:{position:{x:40,z:0}},a:0,cd:0,windup:0,dash:0,dashWait:0});
let m=monster('puffer');
assert(step(m,.1,0,2.7,2.7,1));assert.equal(m.windup,1.2);assert.equal(P.hp,100);
step(m,.6,0,2.7,2.7,1);assert.equal(P.hp,100);assert(m.windup>0);
step(m,.7,0,5,5,1);assert.equal(P.hp,100);assert.equal(m.cd,2.4); // move away to dodge
m.cd=0;step(m,.1,0,2.7,2.7,1);step(m,1.2,0,2.7,2.7,1);assert.equal(P.hp,91);
step(m,.1,0,2.7,2.7,1);assert.equal(P.hp,91); // one hit, then recovery
m=monster('shrimp');P.hp=100;step(m,.1,0,6,6,1);assert.equal(m.windup,.9);assert.equal(P.hp,100);
step(m,.8,0,6,6,1);assert.equal(m.dash,0);assert.equal(P.hp,100);
step(m,.2,0,6,6,1);assert.equal(m.dash,.45);assert.equal(m.dashWait,6);
const z=m.g.position.z;step(m,.1,0,6,6,1);assert(m.g.position.z>z);assert.equal(P.hp,100);
step(m,.1,0,2.7,2.7,1);assert.equal(P.hp,91);assert.equal(m.dash,0);
step(m,.1,0,2.7,2.7,1);assert.equal(P.hp,91);
assert.equal(step(monster('shark'),.1,0,2,2,1),false); // legacy AI still owns legacy species
for(const {t:n,map} of SPAWN.filter(sp=>['puffer','shrimp'].includes(sp.t)))for(const [x,z] of [[0,0],[10,5],[60,0],[-200,40],[30,-90],[140,140]]){
 const m=monster(n);m.map=map;m.g.position={x,z};clamp(m);const d=MAPS[m.map],bx=d.w/2-1.5,bz=d.d/2-1.5;assert(Math.abs(m.g.position.x)<=bx+1e-8&&Math.abs(m.g.position.z)<=bz+1e-8,'habitat rectangle');
}
console.log('PASS: telegraphed puffer attacks, dodging, shrimp windup/dash/single hit/recovery, legacy AI and rectangular map limits');
// Parked/dead monsters never influence the live separation pass.
const separateSrc=html.slice(html.indexOf('function separateMonsters()'),html.indexOf('// ===== ถิ่น:'));
const liveA=monster('ray'),liveB=monster('ray'),parked=monster('ray');
for(const m of [liveA,liveB,parked]){m.g.position={x:0,z:0};m.dead=0;}
parked.dead=1e9;const pool=[liveA,parked,liveB];
new Function('mons',separateSrc+';separateMonsters();')(pool);
assert(Math.hypot(liveA.g.position.x-liveB.g.position.x,liveA.g.position.z-liveB.g.position.z)>1.99);
assert.deepEqual(parked.g.position,{x:0,z:0});
console.log('PASS: live monsters separate while parked monsters remain untouched');
