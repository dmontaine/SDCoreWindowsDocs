Title: Account types
Subtitle: Standard, Programmer, Administrator and Group — what each one may do, and how to make one.

OpenQM gives every account the same VOC and leaves privilege to `SYSTEM`
membership. SD Core does not. **An account is created into one of three tiers,
and the tier decides what verbs its VOC contains.** Group accounts are a fourth
thing entirely — a shared place, not a person.

## The three tiers at a glance

| | Standard | Programmer | Administrator |
|---|---|---|---|
| Verbs | 77 | 77 + 41 | 77 + 41 + 21 |
| VOC records on creation | 354 | 395 | 416 |
| Can run an application | yes | yes | yes |
| Can compile, catalogue, edit | **no** | yes | yes |
| Can create or configure files | **no** | yes | yes |
| Can administer accounts | no | no | yes |
| Windows `Administrators` | no | no | **yes** |
| Local console and Remote Desktop | denied | denied | allowed |

**`administrator` implies `programmer`.** You do not need both keywords.

### Standard — 77 verbs

What an application needs and no more: query and list (`select`, `list`,
`get.list` and family), spool and print, session and environment (`logto`,
`date`, `who`, `set`), screen and message, prompt and input state, and eight
read-only inspectors — `search`, `list.diff`, `list.item`, `list.common`,
`list.vars`, `report.src`, `report.style`, `format`.

Everything an application built on SD invokes, and nothing that edits code or
data in bulk.

### Programmer — 41 more

The development set: the compilers, the editor, the cataloguer, the file and
index definition verbs, the bulk record editors and the process introspection
verbs. See [Programmer commands](06-programmer-commands.html) for what each one
is for.

### The counts are arithmetic, not observation

Installed `NEWVOC` holds 394 names, of which `%t` is a dynamic-file artefact
and the two tier lists are never copied — so **391 records reach a full VOC**.
`create.account` then adds four of its own (`$command.stack`, `$hold`,
`$savedlists`, `bp`):

```
ADMINISTRATOR   391 + 21 + 4 = 416
PROGRAMMER      391      + 4 = 395
STANDARD        391 - 41 + 4 = 354
```

If your counts differ, one of the two tier lists differs — which is worth
reporting.

### Administrator — 21 more

Account and grant administration, system-wide state, and the shell escapes. See
[Administrator commands](05-administrator-commands.html).

> ***NONE OF THE THREE IS A WALL.*** An administrator can copy any verb into
> any account's VOC afterwards. **The reduced VOC is the posture an account
> starts in, not a boundary anything enforces.** The boundaries that are
> enforced are the operating system's file permissions, the ssh confinement,
> and the `os.users` permit list — not the contents of a VOC.

## Creating an account

```
create.account user <name> {administrator | programmer}
                           <ssh | api | both | none> {no.query}

create.account group <name> {no.query}

create.account other <name> <pathname> {no.query}
```

### One of `ssh`, `api`, `both`, `none` is required

***THERE IS NO DEFAULT, ON PURPOSE.*** An account that should only ever be
reached with `logto` says `none` and means it. The old silent behaviour — ssh
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

**`create.account user` is refused on a stand-alone installation**, with
message 10100. See [Installing SD Core](01-installation.html#the-two-kinds-of-installation).

## Group accounts

A group account is a shared workspace with **no Windows account and no sign-in
of its own**. It is how you keep separate work separate, and it is the only
kind of extra account a stand-alone installation can have.

```
create.account group payroll
modify.account add payroll fred
```

Reach it with `logto payroll`, or through an F pointer. On a stand-alone
installation, `logto` into a group account from a session run as administrator.

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

`list.grants` also shows the account's own user, which is always there and is
not a grant. It is listed anyway so that what you see matches the Windows group
it is reporting.

> The old field 4 of an `ACCOUNTS` record — a list of accounts allowed in — has
> been removed, and `list accounts` no longer shows a *Granted to* column.
> `list.grants` answers that question now.

## Changing an account afterwards

```
modify.account <name> <ssh | api | both | none>
modify.account add <group> <user>
modify.password {<account>}
```

***THE KEYWORD SAYS WHAT THE ACCESS IS, NOT WHAT TO ADD.*** So

```
modify.account fred api
```

gives Fred the API **and takes ssh away**. If you want both, say `both`. The
message afterwards always names both routes, so you can see what you have left
him with.

It refuses on an administrator's account — administrators always have both.

**`set.password` is now `modify.password`.** Same verb, same behaviour; the
name changed because every account has a password from the moment it is made,
so there is nothing to *set* for the first time.

## Deleting an account

`delete.account` **asks once, then removes everything.** The single question
names exactly what will go, including the Windows account when there is one to
remove.

***IT WILL NOT DELETE A WINDOWS ACCOUNT SD DID NOT CREATE.*** The question uses
shorter wording in that case rather than promising something it will not do.

## Two things that catch people out

**1. `update.account` never takes a verb away.** SD only ever *adds* records to
a VOC at an update. An account created before a verb was withdrawn keeps it, and
running `update.account` will not remove it.

**2. `sdusers` membership needs a fresh logon.** Same reason as grants. After
being added to the group, sign out of Windows and back in, or you cannot read
the data tree at all — and the symptom looks like a broken install rather than
a permissions problem.
