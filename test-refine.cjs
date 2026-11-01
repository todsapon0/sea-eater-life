// Deterministic tests of the blacksmith refine rules and the save fields for refine levels.
const fs=require('fs'),assert=require('assert'),html=fs.readFileSync('index.html','utf8');
const logic=html.slice(html.indexOf('// REFINE-LOGIC-START'),html.indexOf('// REFINE-LOGIC-END'));
const {REFINE_RATE,refineChance,refineCost,refineBonus}=new Function(logic+';return {REFINE_RATE,refineChance,refineCost,refineBonus};')();
// rates fall as the target level rises; +1..+3 are guaranteed
for(let n=1;n<=3;n++)assert.equal(refineChance(n,0),1);
for(let n=4;n<=10;n++)assert(refineChance(n,0)<refineChance(n-1,0),'rate must fall at +'+n);
assert.equal(refineChance(10,0),.2);
// failures add a chance bonus (pity), capped at 5 stacks, never above 100%
assert(Math.abs(refineChance(10,3)-.44)<1e-9);assert(Math.abs(refineChance(10,99)-.6)<1e-9);assert.equal(refineChance(5,99),1);
// cost: grows with level, needs a boss fang from +8
assert.equal(refineCost(1).mat,7);assert.equal(refineCost(7).fang,0);assert.equal(refineCost(8).fang,1);assert.equal(refineCost(10).mat,34);
// bonuses per slot (percent)
assert.equal(refineBonus('head',10),25);assert.equal(refineBonus('back',10),30);assert.equal(refineBonus('tail',10),15);
// every refine level is a whole number 0..10 in saves, only on head/back/tail
const tools=require('./save-tools.js');
const rec=(extra)=>JSON.stringify({format:'sea-eater-save',version:1,characters:{sea:Object.assign({lv:5,xp:1,qd:0,q:0,inv:{},seen:{}},extra)}});
tools.parseBackup(rec({}));tools.parseBackup(rec({rf:{head:3,back:0,tail:10},rp:{head:2,back:0,tail:5}}));
for(const bad of [{rf:{head:11}},{rf:{head:-1}},{rf:{head:1.5}},{rf:{legs:1}},{rf:[1]},{rp:{tail:'x'}}])assert.throws(()=>tools.parseBackup(rec(bad)),/ตีบวก/);
console.log('PASS: refine rates, pity cap, costs, bonuses and refine save validation');
