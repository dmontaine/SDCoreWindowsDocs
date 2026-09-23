Title: SD BASIC - Python Integration
Subtitle: Calling Python from a BASIC program - the helper-process model, access control, and the twenty-one PY_ functions.

This page continues [SD Client API](37-sd-client-api.html), which is the other
way a program outside SD reaches in; this one is a program *inside* SD
reaching out to Python.

## The model: a separate process, not a library

**Python does not run inside `sd.exe`.** It runs in its own program,
`sdpy.exe`, installed beside `sd.exe`, and a session that calls a `PY_`
function talks to it down a pipe. Nothing starts or stops it by hand: the
first `PY_` call in a session starts the helper, and it goes away when the
session ends.

**This is a rebuild, not a restoration of the old embedded interpreter.**
Python used to run as a library loaded into `sd.exe` itself; that is gone
permanently, because Python and the MSYS2 runtime `sd.exe` is built on
cannot safely share one process (`long` is a different width on each side).
Running Python as a separate program avoids the conflict by never being the
same process at all - and, as a side effect, a Python crash can no longer
take the database down with it.

**Requires an all-users install of Python 3.13 or later, and it is yours to
install.** Unlike a Linux machine, where Python is typically present
already, Windows does not ship Python and SD Core's installer does not
bring one - if this feature matters to you, install Python yourself,
for all users, before you need it. A "for me only" install cannot be found
or used. Without a usable Python on the machine, every `PY_` function
returns `-12040` and nothing else about SD is affected -
`PY_IS_INITIALIZED()` still works and answers `0`.

## Access control

**`PY_` access is gated exactly like `SH` and `OS.EXECUTE`** - the same
`os.users` field 2 permission, checked once, the first time a session calls
any `PY_` function, and the decision stands for the rest of the session:

| Result | Meaning |
|---|---|
| allowed | the helper starts (or a prior failure to start is retried) |
| `-12041` | this session may not use the operating system, so it may not have Python either |
| `-12042` | SD could not determine the permission at all (a damaged or unreadable `os.users` record) - one line is written to the error log saying which |
| `-12040` | the session **is** permitted, but the helper itself could not be started or has died - typically no usable Python on the machine |

SDSYS always has the permission, the same as it always has `SH` and
`OS.EXECUTE`. An ordinary account needs the grant an administrator gives
with `os.users` field 2, the same one that governs the shell - see the
Administrator set's *Operating System Access* chapter for how that grant is
made and read.

**This gate is Windows-specific and does not carry over to SD Core for
Linux.** Confirmed against their source, not assumed: Linux's Python
integration runs embedded in-process, with no separate helper to fail to
start and no permission check anywhere on the call path - it runs
unconditionally for any account there, the same shape their own `SH`/
`OS.EXECUTE` was left in once their equivalent gate was removed. A program
that checks for `-12041` to decide whether it may proceed will behave
correctly on Windows and never see that code at all on Linux.

## `$INCLUDE SDPYFUNC.H`

Declares all twenty-one functions. None of them is a TCL verb - there is no
way to call Python from a command prompt, only from a compiled BASIC
program.

```
$INCLUDE SDPYFUNC.H
```

## Starting and stopping the interpreter

| | |
|---|---|
| `PY_INITIALIZE()` | starts the interpreter if it is not already running. Returns `0` on success, or an error code below. Safe to call more than once - a second call is a no-op that also returns `0` |
| `PY_IS_INITIALIZED()` | `1` if the interpreter is running, `0` if not. Never fails and never needs the permission check, so it is the one `PY_` call safe to make from any session as a probe |
| `PY_FINALIZE()` | shuts the interpreter down. Rarely needed - a session ending does this for you |

```
st = PY_INITIALIZE()
if st # 0 then
   * st is one of the error codes below
end
```

## Running code

| | |
|---|---|
| `PY_RUNSTRING(script)` | compiles and runs `script` as Python source in the interpreter's global namespace. Returns `0` on success. An empty `script` is refused before it reaches Python (`status()` `1`) rather than sent as a no-op |
| `PY_RUNFILE(path)` | runs the Python source in the file at `path`, read on the machine `sdpy.exe` runs on. `path` is checked for shape before it is sent - an obviously unsafe or malformed path is refused (`status()` `1`) without reaching Python |

Python's own `print()` does not reach your terminal. `sdpy.exe`'s standard
output is the pipe protocol itself, not a console, so anything a script
prints is not visible - get a value back with `PY_GETATTR` instead.

## Reading what Python has

| | |
|---|---|
| `PY_GETATTR(name)` | returns the named Python object's value as a string. `name` is looked up in the interpreter's global namespace - this is how a value a script computed comes back into BASIC |
| `PY_OBJTYPE(name)` | returns the object's Python type name as a string - `str`, `list`, `dict`, `int`, and so on |
| `PY_OBJLEN(name)` | returns the object's length (`len()` in Python terms) as a number |

## Dictionaries

A Python dictionary created this way is a plain `dict` with string keys and
string values - not a general-purpose Python object store.

| | |
|---|---|
| `PY_CREATEDICT(name)` | creates an empty dictionary under `name` in the interpreter's namespace |
| `PY_CLEARDICT(name)` | removes every key from an existing dictionary, without deleting the dictionary itself |
| `PY_DICTVALSETS(name,key,value)` | sets `key` to the string `value` |
| `PY_DICTVALGETS(name,key)` | returns the string value stored under `key`, or an empty string if it is not there |
| `PY_DICTIDEL(name,key)` | removes `key` and its value |
| `PY_DICTGETKEYS(name)` | returns every key, tab-separated, in one string |
| `PY_DICTGETVALUES(name)` | returns every value, `@FM`-separated, in one string |

## Strings

| | |
|---|---|
| `PY_STRSET(name,value)` | creates or overwrites a Python string object called `name` with the string `value` |
| `PY_STRGET(name)` | returns the value of the string object `name` |

## Lists

**`PY_LISTCREATE` is the newest of the twenty-one**, added 14 Sep 2026. The
opcode and the C-side dispatch for it existed since Python's return, but
nothing in BASIC called it, so a list could be appended to and read but
never actually made - `PY_LISTAPPD` on a name nothing had created simply
failed. It is shaped exactly like `PY_CREATEDICT`, including reusing its
"already exists" code (`-12012`) rather than a list-specific one. *(SD Core
for Linux built the same function independently and called it
`PY_LISTCRTE` - if you are writing code meant to run on both ports, use the
name your target actually ships.)*

| | |
|---|---|
| `PY_LISTCREATE(name)` | creates an empty list under `name` |
| `PY_LISTAPPD(name,objname)` | appends the *object* named `objname` - a string, a dictionary, or another list already made with these functions - to the list `name` |
| `PY_LISTGETS(name)` | returns every item in the list, tab-separated, in one string |
| `PY_LISTCLR(name)` | empties the list without deleting it |

## Argument checking

**Every function refuses an empty name before it reaches Python at all**,
setting `status()` to `1` and returning an empty string, `0`, or `1`
depending on what the function normally returns on success - never one of
the `-120xx` codes below, which all describe something Python or the
helper process said. An empty name failing differently from a Python-side
failure is deliberate: the two causes need different fixes, and conflating
them was a known trap the error-code table below was itself corrected for
(see `-12040` / `-12041` / `-12042`).

## Error codes

Every function that returns a status uses one of these, defined in
`SYSCOM ERR.H`. They travel back from `sdpy.exe` over the pipe; the numbers
and their meanings are the same ones the earlier, embedded interpreter
used; only the mechanism moved.

| Code | Meaning |
|---|---|
| `-12001` | interpreter not initialised |
| `-12002` | failed to create the dictionary object |
| `-12003` | failed to link Python's built-ins into the running scope |
| `-12004` | an exception was raised while running the code |
| `-12005` | error reported while finalising the interpreter |
| `-12006` | could not open the script file (`PY_RUNFILE`) |
| `-12007` | key not found in dictionary |
| `-12008` | failed to convert a Python object to a string |
| `-12009` | error encoding a Unicode string to Latin-1 |
| `-12010` | cannot import `__main__` |
| `-12011` | could not get the `__main__` namespace dictionary |
| `-12012` | a dictionary of that name already exists |
| `-12013` | failed to add the object to the namespace |
| `-12014` | the requested object does not exist |
| `-12015` | failed to set a dictionary key or value |
| `-12016` | failed to delete a dictionary key or value |
| `-12017` | the named object is not a dictionary |
| `-12018` | error encoding a Latin-1 string to Unicode |
| `-12019` | the named object is not a string |
| `-12020` | failed to remove the object from the namespace |
| `-12030` | the object contains no items |
| `-12031` | failed to create a Python string object |
| `-12032` | failed to concatenate Python strings |
| `-12033` | failed to access a list item |
| `-12034` | the named object is not a list |
| `-12040` | permitted, but the helper process could not be started, or has died |
| `-12041` | this session may not use the operating system, so may not use Python |
| `-12042` | SD could not determine the operating-system permission at all |

**`-12040` used to mean all three of the last rows, and a caller could not
tell them apart** - "Python is broken", "you don't have the permission",
and "SD couldn't tell" all looked identical. Separated on the owner's
ruling, 12 Sep 2026, because confusing them tells an administrator Python
is broken when it is a permission, or tells an ordinary user they lack a
right when the real problem is a missing Python install. `-12040` kept its
narrower meaning; the other two are new.

**This table is not shared with SD Core for Linux above `-12034`.** Codes
`-12001` through `-12034` are the same on both ports, name and meaning.
Above that, each port went its own way: Windows reuses `-12014`, `-12033`
and `-12034` for `PY_LISTAPPD`/`PY_LISTCLR` failures rather than adding new
codes; Linux's build of the equivalent functions defines its own
`-12035`/`-12036`, and its `PY_LISTCRTE` (spelled differently there too —
see below) adds `-12037`/`-12038`. Windows has no code in that range at
all. A program meant to run on both should not assume a failure code above
`-12034` means the same thing on the other port.

## A worked sequence

This is the shape SD's own install-time check runs to confirm Python is
usable - starting the interpreter, running a line of Python, reading a
value back, and making a list:

```
$INCLUDE SDPYFUNC.H

st = PY_INITIALIZE()
if st then stop 'PY_INITIALIZE failed: ' : st

rs = PY_RUNSTRING("zz_probe = 'SDPY-' : str(6*7)")
if rs then stop 'PY_RUNSTRING failed: ' : rs

vv = PY_GETATTR('zz_probe')      * vv = 'SDPY-42' - Python did the arithmetic
ot = PY_OBJTYPE('zz_probe')      * ot = 'str'

lc = PY_LISTCREATE('zz_list')
if lc then stop 'PY_LISTCREATE failed: ' : lc
lty = PY_OBJTYPE('zz_list')      * lty = 'list'
```

## Continued in

*Differences from W1.0-0*, earlier in this set, for the short version of
what changed and why Python's return is a rebuild rather than a
restoration.
