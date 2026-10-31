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

## Rectangular maps, portals, minimap, more monsters (Claude, 31 Oct 2026)

- Five separate rectangular maps (Ragnarok style) share one scene; only the current one is visible (`MAPS`, `buildMapWorld`): town (64x44, safe, plaza/fountain/houses, regenerates HP), shallows, kelp forest, dark cave (100x64 each) and the boss lair (56x56). Player and monsters are clamped to the map rectangle; translucent walls mark the edge. There is no obstacle collision yet.
- Portals sit at map edges (`PORTALS`: x, z, `to:{map,x,z}`), fade + teleport, 2 s cooldown, 3 s protection on arrival. Dying returns to the town. The current map is not saved (always starts in the town).
- Monsters belong to one map each and are "parked" (hidden, `m.dead=1e9`) while the player is elsewhere (`setMap`). Spawn table `SPAWN`: shallows rays 14; kelp forest sharks 8, eels 6, puffers 6; cave whales 7, shrimp 5; lair boss. They spawn in clusters (seeded fixed homes, `m.home`), 47 in total; respawn within 5 units of home, never on the player.
- Zone scaling: kelp forest HP x1.3 / XP x1.6, cave HP x1.7 / XP x2.4. `XPMUL=.3` slows levelling (estimate only: about 2-3 h to Lv20 at constant fighting); daily/login XP halved; normal gear drop 12% (boss 100%).
- UI: minimap under the HUD card (live monsters, portals, player; tap = full map), full map screen with tabs, spawn points (dimmed while waiting) and the boss crown. Target lock-on: ring under the locked monster, attacks auto-aim, shots home in, round target button switches.
- Tests: all `test-*.cjs`, `test-gear-ui.py`, `test-evolution.py`, `test-monsters.py` pass (monster tests updated for the new roster and rectangular bounds). Under slow rendering, game timers use capped dt so cooldowns last longer in real time.

## Directional map branches (Codex, 31 Oct 2026; supersedes five-map chain)

- `MAPS` has 14 entries: town 0; north/poison 5 → 2 → 6; west/spikes 7 → 8 → 9; south/normal 1 → 10 → 11; east/weird 12 → 13 → 3 → boss lair 4. Fields recommend Lv1/6/12; boss Lv15. North is -Z, west -X, south +Z, east +X.
- `MAP_ROUTES` drives both the cross-shaped world selector and 26 directional paired `PORTALS`. Arrival is four units inside the return portal, with the existing two-second warp cooldown and three-second protection. Portal colors use tier, not numeric map IDs.
- `SPAWN` redistributes the existing 90 monsters / 23 species: north eel + poison crab; west puffer, spiked chompers and crystal shrimp; south ray/shark/whale; east the remaining weird families; boss stays in the lair. Town remains safe. Fixed clustered homes and parked respawn timers remain.
- Map metadata now selects biome decoration, music, HP/XP scaling (1/1.3/1.7 HP and 1/1.6/2.4 XP by tier), and daily zone events. Old kelp/cave quest event IDs stay on maps 2/3. The dex habitat list comes from SPAWN, including species with multiple maps. No new save fields or changes to save-tools.js are needed; all saves still start in town.
- Full map: cross-shaped route buttons, theme directions, levels, current-location pin, per-map monsters and portals; responsive layouts checked at 320×568, 390×844, 844×390, 768×1024 and 1024×768. Minimap shows local north, branch theme, recommended level, live monsters and tier-colored portals.
- Owner requested an easier FPS display during this round: book → Display → FPS button. It shows the numeric counter at the bottom and remembers the preference in localStorage `fps` (separate from character saves). `?debug=1` still enables detailed screen diagnostics. Cloud software-renderer values are not device performance results.
- Added `test-maps.cjs` / `test-maps.py`; monster tests now check all actual puffer/shrimp map placements (550 browser spawn samples). The map browser test traverses all 26 portal triggers, checks map/monster visibility, arrival protection, respawn timers, music, legacy save/reload, all route buttons, overflow and the persisted FPS toggle without a query string. Screenshots stay in `/tmp/sea-evolution`.
- Validation: all six Node suites and five Chromium suites pass. Full evolution regression covers all three playable species, six jobs and four views; after a 30-second action timeout, the full rerun passed with a temporary 120-second action timeout (not committed). No physical iPad/iPhone test or real-device FPS measurement.

## Whole-edge block traversal (Codex, 31 Oct 2026; replaces point warps)

- The owner requested walking from block to block by leaving a map edge. The 14-map topology and all species/levels remain; every side with a MAP_ROUTES neighbor is open across its entire length. Non-neighbor sides retain bounds/walls.
- PORTALS now describes directed shared edges (`dx`, `dz`, `to.map`) plus a label anchor. `mapExit` computes the destination from the player's actual position, preserving the lateral fraction using each map's playable inset. The destination is two units inside, so immediate reverse walking works without a timer and standing at arrival does not bounce.
- `crossMap` switches synchronously without a fade/input lock, moves camera/target/bubbles/light by the same displacement, retains facing/input and grants the existing three-second protection. Old-block projectiles/vortices are removed and disposed; monsters keep their map parking/respawn behavior.
- World borders skip walls/lines on connected sides. Terrain-following colored strips and directional destination labels replace the rings; decoration avoids the full exit strip. Full map and minimap draw complete colored sides rather than portal dots.
- No persistent fields changed. Save-tools/account mode/equipment/touch layout are unchanged. Tests now cover 78 off-center browser crossings, real held walking through four town sides, camera displacement, no automatic bounce, closed boundary walls, attack cleanup and legacy reload. The Node suite also covers round trips, corners and missing neighbors.
- All six Node suites and all five Chromium suites pass, including full evolution (three species / six jobs / four views, temporary 120-second action timeout). Screenshots were inspected in portrait/landscape, normal/close views. Physical iPad/iPhone edge-walking behavior remains for the owner to verify on the branch preview.

## Compact bestiary book (Codex, 31 Oct 2026)

- `renderDex` retains the existing `#dex` container and delegated handlers. Icon tabs select species/daily quests/inventory/settings, with equipment accessible from every tab. The 23 species are paged in groups of eight; seen species expand to show habitat, defeats, drop and hints, while unseen species stay unknown.
- `bookTab` and `bookPage` are session-only; no save schema changes. Existing import/export, character switch, naming, FPS/display and equipment button IDs remain intact under their corresponding tabs. `test-book.py` exercises paging, discovered/unknown cards, the tabs, FPS, save-code copying, equipment and four viewport sizes. `test-monsters.py` expands cards for its hint checks; `test-maps.py` opens the settings tab before toggling FPS.
