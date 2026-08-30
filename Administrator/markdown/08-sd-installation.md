Title: SD Core for Windows - Installation and Setup
Subtitle: What the installer does, the two kinds of installation, upgrading, and uninstalling.

SD Core for Windows ships as a single `sd-setup-W1.0-0.exe`. There is
no compiler to run and no dependency to resolve. It carries its own
runtime beside `sd.exe` and installs in one pass.

> ***SD CANNOT BE INSTALLED SILENTLY.*** `/SILENT` and `/VERYSILENT`
> are refused. The installer asks questions whose answers cannot be
> defaulted safely — which kind of installation, whether to expose
> ports, and the password on the account it makes for you.

## Before you start

**You need an elevated session.** The installer creates local groups,
sets file permissions, registers a service and assigns user rights.
You can start the install from a normal console session — you will get
an elevation prompt.

**The installer does not ask where to put SD.** Both roots are fixed.

### It checks the machine before it changes anything

The installer refuses to start, and changes nothing, if it finds:

- another ssh server using port 22
- an ssh service that is not part of Windows
- Windows' own ssh server with settings somebody has already changed

It tells you what it finds so you can decide what to do.

## The two kinds of installation

| | Full | Stand-alone |
|---|---|---|
| Who it is for | more than one person, or a program connecting to SD | one person at one computer |
| ssh server | installed if absent, and configured | not installed |
| Network port | API on 4243, local only unless you tick otherwise | none — SD listens on nothing |
| `create.account user` | works | refused |
| `create.account group` | works | works |

Nothing else is cut down. Same SD Core for Windows, same language, same
database, same commands. What a stand-alone installation lacks is the
ways in from somewhere else.

To change your mind, uninstall and install again.

## What lands where

| What | Where |
|---|---|
| Binaries, and the MSYS2 DLLs beside them | `C:\Program Files\SD\usr\bin\` |
| The changelog | `C:\Program Files\SD\changelog` |
| Configuration | `C:\ProgramData\SD\sd.conf` |
| The SDSYS account | `C:\ProgramData\SD\sdsys\` |
| User accounts | `C:\ProgramData\SD\user_accounts\` |
| Group accounts | `C:\ProgramData\SD\group_accounts\` |
| Shared memory | `C:\ProgramData\SD\shm\` |

> ***DO NOT MOVE THE BINARIES.*** `usr\bin` is load-bearing: shipping
> `msys-2.0.dll` beside the executable relocates the POSIX root to the
> DLL's directory minus two components. Do not change their location.

## What the installer creates on the machine

| | |
|---|---|
| `sdusers` group | grants access to the files under `C:\ProgramData\SD` |
| `sdsshonly` group | carries the deny rights that confine an account to ssh |
| `sdu_<name>` | one per account, created by `create.account` |
| Service | **String Database (SD)** — automatic start |
| ACLs | inheritance broken on `C:\ProgramData\SD` and access granted narrowly |

## The service

| | |
|---|---|
| Display name | **String Database (SD)** |
| Service name | `SD` |
| Start type | automatic — Windows starts it at every boot |
| Starting | `Start-Service SD` or `sd -start` |
| Stopping | `Stop-Service SD` or `sd -stop` |
| Created by | the installer |
| Removed by | the uninstaller |

Stopping the service stops SD and ends every session on the machine.

### After an unclean shutdown

If SD is stopped abruptly, it leaves a shared memory segment behind. On
Windows that survives a reboot. SD now discards it and starts normally:

```
Discarding the shared segment left by the previous boot -
SD did not shut down cleanly.
```

## OpenSSH

On a full installation, an OpenSSH server is always installed if the
machine does not have one. It is not optional — accounts SD creates
cannot log in to Windows, so they reach the machine over ssh or through
an API client.

It is slow and looks like a hang. Never kill it. If it cannot be
installed, the install still succeeds — no account but yours can sign
in until it is. To retry:

```
powershell -File "C:\Program Files\SD\install-ssh.ps1"
```

## Remote access

Remote access is off unless you ask for it. Two tick boxes, both
unticked:

| | |
|---|---|
| ssh from other computers | otherwise the firewall rule is scoped to `127.0.0.1,::1` |
| API from other computers | otherwise port 4243 is reachable from this computer only |

## Upgrading

Installing a new release over an existing one updates your database.

| Replaced | Kept |
|---|---|
| the catalogue and compiled programs | your accounts and their passwords |
| the BASIC source | the private catalogue |
| the messages and include records | which Windows users are linked to which SD accounts |
| the VOC templates and library routines | the commands each account may run |
| the SDSYS `BP` programs | your print queue and held reports |
| terminfo, the licence, the contributor list | everything under your own accounts, and `sd.conf` |

Run `update.account` in each account after upgrading, to bring that
account's VOC up to date with the new release.

## Uninstalling

Settings - Apps, or `unins000.exe`. The default does not touch your
accounts, the database or the configuration. Removing the data is a
separate, opt-in prompt that defaults to keeping it.

The uninstaller does not remove OpenSSH. It restores `sshd_config`,
keeping the original as `sshd_config.before-sd`.
