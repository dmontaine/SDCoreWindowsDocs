# The probes

Every measured value in the `User` set came out of one of these. They are kept
because a number in a document with no way to reproduce it is a number the next
session has to take on trust, and because a probe that has already been through
a review is cheaper to re-run than to rewrite.

Each one is SD BASIC, and each prints its own START and END markers so the
runner can refuse a run that died half way through.

## Which runner takes which probe

| runner | probes | what it refuses |
|---|---|---|
| `..\sdprobe.ps1` | `p14c-txn`, `p15*`, `p16*`, `p17-debug`, `p25-holdtrip` | a run without START, END and `0 error(s)` |
| `..\sdprobe2.ps1` | `p14-holder` + `p14-contender`, `p14b-holder` + `p14b-contender` | two sessions that did not demonstrably contend |
| `..\sdcompile.ps1` | `pcompile-restricted`, `pcompile-debug` | a compile that never reached the source, or that succeeded when it was meant to fail |
| `..\sddebug.ps1` | `p17-prog`, `p17-prog2` | a run where the debugger's `>` prompt never appeared |

```
tools\sdprobe.ps1  -Source tools\probes\p16-system.b
tools\sdprobe2.ps1 -Holder tools\probes\p14-holder.b -Contender tools\probes\p14-contender.b
tools\sdcompile.ps1 -Source tools\probes\pcompile-restricted.b -ExpectErrors
tools\sddebug.ps1  -Source tools\probes\p17-prog.b -Commands 'STACK','/N','S','R'
```

## What each one is for

| | |
|---|---|
| `p14-holder` / `p14-contender` | record locks and task locks under contention — `RECORDLOCKED()` -2, the `locked` branches, and the 252 ms a plain `readu` waits |
| `p14b-holder` / `p14b-contender` | the rest of the `RECORDLOCKED()` table — a shared `readl` seen from outside (-1) and a whole `filelock` (-3). **Signals go to a second file**, because a file lock blocks the other session's writes to the locked one |
| `p14c-txn` | transactions: what `commit`, `rollback` and a bare `end transaction` each do, the 3023 no-lock rule, and the `system(1008)` leak |
| `p15-sockets` | the socket family end to end. **The unresolvable-name test is deliberately after the END marker**: it blocks in the OS resolver and nothing after it would run |
| `p15b-blocking` | the one that matters — a socket read with nothing to read, timed. Proves the timeout is ignored unless the socket is blocking |
| `p15c-shape` | the worked client loop from the page, run rather than composed |
| `p16-system` | `system()`, `env()`, `config()`, `sysmsg()`, `checksum()`, `umask()` and the @variables |
| `p16b-osexec` | `os.execute` in an account without the right. It **aborts**, so the run is refused — the refusal is the result |
| `p16c-config` | `config()` with a lower-case name and with a name over eight characters. Both are after the END marker; the second aborts |
| `p17-debug` | what a session can tell about debugging without entering the debugger |
| `p17-prog` / `p17-prog2` | small programs to drive the debugger over: watch, breakpoint, step, `set`, and the variable types |
| `pcompile-restricted` | what an ordinary account may not compile — the internal-only intrinsics and the restricted statements |
| `pcompile-debug` | the same for the debugging family, run twice: with and without the `DEBUGGING` keyword |

## The rules they were written to

- **A probe that aborted prints values that look like measurements.** Hence the
  markers, and hence the runners refusing rather than reporting.
- **Anything that can block goes after the END marker**, so the measurement is
  banked before the risk is taken.
- **Two sessions need proof they overlapped.** `sdprobe2.ps1` requires the two
  user numbers to differ and the contender to name the holder; without that,
  a pair that ran one after the other prints a clean, wrong answer.
