#!/usr/bin/env python3
"""Convert downloaded consolidated Statutes of Barbados PDFs (_raw/bb) to Markdown.

Most PDFs are scans with an embedded OCR text layer produced by the publisher
(Acrobat Capture); that layer is used as-is. Documents without a usable text
layer are reported as gaps (no OCR is performed here).
"""
import datetime, json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bb_pdfmd as pm

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
RAW = os.path.abspath(os.path.join(ROOT, "..", "_raw", "bb"))
PAGE = "https://www.barbadoslawcourts.gov.bb/laws/consolidated-laws/statutes-of-barbados"
JUNK = [r"^THE LAWS OF BARBADOS$", r"^Printed by the Government Printer", r"^by the authority of the Government of Barbados$"]
MIN_QUALITY = 0.70


def slugify(s):
    s = s.lower().replace("&", " and ")
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s[:80].strip("-")


def q(s):
    return '"' + str(s).replace("\\", "\\\\").replace('"', '\\"') + '"'


def front(d):
    out = ["---"]
    for k, v in d.items():
        if v is None or v == "":
            continue
        out.append(f"{k}: {v if isinstance(v, (int, float)) or k in ('date', 'last_amended', 'retrieved', 'type', 'jurisdiction', 'language', 'status') else q(v)}")
    out.append("---")
    return "\n".join(out) + "\n\n"


def main(kind="statutes"):
    retrieved = datetime.date.today().isoformat()
    for d in ("chapters", "constitution"):
        os.makedirs(os.path.join(ROOT, d), exist_ok=True)
    items = json.load(open(os.path.join(RAW, kind, "list.json")))
    report = {"converted": [], "gaps": []}
    used = set()
    for it in items:
        fn = it.get("file") or re.sub(r"[^A-Za-z0-9._()',&-]", "_", it["href"].split("/")[-1])
        pdf = os.path.join(RAW, kind, "pdf", fn)
        label = re.sub(r"\s+", " ", it["title"]).strip()
        if not os.path.exists(pdf) or not pm_ok(pdf):
            report["gaps"].append({"title": label, "reason": "PDF not downloadable / incomplete", "source": it["url"]})
            continue
        body, st = pm.pdf_to_md(pdf, extra_header_patterns=JUNK, anywhere_patterns=JUNK, tmpdir=RAW)
        if st["chars_per_page"] < 150 or st["quality"] < MIN_QUALITY:
            report["gaps"].append({"title": label, "reason": f"scanned PDF without usable text layer (chars/page "
                                   f"{st['chars_per_page']:.0f}, quality {st['quality']})", "source": it["url"]})
            continue
        cm = re.search(r"\s*CAP\.?\s*(\d+)([A-Z]*)\s*$", label, re.I)
        name = label[:cm.start()].strip() if cm else label
        is_const = name.lower() == "constitution of barbados"
        if cm:
            cap = f"{int(cm.group(1))}{cm.group(2).upper()}"
            fname = f"cap-{int(cm.group(1)):03d}{cm.group(2).lower()}-{slugify(name)}"
        else:
            cap = None
            fname = slugify(name)
        while fname in used:
            fname += "-2"
        used.add(fname)
        rel = ("constitution/" if is_const else "chapters/") + fname + ".md"
        title = name if is_const or re.search(r"\b(Act|Order|Ordinance)\b", name) else name + " Act"
        fm = {
            "title": title,
            "identifier": f"Cap. {cap}" if cap else None,
            "type": "constitution" if is_const else "act",
            "jurisdiction": "bb", "language": "en",
            "status": "in_force",
            "source": PAGE,
            "source_pdf": it["url"],
            "text_source": "embedded text layer of the official PDF (OCR by the publisher; may contain recognition errors)",
            "pages": st["pages"],
            "retrieved": retrieved,
        }
        with open(os.path.join(ROOT, rel), "w", encoding="utf-8") as f:
            f.write(front(fm) + f"# {title}\n\n" + body)
        report["converted"].append({"title": label, "file": rel, "quality": st["quality"]})
        print(rel, st["quality"], flush=True)
    json.dump(report, open(os.path.join(RAW, "convert_report.json"), "w"), indent=1)
    print(len(report["converted"]), "converted;", len(report["gaps"]), "gaps")


def pm_ok(path):
    import subprocess
    with open(path, "rb") as f:
        head = f.read(5)
        f.seek(max(0, os.path.getsize(path) - 4096))
        tail = f.read()
    return head == b"%PDF-" and b"%%EOF" in tail and \
        subprocess.run(["pdfinfo", path], capture_output=True).returncode == 0


if __name__ == "__main__":
    main()
