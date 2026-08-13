# U21CAX01 Entrepreneurship Learning Studio

Responsive GitHub Pages learning hub for **U21CAX01 - Entrepreneurship Development and Startup**.

## Current release

- Unit I: 9 interactive entrepreneurship topics.
- Unit II: 15 native-web venture-creation labs.
- Unit III: 9 business-plan and investment-pitch studios.
- One accessible course home with unit tabs and 33 direct topic links.
- No authentication, learner-level analytics, stored scores or submitted learner text.
- Complete legacy Storyline packages remain in their Unit I folders for archival compatibility, but the student pages present one interaction per topic.

## Live course

[Open the published course](https://counterfietjoel.github.io/U21cax01/)

## Structure

```text
index.html                    Three-unit course home
assets/home.css               Home-page visual system
assets/home.js                Accessible unit tabs
modules/01-.../               Unit I native-web topic plus archived Storyline package
modules/unit-2/               Fifteen Unit II venture labs and shared runtime
modules/unit-3/               Nine Unit III evidence studios
site-manifest.json            Machine-readable three-unit topic map
tools/validate_site.py        Structural and reference validation
tools/smoke_test.js           Desktop/mobile browser QA
.nojekyll                     Preserves all static asset paths on GitHub Pages
```

For local preview, serve the repository through HTTP rather than opening it directly:

```powershell
python -m http.server 8765
```
