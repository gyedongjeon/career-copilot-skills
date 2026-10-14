#!/usr/bin/env python3
"""List current openings for every company in a company-watch watchlist.

Usage:
    python check_watchlist.py results/company-watch/watchlist.md
    python check_watchlist.py watchlist.md --state seen.json -o report.md
    python check_watchlist.py watchlist.md --keywords python,backend --location berlin

Reads the watchlist Markdown table, fetches open postings from each company's
public ATS job feed (Greenhouse, Lever, Ashby, Personio, JOIN, Workable,
SmartRecruiters), keeps postings
whose title and location match the filters, and marks postings that were not
in the state file as NEW. Companies on another ATS are listed for manual checks.
Uses only the Python standard library and curl.
"""
import argparse
import json
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor
from datetime import date, datetime, timezone
from pathlib import Path

# Watchlist companies already use Django, so any engineering title is relevant
# unless it is clearly outside a backend profile.
DEFAULT_KEYWORDS = "engineer,developer,entwickler,programmer"
DEFAULT_EXCLUDE = ("intern,internship,praktikum,werkstudent,working student,student,"
                   "ios,android,mobile,frontend,front-end,hardware,embedded,firmware,"
                   "electrical,production,c++,qt,"
                   "design engineer,sales engineer,solutions engineer,support engineer,field engineer")
DEFAULT_LOCATIONS = "berlin"
REMOTE_TERMS = ["remote", "homeoffice", "home office"]
# A remote posting counts only if it also names one of these regions.
DEFAULT_REMOTE_REGIONS = "europe,european union,eu,emea,germany,deutschland,berlin,cet"
SKIP_STATUSES = {"excluded"}


def fetch(url, timeout=20):
    """Return (http_code, body) via curl; curl handles TLS more reliably than urllib here."""
    completed = subprocess.run(
        ["curl", "-sL", "--max-time", str(timeout), "-A", "Mozilla/5.0",
         "-w", "\n@@code@@:%{http_code}", url],
        capture_output=True, text=True,
    )
    body, _, code = completed.stdout.rpartition("\n@@code@@:")
    try:
        return int(code), body
    except ValueError:
        return 0, completed.stdout


def _iso_date(value):
    if not value:
        return ""
    if isinstance(value, (int, float)):  # Lever uses epoch milliseconds
        return datetime.fromtimestamp(value / 1000, tz=timezone.utc).strftime("%Y-%m-%d")
    return str(value)[:10]


def jobs_greenhouse(slug):
    code, body = fetch(f"https://boards-api.greenhouse.io/v1/boards/{slug}/jobs")
    if code != 200:
        raise RuntimeError(f"HTTP {code}")
    return [{"title": j["title"], "location": (j.get("location") or {}).get("name", ""),
             "url": j["absolute_url"], "posted": _iso_date(j.get("first_published") or j.get("updated_at"))}
            for j in json.loads(body)["jobs"]]


def jobs_lever(slug):
    code, body = fetch(f"https://api.lever.co/v0/postings/{slug}?mode=json")
    if code != 200:
        raise RuntimeError(f"HTTP {code}")
    jobs = []
    for j in json.loads(body):
        cats = j.get("categories") or {}
        locs = cats.get("allLocations") or [cats.get("location", "")]
        jobs.append({"title": j["text"], "location": ", ".join(filter(None, locs + [j.get("workplaceType", "")])),
                     "url": j["hostedUrl"], "posted": _iso_date(j.get("createdAt"))})
    return jobs


def jobs_ashby(slug):
    code, body = fetch(f"https://api.ashbyhq.com/posting-api/job-board/{slug}")
    if code != 200:
        raise RuntimeError(f"HTTP {code}")
    jobs = []
    for j in json.loads(body)["jobs"]:
        if not j.get("isListed", True):
            continue
        locs = [j.get("location", "")] + [s.get("location", "") for s in j.get("secondaryLocations") or []]
        if j.get("isRemote"):
            locs.append("Remote")
        jobs.append({"title": j["title"], "location": ", ".join(filter(None, locs)),
                     "url": j["jobUrl"], "posted": _iso_date(j.get("publishedAt"))})
    return jobs


def jobs_personio(slug):
    code, body = fetch(f"https://{slug}.jobs.personio.de/xml")
    if code != 200:
        raise RuntimeError(f"HTTP {code}")
    jobs = []
    for p in ET.fromstring(body).iter("position"):
        offices = [p.findtext("office", "")] + [o.text or "" for o in p.iter("additionalOffice")]
        jobs.append({"title": p.findtext("name", ""), "location": ", ".join(filter(None, offices)),
                     "url": f"https://{slug}.jobs.personio.de/job/{p.findtext('id')}",
                     "posted": _iso_date(p.findtext("createdAt"))})
    return jobs


def jobs_join(slug):
    code, body = fetch(f"https://join.com/companies/{slug}")
    if code != 200:
        raise RuntimeError(f"HTTP {code}")
    m = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', body, re.S)
    if not m:
        raise RuntimeError("JOIN page data not found")
    items = _find_join_items(json.loads(m.group(1)))
    if items is None:
        raise RuntimeError("JOIN job list not found")
    jobs = []
    for j in items:
        city = (j.get("city") or {}).get("cityName", "")
        remote = "Remote" if j.get("workplaceType") == "REMOTE" else ""
        jobs.append({"title": j["title"], "location": ", ".join(filter(None, [city, remote])),
                     "url": f"https://join.com/companies/{slug}/{j['idParam']}",
                     "posted": _iso_date(j.get("createdAt"))})
    return jobs


def jobs_workable(slug):
    code, body = fetch(f"https://apply.workable.com/api/v1/widget/accounts/{slug}")
    if code != 200:
        raise RuntimeError(f"HTTP {code}")
    jobs = []
    for j in json.loads(body).get("jobs", []):
        locs = [", ".join(filter(None, [l.get("city"), l.get("country")])) for l in j.get("locations") or []]
        if j.get("telecommuting"):
            locs.append("Remote")
        jobs.append({"title": j["title"], "location": ", ".join(filter(None, locs)),
                     "url": j["url"], "posted": _iso_date(j.get("published_on") or j.get("created_at"))})
    return jobs


def jobs_smartrecruiters(slug):
    jobs, offset = [], 0
    while True:
        code, body = fetch(f"https://api.smartrecruiters.com/v1/companies/{slug}/postings?limit=100&offset={offset}")
        if code != 200:
            raise RuntimeError(f"HTTP {code}")
        data = json.loads(body)
        for j in data.get("content", []):
            loc = j.get("location") or {}
            parts = [loc.get("fullLocation", "")] + (["Remote"] if loc.get("remote") else [])
            # The list endpoint has no public URL; this short form resolves to the posting page.
            jobs.append({"title": j["name"], "location": ", ".join(filter(None, parts)),
                         "url": f"https://jobs.smartrecruiters.com/{slug}/{j['id']}",
                         "posted": _iso_date(j.get("releasedDate"))})
        offset += len(data.get("content", []))
        if not data.get("content") or offset >= data.get("totalFound", 0):
            return jobs


def _find_join_items(node):
    """Locate the {"jobs": {"items": [...]}} list inside JOIN's Next.js page data."""
    if isinstance(node, dict):
        jobs = node.get("jobs")
        if isinstance(jobs, dict) and isinstance(jobs.get("items"), list):
            return jobs["items"]
        children = node.values()
    elif isinstance(node, list):
        children = node
    else:
        return None
    for child in children:
        found = _find_join_items(child)
        if found is not None:
            return found
    return None


FETCHERS = {
    "greenhouse": jobs_greenhouse,
    "lever": jobs_lever,
    "ashby": jobs_ashby,
    "personio": jobs_personio,
    "join": jobs_join,
    "workable": jobs_workable,
    "smartrecruiters": jobs_smartrecruiters,
}


def parse_watchlist(path):
    """Parse the first Markdown table whose header contains Company, ATS, and ATS Slug."""
    header, rows = None, []
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line.startswith("|"):
            if header and rows:
                break
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if header is None:
            if {"Company", "ATS", "ATS Slug"} <= set(cells):
                header = cells
            continue
        if all(set(c) <= set("-: ") for c in cells):
            continue
        rows.append(dict(zip(header, cells)))
    if header is None:
        raise SystemExit("Watchlist table with Company, ATS, and ATS Slug columns not found")
    return rows


def matches(text, terms):
    """Whole-word, case-insensitive match of any term ("eu" must not match "seoul")."""
    text = text.lower()
    return any(re.search(rf"(?<![a-z]){re.escape(t)}(?![a-z])", text) for t in terms)


def location_ok(location, locations, remote_regions):
    if not location:
        return True
    if matches(location, locations):
        return True
    return matches(location, REMOTE_TERMS) and matches(location, remote_regions)


def check_company(row, keywords, exclude, locations, remote_regions):
    ats = row.get("ATS", "").strip().lower()
    slug = row.get("ATS Slug", "").strip().strip("`")
    result = {"row": row, "jobs": [], "total": 0, "error": None, "manual": False}
    fetcher = FETCHERS.get(ats)
    if not fetcher or not slug:
        result["manual"] = True
        return result
    try:
        jobs = fetcher(slug)
    except Exception as err:
        result["error"] = str(err)
        return result
    result["total"] = len(jobs)
    result["jobs"] = [j for j in jobs
                      if matches(j["title"], keywords)
                      and not matches(j["title"], exclude)
                      and location_ok(j["location"], locations, remote_regions)]
    return result


def render(results, seen, today):
    lines = [f"# Company Watch Openings - {today}", ""]
    matched = [r for r in results if r["jobs"]]
    new_count = sum(1 for r in matched for j in r["jobs"] if j["url"] not in seen)
    lines += [f"**Companies checked**: {sum(1 for r in results if not r['manual'] and not r['error'])}",
              f"**Companies with matching openings**: {len(matched)}",
              f"**Matching openings**: {sum(len(r['jobs']) for r in matched)} ({new_count} new)", ""]

    for r in matched:
        row = r["row"]
        status = row.get("Status", "")
        flag = f" ({status})" if status and status.lower() != "watch" else ""
        lines += [f"## {row['Company']}{flag}", "",
                  "| New | Title | Location | Posted | URL |",
                  "|-----|-------|----------|--------|-----|"]
        for j in sorted(r["jobs"], key=lambda j: j["posted"], reverse=True):
            new = "NEW" if j["url"] not in seen else ""
            lines.append(f"| {new} | {j['title']} | {j['location']} | {j['posted'] or 'Unknown'} | <{j['url']}> |")
        lines.append("")

    quiet = [r for r in results if not r["jobs"] and not r["manual"] and not r["error"]]
    if quiet:
        lines += ["## No Matching Openings", ""]
        lines += [f"- {r['row']['Company']} ({r['total']} open postings in total)" for r in quiet]
        lines.append("")
    errors = [r for r in results if r["error"]]
    if errors:
        lines += ["## Fetch Errors", ""]
        lines += [f"- {r['row']['Company']} ({r['row'].get('ATS')}: `{r['row'].get('ATS Slug')}`): {r['error']}"
                  for r in errors]
        lines.append("")
    manual = [r for r in results if r["manual"]]
    if manual:
        lines += ["## Manual Check Needed", ""]
        lines += [f"- {r['row']['Company']}: {r['row'].get('Careers URL', '')} (ATS: {r['row'].get('ATS') or 'unknown'})"
                  for r in manual]
        lines.append("")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("watchlist", help="Watchlist Markdown file")
    parser.add_argument("--keywords", default=DEFAULT_KEYWORDS,
                        help="Comma-separated title keywords (whole-word, case-insensitive)")
    parser.add_argument("--exclude", default=DEFAULT_EXCLUDE,
                        help="Comma-separated title terms that drop a posting")
    parser.add_argument("--location", default=DEFAULT_LOCATIONS,
                        help="Comma-separated location terms; postings without a location are kept")
    parser.add_argument("--remote-regions", default=DEFAULT_REMOTE_REGIONS,
                        help="Regions a remote posting must name to be kept")
    parser.add_argument("--state", help="JSON file of previously seen posting URLs; updated after the run")
    parser.add_argument("-o", "--output", help="Write the Markdown report here instead of stdout")
    args = parser.parse_args()

    def terms(value):
        return [k.strip().lower() for k in value.split(",") if k.strip()]

    keywords, exclude = terms(args.keywords), terms(args.exclude)
    locations, remote_regions = terms(args.location), terms(args.remote_regions)
    rows = [r for r in parse_watchlist(args.watchlist)
            if r.get("Status", "").strip().lower() not in SKIP_STATUSES]

    state_path = Path(args.state) if args.state else None
    seen = json.loads(state_path.read_text()) if state_path and state_path.exists() else {}

    with ThreadPoolExecutor(max_workers=8) as pool:
        results = list(pool.map(
            lambda r: check_company(r, keywords, exclude, locations, remote_regions), rows))

    today = date.today().isoformat()
    report = render(results, seen, today)
    if args.output:
        Path(args.output).write_text(report + "\n", encoding="utf-8")
    else:
        print(report)

    if state_path:
        for r in results:
            for j in r["jobs"]:
                seen.setdefault(j["url"], today)
        state_path.write_text(json.dumps(seen, indent=2, ensure_ascii=False) + "\n")

    sys.exit(1 if any(r["error"] for r in results) else 0)


if __name__ == "__main__":
    main()
