Title: Operating System Access
Subtitle: The `sh` and `!` verbs, the list that decides who may use them, and why the list is keyed to the person rather than the account.

`sh` runs a Windows command from the SD prompt. `!` is the same verb under a
shorter name. **They are the only way out of SD to the operating system from
TCL**, and who may use them is decided by a file in the system account rather
than by an account's tier.

> ***THIS DOCUMENT IS SEPARATE SO THAT IT CAN BE WITHHELD.*** It links to
> nothing outside the administrator set. Where a user-set page is worth naming,
> it is named in words.

SD folds case, so a command may be typed in either case. Commands are shown here
in lower case.

> **Every listing on this page was produced by running it**, on SD Core for
> Windows W1.0-0, from an unelevated session in an account that is on the list.

## The two verbs

```
sh command
! command
```

Everything after the verb is handed to the shell as typed:

```
:sh echo hello-from-the-shell
hello-from-the-shell
:! echo via-the-bang-form
via-the-bang-form
```

***NEVER TYPE `sh` WITH NOTHING AFTER IT IN A SCRIPT.*** The configured shell
for the bare form is interactive — `config` reports it as

```
SH        C:/Windows/System32/WindowsPowerShell/v1.0/powershell.exe -NoProfile -NoLogo
SH1       C:/Windows/System32/WindowsPowerShell/v1.0/powershell.exe -NoProfile -NonInteractive -Command
```

so a bare `sh` in a piped session, a phantom or a scheduled job hands control to
a shell with nobody at the keyboard and **waits for ever**. The `SH1` form,
which is what `sh command` uses, is `-NonInteractive`.

## The shell you get is Windows PowerShell 5.1

Not `pwsh`, and the difference bites:

```
:sh echo delta && echo epsilon
At line:1 char:12
+ echo delta && echo epsilon
+            ~~
The token '&&' is not a valid statement separator in this version.
```

***`&&` AND `||` DO NOT EXIST THERE.*** Nor do the ternary, null-coalescing or
null-conditional operators. Chain with `;`, and test with `if ($?) { … }`.

**Pipes and redirection do work**, for an account that is on the list:

```
:sh echo alpha-beta | findstr alpha
alpha-beta
:sh echo gamma > zzsh.txt
:sh Get-Content zzsh.txt
gamma
```

The second and third lines are separate `sh` invocations, so **the working
directory persists between them** — the file written by one was read by the
next.

## SD refuses to nest

```
:sh sd
SD is already running in this session - type EXIT to return to it.
```

The child shell is marked, and SD checks the mark:

```
:sh Get-ChildItem Env:SD_SESSION
Name                           Value
----                           -----
SD_SESSION                     1
```

**That is worth knowing when writing a script for `sh` to run** — anything it
invokes inherits `SD_SESSION`, so a script that starts SD as part of its work
will be refused, wherever it is called from.

## Who is allowed: `os.users`

***THE PERMISSION IS A RECORD IN A FILE IN THE SYSTEM ACCOUNT, NOT A TIER.***
`sdsys/os.users` holds one record per person:

| | |
|---|---|
| **record id** | the **Windows login name** |
| **field 1** | `yes` to allow `sh` and `!` |
| **field 2** | `yes` to allow `OS.EXECUTE` from a program, and the screen editors |

Anything other than `yes` means no, and **a missing file or a missing record
means no**. That is the opposite of the tier lists, where a missing record means
the full set — do not carry the convention across.

***IT IS KEYED TO `@logname`, THE PERSON, NOT THE ACCOUNT.*** The permission
therefore does not change when somebody `logto`s somewhere else. That is
deliberate: the question *may this person reach the operating system* has one
answer per person, and an account they can enter should not be able to change
it.

### Editing it

`os.users` is an ordinary SD file in the system account, edited with `ed` from
`SDSYS` — which needs an elevated session to enter. **`create.account` writes
the record for an administrator account as it creates it**, with both fields
`yes`, and `modify.account`'s `sh-on`/`sh-off`/`os-on`/`os-off` keywords set the
two fields afterwards. Hand-editing remains the only route for the case those
keywords refuse.

> ***THE FILE'S ACL IS THE WHOLE OF THE PROTECTION.*** `os.users` is read-only
> to `sdusers` on disk, which is what stops somebody adding their own name to
> the list from inside their own account. The command processor reads it in the
> user's own process. **Without that ACL this control is decoration** — if you
> are hardening an installation, check it rather than assume it.

## The three outcomes

The gate and the metacharacter rule are separate tests, and they combine like
this:

| | plain command | pipes, redirection, chaining |
|---|---|---|
| **on the list** | runs | **runs** |
| not listed, **elevated** | runs | refused **5240** |
| not listed, unelevated | refused **10053** | refused **10053** |

```
don is not permitted to use the operating system shell
```

is message 10053, and it names the person rather than the account.

***THE MIDDLE ROW IS THE ONE PEOPLE MISREAD.*** An elevated session that is not
on the list keeps a restricted shell: it may run a command, but not one
containing shell metacharacters. **Being on the list is what buys a real
shell** — pipes, redirection and chaining are most of what a programmer wants
one for, and that was the ruling behind lifting the ban for listed accounts.
Elevation on its own does not lift it.

## What this does not gate

***A PROGRAM'S `OS.EXECUTE` IS NOT ON THIS PATH.*** `OS.EXECUTE` from SD BASIC
compiles to a different opcode and is governed by field **2** of the same
record, not by field 1 and not by the metacharacter test. So the two halves are
set independently, and `sh-off` deliberately leaves `OS.EXECUTE` alone.

**The form that does go through this gate is `execute 'sh …'` from a program**,
because that runs the TCL verb.

**The screen editors read field 2**, not field 1 — an account can be refused
`sh` and still run `edit` and `micro`, and the reverse.

## Who has these verbs

`sh` and `!` are administrator-tier, so an ordinary account does not have the
names. ***AND THE TIER IS NOT THE PERMISSION*** — an administrator account whose
Windows login is not in `os.users`, and whose session is not elevated, has the
verb and is refused by it. **Two gates, and both must pass.**

## An SD administrator is a remote shell

State this plainly to anyone deciding who gets an administrator account:

**An SD administrator can run operating-system commands on the server, as
LocalSystem, from any machine that can reach the API port.**

Nothing here is a defect, and no single setting produces it. It follows from
three rules that are each reasonable on their own:

| | |
|---|---|
| An administrator always has API access | and it cannot be taken away |
| An administrator always has `OS.EXECUTE` | and that cannot be taken away either |
| For a session that arrived over a socket, `os.users` is the authority | the session's own token is LocalSystem |

Put together, they mean the administrator tier carries remote command execution
on the machine. That was measured end to end over a remote API connection, with
the operating system reporting `nt authority\system`.

**Do not treat "the API only listens on loopback" as a mitigation.** The port is
reachable from another machine over an ssh tunnel, so a reader who concludes
that a shut firewall closes this has drawn the wrong conclusion. What limits it
is who holds an administrator account and who holds a credential for one.

The verify suite asserts this behaviour, so a future change that quietly
withheld `OS.EXECUTE` from a socket session would show up as a failing test
rather than as a page that had silently become false.

## The first logto out of the system account ends elevation

An administrator working in `SDSYS` is elevated. **The moment they `logto`
anywhere else, that elevation is given up** — the administrator flag is cleared
and the elevated helper is stopped.

This is deliberate. Without it the helper would outlive the rights it belongs
to, leaving a session able to do privileged work from an ordinary account.

The consequence a reader meets first is that **a second hop is refused**:

```
:logto sales
:logto payroll
```

The second `logto` is not running as an administrator any more, so it costs a
fresh UAC prompt. Recover by going back:

```
:logto sdsys
```

An administrator who chains two hops and does not know this will read it as a
fault. It is the design working.

The step is quiet for the ordinary case: a session moving between two ordinary
accounts never had privilege, so nothing is given up and nothing is written to
the audit trail.

## See also

[Accounts and Security](01-accounts-and-security.html) ·
[Sessions and Locks](02-sessions-and-locks.html) ·
[Remote Access and the Machine](05-remote-access-and-the-machine.html).
