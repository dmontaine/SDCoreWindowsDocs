Title: API access
Subtitle: The client API, the port it answers on, the login that replaced the old one, and what a remote session may reach.

The client API is the reason this port exists. SD Core for Windows is built to
be used as a back end data store reached through the API, and that is the
tie-breaker on most other design questions here.

***THE API IS NOT JUST FOR DEVELOPERS AND ADMINISTRATORS.*** It is a normal way
for **any** account to use SD. A person running a custom GUI program that talks
to SD needs API access and may need nothing else — no ssh, no terminal, no
development verbs. A standard-tier account with `api` access is an ordinary
thing to create, and probably the commonest shape a deployed system will have:

```
create.account user jane api
```

Your application code does not change. `SDConnect()` and `SDConnectLocal()`
take the same arguments and return the same things. **What changed is
underneath: the login protocol, the port, the identity a session runs as, and
what it is allowed to open.**

> **The account's tier and its access route are independent.** Tier decides
> which verbs are in the VOC ([Account types](04-account-types.html)); `ssh` /
> `api` / `both` / `none` decides how the account is reached. A standard
> account with API access, a programmer with ssh only, and an administrator
> with both are all normal.

## The login is SCRAM-SHA-256, and the old one is gone

***A CLIENT THAT SENDS A PASSWORD IN CLEAR IS REFUSED.*** It gets *"Cleartext
login is no longer supported; this server requires SCRAM authentication"* and
the connection drops.

The API used to send the user name and password as plain text — anything able
to watch the connection could read the password. It now runs a challenge and
response: the server sets a puzzle only someone who knows the password can
answer, and **the password itself is never sent in any form.**

***THE SERVER ALSO PROVES ITSELF TO YOU.*** It finishes by returning a value
only the real server can compute, and the client refuses the connection if it
does not match. Another program that grabbed the port before SD started cannot
pretend to be SD in order to collect passwords.

### What you have to do

| | |
|---|---|
| **Use a client library from this release or later.** | An older one is refused outright |
| **Run `modify.password` again for every account that uses the API.** | The stored credentials changed shape and the old ones cannot be converted |

***AN ACCOUNT WHOSE PASSWORD HAS NOT BEEN RE-SET IS REFUSED, AND THE REFUSAL
READS AS A WRONG PASSWORD.*** From the server's point of view there is no
credential to check. If a working client suddenly cannot log in after an
upgrade, this is the first thing to try.

The old credentials cannot be converted because **the password was never kept
anywhere, by design** — there is nothing to convert them from.

**Programs using the `!sdclient` class are covered.** The class module BASIC
programs use to reach another SD server speaks the new login too. Your code
does not change — `connect()` takes the same arguments — but the program has to
be running under this release **at both ends**.

**`SDConnectLocal()` connections are unaffected.** They send no password and
never did.

## The port

**`sd.conf` sets `APIPORT=4243`**, and the server accepts API connections on
any network interface. It used to ship commented out and listen on `127.0.0.1`
only, which is why an ssh tunnel was needed.

***IF YOU TUNNEL, STOP.*** `ssh -L 4243:127.0.0.1:4243 user@host` still works
but is no longer what the design expects, and it is not tested. Point the
client straight at port 4243 on the server.

**Reaching the port from another computer is off unless you tick the box during
installation.** To change it afterwards, from an elevated prompt:

```
powershell -File "C:\Program Files\SD\api-firewall.ps1" -Open
powershell -File "C:\Program Files\SD\api-firewall.ps1" -Restrict
```

**To turn the API off altogether**, comment out the `APIPORT` line in
`C:\ProgramData\SD\sd.conf` and restart SD. With no `APIPORT` set, SD creates
no socket at all — "no API" is a real state, not just a firewall rule.

> ***A STAND-ALONE INSTALLATION HAS NO API.*** Its `sd.conf` is written with no
> `APIPORT` line, so nothing listens and there is no firewall rule to open.

> ***`APILOGIN` IS NOT AN OFF SWITCH.*** It decides whether the API demands a
> password. `APILOGIN=0` is the **weaker** setting, not the safer one. Do not
> reach for it.

## Reaching the port is not getting in

A caller must clear three gates, in this order:

1. **Complete the SCRAM exchange** against a password held for that account —
   so **an account with no password cannot connect at all**.
2. **Be a member of the `sdapi` group**, which no account joins unless you put
   it there. `create.account user fred api` or `... both` does that; `ssh` or
   `none` does not.
3. **Pass the account's own group check.**

***FAILED API LOGINS ARE WRITTEN TO THE AUDIT TRAIL***, with the reason. See
[Other hardening](12-hardening.html).

## A session is confined to its own account

***UNTIL 21 Aug 2026 A CLIENT CONNECTING OVER THE API COULD OPEN ANY FILE ON
THIS MACHINE — INCLUDING THE FILE SD KEEPS PASSWORDS IN.*** Holding one
ordinary account's password was enough, and no administration command was
needed. **If you have used a build older than that, treat the passwords of
every account as having been reachable.**

| | |
|---|---|
| **Still allowed** | everything inside its own account, and the shipped SDSYS files every account needs — messages, `syscom`, the dictionaries, `sd.voclib`. Ordinary programs are unaffected |
| **No longer allowed** | opening, renaming, deleting or listing anything else |

**A refused `OPEN` takes the `ELSE` branch and `STATUS()` is 3035**, which
means *not permitted* rather than *not found*. That distinction matters when
you are debugging: 3035 is a containment refusal, not a missing file.

### If your data lives outside an account

Name the directory in the **`NETDIRS`** setting in `C:\ProgramData\SD\sd.conf`,
separating several with a semicolon. Nothing else needs changing.
`config('NETDIRS')` prints what is in force.

***THE PASSWORD FILE, THE PROGRAM CATALOGUE AND THE ACCOUNT REGISTER ARE NEVER
REACHABLE from an API session, and cannot be added to `NETDIRS`.***

## An API session runs as you

***RECORDS AN API SESSION CREATES ARE OWNED BY THE ACCOUNT THAT LOGGED IN***,
and the session reaches files with your access rather than the service's. If
your account may not read something, the API session may not read it either.

This was not true before 24 Aug 2026, and the way it failed is worth knowing
because it was invisible: taking on your Windows identity applied only to the
one thread that did it, and starting a short-lived helper process during the
switch quietly put the session back to the service's own identity — **with no
error and nothing in the log** — before it had opened a single file. So the
login half worked and the part you would notice did not: records came out owned
by the system account.

***IF YOUR IDENTITY CANNOT BE TAKEN ON, THE LOGIN IS NOW REFUSED*** rather than
continued with the service's identity. A session that believes it is you while
holding the service's rights is worse than one that never started.

**There is an alarm for the condition returning.** If a session ever believes
it is you while Windows says it is not, the error log gets:

```
API IDENTITY LOST at record write - session believes it is ...
```

Nothing is written when the two agree, so **a healthy session is silent** and
you should never see this. It refuses and slows nothing; it exists so the
condition cannot go unnoticed a second time.

## `sh` and `OS.EXECUTE` are refused over the API

They used to work, **and they ran as the LocalSystem account** — so a remote
client could run any command on the machine with full privilege, which is more
than the administrator sitting at the keyboard gets.

An API session is no longer treated as an administrator for any purpose, which
is what SD's own code already assumed and did not enforce.

## Client libraries

| | |
|---|---|
| 64-bit | `sdclilib.dll` |
| 32-bit | built separately; 32-bit remains a supported target, not a test convenience |

**Both must come from this release or later.** A client library that predates
SCRAM is refused by the server, and the 32-bit client in particular once
shipped sending passwords in clear — check which one your application is
actually loading.
