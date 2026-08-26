Title: Security
Subtitle: Who you are, what that gets you, and what actually protects the database.

The identity model in SD Core is not OpenQM's and not SD on Linux's. It is
worth understanding before you test anything else, because several behaviours
that look like bugs are consequences of it.

## Signing in asks for no password

***THE OPERATING SYSTEM HAS ALREADY AUTHENTICATED YOU. SD ASKS WINDOWS WHO YOU
ARE.***

| | |
|---|---|
| `sd`, no account named | you land in **the SD account with your own name** |
| no SD account of that name | refused — *Account %1 not in register* (5018) |
| not in `sdusers` | refused at the door — *not registered for SD use* (5009) |
| `sd -A<name>` | **refused unless `<name>` is your own account** (10051) |
| an elevated session | **your own account, like everybody else.** `logto sdsys` afterwards |
| `logto sdsys` | asks for no password. **The gate is elevation** — a UAC consent prompt if the session is not already elevated, and 10002 with an audited `LOGTO REFUSED` if that fails |

**There is no SDSYS password.** There is deliberately no second shared secret
held by every administrator — that is the OpenQM weakness this exists to
remove.

**`sd <command>` no longer asks you to set a password**, which it used to do by
walking into a prompt it could never be given input for.

## Being an administrator

***IF YOU CAN LOG IN TO WINDOWS AS AN ADMINISTRATOR, YOU ARE AN ADMINISTRATOR
OF SD.*** The person who installs SD is an SD administrator without any further
step.

Two different questions are asked in two different places, and both are wanted:

| Question | How it is answered | Gates |
|---|---|---|
| *Are you an administrator?* | the account's groups in the SAM | `sd -start` — starting the server should not demand elevation of somebody already an administrator |
| *Are you elevated?* | the process token | **reaching SDSYS**, and every privileged action |

A UAC-filtered token carries `Administrators` as *deny only*, so these give
different answers for the same person, and conflating them is the easy mistake.

***ONE PROPERTY TO ACCEPT CONSCIOUSLY.*** `Administrators` is machine-wide, so
anyone in it for an unrelated reason — the machine's own administrator, a
domain admin, an IT tool's service account — gets SDSYS. Linux sudoers is
machine-wide too, so this is parity rather than a Windows weakness, but it
should be a decision rather than a discovery.

## Understand what the security position rests on

***NOTHING IN SD CHECKS A SECRET AT CONSOLE OR ssh LOGIN. ACCESS IS ENTIRELY
OPERATING-SYSTEM GROUP MEMBERSHIP.***

That is not a weakening. Every SD process opens the database directly, in your
own process, under your own token. There is no data server standing between
you and the files. So:

> **While SD runs as the invoking user, account passwords organise access; they
> do not secure it.**

A password gate inside SD is not a file security boundary. The old password
model implied one the filesystem never enforced. This states the real position
instead of dressing it up.

**Passwords still matter for the API**, which is a separate door and does
require one — see [API access](08-api-access.html).

## What actually protects the database

### The tree is private from the rest of the machine

`C:\ProgramData` grants `BUILTIN\Users` read and execute by inheritance, so the
Windows default is world-readable and snooping needs no privilege at all. The
installer **breaks inheritance first** and grants narrowly: SYSTEM,
`Administrators` and `sdusers`.

***THIS IS THE STEP THAT MAKES THE DATA PRIVATE, AND NOTHING AT RUN TIME
SUBSTITUTES FOR IT.***

### Your account directory is locked to you

`C:\ProgramData\SD\user_accounts\<name>` is granted to that account's own
group, to administrators and to the system, **and to nobody else**.

Before this, every SD user could read and rewrite every other user's account
files from Explorer or a command prompt — outside SD, so none of SD's own
permission checks applied. SD has always refused to let you `logto` an account
you are not a member of; this makes the files agree with that.

**Nothing you type changes, and your own account is unaffected** — you are a
member of its group.

> A directory whose Windows group has been removed is **skipped deliberately**
> and named in the report. Locking it to a group that no longer exists would
> take the account away from the person who owns it.

### The system directories are read-only to ordinary users

Seven parts of the SD data area could be changed by anyone in `sdusers`. They
are now readable by everyone who needs them and writable only by an
administrator:

```
sdsys\accounts    the register of accounts
sdsys\$map        sdsys\messages    sdsys\newvoc
sdsys\bp          sdsys\cat         SD's own programs
sd.conf           the configuration read at start-up
```

**Nothing an ordinary user does needs to write them** — measured on a real
session first, across fifteen commands including the spooler, saved lists and a
phantom. The commands that *do* write them are already administrator commands
and are unaffected.

***`sdsys\$ipc` IS DELIBERATELY UNCHANGED.*** Every session writes to it, and
it is how a `phantom` is given its command.

The global catalogue and the pcode library are locked the same way.

> ***AN EXISTING INSTALLATION IS NOT CHANGED BY AN UPGRADE***, because the
> installer never overwrites a data area that is already there. To apply it to
> one you already have, run this once per path from an elevated prompt:
>
> ```
> powershell -File "C:\Program Files\SD\secure-sysdirs.ps1" -Path "C:\ProgramData\SD\sdsys\accounts"
> ```

### The credential file

***ON INSTALLS MADE BEFORE 17 Aug 2026, EVERY SD USER COULD WRITE THE FILE SD
KEEPS ACCOUNT PASSWORDS IN.*** No password is stored there — SD keeps a
scrambled verifier that cannot be turned back into a password — but **being
able to replace one was enough**: a user could put in a verifier for a password
of their own choosing and sign in as somebody else, including through the API.

The installer was always meant to lock that file down and never did. The step
ran, reported nothing, and had no effect, because of a quoting fault in how it
was called. **Nothing in the install looked wrong.**

**Reinstalling is what fixes it.** To check without reinstalling, from an
**ordinary** (not administrator) prompt:

```
icacls "C:\ProgramData\SD\sdsys\$CRED"
```

If that prints permissions, the file is still open. ***If it says "Access is
denied", it is protected — which is what you want.***

## Privileged work is done through a script, not a command line

When SD creates an account, sets a password or edits a group, it writes a short
script to a file and runs it, rather than putting a password on a command line
where any local user could read it through Task Manager or WMI.

Those scripts go in **`PSTMP`**, a directory of its own inside the database
directory, where each file belongs to the session that wrote it. Other SD users
cannot read or change them.

Before that they went where every SD user could write, and the second
consequence was the serious one: **another SD user could replace the script
between SD writing it and SD running it, and their version would run with full
administrator privilege.**

***IF `PSTMP` IS MISSING, SD REFUSES THE PRIVILEGED WORK*** rather than falling
back to the old location. You see the command fail rather than quietly running
unprotected.

## The audit trail

`C:\ProgramData\SD\sdsys\audit` records **every login, every refused login,
every `logto`, every refused `logto`, and every `grant` and `revoke`**, with
date, time and the Windows user it belonged to.

```
2026-08-16 11:42:07 user=don uid=1 pid=8624 LOGTO account=SDSYS
```

***THE REFUSALS ARE THE INTERESTING HALF.*** An entry saying somebody who is
not an administrator asked for SDSYS by name, or asked for an account they have
not been granted, is the thing worth seeing. **Failed API logins are recorded
too, with the reason.**

**This is not the error log and does not behave like it.** The error log throws
away its oldest half when it fills; the audit file is **renamed with the date
and time and a new one started, so nothing is ever discarded.** Removing the
old ones is your decision — SD will not do it for you, and they will
accumulate.

| SD users can | SD users cannot |
|---|---|
| **add** to it | read it, change a record in it, empty it, rename or delete it |

**Windows itself refuses, not SD**, so a user cannot quietly remove the line
that records what they did. Administrators can read it and do anything else to
it as well: this raises the floor against ordinary users rather than trying to
constrain somebody who owns the machine.

> Windows keeps its own separate record of account and group changes in the
> Security event log. **Read the two together.**

## What is still not true

***SD USERS ARE NOT ISOLATED FROM EACH OTHER'S DATA AT THE FILE LEVEL, BEYOND
THE PER-ACCOUNT DIRECTORY LOCK.*** Everyone who uses SD needs file access to
the tree, because their own process does the I/O. Anyone deploying SD for ten
people over ssh should be told that plainly.

**SD has no file-level access control of its own** on the console and ssh
paths. The one place a path gate does exist is the API, where a session is
confined to the account it stands in — see
[API access](08-api-access.html#a-session-is-confined-to-its-own-account).
