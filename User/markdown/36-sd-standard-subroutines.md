Title: SD Standard Subroutines
Subtitle: The !-prefixed internal subroutines that ship with SD, what each does, and how to call them.

SD ships a set of catalogued subroutines whose names begin with `!`.
They are part of the system — compiled into the pcode library and
available to every account. They are called from SDBasic with `call`
or from an I-type expression with `SUBR()`.

> ***These are internal subroutines.*** They exist to support the system
> and the query processor. They are documented here because they are
> callable, but they are not versioned as a public API. A program that
> calls one should test the result and not assume a particular
> internal behaviour.

## How to call them

From SDBasic:

```
call "!FTYPE", result, filename
```

From an I-type expression:

```
SUBR("!FTYPE", DATA.NAME)
```

Arguments are passed by reference to `call`; `SUBR()` passes them by
value. The subroutine sets its output argument and the caller reads it.

## The subroutines

### !FTYPE

```
call "!FTYPE", result, filename
```

Returns the file type of *filename*: `"D"` for a directory file, `"F"`
for a dynamic file. Used by the `FTYPE` I-type in `voc.dic`.

### !PARSER

```
call "!PARSER", result, sentence
```

Parses a TCL sentence into its components. Used internally by the
command processor to break a typed line into verb, file name, selection
clauses, sort keys and output fields.

### !OCONV

```
call "!OCONV", result, value, conversion
```

Applies an output conversion code to a value. The same code as the
`OCONV()` function, callable as a subroutine.

### !ICONV

```
call "!ICONV", result, value, conversion
```

Applies an input conversion code to a value. The same code as the
`ICONV()` function, callable as a subroutine.

### !SORT

```
call "!SORT", result, array, order
```

Sorts a dynamic array. *order* is `"A"` for ascending, `"D"` for
descending. Used by the query processor's `by` and `by.dsnd` clauses.

### !USERNAME

```
call "!USERNAME", result
```

Returns the current user's name. The same value as `@user.name`.

### !ERRTEXT

```
call "!ERRTEXT", result, errno
```

Returns the text of a system error message, given its number. Used by
error-handling routines that need to display or log the message for a
status code.

### !SCREEN

```
call "!SCREEN", result, screen.name, data
```

Drives a screen form. Used by full-screen tools like `sp.view` and
the editors. Not callable from a non-interactive context.

### !PCL

```
call "!PCL", result, data, mode
```

Generates PCL (Printer Control Language) output. Used by the printing
system for printers that expect PCL.

## Subroutines that may not exist

Not every `!`-prefixed name that appears in upstream documentation is
present in SD Core for Windows. If a subroutine has been removed or
was never part of the GPL release, calling it will fail with a
*Subroutine not found* error.

> ***Test before relying on any internal subroutine.*** The safe way to
> discover what is catalogued is `map` in the account or `list.dict` on
> the `gpl.bp` file in `sdsys`. If the name is not there, it is not
> available.

## See also

[SD Dictionaries - Conversions and Formatting](34-sd-dicts-conversions.html) ·
[SD TCL - Programs and the Catalogue](24-sd-tcl-programs-and-the-catalogue.html) ·
[SD Basic - Program Structure](01-sd-basic-program-structure.html).
