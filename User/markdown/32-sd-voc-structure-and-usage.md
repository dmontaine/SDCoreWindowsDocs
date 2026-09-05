Title: SD VOC - Structure and Usage
Subtitle: The Vocabulary file: every record type, every field, and how the command processor uses them.

The VOC — Vocabulary — is the file that makes a command line work. Type a
name, and the command processor looks it up here. The name of a verb, a
file, a paragraph, a stored sentence, a keyword — all of them are records
in the VOC. This page is about the record types, their fields, and what
the verbs that manage the VOC do to them.

SD folds case, so a command may be typed in either case. Commands are shown
here in lower case, which is what this port uses on disk. In the tables,
*italics* mark something you supply and **bold** marks a word typed as it
stands; braces mark an optional part.

> **Every record on this page was read from a stock account VOC on SD Core
> for Windows W1.0-0.** The records were written by `CREATE.ACCOUNT`,
> which copies them from `voc_template` in the system directory. The counts
> are what a standard account holds; an administrator account holds more.

## The ten record types

Field 1, character 1, is the type. The rest of field 1 is free text and is
ignored, so a verb record whose field 1 reads `Verb to compile SD BASIC
program` is type `V` and the rest is a comment. **The first character is
load-bearing and the remaining thirty are not.**

| Type | Name | What it does |
|---|---|---|
| `V` | verb | the common case — dispatches to a program or an internal routine |
| `K` | keyword | a query-processor keyword; four of these are also verbs |
| `S` | sentence | one stored command line |
| `PA` | paragraph | several stored command lines, with flow control |
| `M` | menu | dispatched, but no menu ships |
| `Q` | Q-pointer | an indirect pointer to a file in another account |
| `F` | file | a file — local, or pointing into `@SDSYS` |
| `R` | remote | a pointer to a record in another file, re-read and re-parsed |
| `X` | text | miscellaneous data — not a command |
| `D` | descriptor | a data descriptor, which is what dictionary records are |

**`PQ` is a valid type and is refused.** PROC was removed from this port
(23 Aug 2026). A record of type `PQ` is reported as *"PROC is not
supported"* rather than being dispatched, because the record itself is
valid PROC and it is the interpreter that is gone.

### What a stock VOC holds

Read from `voc_template` in the system directory, a stock account VOC
carries 426 records:

| Type | Count |
|---|---|
| `V` | 137 |
| `K` | 248 |
| `F` | 16 |
| `R` | 10 |
| `PA` | 4 |
| `S` | 2 |
| `PH` | 2 |
| `Q` | 2 |
| `X` | 3 |
| `Verb - Full screen editor` | 2 |

The last row is `edit`, the full-screen editor that was removed on 23 Aug
2026. Its type field reads `Verb - Full screen editor` rather than `V`,
which means it is not a verb and cannot be dispatched — but it is still in
the template, and `EDIT` at the command prompt reports *"Full screen editor
is no longer supported"* rather than *"verb not found"*. **Being in the VOC
is not evidence a command works.**

## The F record — a file

```
001  F
002  bp
003
```

This is the `bp` entry — the BASIC source file. Field 1 is `F`, field 2 is
the operating-system path to the data portion, and field 3 is the path to
the dictionary portion. An empty field 3 means the file has no separate
dictionary.

| Field | |
|---|---|
| `1` | `F`, optionally followed by a comment |
| `2` | data path — a name in the account directory, or `@SDSYS/`*name* for a system file |
| `3` | dictionary path, or empty if none |

### The eight pointers into @SDSYS

A stock account VOC carries eight F-records whose data path begins
`@SDSYS/`. They point at files in the system directory that every account
needs:

| VOC id | Field 2 |
|---|---|
| `voc` | `@SDSYS/voc.dic` (field 3 — the dictionary) |
| `newvoc` | `@SDSYS/newvoc` |
| `messages` | `@SDSYS/messages` |
| `syscom` | `@SDSYS/syscom` |
| `$MAP` | `@SDSYS/...` |
| `dict.dic` | `@SDSYS/...` |
| `sd.voclib` | `@SDSYS/...` |
| `$ipc` | (system IPC file) |

These are **read-only to a network session**. The account-root gate in
the file engine allows them on read paths but sets `FV_RDONLY` on the
file variable, so every write path in the engine refuses them. An
administrator in `SDSYS` is exempt; an ordinary account cannot write
these files.

### The $ACC record

```
001  F
002  .
003
```

`$ACC` is the account itself. Field 2 is `.`, which means the current
account directory. It is how a program opens "the account I am in" by
name rather than by path.

## The V record — a verb

```
001  V
002  CA
003  $CREATEF
004
```

This is `create.file`. Field 2 is the dispatch type, field 3 is the
target, and the remaining fields carry options.

| Field 2 | Field 3 | What it does |
|---|---|---|
| `CA` | *catalogue name* | a catalogued program — 99 of the shipped verbs |
| `IN` | *number* | internal verb *n*, handled by the command processor itself — 42 verbs |
| `OS` | *text* | an operating-system command — `sh` and `!`, and nothing else |
| `CS` | *path* | a locally catalogued function |

Those four rows account for 143 of the 147 verbs an administrator account has.
The remaining four are the keyword records described above — `break`, `count`,
`display` and `off` — where field 2 holds a keyword number rather than a
dispatch type, and it is field 3 that marks the record as a verb.

Field 4 carries dispatch options and **field 5 names a security subroutine**.
If field 5 is present, that subroutine is called before the verb runs and
can refuse it. **None of the shipped verbs uses field 5** — the tiering
in this port is done by giving or withholding the VOC record, not by a
security subroutine — but the mechanism is there for a site that wants a
verb guarded rather than absent.

### Internal verbs

`IN` verbs are numbered, and the numbers are positional in the command
processor's dispatch list. Several names share one: `off` and `quit` are
both internal verb 1, `clr` and `cs` are both 2, and each of `clear.data`,
`clear.input`, `clear.prompts` and `clear.select` has a run-together
spelling (`cleardata` and the rest) pointing at the same number.

### The four keyword-verbs

Four records ship as a keyword **and** a verb in one: `break`, `count`,
`display` and `off`. Their field 2 is the keyword number the query
processor uses, and **fields 3 onward are a complete verb record**, which
the command processor re-parses when the name is typed as a command.

**This matters for counting what an account has.** A tally of VOC
records whose field 1 begins with `V` misses all four, and `count` is not
a marginal verb. A standard account has **82** verbs, not 78.

## The Q record — an indirect pointer

```
001  Q
002  SDSYS
003  accounts
```

This is `sd.accounts`. Field 2 is the account name, field 3 is the file
name in that account. `set.file` writes Q-pointers; see below.

`md` is a Q-pointer to `voc` — the VOC's own dictionary is reached
through it, and it is how `dict voc` finds its records.

## The R record — a remote record reference

```
001  R
002  SD.VOCLIB
003  listf
```

This is `listf`. Field 2 is the file name, field 3 is the record id. An
R-record is **re-read and re-parsed every time it is used**, so editing
the referenced record changes what the command does without touching the
VOC entry. The `LIST` family — `listf`, `listfl`, `listfr`, `listk`,
`listpa`, `listph`, `listq`, `listr`, `lists`, `listv` — are all
R-records pointing into `SD.VOCLIB`.

## The S record — a sentence

```
001  S
002  DISPLAY <<@PATH>>
```

This is `where`. A sentence is one stored command line. Typing its name
runs that line with anything else you typed appended, so a sentence is a
command with its first arguments filled in.

## The PA record — a paragraph

```
001  PA
002  TERM WINDOWS
003  TERM 120,36
004  PTERM CASE NOINVERT
```

This is `login`, the paragraph that runs at sign-on. A paragraph holds
several lines and has flow control: `if`, `go`, `stop`, `abort`,
`display`, `pause`. Paragraphs nest, and `abort` unwinds all of them.

**`data` lines are read ahead of the verb, not executed in sequence.**
Before a verb runs, the command processor scans forward over any
immediately following `data`, comment and blank lines and stacks their
text as typed-ahead input.

### The PH record — a phrase

```
001  PH
002  GRAND.TOTAL "'L'"
```

This is `no.grand.total`. A phrase is a stored fragment that is
substituted into a command line wherever its name appears. `PH` is
treated as `S` for most purposes — the difference is that a phrase is
designed to be used inside another command rather than typed on its own.

`without` is also `PH`, holding `WITH NO` — so `list stock without qty`
expands to `list stock with no qty`.

## The K record — a keyword

```
001  K
002  26
```

This is `#`, the comment keyword. Field 2 is the keyword number the query
processor uses. Keywords are not commands in their own right; they are
the words the query processor — `LIST`, `SELECT`, `SORT` and the rest —
recognises inside a command line. `all` is `K` with number 5; `after` is
`K` with a number; `and` is `K`.

The 248 K-records in a stock VOC are the query processor's vocabulary,
and they are what makes a sentence like `list stock with qty > 100 by
supplier` parse.

## The X record — text

```
001  X
002  Most of SD is licensed under the GPL v3.0 ...
```

This is `$licence`. An X-record is **not a command** — it is miscellaneous
data the VOC holds so that a program or a user can read it by name.
`$contrib` and `$RELEASE` are also X-records. Nobody dispatches them; they
are read with `read` from BASIC or with `ct` from the command line.

## How the command processor uses the VOC

The command processor is a BASIC program, `$CPROC`, and it runs a loop:
show any waiting messages, print the prompt, read a line, dispatch it,
repeat. The first word of the line is looked up in the account's `voc`
file.

### Name resolution

A name is tried **as typed, then lower case, then upper case**. This is
the change that lets a lower-case `voc`, `bp` and `newvoc` on disk
coexist with code and habits that still type names in upper case.

**Account names are the deliberate exception.** They are still folded
upward, which is what makes signing in case-insensitive.

### If the VOC has nothing, the catalogue is tried

A name that is not in the VOC is looked for in the **private catalogue**
of the account and then in the **global catalogue**, `gcat`. A hit is
treated exactly as though the VOC had held `V` / `CA` / *name*. This is
why a program you have catalogued can be run by typing its name with no
VOC record of its own.

If neither has it, the command is refused by name.

## Verbs that manage the VOC

### set.file — write a Q-pointer

```
set.file account file.name pointer.name
```

Writes a Q-pointer into the VOC — field 1 `Q`, field 2 the account name,
field 3 the file name. After it, *pointer.name* is usable wherever a file
name is, and the data stays where it is.

**The account must be in the accounts register.** The name is folded to
upper case before the register is read. If it is not there you get
*Account name '...' is not in register* and nothing is written.

### update.accounts — refresh from NEWVOC

```
update.accounts
```

Re-runs `LOGIN`'s `update.voc` paragraph, which copies any changed
records from the system `NEWVOC` into the account's VOC. **Since 17 Aug
2026 this is incremental** — it re-copies only the records whose stamp has
changed, not the whole file. `TIER.OMIT.STANDARD` and
`TIER.ADD.ADMINISTRATOR` in `NEWVOC` control what each account type
receives.

**The tier test is the one this record exists for.** `update.accounts`
on a standard account must not give back the verbs that were withheld
when the account was created. A standard account starts with fewer verbs
than an administrator account, and `update.accounts` preserves that
difference.

### copy — copy records into the VOC

```
copy from voc messages,myname
copy from src.file to dict tgt.file record.id
```

`copy` can write into the VOC the way it writes into any file. The
`from voc` form copies a VOC record under a new name, which is how an
alias is made without `alias`.

### delete — remove a VOC record

```
delete voc name
```

Removes the record. **`.d` *name* at the command prompt asks first**;
`delete voc name` does not.

### .s and .r — save and recall

```
.s name s e
.r name
```

`.s` writes stack lines *s* to *e* into the VOC as *name* — a sentence
when the range is one line, a paragraph when it is more. `.r` loads a
sentence or paragraph from the VOC into the stack. **The record type
follows from what you saved** rather than from anything you say.

### The LIST family

Ten verbs list VOC entries by type. They are all R-records into
`SD.VOCLIB`:

| Verb | Lists |
|---|---|
| `listf` | all files (F-records) |
| `listfl` | local files only |
| `listfr` | remote files only |
| `listk` | all keywords (K-records) |
| `listpa` | all paragraphs (PA-records) |
| `listph` | all phrases (PH-records) |
| `listq` | all Q-pointers |
| `listr` | all remote references (R-records) |
| `lists` | all sentences (S-records) |
| `listv` | all verbs (V-records) |

### count — count the records

```
count voc
count voc with v = "V"
```

`count` over the VOC gives the total record count. With a selection
clause it counts by type or by any other field.

### ct — display a record

```
ct voc name
```

Displays the record field by field. This is the way to see what a VOC
entry actually contains without an editor.

## The VOC and account creation

`CREATE.ACCOUNT` copies the VOC from `voc_template` in the system
directory. The template holds 426 records; `NEWVOC` holds 395. The
difference is that `voc_template` carries the A-verbs — `abort`,
`alias`, `all`, `after`, `and` and the rest — that are also keywords, and
`NEWVOC` does not. An account gets the union of the two, less whatever
its tier omits.

| Tier | What it gets |
|---|---|
| **administrator** | everything in `voc_template` plus everything in `NEWVOC`, less `TIER.OMIT.STANDARD` |
| **standard** | everything in `voc_template` plus everything in `NEWVOC`, less `TIER.OMIT.STANDARD` (42 names) |
| **programmer** | standard plus the programmer verbs from `TIER.ADD.ADMINISTRATOR` |

**The tier is in the VOC, not in the verb.** A standard account does
not have `create.file` because the VOC record for it is not there, not
because a security subroutine refuses it. The name is simply not
recognised. This is the design: tiering is done by giving or withholding
the record.

## Case on disk

Since 18 Aug 2026 the VOC ids are stored in lower case — `list`,
`create.account` and so on. This changes nothing about what you type —
SD tries a name as typed, then lower, then upper. What it changes is what
SD prints back: `CT VOC LIST` answers `VOC list`.

The file-pointer entries — `bp`, `bp.out`, `gpl.bp`, `gpl.bp.out` — moved
to lower case on 19 Aug 2026. `VOC`, `NEWVOC`, `ACCOUNTS`, `MESSAGES`,
`SYSCOM` and `QFILE` are still upper case on disk and are next.

## What is not here

**There is no verb that edits the VOC directly.** `ED` edits any file,
and `ED VOC`*name* is how you edit a VOC record by hand. But there is no
verb whose purpose is to create or modify VOC entries — `set.file` writes
one kind, `.s` writes two, and everything else is done with `ED` or with
`copy from voc`.

**`PROC` is removed.** A `PQ`-type record is refused by name. Nothing
that ships is type `PQ`, so this can only be met in a VOC record somebody
wrote.

**`menu` records are dispatched but no menu ships.** Type `M` is handled
and there is no shipped example to look at.

**`EDIT` is in the VOC but cannot run.** Its type field reads
`Verb - Full screen editor`, which is not `V`, so the command processor
does not dispatch it. The record is there so that `EDIT` at the prompt
prints *"Full screen editor is no longer supported"* rather than *"verb
not found"*.

## See also

[SD TCL - The Command Processor](19-sd-tcl-command-processor.html) ·
[SD TCL - Files and Records](20-sd-tcl-files-and-records.html) ·
[SD Basic - File Handling](07-sd-basic-file-handling.html) ·
[SD Basic - Dynamic Arrays](05-sd-basic-dynamic-arrays.html).
