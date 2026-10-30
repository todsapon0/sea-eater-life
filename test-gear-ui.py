"""Local equipment comparison/sorting regression. Same prerequisites as test-evolution.py."""
import os,threading,http.server
from pathlib import Path
from playwright.sync_api import sync_playwright
os.chdir(Path(__file__).resolve().parent)
artifacts=Path(os.environ.get('EVOLUTION_ARTIFACTS','/tmp/sea-evolution'));artifacts.mkdir(parents=True,exist_ok=True)
three=Path(os.environ.get('THREE_JS_PATH','/tmp/sea-evolution/three.min.js'));assert three.is_file(),'Set THREE_JS_PATH to a trusted local Three.js r128 file'
class H(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*a):pass
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),H);threading.Thread(target=server.serve_forever,daemon=True).start()
url=f'http://127.0.0.1:{server.server_port}/?debug=1'
html=Path('index.html').read_text().replace('loop();\n}', 'window.__gearUI=P;loop();\n}')
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
 page.add_init_script("""if(!localStorage.seeded){localStorage.seeded='1';localStorage.selcls='sea';localStorage.sel01=JSON.stringify({lv:8,xp:0,qd:0,q:0,ev:0,inv:{'eq:fang:1:common':1,'eq:fang:8:rare':1,'eq:fang:20:epic':1,'eq:helm:1:common':1},seen:{},mu:{head:'fang:1:common'}});} """)
 def load():
  page.goto(url,wait_until='networkidle');page.locator('#localPlay').click();page.wait_for_function('window.__gearUI')
 def open_gear():
  page.locator('#dexb').dispatch_event('pointerdown');page.locator('#equipGear').click()
 load();open_gear();inventory=page.evaluate('JSON.stringify(__gearUI.inv)')
 assert 'ดาเมจ +12%' in page.locator('#gearBonuses').inner_text()
 helm=page.locator('[data-organ="helm:1:common"]')
 assert 'ดาเมจ -10.7%' in helm.locator('.gear-down').inner_text()
 assert 'ดาเมจที่รับ -8%' in helm.locator('.gear-up').inner_text()
 locked=page.locator('[data-organ="fang:20:epic"]');assert locked.is_disabled();assert 'ขาดอีก 12 เลเวล' in locked.inner_text()
 assert page.locator('[data-slot="head"]').first.get_attribute('data-organ')=='fang:8:rare'
 for mode,want in [('rarity','fang:20:epic'),('level','fang:20:epic'),('ready','fang:8:rare')]:
  page.locator('#gearSort').select_option(mode)
  assert page.locator('[data-slot="head"]').first.get_attribute('data-organ')==want
  assert page.evaluate('__gearUI.mu.head')=='fang:1:common'
  assert page.evaluate('JSON.stringify(__gearUI.inv)')==inventory
 page.locator('#gearTitle').scroll_into_view_if_needed();page.screenshot(path=str(artifacts/'equipment-comparison.png'))
 page.locator('[data-organ="helm:1:common"]').click()
 assert page.evaluate('__gearUI.dmgMul')==1
 assert abs(page.evaluate('__gearUI.dmgTaken')-.92)<1e-8
 assert 'ดาเมจที่รับ -8%' in page.locator('#gearBonuses').inner_text()
 page.locator('[data-remove="head"]').click()
 assert page.evaluate('__gearUI.mu.head') is None
 assert page.evaluate('__gearUI.dmgTaken')==1
 assert page.evaluate('JSON.stringify(__gearUI.inv)')==inventory
 page.locator('[data-organ="helm:1:common"]').click()
 load();assert page.evaluate('__gearUI.mu.head')=='helm:1:common'
 assert page.evaluate('JSON.stringify(__gearUI.inv)')==inventory
 assert not errors,errors
 print('PASS: mobile equipment comparison, tradeoffs, damage reduction signs, level reasons, all sort modes, nonmutating inventory, equip/unequip/reload; no console errors')
 browser.close()
server.shutdown()
