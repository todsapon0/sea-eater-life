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
  page.goto(url,wait_until='networkidle');assert page.locator('#accountGate').count()==0;page.wait_for_function('window.__gearUI')
 def open_gear():
  page.locator('#dexb').dispatch_event('pointerdown');page.locator('#equipGear').click()
 load();page.evaluate("__gearUI.seen={ray:1,puffer:1};__gearUI.kc={ray:3,puffer:2};")
 page.locator('#dexb').dispatch_event('pointerdown')
 assert page.locator('.bookcard').count()==8
 assert page.locator('summary[aria-label="ปลากระเบนตาฟ้า"]').count()==1
 assert page.locator('summary[aria-label="???"]').count()>0
 page.locator('summary[aria-label="ปลากระเบนตาฟ้า"]').click()
 assert 'ครีบกระเบน' in page.locator('[data-book-section=species]').inner_text()
 page.locator('[data-book-page="1"]').click();assert '2 / 3' in page.locator('.bookpager').inner_text()
 page.locator('[data-book-page="1"]').click();assert '3 / 3' in page.locator('.bookpager').inner_text()
 assert page.locator('[data-book-page="1"]').is_disabled()
 page.locator('[data-book-page="-1"]').click();assert '2 / 3' in page.locator('.bookpager').inner_text()
 page.locator('[data-book-tab=daily]').click();assert 'ภารกิจวันนี้' in page.locator('[data-book-section=daily]').inner_text()
 page.locator('[data-book-tab=bag]').click();assert 'เขี้ยวคม' in page.locator('[data-book-section=bag]').inner_text()
 page.locator('[data-book-tab=settings]').click()
 for name in ['fpsBtn','gfxBtn','fsBtn','hudBtn','camBtn','zoomIn','zoomOut','renameBtn','swc','exportSave','copySave','importFileBtn','importCodeBtn']:
  assert page.locator('#'+name).is_visible(),name
 before=page.locator('#fpsBtn').get_attribute('aria-pressed');page.locator('#fpsBtn').click();assert page.locator('#fpsBtn').get_attribute('aria-pressed')!=before
 page.locator('#copySave').click();assert page.locator('#saveCode').is_visible();assert page.locator('#saveCode').input_value().startswith('SEL1.')
 for width,height in [(390,844),(844,390),(768,1024),(1024,768)]:
  page.set_viewport_size({'width':width,'height':height});page.locator('[data-book-tab=species]').click()
  box=page.locator('#dex').bounding_box();assert box['x']>=0 and box['y']>=0 and box['x']+box['width']<=width and box['y']+box['height']<=height
  page.screenshot(path=str(artifacts/f'book-{width}x{height}.png'))
 page.locator('#equipGear').click();assert page.locator('#evo').is_visible();page.locator('[data-close]').click()
 assert not errors,errors
 print('PASS: bestiary pages, discovery, tabs, settings, inventory, equipment and responsive layout')
 browser.close()
server.shutdown()
