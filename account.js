/* Server account mode is opt-in. Legacy saves remain in localStorage. */
window.startAccount = async function startAccount() {
  const root = document.createElement('section');
  root.id = 'accountGate';
  root.innerHTML = '<div class="account-card"><h1>Sea Eater Life</h1><p>บัญชีผู้เล่น</p><p id="accountError" role="alert"></p><form id="accountForm"><label>อีเมล <input id="accountEmail" type="email" autocomplete="username" required></label><label>รหัสผ่าน <input id="accountPassword" type="password" autocomplete="current-password" required></label><button type="submit">เข้าสู่ระบบ</button></form><button id="localPlay" type="button">เล่นแบบในเครื่อง</button><p>เซฟในเครื่องแยกจากเซฟบัญชี และไม่ถูกย้ายอัตโนมัติ</p></div>';
  document.body.append(root);
  const error = root.querySelector('#accountError');
  const form = root.querySelector('#accountForm');
  const local = root.querySelector('#localPlay');
  const cfg = window.SEA_ACCOUNT_CONFIG || {};
  function publicKeyOnly(key) {
    if (!key || /^sb_secret_/i.test(key)) return false;
    if (key.startsWith('sb_publishable_')) return true;
    try {
      const payload = key.split('.')[1].replace(/-/g,'+').replace(/_/g,'/');
      return JSON.parse(atob(payload)).role === 'anon';
    } catch (_) { return false; }
  }
  const remoteConfigured = /^https:\/\/[a-z0-9-]+\.supabase\.co$/i.test(cfg.url || '') && publicKeyOnly(cfg.publishableKey || '');
  if (!remoteConfigured) {
    error.textContent = 'ยังไม่ได้ตั้งค่าเซิร์ฟเวอร์บัญชี กรุณาติดต่อผู้ดูแล';
    form.querySelector('button').disabled = true;
  }
  return new Promise(resolve => {
    local.onclick = () => { root.remove(); resolve({ storage: localStorage, remote: false }); };
    form.onsubmit = async e => {
      e.preventDefault();
      if (!remoteConfigured) return;
      const submit = form.querySelector('button');
      submit.disabled = true; error.textContent = 'กำลังเข้าสู่ระบบ…';
      try {
        if (!window.supabase) throw new Error('โหลดระบบบัญชีไม่สำเร็จ ตรวจอินเทอร์เน็ต');
        const client = window.supabase.createClient(cfg.url, cfg.publishableKey, {auth:{persistSession:false,autoRefreshToken:true}});
        const { data: auth, error: loginError } = await client.auth.signInWithPassword({email:root.querySelector('#accountEmail').value,password:root.querySelector('#accountPassword').value});
        root.querySelector('#accountPassword').value = '';
        if (loginError || !auth.user) throw new Error('เข้าสู่ระบบไม่สำเร็จ ตรวจอีเมลและรหัสผ่าน');
        let {data: row, error: readError} = await client.from('player_characters').select('character_class,save_data,revision').eq('user_id',auth.user.id).maybeSingle();
        if (readError) throw new Error('โหลดเซฟจากเซิร์ฟเวอร์ไม่สำเร็จ');
        if (!row) {
          form.remove(); local.remove(); error.textContent = 'เลือกตัวละครหนึ่งตัวสำหรับบัญชีนี้';
          const select = document.createElement('div');
          for (const [id,label] of [['sea','Sea Eater'],['bloop','Bloop'],['maja','El Gran Maja']]) {
            const b=document.createElement('button'); b.type='button'; b.textContent=label;
            b.onclick=async()=>{
              select.querySelectorAll('button').forEach(x=>x.disabled=true);
              const initial={lv:1,xp:0,qd:0,q:0,inv:{},seen:{}};
              const result=await client.from('player_characters').insert({user_id:auth.user.id,character_class:id,save_data:initial}).select('character_class,save_data,revision').single();
              if(result.error){error.textContent='สร้างตัวละครไม่สำเร็จ โปรดเข้าสู่ระบบใหม่เพื่อตรวจเซฟ';return;}
              finish(client,auth.user.id,result.data);
            };
            select.append(b);
          }
          root.querySelector('.account-card').append(select); return;
        }
        finish(client,auth.user.id,row);
      } catch (err) { error.textContent=err.message || 'เชื่อมต่อไม่สำเร็จ'; submit.disabled=false; }
    };
    function finish(client,userId,row) {
      const record=row.save_data;
      const object=value=>value && typeof value==='object' && !Array.isArray(value);
      if (!['sea','bloop','maja'].includes(row.character_class) || !object(record) ||
          !Number.isInteger(record.lv) || record.lv<1 || record.lv>20 ||
          !Number.isFinite(record.xp) || record.xp<0 || !Number.isInteger(record.qd) ||
          record.qd<0 || record.qd>2 || !Number.isInteger(record.q) || record.q<0 ||
          record.q >= [5,10,20][record.qd] || !object(record.inv) || !object(record.seen) ||
          !Number.isInteger(row.revision) || row.revision<0) {
        error.textContent='ข้อมูลเซฟบนเซิร์ฟเวอร์ไม่ถูกต้อง กรุณาติดต่อผู้ดูแล'; return;
      }
      const key={sea:'sel01',bloop:'sel01b',maja:'sel01m'}[row.character_class];
      let revision=row.revision, pending=null, saving=false, blocked=false;
      let current=JSON.stringify(row.save_data);
      const status=document.createElement('div'); status.id='accountStatus'; status.textContent='เซฟบัญชี: โหลดแล้ว'; document.body.append(status);
      const storage={
        getItem(k){if(k==='selcls')return row.character_class;if(k===key)return current;return null;},
        setItem(k,value){if(k!==key || blocked)return;current=String(value);pending=current;status.textContent='เซฟบัญชี: รอบันทึก';queueMicrotask(flush);},
        removeItem(){throw new Error('บัญชีมีตัวละครเดียว');}
      };
      async function flush(){
        if(saving || blocked || pending===null)return;
        saving=true; const snapshot=pending;pending=null;
        status.textContent='เซฟบัญชี: กำลังบันทึก';
        try {
          const result=await client.from('player_characters').update({save_data:JSON.parse(snapshot),revision:revision+1}).eq('user_id',userId).eq('revision',revision).select('revision').maybeSingle();
          if(result.error)throw new Error('เชื่อมต่อเซิร์ฟเวอร์ไม่ได้');
          if(!result.data)throw new Error('เซฟเปลี่ยนจากอีกเครื่อง กรุณาหยุดเล่นและติดต่อผู้ดูแล');
          revision=result.data.revision;status.textContent='เซฟบัญชี: บันทึกแล้ว';
        } catch(err) {
          blocked=true;pending=pending||snapshot;status.textContent='เซฟไม่สำเร็จ: '+err.message;
          status.classList.add('error');
          const warning=document.createElement('div');warning.className='account-block';warning.textContent='หยุดเล่น: '+err.message+' ความคืบหน้ารอบนี้ยังไม่ได้บันทึกบนเซิร์ฟเวอร์';document.body.append(warning);
        } finally {saving=false;if(!blocked && pending!==null)flush();}
      }
      root.remove(); resolve({storage,remote:true});
    }
  });
};

