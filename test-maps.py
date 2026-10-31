"""Local Chromium: full-edge block traversal, map UI, spawn lifecycle and legacy saves.
Requires Playwright, /usr/bin/chromium and THREE_JS_PATH (Three.js r128).
Screenshots stay in EVOLUTION_ARTIFACTS (/tmp/sea-evolution by default).
"""
import os,threading,http.server,json
from pathlib import Path
from playwright.sync_api import sync_playwright
os.chdir(Path(__file__).resolve().parent)
artifacts=Path(os.environ.get('EVOLUTION_ARTIFACTS','/tmp/sea-evolution'));artifacts.mkdir(parents=True,exist_ok=True)
three=Path(os.environ.get('THREE_JS_PATH','/tmp/sea-evolution/three.min.js'));assert three.is_file()
class H(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*a):pass
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),H);threading.Thread(target=server.serve_forever,daemon=True).start()
url=f'http://127.0.0.1:{server.server_port}/?debug=1'
html=Path('index.html').read_text().replace('function loop(){requestAnimationFrame(loop);','function loop(){requestAnimationFrame(loop);if(window.__pauseTest)return;')
expose='window.__maps={P,sea,scene,cam,ren,MAPS,PORTALS,SPAWN,mons,spawn,setMap,mapExit,mapEdge,game,keys,shots,vortices,shoot,whirlpool,updatePortals,updateMini,updateZone,updateNames,updateBgm,BGM,ZN,save,kill,openMap,closeMap,get current(){return curMap},get grace(){return grace},ready:()=>{grace=0}};'
html=html.replace('loop();\n}',expose+'loop();\n}')
legacy={'lv':8,'xp':12,'q':2,'qd':1,'inv':{'ครีบกระเบน':7},'seen':{'ray':1}}
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--enable-unsafe-swiftshader'])
 ctx=browser.new_context(viewport={'width':390,'height':844});page=ctx.new_page();errors=[]
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
 page.add_init_script('if(!localStorage.seeded){localStorage.seeded="1";localStorage.selcls="sea";localStorage.snd="0";localStorage.sel01=JSON.stringify('+json.dumps(legacy)+');}')
 def load(target=url):
  page.goto(target,wait_until='networkidle');assert page.locator('#accountGate').count()==0;page.wait_for_function('window.__maps');page.evaluate('window.__pauseTest=true');page.add_style_tag(content='#debug,#msg,#zoneb{visibility:hidden!important}')
 load()
 assert page.evaluate('__maps.current')==0
 assert page.evaluate('__maps.P.inv["ครีบกระเบน"]')==7
 # Cross all 26 shared edges at three lateral positions, not just the old portal center.
 portals=page.evaluate('__maps.PORTALS.map(p=>({map:p.map,to:p.to.map}))')
 report=page.evaluate("""()=>{const t=__maps;let trips=0;for(const [i,p] of t.PORTALS.entries())for(const f of [-.8,0,.8]){
  const A=t.MAPS[p.map];t.setMap(p.map);t.ready();
  t.sea.position.set(p.dx?p.dx*(A.w/2-1):f*(A.w/2-2),0,p.dz?p.dz*(A.d/2-1):f*(A.d/2-2));
  const expected=t.mapExit(p.map,t.sea.position.x,t.sea.position.z),offset=t.cam.position.clone().sub(t.sea.position);
  t.updatePortals(0);if(t.current!==p.to.map)throw Error('edge destination');
  if(Math.hypot(t.sea.position.x-expected.x,t.sea.position.z-expected.z)>1e-9)throw Error('lateral arrival');
  if(t.cam.position.clone().sub(t.sea.position).distanceTo(offset)>1e-8)throw Error('camera jumps');
  if(t.grace<3)throw Error('arrival protection');
  for(const d of t.MAPS)if(d.group.visible!==(d.id===t.current))throw Error('world visibility');
  for(const m of t.mons)if(m.map!==t.current&&(!m.parked||m.g.visible||m.dead<1e8))throw Error('off-map monster');
  t.updateMini(1);t.updateZone(.01);t.updateBgm(.01);if(t.BGM.want!==t.MAPS[t.current].music)throw Error('music');
  t.updatePortals(0);if(t.current!==p.to.map)throw Error('automatic bounce');trips++;
 }
 for(const d of t.MAPS){const walls=d.group.children.filter(c=>c.userData.closedEdge);
  if(walls.length!==4-t.PORTALS.filter(p=>p.map===d.id).length)throw Error('connected side still walled');
  for(const w of walls)if(t.PORTALS.some(p=>p.map===d.id&&p.dx===w.userData.closedEdge.dx&&p.dz===w.userData.closedEdge.dz))throw Error('exit wall');
 }
 // Standing at the old ring location does not teleport anymore.
 t.setMap(0);const p=t.PORTALS.find(p=>p.map===0);t.sea.position.set(p.x,0,p.z);t.updatePortals(0);if(t.current!==0)throw Error('old ring trigger');
 // Clear attack meshes so spells cannot hit monsters in another block.
 let disposed=0;t.shoot(1,1,1,0xffffff,.1);t.whirlpool();const fx=[...t.shots,...t.vortices];for(const a of fx){a.mesh.geometry.addEventListener('dispose',()=>disposed++);a.mesh.material.addEventListener('dispose',()=>disposed++);}
 t.sea.position.set(p.dx*(t.MAPS[0].w/2-1),0,p.dz*(t.MAPS[0].d/2-1));t.updatePortals(0);
 if(t.shots.length||t.vortices.length||disposed!==fx.length*2||fx.some(a=>a.mesh.parent))throw Error('old-block attack remains');
 if(document.querySelector('#fadeov'))throw Error('edge walk should not fade/lock');
 return {trips};}""")
 assert report['trips']==78,report
 # Actual held walking input across all four town edges continues into the next block.
 for key,dx,dz,to in [('d',1,0,12),('a',-1,0,7),('w',0,-1,5),('s',0,1,1)]:
  page.evaluate('''([dx,dz])=>{const t=__maps;t.setMap(0);t.sea.position.set(dx*(t.MAPS[0].w/2-2),0,dz*(t.MAPS[0].d/2-2));__cam.yaw=0;window.__pauseTest=false;}''',[dx,dz])
  page.keyboard.down(key)
  page.wait_for_function('(to)=>__maps.current===to',arg=to,timeout=120000)
  page.keyboard.up(key);page.evaluate('window.__pauseTest=true')
  assert page.evaluate('__cam.yaw')==0
 # In every map, exercise actual spawn/scaling and clamps, including empty town.
 page.evaluate('''()=>{const t=__maps;for(const d of t.MAPS){t.setMap(d.id);t.sea.position.set(0,0,0);
  for(const m of t.mons.filter(m=>m.map===d.id)){t.spawn(m);if(m.hp!==m.ty.hp*d.hpScale*1.8||m.xf!==d.xpScale)throw Error('tier scaling');if(m.parked||!m.g.visible)throw Error('active spawn');}
  t.sea.position.set(999,0,-999);t.updatePortals(0);const active=t.MAPS[t.current];if(Math.abs(t.sea.position.x)>active.w/2-1||Math.abs(t.sea.position.z)>active.d/2-1)throw Error('player bounds');
 }const boss=t.mons.find(m=>m.ty.n==='boss');t.setMap(boss.map);boss.aggro=true;t.updateBgm(.1);if(t.BGM.want!=='boss')throw Error('boss music');t.setMap(0);t.updateBgm(4);if(t.BGM.want!=='town')throw Error('town music');
 // Preserve a respawn timer while away, restore it when returning.
 const m=t.mons.find(m=>m.ty.n==='ray');t.setMap(m.map);m.dead=7;m.g.visible=false;t.setMap(0);t.setMap(m.map);if(m.dead!==7||m.g.visible)throw Error('respawn lifecycle');
 t.setMap(0);t.sea.position.set(0,0,0);t.save();}''')
 saved=page.evaluate('JSON.parse(localStorage.sel01)')
 load();assert page.evaluate('__maps.current')==0
 for key in ['lv','xp','q','qd','inv','seen']:
  assert page.evaluate('(key)=>__maps.P[key]',key)==saved[key],key
 assert page.evaluate('__maps.P.ev')==0
 assert page.evaluate('__maps.P.rf')=={'head':0,'back':0,'tail':0}
 # Both mobile orientations, plus narrow screens and tablet dimensions (emulation only).
 for width,height in [(390,844),(844,390),(320,568),(768,1024),(1024,768)]:
  page.set_viewport_size({'width':width,'height':height})
  page.evaluate('__maps.openMap()');page.wait_for_timeout(450)
  assert page.locator('[data-mtab]').count()==14
  for mapid in range(14):
   page.locator(f'[data-mtab="{mapid}"]').click()
   assert page.locator(f'[data-mtab="{mapid}"]').get_attribute('aria-pressed')=='true'
   assert 'undefined' not in page.locator('#mapov').inner_text()
  # Town screenshot shows the cross; poison/spike/weird examples show full legends.
  for mapid in [0,2,9,3]:
   page.locator(f'[data-mtab="{mapid}"]').click()
   page.evaluate("document.querySelector('.mapbox').scrollTop=0")
   page.screenshot(path=str(artifacts/f'maps-{width}x{height}-{mapid}.png'))
  assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'),'horizontal overflow'
  for box in page.locator('[data-mtab]').all():
   b=box.bounding_box();assert b['x']>=0 and b['x']+b['width']<=width
   if box.locator('small').count():
    level=box.locator('small').bounding_box();assert level['y']>=b['y'] and level['y']+level['height']<=b['y']+b['height'],'level wraps outside button'
  page.locator('[data-mclose]').click();assert not page.locator('#mapov').is_visible()
 # Scene views (normal + close), town and all four branches + boss.
 for width,height in [(390,844),(844,390)]:
  page.set_viewport_size({'width':width,'height':height})
  # Resize reapplies the canvas size for ~1 s; paused test rendering must wait.
  page.wait_for_timeout(1200)
  for mapid in [0,5,7,1,12,2,6,8,9,10,11,13,3,4]:
   page.evaluate('''id=>{const t=__maps;t.setMap(id);t.sea.position.set(0,0,0);t.updateMini(1);t.updateZone(2);t.scene.background.setHex(t.MAPS[id].bg);t.scene.fog.color.copy(t.scene.background);}''',mapid)
   for view,dist in [('normal',24),('close',10)]:
    page.evaluate('''dist=>{const t=__maps;t.cam.position.set(dist*.6,dist*.8,dist);t.cam.lookAt(0,1,0);t.updateNames();t.updatePortals(0);t.ren.render(t.scene,t.cam);}''',dist)
    page.screenshot(path=str(artifacts/f'map-scene-{width}x{height}-{mapid}-{view}.png'))
 # FPS can be enabled from the book without a debug URL, and survives reload.
 page.set_viewport_size({'width':390,'height':844})
 normal_url=url.split('?')[0]
 load(normal_url)
 page.add_style_tag(content='#debug{visibility:visible!important}')
 assert not page.locator('#debug').is_visible()
 page.locator('#dexb').dispatch_event('pointerdown');page.locator('#fpsBtn').click()
 assert page.locator('#fpsBtn').get_attribute('aria-pressed')=='true'
 page.locator('#dexb').dispatch_event('pointerdown')
 page.evaluate('window.__pauseTest=false')
 page.wait_for_function('/^FPS: [0-9]+$/.test(document.querySelector("#debug").textContent)',timeout=120000)
 page.screenshot(path=str(artifacts/'fps-enabled-390x844.png'))
 load(normal_url);page.add_style_tag(content='#debug{visibility:visible!important}')
 assert page.locator('#debug').is_visible()
 page.locator('#dexb').dispatch_event('pointerdown');page.locator('#fpsBtn').click()
 assert not page.locator('#debug').is_visible()
 load(normal_url);assert not page.locator('#debug').is_visible()
 # Fresh child device: select a character directly, without any password field.
 fresh=browser.new_context(viewport={'width':768,'height':1024})
 fresh.route('**/*',route);fp=fresh.new_page();fp.set_default_timeout(120000)
 fp.on('pageerror',lambda e:errors.append(str(e)))
 fp.add_init_script("""window.__loginFieldsSeen=false;new MutationObserver(()=>{if(document.querySelector('input[type=password],#accountForm'))window.__loginFieldsSeen=true;}).observe(document,{subtree:true,childList:true});""")
 fp.goto(normal_url,wait_until='networkidle');fp.wait_for_function('window.__maps');fp.evaluate('window.__pauseTest=true')
 assert fp.locator('#pick').is_visible()
 assert fp.locator('#accountGate,input[type=password],#accountEmail').count()==0
 fp.screenshot(path=str(artifacts/'no-login-picker-768x1024.png'))
 fp.locator('[data-c="bloop"]').click();fp.wait_for_function('window.__maps && localStorage.selcls==="bloop"');fp.evaluate('window.__pauseTest=true')
 assert not fp.locator('#pick').is_visible()
 assert fp.evaluate('window.__loginFieldsSeen') is False
 # Existing daily login reward may level a newly selected character immediately.
 assert fp.evaluate('localStorage.selcls')=='bloop'
 assert fp.evaluate('__maps.P.lv===JSON.parse(localStorage.sel01b).lv && __maps.P.lv>=1')
 for width,height in [(768,1024),(1024,768)]:
  fp.set_viewport_size({'width':width,'height':height});fp.wait_for_timeout(1200)
  fp.evaluate('__maps.ren.render(__maps.scene,__maps.cam)')
  fp.screenshot(path=str(artifacts/f'no-login-playing-{width}x{height}.png'))
 fp.reload(wait_until='networkidle');fp.wait_for_function('window.__maps')
 assert fp.locator('#accountGate,input[type=password]').count()==0
 assert fp.evaluate('localStorage.selcls')=='bloop'
 fresh.close()
 assert not errors,errors
 print(json.dumps({'result':'PASS','edge_crossings':report['trips'],'held_input_directions':4,'maps':14,'screen_sizes':5,'legacy_save':'loaded/reloaded','fps_toggle':'no query string, numeric counter, persists on/off','local_start':'fresh picker, character selection, returning player; no password form','console_errors':errors}),flush=True)
 browser.close()
server.shutdown()
