# U21CAX01 - Entrepreneurship Development and Startup

Responsive GitHub Pages course home for the open elective **U21CAX01**.

## Current release

- Five syllabus units are mapped in the vertical course menu.
- All nine Unit I topics are live as 4-6 minute microlearning modules.
- Every Unit I folder contains its complete Articulate Storyline Web output.
- All 15 Unit II lessons are live as self-contained Lumi H5P interactions.
- Three syllabus-aligned videos and two full-size visual guides supplement the lessons.
- Units III-V and the MCQ/flashcard area remain mapped for future releases.
- Google Analytics measurement ID `G-VDJBZBB0MK` records course-site traffic.
- The site uses no authentication, score storage, or learner-level tracking.

## Open the course

[Launch the published course](https://counterfietjoel.github.io/U21cax01/)

For a local preview, serve the repository through HTTP:

```powershell
python -m http.server 8000
```

Then open `http://localhost:8000/`.

## Structure

```text
index.html                 Course home and unit-wise navigation
assets/                    Shared styling, scripts and original course visuals
modules/01-.../            Topic wrapper plus complete Storyline Web output
...
modules/09-.../
modules/unit-2/01-.../     Self-contained Lumi H5P interactive HTML
...
modules/unit-2/15-.../
site-manifest.json         Machine-readable Unit I and Unit II manifest
.nojekyll                  Preserves Storyline asset paths on GitHub Pages
```

The supplied Storyline templates and editable source files are intentionally
not distributed in this public repository.
