# Local QA evidence

The two screenshots in this folder are generated with the locally installed
Google Chrome:

- `home-desktop.png` — 1440 × 1000 desktop viewport
- `home-mobile.png` — 390 × 844 mobile viewport

Latest checks:

- Static bundle validator: passed
- Five units plus MCQs in the course menu: passed
- Nine Unit I cards: passed
- Nine module wrappers: HTTP 200
- Nine Storyline `story.html` launch files: HTTP 200
- Mobile menu open, Escape close and ARIA state: passed
- Browser console errors: 0

Re-run locally after starting an HTTP server:

```powershell
python tools\validate_site.py

$env:NODE_PATH = "C:\path\to\node_modules"
node tools\smoke_test.js
```
