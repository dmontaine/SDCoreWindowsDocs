Title: SD TCL - The Command Processor
Subtitle: How a command line is read, what the VOC does with it, and the verbs that steer a session and a paragraph.

TCL is the prompt you get when you start SD. It is not a shell: it does not
search a path, it does not expand wildcards, and it has no built-in commands of
its own. **Every command you type is a record in a file**, and this page is
mostly about that file and about the small set of verbs that control the
session you are typing into.

SD folds case, so a command may be typed in either case. Commands are shown
here in lower case, which is what this port uses on disk. In the tables,
*italics* mark something you supply and **bold** marks a word typed as it
stands; braces mark an optional part.

## The prompt

The command processor is a BASIC program, `$CPROC`, and it runs a loop: show
any waiting messages, print the prompt, read a line, dispatch it, repeat. The
prompt character is `?` and it is what `system(26)` reports.

**Messages sent by `message` are printed at the prompt, not when they arrive.**
They queue in the `$ipc` file and the loop drains that queue immediately before
each prompt, so a message sent to a session sitting at TCL appears at once and
a message sent to a session running a long report appears when the report
finishes.

`report.src` turns on a line after every command reading `SRC = ` and the value
of `@system.return.code`. It takes `on`, `off`, or nothing at all, in which case
it toggles.

## Where a command goes

The first word of the line is looked up in the account's `voc` file. **What
comes back decides everything else**, because field 1 of a VOC record begins
with a type character:

| | |
|---|---|
| `V` | a verb — the common case |
| `K` | a query-processor keyword, which may also be a verb (see below) |
| `S` | a sentence: one stored command line |
| `PA` | a paragraph: several stored command lines, with flow control |
| `M` | a menu |
| `Q` | an indirect pointer to a file in another account |
| `F` | a file |
| `R` | a pointer to a record in another file, re-read and re-parsed |
| `X` | miscellaneous data — not a command |
| `D` | a data descriptor, which is what dictionary records are |

The rest of field 1 is free text and is ignored, so a verb record whose field 1
reads `Verb to compile SD BASIC program` is type `V` and the sentence is a
comment. **This is worth knowing before you edit a VOC record by hand**: the
first character is load-bearing and the remaining thirty are not.

### Names are tried as typed, then lower, then upper

This port shipped a change here. Where SD used to try the name exactly as typed
and then in upper case, it now tries **as typed, then lower case, then upper
case**. That is what lets a lower-case `voc`, `bp` and `newvoc` on disk coexist
with code and habits that still type names in upper case, and it is why you can
type `list voc` or `LIST VOC` and reach the same file.

**Account names are the deliberate exception.** They are still folded upward,
and that is what makes signing in case-insensitive.

### A hyphen is accepted where the verb has a dot

After the three case attempts, the command processor tries the name again with
any hyphens changed to dots. **So every dotted verb also answers to a hyphen.**

```
:clear-select
Cleared numbered select list 0
:clear.select
Cleared numbered select list 0
```

This is a spelling variant rather than a second verb, and two controls show it:

```
:zzz-nosuch
zzz-nosuch is not in your VOC
:ct voc create-account
Record 'create-account' not found
```

The first shows the fallback is not accepting anything at all. The second shows
there is no `create-account` record in the VOC — the resolution happens in the
command processor, not in the file.

**The dotted spelling is the documented one** and is what every page here uses.
The hyphen form is supported, and it is worth knowing because a typed hyphen
will not produce the error you expect.

### If the VOC has nothing, the catalogue is tried

A name that is not in the VOC is looked for in the **private catalogue** of the
account and then in the **global catalogue**, `gcat`. A hit is treated exactly
as though the VOC had held `V` / `CA` / *name*. This is why a program you have
catalogued can be run by typing its name with no VOC record of its own.

If neither has it, the command is refused by name.

### A keyword can be a verb

Four records that ship are a keyword **and** a verb in one record: `break`,
`count`, `display` and `off`. Their field 2 is the keyword number the query
processor uses, and **fields 3 onward are a complete verb record**, which the
command processor re-parses when the name is typed as a command.

**This matters for counting what an account has.** A tally of VOC records
whose field 1 begins with `V` misses all four, and `count` is not a marginal
verb. A standard account has **82** verbs, not 78.

## What kind of thing a verb is

Field 2 of a verb record says how to run it, and field 3 says what to run:

| | | |
|---|---|---|
| `CA` | *name* | a catalogued program — 97 of the shipped verbs |
| `IN` | *n* | internal verb *n*, handled by the command processor itself — 45 |
| `OS` | *text* | an operating-system command — `sh` and `!` |
| `CS` | *path* | a locally catalogued function |

Field 4 carries dispatch options and **field 5 names a security subroutine**. If
field 5 is present, that subroutine is called before the verb runs and can
refuse it, in which case you are told the command is restricted. None of the
shipped verbs uses field 5 — **the tiering in this port is done by giving or
withholding the VOC record**, not by a security subroutine — but the mechanism
is there for a site that wants a verb guarded rather than absent.

There are **41 internal verbs**, numbered, and the numbers are positional in the
command processor's dispatch list. Several names share one: `off` and `quit` are
both internal verb 1, `clr` and `cs` are both 2, and each of `clear.data`,
`clear.input`, `clear.prompts` and `clear.select` has a run-together spelling
(`cleardata` and the rest) pointing at the same number.

## Sentences and paragraphs

A **sentence** is a VOC record holding one command line. Typing its name runs
that line with anything else you typed appended, so a sentence is a command with
its first arguments filled in.

A **paragraph** holds several lines and is the closest thing SD Core has to a
shell script. Six verbs exist for paragraphs and **four of them are refused
outside one**:

| | |
|---|---|
| **`if`** *value* *op* *value* **;** *command* | conditional. Only inside a paragraph |
| **`go`** *label* | jump to a label. Only inside a paragraph |
| **`stop`** | end this paragraph, return to the caller |
| **`abort`** {*text*} | end the paragraph **and everything that called it** |
| **`display`** *text* | write a line to the terminal |
| **`pause`** | print a *press return* prompt and wait |

`go` searches forward from the current line for a line beginning with the
label; **a label prefixed with `@` is searched for from line 1 instead**, which
is how you jump backwards. Labels carry a trailing colon, and one is added for
you if you leave it off.

`display` understands a leading cursor-position clause, so
`display @(0,0) ready` positions and then writes. A trailing colon suppresses
the newline.

**`data` lines are read ahead of the verb, not executed in sequence.** Before a
verb runs, the command processor scans forward over any immediately following
`data`, comment and blank lines and stacks their text as typed-ahead input. So
the `data` lines that feed a program are written *after* the command that runs
it, and they must follow it without an intervening ordinary command.

Paragraphs nest, and `abort` unwinds all of them.

## The command stack

Every line you type is kept. The stack is edited with commands beginning with a
dot, and `n` below is a stack position — 1 is the most recent.

| | |
|---|---|
| **`.l`**{*n*} | list the last *n* stack lines. Defaults to 20, or a screenful |
| **`.l`** *name* | show a VOC record, one numbered line per field |
| **`.r`**{*n*} | recall line *n* to the top of the stack |
| **`.r`** *name* | load a sentence or paragraph from the VOC into the stack |
| **`.s`** *name* *s* *e* | save stack lines *s* to *e* into the VOC as *name* |
| **`.a`**{*n*} *text* | append *text* to line *n* |
| **`.i`**{*n*} *text* | insert *text* as line *n* |
| **`.c`**{*n*}`/`*old*`/`*new*`/`{`g`} | change *old* to *new* in line *n*; `g` for every occurrence |
| **`.d`**{*n*} | delete line *n* |
| **`.d`** *name* | delete a sentence or paragraph from the VOC, after asking |
| **`.u`**{*n*} | convert line *n* to upper case |
| **`.x`**{*n*} | execute line *n* |
| **`.x`** *file* *id* | execute a sentence or paragraph held in any file, not just the VOC |
| **`.?`** | print this list |

**`n` defaults to 1 everywhere, and the spaces shown are required.** `.d2`
deletes the second stack line and `.d 2` looks for a VOC record called `2`.

`.s` and `.r` together are the whole workflow: type the lines, then save them
under a name, then recall them later to edit. **`.s` writes a sentence when the
range is one line and a paragraph when it is more**, so the record type follows
from what you saved rather than from anything you say.

`.x` *file* *id* is the one that reaches outside the VOC — the file name and the
record id are each folded as typed, then lower, then upper.

**A dot command that is not one of these is not an error.** It is left alone and
run as an ordinary command, so a verb whose name begins with a dot still works.

> **`.d` does not find a lower-case VOC record typed in upper case, and `.l`
> and `.r` do.** `.l` and `.r` try the name as typed, then lower case, then
> upper case. `.d` tries only as typed and then upper case. A paragraph saved as
> `daily` can be listed and recalled by typing `DAILY` and cannot be deleted by
> typing `DAILY`. **Type the name in the case you saved it in and all three
> work.**

### Editing the line you are on

**There are two help texts and they are different.** `?` on its own prints the
key map below; `.?` prints the dot-command list above. Neither is the `help`
verb, which does not exist — see *What is not here*.

The key map is the same whether you reached the line by typing it or by
recalling it:

| Key | | Also |
|---|---|---|
| `Ctrl-A` | start of line | Home |
| `Ctrl-E` | end of line | End |
| `Ctrl-B` / `Ctrl-F` | back / forward one character | Cursor left / right |
| `Ctrl-P` / `Ctrl-N` | previous / next command | Cursor up / down |
| `Ctrl-Z` | previous command | Cursor up |
| `Ctrl-R` | reverse search | |
| `Ctrl-D` | delete character | Delete |
| `Ctrl-H` | backspace | Backspace |
| `Ctrl-K` | kill line | |
| `Ctrl-O` | toggle overlay | Insert |
| `Ctrl-T` | transpose characters | |
| `Ctrl-U` | upcase all | |
| `Ctrl-G` | exit the stack | |

**A line ending in `?` is put on the stack without being run.** That is the way
to park a half-written command while you go and look something up.

### Saving the stack across sessions

| | |
|---|---|
| **`save.stack`** {*name*} | write the stack to a named record |
| **`get.stack`** {*name*} | read it back |
| **`clear.stack`** | empty it |

Both prompt for the name if you leave it off.

## @-variables

`set` assigns an @-variable, which is then substituted into later command lines
wherever its name appears.

```
set name value
set name eval expression
```

Without `eval` the value is taken literally. With `eval` the text is evaluated
first, and the evaluation handles the four arithmetic operators on numeric
operands. `list.vars` shows what is currently set.

The variables the system sets are readable the same way — `@system.return.code`
is the one worth knowing, because most verbs set it and `report.src` exists to
show it.

## Session verbs

| | |
|---|---|
| **`who`** | your user number and the account you are in |
| **`who.am.i`** | the same information at more length |
| **`logto`** *account* | change account without logging out |
| **`off`** · **`quit`** | end the session |
| **`option`** {*name*} {**on**\|**off**\|**display**} | set or show a session option |
| **`option all off`** | turn every session option off at once |
| **`alias`** *command* *target* | make *command* run as *target* |
| **`alias`** *command* | remove that alias |
| **`alias`** | list the aliases |
| **`clear.abort`** | clear a pending abort condition |
| **`set.exit.status`** *n* | set the numeric status SD exits with |
| **`report.src`** {**on**\|**off**} | show `@system.return.code` after each command |

`who` answers with your user number and the account you are in:

```
39 DON
```

**After a `logto` it grows a third part, and that is the useful one:**

```
29 SDSYS from DON
```

**`from DON` is the account you logged in as**, not the one you are in and not
your Windows account. So the short form means *I am still where I started* and
the long form means *I have moved* — which makes `who` the quick way to find
out whether a `logto` actually took effect.

**`logto sdsys` requires an elevated Windows session in this port.** Entering
`SDSYS` is what confers administrator rights, so it is gated on the operating
system rather than on an SD password, and the elevation obtained by one `logto`
is deliberately not carried into the next one. `who` reports the account you are
in, which is the quick way to confirm a `logto` actually happened.

## What is not here

**There is no online help and `help` is not a verb.** The command processor
still has internal verb 14 reserved for it and the routine is an empty stub —
its body is commented out and it returns immediately. **No VOC record points at
it**, in any account type, so the name is not even recognised. The F1 key at the
command prompt reaches the same empty routine and therefore does nothing. **This
documentation is the help system.**

**`umask` is implemented and unreachable.** Internal verb 35 is a working
routine that reports or sets the file-creation mask, and **no VOC record points
at it either**. It cannot be typed. `umask()` from SD BASIC still works — see
[SD Basic - System and Environment](16-sd-basic-system-and-environment.html).

**PROC is removed.** So are `sed` and `update.record`. A `PQ`-type VOC record
is **refused by name** rather than being reported as a bad dispatch code,
because the record itself is valid PROC and it is the interpreter that is gone.
Nothing that ships is type `PQ`, so this can only be met in a VOC record
somebody wrote.

**`menu` records are dispatched but no menu ships.** Type `M` is handled and
there is no shipped example to look at.

## Who has these verbs

Everything on this page is in a **standard** account except the last two, which
are administrator-only:

| | |
|---|---|
| **standard** | `abort` `alias` `clear.abort` `clear.stack` `display` `get.stack` `go` `if` `list.vars` `logto` `off` `option` `pause` `quit` `report.src` `save.stack` `set` `set.exit.status` `stop` `who` `who.am.i` |

**Everything on this page is in a standard account.** An account that does not
have a verb does not have the VOC record for it — the name is simply not
recognised rather than refused.

**The two `OS` verbs are the exception and are not documented here.** `sh` and
`!` reach the Windows shell, are administrator-tier, and are gated a second time
by a list of who may use them. They are in the **administrator documentation**,
under *Operating System Access*, which is a separate set.

## See also

[SD TCL - Files and Records](20-sd-tcl-files-and-records.html) ·
[SD Basic - Program Control](02-sd-basic-program-control.html) ·
[SD Basic - System and Environment](16-sd-basic-system-and-environment.html).
