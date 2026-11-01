"""Daily wave arena regression. Needs THREE_JS_PATH (three@0.128.0) and Playwright chromium."""
import os,threading,http.server
from pathlib import Path
from playwright.sync_api import sync_playwright
os.chdir(Path(__file__).resolve().parent)
class H(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*a):pass
sv=http.server.ThreadingHTTPServer(('127.0.0.1',0),H);threading.Thread(target=sv.serve_forever,daemon=True).start()
base=f'http://127.0.0.1:{sv.server_port}/'
html=Path('index.html').read_text().replace('loop();\n}','window.__t={P,openNpc,sea,mons,game,updateArena,enterArena,getArena:()=>arena,getMap:()=>curMap,todayStr};loop();\n}')
with sync_playwright() as p:
 b=p.chromium.launch(args=['--no-sandbox','--enable-unsafe-swiftshader']);ctx=b.new_context(viewport={'width':844,'height':390});pg=ctx.new_page();pg.set_default_timeout(90000);errs=[]
 pg.on('pageerror',lambda e:errs.append(str(e)));pg.on('console',lambda m:errs.append(m.text) if m.type=='error' else None)
 def route(r):
  u=r.request.url
  if 'three.min.js' in u:r.fulfill(path=os.environ['THREE_JS_PATH'],content_type='application/javascript')
  elif 'cdn.jsdelivr.net' in u:r.fulfill(body='',content_type='application/javascript')
  elif u.split('?')[0]==base:r.fulfill(body=html,content_type='text/html')
  else:r.continue_()
 ctx.route('**/*',route)
 pg.add_init_script("localStorage.selcls='sea';if(!localStorage.seeded){localStorage.seeded='1';localStorage.sel01=JSON.stringify({lv:10,xp:0,q:0,qd:0,inv:{},seen:{}});}")
 pg.goto(base+'?debug=1',wait_until='networkidle');pg.wait_for_function('window.__t')
 alive="__t.mons.filter(m=>m.map===14&&m.dead<=0&&m.g.visible).length"
 pg.evaluate("__t.openNpc('board')");assert pg.locator('[data-arena]:not([disabled])').count()==1
 pg.locator('[data-arena]').click()
 assert pg.evaluate("__t.getMap()")==14 and pg.evaluate("__t.P.ar")==pg.evaluate("__t.todayStr()")
 assert pg.evaluate(alive)==0,'arena starts dormant'
 for wave,n in enumerate([3,4,5,6,8],1):
  pg.evaluate("__t.updateArena(5)")  # countdown -> spawn wave
  assert pg.evaluate(alive)==n,(wave,pg.evaluate(alive))
  pg.evaluate("__t.mons.filter(m=>m.map===14&&m.dead<=0).forEach(m=>{m.dead=.01;m.g.visible=false;m.bar.visible=false})")
  pg.evaluate("__t.game(.05)")  # arena monsters must NOT auto-respawn
  assert pg.evaluate("__t.mons.filter(m=>m.map===14&&m.dead>0&&m.dead<1e8).length")==0
  assert pg.evaluate(alive)==0,'dormant after death'
  pg.evaluate("__t.updateArena(.1)")  # clear check
  assert pg.evaluate("__t.getArena().wave")==wave
 pearls=pg.evaluate("__t.P.inv['ไข่มุกทะเล']||0");assert pearls>=5,pearls
 pg.evaluate("__t.updateArena(6)")  # exit timer -> back to town
 assert pg.evaluate("__t.getMap()")==0 and pg.evaluate("__t.getArena()")is None
 pg.evaluate("__t.openNpc('board')");assert pg.locator('[data-arena][disabled]').count()==1,'one run per day'
 pg.reload(wait_until='networkidle');pg.wait_for_function('window.__t')
 assert pg.evaluate("__t.P.ar")==pg.evaluate("__t.todayStr()")
 pg.evaluate("__t.openNpc('board')");assert pg.locator('[data-arena][disabled]').count()==1
 assert not errs,errs
 print('PASS: arena entry from board, 5 waves (3/4/5/6/8), dormant between waves, no auto respawn, rewards, exits to town, once per day, persists after reload')
