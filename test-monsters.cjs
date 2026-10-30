// Deterministic tests of shipped monster attack timings and habitat bounds.
const fs=require('fs'),assert=require('assert'),html=fs.readFileSync('index.html','utf8');
const ai=html.slice(html.indexOf('function specialMonsterAI('),html.indexOf('function assignPursuers('));
const P={hp:100},ZR={puffer:[30,60],shrimp:[62,95]};
const {specialMonsterAI:step,clampNewHabitat:clamp}=new Function('hurtP','ZR',ai+';return {specialMonsterAI,clampNewHabitat};')(n=>P.hp-=n,ZR);
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
for(const n of ['puffer','shrimp'])for(const r of [0,10,50,100,140]){
 const m=monster(n);m.g.position={x:r,z:0};clamp(m);const radius=Math.hypot(m.g.position.x,m.g.position.z);assert(radius>=ZR[n][0]-1e-8&&radius<=ZR[n][1]+1e-8);
}
console.log('PASS: telegraphed puffer attacks, dodging, shrimp windup/dash/single hit/recovery, legacy AI and habitat limits');
