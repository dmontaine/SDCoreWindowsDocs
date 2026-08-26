Title: Administrator commands
Subtitle: The 21 verbs an administrator account gets above a programmer, and how to use them.

An administrator account receives everything a programmer account does, plus
the 21 verbs below. In OpenQM most of these lived in `SYSTEM` and you reached
them by being there; in SD Core they are in the administrator's **own** account
VOC, so an SD administrator no longer has to `logto sdsys` to administer
anything.

**Being an SD administrator means being an elevated Windows administrator.**
There is no SD password that confers it. Several of these verbs check for
elevation and say so rather than failing obscurely — see
[Security](12-security.html).

## Accounts

```
create.account  user <name> {administrator | programmer} <ssh|api|both|none>
create.account  group <name>
delete.account  <name>
modify.account  <name> <ssh|api|both|none>
modify.account  add <group> <user>
update.account
clean.account
```

Covered in full in [Account types](05-account-types.html). The three points
worth repeating here:

- **One of `ssh`, `api`, `both`, `none` is required** on `create.account user`.
  There is no default.
- **`modify.account` says what the access *is*, not what to add.**
  `modify.account fred api` takes ssh away.
- **`update.account` only ever adds VOC records**, never removes them.

**`clean.account`** tidies an account's workspace. **`update.account`** is the one you
run in each account after upgrading SD.

## Grants

```
grant       <account> to   <user>
revoke      <account> from <user>
list.grants <account>
```

All three need an elevated session.

***A GRANT OR A REVOKE DOES NOT TAKE EFFECT UNTIL THE PERSON SIGNS OUT OF
WINDOWS AND BACK IN.*** Entry to an account is Windows group membership, and
Windows fixes that at logon. **Somebody you have just revoked keeps the account
until they get a new token.** Both verbs print the reminder every time.

## Passwords and field encryption

```
modify.password {<account>}
encrypt.field
```

**`set.password` was renamed to `modify.password`** — every account now has a
password from the moment it is created, so there is nothing to *set* for the
first time.

***A PASSWORD CANNOT BE TYPED ON THE COMMAND LINE.*** **`modify.password`** refuses
one given as an argument. A password on a command line is visible to any local
user through Task Manager or `Get-CimInstance Win32_Process`, so SD prompts for
it instead, masked.

The password matters for **API logins only**. Console and ssh logins ask for
nothing — see [Security](12-security.html).

## Locks and sessions

```
lock / unlock
list.locks / clear.locks
listu / list.readu
logout
```

***`unlock` is the one to know about.*** It clears a record lock left behind by
a session that died holding one. Without it the only way to release such a lock
is to stop and restart SD, which disconnects everybody.

> An earlier changelog entry claimed **`unlock`** had never worked on any release
> this port was built from, because its VOC entry carried description text in
> the type field. **That conclusion was wrong and has been withdrawn.** SD
> allows a type code followed immediately by comment text — the same rule PI,
> PI/open and UniVerse follow — so `Verb to unlock records` reads as type `V`
> with a comment, and **`unlock`** dispatched normally all along. The record has
> been rewritten as a bare `V` for consistency, and behaves no differently.
> **`copyp`** carried the same style of entry and was likewise working.

**`listu`** and **`list.readu`** report sessions and read locks; **`logout`** ends another
session.

## System state

```
config
set.date
```

**`config`** reports the configuration parameters in force.

> **`CREATUSR` is gone.** **`config`** no longer lists it and `config('CREATUSR')`
> returns nothing. A `CREATUSR` line in `sd.conf` is still accepted and
> ignored, so a configuration file brought from a Linux install still works.
> You can delete the line.

## The shell escapes — `sh` and `!`

***WHO MAY USE `sh` IS A LIST YOU KEEP, NOT A MATTER OF ELEVATION.***

This is one of the larger behavioural changes in the port. **`sh`** used to require
an elevated session — and **an ssh session can never be elevated**, so
programmers, the people who actually need a shell, were the ones who could
never have one.

### The list

From SDSYS:

```
ed os.users don
```

One record per person, **keyed by the name they sign in with, not by the
account name**. The login name follows the person, so it does not change when
they **`logto`** somewhere else.

| Field | Controls | Value |
|---|---|---|
| 1 | `SH` — a shell at the command prompt | `yes`, or anything else for no |
| 2 | `OS.EX` — `OS.EXECUTE` from inside a program | `yes`, or anything else for no |

**A missing record, or a missing file, means no.** An installation that has
never set `os.users` up denies both to ordinary accounts.

### Both fields are enforced

`OS.EXECUTE` used to be unchecked entirely, so **any account that could write a
program had the operating system** and the **`sh`** restriction could be walked
around by anyone able to type BASIC. Field 2 is now what decides whether
`OS.EXECUTE` may run. The refusal reads *`<name>` is not permitted to use
OS.EXECUTE*.

The two fields are independent, and the useful combination is the third row:

```
unlisted            sh refused    OS.EXECUTE refused
SH=yes OS.EX=no     sh RUNS       OS.EXECUTE refused
SH=no  OS.EX=yes    sh refused    OS.EXECUTE RUNS      <- programs may shell
                                                          out; the person at
                                                          the prompt may not
elevated            sh runs       OS.EXECUTE RUNS
```

SD's own system programs are exempt, so **`create.account`** and the **`sh`** verb work
as before.

### Three rules that go with it

***ONLY AN ADMINISTRATOR CAN EDIT THE LIST.*** `os.users` is read-only to
everybody else on disk, and **that ACL is the whole of what stops a user
granting themselves a shell. Do not loosen those permissions.**

**A listed person gets a real shell** — pipes, redirection and chaining all
work: `sh dir | more`. Anyone not on the list who reaches **`sh`** by being
elevated still gets the restricted form, which rejects those characters.

**An elevated session keeps `sh` whatever the list says**, deliberately, so an
empty list cannot lock the machine's own administrator out.

### Neither is available over the API

**`sh`** and `OS.EXECUTE` are refused to a session that arrived over the API. They
used to run **as the LocalSystem account**, so a remote client could run any
command on the machine with full privilege — more than the administrator at the
keyboard gets. An API session is no longer treated as an administrator for any
purpose.

## The full list of the 21

**`create.account`** · **`delete.account`** · **`modify.account`** · **`update.account`** ·
**`clean.account`** · **`grant`** · **`revoke`** · **`list.grants`** · **`unlock`** ·
**`modify.password`** · **`encrypt.field`** · **`config`** · **`listu`** · **`list.readu`** ·
**`list.locks`** · **`clear.locks`** · **`lock`** · **`logout`** · **`set.date`** · **`sh`** · `!`

> **Twelve of these left `NEWVOC` on 24 Aug 2026** — **`config`**, **`listu`**,
> **`list.readu`**, **`list.locks`**, **`clear.locks`**, **`lock`**, **`logout`**, **`set.date`**,
> **`sh`**, `!`, **`clean.account`** and `umask`. They are no longer copied into any
> account's VOC; administrators receive them from `VOC_TEMPLATE` instead. **A
> programmer or standard account created before that update keeps whichever of
> them it had**, because **`update.account`** never removes a record.

> **`umask` was removed from every tier.** It controls POSIX file-mode bits,
> which Windows does not use for security — all file access runs through the
> ACLs an SD account already receives. Setting a umask on Windows produces no
> security effect and would only be misleading. The record types stay compiled,
> but no VOC in any tier dispatches to them.
