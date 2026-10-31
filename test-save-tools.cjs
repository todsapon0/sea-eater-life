// Run: node test-save-tools.cjs   (no network, no browser)
const assert = require('assert');
const fs = require('fs');
const tools = require('./save-tools.js');

const mem = (init = {}) => {
  const d = { ...init };
  return { d, getItem: k => (k in d ? d[k] : null), setItem: (k, v) => { d[k] = String(v); }, removeItem: k => { delete d[k]; } };
};
const rec = (lv, extra = {}) => ({ lv, xp: 12, qd: 1, q: 3, inv: { 'ครีบกระเบน': 2 }, seen: { ray: 1 }, ...extra });
const backup = (chars, sel) => ({ format: 'sea-eater-save', version: 1, exportedAt: 'x', source: { gameVersion: 'v0.5.3' }, characters: chars, ...(sel ? { selectedClass: sel } : {}) });
const throwsMsg = (fn, part) => { try { fn(); } catch (e) { assert(String(e.message).includes(part), 'expected "' + part + '" in "' + e.message + '"'); return; } assert.fail('should throw: ' + part); };

// 1) The backup the existing Export button writes must be importable (compat).
const html = fs.readFileSync('index.html', 'utf8');
const m = html.match(/function makeSaveBackup\([\s\S]*?\n\}\nfunction exportSaveBackup/);
assert(m, 'makeSaveBackup not found in index.html');
const gv = html.match(/const GAME_VERSION='([^']+)'/);
assert(gv, 'GAME_VERSION not found in index.html');
const makeSaveBackup = new Function('GAME_VERSION', m[0].replace(/\nfunction exportSaveBackup$/, '') + '; return makeSaveBackup;')(gv[1]);
const src = mem({ selcls: 'bloop', sel01: JSON.stringify(rec(4)), sel01b: JSON.stringify(rec(7)) });
const exported = makeSaveBackup(src, 'https://example.test', '2026-10-30T00:00:00Z');
const parsed = tools.parseBackup(JSON.stringify(exported));
assert.strictEqual(parsed.characters.bloop.lv, 7);

// 2) Save code round trip, including Thai item names; tolerant of whitespace/line breaks.
const code = tools.encodeCode(parsed);
assert(code.startsWith('SEL1.'));
assert(!/[+/=\s]/.test(code), 'code must be copy/paste safe');
assert.deepStrictEqual(tools.decodeCode(code), parsed);
assert.deepStrictEqual(tools.decodeCode('  ' + code.slice(0, 20) + '\n' + code.slice(20) + '  '), parsed);
assert.deepStrictEqual(tools.decodeCode(JSON.stringify(exported)), parsed); // raw JSON pasted into the code box also works

// 3) Rejects bad input with a Thai message and never returns partial data.
throwsMsg(() => tools.decodeCode(''), 'ไม่มีรหัส');
throwsMsg(() => tools.decodeCode('hello'), 'SEL1.');
throwsMsg(() => tools.decodeCode('SEL1.@@@'), 'รหัสเซฟไม่ถูกต้อง');
throwsMsg(() => tools.parseBackup('{not json'), 'JSON');
throwsMsg(() => tools.parseBackup(JSON.stringify({ format: 'other', version: 1, characters: {} })), 'ไม่ใช่ไฟล์เซฟ');
throwsMsg(() => tools.parseBackup(JSON.stringify(backup({ sea: rec(99) }))), 'เลเวล');
throwsMsg(() => tools.parseBackup(JSON.stringify(backup({ sea: rec(0) }))), 'เลเวล');
throwsMsg(() => tools.parseBackup(JSON.stringify(backup({ sea: rec(3, { xp: -5 }) }))), 'EXP');
throwsMsg(() => tools.parseBackup(JSON.stringify(backup({ sea: rec(3, { qd: 9 }) }))), 'เควสต์');
throwsMsg(() => tools.parseBackup(JSON.stringify(backup({ sea: rec(3, { inv: { x: -1 } }) }))), 'inv');
throwsMsg(() => tools.parseBackup(JSON.stringify(backup({ dragon: rec(3) }))), 'ไม่รู้จัก');
throwsMsg(() => tools.parseBackup(JSON.stringify(backup({ sea: rec(3) }, 'maja'))), 'ตัวละครที่เลือก');
throwsMsg(() => tools.parseBackup(JSON.stringify({ ...backup({ sea: rec(3) }), version: 2 })), 'เวอร์ชัน');
throwsMsg(() => tools.parseBackup('x'.repeat(200001)), 'ใหญ่เกินไป');

// 4) Plan + apply: only characters in the file are overwritten; others stay; selcls follows the file.
const dst = mem({ selcls: 'sea', sel01: JSON.stringify(rec(2)), sel01m: JSON.stringify(rec(9)) });
const plan = tools.planImport(tools.parseBackup(JSON.stringify(backup({ sea: rec(5), bloop: rec(6) }, 'bloop'))), dst);
assert.deepStrictEqual(plan.lines, ['Sea Eater: Lv.5 (เขียนทับ Lv.2)', 'Bloop: Lv.6 (ไม่มีเซฟเดิม)']);
assert.strictEqual(JSON.parse(dst.d.sel01).lv, 2, 'planning must not write');
tools.applyImport(dst, plan);
assert.strictEqual(JSON.parse(dst.d.sel01).lv, 5);
assert.strictEqual(JSON.parse(dst.d.sel01b).lv, 6);
assert.strictEqual(JSON.parse(dst.d.sel01m).lv, 9, 'maja not in file -> untouched');
assert.strictEqual(dst.d.selcls, 'bloop');

// 5) Without selectedClass, keep the player's current class if valid.
const dst2 = mem({ selcls: 'maja', sel01m: JSON.stringify(rec(9)) });
assert.strictEqual(tools.planImport(tools.parseBackup(JSON.stringify(backup({ sea: rec(5) }))), dst2).selcls, 'maja');
assert.strictEqual(tools.planImport(tools.parseBackup(JSON.stringify(backup({ sea: rec(5) }))), mem()).selcls, 'sea');

// 6) A failing write rolls everything back (e.g. iOS private mode / storage full).
const orig = { selcls: 'sea', sel01: JSON.stringify(rec(2)) };
const flaky = mem(orig); let n = 0; const realSet = flaky.setItem;
flaky.setItem = (k, v) => { if (++n === 2) throw new Error('QuotaExceeded'); realSet(k, v); };
const plan3 = tools.planImport(tools.parseBackup(JSON.stringify(backup({ sea: rec(5), bloop: rec(6) }))), flaky);
throwsMsg(() => tools.applyImport(flaky, plan3), 'คืนให้แล้ว');
flaky.setItem = realSet;
assert.deepStrictEqual(flaky.d, orig, 'storage must be exactly as before the failed import');


// 7) New optional fields (daily quests, kill counts, job) validate and round-trip; old saves without them still pass.
const dly = { d: '2026-10-30', last: '2026-10-30', s: 3, k: [1, 0, 2], f: [0, 0, 0], b: 0, qs: [{ e: 'kill:any', n: 12 }, { e: 'skill', n: 10 }, { e: 'zone:1', n: 1 }] };
const rich = rec(7, { kc: { ray: 12, boss: 1 }, dly, job: 'guardian' });
const parsedRich = tools.parseBackup(JSON.stringify(backup({ sea: rich })));
assert.deepStrictEqual(parsedRich.characters.sea.dly, dly);
assert.deepStrictEqual(tools.decodeCode(tools.encodeCode(parsedRich)).characters.sea.kc, { ray: 12, boss: 1 });
tools.parseBackup(JSON.stringify(backup({ sea: rec(7) })));
throwsMsg(() => tools.parseBackup(JSON.stringify(backup({ sea: rec(7, { kc: { ray: -1 } }) }))), 'สถิติ');
throwsMsg(() => tools.parseBackup(JSON.stringify(backup({ sea: rec(7, { job: 5 }) }))), 'อาชีพ');
throwsMsg(() => tools.parseBackup(JSON.stringify(backup({ sea: rec(7, { dly: { ...dly, k: [1, 2] } }) }))), 'ภารกิจรายวัน');

console.log('PASS: save-tools (compat with existing export, code round trip, validation, plan/apply, rollback)');

// Optional evolution fields preserve old saves and reject malformed records.
assert.doesNotThrow(() => tools.parseBackup(JSON.stringify(backup({sea:rec(1)}))));
for (const extra of [{ev:0,es:0,mu:{}},{ev:3,es:1e7,mu:{head:'fang',back:'scale',tail:'whip'}}]) {
 const b=backup({sea:rec(20,extra)});
 assert.deepStrictEqual(tools.decodeCode(tools.encodeCode(b)),b);
}
for (const extra of [{ev:-1},{ev:4},{ev:1.5},{ev:'1'},{ev:null},{es:-1},{es:1e7+1},{es:1.1},{es:'1'},{es:null},{mu:[]},{mu:null},{mu:'fang'},{mu:{leg:'fang'}},{mu:{head:1}},{mu:{tail:'x'.repeat(21)}},{mu:JSON.parse('{"__proto__":"fang"}')}]) {
 assert.throws(()=>tools.parseBackup(JSON.stringify(backup({sea:rec(20,extra)}))));
}
console.log('PASS: evolution save boundaries, legacy compatibility and mutation validation');

const equipmentSave=backup({sea:rec(20,{ev:0,mu:{head:'fang:8:rare',tail:'whip:20:epic'},inv:{'eq:fang:8:rare':2,'eq:whip:20:epic':1}})});
assert.deepStrictEqual(tools.decodeCode(tools.encodeCode(equipmentSave)),equipmentSave);
for(const key of ['eq:fang:0:common','eq:fang:21:rare','eq:fang:1:fake','eq:unknown:1:common'])assert.throws(()=>tools.parseBackup(JSON.stringify(backup({sea:rec(1,{inv:{[key]:1}})}))));
console.log('PASS: equipment level/rarity stacks and equipped IDs survive backup round trip; invalid equipment rejected');

const newMonsterSave=backup({sea:rec(20,{mu:{head:'crest:10:epic',back:'spine:8:rare',tail:'lance:18:rare'},inv:{'eq:crest:10:epic':1,'eq:spine:8:rare':1,'eq:lance:18:rare':1,'หนามตะไคร่':2,'เปลือกผลึก':1},kc:{puffer:2,shrimp:1},seen:{puffer:1,shrimp:1}})});
assert.deepStrictEqual(tools.decodeCode(tools.encodeCode(newMonsterSave)),newMonsterSave);
console.log('PASS: new monster discovery, kills, materials and equipment save round trip');
