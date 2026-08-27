Title: SD Basic - Dynamic Arrays
Subtitle: Fields, values and subvalues - reading, changing, searching and walking the structure that holds every SD record.

A dynamic array is a string with structure in it. Three mark characters divide
it into **fields**, **values** and **subvalues**, and every record SD reads or
writes is one. This page covers the statements and functions that work on that
structure.

The functions that treat the same string as plain text are in
[SD Basic - String Functions](04-sd-basic-string-functions.html); the two pages overlap where a function is used
both ways, and each says so.

SD folds case, so a program may be written in either case. Keywords are shown
here in lower case. In the tables, *italics* mark something you supply and
**bold** marks a word typed as it stands; braces mark an optional part.

> **Every result on this page was measured, not quoted.** The values shown were
> produced by a program compiled and run on SD Core for Windows W1.0-0. In the
> examples below, `^` stands for a field mark, `|` for a value mark and `\` for
> a subvalue mark.

## The marks

| | Name | Constant | Code |
|---|---|---|---|
| ^ | field mark | `@fm` | 254 |
| \| | value mark | `@vm` | 253 |
| \\ | subvalue mark | `@sm` | 252 |

They nest: a field contains values, a value contains subvalues. There is a
fourth, `@tm` (text mark, 251), used by `fmt()` and by some conversions, and
`@im` (item mark, 255), which SD uses internally.

```
a = 'f1' : @fm : 'v1' : @vm : 'v2' : @fm : 'f3'
```

gives `f1^v1|v2^f3` — three fields, the second of which holds two values.

***THE MARKS ARE ORDINARY CHARACTERS AND THEY ARE COUNTED.*** Measured:
`len(a)` is `11` for the array above — eight data characters and three marks.
Everything in [SD Basic - String Functions](04-sd-basic-string-functions.html) sees them.

```
dcount(string, delimiter)
```

counts the pieces a delimiter divides a string into. Measured on the array
above: `dcount(a, @fm)` is `3`, and `dcount(a<2>, @vm)` is `2`.

> **`dcount()` of an empty string is `0`, not `1`.** That is what makes
> `for i = 1 to dcount(rec, @fm)` correct — an empty record does nothing.

## Reading a piece

```
array<field {, value {, subvalue}}>
extract(array, field {, value {, subvalue}})
```

The angle-bracket form and `extract()` are the same operation.

| Expression on `f1^v1\|v2^f3` | Result |
|---|---|
| `a<2>` | `v1\|v2` — the whole field, marks and all |
| `a<2,2>` | `v2` |
| `a<2,1,1>` | `v1` |
| `extract(a, 2, 1)` | `v1` |
| `a<9>` | *empty* |

***READING PAST THE END IS NOT AN ERROR.*** `a<9>` on a three-field array
returns the null string, exactly as a genuinely empty field would. **There is
no way to tell "field 9 is empty" from "there is no field 9"** — use
`dcount()` if the difference matters.

Asking for a value of a field that has none returns the whole field: `a<1,1>`
is `f1`.

## Changing a piece

```
array<field {, value {, subvalue}}> = expression
replace(array, field, value, subvalue, expression)
insert(array, field, value, subvalue, expression)
delete(array, field {, value {, subvalue}})
```

| Expression on `f1^v1\|v2^f3` | Result |
|---|---|
| `b<2,2> = 'NEW'` | `f1^v1\|NEW^f3` |
| `replace(a, 2, 2, 0, 'R')` | `f1^v1\|R^f3` |
| `insert(a, 2, 2, 0, 'I')` | `f1^v1\|I\|v2^f3` — pushes the rest along |
| `delete(a, 2, 1)` | `f1^v2^f3` — removes one value |
| `delete(a, 2)` | `f1^f3` — removes the whole field |

The assignment form is what almost all code uses. `replace()` and `insert()`
exist for when you need the result as an expression rather than assigned back.

> ***`replace()` AND `insert()` COUNT THEIR ARGUMENTS GREEDILY, AND THE SHORT
> FORMS NEED A SEMICOLON.*** `replace(a, 2, 2, 'R')` **does not compile** — the
> parser takes `2` as the value, `'R'` as the subvalue, and then demands the
> replacement string it never got. Either give all five arguments, or separate
> the final one with a semicolon. Measured:
>
> | Call | Result |
> |---|---|
> | `replace(a, 2, 2, 0, 'R')` | `f1^v1\|R^f3` |
> | `replace(a, 2; 'S')` | `f1^S^f3` — replaces the whole field |
> | `replace(a, 2, 2; 'T')` | `f1^v1\|T^f3` |
> | `replace(a, 2, 2, 'R')` | **compile error** |

### Appending

A subscript of `-1` appends:

| | Result |
|---|---|
| `b<-1> = 'APP'` | `f1^v1\|v2^f3^APP` — a new field at the end |
| `b<2,-1> = 'AV'` | `f1^v1\|v2\|AV^f3` — a new value in field 2 |

***WRITING PAST THE END PADS WITH EMPTY FIELDS RATHER THAN FAILING.***
Measured: `insert(a, 9, 0, 0, 'FAR')` on a three-field array gives
`f1^v1|v2^f3^^^^^^FAR` — five empty fields appear to fill the gap. A loop with
an off-by-one index therefore grows the record silently instead of raising
anything.

### The statement forms

```
del array<field {, value {, subvalue}}>
ins string before array<field {, value {, subvalue}}>
```

`del` and `ins` change the variable in place. Measured: `del b<2>` gives
`f1^f3`, and `ins 'X' before b<2>` gives `f1^X^v1|v2^f3`.

## Searching

### `locate`

```
locate expression in array<field {, value {, subvalue}}> {by order} setting variable
   then statements
else statements

locate(expression, array, field {, value {, subvalue}})
```

`locate` finds a whole element and reports its position. When it does not find
one, `setting` receives **the position where it would be inserted** to keep the
order — which is what makes it the standard way to add to a sorted list.

***THE NUMBER OF SUBSCRIPTS CHOOSES THE LEVEL SEARCHED. THIS IS THE THING
PEOPLE GET WRONG.*** Measured, with `vals` holding `apple|cherry|damson` as
three values in one field:

| Statement | Result |
|---|---|
| `locate 'cherry' in vals<1> setting p` | **miss**, insert at 2 |
| `locate 'cherry' in vals<1,1> setting p` | **found at 2** |

`array<f>` searches the **fields**, starting at field *f*. `array<f,v>`
searches the **values of field f**, starting at value *v*. `array<f,v,s>`
searches subvalues. So a single subscript on an array of values finds nothing,
silently, and reports an insertion point — which looks like a working search
right up until the data has two fields.

**The statement form requires the angle brackets.** `locate 'x' in vals setting
p` does not compile: *"Field reference not found where expected"*.

The starting subscript really does start there. Measured: with
`vals<1,2>`, `locate 'apple'` — which is value 1 — **misses**, and reports an
insertion point of 4.

The function form takes the position as arguments instead, and returns the
position or zero:

| Call | Result |
|---|---|
| `locate('cherry', vals, 1)` | `0` — searched fields |
| `locate('cherry', vals, 1, 1)` | `2` — searched values |
| `locate('zebra', vals, 1, 1)` | `0` |

### Order codes

Without `by`, `locate` scans the whole list and the insertion point is the end.
With `by`, it assumes the list is already sorted that way, stops as soon as it
passes the place the value would go, and reports that place.

| Code | Order |
|---|---|
| **al** | ascending, left-justified — ordinary text order |
| **ar** | ascending, right-justified — numbers compare as numbers |
| **dl** | descending, left-justified |
| **dr** | descending, right-justified |

Measured on `apple|cherry|damson`:

| Search | Insert at |
|---|---|
| `'aardvark' by 'al'` | `1` |
| `'banana' by 'al'` | `2` |
| `'zebra' by 'al'` | `4` |

***AND THE JUSTIFICATION IS NOT A DETAIL.*** Measured on the values `2`, `10`,
`30`, looking for `9`:

| | Insert at |
|---|---|
| `by 'al'` | **4** — as text, `9` sorts after `30` |
| `by 'ar'` | **2** — as numbers, between `2` and `10` |

**Use `ar` for anything numeric.** `al` on numbers produces a list that looks
sorted in short test data and comes apart at ten items.

`by` on a list that is *not* actually sorted that way stops early and reports a
miss for a value that is present.

### `find` and `findstr`

```
find string in array {, occurrence} setting field {, value {, subvalue}}
findstr string in array {, occurrence} setting field {, value {, subvalue}}
```

`find` matches a **whole element**; `findstr` matches **any element containing
the string**. Both report the position as separate field, value and subvalue
numbers rather than one index.

Measured on `p^q|r`:

| | Result |
|---|---|
| `find 'r' in d setting f, v, s` | field 2, value 2, subvalue 1 |
| `findstr 'q' in d setting f, v` | field 2, value 1 |

## Walking an array

```
remove variable from array setting delimiter
```

`remove` takes the next element off the front of *array* and reports which mark
followed it. It is much faster than repeated `extract()` on a long record,
because it does not rescan from the start each time.

***THE DELIMITER CODE IS THE MARK'S LEVEL, AND ZERO MEANS THE END.*** Measured
on `p^q|r\s`:

| Code | Meaning |
|---|---|
| `0` | end of the string — this was the last element |
| `2` | a field mark followed |
| `3` | a value mark followed |
| `4` | a subvalue mark followed |

```
s = record
loop
   remove element from s setting mark
   ...
while mark
repeat
```

***`remove` CONSUMES THE VARIABLE IT READS.*** Work on a copy — `s = record` —
or the record is gone by the end of the loop. The functions that follow depend
on an internal pointer into that variable:

| | |
|---|---|
| `getrem(string)` | how far through the string the pointer has reached |
| `setrem offset on string` | move the pointer |

Measured: after one `remove` from `aaa^bbb`, `getrem()` is `4`.

**Changing the string resets the pointer.** A loop that both `remove`s from a
string and assigns to it will restart from the beginning, silently.

## Changing the mark level

```
raise(string)
lower(string)
```

`raise` promotes every mark one level — subvalues become values, values become
fields. `lower` demotes them. Measured: `lower('x' : @fm : 'y')` has one field
and two values; `raise('x' : @vm : 'y')` has two fields.

These are how you move a nested structure between levels without walking it —
for example turning a multivalued field into a record.

## Working across an array

### `vslice`

```
vslice(array, value.number)
```

Takes the *n*-th value of **every** field and returns them as fields. Measured
on `a1|a2^b1|b2`: `vslice(h, 2)` gives `a2^b2`.

That is the idiom for pulling one column out of a set of associated multivalued
fields.

### `substrings`, `fieldstore` and `splice`

| | |
|---|---|
| `substrings(array, start, length)` | the substring operator applied to every element |
| `fieldstore(string, delimiter, start, count, replacement)` | replace or insert delimited fields — a *count* of zero inserts |
| `splice(array1, string, array2)` | joins the arrays element by element with *string* between |

Measured: `splice('a' : @vm : 'b', '-', '1' : @vm : '2')` gives `a-1|b-2`.

### `substitute`

```
substitute(array, old.list, new.list {, delimiter})
```

Replaces whole **elements** that match. Measured: substituting `b` with `Z` in
the values `a`, `b`, `c` gives `a|Z|c`.

### `reuse`

```
reuse(expression)
```

Makes a single value behave as though it repeated for every element of the
other operand. ***WITHOUT IT, ARITHMETIC ONLY REACHES THE FIRST ELEMENT.***
Measured:

| Expression | Result |
|---|---|
| `(1\|2\|3) + 10` | `11\|2\|3` |
| `(1\|2\|3) + reuse(10)` | `11\|12\|13` |

The first line is almost never what was intended, and it produces a plausible
number rather than an error.

## The `s` functions

Most string and arithmetic functions have a partner ending in `s` that applies
the operation to every element instead of to the whole string:
`abss()`, `negs()`, `mods()`, `nums()`, `lens()`, `counts()`, `fields()`,
`trims()`, `trimbs()`, `trimfs()`, `indexs()`, `soundexs()`, `spaces()`,
`strs()`, `fmts()`, `iconvs()`, `oconvs()`, `folds()`, `cats()`.

***WHEN TWO ARRAYS ARE DIFFERENT LENGTHS, THE SHORTER IS TREATED AS EMPTY, NOT
TRUNCATED.*** Measured with `1|2|3` and `10|20`:

| Call | Result | |
|---|---|---|
| `cats(p, q)` | `110\|220\|3` | the third pairs with nothing |
| `mods(p, q)` | `1\|2\|3` | `mod(3, 0)` is `3` — no error |

So a mismatch produces a full-length answer with quietly wrong elements in the
tail. **Compare `dcount()` on both operands before relying on the result.**

## Logical functions

These take true/false values element by element. In SD, zero and the null
string are false and anything else is true.

| | |
|---|---|
| `not(expression)` | logical negation of a single value |
| `nots(array)` | of every element |
| `ands(a, b)` · `ors(a, b)` | element-by-element AND and OR |
| `eqs` · `nes` · `gts` · `ges` · `lts` · `les` | element-by-element comparison, giving 1 or 0 |
| `ifs(control, true.values, false.values)` | picks from one array or the other per element |

Measured:

| Call | Result |
|---|---|
| `not(0)`, `not(1)`, `not('')` | `1`, `0`, `1` |
| `nots(1\|0\|'')` | `0\|1\|1` |
| `ands(1\|0\|1, 1\|1\|0)` | `1\|0\|0` |
| `ors(1\|0\|0, 0\|1\|0)` | `1\|1\|0` |
| `eqs(1\|2\|3, 1\|20\|3)` | `1\|0\|1` |
| `ifs(1\|0, 'yes'\|'yes', 'no'\|'no')` | `yes\|no` |

## Sorting

```
sortinit {order}
sortadd key, data
sortclear
```

`sortinit` starts a sort, `sortadd` feeds it a key and a record, and reading it
back drains it. The order codes are the same `al` / `ar` / `dl` / `dr` as
`locate`. For sorting a whole file, `sselect` is faster — see
[SD Basic - Select Lists](08-sd-basic-select-lists.html).

## Mark mapping

```
mark.mapping file.variable, on | off | expression
```

Controls whether SD translates mark characters when reading and writing a
**directory** file, whose records are ordinary operating-system files. With
mapping on, field marks become newlines on the way out and back again on the
way in; with it off, the bytes pass through unchanged.

**It has no effect on a dynamic file**, where records are stored in SD's own
format.

## What is not here

Nothing in the dynamic-array group has been removed from this port.

`dcount()`, `fieldstore()`, `substrings()`, `splice()`, `substitute()` and the
whole `s` family are also described in [SD Basic - String Functions](04-sd-basic-string-functions.html), where they
are used on text rather than on structure.

## See also

[SD Basic - String Functions](04-sd-basic-string-functions.html) · [SD Basic - File Handling](07-sd-basic-file-handling.html) ·
[SD Basic - Select Lists](08-sd-basic-select-lists.html) · [SD Basic - Math Functions](03-sd-basic-math-functions.html).
