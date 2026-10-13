#!/usr/bin/env python3
"""Fetch the consolidated Statutes of Barbados from the Barbados Judiciary
(Supreme Court Records Branch) website, barbadoslawcourts.gov.bb.

Parses the "Statutes of Barbados" index page and downloads each PDF into
_raw/bb/<kind>/pdf/. robots.txt asks Crawl-delay: 10, which is obeyed.
Usage: bb_fetch.py [statutes|subsidiary]
"""
import json, os, re, subprocess, sys, time, urllib.parse
import requests
from bs4 import BeautifulSoup

BASE = "https://www.barbadoslawcourts.gov.bb/"
PAGES = {"statutes": "laws/consolidated-laws/statutes-of-barbados",
         "subsidiary": "laws/consolidated-laws/subsidiary-legislation-of-barbados"}
UA = "LawCodex/1.0 (+https://github.com/LawCodex)"
RAW = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "_raw", "bb")
DELAY = 10.0  # robots.txt Crawl-delay
s = requests.Session()
s.headers["User-Agent"] = UA


def get(url):
    for i in range(5):
        try:
            r = s.get(url, timeout=300)
            if r.status_code in (200, 404, 403):
                return r
        except requests.RequestException as e:
            print("  retry", url, e, file=sys.stderr)
        time.sleep(DELAY * (i + 1))
    raise RuntimeError("failed " + url)


def pdf_ok(path):
    if not os.path.exists(path):
        return False
    size = os.path.getsize(path)
    with open(path, "rb") as f:
        head = f.read(5)
        f.seek(max(0, size - 4096))
        tail = f.read()
    if head != b"%PDF-" or b"%%EOF" not in tail:
        return False
    return subprocess.run(["pdfinfo", path], capture_output=True).returncode == 0


def main():
    kind = sys.argv[1] if len(sys.argv) > 1 else "statutes"
    d = os.path.join(RAW, kind)
    os.makedirs(os.path.join(d, "pdf"), exist_ok=True)
    lp = os.path.join(d, "list.json")
    if os.path.exists(lp):
        items = json.load(open(lp))
    else:
        soup = BeautifulSoup(get(BASE + PAGES[kind]).text, "lxml")
        items, seen = [], set()
        for a in soup.find_all("a", href=re.compile(r"\.pdf$", re.I)):
            href = a["href"]
            if "/pdfs/statutes/" not in href or href in seen:
                continue
            seen.add(href)
            items.append({"title": a.get_text(" ", strip=True), "href": href,
                          "url": urllib.parse.urljoin(BASE, href)})
        json.dump(items, open(lp, "w"), indent=1)
        time.sleep(DELAY)
    print(len(items), "items", flush=True)
    for n, it in enumerate(items):
        fn = urllib.parse.unquote(it["href"].split("/")[-1])
        fn = re.sub(r"[^A-Za-z0-9._()',&-]", "_", fn)
        it["file"] = fn
        p = os.path.join(d, "pdf", fn)
        if pdf_ok(p):
            it["pdf_ok"] = True
            continue
        try:
            r = get(it["url"])
        except RuntimeError as e:
            print(n, fn, "FAILED", e, flush=True)
            continue
        it["status"] = r.status_code
        if r.status_code == 200 and r.content[:5] == b"%PDF-":
            cl = r.headers.get("content-length")
            if not cl or int(cl) == len(r.content):
                open(p, "wb").write(r.content)
        it["pdf_ok"] = pdf_ok(p)
        print(n, fn, it["pdf_ok"], r.status_code, flush=True)
        if n % 20 == 0:
            json.dump(items, open(lp, "w"), indent=1)
        time.sleep(DELAY)
    json.dump(items, open(lp, "w"), indent=1)


if __name__ == "__main__":
    main()
