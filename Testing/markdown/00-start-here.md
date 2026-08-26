Title: Start here
Subtitle: What this set is, who it is for, and what it deliberately leaves out.

You already know MultiValue. This set does not teach it.

SD Core for Windows is a port of ScarletDME, which is a fork of OpenQM. If you
have used OpenQM — or SD on Linux — almost everything here will be familiar:
the same data model, the same query processor, the same BASIC. **These pages
cover only what is different**, so you can get a test system running and know
where the behaviour has changed under you.

Anything true of stock OpenQM is out of scope. If a verb is not mentioned in
this set, assume it behaves as you expect.

## The pages

**Read them in this order the first time.** After that they stand alone.

| | |
|---|---|
| [Installing SD Core](01-installation.html) | What the installer does, the two kinds of installation, upgrading and uninstalling |
| ***[Your first thirty minutes](02-first-run.html)*** | **Start here if you just want it working** — install to a second user signing in, in eight steps |
| [Running SD](03-running-sd.html) | The service, starting and stopping, and recovering from an unclean shutdown |
| [Scheduled jobs](04-scheduled-jobs.html) | Running an SD command on a timer, and the permit list that decides which ones |
| [Account types](05-account-types.html) | Standard, Programmer, Administrator and Group — what each one is and how to make it |
| [Administrator commands](06-administrator-commands.html) | The verbs an administrator account gets, and how to use them |
| [Programmer commands](07-programmer-commands.html) | The development verbs a standard account does not get |
| [ssh access](08-ssh-access.html) | How people reach SD on this machine, and why it is ssh |
| [API access](09-api-access.html) | The client API, its port, and the login that replaced the old one |
| [Client distribution](10-client-distribution.html) | Which library an application needs, and the one file no installer can update |
| [Lower case](11-lower-case.html) | Case in commands, file names, record ids and account names |
| [Security](12-security.html) | The identity model, and what protects the database |
| [Other hardening](13-hardening.html) | Auditing, the shell permit list, and the rest |
| [Not in SD Core](14-not-in-sd-core.html) | What has been removed, and what to use instead |

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

**It is a hobby project with no release schedule.** This first document set
exists so testers can find the edges. Comprehensive reference documentation
comes later; this is the delta.

## Reporting what you find

The two things worth reporting in most detail are **anything that behaves
differently from OpenQM and is not described here**, and **anything in these
pages that turns out not to be true of the build you are running**. The second
is as valuable as the first.

***QUOTE THE VERSION AS `W1.0-0`*** — the string in the header bar of every
page here, in the installer's file name, and in what `sd --version` reports.
The bare `1.0-0` is the same release; the `W` says it is the Windows one, and
that is the part worth keeping in a report.
