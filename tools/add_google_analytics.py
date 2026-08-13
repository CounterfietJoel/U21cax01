"""Add the course Google Analytics tag to learner-facing entry pages."""

from __future__ import annotations

import json
from pathlib import Path

MEASUREMENT_ID = "G-VDJBZBB0MK"
TAG = f"""  <!-- Google tag (gtag.js) -->
  <script async src="https://www.googletagmanager.com/gtag/js?id={MEASUREMENT_ID}"></script>
  <script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){{dataLayer.push(arguments);}}
    gtag('js', new Date());
    gtag('config', '{MEASUREMENT_ID}');
  </script>
"""


def learner_entry_pages(root: Path) -> list[Path]:
    """Return the homepage, every topic, and the Unit III studio hub."""

    manifest = json.loads((root / "site-manifest.json").read_text(encoding="utf-8"))
    relative_paths = ["index.html", "modules/unit-3/index.html"]
    relative_paths.extend(
        topic[1]
        for unit in manifest["units"]
        for topic in unit["topics"]
    )
    return [root / relative_path for relative_path in dict.fromkeys(relative_paths)]


def main() -> int:
    """Insert the tag once in each designated page."""

    root = Path(__file__).resolve().parent.parent
    changed = 0
    for page in learner_entry_pages(root):
        text = page.read_text(encoding="utf-8")
        if MEASUREMENT_ID in text:
            continue
        if "</head>" not in text.lower():
            raise ValueError(f"Missing </head> in {page.relative_to(root)}")
        head_end = text.lower().index("</head>")
        updated = text[:head_end] + TAG + text[head_end:]
        page.write_text(updated, encoding="utf-8")
        changed += 1
    print(f"Google Analytics tag present on {len(learner_entry_pages(root))} entry pages; {changed} updated.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
