Title: SD Basic - System and Environment
Subtitle: Asking SD about itself, about the machine, and about the session you are in.

This page covers the enquiries: what time is it, who am I, where is the data,
what did the last thing that failed say, and what may this account do. Most of
it is one function, `system()`, and most of the surprises are about which form
a path comes back in.

SD folds case, so a program may be written in either case. Keywords are shown
here in lower case. In the tables, *italics* mark something you supply and
**bold** marks a word typed as it stands; braces mark an optional part.

> **Every result on this page was measured, not quoted.** The values below came
> back from a program run in an ordinary user account on SD Core for Windows
> W1.0-0. Values that are particular to that machine — a user number, a
> computer name, a process id — are marked as examples; the shapes are not.

## SYSTEM()

```
system(key)
```

### The session

| Key | | Measured |
|---|---|---|
| `7` | terminal type | `windows` |
| `9` | CPU time used, ms | `45` |
| `12` | time, as `time()` | `70787` |
| `18` | **user number** | `67` (example) |
| `23` | break key enabled? | `1` |
| `24` | echo enabled? | `1` |
| `25` | is this a phantom? | `0` |
| `26` | prompt character | `?` |
| `1000` | `capturing` in effect? | `0` |
| `1001` | case inversion on? | `0` |
| `1029` | internal subroutine depth | `0` at the top, `1` inside a `gosub` |
| `1030` | login time, internal | `1851017987` |
| `1031` | operating system process id | `605` (example) |
| `1050` | administrator? | `0` |

### The machine

| Key | | Measured |
|---|---|---|
| `31` | licence number | `0` |
| `42` | IP address | *empty* |
| `91` | **is this Windows?** | `1` |
| `1006` | Windows NT style? | **`0`** |
| `1009` | endian — 0 little | `0` |
| `1010` | platform name | `Windows` |
| `1012` | SD version | `W1.0-0` |
| `1013` / `1014` | user limit, without / with the phantom pool | `20` / `20` |
| `1015` | computer name | `Gitorli` (example) |
| `1017` | port number of a tcp connection | `0` |
| `1028` | system id | `1028` |

**Two of those three answer correctly and one does not.** `system(91)` reads
`1` and `system(1010)` reads `Windows`. **`system(1006)`, "Windows NT style?",
reads `0`** — it is the one to leave alone. **Ask `system(91)` whether this is
Windows**; it is the key this port sets deliberately for that purpose.

### Paths, and they are not all in the same form

| Key | | Measured |
|---|---|---|
| `32` | the `sdsys` directory | `C:\ProgramData\SD\sdsys` |
| `38` | the temporary directory | `/cygdrive/c/WINDOWS/TEMP` |
| `1011` | the configuration file | `C:/ProgramData/SD/sd.conf` |
| `1024` | the directory SD was started in | `/cygdrive/c/Users/dmont/OneDrive/Documents` |

**Three different spellings of a Windows PATH come out of one function.** A
backslash path, a POSIX `/cygdrive/` path, and a forward-slash path with a
drive letter. `@sdsys` agrees with key 32 and `@path` — the account directory —
is in the POSIX form.

**A `/cygdrive/` path handed to a Windows program does not work.** Windows
reads it as drive-relative and either fails silently or complains that the
parent directory does not exist. This is not theoretical: it is what stopped
the full-screen editors working the first time they were built for this port.
There is a conversion function in the kernel and **an ordinary program cannot
call it** — see "What is not here". **Take the path from configuration rather
than from `system()` if a Windows program is going to see it.**

### Lists and structures

| Key | | |
|---|---|---|
| `1002` | the call stack | field per level: `path`, then `offset` and line pairs. Measured: `.../BP.OUT/ZZMATH` at line 41, then `$CPROC` |
| `1003` | open files | field per file, `unit` and path. **`$ipc` is always one of them** |
| `1025` | environment variables | **two fields**: field 1 every name, field 2 every value, value-mark separated |

`system(1025)` measured **2** fields with 79 names in the first — it is not a
list of `NAME=value` pairs.

### Time

| Key | | |
|---|---|---|
| `1005` | internal time | `date() * 86400 + time()` — measured, the difference was **0** |
| `1020` | milliseconds since midnight | `9587454` |

`system(1020)` is the one to time something with. Measured against a lock wait
it gave 252 ms where `time()` would have given 0.

## DATE, TIME and TIMEDATE

```
date()      time()      timedate()
```

Measured together at one instant:

| | |
|---|---|
| `date()` | `21423` — days since 31 December 1967 |
| `time()` | `70787` — seconds since midnight |
| `timedate()` | `19:39:47 26 AUG 2026` |
| `oconv(date(), 'D4-')` | `08-26-2026` |
| `oconv(time(), 'MTS')` | `19:39:47` |

`@date` and `@time` hold the same numbers, **but they are set once per command**
rather than read afresh, so in a long loop they do not move while `date()` and
`time()` do.

`timedate()` returns a formatted string, not a number. Do not do arithmetic on
it — see
[SD Basic - Data Conversion](06-sd-basic-data-conversion.html) for the
conversion codes.

## ENV()

```
env(name)
```

**`env()` is case sensitive and a wrong case looks exactly like a missing
variable.** Measured:

| | |
|---|---|
| `env('PATH')` | 926 characters |
| `env('path')` | **0 characters** |
| `env('ProgramData')` | `C:\ProgramData` |
| `env('NOSUCHVAR')` | empty |

Windows itself treats environment variable names as case-insensitive
everywhere else, which is what makes this worth knowing. `ProgramData` works
only because that is exactly how Windows spells it. **Get the spelling from
`system(1025)` field 1 rather than from memory.**

## CONFIG()

```
config(name)
```

Measured on a stock installation:

| | |
|---|---|
| `config('FILERULE')` | `0` |
| `config('GRPSIZE')` | `2` |
| `config('MAXIDLEN')` | `63` |
| `config('NUMFILES')` | `80` |
| `config('NUMLOCKS')` | `100` |
| `config('SORTMEM')` | `4096` |
| `config('SPOOLER')` | empty |

**The name is case sensitive and at most eight characters. both failures now
look the same**, which is the point — a name that is too long is a name that
does not exist, and a caller cannot tell the two apart. Both measured:

| | |
|---|---|
| `config('numlocks')` — right name, wrong case | empty, `status()` **1004** |
| `config('NOSUCHKEY')` — **nine** characters | empty, `status()` **1004** |

**Keep every `config()` name to eight characters and upper case.**

*(A name over eight characters aborted the caller in earlier builds of this
port — *"Data cannot be converted to a string"* — because the length was
rejected before the result variable had been given a value. **Fixed 26 Aug 2026
and re-measured**: neither call aborts.)*

## SYSMSG()

```
sysmsg(number {, substitution ...})
```

Returns the text of one of SD's own messages, with `%s` substitutions filled
in. Measured:

| | |
|---|---|
| `sysmsg(2831)` | `Unrecognised statement` |
| `sysmsg(6711, 'ABC')` | `Unable to find source record ABC` |
| `sysmsg(2201)` | `Account name '' is not in register` — an unfilled substitution comes back empty |
| `sysmsg(99999)` | `[99999] Message not found` |
| `sysmsg(1)` | `[1] Message not found` |

**A message number is not a `status()` code.** They are separate numbering
schemes that overlap. `status()` **3006** is *record not found*; `sysmsg(3006)`
is `Modes: `. Do not render a status code by passing it to `sysmsg()`.

`get.messages()` takes **no arguments** and returned **nothing** — zero fields
— in an ordinary session. It reports messages sent between sessions, and
nothing had sent any.

## STATUS() and OS.ERROR()

`status()` carries the result of the last operation that sets one. It is
overwritten constantly, so **read it into a variable on the line after the call
you care about**, not three lines later. Every `status()` value quoted in this
document set was captured that way.

`os.error()` carries the operating system's own error number from the last call
that made one, and is `0` when nothing has failed.

Codes met while measuring this document set:

| | |
|---|---|
| `1004` | item not found |
| `1006` | bad action key |
| `1008` | action failed — `os.error()` has the detail |
| `1011` | timeout |
| `3001` | subfile not found |
| `3006` | record not found |
| `3007` | **no VOC record** — measured from a failed `open` of a name that is not in the VOC |
| `3021` | cannot gain exclusive access to a file |
| `3023` | write or delete with no lock held |
| `7005` / `7012` / `7013` | socket: cannot connect / cannot bind / closed |

## CHECKSUM()

```
checksum(string)
```

| | |
|---|---|
| `checksum('ABC')` | `451` |
| `checksum('abc')` | `291` |
| `checksum('ACB')` | `448` |
| `checksum('')` | `0` |
| `checksum('A' : @fm : 'B')` | **`-325`** |

It is case sensitive and order sensitive, and **it can be negative**, so a
program that stores it needs a signed field. It is a change detector, not a
digest: it is short, and it is not a security primitive.

## SDENCRYPT() and SDDECRYPT()

```
sdencrypt(data, key, encoding)
sddecrypt(data, key, encoding)
```

Three arguments. The encoding is `201` for hex or `202` for base64.

**A passphrase is not a key, and an ordinary program cannot make one.**
Measured: `sdencrypt('The quick brown fox', 'secretkey', 202)` returned
**nothing** and set `status()` to **10204**, a key length error. The key has to
be an encoded 256-bit key, and the function that derives one from a password is
`sdext()`, which is internal-only. **From an ordinary account these two
functions have no usable key**, and there is no way in.

## UMASK()

```
umask(n)
```

Sets the file creation mask and returns the **previous** value. A negative
argument asks without setting. Measured:

| call | returned | mask afterwards |
|---|---|---|
| `umask(-1)` | `2` | `2` — unchanged |
| `umask(18)` | `2` — the old value | `18` |
| `umask(-1)` | `18` | `18` |
| `umask(2)` | `18` | `2` — restored |

So the way to change it temporarily is to keep what the setting call returned
and pass it back.

## SENTENCE() and the @variables

`sentence()` and `@sentence` are the same thing — measured identical. Both hold
the command line that started the program: `RUN BP ZZMATH`.

| | Measured |
|---|---|
| `@who` | `DON` — **upper case** |
| `@logname`, `@user` | `don` — **lower case** |
| `@path` | `/cygdrive/c/ProgramData/SD/user_accounts/don` |
| `@sdsys` | `C:\ProgramData\SD\sdsys` |
| `@user.no` | `67`, the same as `system(18)` |
| `@tty` | **empty in a piped session** |
| `@system.return.code` | `1` |
| `@user.return.code` | `0` |
| `@crtwide` / `@crthigh` | `200` / `9999` — whatever `TERM` last set |

**`@who` and `@logname` differ in case for the same account.** Compare them
with `upcase()` on both sides or the test fails on a machine where it worked.

`set.exit.status` sets what SD returns to the operating system when the session
ends.

## OS.EXECUTE

```
os.execute command {capturing variable}
```

**It is gated per account, and a refusal aborts the program rather than
setting a status.** Measured in an ordinary account:

```
don is not permitted to use OS.EXECUTE at line 10 of .../BP.OUT/ZZMATH
```

The program stops there. There is no `else`, no `on error` and no status to
test, so **a program that may run in an account without the right must not
reach the statement at all**.

Permission is field 2 of the account's record in the system `os.users` file —
not a VOC entry and not a Windows privilege. An administrator's session passes
regardless. Ask your administrator to grant it; there is nothing a program can
do about it.

## LOGMSG

```
logmsg text
```

Writes a line to SD's error log. It has no return value and nothing to test.
Measured as reached and returning normally; **what `status()` says afterwards
is whatever the previous statement left there**, which is worth knowing because
it looks like a result.

## What is not here

**A whole family of functions is internal-only, and the compiler's complaint
names something else entirely.** Measured — this program, in an ordinary
account:

```
      v1 = kernel(28, 0)
      v2 = ospath('C:', 1)
      v5 = option('X')
      v6 = pterm(1, '')
```

compiles to, at the **last line of the program**:

```
41: Matrix KERNEL is not referenced in a DIM statement
41: Matrix OPTION is not referenced in a DIM statement
41: Matrix OSPATH is not referenced in a DIM statement
41: Matrix PTERM is not referenced in a DIM statement
WARNING: KERNEL is not assigned a value
```

A name the compiler does not know as a function is read as a **matrix
reference**, so the error is about a `dim` statement you never wrote, at a line
number nowhere near the call. **If a function you are sure exists produces
that, it exists and this account may not call it.** A call with three arguments
gives a different but equally misleading answer — `sdext(101, 'pw', 'salt')`
is *"Right bracket not found where expected"*, because a matrix takes at most
two subscripts.

Measured as internal-only: `kernel()` — and therefore the Windows path
conversion — `ospath()`, `option()`, `pterm()`, `sdext()`, `testlock()` and
`getlocks()`. The compiler's list is longer than that; those seven are the ones
this page put in front of it. They are reachable only from a program compiled
with `$internal`, which additionally requires an administrator in the `SDSYS`
account.

**And some statements are restricted the same way.** Measured as
*"Unrecognised statement"* in an ordinary account: `set.modes`, `reset.modes`,
`remove.token`, `release.lock`, `como`, `quit`, `keyboard.input`, `writepkt`,
and the whole debugging family — `debug.on`, `debug.off`, `debug.set`,
`breakpoint` and `watch`.

**`errmsg` is in the compiler's statement table and does not exist.** It
compiles to *"Unrecognised statement"* for everybody. Its opcode was removed in
July 2024 and the name was left behind in the table. **Being in the table is
not evidence a statement exists.**

**`sendmail`, `chgphant()` and `ccall()` compile for an ordinary account and
were not exercised.** `sendmail` needs a mail relay to be configured, `chgphant`
needs a phantom, and `ccall` needs a C function registered into the executable.
Nothing on this page depends on them.

**`procread` and `procwrite`** belong to the PROC language rather than to BASIC
and are only meaningful inside one.

## See also

[SD Basic - Program Control](02-sd-basic-program-control.html) ·
[SD Basic - Data Conversion](06-sd-basic-data-conversion.html) ·
[SD Basic - Debugging](17-sd-basic-debugging.html) ·
[SD Basic - Locks and Transactions](14-sd-basic-locks-and-transactions.html).
