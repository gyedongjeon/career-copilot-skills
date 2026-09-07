#!/usr/bin/env python3
"""Render a Markdown resume to a print-ready A4 PDF.

Usage:
    python md_to_pdf.py "resumes/Gyedong Jeon.md"
    python md_to_pdf.py input.md -o output.pdf --fit-pages 2

Requires: pandoc, weasyprint, beautifulsoup4  (see SKILL.md)
"""
import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path

from bs4 import BeautifulSoup

MIN_BASE_PT = 7.6  # below this the text stops being comfortably readable
CSS_PATH = Path(__file__).resolve().parent.parent / "assets" / "resume.css"

# Sections rendered as a "label | value" grid instead of bullets.
GRID_SECTIONS = ("Technical Skills", "Languages")
# Section rendered as one inline run (kept on a single line when it fits).
INLINE_SECTION = "Languages"
# Adjacent short sections placed side by side.
SIDE_BY_SIDE = ("Certifications", "Education")


def run(cmd, **kw):
    return subprocess.run(cmd, check=True, capture_output=True, text=True, **kw)


def markdown_to_html(md_path: Path) -> str:
    md = md_path.read_text(encoding="utf-8")
    md = re.sub(r"\A---\n.*?\n---\n", "", md, flags=re.S)  # drop YAML frontmatter
    return run(["pandoc", "-f", "markdown", "-t", "html5"], input=md).stdout


def structure(html: str) -> str:
    """Turn pandoc's flat output into the resume layout the stylesheet expects."""
    soup = BeautifulSoup(html, "html.parser")

    def tag(name, cls=None, text=None):
        t = soup.new_tag(name)
        if cls:
            t["class"] = cls
        if text is not None:
            t.string = text
        return t

    def has_class(node, name):
        return node is not None and name in (node.get("class") or "")

    # 1. Header: name + role + contact lines in one block.
    h1 = soup.find("h1")
    if h1:
        header = tag("header", "hdr")
        h1.insert_before(header)
        header.append(h1.extract())

        role_p = header.find_next_sibling("p")
        if role_p:
            role = tag("div", "role")
            role.append(BeautifulSoup(role_p.decode_contents(), "html.parser"))
            header.append(role)
            contact_p = role_p.find_next_sibling("p")
            role_p.decompose()
            if contact_p:
                for line in re.split(r"<br\s*/?>", contact_p.decode_contents()):
                    line = line.strip()
                    if not line:
                        continue
                    c = tag("div", "contact")
                    line = line.replace(" | ", " <span class='sep'>|</span> ")
                    c.append(BeautifulSoup(line, "html.parser"))
                    header.append(c)
                contact_p.decompose()

    # 2. Horizontal rules are replaced by the section borders.
    for hr in soup.find_all("hr"):
        hr.decompose()

    # 3. "**Label:** value" bullets -> aligned label/value grid.
    def to_grid(ul):
        grid = tag("div", "grid")
        for li in ul.find_all("li", recursive=False):
            strong = li.find("strong")
            if not strong:
                continue
            label = strong.get_text().rstrip(":")
            strong.decompose()
            value = re.sub(r"^[:\s]+", "", li.decode_contents().lstrip())
            row = tag("div", "grow")
            row.append(tag("div", "k", label))
            v = tag("div", "v")
            v.append(BeautifulSoup(value, "html.parser"))
            row.append(v)
            grid.append(row)
        ul.replace_with(grid)

    for h2 in soup.find_all("h2"):
        if h2.get_text().strip() in GRID_SECTIONS:
            nxt = h2.find_next_sibling()
            if nxt is not None and nxt.name == "ul":
                to_grid(nxt)

    # 4. Job headings: "Company | Title" on one line, dates/location beneath.
    for h3 in soup.find_all("h3"):
        company, _, title = h3.get_text().partition("|")
        h3.clear()
        h3["class"] = "job"
        h3.append(tag("span", "co", company.strip()))
        if title.strip():
            h3.append(tag("span", "ti", title.strip()))
        nxt = h3.find_next_sibling()
        if (nxt is not None and nxt.name == "p" and nxt.find("em")
                and nxt.get_text().strip() == nxt.find("em").get_text().strip()):
            loc, _, dates = nxt.get_text().strip().partition("|")
            meta = tag("span", "meta")
            meta.append(tag("span", "dates", dates.strip()))
            meta.append(tag("span", "loc", loc.strip()))
            h3.append(meta)
            nxt.decompose()

    # 5. "Stack:" lines become a muted footer under each role.
    for node in soup.find_all(["li", "p"]):
        if re.match(r"^\*?(Tech )?Stack:", node.get_text().strip()):
            node["class"] = "stack"

    # 6. Languages -> one inline run.
    for h2 in soup.find_all("h2"):
        if h2.get_text().strip() != INLINE_SECTION:
            continue
        grid = h2.find_next_sibling()
        if not has_class(grid, "grid"):
            continue
        run_div = tag("div", "inline-run")
        for i, row in enumerate(grid.find_all("div", class_="grow")):
            if i:
                run_div.append(tag("span", "dot", "·"))
            item = tag("span", "item")
            item.append(tag("span", "k", row.find("div", class_="k").get_text()))
            v = tag("span", "v")
            v.append(BeautifulSoup(row.find("div", class_="v").decode_contents(), "html.parser"))
            item.append(v)
            run_div.append(item)
        grid.replace_with(run_div)

    # 7. Two short adjacent sections share a row.
    def grab_section(title):
        for h2 in soup.find_all("h2"):
            if h2.get_text().strip() == title:
                nodes, node = [h2], h2.next_sibling
                while node is not None and getattr(node, "name", None) != "h2":
                    nxt = node.next_sibling
                    nodes.append(node)
                    node = nxt
                return nodes
        return None

    left, right = (grab_section(t) for t in SIDE_BY_SIDE)
    if left and right:
        cols = tag("div", "cols")
        left[0].insert_before(cols)
        for nodes in (left, right):
            col = tag("div", "col")
            for node in nodes:
                col.append(node.extract())
            cols.append(col)

    # 8. Only leaf items get orphan/widow control; parents must stay breakable.
    for li in soup.find_all("li"):
        if not li.find("ul"):
            cls = li.get("class") or []
            li["class"] = ([cls] if isinstance(cls, str) else list(cls)) + ["leaf"]

    return soup.decode()


def render(body: str, out_pdf: Path, base_pt: float, work: Path) -> int:
    css = CSS_PATH.read_text(encoding="utf-8")
    css = re.sub(r"font-size: [\d.]+pt;\s+/\* overridden by --base \*/",
                 f"font-size: {base_pt:.2f}pt;", css, count=1)
    html_path = work / "resume.html"
    html_path.write_text(
        f'<!doctype html><html><head><meta charset="utf-8"><style>{css}</style>'
        f"</head><body>{body}</body></html>", encoding="utf-8")
    run(["weasyprint", str(html_path), str(out_pdf)])
    info = run(["pdfinfo", str(out_pdf)]).stdout if shutil.which("pdfinfo") else ""
    m = re.search(r"^Pages:\s+(\d+)", info, re.M)
    return int(m.group(1)) if m else 0


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("input", type=Path, help="Markdown resume")
    ap.add_argument("-o", "--output", type=Path, help="PDF path (default: alongside the input)")
    ap.add_argument("--base", type=float, default=9.6,
                    help="body font size in pt; scales the whole layout (default: 9.6)")
    ap.add_argument("--fit-pages", type=int, metavar="N",
                    help="shrink the layout until it fits in N pages")
    args = ap.parse_args()

    for binary in ("pandoc", "weasyprint"):
        if not shutil.which(binary):
            sys.exit(f"error: `{binary}` not found — see skills/resume-pdf/SKILL.md")

    out = args.output or args.input.with_suffix(".pdf")
    out.parent.mkdir(parents=True, exist_ok=True)
    work = out.parent
    body = structure(markdown_to_html(args.input))

    base = args.base
    pages = render(body, out, base, work)
    if args.fit_pages:
        while pages > args.fit_pages and base - 0.2 >= MIN_BASE_PT:
            base -= 0.2
            pages = render(body, out, base, work)
        if pages > args.fit_pages:
            print(f"warning: still {pages} pages at the minimum size — trim the resume itself",
                  file=sys.stderr)

    (work / "resume.html").unlink(missing_ok=True)
    print(f"{out}  ({pages} page{'s' if pages != 1 else ''}, base {base:.1f}pt)")


if __name__ == "__main__":
    main()
