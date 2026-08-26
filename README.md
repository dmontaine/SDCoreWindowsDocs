# SD Core for Windows — documentation

Documentation for **SD Core for Windows W1.0-0**. The server source is in a
separate repository, `sd4windows`; nothing here is needed to build SD, and
nothing in `sd4windows` is needed to build these pages.

**This repository does not have `sd4windows`'s no-binaries rule** (owner,
26 Aug 2026). It does not track the rendered pages anyway — see *Generated*
below.

## Layout

Three document sets, each with the same three folders:

| | |
|---|---|
| `Testing/` | the tester set — 15 pages, what ships with W1.0-0 |
| `User/` | not written yet |
| `Technical/` | not written yet |

Inside each: `markdown/` is the source, `html/` and `pdf/` are generated.

`QUESTIONS-2026-08-26.md` at the top is the review list for the tester set,
with the answers recorded against each question. **It is not part of any set.**

## Building

```
tools\release.ps1
```

That renders whatever changed, refuses if any generated page is older than its
Markdown, zips the result and prints the SHA256. `-Set User` does another set,
`-Force` re-renders everything, `-NoZip` stops before the zip.

The two steps it drives can also be run alone:

```
python tools\mkdoc.py --in Testing\markdown --out Testing\html
powershell -File tools\mkpdf.ps1 -In Testing\html -Out Testing\pdf
```

`mkdoc.py` needs **python-markdown** (`pacman -S msys/python-markdown` on the
MSYS2 python, or `pip install markdown`). `mkpdf.ps1` needs Edge or Chrome,
which every supported Windows machine already has.

## Generated, not tracked

`*.html`, `*.pdf` and `*.zip` are ignored. The deliverables — a PDF download,
and eventually the pages on a web site — are built from the Markdown at release
time, so tracking a rendered copy would only add a way for the two to disagree.
`.gitignore` carries the rest of the reasoning.

## A new clone

Set the identity per repository; this machine has no global one:

```
git config user.name dmontaine
git config user.email bigriverguy@posteo.net
```
