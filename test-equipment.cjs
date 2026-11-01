// Pure equipment rules extracted from the shipped single-file game, no browser/network.
const fs=require('fs'),assert=require('assert');
const html=fs.readFileSync('index.html','utf8');
const core=html.slice(html.indexOf('const ORG='),html.indexOf('let organGroup='));
function game(cls='sea',lv=1){const P={lv,ev:0,inv:{},mu:{}};return {P,...new Function('P','CLS',core+';return {ORG,RARITY,GEAR_DROPS,gearFrom,canEquip,organFor,rollGear,awardGear,gearRequirement,gearChanges,equipmentBonuses,sortGear};')(P,cls)};}
const sequence=(...v)=>()=>{assert(v.length,'unexpected random draw');return v.shift();};
for(const cls of ['sea','bloop','maja']){
 const g=game(cls),{P}=g;
 assert.deepEqual(P.inv,{});assert.deepEqual(P.mu,{});
 for(const slot of ['head','back','tail'])assert.equal(g.organFor(slot),null);
 assert.equal(g.canEquip('head','fang:1:common'),false);
 P.inv['eq:fang:1:common']=1;P.mu.head='fang:1:common';assert(g.organFor('head')); // ev0
 P.inv['eq:fin:1:common']=1;P.inv['eq:whip:1:common']=1;
 assert(g.canEquip('back','fin:1:common'));assert(g.canEquip('tail','whip:1:common')); // all slots open
 P.inv['eq:fang:8:rare']=1;assert(!g.canEquip('head','fang:8:rare'));
 P.lv=8;assert(g.canEquip('head','fang:8:rare'));assert(!g.canEquip('tail','fang:8:rare'));
 P.inv['eq:jaw:1:common']=1;assert.equal(g.canEquip('head','jaw:1:common'),cls==='sea');
 for(const id of ['fang:0:common','fang:21:rare','fang:1:fake','fang:1.5:rare','unknown:1:common','fang','__proto__:1:common'])assert.equal(g.gearFrom(id),null);
 assert.equal(g.rollGear('ray',()=>.2),null);assert.equal(g.rollGear('unknown',()=>0),null);
 const found=new Set();
 for(const [monster,d]of Object.entries(g.GEAR_DROPS)){
  const ids=d.ids.filter(id=>Object.values(g.ORG).flat().some(o=>o.id===id&&(!o.only||o.only===cls)));
  for(let i=0;i<ids.length;i++){
   const low=g.rollGear(monster,sequence(0,(i+.1)/ids.length,0,0));
   const high=g.rollGear(monster,sequence(0,(i+.1)/ids.length,.999,.999));
   assert.equal(low.org,ids[i]);assert.equal(low.lv,d.lv[0]);assert.equal(high.lv,d.lv[1]);assert.equal(high.rar,'epic');
   assert(!low.only||low.only===cls);found.add(low.org);
  }
 }
 for(const o of Object.values(g.ORG).flat().filter(o=>!o.only||o.only===cls))assert(found.has(o.id));
 const first=g.awardGear('ray',()=>0);assert.equal(first.id,'fang:1:common');assert.equal(P.inv['eq:'+first.id],2);
 const common=g.gearFrom('fang:1:common'),rare=g.gearFrom('fang:1:rare'),epic=g.gearFrom('fang:20:epic');
 assert(common.dm<rare.dm&&rare.dm<epic.dm);
 P.inv['eq:fang:1:common']=99999;g.awardGear('ray',()=>0);assert.equal(P.inv['eq:fang:1:common'],99999);
 delete P.inv['eq:fang:1:common'];assert.equal(g.organFor('head'),null); // forged equipment grants no stats
}
console.log('PASS: empty/open slots, ownership, levels, rarity, all drop tables/species, deterministic loot and inventory cap');

// Comparisons use ratios, include lost bonuses, and treat lower incoming damage as better.
{
 const g=game('sea',8),P=g.P;
 for(const id of ['fang:1:common','fang:8:rare','helm:1:common','fang:20:epic','scale:1:common'])P.inv['eq:'+id]=1;
 P.mu.head='fang:1:common';P.mu.back='scale:1:common';
 const changes=g.gearChanges('head','helm:1:common');
 assert(Math.abs(changes.find(d=>d.key==='dm').delta-(1/1.12-1)*100)<1e-9);
 assert.equal(changes.find(d=>d.key==='dm').better,false);
 assert.equal(changes.find(d=>d.key==='tk').better,true);
 assert.deepEqual(g.gearChanges('head','fang:1:common'),[]);
 const bonus=Object.fromEntries(g.equipmentBonuses().map(d=>[d.key,d.delta]));
 assert(Math.abs(bonus.dm-12)<1e-8);assert(Math.abs(bonus.hp-15)<1e-8);
 assert(g.gearRequirement('head','fang:20:epic').includes('12'));
 const items=['fang:1:common','fang:20:epic','fang:8:rare'].map(g.gearFrom),before=items.map(o=>o.id);
 assert.deepEqual(g.sortGear(items,'head','ready').map(o=>o.id),['fang:8:rare','fang:1:common','fang:20:epic']);
 assert.equal(g.sortGear(items,'head','rarity')[0].id,'fang:20:epic');
 assert.equal(g.sortGear(items,'head','level')[0].lv,20);
 assert.deepEqual(items.map(o=>o.id),before);
}
console.log('PASS: gear tradeoffs, incoming damage comparison, combined bonuses, level reasons and nonmutating sorting');
