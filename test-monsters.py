"""Local model/spawn/loot/save integration; same prerequisites as test-evolution.py."""
import os,threading,http.server,math,json
from pathlib import Path
from playwright.sync_api import sync_playwright
os.chdir(Path(__file__).resolve().parent)
artifacts=Path(os.environ.get('EVOLUTION_ARTIFACTS','/tmp/sea-evolution'));artifacts.mkdir(parents=True,exist_ok=True)
three=Path(os.environ.get('THREE_JS_PATH','/tmp/sea-evolution/three.min.js'));assert three.is_file(),'Set THREE_JS_PATH to a trusted local Three.js r128 file'
class H(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*a):pass
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),H);threading.Thread(target=server.serve_forever,daemon=True).start()
url=f'http://127.0.0.1:{server.server_port}/?debug=1'
html=Path('index.html').read_text().replace('function loop(){requestAnimationFrame(loop);','function loop(){requestAnimationFrame(loop);if(window.__pauseTest)return;')
html=html.replace('loop();\n}', 'window.__mt={P,sea,scene,ren,cam,mons,types,MAPS,spawn,game,kill,awardGear,save,organFor,applyJob,assignPursuers,renderEvo,stopGrace:()=>{grace=0;}};loop();\n}')
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--enable-unsafe-swiftshader'])
 ctx=browser.new_context(viewport={'width':900,'height':650});page=ctx.new_page();errors=[]
 page.on('pageerror',lambda e:errors.append(str(e)))
 page.on('console',lambda m:errors.append(m.text) if m.type=='error' else None)
 def route(r):
  u=r.request.url
  if 'three.min.js' in u:r.fulfill(path=str(three),content_type='application/javascript')
  elif 'cdn.jsdelivr.net' in u:r.fulfill(body='',content_type='application/javascript')
  elif '.supabase.co' in u:raise AssertionError('unexpected backend request')
  elif u.split('?')[0]==url.split('?')[0]:r.fulfill(body=html,content_type='text/html')
  else:r.continue_()
 ctx.route('**/*',route)
 page.add_init_script("if(!localStorage.seeded){localStorage.seeded='1';localStorage.selcls='sea';localStorage.sel01=JSON.stringify({lv:19,xp:0,q:0,qd:0,inv:{},seen:{}});}")
 def load():
  page.goto(url,wait_until='networkidle');page.locator('#localPlay').click();page.wait_for_function('window.__mt');page.evaluate('window.__pauseTest=true');page.add_style_tag(content='#debug,#msg,#zoneb{visibility:hidden!important}')
 load()
 report=page.evaluate('''()=>{const t=__mt;if(t.mons.length!==47||t.types.length!==7)throw Error('roster size');const counts={};for(const m of t.mons)counts[m.ty.n]=(counts[m.ty.n]||0)+1;
  for(const name of ['puffer','shrimp']){const m=t.mons.find(m=>m.ty.n===name),d=t.MAPS[m.map];for(let i=0;i<50;i++){t.spawn(m);if(Math.abs(m.g.position.x)>d.w/2||Math.abs(m.g.position.z)>d.d/2)throw Error('spawn bounds');}}
  for(const m of t.mons){const d=t.MAPS[m.map];if(!m.home||Math.abs(m.home.x)>d.w/2||Math.abs(m.home.z)>d.d/2)throw Error('home outside map');}
  t.stopGrace();t.sea.position.set(40,0,0);for(const m of t.mons){m.aggro=false;m.dead=0;m.flee=0;m.g.position.set(42,0,0);}t.assignPursuers();if(t.mons.filter(m=>m.aggro&&m.ty.n!=='boss').length>3)throw Error('pursuer cap');return counts;}''')
 assert report=={'ray':14,'shark':8,'whale':7,'eel':6,'puffer':6,'shrimp':5,'boss':1},report
 for name in ['puffer','shrimp']:
  page.evaluate('''(name)=>{const t=__mt;for(const m of t.mons){m.g.visible=m.ty.n===name;m.bar.visible=false;}t.sea.visible=false;const m=t.mons.find(m=>m.ty.n===name);m.g.position.set(0,0,0);m.g.rotation.set(0,0,0);m.g.updateMatrixWorld(true);window.__model=m;}''',name)
  for i,yaw in enumerate([0,math.pi/2,math.pi,3*math.pi/2]):
   page.evaluate('''(yaw)=>{const t=__mt;t.cam.position.set(Math.sin(yaw)*6,3.4,Math.cos(yaw)*6);t.cam.lookAt(0,1,0);t.ren.render(t.scene,t.cam);}''',yaw)
   page.screenshot(path=str(artifacts/f'monster-{name}-{i}.png'))
 # Verify killed new monsters contribute essence/discovery/materials and loot is saved.
 result=page.evaluate('''()=>{const t=__mt,out={};for(const name of ['puffer','shrimp']){const m=t.mons.find(m=>m.ty.n===name),before=t.P.es;t.kill(m);out[name]=t.P.es-before;if(t.P.kc[name]!==1||t.P.seen[name]!==1)throw Error('discovery');}
  for(const id of ['crest','spine','lance']){const monster=id==='lance'?'shrimp':'puffer',rolls=[0,id==='spine'?.6:0,0,0],o=t.awardGear(monster,()=>rolls.shift());if(o.org!==id)throw Error('new loot');const slot=id==='crest'?'head':id==='spine'?'back':'tail';t.P.mu[slot]=o.id;}t.applyJob();t.save();return {essence:out,mu:{...t.P.mu},inv:{...t.P.inv}};}''')
 assert result['essence']=={'puffer':2,'shrimp':3}
 page.locator('#dexb').dispatch_event('pointerdown');assert 'พองตัวก่อนโจมตีหนาม' in page.locator('#dex').inner_text();assert 'ง้างก่อนพุ่ง' in page.locator('#dex').inner_text();page.locator('#equipGear').click()
 assert 'แพนหางผลึก' in page.locator('#evo').inner_text()
 load();assert page.evaluate('__mt.P.mu')==result['mu']
 for id in result['mu'].values():assert page.evaluate('(id)=>__mt.P.inv["eq:"+id]',id)>=1
 assert page.evaluate('__mt.P.seen.puffer && __mt.P.seen.shrimp')==1
 # Compare legacy neutral view against all three new shared attachments, without changing base mesh.
 for cls in ['sea','bloop','maja']:
  page.evaluate('(cls)=>{localStorage.selcls=cls;localStorage.setItem({sea:"sel01",bloop:"sel01b",maja:"sel01m"}[cls],JSON.stringify({lv:19,xp:0,q:0,qd:0,inv:{"eq:crest:4:common":1,"eq:spine:4:common":1,"eq:lance:12:common":1},seen:{},mu:{head:"crest:4:common",back:"spine:4:common",tail:"lance:12:common"}}));}',cls)
  load();page.wait_for_timeout(100)
  page.evaluate('''()=>{const t=__mt;for(const m of t.mons){m.g.visible=false;m.bar.visible=false;}t.sea.position.set(0,0,0);t.sea.rotation.set(0,0,0);t.cam.position.set(8,4.5,4);t.cam.lookAt(0,1.8,0);t.ren.render(t.scene,t.cam);}''')
  page.screenshot(path=str(artifacts/f'new-gear-{cls}.png'))
 assert not errors,errors
 print(json.dumps({'result':'PASS','roster':report,'essence':result['essence'],'spawn_checks':100,'views':8,'gear_species_views':3,'console_errors':errors}),flush=True)
 browser.close()
server.shutdown()
