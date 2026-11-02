import http.server,json,os,threading
from pathlib import Path
from playwright.sync_api import sync_playwright
os.chdir(os.path.dirname(os.path.abspath(__file__)))
class H(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*a):pass
sv=http.server.ThreadingHTTPServer(('127.0.0.1',0),H);threading.Thread(target=sv.serve_forever,daemon=True).start()
base=f'http://127.0.0.1:{sv.server_port}/'
html=Path('index.html').read_text().replace('loop();\n}','window.__t={P,sea,kill,mons,updateGoal,tutNext};loop();\n}')
def run(init,fn):
 with sync_playwright() as p:
  b=p.chromium.launch(args=['--no-sandbox','--enable-unsafe-swiftshader']);ctx=b.new_context(viewport={'width':844,'height':390});pg=ctx.new_page();errs=[]
  pg.on('pageerror',lambda e:errs.append(str(e)))
  def route(r):
   u=r.request.url
   if 'three.min.js' in u:r.fulfill(path=os.environ['THREE_JS_PATH'],content_type='application/javascript')
   elif 'cdn.jsdelivr.net' in u:r.fulfill(body='',content_type='application/javascript')
   elif u.split('?')[0]==base:r.fulfill(body=html,content_type='text/html')
   else:r.continue_()
  ctx.route('**/*',route);pg.add_init_script(init)
  pg.goto(base,wait_until='networkidle');pg.wait_for_timeout(1000)
  out=fn(pg);assert not errs,errs[:2];b.close();return out
goal="()=>{__t.updateGoal(1);return document.getElementById('gtx').textContent}"
def new_game(pg):
 r={}
 r['tu0']=pg.evaluate("__t.P.tu");r['t0']=pg.evaluate(goal)
 # moving 4 short steps counts as swimming (>10 units total)
 pg.evaluate("()=>{for(let i=0;i<6;i++){__t.sea.position.x+=3;__t.updateGoal(1);}}");r['tu_after_move']=pg.evaluate("__t.P.tu")
 r['t1']=pg.evaluate(goal)
 pg.evaluate("document.getElementById('bite').dispatchEvent(new PointerEvent('pointerdown',{bubbles:true,cancelable:true}))");r['tu_after_bite']=pg.evaluate("__t.P.tu");r['t2']=pg.evaluate(goal)
 pg.evaluate("__t.kill(__t.mons.find(m=>m.ty.n==='ray'))");r['tu_after_kill']=pg.evaluate("__t.P.tu");r['t3']=pg.evaluate(goal)
 pg.evaluate("document.getElementById('dexb').dispatchEvent(new PointerEvent('pointerdown',{bubbles:true,cancelable:true}))");r['tu_after_book']=pg.evaluate("__t.P.tu");r['t4']=pg.evaluate(goal)
 pg.evaluate("__t.tutNext(4)");r['tu_end']=pg.evaluate("__t.P.tu");r['t5']=pg.evaluate(goal)
 pg.reload(wait_until='networkidle');pg.wait_for_timeout(800);r['after_reload']=pg.evaluate("__t.P.tu")
 return r
r=run("localStorage.selcls='sea';if(!sessionStorage.getItem('fresh')){localStorage.removeItem('sel01');sessionStorage.setItem('fresh','1');}",new_game)
print(json.dumps(r,ensure_ascii=False))
assert r['tu0']==0 and r['t0'].startswith('ฝึก 1/5')
assert r['tu_after_move']==1 and r['t1'].startswith('ฝึก 2/5')
assert r['tu_after_bite']==2 and r['t2'].startswith('ฝึก 3/5')
assert r['tu_after_kill']==3 and r['t3'].startswith('ฝึก 4/5')
assert r['tu_after_book']==4 and r['t4'].startswith('ฝึก 5/5')
assert r['tu_end']==5 and not r['t5'].startswith('ฝึก') and r['after_reload']==5
old=run("localStorage.selcls='sea';localStorage.sel01=JSON.stringify({lv:5,xp:0,q:0,qd:0,inv:{},seen:{ray:1},kc:{ray:3}});",lambda pg:{'tu':pg.evaluate("__t.P.tu"),'g':pg.evaluate(goal)})
print(old)
assert old['tu']==9 and not old['g'].startswith('ฝึก')
print('PASS: tutorial 5 steps advance on move/bite/kill/book/board, persists across reload, old saves skip it')
