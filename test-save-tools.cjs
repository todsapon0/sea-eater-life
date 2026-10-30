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
const makeSaveBackup = new Function(m[0].replace(/\nfunction exportSaveBackup$/, '') + '; return makeSaveBackup;')();
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

console.log('PASS: save-tools (compat with existing export, code round trip, validation, plan/apply, rollback)');
