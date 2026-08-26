Title: Programmer commands
Subtitle: The 41 development verbs a standard account does not get, and what withholding them does and does not do.

A **standard** account gets 77 verbs — enough to run an application and nothing
that edits code or data in bulk. A **programmer** account gets those plus the
41 below. An **administrator** account gets all of them, plus
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
| **`ed`** · **`edit`** | the line editor, and **the editor this system uses** |
| **`debug`** | the BASIC debugger |
| **`pstat`** · **`pdebug`** · **`pdump`** · **`dump`** | process introspection |

The debug family moved from administrator to programmer deliberately — a
programmer needs these to debug their own code.

***THERE IS NO FULL-SCREEN EDITOR.*** `sed`, `update.record` and `modify` have
all been removed from SD Core. **`ed`** is the editor. See
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

## The full list of the 41

**`basic`** · **`catalog`** · **`catalogue`** · **`delete.catalog`** · **`delete.catalogue`** ·
**`compile.dict`** · **`cd`** · **`generate`** · **`phantom`** · **`run`** · **`map`** · **`debug`** ·
**`ed`** · **`edit`** · **`create.file`** · **`delete.file`** · **`clear.file`** ·
**`configure.file`** · **`analyse.file`** · **`analyze.file`** · **`fstat`** · **`hsm`** ·
**`set.trigger`** · **`create.index`** · **`delete.index`** · **`build.index`** ·
**`make.index`** · **`list.index`** · **`copy`** · **`copyp`** · **`delete`** · **`rename`** ·
**`reformat`** · **`sreformat`** · **`sort.item`** · **`delete.common`** · **`cname`** ·
**`pstat`** · **`pdebug`** · **`pdump`** · **`dump`**

> **This list was 42 until `modify` was removed from SD Core.** A standard
> account's count did not move, because `modify` was already withheld from it —
> it left both sides of the arithmetic at once.
