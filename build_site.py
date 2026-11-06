"""Build the static HTML site in site/ from the Markdown chapters in docs/ (plus README).

Run from the handbook root:
    python build_site.py        # rebuilds site/ and verifies chapter references

Requires the 'Markdown' package (pip install Markdown).
"""
import re
import shutil
import sys
from pathlib import Path

try:
    import markdown
except ImportError:
    print("build_site.py needs the 'Markdown' package: pip install Markdown", file=sys.stderr)
    sys.exit(1)

ROOT = Path(__file__).resolve().parent
DOCS = ROOT / "docs"
SITE = ROOT / "site"

CHAPTERS = [
    ("01-start-here.md", "Start Here"),
    ("02-safety-first.md", "Safety First"),
    ("03-mass-rename.md", "Mass Renames"),
    ("04-csv-join-split.md", "CSVs"),
    ("05-pdf-join-split.md", "PDFs"),
    ("06-image-resize.md", "Images"),
    ("07-format-conversions.md", "Other Formats"),
    ("08-folder-rules.md", "Folder Rules"),
    ("09-ai-copilot.md", "AI Co-Pilot"),
    ("10-cookbook.md", "Cookbook"),
]

CSS = """
:root { --ink:#1f2430; --soft:#5a6270; --line:#e4e7ee; --paper:#ffffff; --wash:#f6f8fb; --accent:#2b6cb0; }
* { box-sizing:border-box; }
body { margin:0; font:17px/1.65 Georgia, 'Times New Roman', serif; color:var(--ink); background:var(--paper); }
.layout { display:flex; max-width:1080px; margin:0 auto; padding:2rem 1rem; gap:2.5rem; }
nav { flex:0 0 190px; position:sticky; top:2rem; align-self:flex-start; font-family:Verdana, sans-serif; }
nav h1 { font-size:1.05rem; margin:0 0 .4rem; }
nav p.brand { font-size:.8rem; color:var(--soft); margin:.2rem 0 1rem; }
nav ol { list-style:none; margin:0; padding:0; font-size:.9rem; }
nav ol a { display:block; padding:.35rem .5rem; color:var(--soft); text-decoration:none; border-left:3px solid transparent; }
nav ol a:hover { color:var(--accent); }
nav ol a.active { border-left-color:var(--accent); color:var(--accent); font-weight:bold; }
main { flex:1; min-width:0; max-width:700px; }
main h1, main h2, main h3, main h4 { line-height:1.25; font-family:Verdana, sans-serif; }
main h1 { font-size:1.9rem; border-bottom:2px solid var(--line); padding-bottom:.4rem; }
main h2 { font-size:1.35rem; margin-top:2rem; }
h3 { font-size:1.1rem; }
p, li { max-width:66ch; }
a { color:var(--accent); }
code { font-family:ui-monospace, 'Cascadia Code', Consolas, Menlo, monospace; font-size:.85em; background:var(--wash); border:1px solid var(--line); border-radius:3px; padding:.08em .35em; }
pre { background:#22262e; color:#e8eaee; padding:1rem 1.2rem; border-radius:8px; overflow-x:auto; }
pre code { background:none; border:none; color:inherit; padding:0; font-size:.88em; }
table { border-collapse:collapse; margin:1.2rem 0; font-family:Verdana, sans-serif; font-size:.85rem; }
th, td { border:1px solid var(--line); padding:.45em .8em; text-align:left; vertical-align:top; }
th { background:var(--wash); }
blockquote { margin:1.2rem 0; padding:.6rem 1.2rem; border-left:4px solid var(--accent); background:var(--wash); }
blockquote p { max-width:none; }
footer { border-top:1px solid var(--line); margin-top:2.5rem; padding:1.2rem 0; font-family:Verdana, sans-serif; font-size:.8rem; color:var(--soft); }
@media (max-width:800px){ .layout { flex-direction:column; } nav { position:static; width:100%; } }
"""


def md_to_html(md_text: str) -> str:
    return markdown.markdown(md_text, extensions=["fenced_code", "tables", "md_in_html"])


def head(page_title: str, site_title: str) -> str:
    return (
        '<!DOCTYPE html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        f"<title>{page_title} — {site_title}</title>\n"
        f"<style>{CSS}</style>\n</head>\n<body>\n"
    )


def nav(active: str, site_title: str) -> str:
    items = [
        f'<a href="index.html"{" class=active" if active == "index" else ""}>Home</a>'
    ]
    items += [
        '<a href="{}.html"{}>{}</a>'.format(
            name[:-3],
            ' class="active"' if name[:-3] == active else "",
            label,
        )
        for name, label in CHAPTERS
    ]
    return (
        f'<nav>\n<h1>{site_title}</h1>\n<p class="brand">Asdale Dynamics, LLC</p>\n<ol>\n'
        + "\n".join(items)
        + '\n</ol>\n</nav>\n'
    )


def footnote() -> str:
    return (
        "<footer>The Everyday Batch-File Automation Handbook &middot; "
        "by Asdale Dynamics, LLC &middot; MIT License &middot; "
        "Education only; never medical or compliance advice.</footer>\n</main>\n</div>\n</body>\n</html>\n"
    )


CHECKED = re.compile(r"scripts/([A-Za-z0-9_]+\.py)")


def main() -> int:
    if SITE.exists():
        shutil.rmtree(SITE)
    SITE.mkdir()
    checked = {}
    for doc_path in sorted(DOCS.glob("*.md") ) + [ROOT / "README.md"]:
        text = doc_path.read_text(encoding="utf-8")
        checked.setdefault(doc_path.name, set()).update(CHECKED.findall(text))
    missing = sorted(s for names in checked.values() for s in names if not (ROOT / "scripts" / s).exists())
    if missing:
        print(f"Docs reference scripts that do not exist: {missing}", file=sys.stderr)
        return 2

    title = "Everyday Batch-File Automation Handbook"
    (SITE / "index.html").write_text(
        head("Home", title)
        + '<div class="layout">\n' + nav("index", title) + "<main>\n"
        + md_to_html((ROOT / "README.md").read_text(encoding="utf-8"))
        + footnote(),
        encoding="utf-8",
    )
    for name, label in CHAPTERS:
        page = name[:-3]
        (SITE / f"{page}.html").write_text(
            head(label, title)
            + '<div class="layout">\n' + nav(page, title) + "<main>\n"
            + md_to_html((DOCS / name).read_text(encoding="utf-8"))
            + footnote(),
            encoding="utf-8",
        )
    pages = len(list(SITE.glob("*.html")))
    print(f"Built site/ with {pages} pages from docs/ and README.md.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
