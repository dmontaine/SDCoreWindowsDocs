Title: Account types
Subtitle: Standard, Programmer, Administrator, Suspended and Group — what each one may do, and how to make one.

OpenQM gives every account the same VOC and leaves privilege to `SYSTEM`
membership. SD Core does not. **An account is created into one of three tiers,
and the tier decides what verbs its VOC contains.** There is a fourth tier,
**suspended**, which is not a capability at all — it denies entry. Group
accounts are a different thing again: a shared place, not a person.

***THE TIER IS NO LONGER FIXED AT CREATION.*** **`modify.account`** moves an
account between all four, in either direction, and rebuilds its VOC to match at
once. See [Changing an account afterwards](#changing-an-account-afterwards).

## The three capability tiers at a glance

| | Standard | Programmer | Administrator |
|---|---|---|---|
| Verbs | 77 | 77 + 42 | 77 + 42 + 21 |
| VOC records on creation | 354 | 396 | 417 |
| Can run an application | yes | yes | yes |
| Can compile, catalogue, edit | **no** | yes | yes |
| Can create or configure files | **no** | yes | yes |
| Can administer accounts | no | no | yes |
| Windows `Administrators` | no | no | **yes** |
| Local console and Remote Desktop | denied | denied | allowed |

**`administrator` implies `programmer`.** You do not need both keywords.

### Standard — 77 verbs

What an application needs and no more: query and list (**`select`**, **`list`**,
**`get.list`** and family), spool and print, session and environment (**`logto`**,
**`date`**, **`who`**, **`set`**), screen and message, prompt and input state, and eight
read-only inspectors — **`search`**, **`list.diff`**, **`list.item`**, **`list.common`**,
**`list.vars`**, **`report.src`**, **`report.style`**, **`format`**.

Everything an application built on SD invokes, and nothing that edits code or
data in bulk.

### Programmer — 42 more

The development set: the compilers, the two full-screen editors, the
cataloguer, the file and index definition verbs, the bulk record editors and
the process introspection verbs. See [Programmer commands](07-programmer-commands.html) for what each one
is for.

### The counts are arithmetic, not observation

Installed `NEWVOC` holds 395 names, of which `%t` is a dynamic-file artefact
and the two tier lists are never copied — so **392 records reach a full VOC**.
**`create.account`** then adds four of its own (`$command.stack`, `$hold`,
`$savedlists`, `bp`):

```
ADMINISTRATOR   392 + 21 + 4 = 417
PROGRAMMER      392      + 4 = 396
STANDARD        392 - 42 + 4 = 354
```

**A standard account's total did not move when `micro` was added**, because
**`micro`** joined `NEWVOC` and `TIER.OMIT.STANDARD` at once — it is on both sides
of the subtraction.

If your counts differ, one of the two tier lists differs — which is worth
reporting.

**The same two numbers are what a tier change reports**, so you can predict
them: moving between standard and programmer is **42** records either way, and
between programmer and administrator **21**. A change that reports a different
number, or zero where it should have moved something, is worth reporting for
the same reason.

### Administrator — 21 more

Account and grant administration, system-wide state, and the shell escapes. See
[Administrator commands](06-administrator-commands.html).

> ***NONE OF THE THREE IS A WALL.*** An administrator can copy any verb into
> any account's VOC afterwards. **The reduced VOC is the posture an account
> starts in, not a boundary anything enforces.** The boundaries that are
> enforced are the operating system's file permissions, the ssh confinement,
> and the `os.users` permit list — not the contents of a VOC.

## Suspended — the fourth tier, and the only one that is a wall

**A suspended account cannot be entered.** It is for an account that should
stop working for a while — somebody on leave, a login being looked into — and
it is refused at all three ways in:

| | |
|---|---|
| ssh, or the console | `Account FRED is suspended` |
| **`logto`** from another account | `Account FRED is suspended` |
| the API | `User not allowed in requested account` |

The API wording is deliberately the same one it gives for an account that does
not exist and for one you are not granted, so the API cannot be used to find
out which accounts exist or what state they are in.

***IT TAKES NOTHING AWAY, WHICH IS WHY LIFTING IT IS FREE.*** The VOC is left
exactly as it is, no Windows group membership moves, and the tier it displaced
is remembered — so bringing the account back puts it exactly where it was, with
nothing for you to write down. Suspending is not a substitute for deleting: it
is reversible on purpose.

***AN ELEVATED ADMINISTRATOR CAN STILL `logto` INTO A SUSPENDED ACCOUNT.***
That is deliberate — looking at a suspended account is the usual reason to have
one, and anybody elevated could lift the suspension anyway. **What a suspension
denies is the account's own user.**

> ***AND A SUSPENDED ADMINISTRATOR IS STILL A WINDOWS ADMINISTRATOR.*** SD
> refuses them; Windows does not. They keep their `Administrators` membership
> and their `os.users` record, so they can still elevate on the machine and
> still reach any account they could reach before. **If you are suspending an
> account to contain somebody rather than to park it, suspend it in Windows
> too.**

## Creating an account

```
create.account user <name> {administrator | programmer}
                           <ssh | api | both | none> {no.query}

create.account group <name> {no.query}

create.account other <name> <pathname> {no.query}
```

### One of `ssh`, `api`, `both`, `none` is required

***THERE IS NO DEFAULT, ON PURPOSE.*** An account that should only ever be
reached with **`logto`** says `none` and means it. The old silent behaviour — ssh
yes, API no — could not tell that apart from somebody who had not thought about
it.

**An administrator account always gets both and needs no keyword.** Group
accounts take none of this: they have no Windows account.

### What creating a user account actually does

| | |
|---|---|
| Makes a Windows local account | created disabled, then enabled when the password is set |
| Creates the group `sdu_<name>` | and writes it to the account record |
| Joins `sdusers` | which is what grants access to the data tree |
| Joins `sdsshonly` | **unless** `administrator` — this is what denies the console and Remote Desktop |
| Joins `Administrators` | **only** with the `administrator` keyword |
| Writes the tier to `ACCOUNTS` field 5 | so `LOGIN` cannot undo it at the next update |
| Prompts for a password | in SD, masked; it never goes on a command line |

***A USER ACCOUNT CANNOT BE CREATED WITHOUT A PASSWORD.*** Refusing the prompt
creates nothing at all. Previously it left an account you could not sign in to.

**Elevation is not optional.** Creating a Windows account needs an elevated
token, and an ordinary SD session has a filtered one. Account creation works
from the installer and from an elevated terminal, and not from a normal
session.

**`create.account user` is refused on a stand-alone installation**, with a
warning saying why. See [Installing SD Core](01-installation.html#the-two-kinds-of-installation).

## Group accounts

A group account is a shared workspace with **no Windows account and no sign-in
of its own**. It is how you keep separate work separate, and it is the only
kind of extra account a stand-alone installation can have.

```
create.account group payroll
modify.account add payroll fred
```

Reach it with `logto payroll`, or through an F pointer. On a stand-alone
installation, **`logto`** into a group account from a session run as administrator.

## Sharing a user account

```
grant   <account> to   <user>
revoke  <account> from <user>
list.grants <account>
```

All three need an elevated session, and say so rather than failing obscurely.

***READ THIS TWICE, BECAUSE IT IS THE MOST CONFUSING PART OF HOW SD CONTROLS
ACCESS.*** Entry to an account is membership of the Windows group named in the
account's record, and **Windows fixes group membership when you sign in**. So:

- a grant does not reach the person until they sign out of Windows and back in;
- and **somebody you have just revoked keeps the account until they do the
  same.**

Both verbs print that reminder every time.

**`list.grants`** also shows the account's own user, which is always there and is
not a grant. It is listed anyway so that what you see matches the Windows group
it is reporting.

> The old field 4 of an `ACCOUNTS` record — a list of accounts allowed in — has
> been removed, and `list accounts` no longer shows a *Granted to* column.
> **`list.grants`** answers that question now.

> ***`list accounts` SHOWS THE TIER, AND ITS COLUMNS HAVE CHANGED.*** The
> default is `Account`, `Pathname`, `Description`, `Tier`. The Windows group
> came out to make room: it is always `sdu_` or `sdg_` followed by the account
> name, so it told you nothing the id did not. Both are still there by name —
> `list accounts path descr group tier`. **`Was` is the tier a suspension
> displaced**, and it is empty on an account that is not suspended.
>
> From an ordinary account the register is reached as `sd.accounts`, not
> `accounts` — `list sd.accounts`, `ct sd.accounts fred`.

## Changing an account afterwards

```
modify.account <name> <standard | programmer | administrator | suspended>
modify.account <name> <ssh | api | both | none>
modify.account <name> <sh-on | sh-off | os-on | os-off>
modify.account add <group> <user>
modify.password {<account>}
```

All of them need an elevated session.

### The tier

***THE TIER MOVES IN EITHER DIRECTION AND NEEDS NO INTERMEDIATE STEP.*** An
account can go programmer, standard, suspended and back to any of them
directly. Naming a tier on a suspended account lifts the suspension into that
tier — **there is no `resume` keyword**; coming back always says where to.

**The VOC is rebuilt there and then**, not at the next login, and the verb says
what it did:

```
:modify.account fred standard
Account FRED is now STANDARD
VOC: 0 records added, 42 removed, 0 left alone
```

***"LEFT ALONE" IS THE COUNT TO READ.*** A record is only removed if it is
still exactly what SD put there. **Anything you or the account's owner has
edited is counted and kept** — it is somebody's work under a verb's name rather
than the verb, and a downgrade will not destroy it.

### Leaving `administrator` takes three things, and you must name one

| | |
|---|---|
| Windows `Administrators` membership | removed for you |
| the `os.users` record | removed for you |
| ssh and the API | **you say** |

The first two were the account's *because* it was an administrator. ssh and the
API are a rule for an administrator and a setting for everybody else, so the
command will not guess:

```
:modify.account fred programmer
Say what remote access FRED is to have: ssh, api, both or none
:modify.account fred programmer both
FRED may sign in over ssh and use the API
Account FRED is now PROGRAMMER
```

**You cannot suspend your own account, or the one you are standing in.** And a
group account can be any tier except `administrator` — there is no single
person behind it to put in a Windows group.

### The remote routes

***THE KEYWORD SAYS WHAT THE ACCESS IS, NOT WHAT TO ADD.*** So

```
modify.account fred api
```

gives Fred the API **and takes ssh away**. If you want both, say `both`. The
message afterwards always names both routes, so you can see what you have left
him with.

### Reaching the operating system

`sh-on`, `sh-off`, `os-on` and `os-off` set the two fields of the person's
`os.users` record without your having to edit it by hand — field 1 is the
**`sh`** verb, field 2 is `OS.EXECUTE` and the two full-screen editors. See
[Administrator commands](06-administrator-commands.html#the-list).

**These four are switches, not names for one state**, unlike the tier and the
routes above — so `sh-off` leaves `OS.EXECUTE` alone.

### What refuses on an administrator's account

**All three of ssh, the API and the operating system.** An administrator has
every route as a rule, and none of them is this verb's to change:

```
:modify.account don os-off
don is an administrator and always reaches the operating system
```

**Downgrade the account first** if that is really what you want. The tier is
the only thing about an administrator that `modify.account` will change.

**`set.password` is now `modify.password`.** Same verb, same behaviour; the
name changed because every account has a password from the moment it is made,
so there is nothing to *set* for the first time.

## Deleting an account

**`delete.account`** **asks once, then removes everything.** The single question
names exactly what will go, including the Windows account when there is one to
remove.

***IT WILL NOT DELETE A WINDOWS ACCOUNT SD DID NOT CREATE.*** The question uses
shorter wording in that case rather than promising something it will not do.

## Two things that catch people out

**1. `update.account` never takes a verb away.** SD only ever *adds* records to
a VOC at an update. An account created before a verb was withdrawn keeps it, and
running **`update.account`** will not remove it.

**`modify.account <tier>` is the one that does remove them**, and it is the only
thing that ever will. If you need a verb gone from an account, change the tier;
`update.account` will not undo it afterwards either, because the tier is
recorded and every update applies it.

**2. `sdusers` membership needs a fresh logon.** Same reason as grants. After
being added to the group, sign out of Windows and back in, or you cannot read
the data tree at all — and the symptom looks like a broken install rather than
a permissions problem.
