#!/usr/bin/env python3
"""Search job boards for a stack keyword and list the hiring companies.

Usage:
    python discover_companies.py --keyword django --city Berlin
    python discover_companies.py --keyword django --city Berlin \
        --watchlist results/company-watch/watchlist.md -o candidates.md

Searches LinkedIn (public guest search), StepStone, XING, WeAreDevelopers, and
the Arbeitnow API, groups postings by company, and splits companies into new
candidates and companies already on the watchlist (any status). Candidates are
leads only: board searches match the keyword anywhere in a posting, and some
hits are recruiters, so verify each company before adding it.
Uses only the Python standard library and curl.
"""
import argparse
import html
import json
import re
import subprocess
import sys
import time
from datetime import date
from pathlib import Path
from urllib.parse import quote, urlsplit, urlunsplit

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0 Safari/537.36")
LEGAL_SUFFIXES = r"\b(gmbh|ag|se|kg|ug|gbr|ohg|inc|ltd|llc|bv|sas|sa|oy|ab|co|haftungsbeschränkt)\b"


def fetch(url, timeout=25):
    """Return (http_code, body) via curl."""
    completed = subprocess.run(
        ["curl", "-sL", "--max-time", str(timeout), "-A", UA,
         "-w", "\n@@code@@:%{http_code}", url],
        capture_output=True, text=True,
    )
    body, _, code = completed.stdout.rpartition("\n@@code@@:")
    try:
        return int(code), body
    except ValueError:
        return 0, completed.stdout


def _text(fragment):
    return html.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", fragment))).strip()


def _json_str(value):
    """Decode a JSON string literal body captured by a regex."""
    return json.loads(f'"{value}"')


def _strip_query(url):
    parts = urlsplit(url)
    return urlunsplit((parts.scheme, parts.netloc, parts.path, "", ""))


def search_linkedin(keyword, city, pages):
    postings = []
    for page in range(pages):
        url = ("https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"
               f"?keywords={quote(keyword)}&location={quote(city)}&start={page * 10}")
        code, body = fetch(url)
        if code == 429:  # rate limited: wait once, then retry
            time.sleep(15)
            code, body = fetch(url)
        if code != 200:
            if page == 0:
                raise RuntimeError(f"HTTP {code}")
            break
        cards = body.split("<li>")[1:]
        if not cards:
            break
        for card in cards:
            title = re.search(r'base-search-card__title">(.*?)</h3>', card, re.S)
            company = re.search(r'base-search-card__subtitle">(.*?)</h4>', card, re.S)
            link = re.search(r'base-card__full-link[^>]*href="([^"]+)"', card)
            loc = re.search(r'job-search-card__location">(.*?)</span>', card, re.S)
            posted = re.search(r'<time[^>]*datetime="([^"]+)"', card)
            if title and company and link:
                postings.append({"company": _text(company.group(1)), "title": _text(title.group(1)),
                                 "url": _strip_query(html.unescape(link.group(1))),
                                 "location": _text(loc.group(1)) if loc else "",
                                 "posted": posted.group(1) if posted else ""})
        time.sleep(2)
    return postings


def search_stepstone(keyword, city):
    code, body = fetch(f"https://www.stepstone.de/jobs/{quote(keyword.lower())}/in-{quote(city.lower())}")
    if code != 200:
        raise RuntimeError(f"HTTP {code}")
    postings = []
    for m in re.finditer(r'"title":"((?:[^"\\]|\\.)*)","url":"((?:[^"\\]|\\.)*)"(.{0,4000}?)"companyName":"((?:[^"\\]|\\.)*)"',
                         body, re.S):
        title, url, middle, company = m.groups()
        loc = re.search(r'"location":"((?:[^"\\]|\\.)*)"', middle)
        posted = re.search(r'"datePosted":"([^"]{10})', middle)
        postings.append({"company": _json_str(company), "title": _json_str(title),
                         "url": _strip_query(_json_str(url)),
                         "location": _json_str(loc.group(1)) if loc else "",
                         "posted": posted.group(1) if posted else ""})
    return postings


def search_xing(keyword, city):
    code, body = fetch(f"https://www.xing.com/jobs/search?keywords={quote(keyword)}&location={quote(city)}")
    if code != 200:
        raise RuntimeError(f"HTTP {code}")
    postings = []
    for m in re.finditer(r'"__typename":"VisibleJob".*?"url":"((?:[^"\\]|\\.)*)","title":"((?:[^"\\]|\\.)*)",'
                         r'"refreshedAt":"([^"]{10}).*?"city":"((?:[^"\\]|\\.)*)".*?"companyInfo":\{(.*?)\},"salary"',
                         body, re.S):
        url, title, posted, loc, info = m.groups()
        name = (re.search(r'"companyNameOverride":"((?:[^"\\]|\\.)*)"', info)
                or re.search(r'"companyName":"((?:[^"\\]|\\.)*)"', info))
        if name:
            postings.append({"company": _json_str(name.group(1)), "title": _json_str(title),
                             "url": _json_str(url), "location": _json_str(loc), "posted": posted})
    return postings


def search_wearedevelopers(keyword, city):
    code, body = fetch(f"https://www.wearedevelopers.com/en/jobs/ls/germany/{quote(city.lower())}/{quote(keyword.lower())}")
    if code != 200:
        raise RuntimeError(f"HTTP {code}")
    postings = []
    for m in re.finditer(r'href="(/jobs/ext/[^"]+)">(.*?)</a>', body, re.S):
        path, inner = m.groups()
        title = re.search(r"<h3[^>]*>(.*?)</h3>", inner, re.S)
        rows = re.findall(r'<div class="truncate[^"]*">(.*?)</div>', inner, re.S)
        posted = re.search(r'<span class="font-display">(.*?)</span>', inner, re.S)
        if title and rows:
            postings.append({"company": _text(rows[0]), "title": _text(title.group(1)),
                             "url": "https://www.wearedevelopers.com" + path,
                             "location": _text(rows[1]) if len(rows) > 1 else "",
                             "posted": _text(posted.group(1)) if posted else ""})
    return postings


def search_arbeitnow(keyword, city, pages=3):
    postings = []
    for page in range(1, pages + 1):
        code, body = fetch(f"https://www.arbeitnow.com/api/job-board-api?page={page}")
        if code != 200:
            if page == 1:
                raise RuntimeError(f"HTTP {code}")
            break
        for j in json.loads(body).get("data", []):
            text = " ".join([j["title"], " ".join(j.get("tags", [])), j.get("description", "")]).lower()
            if keyword.lower() in text and city.lower() in j.get("location", "").lower():
                postings.append({"company": j["company_name"], "title": j["title"], "url": j["url"],
                                 "location": j["location"],
                                 "posted": date.fromtimestamp(j["created_at"]).isoformat()})
    return postings


def normalize(name):
    """Comparable company key: drop parentheses, legal suffixes, and punctuation."""
    name = re.sub(r"\(.*?\)", " ", name.lower())
    name = name.replace("&", " ")
    name = re.sub(LEGAL_SUFFIXES, " ", name)
    return re.sub(r"\s+", " ", re.sub(r"[^\w\s]", " ", name)).strip()


def aliases(name):
    """Keys for a watchlist name: the name itself and any name in parentheses ("Salfy (SalLab GmbH)")."""
    keys = [normalize(name)] + [normalize(inner) for inner in re.findall(r"\((.*?)\)", name)]
    return [k for k in keys if k]


def same_company(a, b):
    """Equal keys ignoring spaces ("pland" ~ "plan d"), or a whole-word prefix ("verbi" ~ "verbi software")."""
    if not a or not b:
        return False
    if a.replace(" ", "") == b.replace(" ", ""):
        return True
    short, long_ = sorted((a, b), key=len)
    return long_.startswith(short + " ")


def load_watchlist(path):
    """Rows from every table with a Company column: the watchlist and the Excluded Leads table."""
    if not path or not Path(path).exists():
        return []
    rows, header = [], None
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        if not line.strip().startswith("|"):
            header = None
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if header is None:
            if "Company" in cells:
                header = cells
            continue
        if all(set(c) <= set("-: ") for c in cells):
            continue
        row = dict(zip(header, cells))
        # Excluded Leads rows have no Status column.
        rows.append((row["Company"], row.get("Status") or "excluded lead", aliases(row["Company"])))
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--keyword", default="django")
    parser.add_argument("--city", default="Berlin")
    parser.add_argument("--watchlist", help="Watchlist Markdown file to compare against")
    parser.add_argument("--linkedin-pages", type=int, default=5, help="LinkedIn result pages (10 postings each)")
    parser.add_argument("-o", "--output", help="Write the Markdown report here instead of stdout")
    args = parser.parse_args()

    searches = {
        "LinkedIn": lambda: search_linkedin(args.keyword, args.city, args.linkedin_pages),
        "StepStone": lambda: search_stepstone(args.keyword, args.city),
        "XING": lambda: search_xing(args.keyword, args.city),
        "WeAreDevelopers": lambda: search_wearedevelopers(args.keyword, args.city),
        "Arbeitnow": lambda: search_arbeitnow(args.keyword, args.city),
    }
    companies, source_counts, errors = {}, {}, {}
    for source, run in searches.items():
        try:
            postings = run()
        except Exception as err:
            errors[source] = str(err)
            continue
        source_counts[source] = len(postings)
        for p in postings:
            key = normalize(p["company"])
            if not key:
                continue
            match = next((k for k in companies if same_company(k, key)), None)
            entry = companies.setdefault(match or key, {"names": set(), "sources": set(), "postings": []})
            entry["names"].add(p["company"])
            entry["sources"].add(source)
            if p["url"] not in {q["url"] for q in entry["postings"]}:
                entry["postings"].append(p)

    watch = load_watchlist(args.watchlist)
    new, known = [], []
    for key, entry in companies.items():
        hit = next(((name, status) for name, status, keys in watch
                    if any(same_company(k, key) for k in keys)), None)
        (known if hit else new).append((key, entry, hit))
    new.sort(key=lambda t: (-len(t[1]["sources"]), -len(t[1]["postings"]), t[0]))
    known.sort(key=lambda t: t[2][0].lower())

    lines = [f"# Company Discovery - {args.keyword} / {args.city} - {date.today().isoformat()}", "",
             "**Sources**: " + ", ".join(f"{s} ({n} postings)" for s, n in source_counts.items()),
             f"**Companies found**: {len(new) + len({h[0] for _, _, h in known})} "
             f"({len(new)} new, {len({h[0] for _, _, h in known})} already on the watchlist)", ""]
    if errors:
        lines += ["**Source errors**: " + "; ".join(f"{s}: {e}" for s, e in errors.items()), ""]
    lines += ["## New Candidates", "",
              "Leads only. Confirm the keyword is a main stack item (not a nice-to-have) and that the company "
              "is not a recruiter before adding it.", "",
              "| Company | Sources | Postings | Example Title | Example URL |",
              "|---------|---------|----------|---------------|-------------|"]
    for key, entry, _ in new:
        example = next((p for p in entry["postings"] if args.keyword.lower() in p["title"].lower()),
                       entry["postings"][0])
        lines.append(f"| {' / '.join(sorted(entry['names']))} | {', '.join(sorted(entry['sources']))} | "
                     f"{len(entry['postings'])} | {example['title']} | <{example['url']}> |")
    lines += ["", "## Already on the Watchlist", "",
              "| Watchlist Company | Status | Board Names | Postings |",
              "|-------------------|--------|-------------|----------|"]
    merged = {}  # several board names can map to one watchlist row
    for _, entry, (name, status) in known:
        row = merged.setdefault(name, {"status": status, "names": set(), "urls": set()})
        row["names"] |= entry["names"]
        row["urls"] |= {p["url"] for p in entry["postings"]}
    for name, row in merged.items():
        lines.append(f"| {name} | {row['status']} | {' / '.join(sorted(row['names']))} | {len(row['urls'])} |")
    report = "\n".join(lines) + "\n"

    if args.output:
        Path(args.output).write_text(report, encoding="utf-8")
    else:
        print(report)
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
