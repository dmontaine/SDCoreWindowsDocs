# SD Core for Windows — documentation

Documentation for **SD Core for Windows W1.0-0**. The server source is in a
separate repository, `sd4windows`; nothing here is needed to build SD, and
nothing in `sd4windows` is needed to build these pages.

**This repository does not have `sd4windows`'s no-binaries rule** (owner,
26 Aug 2026). It does not track the rendered pages anyway — see *Generated*
below.

## Layout

Four document sets, each with the same three folders:

| | |
|---|---|
| `Testing/` | the tester set — 15 pages, what ships with W1.0-0 |
| `User/` | **two references, both complete.** `01`-`18` SD BASIC by subject, where `18` is Modern Program Structure — scope, local routines and objects. `19`-`31` SD TCL by subject; the administrator verbs are not here, they are their own set. ***THE GENERATED SYNTAX CARDS LIVE AT THE END, `94` ONWARDS***, so more can be added without renumbering anything: `94` SD BASIC (411 names), `95` SD TCL (143 verbs) |
| `Administrator/` | **three documents, and a separate deliverable on purpose** — `01` accounts and security, `02` sessions and locks, `03` operating system access. Every verb in it is administrator-tier, **so an administrator can withhold the whole set** |
| `Technical/` | **`01` Restricted Commands** — what an ordinary program cannot compile. The rest is not written yet |

Inside each: `markdown/` is the source, `html/` and `pdf/` are generated.

**The `User` set is measured, not compiled from the old help tree.** Its roster
comes from `BCOMP`'s own tables, and every example was run before it was
written down. `tools\probes\` holds the programs that produced the numbers and
`tools\probes\README.md` says which runner takes which.

***SETS NEVER LINK TO EACH OTHER, AND THAT IS ENFORCED BY CONVENTION RATHER
THAN BY A TOOL.*** Each set is handed out on its own, so a link from one to
another would be a 404 for whoever was given only the first. `Administrator/` is
the reason the rule now matters: withholding it must not break the `User` set.
Where a page in another set is worth naming, **name it in words**.

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

***THEY ARE TWO STEPS AND THE SECOND IS THE ONE THAT GETS FORGOTTEN.*** Pages
19 to 27 of the `User` set were written, rendered to HTML and pushed with **no
PDF at all**, and nothing said so — `release.ps1` exists precisely so this
cannot happen, and running the two steps by hand skips its bookkeeping.

**The check is markdown against PDF, not HTML against PDF.** Re-rendering the
HTML touches every file's mtime, so comparing those two reports the whole set
as stale and tells you nothing. Only the source answers the question:

```sh
for m in Testing/markdown/*.md; do
  p="Testing/pdf/$(basename "$m" .md).pdf"
  [ -f "$p" ] || echo "MISSING $p"
  [ "$m" -nt "$p" ] && echo "STALE   $p"
done
```

Both take one file as well as a directory, so a single changed page costs one
render rather than forty-three.

## Regenerating the syntax cards

***THE CARDS LIVE AT THE END, `94` ONWARDS, SO MORE CAN BE ADDED WITHOUT
RENUMBERING ANYTHING.*** Owner's ruling, 27 Aug 2026: parking them high means
that when they are eventually renumbered it is only ever the cards that move.

| | |
|---|---|
| `User/markdown/94-sd-basic-syntax.md` | SD BASIC, from `mksyntax.py` |
| `User/markdown/95-sd-tcl-syntax.md` | SD TCL, from `mktclsyntax.py` |

### The SD TCL card

```
python tools\mktclsyntax.py <sd4windows>\sdb_ai\sd64\sdsys User\markdown\95-sd-tcl-syntax.md
```

Its roster is computed from SD's own VOC — the verb records in `newvoc` plus
`TIER.ADD.ADMINISTRATOR`, **143** — and it **refuses to write the page** if a
verb has no line, or if a line names something that is not a verb. It caught
`selecte` on the first run, which is a BASIC statement.

***AND IT CAUGHT THE SECOND HALF ITSELF, 28 Aug 2026.*** The roster is computed,
so it dropped to 143 the day `encrypt.field` left `TIER.ADD.ADMINISTRATOR`; the
shapes file and `tclmap`'s map are typed, so they did not. **Both generators had
been refusing to run** — `NOT A VERB encrypt.field has a shape and is not on the
roster` — which is the refusal working as designed, and it is the reason a
computed roster is worth the trouble.

The syntax itself lives in `tools/tcl-syntax-shapes.txt`, **not** in the
programs' `START-DESCRIPTION` blocks. Sixty-three of the ninety-seven
catalogued verbs carry one and none is used as content: they are in a different
notation and several are stale — `LIST.READU`'s omits `DETAIL`,
`CREATE.ACCOUNT`'s predates every tier and access keyword. **They are used as a
control instead**: the script reports where a block mentions a keyword the card
does not, as a lead for a person to follow. That found six real omissions on its
first run, in `cd`, `delete.index`, `fstat`, `map`, `option` and `setptr`.

**The tier column is read from the same two lists the account-creation code
uses**, so the card cannot drift from what an account actually gets.

### The SD BASIC card

`User/markdown/94-sd-basic-syntax.md` is **generated, not edited**:

```
python tools\mksyntax.py <sd4windows>\sdb_ai\sd64\sdsys\gpl.bp\BCOMP User\markdown\94-sd-basic-syntax.md
```

Its roster is `BCOMP`'s own tables and it **refuses to write the page if any
name accepted by the compiler has no line on it** — 411 of 411. Argument counts
for functions are read out of `BCOMP`'s dispatch table, which is positional
against the name list; the script asserts the two agree before using either.
Everything a count cannot express lives in `tools/syntax-shapes.txt`, one
`NAME = syntax` per line. **Edit that file, then regenerate.**

It writes **two** pages and checks that they **partition** the roster —
every name on exactly one of them, 447 of 447:

| | |
|---|---|
| `User/markdown/94-sd-basic-syntax.md` | 372 names an application may use |
| `Technical/markdown/01-sd-basic-restricted-commands.md` | 75 it may not — 36 restricted statements, 38 internal-only functions, and `errmsg`, which is in a table with no opcode behind it |

**`checklinks.py` on `Technical` refuses today**, and it is right to: the
set is one page with no cross-references, so it finds no links at all. Run
it there once there is a second page.

## Checking a set

```
python tools\docmap.py <sd4windows>\sdb_ai\sd64\sdsys\gpl.bp\BCOMP
python tools\tclmap.py <sd4windows>\sdb_ai\sd64\sdsys\newvoc
python tools\linkup.py User\markdown
python tools\checklinks.py User\markdown User\html
```

***`tclmap.py` EXISTS BECAUSE `docmap.py`'s QUESTION IS NOT ENOUGH.*** A map
says where a name is *meant* to be explained. On 27 Aug 2026 the TCL coverage
was recorded as 127 of 144 and was really 118 — seven verbs counted as covered
because their name appeared inside a warning, or inside a longer word. So
`tclmap` requires **evidence on the page**: the verb backticked, or opening a
line inside a fenced syntax block. Prose alone does not count.

| | |
|---|---|
| `docmap.py` | assigns every name `BCOMP` accepts to exactly one document and exits non-zero on a gap. **411 of 411** |
| `tclmap.py` | the same for the **143 TCL verbs**, across the `User` and `Administrator` sets — **and it also checks the page actually documents the verb**, not merely that the name occurs somewhere. **143 of 143, 0 exempt** |
| `linkup.py` | turns `*SD Basic - X*` into a link only for pages that exist |
| `checklinks.py` | every link in the rendered pages. **183 links, 0 broken** across 32 `User` pages |

## Measuring

These five run something inside a real SD session and refuse a run that did not
measure anything. `tools\probes\README.md` says which takes which.

**They default to a user account, not `SDSYS`, and that is not only about file
permissions.** `LOGTO SDSYS` asks UAC when the session is not already elevated,
so every run against `SDSYS` puts a consent prompt in front of whoever is at the
machine — six runs, six prompts. Measure in a user account unless `SDSYS` is
itself the subject.

| | |
|---|---|
| `sdtcl.ps1` | run **TCL commands** and print what SD said; refuses a transcript with fewer command echoes than commands sent |
| `sdprobe.ps1` | run one BASIC probe; refuses without its START and END markers |
| `sdprobe2.ps1` | **two sessions at once**, for locking; refuses unless they demonstrably contended |
| `sdcompile.ps1` | compile only, for measuring what the compiler **refuses** |
| `sddebug.ps1` | compile in debug mode and drive the debugger from a script |

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
