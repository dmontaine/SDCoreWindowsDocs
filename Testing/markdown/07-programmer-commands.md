Title: Programmer commands
Subtitle: The 42 development verbs a standard account does not get, and what withholding them does and does not do.

A **standard** account gets 77 verbs — enough to run an application and nothing
that edits code or data in bulk. A **programmer** account gets those plus the
42 below. An **administrator** account gets all of them, plus
[21 more](06-administrator-commands.html).

This split does not exist in OpenQM, where every account gets the same VOC.
None of the verbs below is new; what is new is that an account has to be
created as `programmer` or `administrator` to receive them.

```
create.account user fred programmer both
```

## What is withheld, by function

### Compile, catalogue and run

| | |
|---|---|
| **`basic`** | compile SD BASIC source |
| **`catalog`** · **`catalogue`** | add to the catalogue |
| **`delete.catalog`** · **`delete.catalogue`** | remove from it |
| **`compile.dict`** | compile dictionary items |
| **`run`** | run a compiled program |
| **`map`** | show a program's map |
| **`generate`** | generate source |
| **`phantom`** | start a background process |

> **Cataloguing globally requires an administrator.** Adding to or removing
> from the system-wide catalogue is an administrator action; private and local
> cataloguing still work in a programmer's own account. That is a separate
> control from the VOC tier.

### Edit and debug

| | |
|---|---|
| **`ed`** | the line editor. Needs nothing installed |
| **`edit`** | a **full-screen** editor — opens the record in Microsoft Edit |
| **`micro`** | a **full-screen** editor — opens the record in micro |
| **`debug`** | the BASIC debugger |
| **`pstat`** · **`pdebug`** · **`pdump`** · **`dump`** | process introspection |

The debug family moved from administrator to programmer deliberately — a
programmer needs these to debug their own code.

### Editors

***THERE ARE TWO, AND THEY BEHAVE IDENTICALLY.*** The verb chooses the editor
and nothing else changes:

| | |
|---|---|
| **`edit`** | **Microsoft Edit** — ships in current Windows builds |
| **`micro`** | **micro** — never ships with Windows; the installer fetches it |

```
edit  bp myprog
micro bp myprog
edit  dict customers name
```

***`edit` USED TO BE A SECOND NAME FOR `ed`, AND IS NOT ANY MORE.*** If you
have been typing it to get the line editor, you will now get a full screen.

Either verb writes the record to a working copy, opens the editor on it, reads
it back, and asks whether to save. For a `bp` record it then offers the compile
and the catalogue, which is the loop the old **`micro`** verb had.

**Both are terminal editors**, so both work over ssh as well as at the console.
Where a machine does not have one, the SD installer installs it; if that could
not be done, the verb says so and names the command that installs it.
`C:\ProgramData\SD\install-editors.log` records what the installer found.

**`ed` is unaffected and is still there.** Nothing has been taken away.

> ***WHAT AN EDITOR CAN REACH, and it is worth knowing before you hand this to
> somebody.*** An editor can open any file the person running it is allowed to
> open, so both verbs reach beyond SD's own files. Neither is a shell — neither
> editor can run a command — and standard accounts have neither verb, nor does
> any session that arrived over the API. **The line here is the account tier,
> not the `os.users` list that governs `sh`.** See
> [Security](12-security.html).

The removed full-screen editors are a different matter: `sed`,
`update.record` and `modify` are gone and are not coming back. See
[Not in SD Core](14-not-in-sd-core.html).

### Files

| | |
|---|---|
| **`create.file`** · **`delete.file`** · **`clear.file`** | the life of a file |
| **`configure.file`** | change a file's configuration |
| **`analyse.file`** · **`analyze.file`** | report on a file's internals |
| **`fstat`** | file statistics |
| **`hsm`** | hashed-file statistics monitoring |
| **`set.trigger`** | attach a trigger |
| **`cd`** | change directory |

### Indexes

**`create.index`** · **`delete.index`** · **`build.index`** · **`make.index`** · **`list.index`**

### Bulk record editing

| | |
|---|---|
| **`copy`** · **`copyp`** | copy records |
| **`delete`** | delete records |
| **`rename`** | rename records |
| **`reformat`** · **`sreformat`** | reformat |
| **`sort.item`** | sort |
| **`cname`** | change a record's name |
| **`delete.common`** | clear a common block |

## What the split does and does not do

***IT IS A POSTURE, NOT A BOUNDARY.*** An administrator can copy any verb into
any account's VOC afterwards. A reduced VOC is where an account **starts**, not
something SD enforces at run time.

**What actually is enforced** is elsewhere, and worth knowing before you rely
on the tier for anything:

| | |
|---|---|
| File permissions | Windows ACLs on the data tree — see [Security](12-security.html) |
| Where an account may sign in | the `sdsshonly` deny rights — see [ssh access](08-ssh-access.html) |
| Reaching the operating system | the `os.users` permit list, both **`sh`** and `OS.EXECUTE` |
| What an API session may open | the containment gate, rooted at the account the session stands in |

**A programmer with `OS.EX` set has the operating system**, whatever their VOC
says, because they can write and run BASIC. That is why field 2 of `os.users`
exists and why it is now enforced — see
[Administrator commands](06-administrator-commands.html#the-shell-escapes-sh-and).

## Two things to know when you compile

**`basic` no longer creates an object file it can never open again.** Compiling
into a reused file name previously produced an object SD could not subsequently
open.

**Object code and the catalogue are replaced on upgrade.** The compiled
programs, the BASIC source SD ships, the messages, include records and VOC
templates are all overwritten by a new release. **Anything you have written
into the SDSYS `bp` file, and anything you have compiled from it, survives an
upgrade untouched** — SD now ships nothing into that file at all, so it is
created empty and is yours.

## The full list of the 42

**`basic`** · **`catalog`** · **`catalogue`** · **`delete.catalog`** · **`delete.catalogue`** ·
**`compile.dict`** · **`cd`** · **`generate`** · **`phantom`** · **`run`** · **`map`** · **`debug`** ·
**`ed`** · **`edit`** · **`micro`** · **`create.file`** · **`delete.file`** · **`clear.file`** ·
**`configure.file`** · **`analyse.file`** · **`analyze.file`** · **`fstat`** · **`hsm`** ·
**`set.trigger`** · **`create.index`** · **`delete.index`** · **`build.index`** ·
**`make.index`** · **`list.index`** · **`copy`** · **`copyp`** · **`delete`** · **`rename`** ·
**`reformat`** · **`sreformat`** · **`sort.item`** · **`delete.common`** · **`cname`** ·
**`pstat`** · **`pdebug`** · **`pdump`** · **`dump`**

> **This list was 42, then 41 when `modify` was removed from SD Core, and is
> 42 again now `micro` is back.** A standard account's count did not move on
> either occasion: both verbs were on both sides of the arithmetic at once —
> in `NEWVOC` and in the standard tier's omit list.
