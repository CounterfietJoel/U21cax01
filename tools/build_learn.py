"""Build the five-unit revision site from content/unit-*.yml.

Run from the repository root:

    python tools/build_learn.py

The script regenerates index.html, learn/unit-N/index.html and one page per
syllabus topic. Edit the YAML files, not the generated HTML.
"""

from __future__ import annotations

import html
import json
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
CONTENT = ROOT / "content"
OUT = ROOT / "learn"
ANALYTICS_ID = "G-VDJBZBB0MK"
CSS_VERSION = "2"
STUDY_MATERIAL = "U21CAX01 Study Material"

GTAG = f"""  <!-- Google tag (gtag.js) -->
  <script async src="https://www.googletagmanager.com/gtag/js?id={ANALYTICS_ID}"></script>
  <script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){{dataLayer.push(arguments);}}
    gtag('js', new Date());
    gtag('config', '{ANALYTICS_ID}');
  </script>"""


def esc(text: object) -> str:
    return html.escape(str(text), quote=True)


def rich(text: object) -> str:
    """Escape text, then allow **bold** and *italic* markers."""

    value = esc(text)
    value = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", value)
    value = re.sub(r"(?<!\*)\*(?!\s)(.+?)(?<!\s)\*(?!\*)", r"<em>\1</em>", value)
    return value


def roman(number: int) -> str:
    return ["", "I", "II", "III", "IV", "V"][number]


def topic_file(topic: dict) -> str:
    return f"{topic['index']:02d}-{topic['slug']}.html"


def head(title: str, description: str, prefix: str) -> str:
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <meta name="description" content="{esc(description)}">
  <meta name="theme-color" content="#07365d">
  <title>{esc(title)}</title>
  <link rel="icon" href="{prefix}assets/favicon.svg" type="image/svg+xml">
  <link rel="stylesheet" href="{prefix}assets/learn.css?v={CSS_VERSION}">
{GTAG}
</head>"""


def topbar(prefix: str, crumbs: list[tuple[str, str]]) -> str:
    items = "".join(
        f'<li><a href="{esc(href)}">{esc(label)}</a></li>' if href else f'<li aria-current="page">{esc(label)}</li>'
        for label, href in crumbs
    )
    units = "".join(
        f'<a href="{prefix}learn/unit-{n}/index.html">Unit {roman(n)}</a>' for n in range(1, 6)
    )
    return f"""<body>
  <a class="skip-link" href="#main">Skip to content</a>
  <header class="topbar">
    <a class="brand" href="{prefix}index.html" aria-label="U21CAX01 course home"><span>U21</span><b>Entrepreneurship Learning Studio</b></a>
    <nav class="unit-links" aria-label="Units">{units}</nav>
  </header>
  <nav class="crumbs" aria-label="Breadcrumb"><ol>{items}</ol></nav>"""


def footer(prefix: str) -> str:
    return f"""  <footer class="site-foot">
    <p>U21CAX01 · Entrepreneurship Development and Startup · KPR Institute of Engineering and Technology</p>
    <p>Read the {STUDY_MATERIAL} first; use these pages to consolidate. Self-checks are not graded and nothing you answer leaves this browser.</p>
  </footer>
  <script src="{prefix}assets/learn.js?v={CSS_VERSION}" defer></script>
</body>
</html>
"""


def mcq(question: dict, qid: str, number: int | None = None) -> str:
    options = cells(question["options"])
    answer = int(question["answer"])
    if not 0 <= answer < len(options):
        raise ValueError(f"{qid}: answer index out of range")
    buttons = "".join(
        f'<li><button type="button" class="opt" data-correct="{str(i == answer).lower()}">'
        f'<span class="opt-key">{"abcd"[i]}</span><span>{rich(text)}</span></button></li>'
        for i, text in enumerate(options)
    )
    label = f'<span class="q-no">{number}</span>' if number else ""
    why = question.get("why", "")
    return f"""<li class="mcq" id="{qid}">
        <p class="q">{label}{rich(question['q'])}</p>
        <ol class="opts" type="a">{buttons}</ol>
        <p class="feedback" hidden><span class="verdict"></span> {rich(why)}</p>
      </li>"""


def short_answers(items: list[dict], prefix_id: str) -> str:
    if not items:
        return ""
    rows = "".join(
        f"""<details class="qa" id="{prefix_id}-{i + 1}"><summary>{rich(item['q'])}</summary>
          <div class="answer">{''.join(f'<p>{rich(p)}</p>' for p in as_list(item['a']))}</div></details>"""
        for i, item in enumerate(items)
    )
    return rows


def cells(value: object) -> list:
    """Accept a YAML list or a string with ' | ' separators."""

    if isinstance(value, str):
        return [part.strip() for part in value.split(" | ")]
    return list(value)


def as_list(value: object) -> list:
    if value is None:
        return []
    return value if isinstance(value, list) else [value]


def table(block: dict) -> str:
    head_row = cells(block["head"])
    head_cells = "".join(f"<th scope=\"col\">{rich(c)}</th>" for c in head_row)
    body = "".join(
        "<tr>" + "".join(
            (f"<th scope=\"row\">{rich(c)}</th>" if j == 0 else f"<td>{rich(c)}</td>")
            for j, c in enumerate(cells(row))
        ) + "</tr>"
        for row in block["rows"]
    )
    caption = f"<caption>{rich(block['caption'])}</caption>" if block.get("caption") else ""
    return f"""<div class="table-wrap" tabindex="0"><table>{caption}<thead><tr>{head_cells}</tr></thead><tbody>{body}</tbody></table></div>"""


def lab_cards(labs: list[dict], prefix: str) -> str:
    if not labs:
        return ""
    cards = "".join(
        f'<li><a class="lab" href="{prefix}{esc(lab["href"])}"><b>{esc(lab["title"])}</b><span>{esc(lab.get("note", "Interactive practice"))}</span></a></li>'
        for lab in labs
    )
    return f"""<section class="block" aria-labelledby="labs-h">
      <h2 id="labs-h"><span class="num">8</span>Practise in a lab</h2>
      <p class="lead-in">Optional. These interactive labs let you apply the topic to a realistic decision.</p>
      <ul class="lab-grid">{cards}</ul>
    </section>"""


def topic_page(unit: dict, topic: dict, prev_t: dict | None, next_t: dict | None) -> str:
    n = unit["number"]
    prefix = "../../"
    tid = topic["id"]
    hub = "index.html"
    crumbs = [("Home", f"{prefix}index.html"), (f"Unit {roman(n)}", hub), (f"{tid} {topic['title']}", "")]
    key_points = "".join(f"<li>{rich(p)}</li>" for p in topic["key_points"])
    framework = topic.get("framework")
    framework_html = ""
    if framework:
        cards = "".join(
            f'<li><b>{rich(item["term"])}</b><span>{rich(item["text"])}</span></li>' for item in framework["items"]
        )
        framework_html = f"""<section class="block" aria-labelledby="fw-h">
      <h2 id="fw-h"><span class="num">2</span>{rich(framework['title'])}</h2>
      <ul class="cards">{cards}</ul>
      {table(topic['table']) if topic.get('table') else ''}
    </section>"""
    elif topic.get("table"):
        framework_html = f"""<section class="block" aria-labelledby="fw-h"><h2 id="fw-h"><span class="num">2</span>Compare</h2>{table(topic['table'])}</section>"""
    case = topic.get("case")
    case_html = ""
    if case:
        case_html = f"""<aside class="case">
          <p class="tag">Case lens</p>
          <h3>{rich(case['name'])}</h3>
          <p>{rich(case['text'])}</p>
          {f'<p class="prompt"><b>Think:</b> {rich(case["prompt"])}</p>' if case.get('prompt') else ''}
        </aside>"""
    mistakes = "".join(f"<li>{rich(m)}</li>" for m in topic.get("mistakes", []))
    terms = "".join(
        f"<div><dt>{rich(t['term'])}</dt><dd>{rich(t['def'])}</dd></div>" for t in topic.get("terms", [])
    )
    checks = "".join(mcq(q, f"{topic['slug']}-q{i + 1}", i + 1) for i, q in enumerate(topic["check"]))
    exam = short_answers(topic.get("short_answers", []), f"{topic['slug']}-sa")
    pager = '<nav class="pager" aria-label="Topic navigation">'
    pager += (f'<a class="prev" href="{topic_file(prev_t)}"><small>Previous</small><b>{esc(prev_t["id"])} {esc(prev_t["title"])}</b></a>'
              if prev_t else f'<a class="prev" href="{hub}"><small>Back to</small><b>Unit {roman(n)} overview</b></a>')
    pager += (f'<a class="next" href="{topic_file(next_t)}"><small>Next</small><b>{esc(next_t["id"])} {esc(next_t["title"])}</b></a>'
              if next_t else f'<a class="next" href="{hub}#quiz"><small>Finish the unit</small><b>Unit {roman(n)} quiz and exam practice</b></a>')
    pager += "</nav>"
    position = f"Topic {topic['index']} of {len(unit['topics'])}"
    return f"""{head(f"{tid} {topic['title']} | U21CAX01", topic['outcome'], prefix)}
{topbar(prefix, crumbs)}
  <main id="main" class="topic" data-topic="{esc(tid)}" data-unit="{n}">
    <section class="topic-hero u{n}">
      <p class="eyebrow">Unit {roman(n)} · {esc(unit['co_short'])} · {esc(position)}</p>
      <h1><span class="tid">{esc(tid)}</span> {esc(topic['title'])}</h1>
      <p class="outcome"><b>You should be able to:</b> {esc(topic['outcome'])}</p>
      <ul class="chips">
        <li><span aria-hidden="true">📖</span> Read first: {STUDY_MATERIAL}, p. {esc(topic['page'])}</li>
        <li><span aria-hidden="true">⏱</span> About 10 minutes to revise</li>
      </ul>
    </section>

    <section class="block nutshell" aria-labelledby="ns-h">
      <h2 id="ns-h"><span class="num">1</span>In a nutshell</h2>
      {''.join(f'<p>{rich(p)}</p>' for p in as_list(topic['summary']))}
      <ol class="points">{key_points}</ol>
    </section>

    {framework_html}

    <section class="block" aria-labelledby="ap-h">
      <h2 id="ap-h"><span class="num">3</span>See it applied</h2>
      <div class="applied">
        <div class="example"><p class="tag">Example</p><p>{rich(topic['example'])}</p></div>
        {case_html}
      </div>
    </section>

    <section class="block" aria-labelledby="mi-h">
      <h2 id="mi-h"><span class="num">4</span>Avoid these mistakes</h2>
      <ul class="mistakes">{mistakes}</ul>
    </section>

    <section class="block" aria-labelledby="kt-h">
      <h2 id="kt-h"><span class="num">5</span>Key terms</h2>
      <dl class="terms">{terms}</dl>
    </section>

    <section class="block check" aria-labelledby="qc-h">
      <h2 id="qc-h"><span class="num">6</span>Quick check</h2>
      <p class="lead-in">Pick an answer to see the explanation. Get all of them right to mark this topic as revised.</p>
      <ol class="mcqs" data-set="{esc(tid)}">{checks}</ol>
      <p class="set-result" aria-live="polite"></p>
    </section>

    <section class="block" aria-labelledby="ex-h">
      <h2 id="ex-h"><span class="num">7</span>Exam practice: 2-mark questions</h2>
      <p class="lead-in">Answer in your own words first, then open the model answer to compare.</p>
      {exam}
    </section>

    {lab_cards(topic.get('labs', []), prefix)}

    {pager}
  </main>
{footer(prefix)}"""


def hub_page(unit: dict) -> str:
    n = unit["number"]
    prefix = "../../"
    crumbs = [("Home", f"{prefix}index.html"), (f"Unit {roman(n)} · {unit['title']}", "")]
    topics = "".join(
        f"""<li><a href="{topic_file(t)}" data-progress="{esc(t['id'])}"><span class="tid">{esc(t['id'])}</span>
          <span><b>{esc(t['title'])}</b><small>{esc(t['outcome'])}</small></span><i class="tick" aria-hidden="true"></i></a></li>"""
        for t in unit["topics"]
    )
    cases = "".join(
        f"""<li class="case-card"><h3>{rich(c['name'])}</h3><p>{rich(c['what'])}</p>
          {f'<p class="prompt"><b>Use it for:</b> {rich(c["use"])}</p>' if c.get('use') else ''}</li>"""
        for c in unit.get("cases", [])
    )
    quiz = "".join(mcq(q, f"u{n}-quiz-{i + 1}", i + 1) for i, q in enumerate(unit["quiz"]))
    short = short_answers(
        [item for t in unit["topics"] for item in t.get("short_answers", [])], f"u{n}-sa"
    )
    long_items = "".join(
        f"""<details class="qa long" id="u{n}-lq-{i + 1}"><summary><span class="q-no">{i + 1}</span>{''.join(f'<span class="part">{rich(p)}</span>' for p in as_list(q['q']))}</summary>
          <div class="answer"><p class="tag">Points to cover</p><ul>{''.join(f'<li>{rich(p)}</li>' for p in q['points'])}</ul>
          <p class="study">Study: {', '.join(f'<a href="{topic_file(by_id(unit, tid))}">{esc(tid)} {esc(by_id(unit, tid)["title"])}</a>' for tid in q['topics'])}</p></div></details>"""
        for i, q in enumerate(unit.get("long_questions", []))
    )
    cards = "".join(
        f'<li><button type="button" class="flash" aria-pressed="false"><span class="front">{rich(t["term"])}</span><span class="back">{rich(t["def"])}</span></button></li>'
        for t in unit_terms(unit)
    )
    labs = [lab for t in unit["topics"] for lab in t.get("labs", [])]
    seen: set[str] = set()
    lab_items = ""
    for lab in labs:
        if lab["href"] in seen:
            continue
        seen.add(lab["href"])
        lab_items += f'<li><a class="lab" href="{prefix}{esc(lab["href"])}"><b>{esc(lab["title"])}</b><span>{esc(lab.get("note", "Interactive practice"))}</span></a></li>'
    labs_html = f"""<section class="block" id="labs" aria-labelledby="lab-h"><h2 id="lab-h">Interactive labs</h2>
      <p class="lead-in">Optional practice that applies the unit to realistic decisions.</p><ul class="lab-grid">{lab_items}</ul></section>""" if lab_items else ""
    return f"""{head(f"Unit {roman(n)} · {unit['title']} | U21CAX01", unit['overview'][0], prefix)}
{topbar(prefix, crumbs)}
  <main id="main" class="hub" data-unit="{n}">
    <section class="hub-hero u{n}">
      <p class="eyebrow">Unit {roman(n)} · {esc(unit['co'])}</p>
      <h1>{esc(unit['title'])}</h1>
      {''.join(f'<p>{rich(p)}</p>' for p in unit['overview'])}
      <ul class="chips"><li><span aria-hidden="true">📖</span> Reading: {STUDY_MATERIAL}, pp. {esc(unit['pages'])}</li>
        <li><span class="done-count" data-unit-count="{n}">0</span> of {len(unit['topics'])} topics revised</li></ul>
      <nav class="jump" aria-label="On this page"><a href="#topics">Topics</a><a href="#cases">Cases</a><a href="#quiz">Unit quiz</a><a href="#two-mark">2-mark answers</a><a href="#long">14-mark questions</a><a href="#terms">Flashcards</a></nav>
    </section>

    <section class="block" id="topics" aria-labelledby="t-h">
      <h2 id="t-h">Syllabus topics</h2>
      <p class="lead-in">Work through them in order after reading the unit. Each page takes about 10 minutes.</p>
      <ol class="topic-list">{topics}</ol>
    </section>

    <section class="block" id="cases" aria-labelledby="c-h">
      <h2 id="c-h">Case bank</h2>
      <p class="lead-in">Short Indian cases to quote in answers. Name the case, state what it shows, and link it to the concept.</p>
      <ul class="case-grid">{cases}</ul>
    </section>

    <section class="block check" id="quiz" aria-labelledby="q-h">
      <h2 id="q-h">Unit quiz · {len(unit['quiz'])} questions</h2>
      <p class="lead-in">Part A style questions from the course question bank. Pick an answer to see why it is right or wrong.</p>
      <ol class="mcqs" data-set="unit-{n}">{quiz}</ol>
      <p class="set-result" aria-live="polite"></p>
      <button type="button" class="reset" data-reset="unit-{n}">Reset quiz</button>
    </section>

    <section class="block" id="two-mark" aria-labelledby="s-h">
      <h2 id="s-h">2-mark questions with model answers</h2>
      <p class="lead-in">Write your answer first. A 2-mark answer needs a precise definition or two clear points, not a paragraph.</p>
      {short}
    </section>

    <section class="block" id="long" aria-labelledby="l-h">
      <h2 id="l-h">14-mark questions</h2>
      <p class="lead-in">Plan before you write: an introduction, the points below as headings with explanation and an example, then a short conclusion. Open a question to see the points to cover.</p>
      {long_items}
    </section>

    <section class="block" id="terms" aria-labelledby="f-h">
      <h2 id="f-h">Key-term flashcards</h2>
      <p class="lead-in">Say the definition aloud, then tap the card to check.</p>
      <ul class="flash-grid">{cards}</ul>
    </section>

    {labs_html}

    <nav class="pager" aria-label="Unit navigation">
      {f'<a class="prev" href="../unit-{n - 1}/index.html"><small>Previous unit</small><b>Unit {roman(n - 1)}</b></a>' if n > 1 else '<a class="prev" href="../../index.html"><small>Back to</small><b>Course home</b></a>'}
      {f'<a class="next" href="../unit-{n + 1}/index.html"><small>Next unit</small><b>Unit {roman(n + 1)}</b></a>' if n < 5 else '<a class="next" href="../../index.html"><small>Back to</small><b>Course home</b></a>'}
    </nav>
  </main>
{footer(prefix)}"""


def by_id(unit: dict, tid: str) -> dict:
    for topic in unit["topics"]:
        if topic["id"] == tid:
            return topic
    raise KeyError(f"Unknown topic {tid} in unit {unit['number']}")


def unit_terms(unit: dict) -> list[dict]:
    seen: set[str] = set()
    terms = []
    for topic in unit["topics"]:
        for term in topic.get("terms", []):
            key = term["term"].lower()
            if key not in seen:
                seen.add(key)
                terms.append(term)
    return terms


def home_page(units: list[dict]) -> str:
    tabs = "".join(
        f"""<button id="tab-u{u['number']}" role="tab" aria-selected="{str(i == 0).lower()}" aria-controls="panel-u{u['number']}"{'' if i == 0 else ' tabindex="-1"'}>
          <span class="unit-no">UNIT {u['number']:02d}</span><b>{esc(u['tagline'])}</b><small>{len(u['topics'])} topics · {esc(u['co_short'])}</small></button>"""
        for i, u in enumerate(units)
    )
    panels = ""
    for i, u in enumerate(units):
        n = u["number"]
        items = "".join(
            f"""<li><a href="learn/unit-{n}/{topic_file(t)}" data-progress="{esc(t['id'])}"><span>{esc(t['id'])}</span><div><b>{esc(t['title'])}</b><small>{esc(t['outcome'])}</small></div></a></li>"""
            for t in u["topics"]
        )
        panels += f"""
      <section id="panel-u{n}" class="unit-panel" role="tabpanel" aria-labelledby="tab-u{n}"{'' if i == 0 else ' hidden'}>
        <div class="unit-intro"><div><p class="eyebrow">{esc(u['co'])}</p><h2>{esc(u['title'])}</h2><p>{esc(u['overview'][0])}</p></div>
          <div class="unit-actions"><a class="unit-start" href="learn/unit-{n}/index.html">Unit {roman(n)} overview →</a><a class="unit-quiz" href="learn/unit-{n}/index.html#quiz">Unit quiz</a></div></div>
        <ol class="topic-grid">{items}</ol>
      </section>"""
    total = sum(len(u["topics"]) for u in units)
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <meta name="description" content="Revision and practice hub for U21CAX01 Entrepreneurship Development and Startup">
  <meta name="theme-color" content="#07365d">
  <title>U21CAX01 · Entrepreneurship Learning Studio</title>
  <link rel="icon" href="assets/favicon.svg" type="image/svg+xml">
  <link rel="stylesheet" href="assets/home.css?v=2">
{GTAG}
</head>
<body>
  <a class="skip-link" href="#learning-path">Skip to learning path</a>
  <header class="site-head">
    <a class="identity" href="./" aria-label="U21CAX01 course home"><span>U21</span><b>Entrepreneurship Learning Studio</b></a>
    <nav aria-label="Course navigation"><a href="#learning-path">Units</a><a href="#how-to-use">How to use</a></nav>
  </header>

  <main>
    <section class="hero" aria-labelledby="hero-title">
      <div class="hero-copy">
        <p class="eyebrow">U21CAX01 · Entrepreneurship Development and Startup</p>
        <h1 id="hero-title">Read the material. Then make it stick here.</h1>
        <p class="hero-lead">{total} revision pages, one for every syllabus topic, with key ideas, Indian cases, quick checks and exam practice for all five units.</p>
        <div class="hero-actions"><a class="primary-action" href="#learning-path">Choose a unit <span aria-hidden="true">↓</span></a><span>Read · Revise · Check · Practise</span></div>
      </div>
      <div class="hero-visual" aria-label="Course journey from opportunity to funding">
        <img src="assets/images/hero-venture-lab.webp" width="1400" height="467" alt="Students developing an entrepreneurial venture through research, prototyping and presentation">
        <div class="journey-tag tag-one"><b>01</b> Discover</div><div class="journey-tag tag-two"><b>03</b> Plan</div><div class="journey-tag tag-three"><b>05</b> Fund</div>
      </div>
    </section>

    <section id="how-to-use" class="orientation" aria-labelledby="orientation-title">
      <div><p class="eyebrow">How to use this site</p><h2 id="orientation-title">Four steps for each topic</h2></div>
      <ol class="steps-4"><li><b>Read</b><span>Read the topic in the {STUDY_MATERIAL}. Each page tells you where.</span></li><li><b>Revise</b><span>Use the key ideas, terms and case to fix the concept.</span></li><li><b>Check</b><span>Answer the quick check. A tick marks the topic as revised.</span></li><li><b>Practise</b><span>Write 2-mark answers, then try the unit quiz and 14-mark plans.</span></li></ol>
    </section>

    <section id="learning-path" class="learning-path" aria-labelledby="path-title">
      <div class="section-head"><div><p class="eyebrow">All five units</p><h2 id="path-title">Choose your unit</h2></div><p>Ticks show topics whose quick check you have completed on this device.</p></div>
      <div class="unit-switcher five" role="tablist" aria-label="Select a course unit">{tabs}
      </div>{panels}
    </section>
  </main>

  <footer>
    <p>U21CAX01 · KPR Institute of Engineering and Technology</p>
    <p>No account or score leaves your browser. Anonymous aggregate usage is measured.</p>
  </footer>
  <script src="assets/home.js?v=2" defer></script>
  <script src="assets/learn.js?v={CSS_VERSION}" defer></script>
</body>
</html>
"""


def load_units() -> list[dict]:
    bank = json.loads((CONTENT / "question-bank.json").read_text(encoding="utf-8"))
    units = []
    for path in sorted(CONTENT.glob("unit-*.yml")):
        unit = yaml.safe_load(path.read_text(encoding="utf-8"))
        for index, topic in enumerate(unit["topics"], start=1):
            topic["index"] = index
        part_a = bank[unit["number"] - 1]["A"]
        for i, item in enumerate(unit.get("quiz", [])):
            if "options" not in item:
                item["q"] = part_a[i]["q"]
                item["options"] = [part_a[i]["opts"][k] for k in "abcd"]
        units.append(unit)
    return units


def check(units: list[dict]) -> list[str]:
    errors = []
    required = ("id", "slug", "title", "outcome", "page", "summary", "key_points", "example", "case", "mistakes", "terms", "check", "short_answers")
    for unit in units:
        for key in ("number", "title", "co", "co_short", "tagline", "overview", "pages", "quiz", "topics"):
            if key not in unit:
                errors.append(f"unit {unit.get('number')}: missing {key}")
        for topic in unit["topics"]:
            for key in required:
                if not topic.get(key):
                    errors.append(f"{topic.get('id')}: missing {key}")
            for q in topic.get("check", []):
                if len(cells(q.get("options", []))) != 4:
                    errors.append(f"{topic['id']}: quick-check question needs 4 options: {q.get('q')}")
            if topic.get("table"):
                width = len(cells(topic["table"]["head"]))
                for row in topic["table"]["rows"]:
                    if len(cells(row)) != width:
                        errors.append(f"{topic['id']}: table row has {len(cells(row))} cells, expected {width}: {row}")
        for i, q in enumerate(unit.get("quiz", []), start=1):
            if len(cells(q.get("options", []))) != 4 or not q.get("why"):
                errors.append(f"unit {unit['number']} quiz {i}: needs 4 options and why")
        for q in unit.get("long_questions", []):
            for tid in q["topics"]:
                try:
                    by_id(unit, tid)
                except KeyError as exc:
                    errors.append(str(exc))
    return errors


def main() -> int:
    units = load_units()
    errors = check(units)
    if errors:
        print("\n".join(errors))
        return 1
    for unit in units:
        folder = OUT / f"unit-{unit['number']}"
        folder.mkdir(parents=True, exist_ok=True)
        for old in folder.glob("*.html"):
            old.unlink()
        (folder / "index.html").write_text(hub_page(unit), encoding="utf-8")
        topics = unit["topics"]
        for i, topic in enumerate(topics):
            prev_t = topics[i - 1] if i else None
            next_t = topics[i + 1] if i + 1 < len(topics) else None
            (folder / topic_file(topic)).write_text(topic_page(unit, topic, prev_t, next_t), encoding="utf-8")
    (ROOT / "index.html").write_text(home_page(units), encoding="utf-8")
    manifest = {
        "course": {
            "code": "U21CAX01",
            "title": "Entrepreneurship Development and Startup",
            "institution": "KPR Institute of Engineering and Technology",
            "audience": "Fifth-semester B.E. open-elective students",
            "live_units": len(units),
            "live_topics": sum(len(u["topics"]) for u in units),
            "privacy": "Anonymous aggregate usage analytics via Google Analytics; quiz progress stays in the learner's browser",
        },
        "units": [
            {
                "number": u["number"],
                "title": u["title"],
                "course_outcome": u["co"],
                "hub": f"learn/unit-{u['number']}/index.html",
                "topics": [[t["id"], t["title"], f"learn/unit-{u['number']}/{topic_file(t)}"] for t in u["topics"]],
                "labs": sorted({lab["href"] for t in u["topics"] for lab in t.get("labs", [])}),
            }
            for u in units
        ],
    }
    (ROOT / "site-manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Built {len(units)} units and {manifest['course']['live_topics']} topic pages.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
