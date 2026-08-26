Title: Installing SD Core
Subtitle: What the installer does to the machine, the two kinds of installation, and what upgrading and uninstalling touch.

There is no compiler to run and no dependency to resolve. SD Core for Windows
ships as a single `sd-setup-W1.0-0.exe`, carries its own runtime beside
`sd.exe`, and installs in one pass.

This is the largest single difference from the regular SD version — that, and
the fact that this version is for Windows and not Linux. In regular SD,
`installsdai.sh` existed because ScarletDME targeted four distributions and the
end user had to compile; Windows has one target and one ABI, so none of that
transfers.

## Before you start

**You need an elevated session.** The installer creates local groups, sets
file permissions, registers a service and assigns user rights. You can start
the install from a normal console session — you will get an elevation prompt.

***SD CANNOT BE INSTALLED SILENTLY.*** This is deliberate, not a missing
feature. The installer asks questions whose answers cannot be defaulted safely
— which kind of installation, whether to expose ports, and the password on the
account it makes for you.

**The installer does not ask where to put SD.** Both roots are fixed. See
[What lands where](#what-lands-where).

### It checks the machine before it changes anything

The installer refuses to start, and changes nothing, if it finds:

- another ssh server using port 22, or
- an ssh service that is not part of Windows, installed even if it is not
  running, or
- Windows' own ssh server with settings somebody has already changed.

It tells you what it finds — the service and its path, or the directive that
was added — so you can decide what to do. You may **remove the other ssh
server, or put the ssh configuration back the way Windows shipped it, and run
the installer again.**

Why it is this strict: accounts SD creates cannot log in to Windows at all, so
ssh is one of only two ways they reach the machine — and SD configures the ssh
server so those sessions land inside SD and cannot reach a command prompt. **SD
can only promise that about a server it installed and configured itself.**

> This check runs on a stand-alone installation too, even though a stand-alone
> installation never touches ssh. That is a known wrinkle rather than an
> oversight — the check runs before the wizard exists, so it cannot yet know
> which kind you are about to choose.

## The two kinds of installation

You are asked on a new page just after the welcome page, and only on a **first**
install. Upgrading keeps whatever the computer already is.

| | Full | Stand-alone |
|---|---|---|
| Who it is for | more than one person, or a program connecting to SD | one person at one computer, learning or trying code out |
| ssh server | installed if absent, and configured | **not installed, and nothing about ssh is changed** |
| Network port | API on 4243, local only unless you tick otherwise | **none — SD listens on nothing** |
| `create.account user` | works | **refused, and says why** |
| `create.account group` | works | works |
| scp / sftp | stop working, for everyone | **go on working** |

***NOTHING ELSE IS CUT DOWN.*** Same SD Core for Windows, same language, same
database, same commands. What a stand-alone installation lacks is the ways in
from somewhere else.

**Why `create.account user` is refused on a stand-alone install** rather than
quietly making something useless: the Windows account it would create is denied
the console and Remote Desktop because it is meant to arrive over ssh. With no
ssh server, it could sign in nowhere at all. You get a warning and no account
is made.

**To change your mind — stand-alone to full, or the other way — you must
uninstall and install again.** Nothing inside SD converts one into the
other.

## What lands where

Two roots, following Windows convention rather than the Unix layout stage 1
used.

| What | Where | Was, on Linux |
|---|---|---|
| Binaries, and the MSYS2 DLLs beside them | `C:\Program Files\SD\usr\bin\` | `/usr/local/bin` |
| The changelog | `C:\Program Files\SD\changelog` | — |
| Configuration | `C:\ProgramData\SD\sd.conf` | `/etc/sd.conf` |
| The SDSYS account | `C:\ProgramData\SD\sdsys\` | `/usr/local/sdsys` |
| User accounts | `C:\ProgramData\SD\user_accounts\` | `/home/sd/user_accounts` |
| Group accounts | `C:\ProgramData\SD\group_accounts\` | `/home/sd/group_accounts` |
| POSIX shared memory | `C:\ProgramData\SD\shm\` | `/dev/shm` |

**`usr\bin` is load-bearing, not tidiness.** Shipping `msys-2.0.dll` beside the
executable relocates the POSIX root to the DLL's directory minus two
components, so only that depth puts `/` on `C:\Program Files\SD\`. Do not move
the binaries.

**The DLLs ship beside `sd.exe` on purpose.** Do not change their location.

### Configuration

Server and client both read `SD_CONFIG`, then fall back to
`%ProgramData%\SD\sd.conf`.

`sd.conf` is installed `onlyifdoesntexist` and marked never to uninstall, so
your edits survive both upgrade and removal.

## What the installer creates on the machine

| | |
|---|---|
| `sdusers` | grants access to the files under `C:\ProgramData\SD`. Everyone who uses SD needs it |
| `sdsshonly` | carries the two deny rights that confine an account to ssh. Every non-administrator account SD creates joins it |
| `sdu_<name>` | one per account, created by **`create.account`** |
| the service | **String Database (SD)** |
| ACLs | inheritance is broken on `C:\ProgramData\SD` and access granted narrowly. This is what makes the database private from the rest of the machine |

***YOU MUST SIGN OUT AND BACK IN AFTER BEING ADDED TO `sdusers`.*** Windows
group membership is carried in your logon token. Until you get a new one, you
cannot read the data tree at all, and the symptom looks like a broken install.

## OpenSSH

**On a full installation an OpenSSH server is always installed if the machine
does not have one.** It is not optional. Accounts SD creates cannot log in to
Windows, so they reach the machine over ssh or through an API client — and an
install with neither is one nobody but you can use. A local-only machine is
served by `ssh localhost`, which needs no network.

***IT IS SLOW AND IT LOOKS LIKE A HANG.*** `Add-WindowsCapability` hands off to
`TiWorker` and can work for minutes with nothing on screen. **Never kill it** —
interrupting Windows servicing mid-flight is how the component store gets
corrupted. It may also leave a reboot pending, which is real; SD itself needs
none.

**If it cannot be installed, the install still succeeds.** It is a Features on
Demand capability and can be blocked by policy, a WSUS with no source, a
metered connection or an offline machine. The installer reports it in as many
words, with the command to retry — and you should read that report, because in
that state **no account but yours can sign in anywhere.**

**Remote access is off unless you ask for it.** Two tick boxes, both unticked:

| | |
|---|---|
| ssh from other computers | otherwise the firewall rule is scoped to `127.0.0.1,::1` |
| API from other computers | otherwise port 4243 is reachable from this computer only |

To open the API afterwards, from an elevated prompt:

```
powershell -File "C:\Program Files\SD\api-firewall.ps1" -Open
```

## At the end

The installer **finishes, and then opens SD** so you can set your own password.
It does not leave a wizard page waiting behind the session.

A Start Menu entry, **Check the SD installation**, runs a post-install check
you can re-run at any time. It closes on a keypress.

You are told plainly what setting no password costs, rather than being allowed
to skip past it silently.

## Upgrading

**Installing a new release over an existing one updates your database.**

| Replaced | Kept, and not touched |
|---|---|
| the catalogue and compiled programs | your accounts and their passwords |
| the BASIC source | the private catalogue |
| the messages and include records | which Windows users are linked to which SD accounts |
| the VOC templates and library routines | the commands each account may run |
| the SDSYS `BP` programs | your print queue and held reports |
| terminfo, the licence, the contributor list | everything under your own accounts, and `sd.conf` |

Anything SD created while it was running — your VOC included — is left exactly
as it is.

**The dictionaries are brought up to date for you.** Upgrading reapplies the
dictionary definitions the release ships: it adds and updates the entries SD
ships and leaves alone any you added. If that step cannot run, the installer
says so at the end rather than finishing quietly, and `upgrade-dicts.log` in
`C:\ProgramData\SD` says what happened.

***ONE THING YOU STILL DO YOURSELF: run `update.account` in each account after
upgrading***, to bring that account's VOC up to date with the new release.

> **SD only ever adds records to a VOC at an update, never removes them.** An
> account created before a verb was withdrawn keeps it. That is why
> **`update.account`** cannot be relied on to take something away.

## Uninstalling

It is the standard Windows uninstall — Settings ▸ Apps, or `unins000.exe`.

**The default does not touch your accounts, the database or the
configuration.** Inno removes only what it installed and only removes a
directory if it is empty, so everything the running system created is invisible
to it.

**Removing the data is a separate, opt-in prompt** that defaults to keeping it,
and says exactly what it destroys and where. ***A silent uninstall never
deletes the database***, whatever the prompt would have offered.

**The uninstaller does not remove OpenSSH.** It may predate SD or be in use by
something else. It does restore `sshd_config`, keeping the original as
`sshd_config.before-sd` — but it deliberately does **not** widen the firewall
rule back, because restoring it would mean opening a port on the way out.
