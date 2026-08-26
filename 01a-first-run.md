Title: Your first thirty minutes
Subtitle: From a finished install to a working account, a file and a second user signing in over ssh.

This page assumes SD Core is installed and you have never used this port
before. It is a walkthrough, not a reference — every step links to the page
that explains it properly.

***DO THIS FIRST, BEFORE ANYTHING ELSE.***

## 1. Sign out of Windows and back in

**Not optional, and not a tidiness step.** The installer put your Windows
account into the `sdusers` group, and **Windows fixes group membership when you
sign in**. Until you get a new logon token you cannot read the database at all.

***THE SYMPTOM LOOKS LIKE A BROKEN INSTALL, NOT A PERMISSIONS PROBLEM***, which
is why it is step 1. The post-install check knows this: the run it offers at the
end of the installer is **always the incomplete one**, for exactly this reason.

Sign out, sign back in, then run **Check the SD installation** from the Start
Menu. It closes on a keypress.

## 2. Start SD

```
sd
```

You land in **the SD account named after your Windows login**. Nothing asks for
a password — Windows has already authenticated you.

**SD is already running.** It is a Windows service, `String Database (SD)`, and
Windows starts it at every boot. You do not type `sd -start`. See
[Running SD](01b-running-sd.html).

If `sd` answers *Account ... not in register*, you are in the wrong account or
step 1 has not taken effect. If it answers *not registered for SD use*, you are
not in `sdusers`.

## 3. Look around

```
who
listf
term
```

| | |
|---|---|
| `who` | the account you are standing in |
| `listf` | the files in it |
| `term` | your terminal type — should say `Device : windows` |

**If `term` says something else and your arrow keys do not work**, run
`term windows` for this session and see
[Other hardening](09-hardening.html#the-terminal). An account created before
the `WINDOWS` definition shipped keeps its old setting until `update.account`.

## 4. Make a file and put something in it

```
create.file customers
ed customers 1001
```

`ed` is the **line** editor and it is the editor this system uses. There is no
full-screen editor — `sed`, `update.record` and `modify` have all been removed.
See [Not in SD Core](10-not-in-sd-core.html).

In `ed`: `i` to insert, type your lines, a full stop on its own line to stop
inserting, then `fi` to file and exit.

```
list customers
count customers
```

**Commands are lower case now**, and so are the VOC records behind them. Typing
`LIST` still works — SD tries what you typed, then lower case, then upper. See
[Lower case](07-lower-case.html).

***THIS IS THE POINT AT WHICH MOST THINGS SHOULD FEEL LIKE OpenQM.*** If
anything in ordinary data work behaves differently and is not described in this
set, that is worth reporting.

## 5. Become an administrator

```
logto sdsys
```

**You will get a UAC consent prompt** unless the session is already elevated.
That is the gate — there is no SDSYS password, and there is deliberately no
second shared secret held by every administrator.

***IF YOU ARE OVER ssh, THIS MAY NOT WORK.*** A UAC prompt has no interactive
desktop there. Start an elevated terminal at the machine instead. See
[Security](08-security.html).

## 6. Create an account for somebody else

```
create.account user jane programmer both
```

Three things about that line, and each has caught people out:

| | |
|---|---|
| `programmer` | without it, `jane` gets a **standard** account and cannot compile, catalogue, edit or create files. See [Account types](02-account-types.html) |
| `both` | one of `ssh`, `api`, `both`, `none` is **required**. There is no default |
| it needs elevation | creating a Windows account cannot be done from a filtered token |

You will be prompted for Jane's password, masked. ***Refusing the prompt
creates nothing at all*** — a user account cannot exist without a password.

**The password is for the API.** Console and ssh logins ask for nothing.

## 7. Sign in as Jane

```
ssh jane@localhost
```

**You land directly inside SD**, not at a Windows prompt. That is the forced
command, and it applies to everyone who connects, administrators included.

***JANE CANNOT LOG IN TO WINDOWS AT THIS MACHINE.*** She is denied the console
and Remote Desktop by group membership, deliberately. She reaches SD over ssh
or through an API client — which is what the `ssh`/`api`/`both` keyword chose.
See [ssh access](05-ssh-access.html).

`ssh localhost` needs no network and works on a machine with no network
connection at all.

## 8. Leave

```
off
```

## What to try next, in rough order of how likely it is to find something

1. **Your own application data.** Restore a file you know and query it. The
   query processor is where most of the surface area is.
2. **A client program against the API.** Point it at port 4243 — **not** an ssh
   tunnel any more. It needs a client library from this release, because the
   old cleartext login is gone. See [API access](06-api-access.html) and
   [Client distribution](06a-client-distribution.html).
3. **A standard account.** Create one without `programmer` and confirm it can
   run your application but not edit it.
4. **An upgrade.** Install over the top and check your data survived and
   `update.account` brought the VOC forward.

## When something goes wrong

| | |
|---|---|
| Something SD did, and who did it | `audit`, in `C:\ProgramData\SD\sdsys` |
| Diagnostics, and API connections | `errlog`, same place |
| *"the account was not created — what happened"* | `sd-elevate.log`, in `C:\ProgramData\SD` |
| The installation itself | **Check the SD installation** on the Start Menu |

[Other hardening](09-hardening.html#the-logs) explains which log answers which
question — they are not interchangeable.

***WHEN YOU REPORT SOMETHING, SAY WHICH BUILD.*** The release stamp is on the
sign-on banner and in `C:\Program Files\SD\changelog`.
