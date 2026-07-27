"""Validate the deployable U21CAX01 GitHub Pages bundle."""

from __future__ import annotations

import json
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit


EXPECTED_MODULES = (
    "01-concept-of-entrepreneurship",
    "02-characteristics-of-entrepreneurship",
    "03-types-of-entrepreneurship",
    "04-factors-affecting-entrepreneurs",
    "05-entrepreneurship-mindset",
    "06-inventors-and-entrepreneurs",
    "07-companies-and-startups",
    "08-entrepreneurial-environment-and-growth",
    "09-entrepreneurship-economic-development",
)
REQUIRED_STORYLINE_PATHS = ("story.html", "html5", "mobile", "story_content")
FORBIDDEN_TEXT = (
    "lorem ipsum",
    "insert title",
    "placeholder text",
    "replace this text",
)


class ReferenceParser(HTMLParser):
    """Collect local href and src references from an HTML document."""

    def __init__(self) -> None:
        super().__init__()
        self.references: list[str] = []

    def handle_starttag(
        self, tag: str, attrs: list[tuple[str, str | None]]
    ) -> None:
        for name, value in attrs:
            if name in {"href", "src"} and value:
                self.references.append(value)


def local_target(document: Path, reference: str) -> Path | None:
    """Resolve a local document reference, ignoring remote and fragment URLs."""

    parsed = urlsplit(reference)
    if parsed.scheme or parsed.netloc or reference.startswith(("#", "data:")):
        return None
    path_text = unquote(parsed.path)
    if not path_text:
        return None
    return (document.parent / path_text).resolve()


def validate(root: Path) -> list[str]:
    """Return validation errors for the site rooted at *root*."""

    errors: list[str] = []
    required_root_files = (
        "index.html",
        "README.md",
        ".nojekyll",
        "assets/styles.css",
        "assets/app.js",
        "assets/images/hero-venture-lab.png",
        "assets/images/mcq-flashcards.png",
        "site-manifest.json",
    )
    for relative_path in required_root_files:
        if not (root / relative_path).exists():
            errors.append(f"Missing required site path: {relative_path}")

    modules_root = root / "modules"
    actual_modules = (
        sorted(path.name for path in modules_root.iterdir() if path.is_dir())
        if modules_root.exists()
        else []
    )
    if actual_modules != list(EXPECTED_MODULES):
        errors.append(
            "Module folders do not match the expected nine: "
            f"{', '.join(actual_modules)}"
        )

    for module_name in EXPECTED_MODULES:
        module_root = modules_root / module_name
        for required_path in ("index.html", "module.json", *REQUIRED_STORYLINE_PATHS):
            if not (module_root / required_path).exists():
                errors.append(f"{module_name}: missing {required_path}")

        if module_root.exists():
            file_count = sum(1 for path in module_root.rglob("*") if path.is_file())
            if file_count < 20:
                errors.append(
                    f"{module_name}: only {file_count} files; published output appears incomplete"
                )

    manifest_path = root / "site-manifest.json"
    if manifest_path.exists():
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            modules = manifest.get("modules", [])
            if manifest.get("module_count") != 9 or len(modules) != 9:
                errors.append("Manifest must declare exactly nine modules")
            for module in modules:
                if not module.get("storyline_published"):
                    errors.append(
                        f"Manifest marks {module.get('slug', 'unknown')} as unpublished"
                    )
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"Invalid site-manifest.json: {exc}")

    html_documents = [root / "index.html"]
    html_documents.extend(
        modules_root / module_name / "index.html"
        for module_name in EXPECTED_MODULES
    )
    resolved_root = root.resolve()
    for document in html_documents:
        if not document.exists():
            continue
        text = document.read_text(encoding="utf-8")
        lower_text = text.lower()
        for forbidden in FORBIDDEN_TEXT:
            if forbidden in lower_text:
                errors.append(f"{document.relative_to(root)} contains '{forbidden}'")

        parser = ReferenceParser()
        parser.feed(text)
        for reference in parser.references:
            target = local_target(document, reference)
            if target is None:
                continue
            try:
                target.relative_to(resolved_root)
            except ValueError:
                errors.append(
                    f"{document.relative_to(root)} references outside site: {reference}"
                )
                continue
            if not target.exists():
                errors.append(
                    f"{document.relative_to(root)} has missing reference: {reference}"
                )

    return errors


def deployable_files(root: Path):
    """Yield files that belong to the Pages artifact, excluding Git internals."""

    for path in root.rglob("*"):
        if not path.is_file():
            continue
        relative_parts = path.relative_to(root).parts
        if ".git" in relative_parts:
            continue
        if len(relative_parts) == 2 and relative_parts[0] == "qa":
            if relative_parts[1].endswith(".log"):
                continue
        yield path


def main() -> int:
    """Run validation and print a concise report."""

    site_root = Path(__file__).resolve().parent.parent
    errors = validate(site_root)
    if errors:
        print(f"VALIDATION FAILED ({len(errors)} error(s))")
        for error in errors:
            print(f"- {error}")
        return 1

    files = list(deployable_files(site_root))
    total_files = len(files)
    total_bytes = sum(path.stat().st_size for path in files)
    print("VALIDATION PASSED")
    print(f"- Modules: {len(EXPECTED_MODULES)}")
    print(f"- Files: {total_files}")
    print(f"- Bundle size: {total_bytes / (1024 * 1024):.1f} MB")
    print("- Complete Storyline paths: story.html, html5, mobile, story_content")
    print("- Homepage and module wrapper references: resolved")
    return 0


if __name__ == "__main__":
    sys.exit(main())
