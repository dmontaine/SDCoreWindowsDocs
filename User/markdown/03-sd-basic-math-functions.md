Title: SD Basic - Math Functions
Subtitle: Arithmetic, rounding, powers, trigonometry, aggregates, bit operations and numeric precision.

This page covers the numeric side of SD BASIC: the arithmetic operators, the
functions that divide and round, powers and logarithms, trigonometry, the
functions that reduce a dynamic array to a number, bit manipulation, and the
control over how many decimal places a number shows when it becomes a string.

SD folds case, so a program may be written in either case. Keywords are shown
here in lower case. Braces mark optional parts of a syntax line; in the tables,
*italics* mark something you supply and **bold** marks a word typed as it
stands.

> **Every result on this page was measured, not quoted.** The values shown were
> produced by a program compiled and run on SD Core for Windows W1.0-0. Where
> this port behaves differently from the older OpenQM and SD documentation, the
> difference is called out rather than left for you to discover.

## Numbers in SD BASIC

SD holds a number as either an **integer** or a **floating-point** value and
moves between them as needed. You do not declare which; an expression that can
stay integral does, and one that cannot becomes floating point.

Everything in SD is ultimately a string, so a variable holding `"12"` is a
number wherever a number is wanted. A string that is not numeric evaluates as
zero in an arithmetic context, and `num()` below is how you test before
relying on that.

### Arithmetic operators

| Operator | Meaning |
|---|---|
| `+` | add |
| `-` | subtract, and unary minus |
| `*` | multiply |
| `/` | divide — the result may be fractional |
| `**` · `^` | raise to a power. The two spellings are the same operator |

There are also compound assignment operators — `+=`, `-=`, `*=`, `/=` and `:=`
for concatenation — so `total += n` is `total = total + n`.

**There is no integer-divide operator.** `/` always divides fully:

```
print 7 / 2        ;* prints 3.5
```

For a whole-number result use `div()`, `idiv()` or `rdiv()`, described below.
`//` is **not** integer division — it is the marker for an unnamed common
block, as in `common // a, b, c`.

### Precedence

Operators lower in this table are applied first. Anything in parentheses is
evaluated before the expression around it.

| | Operators |
|---|---|
| 1 | `**` `^` |
| 2 | `*` `/` |
| 3 | `+` `-` |
| 4 | the `fmt` operator |
| 5 | `:` concatenation |
| 6 | `<` `>` `=` `#` `<=` `>=` `<>` `matches`, and their word forms `lt` `gt` `eq` `ne` `le` `ge` |
| 7 | `and` `&` `or` `!` |

> **`and` and `or` have the same precedence, which is not what most languages
> do.** They are applied left to right as they are met, so `a or b and c` is
> `(a or b) and c` — not `a or (b and c)`. **Parenthesise any condition that
> mixes them.** This has been true since OpenQM and is not a change made by
> this port, but it surprises people arriving from C, Python or SQL, where
> `and` binds tighter.

### Dividing by zero

Dividing by zero stops the program with a runtime error. That can be turned
into a warning that yields zero and carries on:

```
option div.zero.warning
```

The option applies to `/`, `div()`, `idiv()` and `rdiv()` alike.

## Dividing to a whole number

Three functions divide and return an integer, and **they do not round the same
way**. Picking the wrong one is the commonest numeric bug in MultiValue code,
so the differences are set out in full.

### Format

```
div(dividend, divisor)
idiv(dividend, divisor)
rdiv(dividend, divisor)
```

| Function | Rule |
|---|---|
| `div()` | divides and discards the fraction, **always towards zero** |
| `idiv()` | **towards zero when both arguments are integers, downwards when either is floating point** — see the warning below |
| `rdiv()` | divides and rounds to the **nearest** integer, with a half rounded **away from zero** |

### Measured

| Expression | Result | | Expression | Result |
|---|---|---|---|---|
| `div(7, 2)` | `3` | | `rdiv(7, 2)` | `4` |
| `div(-7, 2)` | `-3` | | `rdiv(-7, 2)` | `-4` |
| `div(7, -2)` | `-3` | | `rdiv(7, -2)` | `-4` |
| `div(-7.5, 2)` | `-3` | | `rdiv(5, 2)` | `3` |
| `idiv(7, 2)` | `3` | | `rdiv(-5, 2)` | `-3` |
| `idiv(-7, 2)` | `-3` | | | |

> **`idiv()` changes its rounding when a floating-point number is involved,
> and nothing in the call shows it.** With two integers it truncates towards
> zero; if either argument is floating point it takes the floor, which for a
> negative result is a different number:
>
> ```
> idiv(-7, 2)      ;* -3   both arguments are integers
> idiv(-7.0, 2)    ;* -4   one argument is floating point
> ```
>
> The two differ only for negative results — for positive ones truncation and
> floor agree. **If the sign can be negative, use `div()`**, which truncates
> towards zero whatever the argument types are. This behaviour is inherited
> from OpenQM and has been kept for compatibility; it is not new in this port.

`div()` returns a whole number even when the arguments are fractional:
`div(7.5, 2)` is `3`.

## Remainders

```
mod(dividend, divisor)
rem(dividend, divisor)
```

Both give the remainder of a division and **they differ on the sign**. `mod()`
takes the sign of the *divisor*; `rem()` takes the sign of the *dividend*.

| Expression | `mod` | `rem` |
|---|---|---|
| `(7, 3)` | `1` | `1` |
| `(-7, 3)` | `2` | `-1` |
| `(7, -3)` | `-2` | `1` |
| `(-7, -3)` | `-1` | `-1` |

`mod()` is the mathematical modulus — the result always lies between zero and
the divisor — which is what you want for wrapping a value into a range, such
as an index into a cyclic table. `rem()` is the remainder C and most other
languages give, and is what you want when you are reconstructing a value from
a quotient and a remainder.

> **Neither raises a divide-by-zero error.** A divisor of zero returns the
> dividend unchanged: `mod(7, 0)` and `rem(7, 0)` are both `7`. A loop that
> relies on a remainder shrinking will not terminate if the divisor can reach
> zero, and nothing will tell you.

## Truncation, sign and magnitude

```
int(expr)
abs(expr)
neg(expr)
```

| | |
|---|---|
| `int()` | discards the fractional part, **towards zero**. `int(3.7)` is `3` and `int(-3.7)` is `-3`. It does not round: use `rdiv(n, 1)` or add `0.5` if you want rounding |
| `abs()` | the magnitude, with any sign removed. `abs(-3.5)` is `3.5` |
| `neg()` | the value with its sign reversed. `neg(3)` is `-3` |

> **`int()` is affected by a configuration parameter.** `INTPREC` sets how
> many decimal places are considered before truncating, which stops a value
> that is `2.9999999999` only because of floating-point representation from
> truncating to `2`. It defaults to `13` and may be set from `0` to `14`.
> `config('INTPREC')` reports the value in force, and `config gpl` is not
> where to look — the whole parameter list is shown by the `config` verb.

## Powers, roots and logarithms

```
pwr(base, exponent)
sqrt(expr)
exp(expr)
ln(expr)
```

| | |
|---|---|
| `pwr()` | *base* raised to *exponent*. Identical to the `**` and `^` operators, so `pwr(2, 10)`, `2 ** 10` and `2 ^ 10` all give `1024`. A fractional exponent works: `pwr(2, 0.5)` is `1.4142` |
| `sqrt()` | the square root. `sqrt(2)` is `1.4142` |
| `exp()` | *e* raised to the given power. `exp(1)` is `2.7183` |
| `ln()` | the natural logarithm, base *e*. `ln(10)` is `2.3026` |

**There is no base-10 logarithm function.** Divide by the natural log of ten:
`ln(x) / ln(10)`.

> **`sqrt()` and `ln()` stop the program on a negative argument** — *"SQRT()
> attempted for negative value"* and *"LN() attempted for negative value"*.
> Neither returns an error code you can test, so guard the argument yourself if
> it can go negative.

The four decimal places shown above are not the precision of the calculation —
they are the default precision applied when the number is turned into a string
for printing. See *Controlling how numbers print*.

## Trigonometry

```
sin(expr)     asin(expr)
cos(expr)     acos(expr)
tan(expr)     atan(expr)
```

> **The arguments and results are in degrees, not radians.** This catches
> people out constantly, because almost every other language's maths library
> uses radians. There is no radian variant.

| Expression | Result | | Expression | Result |
|---|---|---|---|---|
| `sin(30)` | `0.5` | | `asin(0.5)` | `30` |
| `cos(60)` | `0.5` | | `acos(0.5)` | `60` |
| `tan(45)` | `1` | | `atan(1)` | `45` |

To work in radians, convert: multiply by `180 / 3.14159265358979` on the way
in, and divide on the way out.

## Random numbers

```
rnd(limit)
randomize {seed}
```

`rnd()` returns a whole number from `0` to *limit* minus one — so `rnd(10)`
gives `0` through `9`, confirmed over 500 draws. A negative *limit* gives a
negative result in the mirrored range: `rnd(-10)` returns `0` down to `-9`.

`randomize` seeds the generator. With a *seed* the sequence repeats identically
every run — measured: `randomize 42` followed by three `rnd(1000)` calls gave
the same three numbers both times — which is what you want for a reproducible
test. With no argument it seeds from the clock, which is what you want in
production.

```
randomize 42
for i = 1 to 5
   print rnd(100)
next i
```

> **This is not a cryptographic random number generator** and must not be used
> to make passwords, tokens or keys. It is the C library's `rand()`, seeded
> from a 32-bit value. For anything security-bearing use `sdencrypt()` and the
> facilities described under *Security* rather than building your own.

## Reducing a dynamic array to a number

These take a dynamic array and give a single value, or a shallower array.

```
sum(array)
summation(array)
maximum(array)
minimum(array)
```

| | |
|---|---|
| `sum()` | adds the elements at the **lowest mark level present** and returns an array one level shallower. Subvalues become values, values become fields |
| `summation()` | adds **every** element at every level and returns one number |
| `maximum()` | the largest numeric element |
| `minimum()` | the smallest numeric element |

### Measured

With `a` holding `1`, `2`, `3` as values, and `b` holding a field of
`10`ˢ`20` and `30`, where ˢ is a subvalue mark:

| Expression | Result |
|---|---|
| `sum(a)` | `6` |
| `sum(b)` | `30` and `30` as two values — the subvalues collapsed, the value did not |
| `summation(b)` | `60` |
| `maximum(a)` | `3` |
| `minimum(a)` | `1` |

> **All four silently skip anything that is not a number.** With `1`, `two`,
> `3` in an array, `sum()` returns `4` and `maximum()` returns `3`. Nothing is
> reported. **If a non-numeric element means your data is wrong, you have to
> test for it yourself** — walk the array with `num()` before summing.
>
> `maximum()` and `minimum()` return the **null string**, not zero, when there
> is no numeric element at all. Test for that with `if result = '' then`,
> because a numeric test would read the null string as zero and cannot tell it
> from a genuine maximum of zero.

While developing, `option non.numeric.warning` makes SD report a non-numeric
value used where a number was expected, which turns a class of silent wrong
answers into something you can see. It is off by default. `option` on its own
lists every option and its current state; `option all off` clears them.

Negative values are handled correctly: `maximum()` of `-5` and `-3` is `-3`.

### Comparing two values

```
max(expr1, expr2)
min(expr1, expr2)
```

These take **two values, not an array**, and return the larger or smaller.
Unlike the four above they are not restricted to numbers: they use SD's general
comparison, so `max('abc', 'abd')` returns `abd`. `max(3, 7)` returns `7`.

## Testing whether a value is a number

```
num(expr)
```

Returns true if *expr* would be accepted as a number, false otherwise.

### What it accepts, measured

| Expression | Result | |
|---|---|---|
| `num('12')` | true | |
| `num('12.5')` | true | |
| `num('.5')` | true | a leading decimal point is fine |
| `num('+3')` | true | a leading sign is fine |
| `num('')` | **true** | **the null string is numeric** |
| `num(' 12')` | false | no leading space |
| `num('12 ')` | false | no trailing space |
| `num('3-')` | false | a trailing sign is not accepted |
| `num('1e3')` | false | no exponent notation |
| `num('123456789012345')` | true | 15 digits before the point |
| `num('1234567890123456')` | false | 16 is too many |

> **`num('')` is true, and it is the single most common source of a wrong
> answer from this function.** An empty field passes the test and then
> evaluates as zero, so a validation written as `if num(value) then ...`
> accepts a blank. **Test for the null string first:**
>
> ```
> if value # '' and num(value) then
>    ...
> end
> ```
>
> The rule is consistent with the rest of SD, where an empty value is zero in
> a numeric context — but the function reads like a validator and is not one.

`nums()` applies the same test to every element of a dynamic array. See
[SD Basic - Dynamic Arrays](05-sd-basic-dynamic-arrays.html) for the whole family of `s` functions.

## Bit operations

These work on **32-bit signed integers**. A value outside that range is
truncated to fit.

```
bitand(expr1, expr2)      bitset(expr, bit)
bitor(expr1, expr2)       bitreset(expr, bit)
bitxor(expr1, expr2)      bittest(expr, bit)
bitnot(expr)              shift(expr, distance)
```

| | |
|---|---|
| `bitand()` | bitwise AND. `bitand(12, 10)` is `8` |
| `bitor()` | bitwise OR. `bitor(12, 10)` is `14` |
| `bitxor()` | bitwise exclusive OR. `bitxor(12, 10)` is `6` |
| `bitnot()` | bitwise NOT — every bit inverted. `bitnot(0)` is `-1` |
| `bitset()` | returns *expr* with the given bit set. `bitset(0, 3)` is `8` |
| `bitreset()` | returns *expr* with the given bit cleared. `bitreset(15, 0)` is `14` |
| `bittest()` | true if the given bit is set. `bittest(8, 3)` is true, `bittest(8, 2)` is false |
| `shift()` | shifts the bits. **A negative distance shifts left, a positive distance shifts right** |

**Bits are numbered from zero, and zero is the least significant bit.** So
bit 3 has the value 8, and bit 31 is the sign bit. **There is no range check on
the bit number** — a value outside 0 to 31 gives an unpredictable result rather
than an error, so validate it yourself if it is calculated.

> **`shift()`'s direction is the reverse of what the name suggests, and its
> right shift does not preserve the sign.** `shift(1, -4)` is `16` — shifted
> left. `shift(256, 4)` is `16` — shifted right. And `shift(-1, 1)` is
> `2147483647`, not `-1`: the value is treated as unsigned, so a right shift
> brings in zeros rather than copying the sign bit. **Do not use `shift()` to
> divide a signed number by a power of two** — use `div()`.

## Checksums

```
checksum(expr)
```

Returns a 32-bit integer derived from the bytes of *expr*. It is cheap and it
changes when the data changes — `checksum('hello')` is `1199` and
`checksum('hellp')` is `1200` — which makes it useful for spotting that a
record has been altered since you last read it.

> **It is not a cryptographic hash and must not be used as one.** It is a
> rotate-and-exclusive-or over the bytes, and it is straightforward to
> construct a different string with the same result. It will not detect
> deliberate tampering, and it must never be used to store or compare a
> password. `checksum('')` is `0`, so an empty value and a failed read are
> indistinguishable by checksum alone.

For real cryptography this port provides `sdencrypt()` and `sddecrypt()`. The
older `encrypt()` and `decrypt()` functions **have been removed** and programs
using them will not compile.

## Controlling how numbers print

```
precision n
```

Sets how many decimal places are used when a floating-point number is converted
to a string — by `print`, by concatenation, by writing to a file. It does not
change the accuracy of the arithmetic itself, only what you see and what gets
stored.

**The default is 4.** *n* may be 0 to 14; a value outside that range is pulled
to the nearest end rather than refused.

| | |
|---|---|
| `1 / 3` at the default | `0.3333` |
| `1 / 3` after `precision 8` | `0.33333333` |
| `1 / 3` after `precision 0` | `0` |
| `1 / 3` after `precision 20` | `0.33333333333333` — clamped to 14, not refused |

> **Precision is per program and it does not travel with a call.** Every
> program starts at 4, including one you `call`, and setting it in a caller has
> no effect inside the subroutine. It is restored to the caller's value when the
> subroutine returns. **A subroutine that formats numbers must set its own
> `precision`** — a common cause of a report where the totals show four decimal
> places and the line items show something else.

Where you need a specific layout rather than a number of decimals, use `fmt()`
and the output conversion codes instead; they are covered in
[SD Basic - Data Conversion](06-sd-basic-data-conversion.html).

### Comparing floating-point numbers

Two floating-point values are treated as equal if they differ by less than the
`FLTDIFF` configuration parameter, which defaults to a very small number
(`0.0000000000291`).

**This is why `0.1 + 0.2 = 0.3` is true in SD BASIC** — measured — where the
same test is false in C, Java, Python and JavaScript. It is a deliberate
convenience and not an accident of this port. `config('FLTDIFF')` reports the
value in force.

**It also means two values that differ in the fourteenth decimal place compare
as equal**, so a comparison is not a safe way to detect a tiny drift. If you
need to know that two numbers really are bit-identical, compare their string
forms after `precision 14`.

## Applying a function to every element

Several of the functions above have a partner ending in `s` that applies the
same operation to every element of a dynamic array instead of to a single
value: `abss()`, `negs()`, `mods()`, `nums()`.

```
abss(-1 : @vm : 2 : @vm : -3)     ;* gives 1, 2, 3 as three values
```

The whole family — including the string and comparison members — is described
in [SD Basic - Dynamic Arrays](05-sd-basic-dynamic-arrays.html).

## What is not here

These existed in OpenQM and in earlier SD releases and **are not in SD Core for
Windows**. A program using one will not compile.

| | |
|---|---|
| `encrypt()` · `decrypt()` | replaced by `sdencrypt()` and `sddecrypt()` |

Nothing else in the mathematical and logical group has been removed: every
function the OpenQM 2.6.6 documentation lists under that heading is present in
this port, and this page covers the numeric ones. The comparison and logical
members of the group — `ands()`, `ors()`, `nots()`, `eqs()`, `nes()`, `gts()`,
`ges()`, `lts()`, `les()`, `ifs()`, `not()`, `reuse()` — are documented in
[SD Basic - Dynamic Arrays](05-sd-basic-dynamic-arrays.html), where their multivalue behaviour is the point.

## See also

[SD Basic - Dynamic Arrays](05-sd-basic-dynamic-arrays.html) · [SD Basic - Data Conversion](06-sd-basic-data-conversion.html) ·
[SD Basic - String Functions](04-sd-basic-string-functions.html) · the `config` verb, for `INTPREC` and `FLTDIFF`.
