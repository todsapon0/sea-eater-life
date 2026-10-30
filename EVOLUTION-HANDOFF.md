# Species Evolution & Custom Mutation — PR #11

Base: `95fbcb60bffda7fad244d945e22c49d6d4a4b71b`, branch `claude/family-build`.
Continue on this branch and the existing PR #11. Do not merge into main before
owner approval of the character visuals. No keys or reference images belong in
this public repository. No paid services or real Supabase writes are needed.

## Implementation

- `index.html`: optional save fields `ev`, `es`, `mu`; permanent evolution costs
  40/140/360 essence at Lv8/14/20 (last requires a valid species job).
- `ORG` is the organ catalog; `organFor` filters by unlocked slot and species.
  `applyJob` resets and combines job, stars, evolution and organs each time.
  HP gains preserve current health; reduced maximum clamps health.
- `applyJobVisual` preserves the existing main mesh/color and job color handling.
  `buildOrgans` disposes its own old geometries/materials before rebuilding small
  attachments. Sea back attachment is lowered 0.4 from the requested anchor to
  contact the actual v2 body; sea tail is advanced toward its tip by 0.9 and
  fangs lowered 0.35 to clear the lip. Sea tail attachments rise 0.25
  (spikes another 0.2) to contact the upward-curving tail. Bloop bubbles are lowered/advanced to clear eyes.
- Movement uses `spMul`; Maja whirlpool ticks now also honor `dmgMul`; Bloop heal uses `healMul`.
- Evolution dialog allows free removal/switching, confirmation before permanent
  evolution, locked slots, requirements, and ready notifications. Narrow screens
  wrap the top toolbar so the new button does not cover the existing HUD.
- `save-tools.js`: optional fields validate on backup import; legacy saves still
  pass. Unknown organ IDs may be stored but cannot grant stats or render parts.

## Validation and rerun

```
node test-save-tools.cjs
node test-account-recovery.cjs
THREE_JS_PATH=/path/to/trusted/three-r128.min.js python3 test-evolution.py
```

Browser test requires Python Playwright and `/usr/bin/chromium` (provided in this
Cloud environment). Obtain Three.js r128 from the existing authoritative CDN with
TLS verification enabled; keep it outside the repo. The test routes that URL to
the local file, stubs the unused Supabase SDK, blocks all Supabase project calls,
and uses disposable browser contexts. Debug instrumentation is inserted only in
HTML served in memory, never into shipped code. Screenshots go outside the repo
to `/tmp/sea-evolution` or `EVOLUTION_ARTIFACTS`.

Tests cover three evolution steps, cancel confirmation, slot locking, all 15
organ multipliers (including incompatible species), job/star/evolution factors,
free unequip, increased HP, save/reload, and essence rewards for all five enemies.
The six existing jobs across three playable species are rendered from four angles.
There is no fourth playable species model in index.html at this base commit;
account.js has a pre-existing crab identifier but no matching playable model.

Cloud Chromium uses software WebGL. FPS observations here are not evidence of
30 FPS on iPad/iPhone. Review the model screenshots and test touch scrolling,
controls and FPS on actual devices before merge. Test accounts/real server-save
end-to-end checks remain outside this local-only test scope. Do not provision or
write Supabase data without explicit authorization.

## Results in this Cloud session

- Both Node suites and inline JavaScript syntax checks pass.
- Browser functional regression passes for Sea Eater, Bloop and El Gran Maja:
  requirements, confirmations, 3 stages, 15-organ multiplier checks per species,
  free equip/remove, save/reload, essence rewards, actual Bloop healing and Maja
  whirlpool damage. No console/page errors or Supabase project requests.
- 390px viewport checks pass: toolbar does not overlap HUD; evolution panel scrolls.
- Debug FPS in the last sequential functional run (software WebGL, 1000×780):
  Sea 6→5, Bloop 4→6, Maja 6→7. These brief readings vary substantially and do
  **not** establish a performance target or rule out a smaller regression.
- The visual capture run covers all six existing jobs at four camera angles.
  Owner approval of the rendered attachments and real-device FPS is still pending.

## Follow-up: larger joystick / camera separation

User reported that the left joystick was too small and near misses rotated the
camera. `#movezone` now owns a larger bottom-left touch area, including outside
of the visible circle. It captures the first movement pointer; a second pointer
cannot steal it. Releasing, cancelling, losing capture or window blur resets it.
Camera gestures remain on the canvas; walking + attack and walking + intentional
camera movement still work independently.

The circle is 144px on phones (previously 104px), 132px on narrow/landscape layouts
(previously 88px in landscape), and 160px on larger screens. The knob is 58–64px;
its travel stays inside the circle. Existing buttons remain above the pad and
panels remain scrollable.

Run `THREE_JS_PATH=/path/to/three-r128.min.js python3 test-touch-controls.py`.
CDP touch tests passed at 390×844, 844×390 and 320×568: near misses, capture outside
pad bounds, second-finger ownership, attack while walking, independent camera,
cancellation and two-finger canvas pinch. No console/page errors. Screenshots:
`/tmp/sea-evolution/touch-controls-<width>x<height>.png` (not committed).
Confirm the thumb feel on an actual phone; these are Chromium emulation checks.
