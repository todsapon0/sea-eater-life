"""Map treasures: legacy saves, interaction, map markers and one-time rewards."""
import os,threading,http.server
from pathlib import Path
from playwright.sync_api import sync_playwright
os.chdir(Path(__file__).resolve().parent)
class H(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*a):pass
sv=http.server.ThreadingHTTPServer(('127.0.0.1',0),H);threading.Thread(target=sv.serve_forever,daemon=True).start()
url=f'http://127.0.0.1:{sv.server_port}/?debug=1'
html=Path('index.html').read_text().replace('loop();\n}','window.__tr={P,TREASURES,sea,setMap,updateTreasure,claimTreasure,drawMap,updateMini};grace=999;loop();\n}')
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--enable-unsafe-swiftshader']);ctx=browser.new_context(viewport={'width':390,'height':844});pg=ctx.new_page();pg.set_default_timeout(120000);errs=[]
 pg.on('pageerror',lambda e:errs.append(str(e)))
 def route(r):
  u=r.request.url
  if 'three.min.js' in u:r.fulfill(path=os.environ['THREE_JS_PATH'],content_type='application/javascript')
  elif 'cdn.jsdelivr.net' in u:r.fulfill(body='',content_type='application/javascript')
  elif u.split('?')[0]==url.split('?')[0]:r.fulfill(body=html,content_type='text/html')
  else:r.continue_()
 ctx.route('**/*',route)
 pg.add_init_script("""if(!localStorage.seeded){localStorage.seeded='1';localStorage.selcls='sea';localStorage.sel01=JSON.stringify({lv:2,xp:0,q:0,qd:0,inv:{},seen:{}});}window.mapLabels=[];const orig=CanvasRenderingContext2D.prototype.fillText;CanvasRenderingContext2D.prototype.fillText=function(t,...args){if(this.canvas.id==='mapcv')window.mapLabels.push(t);return orig.call(this,t,...args);};window.miniColors=[];const ofill=CanvasRenderingContext2D.prototype.fill;CanvasRenderingContext2D.prototype.fill=function(...args){if(this.canvas.id==='minimap')window.miniColors.push(this.fillStyle);return ofill.apply(this,args);};""")
 pg.goto(url,wait_until='networkidle');pg.wait_for_function('window.__tr');assert pg.evaluate('__tr.P.tr.length')==0
 assert pg.evaluate('__tr.TREASURES.length')==26
 assert pg.evaluate("__tr.claimTreasure(__tr.TREASURES.find(t=>t.id==='c1'))")==False
 pg.evaluate("__tr.setMap(1);const t=__tr.TREASURES.find(x=>x.id==='c1');__tr.sea.position.set(t.x+2.8,0,t.z);__tr.updateTreasure();")
 def check_button():
  a=pg.locator('#treasurebtn').bounding_box();assert a and a['x']>=0 and a['y']>=0 and a['x']+a['width']<=pg.viewport_size['width'] and a['y']+a['height']<=pg.viewport_size['height'],a
  for ident in ['bite','slam','devour','taunt','shield','stick']:
   b=pg.locator('#'+ident).bounding_box()
   if b:assert a['x']+a['width']<=b['x'] or b['x']+b['width']<=a['x'] or a['y']+a['height']<=b['y'] or b['y']+b['height']<=a['y'],(ident,a,b)
 pg.wait_for_selector('#treasurebtn:visible');pg.wait_for_timeout(1200);pg.evaluate('window.miniColors=[];__tr.updateMini(1)');assert '#ffdf48' in pg.evaluate('window.miniColors') and '#f5e6ff' in pg.evaluate('window.miniColors');check_button();pg.screenshot(path='/tmp/sea-evolution/treasure-portrait.png')
 pg.locator('#mapb').click();pg.wait_for_selector('#mapcv');pg.evaluate('window.mapLabels=[];__tr.drawMap()');labels=pg.evaluate('window.mapLabels');assert '💰' in labels and '🦪' in labels,labels
 pg.locator('[data-mclose]').click();pg.locator('#treasurebtn').dispatch_event('pointerdown');assert pg.evaluate("__tr.P.tr.includes('c1')")
 pearls_before=pg.evaluate("__tr.P.inv['ไข่มุกทะเล']||0")
 pg.evaluate("__tr.setMap(1);const t=__tr.TREASURES.find(x=>x.id==='p1');__tr.sea.position.set(t.x+2.8,0,t.z);__tr.updateTreasure();")
 for w,h in [(768,1024),(1024,768),(320,568),(844,390)]:
  pg.set_viewport_size({'width':w,'height':h});pg.wait_for_timeout(500);check_button()
 pg.screenshot(path='/tmp/sea-evolution/treasure-landscape.png');pg.locator('#treasurebtn').dispatch_event('pointerdown')
 assert pg.evaluate("__tr.P.inv['ไข่มุกทะเล']")==pearls_before+1
 assert not pg.evaluate("__tr.claimTreasure(__tr.TREASURES.find(t=>t.id==='p1'))")
 pg.reload(wait_until='networkidle');pg.wait_for_function('window.__tr');assert pg.evaluate("__tr.P.tr.includes('c1')&&__tr.P.tr.includes('p1')") and pg.evaluate("__tr.P.inv['ไข่มุกทะเล']")==pearls_before+1
 pg.evaluate('__tr.setMap(1);window.miniColors=[];__tr.updateMini(1)');assert '#ffdf48' not in pg.evaluate('window.miniColors') and '#f5e6ff' not in pg.evaluate('window.miniColors');pg.locator('#mapb').click();pg.wait_for_selector('#mapcv');pg.evaluate('window.mapLabels=[];__tr.drawMap()');labels=pg.evaluate('window.mapLabels');assert '💰' not in labels and '🦪' not in labels,labels
 assert not errs,errs;browser.close()
print('PASS: 26 treasures, legacy save, range checks, map icons, one-time rewards and reload')
sv.shutdown()
