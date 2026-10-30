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

`index.html` remains the single-file Three.js r128 game. `ORG` contains the 18 base
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
| puffer | 4–10 | crest, spine, bub |
| shrimp | 12–20 | lance, crys, rud |

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
18-organ multiplier checks per species, save/reload, essence, heal/whirlpool and
mobile UI. Touch tests cover 390×844, 844×390, 320×568: near misses, pointer capture,
second-touch ownership, walking+attack, independent camera, cancel and pinch.

Cloud Chromium uses software WebGL; measured low/variable FPS is not proof of 30 FPS
on iPhone/iPad. Owner still needs to approve model visuals and actual-device feel/
performance before merge. Real server/account integration remains untested here.

## Equipment usability follow-up

The equipment panel now shows combined equipment-only bonuses (not job/evolution
bonuses), requirements including levels still missing, and stat changes relative
to the currently equipped item. Comparisons use `(candidate/current - 1)*100`,
including stats lost on a swap. Incoming damage reduction is better when negative;
other stat gains are better when positive. A tradeoff is not labelled universally
better and nothing is equipped automatically.

Sort choices: usable first (default), item level descending, rarity descending.
Sorting copies the list, does not alter saved inventory/equipment, and keeps panel
scroll position. The selected sort is a session-only UI preference. Helpers
`gearRequirement`, `gearChanges`, `equipmentBonuses`, `sortGear` are covered in
`test-equipment.cjs`. The 390px browser regression is:

```
THREE_JS_PATH=/path/to/trusted/three-r128.min.js python3 test-gear-ui.py
```

It checks comparison signs/tradeoffs, level gating text, all sorting modes,
inventory unchanged by sorting/equip/remove, actual stats, and save/reload.
Screenshot: `/tmp/sea-evolution/equipment-comparison.png` (outside git).


## New encounters and loot

Two original low-poly monster models, no external assets:

- `puffer` / ปลาปักเป้าตะไคร่: kelp forest radius 30–60, HP65, XP20,
  damage9, essence2, material หนามตะไคร่. Inflates/emissive-warns for 1.2 seconds
  before a short-range hit; 2.4-second recovery. Backing away dodges it.
- `shrimp` / กุ้งหอกผลึก: cave radius 62–95, HP85, XP32, damage12, essence3,
  material เปลือกผลึก. Warns 0.9 seconds before a locked-direction 0.45-second
  dash. Side-step to dodge; each dash hits at most once, with recovery/cooldown.

`specialMonsterAI` handles only new species; old species retain their existing AI.
`clampNewHabitat` keeps new species in their zones. Central radius28 training area
and three-pursuer cap remain. `monsterRoster` keeps 21 active monsters:
5 ray, 4 shark, 4 whale, 4 eel, 2 puffer, 1 shrimp, 1 boss. Geometry is created at
startup, not per attack/frame. Real-device performance remains unverified.

New shared equipment (same level/rarity scaling and ownership rules):
- `crest` head / มงกุฎปะการัง: base HP×1.06, healing×1.08.
- `spine` back / แผงหนามปักเป้า: incoming damage×0.94, HP×1.08.
- `lance` tail / แพนหางผลึก: damage×1.06, cooldown recovery×1.05.

New equipment drops use the existing 20% normal-enemy chance and 75/22/3 rarity
weights. Materials keep the existing 60% chance. Daily quests can target puffer
for Lv6+ and shrimp for Lv12+. Bestiary includes discovery/kills/materials and
short dodge hints. Existing save fields store all progress; reserved eq key
validation now accepts the three new IDs.

```
node test-monsters.cjs
THREE_JS_PATH=/path/to/trusted/three-r128.min.js python3 test-monsters.py
```

Unit checks: attack telegraphs, dodging, single-hit dash, recovery, legacy AI
routing and habitat clamps. Browser checks: 100 spawn samples, exact roster,
starter-area exclusion, pursuer cap, essence/discovery, new equipment awards,
backup-compatible save/reload, 4 views per monster and gear on all 3 species.
Model screenshots pause simulation and hide transient messages/debug output;
they are not FPS benchmarks. Images stay in `/tmp/sea-evolution`, outside git.
