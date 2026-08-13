"""Validate the complete U21CAX01 three-unit GitHub Pages bundle."""

from __future__ import annotations

import json
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

UNIT_ONE = (
    "01-concept-of-entrepreneurship", "02-characteristics-of-entrepreneurship",
    "03-types-of-entrepreneurship", "04-factors-affecting-entrepreneurs",
    "05-entrepreneurship-mindset", "06-inventors-and-entrepreneurs",
    "07-companies-and-startups", "08-entrepreneurial-environment-and-growth",
    "09-entrepreneurship-economic-development",
)
UNIT_COUNTS = (9, 15, 9)
ANALYTICS_ID = "G-VDJBZBB0MK"
FORBIDDEN = (
    "lorem ipsum", "placeholder text",
    "units iii-v and the mcq", "lumi h5p",
)


class ReferenceParser(HTMLParser):
    """Collect local href and src references."""

    def __init__(self) -> None:
        super().__init__()
        self.references: list[str] = []

    def handle_starttag(self, _tag: str, attrs: list[tuple[str, str | None]]) -> None:
        for name, value in attrs:
            if name in {"href", "src"} and value:
                self.references.append(value)


def local_target(document: Path, reference: str) -> Path | None:
    """Resolve a local reference and ignore fragments, data and remote URLs."""

    parsed = urlsplit(reference)
    if parsed.scheme or parsed.netloc or reference.startswith(("#", "data:")):
        return None
    if not parsed.path:
        return None
    return (document.parent / unquote(parsed.path)).resolve()


def validate(root: Path) -> list[str]:
    """Return all structural, content and reference errors."""

    errors: list[str] = []
    for relative in (
        "index.html", ".nojekyll", "README.md", "site-manifest.json",
        "assets/home.css", "assets/home.js", "assets/favicon.svg",
        "assets/images/hero-venture-lab.png",
        "modules/unit-2/shared/unit2.css",
        "modules/unit-2/shared/unit2-data.js",
        "modules/unit-2/shared/unit2-runtime.js",
        "modules/unit-3/assets/unit3.css",
        "modules/unit-3/assets/unit3.js",
    ):
        if not (root / relative).exists():
            errors.append(f"Missing required path: {relative}")

    try:
        manifest = json.loads((root / "site-manifest.json").read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"Invalid site-manifest.json: {exc}"]

    units = manifest.get("units", [])
    if len(units) != 3:
        errors.append("Manifest must contain exactly three live units")
    counts = tuple(len(unit.get("topics", [])) for unit in units)
    if counts != UNIT_COUNTS:
        errors.append(f"Topic counts must be {UNIT_COUNTS}; found {counts}")

    topic_paths: list[str] = []
    for unit in units:
        for topic in unit.get("topics", []):
            if not isinstance(topic, list) or len(topic) != 2:
                errors.append(f"Invalid topic entry: {topic!r}")
                continue
            topic_paths.append(topic[1])
    if len(topic_paths) != len(set(topic_paths)):
        errors.append("Manifest contains duplicate topic paths")

    for slug in UNIT_ONE:
        module = root / "modules" / slug
        for relative in ("index.html", "story.html", "html5", "mobile", "story_content"):
            if not (module / relative).exists():
                errors.append(f"Unit I {slug}: missing {relative}")

    documents = [
        root / "index.html",
        root / "modules" / "unit-3" / "index.html",
        *(root / path for path in topic_paths),
    ]
    resolved_root = root.resolve()
    for document in documents:
        if not document.exists():
            errors.append(f"Missing topic document: {document.relative_to(root)}")
            continue
        text = document.read_text(encoding="utf-8")
        lower = text.lower()
        if text.count(ANALYTICS_ID) != 2:
            errors.append(
                f"{document.relative_to(root)} must contain one Google Analytics loader and config"
            )
        if text.count("googletagmanager.com/gtag/js") != 1:
            errors.append(
                f"{document.relative_to(root)} must contain exactly one Google tag loader"
            )
        for phrase in FORBIDDEN:
            if phrase in lower:
                errors.append(f"{document.relative_to(root)} contains forbidden text: {phrase}")
        parser = ReferenceParser()
        parser.feed(text)
        for reference in parser.references:
            target = local_target(document, reference)
            if target is None:
                continue
            try:
                target.relative_to(resolved_root)
            except ValueError:
                errors.append(f"{document.relative_to(root)} escapes site: {reference}")
                continue
            if not target.exists():
                errors.append(f"{document.relative_to(root)} missing reference: {reference}")
    return errors


def main() -> int:
    """Run validation and print a concise report."""

    root = Path(__file__).resolve().parent.parent
    errors = validate(root)
    if errors:
        print(f"VALIDATION FAILED ({len(errors)} error(s))")
        for error in errors:
            print(f"- {error}")
        return 1
    file_count = sum(1 for path in root.rglob("*") if path.is_file() and ".git" not in path.parts)
    bundle_bytes = sum(path.stat().st_size for path in root.rglob("*") if path.is_file() and ".git" not in path.parts)
    print("VALIDATION PASSED")
    print("- Live units: 3")
    print("- Live topics: 33")
    print(f"- Bundle files: {file_count}")
    print(f"- Bundle size: {bundle_bytes / (1024 * 1024):.1f} MB")
    print("- Topic references and required assets: resolved")
    print(f"- Anonymous aggregate analytics: enabled ({ANALYTICS_ID})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
