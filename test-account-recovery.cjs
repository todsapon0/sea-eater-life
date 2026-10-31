const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const code = fs.readFileSync(__dirname + '/account.js', 'utf8');
const tick = () => new Promise(resolve => setImmediate(resolve));
const data = lv => ({lv,xp:0,qd:0,q:0,inv:{},seen:{}});
const rows = {A:{sea:{character_class:'sea',save_data:data(1),revision:0},bloop:{character_class:'bloop',save_data:data(5),revision:0}},B:{bloop:{character_class:'bloop',save_data:data(1),revision:0}}};
let saved=null;
const map = new Map(); let online=true, user='A', page;
class Element {
  constructor(tag='div'){this.tag=tag;this.children=[];this.textContent='';this.hidden=false;this.disabled=false;this.classList={add(){}};}
  append(...items){this.children.push(...items);} prepend(item){this.children.unshift(item);}
  remove(){} querySelector(q){return this.elements?.[q] || (q==='button' ? this.button : null);}
  querySelectorAll(){return [];} click(){if(this.onclick)this.onclick();}
  set innerHTML(v){this.button=new Element('button');this.elements={'#accountError':new Element(),'#accountForm':new Element('form'),'#localPlay':new Element('button'),'#accountEmail':new Element('input'),'#accountPassword':new Element('input'),'.account-card':new Element()};this.elements['#accountForm'].button=this.button;}
}
const localStorage={getItem:k=>map.get(k)??null,setItem:(k,v)=>map.set(k,v),removeItem:k=>map.delete(k)};
function client(){return {auth:{signInWithPassword:async()=>({data:{user:{id:user}}}),getSession:async()=>({data:{session:saved?{user:{id:saved}}:null}}),signOut:async()=>{saved=null;}},from(){let mode='read',payload,filters={},single=false;const find=()=>rows[filters.user_id]?.[filters.character_class];const q={select(){return q;},eq(k,v){filters[k]=v;return q;},update(v){mode='update';payload=v;return q;},insert(v){mode='insert';payload=v;filters={user_id:v.user_id,character_class:v.character_class};return q;},
 then(res,rej){return Promise.resolve({data:Object.values(rows[filters.user_id]||{}).map(r=>JSON.parse(JSON.stringify(r)))}).then(res,rej);},
 async single(){rows[payload.user_id]=rows[payload.user_id]||{};rows[payload.user_id][payload.character_class]={character_class:payload.character_class,save_data:payload.save_data,revision:0};return {data:JSON.parse(JSON.stringify(rows[payload.user_id][payload.character_class]))};},
 async maybeSingle(){if(!online)return {error:{message:'offline'}};const r=find();if(!r)return {data:null};if(mode==='update'){if(r.revision!==filters.revision)return {data:null};Object.assign(r,JSON.parse(JSON.stringify(payload)));return {data:{revision:r.revision}};}return {data:JSON.parse(JSON.stringify(r))};}};return q;}};}
async function open(id,cls,viaSession){
 user=id;const made=[];const body=new Element('body');const document={body,createElement:tag=>{const e=new Element(tag);made.push(e);return e;}};
 const window={SEA_ACCOUNT_CONFIG:{url:'https://example.supabase.co',publishableKey:'sb_publishable_test'},supabase:{createClient:client},addEventListener(){}};
 const ctx={window,document,localStorage,queueMicrotask,setTimeout:()=>1,clearTimeout(){},Blob,URL,atob,location:{reload(){}}};vm.runInNewContext(code,ctx);
 saved=viaSession?id:null;const p=window.startAccount({online:true});const root=body.children[0];
 if(!viaSession)await root.elements['#accountForm'].onsubmit({preventDefault(){}});
 await tick();await tick();
 const label={sea:'Sea Eater',bloop:'Bloop',maja:'El Gran Maja'}[cls];
 const btn=made.find(e=>e.tag==='button'&&(e.textContent.startsWith(label+' Lv.')||e.textContent==='สร้างตัวละคร '+label));
 assert.ok(btn,'picker shows '+label);const text=btn.textContent;btn.click();return {session:await p,body,text};
}
(async()=>{
 map.set('sel01',JSON.stringify(data(7)));map.set('selcls','sea');map.set('sel-account-pending-v2:untouched','pending');
 // Default play never builds a password form or touches auth, even if configured.
 for(const cfg of [{},{url:'',publishableKey:''},{url:'https://example.supabase.co',publishableKey:'sb_publishable_test'}]){
  const before=JSON.stringify([...map]);
  const window={SEA_ACCOUNT_CONFIG:cfg};
  Object.defineProperty(window,'supabase',{get(){throw new Error('auth must not be touched');}});
  const document={createElement(){throw new Error('login DOM must not be created');}};
  vm.runInNewContext(code,{window,document,localStorage});
  const session=await window.startAccount();
  assert.equal(session.storage,localStorage);assert.equal(session.remote,false);
  assert.equal(JSON.stringify([...map]),before,'default startup leaves saves/journals unchanged');
 }
 map.clear();
 console.log('PASS: login-free local startup, no auth/credential form, no save changes even with configured account');
 page=await open('A','sea');assert.equal(page.text,'Sea Eater Lv.1');online=false;page.session.storage.setItem('sel01',JSON.stringify(data(2)));await tick();
 assert.equal(rows.A.sea.save_data.lv,1);assert.equal(map.size,1);
 online=true;page=await open('B','bloop');await tick();assert.equal(page.session.storage.getItem('sel01b'),JSON.stringify(data(1)));assert.equal(rows.B.bloop.revision,0);assert.equal(map.size,1);
 page=await open('A','sea');await tick();await tick();assert.equal(rows.A.sea.save_data.lv,2);assert.equal(map.size,0);
 // Same account, second character: separate level, untouched by the first.
 page=await open('A','bloop');assert.equal(page.text,'Bloop Lv.5');assert.equal(JSON.parse(page.session.storage.getItem('sel01b')).lv,5);assert.equal(page.session.storage.getItem('selcls'),'bloop');
 page.session.storage.setItem('sel01b',JSON.stringify(data(6)));await tick();await tick();assert.equal(rows.A.bloop.save_data.lv,6);assert.equal(rows.A.sea.save_data.lv,2,'other character unchanged');
 // Offline conflict on the first character still recovers.
 page=await open('A','sea');online=false;page.session.storage.setItem('sel01',JSON.stringify(data(3)));await tick();rows.A.sea.save_data=data(4);rows.A.sea.revision++;
 online=true;page=await open('A','sea');await tick();assert.equal(rows.A.sea.save_data.lv,4);assert.equal(map.size,1);assert.equal(JSON.parse(page.session.storage.getItem('sel01')).lv,3);
 // Signed-in device skips the password form and goes straight to the picker; a new class can be created.
 map.clear();page=await open('A','maja',true);assert.equal(page.text,'สร้างตัวละคร El Gran Maja');assert.equal(rows.A.maja.save_data.lv,1);
 console.log('PASS: synthetic offline queue survives reload, account isolation, retry, revision conflict, multiple characters per account, remembered login');
})().catch(e=>{console.error(e);process.exitCode=1;});
