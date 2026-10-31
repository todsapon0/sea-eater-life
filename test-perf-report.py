"""Performance report opt-in, clipboard and fallback in a real browser."""
import os, threading, http.server
from pathlib import Path
from playwright.sync_api import sync_playwright
os.chdir(Path(__file__).resolve().parent)
class H(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*args): pass
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),H);threading.Thread(target=server.serve_forever,daemon=True).start()
url=f'http://127.0.0.1:{server.server_port}/'
html=Path('index.html').read_text().replace('loop();\n}', 'window.__perfTest={setMap,perfReport};loop();\n}')
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--enable-unsafe-swiftshader'])
 ctx=browser.new_context(viewport={'width':390,'height':844});page=ctx.new_page();page.set_default_timeout(120000);errors=[];outbound=[]
 page.on('pageerror',lambda e:errors.append(str(e)))
 def route(r):
  u=r.request.url
  if 'three.min.js' in u:r.fulfill(path=os.environ['THREE_JS_PATH'],content_type='application/javascript')
  elif 'cdn.jsdelivr.net' in u:r.fulfill(body='',content_type='application/javascript')
  elif u.split('?')[0]==url:r.fulfill(body=html,content_type='text/html')
  elif u.startswith(url):r.continue_()
  else:outbound.append(u);r.abort()
 ctx.route('**/*',route)
 page.add_init_script("""localStorage.selcls='sea';localStorage.pname_sea='PRIVATE PLAYER';window.copyFail=true;window.copied='';Object.defineProperty(navigator,'clipboard',{value:{writeText(t){if(window.copyFail)return Promise.reject(Error('denied'));window.copied=t;return Promise.resolve();}}});""")
 page.goto(url,wait_until='networkidle');page.wait_for_function('window.__perfTest');page.locator('#dexb').dispatch_event('pointerdown');page.locator('[data-book-tab=settings]').click()
 assert page.locator('#perfToggle').get_attribute('aria-pressed')=='false'
 page.locator('#perfCopy').click();page.wait_for_selector('#perfReportText:visible');assert 'ยังไม่มีข้อมูล' in page.locator('#perfReportText').input_value()
 page.locator('#perfToggle').click();assert page.locator('#perfToggle').get_attribute('aria-pressed')=='true'
 page.wait_for_timeout(2300);page.evaluate('__perfTest.setMap(1)');page.wait_for_timeout(2300)
 page.evaluate('window.copyFail=false');page.locator('#perfCopy').click();page.wait_for_function('window.copied.length>0');report=page.evaluate('window.copied')
 for term in ['เมืองริมหาด','หาดตื้น','FPS เฉลี่ย','calls','triangles','เปลี่ยนแมพ','ภาพแรก','มอนสเตอร์ทั้งหมด']:
  assert term in report,(term,report)
 assert 'PRIVATE PLAYER' not in report and not outbound and not errors,(outbound,errors,report)
 page.locator('#perfToggle').click();assert page.locator('#perfToggle').get_attribute('aria-pressed')=='false'
 page.evaluate('window.copyFail=true');page.locator('#perfCopy').click();page.wait_for_function("document.querySelector('#perfReportText').value.includes('หาดตื้น')")
 page.screenshot(path='/tmp/sea-evolution/perf-report-book.png');page.set_viewport_size({'width':844,'height':390});page.screenshot(path='/tmp/sea-evolution/perf-report-landscape.png');browser.close()
print('PASS: opt-in report across maps, clipboard success and fallback, no player name or external requests')
server.shutdown()
