Title: The Installed Scripts
Subtitle: The thirty-seven PowerShell scripts installed beside SD - which the installer runs, which you may run yourself, and what their exit codes mean.

SD's installer does most of its work in PowerShell rather than inside the
installer script, and **it leaves every one of those scripts on the machine**.
They are in `C:\Program Files\SD`, beside `sd.exe`, and they are there for two
reasons: so that a step which failed during the installation can be run again
without reinstalling, and so that a choice made in the wizard can be changed
afterwards.

**They are Windows scripts, not SD verbs.** Nothing here is typed at an `sd`
prompt. Run them from a PowerShell prompt started with **Run as
administrator** - almost all of them refuse a prompt that is not elevated, and
say so rather than half-working. ***`check-install.ps1` IS THE EXCEPTION AND
WANTS AN ORDINARY PROMPT***; the section on it says why.

*Italics* mark something you supply, **bold** a word typed as it stands, and
braces an optional part.

## What is here and what is not

**Thirty-seven scripts ship.** They are the installer's own steps, the helpers
SD launches while it is running, and the ones the administrator verbs call.
Everything else in the project's
`gplbld` directory - the verifiers, the probes, the build and test cycle - is
development tooling and **is deliberately not installed**. If you have read
about `cycle.ps1`, `assert-current.ps1` or a `verify-` script and cannot find
it, that is why: they compare an install against the source tree it was built
from, and they are destructive.

## The exit codes are a convention

Every script prints what it did and then exits on the same three-value
convention:

| | |
|---|---|
| **0** | it is done. That includes *"it was already done"* - the scripts are written to be run twice |
| **1** | it failed, and the line above the exit says why |
| **2** | ***it neither did the work nor failed.*** It refused, or it could not run, or the work needs a restart first |

***2 IS THE ONE WORTH READING.*** It is not an error code; it means the script
declined to act and is telling you the condition. Each script below says what
its own 2 means, because they differ - a refusal in `allow-ssh-groups.ps1` is
not the same event as a pending restart in `install-ssh.ps1`. Only
`sd-elevate.ps1` adds a fourth, **5**, for *not elevated*.

## The ones you may need to run

These answer a question or change a decision. Every command below is complete
as written; run it from an elevated PowerShell prompt.

### Is the installation sound?

```
powershell -File "C:\Program Files\SD\check-install.ps1"
powershell -File "C:\Program Files\SD\check-install.ps1" -Brief
```

Exit **0** nothing is wrong, **1** something is. `-Brief` prints one line per
check with no preamble. **A check that cannot be answered yet is not a
failure** and it says so separately.

***RUN THIS ONE WITHOUT ELEVATION.*** It is the only script here that does, and
the reason is the question it asks: *can this user's ordinary sign-in reach
SD?* An administrator token reads the data tree through the `Administrators`
entry on the ACL and would pass whether or not the answer is yes. The script
notices it is elevated and says what the answer is worth, but that is a
backstop rather than the intent. The Start Menu entry **Check the SD
installation** runs it exactly this way.

***AND RUN IT AGAIN LATER.*** The installer offers this check as a tick box at
the end, and that run is **always the incomplete one**: the installing user's
logon token cannot carry the `sdusers` group until they sign out and back in,
so every database check reports *"not yet"* by design. The Start Menu entry is
there so the real run can be done afterwards without writing the command down.

### The ssh server would not install

```
powershell -File "C:\Program Files\SD\install-ssh.ps1"
```

Exit **0** installed and running, **2** installed but Windows needs a restart
before the service exists, **1** failed.

***THIS IS THE ONE THAT MATTERS MOST.*** Accounts SD creates sign in over ssh
and nothing else, so until this succeeds nobody but you can use that SD. The
installer prints this same command in its closing report when it could not
install the server; it is repeated here because that report is easy to close.
**It is slow** - `Add-WindowsCapability` downloads from Windows Update and can
work for minutes in silence. Do not interrupt it.

### An editor verb does nothing

```
powershell -File "C:\Program Files\SD\install-editors.ps1"
powershell -File "C:\Program Files\SD\install-editors.ps1" -CheckOnly
```

Exit **0** every editor is present, **2** at least one is missing and could not
be installed, **1** failed. `-CheckOnly` reports and installs nothing. What
happened last time is in `C:\ProgramData\SD\install-editors.log`.

### The SD service

```
powershell -File "C:\Program Files\SD\install-service.ps1" -Install
powershell -File "C:\Program Files\SD\install-service.ps1" -Remove
```

Exit **0** done, **1** failed, **2** could not be attempted - not elevated, or
`sdsvc.exe` is not there. `-Install` accepts *{-AppDir directory}* if SD is not
in the usual place.

### Who may reach the API from other computers

```
powershell -File "C:\Program Files\SD\api-firewall.ps1" -Show
powershell -File "C:\Program Files\SD\api-firewall.ps1" -Open
powershell -File "C:\Program Files\SD\api-firewall.ps1" -Restrict
powershell -File "C:\Program Files\SD\api-firewall.ps1" -Remove
```

Exit **0** applied, **1** failed, **2** refused. `-Show` changes nothing.
`-Open` allows any address, `-Restrict` this machine only; add *{-Port n}* for
a port other than 4243. **This script owns its rule** - it created it, and
`-Remove` takes it away.

### Who may reach ssh from other computers

```
powershell -File "C:\Program Files\SD\ssh-firewall.ps1" -Show
powershell -File "C:\Program Files\SD\ssh-firewall.ps1" -Installed -Restrict
powershell -File "C:\Program Files\SD\ssh-firewall.ps1" -Installed -Open
```

Exit **0** applied, **1** failed, **2** refused, or the rule is not there yet.

***IT TOGGLES A RULE IT DID NOT CREATE.*** Installing the OpenSSH capability
creates `OpenSSH-Server-In-TCP` and enables it for any address; this narrows it
to loopback or widens it again. It has no `-Remove`, deliberately: the rule is
Microsoft's and SD must not delete it.

### Who may ssh into this machine at all

```
powershell -File "C:\Program Files\SD\allow-ssh-groups.ps1" -Check
powershell -File "C:\Program Files\SD\allow-ssh-groups.ps1" -Installed
powershell -File "C:\Program Files\SD\allow-ssh-groups.ps1" -Remove
```

Exit **0** done or nothing to do, **1** failed, **2** refused.

***THE WRITE NEEDS `-Installed` AND THE SCRIPT'S OWN USAGE TEXT LEAVES IT
OUT.*** Without it you get *"-Installed not given"* and exit 2, and nothing is
written. The switch means *an administrator asked for this*: the script
rewrites `sshd_config` and restarts sshd, so it will not do that merely because
it was run. `-Check` and `-Remove` do not need it.

**It also refuses if `sshd_config` already says who may connect** - an existing
`AllowGroups`, `AllowUsers`, `DenyGroups` or `DenyUsers` line is somebody
else's decision and is left alone. That refusal is also exit 2, and it prints
the lines it found.

### The two remote-route groups

```
powershell -File "C:\Program Files\SD\sync-route-groups.ps1" -Check
powershell -File "C:\Program Files\SD\sync-route-groups.ps1"
```

Exit **0** success, **1** failure; it prints what it did either way. It creates
the groups that decide which remote route an SD account may use, and seeds
`sdssh` so an install that predates them does not lose ssh. `-Check` prints
what it would do and changes nothing.

### Re-stamping the account directories

```
powershell -File "C:\Program Files\SD\secure-account-dirs.ps1" -Root "C:\ProgramData\SD\user_accounts" -WhatIf
powershell -File "C:\Program Files\SD\secure-account-dirs.ps1" -Root "C:\ProgramData\SD\user_accounts"
```

Exit **0** every directory stamped, **1** at least one failed, **2** it could
not run. Add *{-Account name}* for one account rather than all of them.

**This is the only `secure-` script with a reason to be run again.** The others
name one fixed path and the installer has already done them; this one walks a
directory whose contents grow as accounts are made, and `create.account` stamps
each new account itself.

### May SD install on this machine?

```
powershell -File "C:\Program Files\SD\ssh-preflight.ps1"
```

Exit **0** clear to install, **1** refuse, **2** could not determine - which is
also a refusal. ***IT CHANGES NOTHING***: it reads the service registry, one
TCP table and two files. The installer runs it before the wizard is drawn, and
running it yourself is how you find out in advance why an installation would be
refused on a machine that already has an ssh server.

## The ones the installer runs

**You should not need any of these**, and running one out of order can undo
work rather than repeat it - most of them must run *after* the step that
secures the data tree, or inheritance puts back exactly what they took away.
They are listed so that a name in a log or an error message can be looked up.

| | |
|---|---|
| `adopt-account.ps1` | gives the installing user an SD account. Without it SD installs and then refuses the person who installed it |
| `deny-logon.ps1` | denies a local group the console and Remote Desktop, which is what confines an account to ssh |
| `finish-install.ps1` | the two steps that happen after the installer closes - SD opens so you can set your own password, then the post-install check runs |
| `install-service.ps1` | creates, starts and removes the Windows service **String Database (SD)** |
| `install-editors.ps1` | makes sure the editors the `edit` and `micro` verbs run are on the machine |
| `ssh-preflight.ps1` | asks whether SD may install here at all, and refuses a machine carrying an ssh server SD does not own. Runs before the wizard is drawn |
| `sync-route-groups.ps1` | creates the two groups that decide which remote route an account may use, and seeds `sdssh` so an existing install does not lose ssh |
| `upgrade-dicts.ps1` | brings an upgraded install's dictionaries up to the release. Runs on an upgrade only |
| `upgrade-voc.ps1` | brings every existing account's VOC up to the release, by running `update.accounts all`. Runs on an upgrade only |
| `secure-accounts.ps1` | the containers account directories are created in |
| `secure-account-dirs.ps1` | the ACL on each account's own directory |
| `secure-audit.ps1` | creates the audit trail and makes it append-only |
| `secure-cred.ps1` | locks the credential store to SYSTEM and Administrators |
| `secure-dumps.ps1` | makes the process-dump directory write-only to SD users, so a dump can be added and nobody else's can be read |
| `secure-gcat.ps1` | locks the global catalogue, and separately the compiled objects it is loaded from |
| `secure-log.ps1` | creates a log only administrators can see or write |
| `secure-osusers.ps1` | locks a permission list so only an administrator can change who is on it. The installer calls it four times - twice for `os.users` and twice for `batch.jobs` |
| `secure-pcode.ps1` | locks the pcode library, which is the interpreter every session runs |
| `secure-psdir.ps1` | the directory privileged scripts are written into |
| `secure-reclaim.ps1` | creates the profile-reclaim store and locks it to SYSTEM |
| `secure-sysdirs.ps1` | takes Modify off the system directories that nothing writes |

***THE `secure-` FAMILY IS WHAT KEEPS SD's USERS OUT OF SD's OWN FILES.*** The
data tree grants the `sdusers` group Modify, because every SD user needs it to
use the database at all, and that grant is inherited everywhere. Each of these
scripts takes it back off one thing that must not carry it.

## The ones an administrator verb calls

Four SD verbs change the machine rather than the database, and each of them
works by running one of these. **Prefer the verb.** It asks the questions that
need asking, reports what happened in the product's own words, and refuses
when it cannot act; the script does the work and assumes the caller knew what
they were doing.

| | Called by |
|---|---|
| `install-ssh.ps1` | `ssh.server install` |
| `remove-ssh.ps1` | `ssh.server remove` - takes the Windows OpenSSH server capability off the machine. The removal completes at the next restart |
| `ssh-firewall.ps1` | `remote.ssh on` \| `off` - scopes the shared Windows rule `OpenSSH-Server-In-TCP` rather than disabling it |
| `api-listener.ps1` | `remote.api on` \| `off` - writes or comments out the `APIPORT` line in `sd.conf` |
| `api-firewall.ps1` | `remote.api on` \| `local` - opens or restricts the API port |
| `sd-path.ps1` | `append.sd.path on` \| `off` - puts SD's program directory on the system PATH, or takes it off |
| `restart-sd.ps1` | offered by `remote.api on` and `off`, because the listener is only read at start-up |

The verbs are covered in the SD Core for Windows administrator documentation,
under *Remote access and the machine*.

## The ones the uninstaller runs

| | |
|---|---|
| `remove-sdaccounts.ps1` | takes away the Windows accounts SD created. Only runs if you ask for the data to be removed |
| `reclaim-profiles.ps1` | removes the Windows profiles SD had to leave behind at the time |
| `restore-sshonly.ps1` | puts every non-administrator SD account back into `sdsshonly`, reading the account register rather than anything local |

`restore-sshonly.ps1` is the repair for a half-finished removal: an account
that lost its deny rights but still exists would otherwise become an ordinary
ssh login on the machine.

## The ones SD runs for itself

These are launched by SD while it is running rather than by the installer.
**Do not run them by hand**; they are listed because they appear in logs and in
Task Manager.

| | |
|---|---|
| `sd-elevate.ps1` | the unelevated half of an administrator session, called by SD's `ELEVATE` program with `-Start`, `-Run` or `-Stop`. Exit 0 done, 1 failed, **5 not elevated or elevation refused** |
| `sd-elevate-helper.ps1` | the elevated half. `sd-elevate.ps1` launches it, which is where the UAC prompt appears, and it serves one SD session until that session ends |
| `micro-home.ps1` | gives the calling user a `micro` configuration home they can write to, and prints where it is. Run by the `EDIT` program before it launches `micro` |
| `reconcile-accounts.ps1` | removes register records whose Windows account has gone, and the account directory with them. Runs at every service start |

***A WINDOWS PROCESS'S TOKEN IS FIXED WHEN IT IS CREATED***, so nothing can
elevate a running process. That is why administrator work is done by a separate
helper process rather than by an elevated `sd.exe`: SD stays unelevated for its
whole life.
