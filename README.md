# Barbados — Laws of Barbados (LawCodex)

Consolidated Acts (chapters) of **Barbados** as plain Markdown, converted from the "Statutes of Barbados"
PDFs published by the **Barbados Judiciary / Supreme Court Records Branch** at
<https://www.barbadoslawcourts.gov.bb/laws/consolidated-laws/statutes-of-barbados>.

Retrieved: 2026-10-13.

## Contents

| Directory | What | Files |
|---|---|---|
| `constitution/` | Constitution of Barbados (see caveat below) | 1 |
| `chapters/` | Consolidated Acts, mostly with their Cap. number (`cap-NNN[a]-<slug>.md`), plus a few un-numbered instruments (Barbados Independence Act & Order 1966, Constitution (Amendment) Act 1974, …) | 538 |

Total: **539 of the 540 statute PDFs** listed on the page. Front matter: `title`, `identifier`
(Cap. number), `type`, `revision` (latest "L.R.O. YYYY" reprint year printed on the first pages, when
present), `source`, `source_pdf`, `text_source`, `pages`, `retrieved`.

## Important caveats

- **Currency.** These are the consolidated reprints held on the Judiciary's site, with Law Revision Office
  reprint years ranging from the 1970s to 2008 (see `revision`). Many later amendments are **not**
  reflected. In particular, the Constitution text is the pre-2021 version (L.R.O. 2002): it does not
  include the Constitution (Amendment) (No. 2) Act, 2021 by which Barbados became a parliamentary republic.
- **OCR text.** Most PDFs are page scans carrying an embedded OCR text layer produced by the publisher
  (Acrobat Capture). That text layer is used as-is (no OCR by LawCodex), so recognition errors occur;
  documents are flagged with `text_source` in front matter. Average dictionary-word ratio is ~0.95.
- Marginal notes are rendered as *italic* lines; section numbers in **bold**; running headers/footers
  ("THE LAWS OF BARBADOS / Printed by the Government Printer …") removed. Tables are flattened to text.

## Gaps

- **Printers and Publishers, Cap. 301** — scanned PDF with no text layer (not OCR'd).
- **Subsidiary legislation** ("Subsidiary Legislation of Barbados" page) — not included.
- Acts passed after each chapter's reprint, and Acts not consolidated on the site (annual volumes), are not
  included. The Barbados Parliament site (barbadosparliament.com) publishes Bills, not consolidated laws.

## Source, robots and licence

robots.txt of barbadoslawcourts.gov.bb sets `Crawl-delay: 10`; the fetcher waits 10 s between requests.
No terms of use restricting reuse were found (the site's "Terms & Conditions" link is empty). Official
texts of the Government of Barbados; this is an unofficial conversion — the official publication
remains authoritative.

## Regenerate

```
python3 scripts/bb_fetch.py statutes   # parses the index page, downloads PDFs (10 s delay) -> ../_raw/bb/statutes/pdf
python3 scripts/bb_convert.py          # pdftotext -bbox-layout -> Markdown (scripts/bb_pdfmd.py)
```

Requires poppler (`pdftotext`, `pdfinfo`) and `scripts/requirements.txt`. PDFs are verified (header,
`%%EOF`, `pdfinfo`, Content-Length) before conversion.
