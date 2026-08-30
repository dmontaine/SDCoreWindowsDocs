Title: SD Programming 101
Subtitle: A tutorial with worked example programs - from hello world to a small application that ties everything together.

This page is a tutorial. The rest of the `User` set is reference: each
page covers one subject and every statement on it. Here we put them
together into programs that do something, and each program builds on
the one before.

***Every program on this page compiles and runs on SD Core for Windows
W1.0-0.*** The output shown is what SD printed. If you type the program
in, compile it and run it, you will see the same thing.

The reference pages are linked at the end of each section. Read them
when you want the full story on a statement or function — this page
shows what you need to make the programs work and no more.

*Italics* mark something you supply, **bold** a word typed as it stands,
and braces an optional part.

## Before you start

You need an SD session and a `bp` file. If you have signed in and
created a file called `customers` as the Introduction suggests, you
already have `bp` — every account gets one.

```
sd
```

You land at the `:` prompt. That is TCL — the command processor. From
here you compile, catalogue and run programs. The programs themselves
are written in SDBasic, which is a different language from TCL.

Your `bp` file is an ordinary Windows folder. You can write programs
in `ed` from inside SD, in `edit` or `micro` if your account can run
external programs, or in any text editor you like — Notepad, VS Code,
anything. The folder is on disk at:

```
C:\ProgramData\SD\user_accounts\<account>\bp
```

## 1. Hello world

The smallest program:

```
program hello
   print 'hello, world'
end
```

Type it into `ed` — `ed bp hello`, `i`, type the three lines, a full
stop on its own line to stop inserting, `fi` to file and exit. Or save
it as `hello` in the `bp` folder with a text editor.

Compile and run it:

```
basic bp hello
run bp hello
```

```
hello, world
```

Every program starts with a declaration — `program` here — and ends
with `end`. Between them are statements. `print` sends a line to the
terminal. The string is in single quotes; double quotes work too, but
single quotes are what the rest of the documentation uses and what SD's
own source uses.

> ***`program` IS OPTIONAL.*** A source record with no declaration is a
> program. But every program on this page has one, because naming the
> program is how you know what it is when it is catalogued and called
> from another program.

## 2. Variables and input

A program that asks your name and says hello back:

```
program hello2
   print 'what is your name?' :
   input name
   print 'hello, ' : name
end
```

```
basic bp hello2
run bp hello2
```

```
what is your name? dave
hello, dave
```

`input` reads a line from the terminal into the variable `name`. The
colon at the end of the first `print` stops it printing a newline, so
the question mark is on the same line as the answer.

Variables are not declared. A variable that has never been assigned is
an **unassigned variable** — reading it is an error, not an empty
string. This is deliberate: it catches typos.

The colon `:` in a `print` statement is the concatenation operator for
output. It does not add spaces — it joins the pieces with nothing
between them. To put a space between *hello,* and the name, the string
itself carries the space: `'hello, '`.

## 3. Variables and arithmetic

SDBasic variables are **type variant** — a variable holds whatever
type the last assignment gave it, and the type can change from one
line to the next. A variable that held a string can be used in
arithmetic on the next line: the value is converted to numeric form
for the calculation without changing the variable itself.

Numeric values are held as **integers wherever possible**. Conversion
to floating point occurs when a result is non-integer or too large to
store as an integer. This is invisible — you do not declare a variable
as integer or real.

```
program maths
   print 'first number?' :
   input a
   print 'second number?' :
   input b
   print 'sum      = ' : a + b
   print 'product  = ' : a * b
   print 'quotient = ' : a / b
   print 'remainder= ' : mod(a, b)
end
```

```
run bp maths
```

```
first number? 17
second number? 5
sum      = 22
product  = 85
quotient = 3.4
remainder= 2
```

`mod()` is a function, not a statement — it is called inside an
expression and returns a value. SDBasic has a full set of math
functions: `abs`, `int`, `sqrt`, `sin`, `cos`, `tan`, `ln`, `exp`,
`pwr`, and more. The full list is in [SD Basic - Math Functions](03-sd-basic-math-functions.html).

> ***THE REDUNDANT-LOOKING TYPE-FORCING IDIOM.*** Because conversion
> happens on use, not on assignment, a string of digits used in a tight
> loop converts on every iteration. SDBasic programs often contain
> apparently redundant statements that force the conversion once:
>
> ```
> a = a + 0        ;* Convert to numeric form
> s = s : ""       ;* Convert to string form
> ```
>
> The first makes `a` numeric so the next arithmetic use does not
> convert again; the second makes `s` a string. Neither changes the
> value — they change how it is held.

## 4. A program that reads a file

This is where SDBasic starts to earn its keep. The `customers` file
from the Introduction holds records. Each record is a dynamic array —
a string with field marks in it. Reading a record gives you the whole
string; extracting a field gives you one piece of it.

```
program show.customer
   open 'customers' to f.cust else
      print 'cannot open customers'
      stop
   end

   print 'customer id?' :
   input id

   read rec from f.cust, id then
      print 'name  : ' : rec<1>
      print 'phone : ' : rec<2>
      print 'city  : ' : rec<3>
   end else
      print 'no such customer'
   end
end
```

```
run bp show.customer
```

```
customer id? 1001
name  : Acme Supplies
phone : 555-1234
city  : Springfield
```

### What just happened

`open` looks up `customers` in the VOC and gives you a file variable.
The `else` branch fires if the file does not exist — and **it is
compulsory**. A program that omits the `else` does not compile.

`read` fetches the whole record by id. The `then` branch fires if the
record exists; the `else` branch fires if it does not.

`rec<1>` is **field extraction** — the angle brackets are the
shorthand for `extract(rec, 1, 0, 0)`. Field 1, field 2, field 3.
Dynamic arrays are covered in [SD Basic - Dynamic Arrays](05-sd-basic-dynamic-arrays.html).

## 5. A program that writes

```
program add.customer
   open 'customers' to f.cust else
      print 'cannot open customers'
      stop
   end

   print 'new customer id?' :
   input id

   print 'name?' :
   input name
   print 'phone?' :
   input phone
   print 'city?' :
   input city

   rec = name : @fm : phone : @fm : city
   write rec on f.cust, id
   print 'saved'
end
```

```
run bp add.customer
```

```
new customer id? 1002
name? Widget Corp
phone? 555-5678
city? Shelbyville
saved
```

`@fm` is the **field mark constant** — character 254. Building a
record is joining fields with it. `write` stores the whole record;
the old record, if any, is replaced.

### The marks

Three mark characters divide a dynamic array:

| | Name | Constant | Code |
|---|---|---|---|
| field mark | `@fm` | 254 |
| value mark | `@vm` | 253 |
| subvalue mark | `@sm` | 252 |

A field contains values; a value contains subvalues. `rec<1>` gets
the first field; `rec<1,2>` gets the second value in the first field;
`rec<1,2,1>` gets the first subvalue in that value.

## 6. A program with a select list

Reading one record by id is useful. Reading every record in a file is
how you produce reports. A select list is the mechanism:

```
program list.customers
   open 'customers' to f.cust else
      print 'cannot open customers'
      stop
   end

   select f.cust to 1
   print 'id' : ' ' : 'name' : ' ' : 'city'
   print '---' : ' ' : '----' : ' ' : '----'

   loop while readnext(id) from 1 do
      read rec from f.cust, id then
         print id : ' ' : rec<1> : ' ' : rec<3>
      end
   repeat

   clearselect 1
end
```

```
run bp list.customers
```

```
id name city
--- ---- ----
1001 Acme Supplies Springfield
1002 Widget Corp Shelbyville
```

`select` builds a list of every record id in the file. `readnext`
reads one id at a time from the list. The `loop while readnext(id)
from 1 do ... repeat` is the standard pattern for walking a select
list — it ends when `readnext` has nothing left.

`clearselect 1` clears list 1 when the program is done. A select list
is **session state**: it survives the program that made it. Clearing
it is good manners.

## 7. A subroutine

A subroutine is a separate program, called by name, that takes
arguments and returns values through them. You write it as its own
source record and compile it:

```
program get.field
   subroutine get.field(result, file.var, id, field.no)
   read rec from file.var, id then
      result = rec<field.no>
   end else
      result = ''
   end
end
```

```
basic bp get.field
```

Notice: a subroutine starts with `subroutine` where a program starts
with `program`. It does not `run` — you call it from another program.

```
program test.get.field
   open 'customers' to f.cust else stop 'no file'
   call get.field(name, f.cust, '1001', 1)
   print 'name is ' : name

   call get.field(phone, f.cust, '1001', 2)
   print 'phone is ' : phone
end
```

```
basic bp test.get.field
run bp test.get.field
```

```
name is Acme Supplies
phone is 555-1234
```

`call` runs the subroutine. Arguments are passed **by reference**: the
subroutine sets `result` and the caller sees it in `name`. This is
how subroutines return values — there is no `return value` statement
for subroutines.

A subroutine must be compiled before the program that calls it. If
`get.field` is not compiled, the calling program gets *Subroutine not
found* at run time, not at compile time.

## 8. A function

A function is like a subroutine, but it returns a value in an
expression rather than through an argument:

```
program fmt.phone
   function fmt.phone(number)
      if len(number) = 7 then
         fmt.phone = number[1,3] : '-' : number[4,3]
      end else
         fmt.phone = number
      end
end
```

```
basic bp fmt.phone
```

A function assigns its return value to **its own name**. That is the
`fmt.phone = ...` line — it is not a variable called `fmt.phone`, it
is the function saying what to return.

```
program test.fmt.phone
   open 'customers' to f.cust else stop 'no file'
   read rec from f.cust, '1001' then
      raw = rec<2>
      print 'raw    : ' : raw
      print 'formatted: ' : fmt.phone(raw)
   end
end
```

```
basic bp test.fmt.phone
run bp test.fmt.phone
```

```
raw    : 5551234
formatted: 555-1234
```

`number[1,3]` is a **substring**: start at position 1, take 3
characters. `number[4,3]` starts at position 4 and takes 3 more. The
square brackets are the shorthand for the `substr()` function.

## 9. Error handling

File operations can fail. The `on error` clause catches failures that
are not about the record being missing — disk full, file locked by
another session, network error:

```
program safe.write
   open 'customers' to f.cust else stop 'no file'

   print 'id?' :
   input id
   print 'name?' :
   input name

   rec = name : @fm : '' : @fm : ''

   write rec on f.cust, id on error
      print 'write failed: ' : @system.error.text
      stop
   end
   print 'saved'
end
```

```
basic bp safe.write
run bp safe.write
```

```
id? 1003
name? Test Co
saved
```

The `on error` clause fires when the write fails for a system reason.
The `then`/`else` on `write` is about the record — but `write` has no
`then`/`else`, because writing always succeeds unless something is
broken. The `on error` is where that broken-something arrives.

`@system.error.text` is a system variable that holds the last error
message. It is the same one the API's `SDError()` returns.

## 10. Putting it together: a small application

This program ties everything together. It is a menu-driven customer
manager: list, add, view and delete. It uses subroutines, select
lists, file I/O, error handling, and a loop.

```
program customer.manager
   open 'customers' to f.cust else
      print 'cannot open customers - create it first'
      stop
   end

   loop
      print
      print 'l)ist  a)dd  v)iew  d)elete  q)uit'
      print 'choice?' :
      input choice

      begin case
         case choice = 'l'
            gosub list.all

         case choice = 'a'
            gosub add.one

         case choice = 'v'
            gosub view.one

         case choice = 'd'
            gosub delete.one

         case choice = 'q'
            exit

         case 1
            print 'not a choice'
      end case
   repeat

   print 'bye'
   stop

* ---- list ----
list.all:
   select f.cust to 2
   cnt = 0

   print 'id' : ' ' : 'name' : ' ' : 'city'
   print '---' : ' ' : '----' : ' ' : '----'

   loop while readnext(id) from 2 do
      read rec from f.cust, id then
         print id : ' ' : rec<1> : ' ' : rec<3>
         cnt += 1
      end
   repeat

   clearselect 2
   print cnt : ' record(s)'
   return

* ---- add ----
add.one:
   print 'new id?' :
   input id
   print 'name?' :
   input name
   print 'phone?' :
   input phone
   print 'city?' :
   input city

   rec = name : @fm : phone : @fm : city
   write rec on f.cust, id on error
      print 'write failed: ' : @system.error.text
      return
   end
   print 'saved'
   return

* ---- view ----
view.one:
   print 'id?' :
   input id
   read rec from f.cust, id then
      print 'name  : ' : rec<1>
      print 'phone : ' : rec<2>
      print 'city  : ' : rec<3>
   end else
      print 'not found'
   end
   return

* ---- delete ----
delete.one:
   print 'id?' :
   input id
   print 'are you sure? (y/n)' :
   input confirm
   if confirm # 'y' then
      print 'cancelled'
      return
   end

   delete f.cust, id on error
      print 'delete failed: ' : @system.error.text
      return
   end
   print 'deleted'
   return
end
```

```
basic bp customer.manager
run bp customer.manager
```

```
l)ist  a)dd  v)iew  d)elete  q)uit
choice? l

id name city
--- ---- ----
1001 Acme Supplies Springfield
1002 Widget Corp Shelbyville
2 record(s)

l)ist  a)dd  v)iew  d)elete  q)uit
choice? v
id? 1001
name  : Acme Supplies
phone : 555-1234
city  : Springfield

l)ist  a)dd  v)iew  d)elete  q)uit
choice? q
bye
```

### What is in this program

| Feature | Where |
|---|---|
| `loop ... repeat` | the main menu loop |
| `begin case` / `case` / `end case` | dispatching on the menu choice |
| `gosub` / `return` | internal subroutines — labels inside the program |
| `select` / `readnext` / `clearselect` | walking the file for the list |
| `read` / `then` / `else` | reading a record |
| `write` / `on error` | writing a record safely |
| `delete` / `on error` | deleting a record |
| `@fm` | building a dynamic array |
| `rec<1>` | extracting fields |
| `exit` | leaving the main loop |
| `#` | not-equal comparison |
| `+=` | increment |

The `gosub` subroutines are **internal** — they are labels in the
same program, not separate programs. They share every variable in the
program. For subroutines with their own scope, see *SD Basic - Modern
Program Structure*.

## Cataloguing

Running a program with `run bp name` works, but typing `run bp` every
time is tedious. **Cataloguing** gives a program a name you can type
directly:

```
basic bp customer.manager
catalog bp customer.manager
```

```
customer.manager
```

```
l)ist  a)dd  v)iew  d)elete  q)uit
choice?
```

A catalogued program can be called from any account that can reach
it. The catalogue puts an entry in the VOC — the same file that maps
`list`, `select` and the built-in verbs. See *SD TCL - Programs and
the Catalogue*.

## Where to go next

Each section above linked to a reference page. Here they are together,
in the order the tutorial uses them:

| Topic | Reference page |
|---|---|
| Program structure | [SD Basic - Program Structure](01-sd-basic-program-structure.html) |
| Variables, loops, conditions | [SD Basic - Program Control](02-sd-basic-program-control.html) |
| Math functions | [SD Basic - Math Functions](03-sd-basic-math-functions.html) |
| String functions | [SD Basic - String Functions](04-sd-basic-string-functions.html) |
| Dynamic arrays | [SD Basic - Dynamic Arrays](05-sd-basic-dynamic-arrays.html) |
| Data conversion | [SD Basic - Data Conversion](06-sd-basic-data-conversion.html) |
| File handling | [SD Basic - File Handling](07-sd-basic-file-handling.html) |
| Select lists | [SD Basic - Select Lists](08-sd-basic-select-lists.html) |
| Locks and transactions | [SD Basic - Locks and Transactions](14-sd-basic-locks-and-transactions.html) |
| Modern program structure | [SD Basic - Modern Program Structure](18-sd-basic-modern-program-structure.html) |
| Compiling and cataloguing | [SD TCL - Programs and the Catalogue](24-sd-tcl-programs-and-the-catalogue.html) |
| File system concepts | [SD File System Concepts](35-sd-file-system.html) |
| Standard subroutines | [SD Standard Subroutines](36-sd-standard-subroutines.html) |

The syntax cards at the end of the set list every statement and
function alphabetically:

| | |
|---|---|
| [SD Basic - Syntax](94-sd-basic-syntax.html) | every SDBasic name, with its syntax |
| [SD TCL - Syntax](95-sd-tcl-syntax.html) | every TCL verb, with its syntax |
