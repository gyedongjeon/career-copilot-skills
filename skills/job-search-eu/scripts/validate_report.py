#!/usr/bin/env python3
"""Re-check every recommended posting in a job-search-eu report before it is final.

Usage:
    python validate_report.py "results/job-search-eu/2026-10-14_Name_Berlin_search_results.md"

Fails (exit 1) on entries whose Detail URL is malformed, a generic jobs hub,
unresolvable, removed (HTTP 404/410), shows a closure notice, is a JOIN posting
whose embedded status is not ONLINE, or is a LinkedIn posting that the
jobs-guest API reports as closed or expired. A Detail URL that now redirects to
another page is reported as a warning so the link can be updated. Pages that block
automated access or do not mention the saved company/position are reported as
warnings: the agent must rely on its own application-status evidence for those.

Adapted from eu-job-agent (job-search-eu/validate_report.py).
"""
import html
import re
import subprocess
import sys
import unicodedata
import urllib.error
import urllib.request
from pathlib import Path
from urllib.parse import urlparse

# Human-readable closure notices, matched against visible text only.
CLOSED_KEYWORDS = [
    "job no longer available", "position has been filled", "vacancy is closed",
    "page not found", "error 404", "job has expired", "this job has expired",
    "job you are trying to view has expired", "advert has expired", "vacancy has expired",
    "this vacancy has now expired", "no longer accepting", "this job has been removed",
    "job is not active", "this job posting is closed", "this position has been filled",
    "applications closed",
    "keine bewerbungen mehr möglich", "stelle nicht mehr verfügbar", "anzeige geschlossen",
    "nicht mehr aktiv", "abgelaufen", "geschlossen", "stelle besetzt",
    "offre non disponible", "plus d'acceptation de candidatures", "annonce clôturée",
    "offre expirée", "expiré", "clôturé", "poste pourvu",
    "ya no se aceptan solicitudes", "oferta no disponible", "oferta cerrada",
    "puesto cubierto", "expirado",
    "verlopen", "gesloten", "vervuld",
    "scaduto", "chiuso", "terminato",
]

# Auth-wall signals that live inside scripts/JSON, matched against the raw body.
AUTHWALL_KEYWORDS = [
    "sign in to see", "create an account to view",
    "isauthstateblocked\":true", "authstateblocked",
]

# Benign phrases that contain a closure keyword but do not mean the posting is
# closed. A keyword fails the entry only if it remains after removing these.
KEYWORD_EXCEPTIONS = {
    "geschlossen": ["abgeschlossen", "aufgeschlossen"],
    "gesloten": ["aangesloten", "uitgesloten", "opgesloten", "afgesloten"],
    # Italian contract types: "a tempo (in)determinato".
    "terminato": ["indeterminato", "determinato"],
}

JOB_MARKERS = ["description", "requirements", "responsibilities", "qualification",
               "what you will do", "aufgaben", "profil"]

# Path segments that indicate a listing hub rather than a single posting.
GENERIC_HUB_PATHS = {
    "", "jobs", "job", "careers", "career", "karriere", "company/careers", "join-us",
    "work-with-us", "open-positions", "positions", "vacancies", "stellenangebote",
}

DEAD_CODES = {404, 410}

_DNS_ERROR_SIGNS = ("getaddrinfo", "name or service not known",
                    "nodename nor servname", "nxdomain", "name resolution")

# LinkedIn renders the closed banner with JavaScript, so /jobs/view/ pages look
# open when fetched. The jobs-guest API exposes the closed state statically.
LINKEDIN_JOB_RE = re.compile(r"linkedin\.com/jobs/view/[^?#]*?(\d{7,})(?:[/?#]|$)", re.I)
LINKEDIN_GUEST_API = "https://www.linkedin.com/jobs-guest/jobs/api/jobPosting/{job_id}"

_CURL_META_MARK = b"\n@@meta@@:"

# JOIN ships its full i18n dictionary (including "This job is no longer
# available") in every page's scripts, so its posting state is read from the
# embedded job JSON instead: "status":"ONLINE" is open, anything else is not.
# Page bodies are lowercased on fetch, so match and compare in lowercase.
JOIN_STATUS_RE = re.compile(r'"title":"[^"]*","status":"([a-z_]+)"')


def _fold(s):
    """Lowercase and strip diacritics so "Moët" matches "moet"."""
    return "".join(c for c in unicodedata.normalize("NFKD", s.lower())
                   if not unicodedata.combining(c))


def _is_dns_error(err):
    return any(s in str(err).lower() for s in _DNS_ERROR_SIGNS)


def _decode_body(raw, charset=None):
    try:
        return raw.decode(charset or "utf-8", errors="replace").lower()
    except LookupError:
        return raw.decode("utf-8", errors="ignore").lower()


def _fetch_with_urllib(url, timeout=10):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return _decode_body(r.read(), r.headers.get_content_charset()), r.geturl()


def _fetch_with_curl(url, timeout=20):
    """Return (body, final_url, http_code); http_code is 0 if unparseable."""
    completed = subprocess.run(
        ["curl", "-sL", "--http1.1", "--max-time", str(timeout), "-A", "Mozilla/5.0",
         "-w", "\n@@meta@@:%{http_code} %{url_effective}", url],
        capture_output=True,
        check=True,
    )
    raw, sep, tail = completed.stdout.rpartition(_CURL_META_MARK)
    if not sep:
        return _decode_body(completed.stdout), url, 0
    code_str, _, final_url = tail.decode("utf-8", errors="ignore").strip().partition(" ")
    try:
        code = int(code_str)
    except ValueError:
        code = 0
    return _decode_body(raw), final_url.strip() or url, code


def check_format(url):
    """Local checks that need no network access. Return an error string or None."""
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https") or not parsed.netloc:
        return "Not an absolute http(s) URL"
    if url[-1] in ".,)":
        return "Trailing punctuation in URL"
    if parsed.path.strip("/").lower() in GENERIC_HUB_PATHS and not parsed.query:
        return "Generic jobs hub, not a posting detail page"
    if "-inline.html" in parsed.path:
        return "Intermediate inline rendering page"
    return None


def _linkedin_expired_redirect(orig_url, final_url):
    if "linkedin.com/jobs/view/" not in (orig_url or "").lower():
        return None
    f = (final_url or "").lower()
    if "expired_jd_redirect" in f:
        return "Expired: LinkedIn redirected with trk=expired_jd_redirect"
    # authwall is a login block, not an expiry signal.
    if f and "linkedin.com/jobs/view/" not in f and "linkedin.com/authwall" not in f:
        return "Expired or removed: LinkedIn redirected to a generic hub"
    return None


def _same_page(a, b):
    """Compare URLs ignoring scheme, query, fragment, and trailing slash."""
    pa, pb = urlparse(a), urlparse(b)
    return (pa.netloc.lower(), pa.path.rstrip("/")) == (pb.netloc.lower(), pb.path.rstrip("/"))


def _check_page(url, final_url, body, company, position):
    """Shared checks for a fetched page, after HTTP-level failures are ruled out."""
    expired = _linkedin_expired_redirect(url, final_url)
    if expired:
        return False, expired
    if "join.com/" in (final_url or url).lower():
        m = JOIN_STATUS_RE.search(body)
        if m and m.group(1) != "online":
            return False, f"Closed: JOIN posting status {m.group(1).upper()}"
    ok, msg = _validate_body(body, company, position)
    if ok and final_url and not _same_page(url, final_url):
        # Boards such as JOIN repost a role under a new ID and redirect the old one.
        return True, f"WARN redirected to {final_url}; update Detail URL if it is the same role"
    return ok, msg


def _validate_body(body, company, position):
    visible = re.sub(r"<script.*?</script>", " ", body, flags=re.S)
    visible = re.sub(r"<style.*?</style>", " ", visible, flags=re.S)
    for kw in CLOSED_KEYWORDS:
        if kw not in visible:
            continue
        clean = visible
        for benign in KEYWORD_EXCEPTIONS.get(kw, []):
            clean = clean.replace(benign, "")
        if kw in clean:
            return False, f"Closed or dead: '{kw}'"
    for kw in AUTHWALL_KEYWORDS:
        if kw in body:
            return False, f"Login wall hides application state: '{kw}'"

    folded = _fold(html.unescape(body))
    co_ok = bool(company) and _fold(company).split()[0] in folded
    pos_ok = any(_fold(w) in folded for w in position.split() if len(w) > 3)
    if not any(m in body for m in JOB_MARKERS) or not (co_ok and pos_ok):
        # JS-rendered ATS pages often hide content from plain fetches.
        return True, f"WARN content not confirmed (Co:{co_ok}, Pos:{pos_ok}); recheck with a browser"
    return True, "OK"


def _check_linkedin_guest(url, company, position):
    """Return a definitive (ok, msg), or None when the guest API is unreachable."""
    m = LINKEDIN_JOB_RE.search(url)
    if not m:
        return None
    guest_url = LINKEDIN_GUEST_API.format(job_id=m.group(1))
    try:
        body, _, code = _fetch_with_curl(guest_url)
    except Exception:
        return None
    if code in DEAD_CODES:
        return False, f"Dead LinkedIn posting (guest API HTTP {code})"
    if code == 0 or code >= 400:
        return None
    if len(body.strip()) < 100:
        return False, "Dead LinkedIn posting (guest API returned empty)"
    if "closed-job" in body:
        return False, "Closed: LinkedIn 'No longer accepting applications'"
    return _validate_body(body, company, position)


def _check_via_curl(url, company, position, reason):
    try:
        body, final_url, code = _fetch_with_curl(url)
    except Exception as err:
        if _is_dns_error(err):
            return False, f"Unresolvable host: {err}"
        return True, f"WARN unverifiable: page blocked/unreachable ({reason}); rely on recorded application evidence"
    if code in DEAD_CODES:
        return False, f"Dead page (HTTP {code})"
    if code == 0 or code >= 400:
        # Never content-check a bot-challenge body as if it were the posting.
        return True, f"WARN unverifiable: bot protection (HTTP {code}); rely on recorded application evidence"
    return _check_page(url, final_url, body, company, position)


def check_link(url, company, position):
    if not url:
        return False, "Missing Detail URL"
    format_error = check_format(url)
    if format_error:
        return False, format_error
    if "linkedin.com/jobs" in url.lower():
        guest_result = _check_linkedin_guest(url, company, position)
        if guest_result is not None:
            return guest_result
    try:
        body, final_url = _fetch_with_urllib(url)
    except urllib.error.HTTPError as err:
        if err.code in DEAD_CODES:
            return False, f"Dead page (HTTP {err.code})"
        return _check_via_curl(url, company, position, f"HTTP {err.code}")
    except Exception as err:
        if _is_dns_error(err):
            return False, f"Unresolvable host: {err}"
        return _check_via_curl(url, company, position, str(err))
    return _check_page(url, final_url, body, company, position)


def parse_entries(content):
    entries = []
    for m in re.finditer(r"^## (\d+)\.\s+(.+?)\n(.*?)(?=^## |\Z)", content, re.S | re.M):
        num, head, block = m.groups()
        u = re.search(r"\*\*Detail URL\*\*:\s*(.+?)$", block, re.M)
        url = u.group(1).strip().strip("<>") if u else None
        company, position = head.split(" - ", 1) if " - " in head else ("", head)
        entries.append({"num": num, "head": head.strip(), "url": url,
                        "company": company.strip(), "position": position.strip()})
    return entries


def main():
    if len(sys.argv) != 2:
        print(__doc__, file=sys.stderr)
        sys.exit(2)
    path = Path(sys.argv[1])
    entries = parse_entries(path.read_text(encoding="utf-8"))

    all_ok = True
    print(f"\nFinal Validation: {path.name} ({len(entries)} entries)")
    for e in entries:
        ok, msg = check_link(e["url"], e["company"], e["position"])
        icon = "✅" if ok else "❌"
        if ok and msg.startswith("WARN"):
            icon = "⚠️"
        print(f"{icon} #{e['num']} {e['head']}")
        if msg != "OK":
            print(f"  └─ {msg}")
        all_ok = all_ok and ok
    sys.exit(0 if all_ok else 1)


if __name__ == "__main__":
    main()
