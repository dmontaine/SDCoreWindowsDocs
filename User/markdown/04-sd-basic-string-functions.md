Title: SD Basic - String Functions
Subtitle: Measuring, extracting, trimming, replacing, comparing and pattern-matching text.

This page covers the functions that work on a string as text. The functions
that work on a string as a **structure** — fields, values and subvalues held
together by marks — are in [SD Basic - Dynamic Arrays](05-sd-basic-dynamic-arrays.html), and the ones that
convert between internal and external form are in
[SD Basic - Data Conversion](06-sd-basic-data-conversion.html). The line between the three is not always obvious,
so each page points at the others where they meet.

SD folds case, so a program may be written in either case. Keywords are shown
here in lower case. In the tables, *italics* mark something you supply and
**bold** marks a word typed as it stands; braces mark an optional part.

> **Every result on this page was measured, not quoted.** The values shown were
> produced by a program compiled and run on SD Core for Windows W1.0-0.

## Strings, and what counts as a character

Everything in SD is a string. There is no separate character type and no
length declaration — a variable holds as much as you put in it.

***THE MARK CHARACTERS ARE ORDINARY CHARACTERS TO EVERY FUNCTION ON THIS
PAGE.*** `@fm`, `@vm` and `@sm` occupy one byte each and are counted, indexed,
extracted and replaced like any other:

```
len(1 : @vm : 2)      ;* 3 - the two digits and the mark between them
len(@fm)              ;* 1
```

That is convenient when you want it and a trap when you do not. A `len()` used
to size a display field will include the marks; an `index()` searching for a
character may find one inside a mark-delimited structure you did not mean to
look at. Where you want structure rather than text, use the dynamic-array
functions.

Case conversion leaves marks alone: `upcase(@vm)` is still `@vm`.

## Measuring and counting

```
len(string)
count(string, substring)
dcount(string, delimiter)
```

| | |
|---|---|
| `len()` | the number of characters. `len('hello')` is `5`, `len('')` is `0` |
| `count()` | how many times *substring* occurs |
| `dcount()` | how many **fields** *delimiter* divides the string into — normally one more than `count()` |

### Measured

| Expression | Result | |
|---|---|---|
| `count('a,b,c', ',')` | `2` | two delimiters |
| `dcount('a,b,c', ',')` | `3` | three fields |
| `dcount('a,,c', ',')` | `3` | the empty middle field still counts |
| `dcount('a', ',')` | `1` | no delimiter, one field |
| `dcount('', ',')` | **`0`** | ***not 1*** |
| `count('aaaa', 'aa')` | `2` | matches do not overlap |

> ***`dcount()` OF AN EMPTY STRING IS ZERO, NOT ONE.*** Everywhere else an
> empty string behaves like a single empty field, so `for i = 1 to dcount(x,
> @fm)` is the correct idiom precisely **because** it does nothing when `x` is
> empty. Code that assumes at least one field and indexes `field(x, ',', 1)`
> without checking will read an empty value rather than fail.

> **`count()` does not count overlapping matches.** `count('aaaa', 'aa')` is
> `2`, not `3`: once a match is taken, scanning resumes after it. This matters
> when the substring can overlap itself.

*Delimiters may be more than one character* — `dcount('a::b', '::')` is `2`.

## Finding a position

```
index(string, substring, occurrence)
```

Returns the character position at which the *occurrence*-th appearance of
*substring* starts, or `0` if there is no such occurrence. **The occurrence
argument is not optional.**

| Expression | Result |
|---|---|
| `index('banana', 'an', 1)` | `2` |
| `index('banana', 'an', 2)` | `4` |
| `index('banana', 'an', 3)` | `0` — there is no third |
| `index('banana', 'z', 1)` | `0` |
| `index('banana', 'an', 0)` | `0` |

Because a miss and a zeroth occurrence both return `0`, and position `0` is not
a valid position, a simple `if index(...) then` is a safe test for "was it
found".

### `col1()` and `col2()`

```
col1()
col2()
```

After a `field()` call, these give the positions **either side** of the field
that was extracted: `col1()` is the position of the delimiter before it and
`col2()` the position of the delimiter after it.

Measured on `field('alpha,beta,gamma', ',', 2)`, which returns `beta`:

| | |
|---|---|
| `col1()` | `6` — the comma before `beta` |
| `col2()` | `11` — the comma after it |

For the first field `col1()` is `0`, since nothing precedes it. **When the
field is not found, both are `0`** — which is also what they read before any
`field()` has been called, so they cannot distinguish "not found" from "not
asked". Test the result of `field()` itself.

> **`col1()` and `col2()` belong to the running program**, and every called
> program starts with both at zero. A subroutine that calls `field()` changes
> its own pair, not the caller's.

## Extracting part of a string

### By position

The substring operator takes a start and a length:

```
string[start, length]
```

| Expression on `'abcdefgh'` | Result | |
|---|---|---|
| `s[2, 3]` | `bcd` | |
| `s[2, 99]` | `bcdefgh` | a length past the end is not an error |
| `s[9, 2]` | *empty* | a start past the end gives nothing |
| `s[0, 3]` | `abc` | a start below 1 is treated as 1 |
| `s[-3, 2]` | `ab` | so is a negative start |

***THE ONE-ARGUMENT FORM IS THE RIGHTMOST CHARACTERS, NOT THE CHARACTER AT
THAT POSITION.***

```
s[3]        ;* fgh - the last three characters of 'abcdefgh'
```

This reads like an array subscript and is not one. It is the commonest
misreading of SD BASIC by someone arriving from another language.

**The substring form can also be assigned to**, replacing that stretch in
place:

```
z = 'a,b,c'
z[2,1] = 'Z'      ;* z is now 'aZb,c'
```

### By delimiter

```
field(string, delimiter, occurrence {, count})
fieldstore(string, delimiter, start, count, replacement)
```

| | |
|---|---|
| `field()` | returns the *occurrence*-th delimited field. With *count*, returns that many fields **including their delimiters** |
| `fieldstore()` | replaces *count* fields starting at *start*. **A *count* of zero inserts instead of replacing** |

| Expression | Result |
|---|---|
| `field('a,b,c', ',', 2)` | `b` |
| `field('a,b,c', ',', 2, 2)` | `b,c` |
| `field('a,b,c', ',', 9)` | *empty* |
| `fieldstore('a,b,c', ',', 2, 1, 'X')` | `a,X,c` — replaced |
| `fieldstore('a,b,c', ',', 2, 0, 'X')` | `a,X,b,c` — inserted |

An *occurrence* below 1 is treated as 1.

`substrings(array, start, length)` applies the substring operator to **every
element** of a dynamic array: `substrings('abcd' : @vm : 'efgh', 2, 3)` gives
`bcd` and `fgh`.

## Trimming

```
trim(string)
trimb(string)
trimf(string)
trim(string, character {, mode})
```

The one-argument forms work on spaces:

| Expression on `'  a  b  '` | Result |
|---|---|
| `trim()` | `a b` — leading, trailing **and** repeated inner spaces |
| `trimb()` | `  a  b` — trailing only |
| `trimf()` | `a  b  ` — leading only |

The three-argument form works on any character and takes a mode letter. **All
nine were measured on `'xxaxxbxx'` trimming `x`:**

| Mode | Meaning | Result |
|---|---|---|
| **a** | remove every occurrence | `ab` |
| **b** | leading and trailing only | `axxb` |
| **c** | compress repeats, leave the ends | `xaxbx` |
| **d** | as `trim()` — spaces, both ends and compressed inside | — |
| **e** | as `trimb()` — trailing spaces | — |
| **f** | as `trimf()` — leading spaces | — |
| **l** | leading only | `axxbxx` |
| **t** | trailing only | `xxaxxb` |
| **r** | both ends **and** compress repeats inside | `axb` |

**Omitting the mode gives `r`**, not `b`: `trim(t, 'x')` is `axb`. If you only
want the ends stripped, you must say `'b'` — this is the difference between
`a  b` and `a b` on real data and it is easy to miss.

Modes `d`, `e` and `f` ignore the character argument entirely and act on
spaces, so the character you pass with them is never read.

**For every other mode the character must not be empty.** A null second
argument stops the program with *"Null string as second argument to TRIM()"* —
so a `trim(x, sep)` where *sep* came from data needs checking before the call,
not after.

### `crop()`

```
crop(string)
```

Removes **trailing empty fields, values and subvalues** — the debris left by
deleting the last element of a dynamic array. `crop()` of a value list `a`,
`b`, empty, empty gives just `a`, `b`. It does not touch spaces.

## Building strings

```
space(count)
str(string, count)
```

| | |
|---|---|
| `space()` | *count* spaces. `space(0)` is empty |
| `str()` | *string* **repeated** *count* times |

> ***`str()` REPEATS, IT DOES NOT PAD.*** `str('ab', 3)` is `ababab`, six
> characters, not `ab ` padded to three. To pad, concatenate `space()` and take
> a substring, or use `fmt()` — see [SD Basic - Data Conversion](06-sd-basic-data-conversion.html). `str('ab', 0)`
> is empty.

Strings are joined with the `:` operator, and `:=` appends in place:

```
line = 'a' : ',' : 'b'
line := ',c'
```

`cats(array1, array2)` joins two dynamic arrays **element by element** rather
than end to end, and `splice(array1, string, array2)` does the same with a
separator between each pair:

| Expression on `a`,`b` and `1`,`2` | Result |
|---|---|
| `cats(p, q)` | `a1` and `b2` |
| `splice(p, '-', q)` | `a-1` and `b-2` |

## Changing case

```
upcase(string)
downcase(string)
swapcase(string)
```

| Expression on `'aBc1'` | Result |
|---|---|
| `upcase()` | `ABC1` |
| `downcase()` | `abc1` |
| `swapcase()` | `AbC1` |

Digits, punctuation and mark characters are left alone.

> **`fold()` is not a case function.** Despite the name it wraps text into
> lines — see *Wrapping text into lines* below. The case-insensitive
> comparison people reach for `fold` expecting is `compare()` or, for whole
> files, the no-case file option described under [SD Basic - File Handling](07-sd-basic-file-handling.html).

## Replacing

```
change(string, old, new {, count {, start}})
swap(string, old, new {, count {, start}})
substitute(array, old.list, new.list {, delimiter})
convert(from.characters, to.characters, string)
convert from.characters to to.characters in variable
```

***`change()` AND `swap()` ARE THE SAME FUNCTION*** — the compiler emits the
same operation for both. Use whichever reads better; there is no behavioural
difference to choose between.

The fourth and fifth arguments are frequently misread:

| | |
|---|---|
| *count* | **how many occurrences to change**, not which one |
| *start* | which occurrence to start at |

| Expression on `'banana'` | Result | |
|---|---|---|
| `change('banana', 'a', 'X')` | `bXnXnX` | all of them |
| `change('banana', 'a', 'X', 2)` | `bXnXna` | the first **two** |
| `change('banana', 'a', 'X', 1, 2)` | `banXna` | one, starting at the second |
| `change('banana', 'a', '')` | `bnn` | an empty replacement deletes |

### `convert()` works on single characters, and deletes

`convert()` maps each character of *from.characters* to the character in the
same position of *to.characters*.

| Expression | Result | |
|---|---|---|
| `convert('abc', 'xyz', 'aabbcc')` | `xxyyzz` | a → x, b → y, c → z |
| `convert('abc', 'x', 'aabbcc')` | `xx` | ***b and c were deleted*** |

> ***A CHARACTER WITH NO OPPOSITE NUMBER IS REMOVED, NOT LEFT ALONE.*** If the
> two lists are not the same length, every character in the excess of
> *from.characters* is deleted from the string. This is the documented Pick
> behaviour and it is almost never what someone writing
> `convert(',', '', text)` expects to happen to the rest of their data —
> though it is exactly what they want when deleting is the intent.

`convert` also exists as a **statement**, which modifies a variable in place
rather than returning a value:

```
convert ',' to ';' in line
```

### `substitute()`

`substitute(array, old.list, new.list {, delimiter})` replaces whole
**elements** of a dynamic array rather than characters within them, matching
each element against *old.list*. Substituting `b` with `Z` in the values `a`,
`b`, `c` gives `a`, `Z`, `c`.

## Wrapping text into lines

```
fold(string, width {, delimiter})
```

Breaks *string* into lines of at most *width* characters, **breaking at spaces
where it can** and hard-breaking where a single word is too long.

```
fold('the quick brown fox jumps over the lazy dog', 12, '|')
```

gives

```
the quick|brown fox|jumps over|the lazy dog
```

> ***THE TWO-ARGUMENT AND THREE-ARGUMENT FORMS USE DIFFERENT DEFAULT
> SEPARATORS, WHICH IS NOT AN OBVIOUS THING TO GUESS.*** Measured:
>
> | Call | Separator |
> |---|---|
> | `fold(s, 12)` | **field marks** — four fields |
> | `fold(s, 12, '')` | **value marks** — four values |
> | `fold(s, 12, sep)` | whatever *sep* holds — its first character only |
>
> So passing an explicit empty delimiter is **not** the same as omitting it.
> If the mark level matters, give the delimiter explicitly.

**The width may itself be a dynamic array**, giving successive lines different
lengths and reusing the last value once the list runs out:

```
fold(s, 5 : @vm : 20, '|')
```

gives `the|quick brown fox|jumps over the lazy|dog` — a five-character first
line, then twenty. This is how you wrap a paragraph around an indent.

## Comparing and testing

```
compare(string1, string2 {, justification})
alpha(string)
```

`compare()` returns `-1` if *string1* sorts first, `1` if *string2* does, and
`0` if they are equal.

| Expression | Result | |
|---|---|---|
| `compare('abc', 'abd')` | `-1` | |
| `compare('abd', 'abc')` | `1` | |
| `compare('abc', 'abc')` | `0` | |
| `compare('B', 'a')` | `-1` | upper case sorts before lower — byte order |
| `compare('a2', 'a10')` | `1` | plain text order: `2` after `1` |
| `compare('a2', 'a10', 'r')` | `-1` | right-justified: the numbers compare as numbers |

***THE `r` JUSTIFICATION IS HOW YOU SORT `item2` BEFORE `item10`.*** Without
it, embedded numbers compare character by character and `10` sorts before `9`.
`l` is the explicit left-justified form and is the default.

`alpha()` is true if every character is a letter.

| Expression | Result | |
|---|---|---|
| `alpha('abc')` | true | |
| `alpha('ab1')` | false | |
| `alpha('')` | **false** | |

> **`alpha('')` is false and `num('')` is true.** The two tests disagree about
> the empty string, so a validation that uses both needs to say which answer it
> wants for an empty field rather than assuming they behave alike. `num()` is
> covered in [SD Basic - Math Functions](03-sd-basic-math-functions.html).

## Pattern matching

```
string matches pattern
matchfield(string, pattern, element)
```

`matches` is an operator and returns true or false. `matchfield()` returns the
part of the string that matched a given element of the pattern.

### The pattern language

| Element | Matches |
|---|---|
| *n***a** | exactly *n* alphabetic characters |
| *n***n** | exactly *n* digits |
| *n***x** | exactly *n* characters of any kind |
| **0a** · **0n** · **0x** | **any number, including none** |
| *n*`-`*m***a** · *n*`-`*m***n** · *n*`-`*m***x** | between *n* and *m* characters |
| `"literal"` | the quoted text, as it stands |
| `~`*element* | anything the element would **not** match |

Elements are written one after another with no separator.

### Measured

| Test | Result |
|---|---|
| `'abc' matches '3a'` | true |
| `'ab12' matches '2a2n'` | true |
| `'abc' matches '0a'` | true |
| `'' matches '0a'` | true |
| `'ab' matches '3x'` | false |
| `'12' matches '2-4n'` | true |
| `'1' matches '2-4n'` | false |
| `'12345' matches '2-4n'` | false |
| `'abc' matches '~3n'` | true |
| `'123' matches '~3n'` | false |
| `'ab-12' matches '2a"-"2n'` | true |
| `'ab12' matches '0a0n'` | true |
| `'a1b2' matches '0a0n'` | false |

***A PATTERN MAY BE A DYNAMIC ARRAY, AND THE VALUES ARE ALTERNATIVES.***
Measured: `'ab' matches ('2a' : @vm : '2n')` is **true** — the string need only
match one of them. This is how you accept several formats without writing the
test three times:

```
valid = code matches ('3n' : @vm : '2a4n' : @vm : '"X"5n')
```

### Picking out the parts

`matchfield(string, pattern, element)` returns the text that matched the
*element*-th part of the pattern. On `'ab12'` against `'2a2n'`:

| | |
|---|---|
| `matchfield('ab12', '2a2n', 1)` | `ab` |
| `matchfield('ab12', '2a2n', 2)` | `12` |

That makes a pattern a parser as well as a test — validate with `matches`,
then pull the pieces out with `matchfield()` rather than counting character
positions by hand.

## Quoting

```
quote(expr)
dquote(expr)
squote(expr)
```

| | |
|---|---|
| `quote()` · `dquote()` | wrap in double quotes — `"a"` |
| `squote()` | wrap in single quotes — `'a'` |

***`quote()` AND `dquote()` ARE THE SAME FUNCTION*** — the compiler emits the
same operation for both, so there is nothing to choose between them.

For CSV output do not build quoting by hand: `csvdq()` and the CSV statements
handle embedded quotes and separators to RFC 4180, and are covered in
[SD Basic - CSV Files](11-sd-basic-csv-files.html).

## Phonetic matching

```
soundex(string)
```

Returns a four-character code that is the same for words that sound alike, for
finding a name someone has spelled by ear.

| Expression | Result |
|---|---|
| `soundex('Smith')` | `S530` |
| `soundex('Smyth')` | `S530` |
| `soundex('Robert')` | `R163` |
| `soundex('Rupert')` | `R163` |
| `soundex('O Brien 123')` | `O165` — non-letters are ignored |
| `soundex('')` | **`0000`** |

> **`soundex('')` returns `0000`, not an empty string.** A blank name therefore
> gets a code, and every blank name gets the *same* code — so a search keyed on
> soundex will match all of them together unless you exclude empty input
> first.

Soundex is tuned for English and does poorly on names of other origins. It is a
way to narrow a search, not to decide a match.

## Applying a function to every element

Most functions here have a partner ending in `s` that applies the same
operation to every element of a dynamic array. Measured:

| | |
|---|---|
| `lens('one' : @vm : 'three')` | `3` and `5` |
| `counts('a-b' : @vm : 'c-d-e', '-')` | `1` and `2` |
| `fields('a-b' : @vm : 'c-d-e', '-', 1)` | `a` and `c` |
| `trims(' x ' : @vm : '  y  ')` | `x` and `y` |
| `indexs('Ab' : @vm : 'cD', 'b', 1)` | `2` and `0` |
| `soundexs('Smith' : @vm : 'Smyth')` | `S530` and `S530` |
| `spaces(2 : @vm : 3)` | two spaces and three |

The full family, and the rules for how they pair elements when given two
arrays, is in [SD Basic - Dynamic Arrays](05-sd-basic-dynamic-arrays.html).

## What is not here

| | |
|---|---|
| `encrypt()` · `decrypt()` | **removed** — replaced by `sdencrypt()` and `sddecrypt()` |

Nothing else in the string-handling group has been removed. `dparse` and
`dparse.csv` are statements rather than functions and are covered in
[SD Basic - Data Conversion](06-sd-basic-data-conversion.html) and [SD Basic - CSV Files](11-sd-basic-csv-files.html); `iconv()`, `oconv()`,
`fmt()`, `char()`, `seq()`, `ascii()` and `ebcdic()` are in
[SD Basic - Data Conversion](06-sd-basic-data-conversion.html); `extract()`, `insert()`, `delete()`, `replace()`,
`locate`, `remove`, `raise()`, `lower()`, `vslice()` and `dcount()` used
against marks are in [SD Basic - Dynamic Arrays](05-sd-basic-dynamic-arrays.html).

## See also

[SD Basic - Dynamic Arrays](05-sd-basic-dynamic-arrays.html) · [SD Basic - Data Conversion](06-sd-basic-data-conversion.html) ·
[SD Basic - Math Functions](03-sd-basic-math-functions.html) · [SD Basic - CSV Files](11-sd-basic-csv-files.html).
