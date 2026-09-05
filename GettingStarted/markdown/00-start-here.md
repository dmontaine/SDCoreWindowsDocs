Title: Start here
Subtitle: What this set covers, who it is for, and what it deliberately leaves out.

You already know MultiValue. This set does not teach it.

SD Core for Windows is a version of SD, with elements found in the main SD
version and in ScarletDME. ScarletDME was a fork of the original GPL release of
OpenQM 2.6.6.

**That lineage matters when you go looking for documentation.** Not all the
features of the **commercial** OpenQM 2.6.6 were in the GPL release, and **no
documentation specific to the GPL version was ever released**. So even the
OpenQM documents are not authoritative here.

**The OpenQM 2.6.6 documents can be used as a reference**, but SD Core has
additions, changes and deletions — of features, of structure, of security and
of commands. **These pages cover those changes.**

If you have used OpenQM, or SD on Linux, much of SD Core will still be
familiar: the same data model, the same query processor, the same BASIC.

## What "used to" means in these pages

These pages describe changes, so **used to**, **no longer** and **now**
run all through them. **The comparison is against the code this version was
made from** — SD on Linux, and ScarletDME and OpenQM 2.6.6 behind it.

**It never means an earlier release of SD Core for Windows**, because this is
the first one. Some of the changes are Windows-only and have no Linux original
to differ from; those say **earlier builds of this port** instead, so the two
are never confused.

## The pages

**There are fifteen, and they are numbered.** Read them in numerical order the
first time; after that they stand alone.

| | | |
|---|---|---|
| **00** | Start here | this page — what the set is and what it leaves out |
| **01** | [Installing SD Core](01-installation.html) | What the installer does, the two kinds of installation, upgrading and uninstalling |
| **02** | **[Your first thirty minutes](02-first-run.html)** | **Start here if you just want it working** — install to a second user signing in, in eight steps |
| **03** | [Running SD](03-running-sd.html) | The service, starting and stopping, and recovering from an unclean shutdown |
| **04** | [Scheduled jobs](04-scheduled-jobs.html) | Running an SD command on a timer, and the permit list that decides which ones |
| **05** | [Account types](05-account-types.html) | Standard, Programmer, Administrator, Suspended and Group — what each one is, how to make one, and how to change it afterwards |
| **06** | [Administrator commands](06-administrator-commands.html) | The verbs an administrator account gets, and how to use them |
| **07** | [Programmer commands](07-programmer-commands.html) | The development verbs a standard account does not get |
| **08** | [ssh access](08-ssh-access.html) | How people reach SD on this machine, and why it is ssh |
| **09** | [API access](09-api-access.html) | The client API, its port, and the login that replaced the old one |
| **10** | [Client distribution](10-client-distribution.html) | Which library an application needs, and the one file no installer can update |
| **11** | [Lower case](11-lower-case.html) | Case in commands, file names, record ids and account names |
| **12** | [Security](12-security.html) | The identity model, and what protects the database |
| **13** | [Other hardening](13-hardening.html) | Auditing, the shell permit list, and the rest |
| **14** | [Not in SD Core](14-not-in-sd-core.html) | What has been removed, and what to use instead |

## The five things most likely to surprise you

**1. Signing in asks for no password.** Windows has already authenticated you.
`sd` puts you in the SD account with your own name; if there is no such
account, or you are not in the `sdusers` group, you are refused. Administration
is gated on being an elevated Windows administrator, not on a secret SD holds.
See [Security](12-security.html).

**2. Accounts SD creates cannot log in to Windows at this machine.** They are
denied the physical console and Remote Desktop, deliberately. They reach SD
**over ssh, or through an API client, or both** — and which of those is a
required keyword on **`create.account`**. **Multi-user access over Remote Desktop
is not supported** and is not a gap to be filled later. See
[ssh access](08-ssh-access.html) and [API access](09-api-access.html).

**3. A new account gets a reduced VOC unless you say otherwise.** A standard
account cannot compile, catalogue, edit or create files. `programmer` and
`administrator` keywords on **`create.account`** decide that.
See [Account types](05-account-types.html).

**4. Commands and names are lower case now.** Everything that can be lower case
is. Typing in upper case still works — the lookup tries what you typed, then
lower, then upper. See [Lower case](11-lower-case.html).

**5. The API login is SCRAM, and the old cleartext one is gone.** Clients built
against the old protocol will not connect. See [API access](09-api-access.html).

## What this release is

**W1.0-0.** Windows only. There are no `#ifdef` branches keeping Linux alive in
this source — Linux SD is a separate project and this is not a build of it.

**It is a hobby project with no release schedule.**

This set is the delta. It covers installing SD Core on Windows, running it, and
what differs from OpenQM and from SD on Linux. The reference for the language
and the command processor is a separate set, and so is the administrator's.

## Reporting what you find

The two things worth reporting in most detail are **anything that behaves
differently from OpenQM and is not described here**, and **anything in these
pages that turns out not to be true of the build you are running**. The second
is as valuable as the first.

**Quote the version as `W1.0-0`** — the string in the header bar of every
page here, in the installer's file name, and in what `sd --version` reports.
The bare `1.0-0` is the same release; the `W` says it is the Windows one, and
that is the part worth keeping in a report.
