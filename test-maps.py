"""Local Chromium: actual directional warps, map UI, spawn lifecycle and legacy saves.
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
expose='window.__maps={P,sea,scene,cam,ren,MAPS,PORTALS,SPAWN,mons,spawn,setMap,updatePortals,updateMini,updateZone,updateNames,updateBgm,BGM,ZN,save,kill,openMap,closeMap,get current(){return curMap},get grace(){return grace},get cooldown(){return warpCD},ready:()=>{warpCD=0;grace=0}};'
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
  page.goto(target,wait_until='networkidle');page.locator('#localPlay').click();page.wait_for_function('window.__maps');page.evaluate('window.__pauseTest=true');page.add_style_tag(content='#debug,#msg,#zoneb{visibility:hidden!important}')
 load()
 assert page.evaluate('__maps.current')==0
 assert page.evaluate('__maps.P.inv["ครีบกระเบน"]')==7
 # Walk into all 26 real portal triggers; follow the async warp and check protection,
 # arrival, correct visible world/monsters, no bounce, and music/quest routing.
 portals=page.evaluate('__maps.PORTALS.map(p=>({map:p.map,to:p.to.map}))')
 for i,pair in enumerate(portals):
  page.evaluate('''i=>{const t=__maps,p=t.PORTALS[i];t.setMap(p.map);t.ready();t.sea.position.set(p.x,0,p.z);t.updatePortals(0);}''',i)
  page.wait_for_function('(to)=>__maps.current===to',arg=pair['to'])
  page.evaluate('''i=>{const t=__maps,p=t.PORTALS[i];if(t.sea.position.x!==p.to.x||t.sea.position.z!==p.to.z)throw Error('arrival');if(t.grace<3||t.cooldown!==2)throw Error('protection');
   for(const d of t.MAPS)if(d.group.visible!==(d.id===t.current))throw Error('world visibility');
   for(const m of t.mons)if(m.map!==t.current&&(!m.parked||m.g.visible||m.dead<1e8))throw Error('off-map monster');
   t.updateMini(1);t.updateZone(.01);t.updateBgm(.01);if(t.BGM.want!==t.MAPS[t.current].music)throw Error('music');t.updatePortals(0);
   if(t.ZN.puffer!=='ลานปักเป้า / แนวปะการังหนาม / ถ้ำผลึกหนาม')throw Error('dex habitat');}''',i)
  page.wait_for_timeout(300)
  assert page.evaluate('__maps.current')==pair['to']
 # In every map, exercise actual spawn/scaling and clamps, including empty town.
 page.evaluate('''()=>{const t=__maps;for(const d of t.MAPS){t.setMap(d.id);t.sea.position.set(0,0,0);
  for(const m of t.mons.filter(m=>m.map===d.id)){t.spawn(m);if(m.hp!==m.ty.hp*d.hpScale*1.8||m.xf!==d.xpScale)throw Error('tier scaling');if(m.parked||!m.g.visible)throw Error('active spawn');}
  t.sea.position.set(999,0,-999);t.updatePortals(0);if(Math.abs(t.sea.position.x)>d.w/2-1||Math.abs(t.sea.position.z)>d.d/2-1)throw Error('player bounds');
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
 assert not errors,errors
 print(json.dumps({'result':'PASS','portal_trips':len(portals),'maps':14,'screen_sizes':5,'legacy_save':'loaded/reloaded','fps_toggle':'no query string, numeric counter, persists on/off','console_errors':errors}),flush=True)
 browser.close()
server.shutdown()
