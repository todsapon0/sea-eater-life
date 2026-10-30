"""Local-only browser regression. Requires Python Playwright and /usr/bin/chromium.
THREE_JS_PATH: trusted local Three.js r128 file; EVOLUTION_ARTIFACTS: output directory.
No credentials, reference images or backend requests. Instruments HTML only in memory.
Run: THREE_JS_PATH=/path/to/three.min.js python3 test-evolution.py
"""
import os,threading,http.server,json,math,re
from pathlib import Path
from playwright.sync_api import sync_playwright
root=Path(__file__).resolve().parent;os.chdir(root)
artifacts=Path(os.environ.get('EVOLUTION_ARTIFACTS','/tmp/sea-evolution'));artifacts.mkdir(parents=True,exist_ok=True)
three=Path(os.environ.get('THREE_JS_PATH','/tmp/sea-evolution/three.min.js'));assert three.is_file(),'Set THREE_JS_PATH to a trusted local Three.js r128 file'
class Handler(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*a):pass
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),Handler);threading.Thread(target=server.serve_forever,daemon=True).start()
url=f'http://127.0.0.1:{server.server_port}/?debug=1'
html=(root/'index.html').read_text()
# Test-only instrumentation served in memory: never added to repository or shipped.
html=html.replace('loop();\n}', 'window.__evoTest={P,sea,cam,ren,ORG,JOBS,applyJob,save,kill,mons,updateEvo,organFor,evoReady,renderEvo,doSlam,whirlpool,updateMaja,vortices,resetCooldown:()=>{slamCD=0;biteT=0}};loop();\n}')
with sync_playwright() as p:
 b=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--enable-unsafe-swiftshader'])
 for cls,job in [('sea','guardian'),('bloop','priest'),('maja','frost')]:
  ctx=b.new_context(viewport={'width':1000,'height':780});page=ctx.new_page();errors=[];network=[]
  page.on('pageerror',lambda e:errors.append(str(e)))
  page.on('console',lambda m:errors.append(m.text) if m.type=='error' else None)
  def route(r):
   u=r.request.url
   if 'three.min.js' in u:r.fulfill(path=str(three),content_type='application/javascript')
   elif 'cdn.jsdelivr.net' in u:r.fulfill(body='',content_type='application/javascript')
   elif '.supabase.co' in u:network.append(u);r.abort()
   elif u.startswith(url.split('?')[0]) and (u.split('?')[0].endswith('/') or 'index.html' in u):r.fulfill(body=html,content_type='text/html')
   else:r.continue_()
  ctx.route('**/*',route)
  key={'sea':'sel01','bloop':'sel01b','maja':'sel01m'}[cls]
  seed={'lv':20,'xp':0,'q':0,'qd':0,'inv':{},'seen':{},'job':job,'st':2,'es':600}
  page.add_init_script(f"if(!localStorage.getItem('seeded')){{localStorage.setItem('seeded','1');localStorage.setItem('selcls',{json.dumps(cls)});localStorage.setItem({json.dumps(key)},JSON.stringify({json.dumps(seed)}));}}")
  def load():
   page.goto(url,wait_until='networkidle');page.locator('#localPlay').click();page.wait_for_function('window.__evoTest && document.querySelector("canvas")')
  load();page.evaluate('''()=>{const t=__evoTest,P=t.P,seed={...P};for(const c of [{ev:0,lv:7,es:600,job:seed.job,want:false},{ev:0,lv:8,es:39,job:seed.job,want:false},{ev:0,lv:8,es:40,job:seed.job,want:true},{ev:1,lv:13,es:600,job:seed.job,want:false},{ev:2,lv:20,es:600,job:'',want:false},{ev:2,lv:20,es:600,job:'__proto__',want:false},{ev:2,lv:20,es:600,job:'invalid',want:false},{ev:2,lv:20,es:360,job:seed.job,want:true}]){Object.assign(P,c);if(t.evoReady()!==c.want)throw Error('requirements gate');}Object.assign(P,seed);t.applyJob();}''');page.evaluate('window.__cam.dist=9');page.wait_for_timeout(2500)
  baseline=page.locator('#debug').inner_text()
  page.locator('#evob').click();assert page.locator('[data-evolve]').is_enabled()
  assert page.locator('[data-slot="back"]').count()==0
  page.once('dialog',lambda d:d.dismiss());page.locator('[data-evolve]').click();assert page.evaluate('__evoTest.P.ev')==0
  page.on('dialog',lambda d:d.accept())
  for stage,ess in [(1,560),(2,420),(3,60)]:
   page.locator('[data-evolve]').click();assert page.evaluate('__evoTest.P.ev')==stage;assert page.evaluate('__evoTest.P.es')==ess
  assert page.locator('[data-evolve]').count()==0
  # Check every organ's multiplier, free removal, filtering, and geometry disposal.
  print(cls+': evolution UI PASS',flush=True)
  report=page.evaluate('''()=>{const t=__evoTest,P=t.P;let count=0;const fields={dm:'dmgMul',hp:'hpMul',tk:'dmgTaken',heal:'healMul',cdr:'cdr',shm:'shMul',bl:'blMul',sp:'spMul'};
   const near=(a,b)=>{if(Math.abs(a-b)>1e-8)throw Error(a+' != '+b)};
   const j=t.JOBS[localStorage.selcls][P.job];P.mu={};t.applyJob();near(P.hpMul,(j.hp||1)*1.08*1.36);near(P.dmgMul,(j.dm||1)*1.08*1.18);
   const old=P.ev;P.ev=0;P.mu={head:'fang',back:'scale',tail:'whip'};t.applyJob();near(P.dmgMul,(j.dm||1)*1.08);P.ev=old;
   for(const slot of Object.keys(t.ORG))for(const o of t.ORG[slot]){P.mu={};t.applyJob();const base={...P};P.mu[slot]=o.id;t.applyJob();for(const [k,f]of Object.entries(fields))near(P[f],base[f]*((!o.only||o.only===localStorage.selcls)?o[k]||1:1));count++;}
   P.mu={};t.applyJob();const hp=P.hp;P.mu.back='scale';t.applyJob();if(P.hp<hp)throw Error('HP decreased');P.mu={};t.applyJob();return {organsChecked:count};}''')
  print(cls+': all organ multipliers PASS',flush=True)
  # Select species-specific organs through the actual UI.
  choices={'sea':['jaw','shell','spike'],'bloop':['bub','wing','glow'],'maja':['horn','crys','orb']}[cls]
  for slot,organ in zip(['head','back','tail'],choices):page.locator(f'[data-slot="{slot}"][data-organ="{organ}"]').click()
  page.locator('[data-remove="tail"]').click();assert page.evaluate('__evoTest.P.mu.tail') is None
  page.locator(f'[data-organ="{choices[2]}"]').click()
  saved=page.evaluate(f'JSON.parse(localStorage.getItem({json.dumps(key)}))')
  assert saved['ev']==3 and saved['es']==60 and saved['mu']==dict(zip(['head','back','tail'],choices))
  page.locator('[data-close]').click()
  page.locator('#evob').click();page.locator('#evo').evaluate('(e)=>e.scrollTop=0');page.screenshot(path=str(artifacts/f'{cls}-evolution-ui.png'));page.locator('[data-close]').click()
  # Four angles per species and both job appearances, without changing body geometry.
  for variant in ([] if os.environ.get('EVOLUTION_QUICK') else page.evaluate('Object.keys(__evoTest.JOBS[localStorage.selcls])')):
   page.evaluate('(job)=>{__evoTest.P.job=job;__evoTest.applyJob();}',variant);page.wait_for_timeout(100)
   for i,yaw in enumerate([0,math.pi/2,math.pi,3*math.pi/2]):
    page.evaluate('(yaw)=>{window.__cam.yaw=yaw;window.__cam.dist=15;const s=__evoTest.sea;__evoTest.cam.position.set(s.position.x+Math.sin(yaw)*15*Math.cos(__cam.pitch),s.position.y+15*Math.sin(__cam.pitch),s.position.z+Math.cos(yaw)*15*Math.cos(__cam.pitch));}',yaw);page.wait_for_timeout(350)
    page.screenshot(path=str(artifacts/f'{cls}-{variant}-{i}.png'))
  page.set_viewport_size({'width':390,'height':844});page.evaluate('(yaw)=>{window.__cam.yaw=yaw;window.__cam.dist=24;}',math.pi/2);page.wait_for_timeout(500);page.screenshot(path=str(artifacts/f'{cls}-mobile-side.png'))
  boxes=page.evaluate('''()=>{const a=document.querySelector('#hud').getBoundingClientRect(),b=document.querySelector('#topbar').getBoundingClientRect();return {hudRight:a.right,toolbarLeft:b.left};}''');assert boxes['hudRight']<boxes['toolbarLeft'],boxes
  page.locator('#evob').click();page.locator('#evo').evaluate('(e)=>e.scrollTop=0');page.screenshot(path=str(artifacts/f'{cls}-mobile-ui.png'));page.locator('[data-close]').click();page.set_viewport_size({'width':1000,'height':780})
  page.evaluate('(job)=>{__evoTest.P.job=job;__evoTest.applyJob();__evoTest.save();}',job)
  load();assert page.evaluate('__evoTest.P.ev')==3;assert page.evaluate('__evoTest.P.mu')==saved['mu']
  assert page.evaluate('__evoTest.P.es')==60
  page.evaluate('window.__cam.dist=9');page.wait_for_timeout(2000)
  # Actual healing and whirlpool ticks honor mutation/job multipliers.
  if cls=='bloop':
   page.evaluate("()=>{const t=__evoTest;t.P.hp=10;t.resetCooldown();const want=Math.min(t.P.max,10+t.P.max*.3*t.P.healMul);t.doSlam();if(Math.abs(t.P.hp-want)>1e-8)throw Error('healing multiplier');}")
  if cls=='maja':
   page.evaluate("()=>{const t=__evoTest;t.whirlpool();const m=t.mons[0];m.dead=0;m.hp=10000;m.g.position.copy(t.vortices[0].mesh.position);t.updateMaja(.01);if(Math.abs((10000-m.hp)-(4+t.P.lv)*t.P.dmgMul)>1e-8)throw Error('whirlpool multiplier');}")
  # Kill essence rewards, no backend.
  rewards=page.evaluate('''()=>{const t=__evoTest,out={};for(const name of ['ray','shark','eel','whale','boss']){const m=t.mons.find(m=>m.ty.n===name),before=t.P.es;t.kill(m);out[name]=t.P.es-before;}return out;}''')
  assert rewards=={'ray':1,'shark':2,'eel':2,'whale':3,'boss':30},rewards
  page.wait_for_timeout(1600);after=page.locator('#debug').inner_text()
  assert not errors,errors;assert not network,network
  print(json.dumps({'class':cls,'result':'PASS','multipliers':report,'rewards':rewards,'fps_before':baseline,'fps_after':after,'errors':errors},ensure_ascii=False),flush=True)
  ctx.close()
 b.close()
server.shutdown()
