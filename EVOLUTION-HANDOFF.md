# PR #11 — Evolution, dropped equipment and touch controls

Continue on `claude/family-build` and the existing PR #11. Do not merge into main
before owner approval of visuals. No keys/reference images in this public repo,
no paid services, no real Supabase writes or provisioning.

## Current approved design (supersedes the original mutation-slot rules)

- Evolution is permanent, similar to a job advancement. It is independent of gear.
  Costs remain 40/140/360 essence at Lv8/14/20; stage 3 requires a valid species job.
  HP +12%, damage +6%, body size +5% per stage; stars/jobs continue to stack.
- All three equipment slots (head/back/tail) are open from the start and initially
  empty. Evolution does not unlock or gate equipment slots.
- Gear must drop into the inventory before equipping. Each item has its own Lv1–20,
  a rarity (common/rare/epic), and requires player level >= item level. Shared and
  species-specific restrictions remain. Equipping/removing is free and retains
  the item in inventory; there is no automatic equip on drop.
- Old free-selection `mu` IDs (e.g. `fang`) no longer count as equipment. On load,
  unsupported/unowned selections are cleared, without granting free items. Keep
  existing evolution, essence, job, stars, materials and other progress.

## Implementation / storage

`index.html` remains the single-file Three.js r128 game. `ORG` contains the 15 base
attachments; `RARITY`, `GEAR_DROPS`, `gearFrom`, `canEquip`, `rollGear`, `awardGear`
implement loot. `organFor` filters ownership, player level, slot and species for
both stats and rendering. `applyJob` resets all multipliers then combines job,
stars, evolution and selected eligible gear. HP increases preserve current health;
reduced max HP clamps health. Bloop heal and Maja whirlpool honor their multipliers.

No new database/schema fields: inventory stacks use `P.inv['eq:fang:8:rare'] = count`
and `P.mu.head = 'fang:8:rare'`. IDs fit the existing <=20-character mu limit; keys
fit the existing inventory limit. Counts cap at 99999. Existing save/export/account
queue code retains the full record. `save-tools.js` validates reserved `eq:` keys,
levels and rarities; old saves without these fields remain valid.

For each stat multiplier, gear = `1 + (base - 1) * (1 + (lv - 1)*0.025) * rarity`;
rarity factors are common 1, rare 1.25, epic 1.5. This strengthens reductions as
well as bonuses. Stats do not stack from repeat calls to applyJob.

Default loot balance (owner has not separately tuned these rates):

| Enemy | Gear Lv | Possible organs (filtered to shared/current species) |
| --- | --- | --- |
| ray | 1–7 | fang, bub, fin |
| shark | 5–12 | helm, jaw, spike |
| eel | 8–16 | horn, crys, rud |
| whale | 12–20 | scale, shell, wing |
| boss | 16–20 | whip, glow, orb |

Normal enemies: 20% equipment drop, rarity common/rare/epic = 75/22/3%.
Boss: guaranteed equipment, rare/epic = 70/30%. Existing material and essence
rewards are retained. The equipment UI shows level, rarity, requirements, counts,
effects and a drop-source guide. Open it via 🧬 or the book's “🎒 สวมอุปกรณ์”.

Visuals preserve base geometry and existing job colors. `buildOrgans` disposes
old attachment geometries/materials. Sea back lowers 0.4 to contact the v2 body;
tail shifts -0.9 Z/+0.25 Y (spikes +0.2 Y); fangs lower 0.35; Bloop bubbles shift
down/forward to clear the eyes. No fourth species model exists in this index.html;
account.js has a pre-existing crab identifier without a matching playable model.

## Larger joystick

`#movezone` owns a generous bottom-left touch area, including near misses of the
circle. It captures only the first movement pointer, resets on release/cancel/
lost capture/blur, and leaves intentional canvas gestures independent. Circle is
144px on phones, 132px on narrow/landscape screens, 160px on larger screens.
Knob 58–64px. Toolbar wraps on narrow screens; existing controls/panels remain.

## Tests / continuation

```
node test-equipment.cjs
node test-save-tools.cjs
node test-account-recovery.cjs
THREE_JS_PATH=/path/to/trusted/three-r128.min.js EVOLUTION_QUICK=1 python3 test-evolution.py
THREE_JS_PATH=/path/to/trusted/three-r128.min.js python3 test-touch-controls.py
```

Python browser tests require installed Playwright and `/usr/bin/chromium` (provided
here). Download Three.js r128 from the existing authoritative CDN with TLS
verification enabled, outside the repo. Tests route it to the local file, stub
the unused SDK, block Supabase project calls and use disposable local saves.
Instrumentation is injected in memory only. Screenshots go to `/tmp/sea-evolution`
or `EVOLUTION_ARTIFACTS`, not git. Omit EVOLUTION_QUICK for all 6 jobs × 4 views.

Equipment Node tests cover empty/open slots at ev0, ownership, item levels, species,
rarity stats, deterministic drops for all organ/enemy combinations and count caps.
Browser regression covers evolution, equipment selection, under-level disabling,
15-organ multiplier checks per species, save/reload, essence, heal/whirlpool and
mobile UI. Touch tests cover 390×844, 844×390, 320×568: near misses, pointer capture,
second-touch ownership, walking+attack, independent camera, cancel and pinch.

Cloud Chromium uses software WebGL; measured low/variable FPS is not proof of 30 FPS
on iPhone/iPad. Owner still needs to approve model visuals and actual-device feel/
performance before merge. Real server/account integration remains untested here.
