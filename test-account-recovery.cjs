const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const code = fs.readFileSync(__dirname + '/account.js', 'utf8');
const tick = () => new Promise(resolve => setImmediate(resolve));
const data = lv => ({lv,xp:0,qd:0,q:0,inv:{},seen:{}});
const rows = {A:{character_class:'sea',save_data:data(1),revision:0},B:{character_class:'bloop',save_data:data(1),revision:0}};
const map = new Map(); let online=true, user='A', page;
class Element {
  constructor(tag='div'){this.tag=tag;this.children=[];this.textContent='';this.hidden=false;this.disabled=false;this.classList={add(){}};}
  append(...items){this.children.push(...items);} prepend(item){this.children.unshift(item);}
  remove(){} querySelector(q){return this.elements?.[q] || (q==='button' ? this.button : null);}
  querySelectorAll(){return [];} click(){if(this.onclick)this.onclick();}
  set innerHTML(v){this.button=new Element('button');this.elements={'#accountError':new Element(),'#accountForm':new Element('form'),'#localPlay':new Element('button'),'#accountEmail':new Element('input'),'#accountPassword':new Element('input'),'.account-card':new Element()};this.elements['#accountForm'].button=this.button;}
}
const localStorage={getItem:k=>map.get(k)??null,setItem:(k,v)=>map.set(k,v),removeItem:k=>map.delete(k)};
function client(){return {auth:{signInWithPassword:async()=>({data:{user:{id:user}}})},from(){let mode='read',payload, filters={};const q={select(){return q;},eq(k,v){filters[k]=v;return q;},update(v){mode='update';payload=v;return q;},async maybeSingle(){if(!online)return {error:{message:'offline'}};const r=rows[filters.user_id];if(!r)return {data:null};if(mode==='update'){if(r.revision!==filters.revision)return {data:null};Object.assign(r,JSON.parse(JSON.stringify(payload)));return {data:{revision:r.revision}};}return {data:JSON.parse(JSON.stringify(r))};}};return q;}};}
async function open(id){
 user=id;const body=new Element('body');const document={body,createElement:tag=>new Element(tag)};
 const window={SEA_ACCOUNT_CONFIG:{url:'https://example.supabase.co',publishableKey:'sb_publishable_test'},supabase:{createClient:client},addEventListener(){}};
 const ctx={window,document,localStorage,queueMicrotask,setTimeout:()=>1,clearTimeout(){},Blob,URL,atob};vm.runInNewContext(code,ctx);
 const p=window.startAccount();const root=body.children[0];await root.elements['#accountForm'].onsubmit({preventDefault(){}});return {session:await p,body};
}
(async()=>{
 page=await open('A');online=false;page.session.storage.setItem('sel01',JSON.stringify(data(2)));await tick();
 assert.equal(rows.A.save_data.lv,1);assert.equal(map.size,1);
 online=true;page=await open('B');await tick();assert.equal(page.session.storage.getItem('sel01b'),JSON.stringify(data(1)));assert.equal(rows.B.revision,0);assert.equal(map.size,1);
 page=await open('A');await tick();await tick();assert.equal(rows.A.save_data.lv,2);assert.equal(map.size,0);
 online=false;page.session.storage.setItem('sel01',JSON.stringify(data(3)));await tick();rows.A.save_data=data(4);rows.A.revision++;
 online=true;page=await open('A');await tick();assert.equal(rows.A.save_data.lv,4);assert.equal(map.size,1);assert.equal(JSON.parse(page.session.storage.getItem('sel01')).lv,3);
 console.log('PASS: synthetic offline queue survives reload, account isolation, retry, and revision conflict');
})().catch(e=>{console.error(e);process.exitCode=1;});

