Title: Accounts and Security
Subtitle: Making and changing accounts, passwords, who may enter an account, and reading the system's configuration.

These are the verbs that decide **who may use this installation and what they
may do with it.** They are the administrator's set, they are the smallest set
on the machine, and almost all of them need more than the verb before they will
do anything.

> ***THIS DOCUMENT IS SEPARATE SO THAT IT CAN BE WITHHELD.*** Everything in the
> administrator set describes verbs an ordinary account does not have and cannot
> run. It is a complete set on its own and **links to nothing outside itself**,
> so that handing somebody the user documentation without this never leaves them
> at a page that is not there. Where a user-set page is worth naming, it is
> named in words rather than linked.

SD folds case, so a command may be typed in either case. Commands are shown here
in lower case. In the tables, *italics* mark something you supply and **bold**
marks a word typed as it stands; braces mark an optional part.

## Read this before anything else: there are two gates, not one

***HAVING THE VERB IS NOT HAVING THE RIGHT TO USE IT.***

| | |
|---|---|
| **the tier** | decides whether the account's VOC has the verb at all. Only an `administrator` account has these names; in any other account they are not recognised |
| **elevation** | decides whether the verb does anything. Almost every verb here begins by testing it, and stops if the session is not elevated |

Measured, in an administrator account, from an ordinary unelevated session:

```
:list.grants don
Command requires administrator privileges
:delete.account sdsys
Command requires administrator privileges
:modify.password sdsys
Command requires administrator privileges
```

**Every one of those refusals came before the command was looked at.**
`delete.account sdsys` would have been refused anyway — you cannot delete
`SDSYS` — and it never got that far.

***WHAT COUNTS AS ELEVATED IS A WINDOWS QUESTION AND IS FIXED WHEN SD STARTS.***
The token a process gets is decided at process creation, so there is nothing
you can type inside a running session to elevate it. **Start SD from an
elevated terminal**, or accept the UAC prompt that `logto sdsys` raises. The
three verbs on this page that do *not* test elevation are `clean.account`,
`config` and `update.account`, and each of them acts only on the account you
are already standing in or on your own session.

## Making an account: `create.account`

```
create.account user <name> {administrator | programmer}
                           <ssh | api | both | none> {no.query}

create.account group <name> {no.query}

create.account other <name> <pathname> {no.query}
```

| | |
|---|---|
| **`user`** | an SD account **and** a Windows local account to sign in as |
| **`group`** | a shared workspace with no Windows account, reached only with `logto` |
| **`other`** | an SD account over a directory you name |

***ONE OF `ssh`, `api`, `both`, `none` IS REQUIRED FOR A USER ACCOUNT AND THERE
IS NO DEFAULT.*** An account meant to be reached only with `logto` says `none`
and means it. An `administrator` account is given both routes and takes no
keyword. Omitting the tier gives a **standard** account.

> ***IT PROMPTS FOR A PASSWORD AND `no.query` DOES NOT SUPPRESS THAT.***
> `no.query` covers the confirmation, not the credential — a password is never
> an argument anywhere in SD. **`create.account user` therefore cannot be
> driven from a script**, and a group account, which has no password, can.

**`sh-on`** and **`os-on`** may be added to give the new account the `sh` verb
and `OS.EXECUTE`; see `modify.account` below, which has both and their `-off`
forms.

The full account of what creating a user account does to Windows — the groups,
the disabled-then-enabled login, the console denial — is in the SD Core for
Windows tester documentation, under *Account types*, and is not repeated here.

## Changing one: `modify.account`

```
modify.account account standard | programmer | administrator | suspended
modify.account account standard | programmer   ssh | api | both | none
modify.account account ssh | api | both | none
modify.account account sh-on | sh-off
modify.account account os-on | os-off
modify.account account add | delete  user.name
```

### The tier moves in any direction

**`standard`, `programmer`, `administrator` and `suspended` are four names for
one state**, and any of them can be reached from any other with no intermediate
step. The account's VOC is rewritten there and then, not at its next login.

***`suspended` DENIES ACCESS AND CHANGES NOTHING ELSE.*** The VOC is left as it
is, no Windows group membership moves, and the tier it displaced is remembered
so that the way back knows where the account is coming from. **There is no
`resume` keyword** — coming back names the destination tier, and naming one on
a suspended account lifts the suspension into it.

Three doors refuse a suspended account: signing in, `logto`, and the API.

***LEAVING `administrator` TAKES THREE THINGS AWAY AND ONE MUST BE NAMED.***
Windows `Administrators` membership and the operating-system access record go
by themselves, because the account held them *because* it was an
administrator. **ssh and the API were a rule and now have to be a choice**, so
the second form above is compulsory: `modify.account don programmer both`.

### The other keywords

| | |
|---|---|
| **`ssh`** \| **`api`** \| **`both`** \| **`none`** | what the account's remote access **is**. Absolute: `api` takes ssh away |
| **`sh-on`** \| **`sh-off`** | the `sh` verb and `!` |
| **`os-on`** \| **`os-off`** | `OS.EXECUTE` and the screen editors |
| **`add`** \| **`delete`** *user* | put a Windows user in, or out of, the account's group |

***THE FIRST GROUP IS ABSOLUTE AND THE SECOND IS NOT.*** `ssh`/`api`/`both`/
`none` are four names for one state, so whatever is not named is withdrawn.
`sh-on` and `os-on` are two independent switches over two separate settings, so
**`sh-off` says nothing about `OS.EXECUTE`** and leaves it alone.

**All of these refuse an administrator account.** An administrator has full
access and there is no way to turn any of it off — the way to reduce one is to
move it to another tier, which is what the tier keywords are for. A group
account is refused too: it has no Windows user to put in a group.

## Passwords: `modify.password`

```
modify.password {account}
```

With no account name it changes **your own**, and asks for the current password
first. With one it changes somebody else's, which needs elevation and does not
ask for the old password — an administrator resetting a forgotten password does
not know it.

***THE PASSWORD IS NEVER AN ARGUMENT, AND A TRAILING TOKEN IS REFUSED RATHER
THAN IGNORED:***

```
:modify.password don hunter2
A password is never given on the command line; MODIFY.PASSWORD prompts for it
```

**That refusal is the point of the verb's design.** The older behaviour set the
password from the prompt and threw the extra word away without a word, so every
visible sign said it had worked — while the password had already reached SD's
command stack, and a shell's history and process list if the verb was reached
from one. Refusing does not put it back, but it says so.

The prompts are hidden, asked twice, and the account must already exist in the
register. **`modify.password` cannot be scripted**, by design.

## Who may enter an account: `grant`, `revoke`, `list.grants`

```
grant account to user
revoke account from user
list.grants account
grant account              the same as list.grants
```

***THE GRANT IS WINDOWS GROUP MEMBERSHIP AND NOTHING IS WRITTEN TO THE ACCOUNT
RECORD.*** Every SD account has a Windows group — `sdu_`*name* for a user
account, `sdg_`*name* for a group account — and entry to the account **is**
membership of that group. These three verbs edit that group and read it back.

| | |
|---|---|
| *There is no Windows account named %1* | `grant` to somebody who does not exist |
| *%1 is already a member of group %2* | `grant` to somebody who already has it |
| *%1 has not been granted account %2* | `revoke` from somebody who has not |
| *Account not registered in ACCOUNTS file* | the account name is not one of SD's |
| *Account %1 has no Windows group recorded* | a record predating the group model; it is **refused, not guessed at** |

**The account's own user is listed like any other member.** It is not a grant —
creating the account put them there — but hiding it would make the listing
disagree with the Windows group it is reporting.

***A SUCCESSFUL `grant` OR `revoke` WRITES AN AUDIT RECORD*** to SD's audit
trail, stamped with the user and process that did it. The identity is stamped
by SD and is not passed in, so a caller cannot get it wrong or forge it.
Windows records the group change in its own security log as well, and the two
are independent records of the same act.

> **`modify.account` *account* `add`/`delete` *user* makes the same group
> change and writes no audit record.** Prefer `grant` and `revoke` when there
> is a choice: they say what they mean and they leave a trail.

## Emptying an account's scratch files: `clean.account`

```
clean.account
```

Empties three things in the account you are standing in, and takes no
arguments — **there is no way to clean an account you are not in**:

```
:clean.account
Cleaned $COMO
Cleaned $hold
Cleaned $savedlists
```

| | |
|---|---|
| **`$COMO`** | captured session transcripts, including every phantom's |
| **`$hold`** | reports sent to the hold file instead of a printer |
| **`$savedlists`** | saved select lists |

***NOTHING ELSE IS TOUCHED*** — no data file, no program, no dictionary. A como
capture that is currently running is left alone and says so: *$COMO not cleaned
- COMO file active*.

**It needs no elevation.** It is the one verb here an administrator account can
use from an ordinary session, which is right: it deletes only that account's own
scratch.

## Refreshing an account's VOC: `update.account`

```
update.account
```

```
Copying records from NEWVOC to VOC...
```

Copies the shipped verb and keyword definitions into the account you are
standing in, adding what is missing and leaving your own VOC entries alone. It
is what brings an existing account up to date after SD itself is upgraded, and
**it respects the account's tier** — a standard account does not collect
programmer verbs by being refreshed, and a suspended one keeps the tier it was
suspended from.

## Reading and setting configuration: `config`

```
config                     report every setting
config lptr                the same, to the default printer
config param value         set one
config gpl                 display the licence
config contrib             display the contributors
```

```
:config
Virtual Machine Version Number W1.0-0
APILOGIN  1
APIPORT   4243
CMDSTACK  99
DEADLOCK  0
DUMPDIR
ERRLOG    50 kb
...
NUMFILES  80
NUMLOCKS  100
NUMUSERS  20
...
SH        C:/Windows/System32/WindowsPowerShell/v1.0/powershell.exe -NoProfile -NoLogo
SORTWORK  /cygdrive/c/WINDOWS/TEMP
TEMPDIR   /cygdrive/c/WINDOWS/TEMP
YEARBASE  1930
```

*(Forty-odd lines; cut here.)* **Reading needs nothing** — any account with the
verb can do it, and it is the quickest answer to *how many users, how many
locks, how many open files is this machine set up for*.

| | |
|---|---|
| *New parameter value required* | `config numlocks` with nothing after it. **The report form is `config` alone**; naming one parameter means *set it* |
| *Not a recognised private configuration parameter name* | the name is not one that can be set per-session |
| *Invalid value for this parameter* | it is, and the value is not |

***`config param value` SETS A PRIVATE, SESSION-LOCAL VALUE AND NOT THE
MACHINE'S.*** The machine's settings live in SD's configuration file and are
read when SD starts. This form overrides one for the session you are in, which
is the right tool for trying a value before writing it down and the wrong one
for changing an installation.

**`config gpl` and `config contrib` read a record inside SD** rather than
running a pager over a file, so they work in any account and need no
operating-system access.

## `encrypt.field` does not work in this release

```
:encrypt.field
00001FCB: Unable to load '$CRYPTO' object code at line 1550 of $CPROC
```

***THE VERB IS IN AN ADMINISTRATOR'S VOC AND THE PROGRAM BEHIND IT IS NOT IN
THE DISTRIBUTION.*** Every form of it fails the same way, at the point of
loading, before it looks at anything you typed. **It is recorded as a defect
against this release.** Treat field-level encryption as not present in SD Core
for Windows W1.0-0; nothing else on this page depends on it.

## Deleting an account: `delete.account`

```
delete.account account.name
```

Removes the account directory, its Windows group, its entry in the accounts
register, and — for a user account SD itself created — the Windows account and
its profile. **One confirmation covers all of it**, and the wording is decided
before the question is asked, so it never offers to remove a Windows account it
is not going to.

***IT WILL NOT DELETE A WINDOWS ACCOUNT SD DID NOT CREATE.*** The account is
left in place and it says so.

**Three refusals come before the confirmation**, so none of them can be reached
by accident:

| | |
|---|---|
| *Cannot delete SDSYS account* | `delete.account sdsys` |
| *Cannot delete own account* | the account you are standing in |
| *Account not registered in ACCOUNTS file* | the name is not one of SD's |

*(Those three wordings are the verb's own; they are not shown as a transcript
here because reaching them takes an elevated session, and an unelevated one is
refused by the privilege gate first — which is itself the fourth refusal, and
the one most people meet.)*

> ***THE CONFIRMATION IS UNCONDITIONAL AND NO KEYWORD SUPPRESSES IT.*** There
> is no `no.query` on this verb. **Never send `delete.account` down a pipe** —
> the prompt will eat the commands that follow it as its answers, and the
> session will then wait for ever.

## Who has these verbs

**All of them are administrator verbs.** A standard or programmer account has
none of these names at all.

| | |
|---|---|
| **needs elevation as well** | `create.account` `modify.account` `modify.password` (for another account) `delete.account` `grant` `revoke` `list.grants` |
| **the verb is enough** | `clean.account` `update.account` `config` |

***`list.grants` NEEDS ELEVATION EVEN THOUGH IT ONLY READS.*** It answers *who
may enter this account*, which is worth knowing before you have it, and the
gate is at the top of the program the three grant verbs share.

## See also

[Sessions and Locks](02-sessions-and-locks.html) ·
[Operating System Access](03-operating-system-access.html).

**In the user documentation**, which does not repeat any of this: *SD TCL - The
Command Processor* for how a verb is dispatched and what a VOC record holds, and
*SD Basic - System and Environment* for what a program can read about its own
session. Those pages are in a different set and are deliberately not linked from
here — see the note at the top.
