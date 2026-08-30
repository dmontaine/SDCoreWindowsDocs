Title: SD Administration - Configuration
Subtitle: The config command, the sd.conf file, and every configuration parameter in the Windows port.

The `config` command reports the configuration parameters in force. The
configuration file is `C:\ProgramData\SD\sd.conf`.

```
config
config('NUMFILES')
```

## The configuration file

`sd.conf` is a text file read at start-up. It is installed
`onlyifdoesntexist` and marked never to uninstall, so your edits
survive both upgrade and removal.

Server and client both read the `SD_CONFIG` environment variable, then
fall back to `%ProgramData%\SD\sd.conf`.

## Active configuration parameters

### System limits

| Parameter | What it controls |
|---|---|
| `NUMFILES` | maximum open files per session |
| `NUMLOCKS` | maximum locks per session |
| `GRPSIZE` | group size for dynamic files |
| `MAXIDLEN` | maximum record id length |
| `CMDSTACK` | depth of the command stack |
| `OBJECTS` | maximum object count |
| `OBJMEM` | object memory |

### Locking

| Parameter | What it controls |
|---|---|
| `DEADLOCK` | deadlock detection interval |
| `MUSTLOCK` | whether `writeu` requires a prior `readu` |

### Printing

| Parameter | What it controls |
|---|---|
| `PTYPES` | printer types available |
| `PDUMP` | printer dump |

### Diagnostics

| Parameter | What it controls |
|---|---|
| `ERRLOG` | error log size (trims oldest when exceeded) |
| `FSYNC` | flush interval for the error log |

### Precision

| Parameter | What it controls |
|---|---|
| `PRECISION` | decimal precision for arithmetic |

### API

| Parameter | What it controls |
|---|---|
| `APIPORT` | the port the API listens on (default 4243). If not set, no socket is created — "no API" is a real state |
| `APILOGIN` | whether the API demands a password. `APILOGIN=0` is the **weaker** setting, not the safer one |
| `NETDIRS` | directories outside the account an API session may reach (semicolon-separated). The credential file, the program catalogue and the account register are never reachable |

### Shell

| Parameter | What it controls |
|---|---|
| `SH` | the shell command for `sh` at the prompt |
| `SH1` | the shell command for `sh` from a non-interactive context |

The default shell is PowerShell:

```
SH        C:/Windows/System32/WindowsPowerShell/v1.0/powershell.exe -NoProfile -NoLogo
SH1       C:/Windows/System32/WindowsPowerShell/v1.0/powershell.exe -NoProfile -NonInteractive -Command
```

## Inert parameters

These are accepted in `sd.conf` but do nothing in SD Core for Windows.
An existing configuration file brought from another install still
works.

| Parameter | Status |
|---|---|
| `NETFILES` | accepted, parsed, never consulted — QMNet was removed |
| `FILERULE` | accepted, parsed, never consulted — QMNet was removed |
| `CREATUSR` | accepted and ignored — `config` no longer lists it; `config('CREATUSR')` returns nothing |

## Removed parameters

| Parameter | Status |
|---|---|
| `umask` | removed from every tier — Windows does not use POSIX file-mode bits for security |

## Global vs. private parameters

`config` without an argument reports all global parameters. Private
parameters are set per-session with `set` and reported with `set` or
`status`.

## Licence management

```
update.licence
```

`update.licence` is an administrator command that updates the SD
licence. It is not a configuration parameter — it is a verb that writes
to the licence file.
