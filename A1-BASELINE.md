# A1 — Mobile and save export baseline

Baseline inspected against PR #7 commit `f99cbea7237433cb50eae3db4f074667e5d88dc4`.

- The game is a single HTML file, with viewport-fit, safe-area CSS, compact landscape layout and touch controls. It loads Three.js from cdnjs. The inspected code has no app manifest or service worker; offline play and cached update behavior are not established.
- GitHub Pages production and Cloudflare previews use distinct origins and localStorage. Safari and a Home Screen web app may have separate storage even for the same site. Do not assume any automatic save transfer.
- Save keys are `selcls`, `sel01`, `sel01b`, `sel01m`; v0.4/v0.5 records may lack `q`, and unrecorded historical kill counts cannot be reconstructed.
- Save export is initiated by the user from the species book. It reads existing keys and creates a local JSON download; it does not import or modify saves. Invalid data, unavailable storage, missing saves and mismatched selection stop export with a message. The export preserves unknown fields and contains metadata including origin and time; keep the backup private and outside the repository.
- Downloads use Blob/object URLs and an anchor. Starting a download is not proof the device saved the file. Validate the file in the device Downloads/Files app. Browser policy and device settings can prevent or alter the download.
- No manifest, service worker, offline mode or import is added by A1–A2. A CDN or network failure can prevent game startup, including on Home Screen.
- Code inspection and desktop fixtures do not establish behavior on iOS Safari or Home Screen. Owner testing on iPhone 15 Pro remains required; iPhone 11 and iPad 8 remain target devices. Verify portrait/landscape, safe area, save download/open in Files, private data handling and network unavailable/recovery using test saves only.
- Previously a single real Sea Eater save copy was checked on Windows Chrome with a separate fixture; it is not evidence for other characters, devices or historical save origins.
