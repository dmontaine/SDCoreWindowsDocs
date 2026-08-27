Title: SD TCL - Locks
Subtitle: Seeing what is locked, giving your own locks back, taking a numbered lock, and forcing somebody else's open.

***THERE ARE TWO UNRELATED THINGS CALLED A LOCK AND SIX VERBS DIVIDED BETWEEN
THEM.*** Knowing which family a verb belongs to is most of what this page has
to say, because the two do not interact at all and the names do not make that
obvious.

| | | |
|---|---|---|
| **database locks** | on a record or on a whole file. Taken by `readu`, `readl` and `filelock` in a program, and by `ed` while it holds a record | `list.readu` `release` `unlock` |
| **task locks** | 64 numbered flags, 0 to 63, with **no connection to any data**. A program takes one by agreement to keep other programs out of something | `list.locks` `lock` `clear.locks` |

`unlock` straddles them and is the only verb that does: `unlock tasklock` *n*
forces a task lock, everything else about it is database locks.

The statements a program uses to take these locks are in
[SD Basic - Locks and Transactions](14-sd-basic-locks-and-transactions.html),
and this page does not repeat them.

SD folds case, so a command may be typed in either case. Commands are shown here
in lower case. In the tables, *italics* mark something you supply and **bold**
marks a word typed as it stands; braces mark an optional part.

> **Every listing on this page was produced by running it**, on SD Core for
> Windows W1.0-0. The database-lock listings come from a program that took the
> locks first and then ran the verb against itself, because a lock nobody holds
> is not something a listing can show.

## What is locked: `list.readu`

```
list.readu {user.no} {detail} {wait} {no.page} {lptr {n}}
```

With nothing held, it says so, and says it about the **whole system** rather
than about you:

```
:list.readu
There are no active file, read or update locks held by any user
```

With locks held — here an update lock on `R1` and a read lock on `R2`, taken by
user 23:

```
User File Path........................... Type Id..............................
  23    1 /cygdrive/c/ProgramData/SD/user RU   R1
          _accounts/don/ZZLK31A
  19    4 /cygdrive/c/ProgramData/SD/user RU   zzlock31
          _accounts/don/voc
  23    1 /cygdrive/c/ProgramData/SD/user RL   R2
          _accounts/don/ZZLK31A
```

| | |
|---|---|
| **`User`** | the SD user number holding it — [`listu`](30-sd-tcl-processes-and-phantoms.html#who-is-logged-in-listu) turns that into a person |
| **`File`** | SD's internal file number, and **this is the number `unlock` wants** |
| **`Path`** | wrapped over as many lines as it needs, in POSIX form |
| **`Type`** | `RU` update lock · `RL` read lock · `FX` exclusive file lock · `SX` shared file lock · `WAIT` a session waiting for one |
| **`Id`** | the record id; blank for a file lock |

**A file lock has no id**, and looks like this:

```
User File Path........................... Type Id..............................
  23    1 /cygdrive/c/ProgramData/SD/user FX
          _accounts/don/ZZLK31A
```

***THE PATH IS THE POSIX ONE AND THAT IS NOT A DISPLAY FAULT.*** SD holds file
paths internally in `/cygdrive/c/...` form on this port. It is the same path
`C:\ProgramData\SD\...` names; see
[SD Basic - File Handling](07-sd-basic-file-handling.html).

### The keywords

**`detail`** prints the record-lock budget above the listing:

```
:list.readu detail
Record lock limit (NUMLOCKS) = 100, Current = 0, Peak = 2
There are no active file, read or update locks held by any user
```

***`Peak` IS THE ONE TO WATCH.*** `Current` tells you about this instant, which
is rarely the instant that mattered. A peak close to the limit is how you find
out that `NUMLOCKS` needs raising before a program fails with a lock table
full. The limit is the `NUMLOCKS` configuration parameter, reported by
[`config`](32-sd-tcl-accounts-and-security.html#reading-and-setting-configuration-config).

**A user number** restricts the listing to one session — the same three-lock
system as above, asked about user 23 only:

```
User File Path........................... Type Id..............................
  23    1 /cygdrive/c/ProgramData/SD/user RU   R1
          _accounts/don/ZZLK31A
  23    1 /cygdrive/c/ProgramData/SD/user RL   R2
          _accounts/don/ZZLK31A
```

**`wait`** adds the sessions that are **waiting** for a lock, as `WAIT` rows.
They are left out by default, which means the plain listing shows the cause of
a hold-up and not its victims. **Ask for `wait` when something is stuck** — the
answer to *"who is blocked"* is the row that is normally hidden.

### A lock outliving its session is a real thing and this is how you see it

The `19 … RU zzlock31` row above is not part of the example. It is a lock on a
record in an account's `voc` file, left behind by user 19 — a session that was
killed while it held it. **A dead session's locks are not released**, any more
than its user-table entry is, and everything that wants that record waits for a
process that is not there.

***THAT IS WHAT THE `User` COLUMN IS FOR.*** Take the number to
[`pstat`](30-sd-tcl-processes-and-phantoms.html#what-a-session-is-doing-pstat):
*(Not responding)* means there is nothing behind the lock and the entry needs
clearing rather than waiting for. The clearing is an elevated `sd -cleanup`, or
`unlock` below.

## Giving your own locks back: `release`

```
release filename id {id …}
release filelock filename
```

**`release` gives back locks this session holds**, and only this session's — it
is the TCL form of the BASIC statement of the same name, and it needs no
special rights. The file is named the way you would name it to any other verb.

```
:release
File  not found
:release voc
Record id required
```

**A record id is compulsory in the first form**; there is no *release
everything* at the prompt. `release filelock` *name* gives back a file lock,
which has no id to give.

## Forcing somebody else's: `unlock`

```
unlock file n {user n} record.id {record.id …}
unlock file n {user n} all
unlock file n {user n} filelock
unlock tasklock n {n …}
```

***THIS IS THE VERB FOR SOMEBODY ELSE'S LOCK, AND IT NEEDS AN ELEVATED
SESSION*** — having the verb is not enough:

```
:unlock
Command requires administrator privileges
```

**It names a file by number, not by name.** That is the `File` column of
`list.readu`, and it is deliberate: the lock is on a file the machine has open,
which may not be in your VOC at all and may be reached under different names in
different accounts. `release`, which acts on your own locks in your own
account, takes a name for the same reason.

| | |
|---|---|
| **`file`** *n* | the file, by the number `list.readu` printed |
| **`user`** *n* | restrict to one session's locks |
| **`all`** | every record lock matching, rather than named ids |
| **`filelock`** | the file lock, which cannot be combined with record ids |

**A file number or a user number is compulsory** — *Either a file number or a
user number must be specified* — so there is no way to type an `unlock` that
means *everything on the machine*.

> ***UNLOCKING IS NOT FREE AND SD CANNOT MAKE IT SO.*** A lock is a promise the
> holder is relying on. Forcing one open while its owner is alive lets two
> sessions write the same record, and neither will be told. **Establish that
> the holder is dead first** — `pstat` on the user number, `listu` for
> *(logout pending)* — and prefer clearing the session to clearing the lock.

## Task locks: `lock`, `clear.locks`, `list.locks`

Task locks are **64 numbered flags with no meaning of their own**. They mean
whatever the programs using them agree they mean — the usual use is *only one
session runs this job at a time*, where the thing being protected is not a
single file and so cannot be guarded with a file lock.

```
list.locks
lock n {no.wait}
clear.locks {n}
```

An idle system:

```
:list.locks
No task locks reserved by any user
```

and one where lock 5 is held by user 16, `*` marking your own session:

```
:list.locks
 0:       1:       2:       3:       4:       5: 16*   6:       7:
 8:       9:      10:      11:      12:      13:      14:      15:
16:      17:      18:      19:      20:      21:      22:      23:
```

*(64 numbers over eight rows; the rest are blank and are cut here.)*

### `lock` waits unless you tell it not to

```
:lock 5 no.wait
Set task lock 5
:lock 5 no.wait
Task lock already owned by this process
```

***WITHOUT `no.wait` IT WAITS FOR EVER.*** It prints *Waiting for task lock to
become available* once and then retries every two seconds until it gets it,
which is right for a job that must run and wrong for anything with nobody
watching. **`no.wait` turns the wait into a refusal** — *Task lock is already
in use* — which a script can act on.

Taking a lock you already hold is not an error; it says so and carries on.

### `clear.locks` gives back your own

```
:clear.locks 5
Released task lock 5
:clear.locks
All task locks released
```

**With no number it releases all 64 that this session holds**, and the message
says *all* whether it held any or not. With a number it releases that one.

| | |
|---|---|
| *Released task lock n* | it was yours and it is now free |
| *Task lock n is held by another process* | it is not yours; **`clear.locks` will not take it** |
| *Task lock n is not held by any process* | it was already free |
| *Task lock number must be in range 0 to 63* | measured with `clear.locks 99` |

***`clear.locks` CANNOT TAKE SOMEBODY ELSE'S AND `unlock tasklock` CAN.*** That
is the whole difference between the two, and it is why one is a standard part
of running a job and the other is an administrator's tool.

**Task locks are released when a session ends normally.** They are not part of
any file, so nothing has to be written and nothing is left half-done.

> ***A SESSION KILLED FROM OUTSIDE SD IS THE EXCEPTION, AND IT IS THE ONE THAT
> CATCHES PEOPLE.*** `sd -cleanup` gives back a dead session's record locks and
> file locks and **does not give back its task locks**; they stay held, by a
> user number nothing is behind, until SD itself is restarted. `list.locks`
> shows the number with an owner and `clear.locks` will not take it, because it
> is not yours. **`unlock tasklock` *n*, elevated, is the way out** — that is
> the forced form, and this is what it is for. The defect is recorded in the
> project's fix lists.

## Who has these verbs

| | |
|---|---|
| **standard** | `release` |
| **administrator** | `list.readu` `list.locks` `lock` `clear.locks` `unlock` |

***ONLY `release` IS IN AN ORDINARY ACCOUNT, AND THE SPLIT IS EXACTLY THE ONE
THE PAGE DESCRIBES***: giving back what you hold is something any session may
do, and everything that looks at, takes or forces a lock across the machine is
an administrator verb. `unlock` needs an elevated session on top of that.

## See also

[SD Basic - Locks and Transactions](14-sd-basic-locks-and-transactions.html) ·
[SD TCL - Processes and Phantoms](30-sd-tcl-processes-and-phantoms.html) ·
[SD TCL - Files and Records](20-sd-tcl-files-and-records.html).
