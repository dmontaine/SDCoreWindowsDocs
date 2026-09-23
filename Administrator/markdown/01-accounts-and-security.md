Title: Accounts and Security
Subtitle: Making and changing accounts, passwords, and who may enter an account.

These are the verbs that decide **who may use this installation and what
they may do with it.** They are SDSYS's set — not in any other account's
VOC at all — and almost all of them need more than the verb before they
will do anything.

> **This document is separate so that it can be withheld.** Everything in
> the administrator set describes verbs an ordinary account does not have
> and cannot run. It is a complete set on its own and **links to nothing
> outside itself**, so that handing somebody the user documentation without
> this never leaves them at a page that is not there. Where a user-set page
> is worth naming, it is named in words rather than linked.

SD folds case, so a command may be typed in either case. Commands are shown
here in lower case. In the tables, *italics* mark something you supply and
**bold** marks a word typed as it stands; braces mark an optional part.

## Read this before anything else: being SDSYS is the whole of it

**Having the verb is not having the right to use it — but there is only one
gate now, not two.** SD Core used to check a VOC tier and elevation
separately; the tier is gone. Every verb on this page is refused outright
to any session that is not actually SDSYS, whether or not that session is
elevated:

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

**Being SDSYS means having signed in to Windows as the account named
`sdsys`**, made once by the installer, and nothing else. Being a Windows
administrator grants nothing by itself — an elevated session in an ordinary
account is still an ordinary account. **Start SD by signing in to Windows
as SDSYS and running it elevated.** The three verbs on this page that do
*not* require this are `clean.account`, `config` and `update.accounts`, and
each of them acts only on the account you are already standing in or on
your own session.

## Making an account: `create.account`

```
create.account user <name> {ssh | api | both | none} {no.query}

create.account group <name> {no.query}

create.account other <name> <pathname> {no.query}
```

| | |
|---|---|
| **`user`** | an SD account **and** a Windows local account to sign in as |
| **`group`** | a shared workspace with no Windows account, reached only with `logto` |
| **`other`** | an SD account over a directory you name |

**Say nothing and a user account gets `both`** (ssh and the API). Name
`ssh`, `api` or `none` to be narrower — an account meant to be reached only
with `logto` says `none` and means it.

> **It prompts for a password and `no.query` does not suppress that.**
> `no.query` covers the confirmation, not the credential — a password is
> never an argument anywhere in SD. **`create.account user` therefore
> cannot be driven from a script**, and a group account, which has no
> password, can.

**Every account gets the same VOC**, the whole of `newvoc` — there is no
tier to choose at creation. What it does *not* get automatically is
`sh`/`OS.EXECUTE` access: both default to off, and `modify.account`'s
`sh-on`/`os-on` grant them afterward (see below).

### Two settings that are easy to conflate

| | |
|---|---|
| `api` | says who may **connect** |
| `os-on` | says who may reach the **operating system** |

Holding the first has never implied the second. They are independent
settings and are checked in different places.

### What `os-on` actually costs

Granting `os-on` to any account is a larger decision than it looks.

**That account reaches the operating system over the API as well as
locally** — and over the API the session's process token is LocalSystem.
On an ordinary account with both `os-on` and API access, a remote API
connection makes the operating system report the session as
`nt authority\system`.

This is accepted behaviour rather than a defect, and it follows from the
way SD's listener creates a session — it is unrelated to the account's own
identity, which is why it is stated here rather than assumed. It is stated
here because it is not something a reader should have to discover: `os-on`
on an account with API access gives that account the operating system, as
LocalSystem, from any machine that can reach the API port.

The full account of what creating a user account does to Windows — the
groups, the disabled-then-enabled login, the console denial — is in the SD
Core for Windows release documentation, under *Accounts*, and is not
repeated here.

## Changing one: `modify.account`

```
modify.account account add | delete  user.name
modify.account account ssh | api | both | none
modify.account account sh-on | sh-off
modify.account account os-on | os-off
modify.account account suspended | unsuspended
```

### `suspended`/`unsuspended` is a state, not a tier

**Nothing about the account moves except the one field.** No Windows
membership changes, no VOC changes — every account's VOC is the whole of
`newvoc` regardless of the field. Three doors refuse a suspended account:
signing in, `logto`, and the API.

### The other keywords

| | |
|---|---|
| **`ssh`** \| **`api`** \| **`both`** \| **`none`** | what the account's remote access **is**. Absolute: `api` takes ssh away |
| **`sh-on`** \| **`sh-off`** | the `sh` verb and `!` |
| **`os-on`** \| **`os-off`** | `OS.EXECUTE` and the screen editors |
| **`add`** \| **`delete`** *user* | put a Windows user in, or out of, the account's group |

**The first group is absolute and the second is not.** `ssh`/`api`/`both`/
`none` are four names for one state, so whatever is not named is
withdrawn. `sh-on` and `os-on` are two independent switches over two
separate settings, so **`sh-off` says nothing about `OS.EXECUTE`** and
leaves it alone.

**Every keyword on this page refuses `SDSYS` as the target account,
outright, before the keyword itself is even read** — *"Remote access is
never available to SDSYS"* is the message whatever you asked for. SDSYS's
own routes are not a setting; see [Read this before anything
else](#read-this-before-anything-else-being-sdsys-is-the-whole-of-it). A
group account is refused too, for the `sh-on`/`sh-off`/`os-on`/`os-off`
forms: it has no Windows user to hold the record.

## Passwords: `modify.password`

```
modify.password {account}
```

With no account name it changes **your own**, and asks for the current
password first. With one, from SDSYS, it changes that account's — any
account, including SDSYS's own — and does not ask for the old password: an
administrator resetting a forgotten password does not know it.

**The password is never an argument, and a trailing token is refused rather
than ignored:**

```
:modify.password don hunter2
A password is never given on the command line; MODIFY.PASSWORD prompts for it
```

**That refusal is the point of the verb's design.** The older behaviour set
the password from the prompt and threw the extra word away without a word,
so every visible sign said it had worked — while the password had already
reached SD's command stack, and a shell's history and process list if the
verb was reached from one. Refusing does not put it back, but it says so.

The prompts are hidden, asked twice, and the account must already exist in
the register. **`modify.password` cannot be scripted**, by design.

**SDSYS's *Windows* sign-in password is a separate thing** — set once,
during installation, and changed afterward the ordinary Windows way, not
with this verb.

## Who may enter an account: `grant`, `revoke`, `list.grants`

```
grant account to user
revoke account from user
list.grants account
grant account              the same as list.grants
```

**The grant is Windows group membership and nothing is written to the
account record.** Every SD account has a Windows group — `sdu_`*name* for a
user account, `sdg_`*name* for a group account — and entry to the account
**is** membership of that group. These three verbs edit that group and
read it back.

| | |
|---|---|
| *There is no Windows account named %1* | `grant` to somebody who does not exist |
| *%1 is already a member of group %2* | `grant` to somebody who already has it |
| *%1 has not been granted account %2* | `revoke` from somebody who has not |
| *Account not registered in ACCOUNTS file* | the account name is not one of SD's |
| *Account %1 has no Windows group recorded* | a record predating the group model; it is **refused, not guessed at** |

**The account's own user is listed like any other member.** It is not a
grant — creating the account put them there — but hiding it would make the
listing disagree with the Windows group it is reporting.

**A successful `grant` or `revoke` writes an audit record** to SD's audit
trail, stamped with the user and process that did it. The identity is
stamped by SD and is not passed in, so a caller cannot get it wrong or
forge it. Windows records the group change in its own security log as
well, and the two are independent records of the same act.

> **`modify.account` *account* `add`/`delete` *user* makes the same group
> change and writes no audit record.** Prefer `grant` and `revoke` when
> there is a choice: they say what they mean and they leave a trail.

## Continued in

[Account Maintenance](01a-account-maintenance.html) — clean.account,
update.accounts, [locked], config, set.date and delete.account.

[Differences from W1.0-0](12-differences-from-w1-0-0.html) — what changed
since the previous release, for an administrator upgrading into it.
