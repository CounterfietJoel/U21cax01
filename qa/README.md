# Local QA evidence

The two screenshots in this folder are generated with the locally installed
Google Chrome:

- `home-desktop.png` — 1440 × 1000 desktop viewport
- `home-mobile.png` — 390 × 844 mobile viewport

Latest checks:

- Static bundle validator: passed
- Five unit tabs and 45 topic links on the course home: passed
- 45 revision-topic pages and 5 unit hubs: HTTP 200, one h1 each
- All home, hub and topic pages at 1366 px and 390 px: no horizontal overflow, no console errors
- All internal links from generated pages resolve
- Browser console errors: 0

Re-run locally after starting an HTTP server:

```powershell
python tools\validate_site.py

$env:NODE_PATH = "C:\path\to\node_modules"
node tools\smoke_test.js
```
