Title: Differences from W1.0-0
Subtitle: What changed for someone writing SD BASIC or working at TCL, grouped by theme rather than by date.

This page is for someone who already knows **W1.0-0** and is looking at
**W1.1-0**. The rest of this set describes the current language and command
processor on their own terms; this page exists only to say what is
*different*, and to flag what an existing program or habit might trip over.

The day-by-day version — every fix, in the order it was made — ships on the
machine at `C:\ProgramData\SD\sdsys\changelog`. The GettingStarted and
Administrator sets each carry a page with the same title, covering the
account, security and installation changes from their own angle; this page
covers what actually reaches a program or a TCL session.

## Record ids no longer distinguish case, anywhere

**A file can hold `jack` or `JACK` but never both.** Writing one when the
other already exists updates the same record, in every file — this is how
the system files (`voc`, the dictionaries) already behaved, and it now holds
for files you create too. `CREATE.FILE ... CASE` is refused; there is no way
back to case-sensitive ids.

**Upgrading converts your existing files for you**, and leaves untouched any
file that already holds two ids differing only by case — both are named in
`nocase-upgrade.log` in the SD data folder. Resolve the pair by hand (rename
or delete one), then convert that file yourself with `CONFIGURE.FILE
NO.CASE`. A file with alternate key indexes needs the same treatment. See
*Lower case*, in the GettingStarted set, for the full mechanism.

## SD's own names are lower case, but every lookup still finds what you type

**SD's vocabulary, dictionary field names, and catalogued program names are
now stored in lower case.** `MAP` lists `$cproc`, `!parser` and so on;
`CATALOG` and `DELETE.CATALOG` report lower-case names; the fields in the
dictionaries SD ships (`voc`, dictionaries themselves, `$map`, `accounts`,
`os.users`, `batch.jobs`, `$hold`) are `type`, `desc`, `f1`, `data.name`,
`@id` and so on.

**None of this changes what you type.** A lookup tries the name exactly as
typed, then lower case, then upper case — in VOC entries (as before), and
now the same way in dictionary field names too: `LIST`, `SORT`, `SELECT`,
`COMPILE.DICT`, `CREATE.INDEX`, `SHOW`, and I-type or A-type expressions all
resolve a field name in any case. Before this release, an I-type expression
could only name a field defined in upper case, and `CD` could not find an
item defined in a different case from how you typed it.

**Names compiled into a program are lower case too, and case no longer
matters when you call them.** A `CALL`, `SUBROUTINE`, `FUNCTION`, `PROGRAM`
or `CLASS` name compiles to lower case, and a call made in any case —
including from a program compiled by an earlier release — still finds it.
`COMMON` block names are unchanged. Cataloguing a program you already
catalogued under an earlier release renames its VOC entry to lower case
rather than adding a second entry beside it.

**`SET.FILE`, `.S` and `CNAME` now store new VOC entries in lower case, and
treat a differently-cased match as the same entry** rather than silently
creating a second one — `SET.FILE` reports the pointer name already exists,
`.S` asks whether to overwrite, `CNAME` refuses the new name. `CNAME` also
renames a lower-cased file's dictionary directory along with its data;
catalogued program names stay upper case regardless.

**Four VOC entries and the `SYSCOM` include files were renamed to lower
case**: `$ACC`, `$MAP`, `$RELEASE` and `SD.VOCLIB` are now `$acc`, `$map`,
`$release` and `sd.voclib`; `$INCLUDE` finds `keys.h`, `err.h` and the rest
however you type the name. Typing an old upper-case name still works
everywhere; updating an account (`UPDATE.ACCOUNTS`, or answering Y to
"Update VOC to new release?") renames an entry held under its old name
rather than adding a duplicate.

**New files, from `CREATE.FILE`, are named in lower case** —
`CREATE.FILE ORDERS` makes a file called `orders` — and every command looks
a file name up as typed, then lower, then upper, so `ORDERS` and `orders`
both reach it. Files that already exist keep their existing name.
`OPTION CREATE.FILE.UPCASE` keeps whatever case you actually typed, despite
its name.

## Python (`PY_` functions) is back, and runs outside the database

**All twenty-one `PY_` functions are available** — `PY_INITIALIZE`,
`PY_RUNSTRING`, `PY_RUNFILE`, `PY_GETATTR`, the dictionary and list
families, and `PY_LISTCREATE`, which is new: a program could append to a
Python list and read one back before, but had no way to make one. Declare
them all with `$INCLUDE SDPYFUNC.H`. Full reference, every function and
every error code: *SD BASIC - Python Integration*, earlier in this set.

**Python no longer runs inside `sd.exe`.** It runs in a separate program,
`sdpy.exe`, and your session talks to it down a pipe — the first `PY_` call
in a session starts it, and it goes away when the session ends. You do not
start or stop it yourself. This matters because a Python crash can no
longer take the database process down with it, and Python's own version is
no longer tied to SD's.

**You need an all-users install of Python 3.13 or later** — a "for me only"
install cannot be used. Without one, every `PY_` function returns `-12040`
and nothing else about SD is affected. The installer offers to install one
from the release zip.

**Access follows whoever may reach the operating system.** The same test
that gates `SH` and `OS.EXECUTE` — an `OS.USERS` grant, or being SDSYS —
gates Python, because it can read and write files and start programs just
as freely. `PY_INITIALIZE` and every other `PY_` call return `-12041` in a
session that may not use `OS.EXECUTE`, or `-12042` if SD could not even tell
(reported once in the error log). The decision is made at the first `PY_`
call and stands for the session.

## Saving in `micro` no longer fails for an ordinary account

**An earlier build failed here and it is fixed.** Full detail, including
what was actually wrong, is on the page it belongs to:
[Saving works for an ordinary account](27-sd-tcl-micro.html#saving-works-for-an-ordinary-account).

## Prompts, and a few command fixes

**Ten confirmation prompts across TCL now show their default and take
Enter as an answer**, instead of repeating the question forever when the
input runs out — this matters most to a script or batch job feeding answers
from a file or a pipe. Covered: the `DATA`/`DICT`/"use file" questions in
`DELETE.FILE`, its three-way "delete all data components of multifile"
prompt (`Y`/`N`/`C`, where Enter now means `C`, cancel), the three `CATALOG`
questions, `.D`'s "delete VOC record", `.S`'s "overwrite VOC record", and
`DELETE.FILE ... NO.QUERY`'s stray extra prompt when the file's data lives
in the system account — removed outright, since `NO.QUERY` exists precisely
so nothing asks. Two prompts are deliberately unchanged, because no is not
a safe default for either: "delete all data components of multifile" (plain
`DELETE.FILE`, without `NO.QUERY`) and "use active select list".

- **`COPY ... OVERWRITING DELETING` onto the same record** — same file, same
  id, or ids differing only in case now that every file is nocase — no
  longer writes the record and then deletes it. It leaves the record in
  place and reports it was copied onto itself.
- **A page-full report's "Suppress pagination" answer (`S`) now actually
  suppresses it.** It used to stop the prompts but still clear the screen
  and repeat the heading on every later page, so only the last page was
  readable.
- **`LIST.READU` and `GETLOCKS` no longer risk a crash** when a lock is held
  for a session that has already gone; such a lock now shows its owner as
  `(gone)`.
- **A terminfo source with a truncated final entry is now reported as a
  failure** by `sdtic`, rather than being silently written to the database
  without that entry and exiting 0. See
  [Compiling a definition](39-sd-terminfo.html#compiling-a-definition).

## Not yet reflected on the client API page

**`37-sd-client-api.md`'s "A session is confined to its own account"
describes the pre-W1.1-0 shape.** An API session now runs as the Windows
user who logged in rather than as the SD service account, and the whole
connection — network or local — is wrapped in TLS 1.3 before login. Both
are real, current behaviour; this page states them because the page that
should carry them does not yet. Until it is updated: `SH` and `OS.EXECUTE`
do not work at all from a program that logs in over the API in this
release, and a client built against an older client library cannot connect
until it is relinked.

## What might stop working

- **A program relying on `CREATE.FILE ... CASE`** to keep two record ids
  that differ only by case — refused outright now, and an existing file
  with such a pair is left unconverted until you resolve it by hand.
- **A dictionary or program that depended on an upper-case-only field or
  catalogue name existing as a *separate* entry from its lower-case
  counterpart** — the two are the same entry now.
- **A script or batch job answering prompts from a file or pipe**, if it was
  written to answer a question that no longer appears (the extra
  `DELETE.FILE ... NO.QUERY` prompt) or to expect no default on one that now
  has one.
- **A Python-dependent program**, if the machine's only Python install is
  "for me only" rather than all-users, or is older than 3.13.
- **An API client built against an older client library**, once the server
  it connects to is upgraded.

## See also

*Lower case*, in the GettingStarted set — the complete mechanism, exceptions
and upgrade log, written once and not repeated here.
