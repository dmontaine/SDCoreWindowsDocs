Title: Differences from W1.0-0
Subtitle: What changed for someone who already knows SD Core for Windows, grouped by theme rather than by date.

This page is for somebody who used **W1.0-0** and is looking at **W1.1-0**.
Everything else in this set already describes the current behaviour on its
own terms; this page exists only to say what is *different*, and to flag
what might stop working after an upgrade.

The day-by-day version of everything below — every fix, in the order it was
made — ships on the machine at `C:\ProgramData\SD\sdsys\changelog` (or
`config gpl` from an `sd` prompt for the licence, `LIST.VOCLIB` is not it;
the changelog is a plain text file in the SDSYS account's install tree).
This page is the same material, reorganised.

## Accounts: the tiers are gone

**Standard, Programmer and Administrator no longer exist.** Every account
`create.account` makes gets the whole vocabulary — the same one SDSYS uses —
and the only account with anything more is SDSYS itself, which is not
something `create.account` can produce at all. See
[Accounts](05-account-types.html), which describes the current model in
full — do not read an account-tier explanation anywhere else in this set or
in an older document as still true.

**What used to be a tier change is now a suspension.** `MODIFY.ACCOUNT
<account> SUSPENDED` denies an account every door; `UNSUSPENDED` reverses
it. Naming a tier keyword anywhere — `CREATE.ACCOUNT`, `MODIFY.ACCOUNT`, or
to lift what used to be a downgrade — is now a syntax error.

**The route keyword on `CREATE.ACCOUNT` is optional**, and defaults to
`BOTH` (ssh and the API) rather than refusing until you name one. See
[Creating an account](05-account-types.html#creating-an-account).

## Reaching SDSYS

**SDSYS is reached only by signing in to Windows as SDSYS and starting `sd`
from an elevated prompt.** Being a Windows administrator in your own account
no longer gets you into SDSYS, or gives your own account anything SDSYS has
— not `CATALOG ... GLOBAL`, not `SH`/`!`/`EDIT`/`MICRO` without a grant, not
`BREAK ON USER`, not `PDUMP` of another user's session. All of that used to
follow from Windows elevation; none of it does now. See
[SDSYS is the only administrator](05-account-types.html#sdsys-is-the-only-administrator).

**`LOGTO SDSYS` is refused unconditionally**, from anywhere, elevated or
not — the only way in is the elevated start itself. An elevated session that
`LOGTO`s down to an ordinary account can `LOGTO SDSYS` back up again, which
did not work before: leaving SDSYS used to end the elevated session.

**`SH` and `!` are back on ordinary accounts** — gated the same way they
always should have been, by an administrator's `OS.USERS` grant
(`MODIFY.ACCOUNT <account> SH-ON`), not by whether the account could type
the command at all.

## Passwords are stronger, and yours to change

**A password must now be at least 8 characters and contain a lower-case
letter, an upper-case letter, a digit and a symbol**, everywhere SD Core
sets one: `MODIFY.PASSWORD`, `CREATE.ACCOUNT`, an elevated session's
first-run prompt, and the SDSYS password the installer asks for.

**`MODIFY.PASSWORD` typed on its own now changes your own password**, for
every account. Before this it belonged to SDSYS alone, so an ordinary
account had no way to change what it had been given. Naming another
account's name still needs an administrator session, and still sets the
password without asking for the old one.

## The API is now encrypted end to end

**This is not documented elsewhere in this set yet — read it here.** Until
W1.1-0, only the API login was protected: the password never crossed the
network, but every command, every record and every result after it did, as
plain text. **Every API connection — the network port and the local one
alike — is now wrapped in TLS 1.3 before SD sends anything**, and the login
itself is bound to that encrypted connection, so a machine sitting between a
client and the server cannot log in on the client's behalf or read the
traffic, even by pretending to be the server.

**The client libraries do this automatically.** `sdclilib`, `sdclient` and
the BASIC `!sdclient` class all negotiate TLS themselves. A program linked
against an *older* copy of the library cannot connect at all — the server
waits for the encryption handshake and closes the connection after ten
seconds of silence. Relink it against the current library.

**A new low-privilege Windows account, `sdrelay`, appears in Computer
Management.** The small helper program that terminates the encryption for
each connection (`sdtlsrelay.exe`, beside `sd.exe`) used to run with the
same privilege as the SD service itself — LocalSystem — so a flaw in the
encryption code could in the worst case hand a remote caller that privilege
before they had even signed in. It now runs as `sdrelay`, an account with
every privilege stripped, at low integrity, unable to sign in interactively
and belonging to no group. **Leave it alone**: SD's service creates it and
removes it. If it is deleted by hand, every API connection is refused until
the service is reinstalled.

**What this does not do**: a client does not yet check the server's
certificate. The encryption stops a machine in the middle from reading
traffic or logging in on your behalf, but such a machine could still record
a login attempt and try to guess the password later, offline. Use long API
passwords that are not reused elsewhere.

**An API session now runs as the Windows user who logged in**, not as the
service account. Before this, every API session ran as LocalSystem and only
*pretended* to be you for some checks — it could read or write anything
LocalSystem could, even though the files it created were correctly owned by
you. Now it can only reach what your own Windows account may. See
[An API session runs as you](09-api-access.html#an-api-session-runs-as-you).

> **What might stop working, and it is the point rather than a fault.** An
> API program that used to read or write a file your Windows account has no
> permission on will now be refused. That only ever worked because the
> session was effectively LocalSystem. If something that worked before now
> says it cannot open a file, check that file's Windows permissions for the
> account the API session logs in as.

**`SH` and `OS.EXECUTE` do not work from an API session in this release.**
Windows will not let a process started the way an API login starts one
launch anything that needs a desktop — which includes PowerShell. Console
sessions and ssh are unaffected. See
[`sh` and `OS.EXECUTE` are refused over the API](09-api-access.html#sh-and-osexecute-are-refused-over-the-api).

## ssh: port forwarding is off

**An ssh session can no longer be used to reach anything else.** Every ssh
login already went straight into `sd` rather than a command prompt; the
server is now also told to refuse port forwarding, so `ssh -L`, `ssh -R` and
`ssh -D` against the machine are refused. `scp` and `sftp` were already
unreachable, because the session command was already forced.

**An administrator's own account has no special ssh or API route** — that
was tried and reversed the same day it was built (18 Sep 2026): the settled
rule is that Windows administrator status changes nothing about what an SD
account may do remotely. See [Reaching SDSYS](#reaching-sdsys) above.

## Nearly everything is lower case now

**Record ids no longer distinguish case, anywhere.** A file can hold `jack`
or `JACK` but never both; writing one when the other exists updates the same
record. This is how the system files always behaved; it now holds for every
file, including your own. `CREATE.FILE ... CASE` is no longer accepted.

**SD's own vocabulary, dictionaries, catalogued program names and several
VOC pointers are named in lower case** — but every lookup tries what you
typed first, then lower case, then upper case, so nothing you already type
stops working. This has its own page, with the exceptions and the upgrade
mechanics in full: [Lower case](11-lower-case.html).

**Upgrading converts your existing files for you**, and refuses to touch one
that would lose a record — see `nocase-upgrade.log` in the SD data folder,
and [Upgrading and uninstalling](01a-upgrading-and-uninstalling.html).

## The installer says less

**Every installer screen was cut down to what you need to install**: what
Setup changes, what to do next, and what to run if a step failed. The
explanations of *why* are gone from the wizard and live instead in
[Installing SD Core](01-installation.html#warnings-and-things-to-know),
under *Warnings and things to know*. Nothing Setup actually does changed.

**The `voc_template` directory is no longer installed** — it was a build-time
copy that nothing on an installed system ever read, and an upgrade removes
one an earlier release left behind.

## Upgrading is quieter, and no longer hangs

**Upgrading no longer stops for around five minutes and then reports
failure.** It used to ask, at sign-in, whether to update an account's VOC to
the new release — a question some upgrade steps trigger with no screen to
show it on and nobody to answer it. The installer already updates every
account's vocabulary itself, so the question is gone; upgrading finishes
without waiting on it.

**Each upgrade step now names itself before it runs**, and the two steps
that walk every account and every file — so they take longer the more you
have — say so.

**Uninstalling asks about your database and your settings file
separately.** Before, removing the database took `sd.conf` with it, because
both live in the same folder; you can now keep one and discard the other.
**Removing the Windows accounts `CREATE.ACCOUNT` made now actually works**
when the database is removed in the same pass — the two steps used to run in
an order that deleted the list of which accounts to remove before removing
them, which silently left every one of them in place, still able to sign
in.

## Printing reaches a real Windows printer

**A spooled print job (`SETPTR` mode 1) now goes to a Windows printer** — the
one named with `AT`, or your default printer — the same as OpenQM does. It
used to be handed to a Linux print command that does not exist on Windows,
and the job simply disappeared with no message.

> **One Windows setting to know about.** "Let Windows manage my default
> printer" (on by default in Windows 10 and 11) makes your default printer
> silently become the last one used *from any program* — which may be
> Microsoft Print to PDF. If you have more than one printer, turn that
> setting off and choose your default, or always name the printer with `AT`
> in `SETPTR`.

**`SENDMAIL` now says it is not supported, instead of reporting success and
sending nothing.**

## Python is back, running outside the database

**The `PY_` functions are available again** — twenty of them, declared in
`$INCLUDE SDPYFUNC.H`. **What is different from before they were withdrawn:
Python no longer runs inside `sd.exe`.** It runs in a separate program,
`sdpy.exe`, and a session talks to it down a pipe; the first `PY_` call
starts it and it goes away when the session ends. You need an all-users
install of Python 3.13 or later — a "for me only" install cannot be used —
and without one, every `PY_` function simply returns `-12040` and nothing
else is affected.

**Access follows the same rule as the shell.** Whatever governs `SH` and
`OS.EXECUTE` for an account — the `OS.USERS` grant, or being SDSYS — governs
Python too, since it can read and write files and start programs just as
freely.

## Smaller fixes worth knowing

- **Seven more prompts now show their default and take Enter as an answer**
  — the `DATA`/`DICT`/"use file" questions in `DELETE.FILE`, the three
  `CATALOG` questions, `.D`'s "delete VOC record", and `.S`'s "overwrite VOC
  record". Two prompts are deliberately unchanged because no is not a safe
  default either way: "delete all data components of multifile" and "use
  active select list".
- **Every command SD or the installer prints for you to run now says
  `powershell -ExecutionPolicy Bypass -File`.** They used to say `powershell
  -File`, which a stock Windows machine refuses outright — exactly when the
  advice was needed most, since these commands mostly appear after something
  has already gone wrong.
- **`DELETE.ACCOUNT` tells you when the account's directory did not actually
  go** — a file still open in it, or a denying access rule, used to leave it
  on disk with nothing said.
- **A session that dies without signing off is cleared within five
  minutes**, automatically, instead of needing `sd -cleanup` run by hand.
- **`COPY ... OVERWRITING DELETING` onto the same record** no longer writes
  it and then deletes it; it leaves the record in place and says so.
- **`LIST.READU` and `GETLOCKS` no longer risk a crash** when a lock is held
  for a session that has already gone — such a lock now shows its owner as
  `(gone)`.

## What might stop working

- **A script that names a tier keyword** — `CREATE.ACCOUNT ... STANDARD`,
  `MODIFY.ACCOUNT ... PROGRAMMER`, or a tier name used to lift a suspension —
  is now a syntax error. Drop the keyword, or say `UNSUSPENDED`.
- **A script or habit that used `LOGTO SDSYS` from an elevated ordinary
  session.** Sign in to Windows as SDSYS and start `sd` elevated instead.
- **An API program built against an older client library** cannot connect at
  all until it is relinked — the server waits for a TLS handshake that an
  old client never starts.
- **An API program that reads or writes files your own Windows account
  cannot** will now be refused, where an unprivileged-looking session used
  to have LocalSystem's reach without asking.
- **`SH` or `OS.EXECUTE` from a program that logs in over the API** cannot
  launch anything in this release; move that work to the console or ssh.
- **`ssh -L` / `-R` / `-D` (port forwarding) against the machine** is
  refused.
- **`CREATE.FILE ... CASE`** is refused; every file is nocase now.
- **A file with two ids differing only by case** is left untouched by the
  upgrade and named in `nocase-upgrade.log` — resolve those by hand, then
  convert the file with `CONFIGURE.FILE NO.CASE`.

## Continued in

[Upgrading and uninstalling](01a-upgrading-and-uninstalling.html) — what an
upgrade does and does not touch, and the mechanics of the two changes above
that affect it most: lower-case conversion and the quieter upgrade path.
