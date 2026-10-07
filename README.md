# U21CAX01 Entrepreneurship Learning Studio

Responsive GitHub Pages learning hub for **U21CAX01 - Entrepreneurship Development and Startup**.

## Current release

The site is designed for revision: students read the U21CAX01 Study Material first, then use these pages to consolidate.

- 45 revision pages, one per syllabus topic across all five units. Each has a Study Material page reference, key points, a framework, a worked example and Indian case lens, common mistakes, key terms, a three-question quick check and model 2-mark answers.
- Five unit hubs, each with the case bank, a 20-question unit quiz, all 2-mark answers, 14-mark question plans, key-term flashcards and lab links.
- Quick-check and quiz progress is kept only in the learner's browser (`localStorage`).
- Interactive labs: 9 for Unit I, 15 for Unit II and 9 for Unit III, linked from the matching revision topics. Units IV and V link to related earlier labs.
- One accessible course home with five unit tabs and 45 topic links.
- Anonymous aggregate usage is measured with Google Analytics (`G-VDJBZBB0MK`); the site has no authentication, stored scores or submitted learner text.
- Complete legacy Storyline packages remain in their Unit I folders for archival compatibility, but the student pages present one interaction per topic.

## Live course

[Open the published course](https://counterfietjoel.github.io/U21cax01/)

## Structure

```text
index.html                    Five-unit course home (generated)
content/unit-N.yml            Revision content for each unit (edit these)
content/question-bank.json    Question bank: Part A MCQs, Part B and Part C
learn/unit-N/                 Generated unit hubs and topic revision pages
assets/learn.css, learn.js    Revision-page styles, quizzes and progress ticks
tools/build_learn.py          Builds learn/, index.html and site-manifest.json
assets/home.css               Home-page visual system
assets/home.js                Accessible unit tabs
modules/01-.../               Unit I native-web topic plus archived Storyline package
modules/unit-2/               Fifteen Unit II venture labs and shared runtime
modules/unit-3/               Nine Unit III evidence studios
site-manifest.json            Machine-readable five-unit topic map
tools/validate_site.py        Structural and reference validation
tools/smoke_test.js           Desktop/mobile browser QA
.nojekyll                     Preserves all static asset paths on GitHub Pages
```

For local preview, serve the repository through HTTP rather than opening it directly:

```powershell
python -m http.server 8765
```

## Editing revision content

Edit `content/unit-N.yml`, then rebuild and validate:

```powershell
pip install pyyaml
python tools\build_learn.py
python tools\validate_site.py
```

In the YAML, options and table rows are pipe-separated strings (`A | B | C | D`). Unit quiz items hold only `answer` (0-based) and `why`; the stem and options come from Part A of `content/question-bank.json`, in order. `build_learn.py` stops with a message if a required field, option count or table width is wrong.
