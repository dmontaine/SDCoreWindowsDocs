Title: Differences from W1.0-0
Subtitle: What changed for an administrator, grouped by theme rather than by date.

This page is for an administrator who already knows **W1.0-0** and is
looking at **W1.1-0**. The rest of this set describes the current model on
its own terms, already corrected where W1.1-0 changed it; this page exists
to say what is *different*, in one place, and to flag what an existing
install or script might trip over.

The day-by-day version — every fix, in the order it was made — ships on the
machine at `C:\ProgramData\SD\sdsys\changelog`. The GettingStarted set
carries the same material from a general reader's perspective, in its own
*Differences from W1.0-0* page; this one is the administrator's angle on it,
and does not repeat what *Accounts and Security*, *Operating System Access*
and the other chapters in this set already say correctly.

## Accounts: the tiers are gone, and it is not a narrowing

**Standard, Programmer and Administrator no longer exist.** Every account
`create.account` makes gets the whole vocabulary, and the only account with
anything more is SDSYS — which nothing an administrator runs can create; it
is a single Windows account the installer makes. See
[Read this before anything else: being SDSYS is the whole of it](01-accounts-and-security.html#read-this-before-anything-else-being-sdsys-is-the-whole-of-it).

**A tier keyword anywhere is now a syntax error**: `CREATE.ACCOUNT ...
STANDARD`, `MODIFY.ACCOUNT ... PROGRAMMER`, or naming a tier to lift what
used to be a downgrade. What used to be a tier change is a suspension now —
`MODIFY.ACCOUNT <account> SUSPENDED` / `UNSUSPENDED` — which denies every
door and takes nothing away, so it is free to reverse. `LIST ACCOUNTS` no
longer has a tier column; it shows the suspension state instead.

**The route keyword on `CREATE.ACCOUNT` is optional, and defaults to
`BOTH`.** Leaving it out used to be a syntax error; now it means the account
gets both ssh and the API, which is what every account is entitled to. See
[Making an account: `create.account`](01-accounts-and-security.html#making-an-account-createaccount).

### A file that came and went in the same release: `tier.policy`

**If you read, on 13 Sep 2026, that the tier lists moved to a dedicated
`SDSYS tier.policy` file** (`omit.standard` and `add.administrator`,
replacing the malformed-looking `TIER.OMIT.STANDARD` and
`TIER.ADD.ADMINISTRATOR` VOC records) — that move was itself superseded five
days later when tiers were removed altogether. There is no tier policy to
customise any more; there is one vocabulary, and administration is SDSYS's
alone. Nothing to migrate: if your tree never carried a customised
`tier.policy`, this never touched you.

## Passwords: a minimum policy, and self-service

**SD Core now enforces its own minimum, on top of whatever Windows already
requires**: at least 8 characters, with a lower-case letter, an upper-case
letter, a digit and a symbol (any printable character that is not a letter
or digit; a space counts). It applies everywhere SD sets a password —
`MODIFY.PASSWORD`, `CREATE.ACCOUNT`, an elevated session's first-run prompt,
and the SDSYS password the installer asks for. See
[Passwords: `modify.password`](01-accounts-and-security.html#passwords-modifypassword).

**`MODIFY.PASSWORD` typed alone now changes the caller's own password, for
every account** — before this it belonged to SDSYS alone, so an ordinary
account had no self-service route at all. Naming another account's name
still needs an SDSYS session and still skips the old-password prompt, since
an administrator resetting a forgotten password does not know it.

## An API session now runs as the signed-in user

**This is the one with the sharpest permissions consequence, and it belongs
in this set more than anywhere else.** Until W1.1-0, every API session ran
as the SD service account — LocalSystem on Windows, the most privileged
account on the machine — and only *pretended* to be the logged-in user for
some checks. Files it created were correctly owned by that user, but the
session itself could reach anything LocalSystem could.

**An API session now runs as exactly the Windows user who logged in**,
inheriting only that user's own file permissions. A file an API session
used to read or write despite the account having no Windows permission on
it **will now be refused** — check the file's Windows ACL for the account
the session logs in as; that is the fix working as intended, not a fault to
route around with a broader grant. `SH` and `OS.EXECUTE` do not work at all
from an API session in this release: Windows will not let a process started
the way an API login starts one launch anything needing a desktop.

## The API is now encrypted end to end

**Not yet covered elsewhere in this set — read it here.** Until W1.1-0, only
the API login was protected; every command, record and result after it
crossed the network as plain text. **Every API connection — the network
port and the local one alike — is now wrapped in TLS 1.3 before SD sends
anything**, and the login itself is bound to that encrypted connection, so a
machine sitting between a client and the server cannot log in on the
client's behalf or read the traffic, even by pretending to be the server.
The client libraries (`sdclilib`, `sdclient`, the BASIC `!sdclient` class)
negotiate this automatically; a program linked against an **older** copy of
the library cannot connect — the server waits out a ten-second handshake
timeout and closes the connection. A client does not yet check the server's
certificate, so use API passwords that are long and not reused elsewhere.

**A new local Windows account, `sdrelay`, will appear in Computer
Management** the first time an API connection is made — do not delete it or
wonder what created it. The small helper program that terminates the
encryption per connection (`sdtlsrelay.exe`, beside `sd.exe`) used to run at
the same privilege as the SD service itself; it now runs as `sdrelay`, with
every privilege stripped, at low integrity, unable to sign in interactively
and in no group. SD's service creates and removes it; deleting it by hand
refuses every API connection until the service is reinstalled. It cannot
read the database, `sd.conf`, or the server's own TLS key.

## Installation and upgrading

**The install now makes you an ordinary SD account of your own, named after
your Windows account, in addition to SDSYS.** The finishing window asks for
two passwords in turn — SDSYS's, then yours if you have none yet — where the
W1.0-0 installer asked for one. See
[Two things to know before the first install](08-sd-installation.html#two-things-to-know-before-the-first-install).

**Upgrading no longer stalls for around five minutes and then reports
failure.** The cause was a sign-in-time question — "Update VOC to new
release?" — that some upgrade steps trigger with no screen to answer it on;
the installer already does the same update itself via `update.accounts
all`, so the question is gone and the steps that used to hang on it now run
straight through. Each upgrade step also names itself on the installer's
page before it starts, rather than leaving the window blank while the two
whole-tree steps run.

**Uninstalling asks about your database and your `sd.conf` separately.**
They used to be one question, because both live in the same folder;
removing the database took the settings file with it whether you wanted
that or not. **Removing the Windows accounts `CREATE.ACCOUNT` made now
actually removes them when the database is removed in the same pass** — the
two steps used to run in an order that deleted `sdusers` (the list of which
accounts to remove) before the removal ran, so it silently found nothing to
do and left every one of those accounts able to sign in to Windows.

**The `voc_template` directory is no longer installed.** It was a build-time
source for SDSYS's own VOC and nothing on an installed system ever read it;
an upgrade removes one an earlier release left behind. SDSYS's own VOC is
unaffected.

## Session and lock behaviour

**A session that dies without signing off is cleared automatically, within
five minutes**, rather than needing `sd -cleanup` run by hand. The five-
minute check already existed and was finding these sessions; the cleanup
step that should have followed simply never ran. The error log now records
both halves — the session found gone, and what the cleanup removed. Running
`sd -cleanup` by hand still works and is still the immediate remedy if you
do not want to wait.

**`LIST.READU` and `GETLOCKS` no longer risk a crash** when a lock is held
for a session that has already gone; such a lock now shows its owner as
`(gone)`. See
[What is locked: `list.readu`](02-sessions-and-locks.html#what-is-locked-listreadu).

## Printing and mail

**A spooled print job (`SETPTR` mode 1) now reaches a real Windows
printer** — the one named with `AT`, or the session's default — instead of
being handed to a Linux print command that silently discarded it. Windows'
"Let Windows manage my default printer" (on by default) makes the default
printer become whichever one was last used *from any program*; on a
multi-printer machine, either turn that off or always name the printer with
`AT`. See [Printing](07-sd-admin-configuration.html#printing).

**`SENDMAIL` now reports that it is not supported, instead of reporting
success and sending nothing.** SD Core on Windows has no mail transport
configured; nobody has asked for one.

## Smaller fixes worth an administrator's attention

- **Every command SD or the installer prints for you to run now says
  `powershell -ExecutionPolicy Bypass -File`.** They used to omit the
  switch, which a stock Windows machine refuses outright — exactly when the
  advice mattered most, since most of these commands appear after something
  has already gone wrong.
- **`DELETE.ACCOUNT` tells you when the account's directory did not actually
  go** — a file still open in it, or a denying access rule, used to leave it
  on disk with nothing said.
- **Seven confirmation prompts now show their default and take Enter as an
  answer**, so a script or pipe feeding answers cannot be desynchronised by
  an unexpected repeat of the same question. Two prompts are deliberately
  unchanged, because no is not a safe default for either.

## What might stop working

- **A script naming a tier keyword** anywhere — creating, modifying, or
  lifting a suspension — is now a syntax error.
- **A file permission granted only because an API session ran as
  LocalSystem.** Grant the caller's own Windows account the access it
  actually needs.
- **An API client built against an older client library** cannot connect
  until it is relinked against the current one.
- **`SH` or `OS.EXECUTE` invoked from a program that logs in over the API**
  will not run in this release.
- **A customised `tier.policy` file**, if you had one — there is nothing
  left for it to configure.
- **A silent uninstall that relied on the database prompt also clearing
  `sd.conf`** — the two are independent questions now, and a silent run
  (`/VERYSILENT`) still keeps both by default.

## See also

[Accounts and Security](01-accounts-and-security.html) — the current
account model in full. [Operating System Access](03-operating-system-access.html)
— `os.users`, unaffected by any of the above. [Installation and the
service](08-sd-installation.html) — what an upgrade replaces today.
