Title: SD TCL - Printing and Spooling
Subtitle: Print units at the command prompt, keeping a job open, and capturing a session instead of printing it.

Printing is set up at the prompt and used from a program. **This page is the
prompt half**: the verbs that point a print unit somewhere, hold it open, and
capture what a session displays. The statements a program uses — `print on`,
`heading`, `printer file` — are in
[SD Basic - Printing](13-sd-basic-printing.html), and nothing here repeats them.

SD folds case, so a command may be typed in either case. Commands are shown here
in lower case. In the tables, *italics* mark something you supply and **bold**
something you type as it stands.

## Print units, and where they point

**Unit 0 is the terminal.** Every other unit is somewhere you have sent it.
**`setptr`** is how you look and how you set:

```
:setptr display
Unit Width Depth Tmgn Bmgn Mode Options
   0    80    66    0    0    1 
```

| Column | |
|---|---|
| **Unit** | the print unit number a program names in `print on n` |
| **Width**, **Depth** | the page, in characters and lines |
| **Tmgn**, **Bmgn** | top and bottom margins, in lines |
| **Mode** | what the unit does with the output |
| **Options** | everything else that has been set on the unit |

***THE DEPTH IS 66 AND THE TERMINAL IS NOT 66 LINES.*** Unit 0's page is a
printed page, not your screen — it is the size a report is paginated to when it
goes to a printer. The screen's own size is **`term`**, which is a different
setting on a different page:
[SD TCL - The Terminal and the Session](29-sd-tcl-the-terminal-and-the-session.html).

## Setting a unit

```
setptr unit, width, depth, top.margin, bottom.margin, mode {, options}
setptr default, width, depth, top.margin, bottom.margin, mode {, options}
setptr display
setptr unit, display
```

The positional arguments are all optional — `setptr 1,,,,,3` sets only the mode
of unit 1 — and **`nodefault`** keeps the values you did not name rather than
resetting them.

> ***`setptr` ASKS BEFORE IT CHANGES A UNIT, AND `brief` IS HOW YOU STOP IT.***
> That confirmation is a prompt, so a `setptr` inside a phantom, a script or an
> API session **hangs waiting for an answer nobody is there to give**. Give it
> `brief` in anything that is not a person at a keyboard.

The options are many and most are printer-specific. The ones worth knowing at
the prompt:

| | |
|---|---|
| **`as`** *name*, **`as pathname`** *path* | the name or path a mode 3 unit writes to |
| **`at`** *printer* | the Windows printer to send to |
| **`brief`** | suppress the confirmation prompt |
| **`keep.open`** | hold the unit open between jobs — see below |
| **`copies`** *n*, **`landscape`**, **`portrait`**, **`duplex`** | passed to the Windows spooler |
| **`newline cr`** \| **`lf`** \| **`crlf`** | the line ending written |
| **`nfmt`** | send the data with no formatting at all |
| **`style`** *name* | apply a report style |

**`paper.size`, `cpi`, `pcl`, `symbol.set`, `weight` and `overlay`** are the
printer-formatting set and behave as they always did.

## Holding a unit open

```
sp.open
sp.close
```

By default a unit finishes its job and releases when the program closes it, so
two reports become two print jobs. **`sp.open`** sets the keep-open flag so they
become one; **`sp.close`** clears it again. The flag shows up in `setptr`'s
Options column, which is the way to check it took:

```
:setptr display
   0    80    66    0    0    1 
:sp.open
:setptr display
   0    80    66    0    0    1 KEEP.OPEN
:sp.close
:setptr display
   0    80    66    0    0    1 
```

**Neither verb prints anything.** The Options column is the only report you get,
and it is worth looking at — a keep-open flag left set is why a report
occasionally arrives stapled to the one before it.

## Printing records

```
spool file.name record.id... {lines n m} {lnum} {lptr n}
```

**With no ids it prints select list 0**, so the usual shape is a `select`
followed by a `spool`. With no file name at all it refuses rather than guessing:

```
:spool
File name required
```

| | |
|---|---|
| **`lines`** *n* *m* | print only lines *n* to *m* of each record |
| **`lnum`** | number the lines |
| **`lptr`** *n* | send to print unit *n* rather than the default |

## Looking at what is queued

**`sp.view`** shows the records in `$hold` and offers to print them.

***IT IS A FULL-SCREEN FORM AND CANNOT BE DRIVEN DOWN A PIPE.*** It asks for a
printer number, then whether to print, then a confirmation — three prompts, so a
script that runs it stops and waits. Like the screen editors, it wants a person
at a terminal. Everything on this page except `sp.view` can be scripted.

`$hold` is an ordinary directory file in the account, so a script that needs to
work with held reports can read it with `select`, `list` and `spool` instead.

## Capturing a session instead of printing it

```
como on record.name
como off
```

**`como` writes everything the session displays into a record** in the `$como`
file, which it creates in the account the first time you use it. Measured end to
end:

```
:como on zzcomo
COMO file activated to zzcomo
:who
11 DON
:date
Thursday, 27 August 2026  01:13pm
:como off
COMO file deactivated
```

and the record afterwards:

```
:ct $como zzcomo
$como zzcomo
1: COMO file activated to zzcomo
2: 
3: 11 DON
4: 
5: Thursday, 27 August 2026  01:13pm
6: 
```

***IT CAPTURES THE PROMPTS AND THE ECHOES, NOT JUST THE OUTPUT.*** The record is
a transcript of the session, which is what makes it useful for showing somebody
what you did — and it means a COMO of a long run is larger than the output
alone. **`como off` is captured too**, as the last thing before the file closes.

To capture one command rather than a whole session, `execute ... capturing` in a
program is the better tool — see
[SD Basic - Program Control](02-sd-basic-program-control.html).

## Report styles

```
report.style
report.style name
report.style off
```

A report style is a stored set of print settings applied by name. With no
argument the verb says what the default is:

```
:report.style
No default report style has been set
```

which is what a fresh account reports. **`off`** clears it again.

## Printing on this port

**A named printer is a Windows printer**, and printing goes to the Windows
spooler rather than to a POSIX print command. There is no `lp` and no PostScript
pipeline. The consequences for a report that assumed either are set out in
[SD Basic - Printing](13-sd-basic-printing.html#printing-on-this-port), and they
apply the same way to a unit set up with `setptr`.

## See also

[SD Basic - Printing](13-sd-basic-printing.html) ·
[SD TCL - The Terminal and the Session](29-sd-tcl-the-terminal-and-the-session.html) ·
[SD TCL - The Query Processor](21-sd-tcl-query-processor.html).
