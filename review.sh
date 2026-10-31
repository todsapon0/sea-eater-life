#!/usr/bin/env bash
# ตรวจงานเร็ว-ประหยัดโควต้า: รันทุกอย่างอัตโนมัติ แล้วอ่านแค่รายงานสั้นๆ ไฟล์เดียว
# ใช้: ./review.sh [commit-ฐาน]   (ค่าเริ่มต้น = origin/claude/family-build~5)  ต้องตั้ง THREE_JS_PATH (three@0.128.0)
cd "$(dirname "$0")" || exit 1
BASE=${1:-origin/claude/family-build~5}; OUT=${REVIEW_OUT:-/tmp/review-report.txt}; TMP=$(mktemp -d); : >"$OUT"
[ -f "${THREE_JS_PATH:-}" ] || { echo "ตั้ง THREE_JS_PATH ก่อน (three@0.128.0 จาก npm)"; exit 2; }
say(){ echo "$*" | tee -a "$OUT"; }
say "== รายงานตรวจ $(date -u +%FT%TZ) ฐาน=$BASE HEAD=$(git rev-parse --short HEAD) =="
# 1) เปลี่ยนอะไรบ้าง (สั้น)
say "-- ไฟล์ที่เปลี่ยน"; git diff --stat "$BASE" HEAD -- . ':!HANDOFF.md' | tail -12 | tee -a "$OUT"
# 2) ไวยากรณ์สคริปต์ในเกม
python3 - "$TMP" <<'PY'
import re,sys;s=open('index.html',encoding='utf-8').read();m=re.findall(r'<script>(.*?)</script>',s,re.S);open(sys.argv[1]+'/g.js','w').write(max(m,key=len))
PY
node --check "$TMP/g.js" 2>"$TMP/syn" && say "PASS syntax index.html" || { say "FAIL syntax index.html"; head -3 "$TMP/syn"|tee -a "$OUT"; }
# 3) ชนกับล็อกของอีกฝ่ายหรือไม่ (ดูบรรทัด 🔒)
say "-- ล็อกที่ค้างใน HANDOFF.md"; grep -nE "🔒 กำลังทำ: (Claude|Codex|โค) เริ่ม" HANDOFF.md | cut -c1-150 | tee -a "$OUT"
# 4) เทสต์ทั้งหมด (node ต่อเนื่อง, python ขนาน 3 ตัว)
for t in test-*.cjs; do if timeout 120 node "$t" >"$TMP/$t.log" 2>&1; then say "PASS $t"; else say "FAIL $t: $(tail -2 "$TMP/$t.log"|tr '\n' ' '|cut -c1-200)"; fi; done
mkpy(){ sed "s#executable_path='/usr/bin/chromium',##;s#executable_path=\"/usr/bin/chromium\",##" "$1" > ".rv_$1"; }
runpy(){ t=$1; mkpy "$t"; if timeout 600 python3 ".rv_$t" >"$TMP/$t.log" 2>&1; then echo "PASS $t" >"$TMP/$t.res"; else echo "FAIL $t: $(tail -2 "$TMP/$t.log"|tr '\n' ' '|cut -c1-200)" >"$TMP/$t.res"; fi; rm -f ".rv_$t"; }
export -f runpy mkpy; export TMP
ls test-*.py | xargs -P 3 -I{} bash -c 'runpy {}'
cat "$TMP"/*.res | sort | tee -a "$OUT"
# 5) ผลสรุป
F=$(grep -c "^FAIL" "$OUT"); P=$(grep -c "^PASS" "$OUT")
say "== สรุป: ผ่าน $P ล้มเหลว $F (รายละเอียด log: $TMP) =="; rm -f .rv_*.py; [ "$F" = 0 ]
