#
# mksyntax.py <gpl.bp/BCOMP> <out.md>
#
# Build User document 18, the syntax card: ONE alphabetical run of every name
# BCOMP accepts, with its syntax and nothing else.
#
# WHY IT IS GENERATED.  The card's whole value is that every name is on it.  A
# hand-written list of four hundred entries is a list with omissions nobody
# notices, so the roster comes from BCOMP's own tables and this script REFUSES
# to write the page if any name lacks a line.  The same reason docmap.py
# exists, one level down: docmap says each name is described somewhere, this
# says each name is looked up here.
#
# WHERE THE SYNTAX COMES FROM, said plainly because it is not all one thing:
#
#   * ARGUMENT COUNTS FOR FUNCTIONS ARE MECHANICAL.  BCOMP dispatches each
#     intrinsic to an argument handler through an "on i goto" list that is
#     POSITIONAL against the name list, and each entry carries the name in a
#     trailing comment.  So the count can be read off, and the comment is a
#     free alignment control - this script asserts the two lists are the same
#     length and that every comment matches its name.  If BCOMP is edited and
#     the two drift apart, this stops rather than emitting a wrong card.
#
#   * EVERYTHING ELSE IS IN syntax-shapes.txt, one NAME = syntax per line.
#     Statements have clauses rather than argument lists, and functions whose
#     handler is a special case (CSVDQ, OPEN.SOCKET, SYSMSG and about twenty
#     more) have shapes the count cannot express.  Those lines were taken from
#     documents 01 to 17, where they were measured, and from BCOMP's own
#     statement compilers where no page covers them.
#
# The data file wins wherever both have an opinion, so a measured shape always
# beats a derived one.
#
import io
import os
import re
import sys

BCOMP = sys.argv[1]
OUT = sys.argv[2]
SHAPES = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                      'syntax-shapes.txt')

src = io.open(BCOMP, encoding='latin-1', newline='').read()
lines = src.split('\n')
WORD = re.compile(r'"([A-Z][A-Z0-9.$]*)"')

# ---------------------------------------------------------------- the tables

def table(name):
    """The same matcher docmap.py uses, which is checked at 411 of 411."""
    got = set()
    for line in lines:
        s = line.strip()
        if s.startswith('*'):
            continue
        if re.match(re.escape(name) + r'\s*(<[^>]*>)?\s*:?=', s):
            got.update(WORD.findall(s))
    if not got:
        sys.exit('EMPTY table %s - refusing to build a card from nothing' % name)
    return got


def ordered(prefix):
    """The names of one list IN SOURCE ORDER, initialiser and appends alike."""
    out = []
    pat = re.compile(r'^' + re.escape(prefix) + r'\s*(?:<-1>)?\s*=\s*"([A-Z][A-Z0-9.$]*)"')
    for line in lines:
        s = line.strip()
        if s.startswith('*'):
            continue
        m = pat.match(s)
        if m:
            out.append(m.group(1))
    return out


def handlers(start):
    """(handler, commented name) from an 'on i goto' dispatch block."""
    out = []
    i = start
    while i < len(lines):
        s = lines[i].strip()
        m = re.match(r'(?:on i goto\s+)?(in\.[a-z0-9.]+)\s*,?\s*;\*\s*(\S+)', s)
        if m:
            out.append((m.group(1), m.group(2)))
        elif out:
            break
        i += 1
    return out


STATEMENTS = table('statements') | table('non.debug.statements')
RESTRICTED = table('restricted.statements')
RESERVED = table('reserved.names')
INTRINSICS = table('intrinsics')
EVERYTHING = STATEMENTS | RESTRICTED | RESERVED | INTRINSICS

pub = ordered('intrinsics')
starts = [n for n, ln in enumerate(lines) if 'on i goto' in ln and 'in.' in ln]
if len(starts) < 2:
    sys.exit('cannot find both intrinsic dispatch blocks - refusing')
hp = handlers(starts[1])

if len(pub) != len(hp):
    sys.exit('intrinsic name list is %d and its dispatch list is %d - they are '
             'positional and have drifted apart.  Refusing.' % (len(pub), len(hp)))
# The comments are informal, so a couple are abbreviations rather than the
# name.  Listed one by one ON PURPOSE: loosening the comparison to let them
# through would throw away the only control there is on the two lists being
# in step.  A new abbreviation should stop this script and be added here after
# somebody has looked at it.
COMMENT_ALIASES = {'ARG.COUNT': 'ARGCT'}
drift = [(a, b[1]) for a, b in zip(pub, hp)
         if a.replace('.', '') != b[1].replace('.', '')
         and COMMENT_ALIASES.get(a) != b[1]]
if drift:
    sys.exit('dispatch comments do not match their names: %s' % drift[:5])

# The placeholders are italic because the page says italic means "you supply
# it".  A derived line that used plain letters would contradict its own key.
# They are generic on purpose: what the dispatch table knows is the COUNT, and
# inventing a meaningful name for each argument would be inventing.
ARITY = {
    'in.none': 0,
    'in.one': 1,
    'in.two': 2,
    'in.three': 3,
    'in.four': 4,
    'in.five': 5,
}
LETTERS = ['a', 'b', 'c', 'd', 'e']
derived = {}
for name, (hnd, _c) in zip(pub, hp):
    if hnd in ARITY:
        n = ARITY[hnd]
        args = ', '.join('*%s*' % LETTERS[i] for i in range(n))
        derived[name] = '`%s(`%s`)`' % (name.lower(), args)

# ------------------------------------------------------------- the data file

shapes = {}
with io.open(SHAPES, encoding='utf-8', newline='') as f:
    for n, line in enumerate(f, 1):
        line = line.rstrip('\r\n')
        if not line.strip() or line.lstrip().startswith('#'):
            continue
        if '=' not in line:
            sys.exit('%s:%d has no "=": %r' % (SHAPES, n, line))
        key, val = line.split('=', 1)
        key = key.strip().upper()
        val = val.strip()
        if key in shapes:
            sys.exit('%s:%d duplicates %s' % (SHAPES, n, key))
        shapes[key] = val
if not shapes:
    sys.exit('syntax-shapes.txt is empty - refusing')

# ------------------------------------------------------------- the null case

entries = {}
for name in EVERYTHING:
    if name in shapes:
        entries[name] = shapes[name]
    elif name in derived:
        entries[name] = derived[name]

missing = sorted(EVERYTHING - set(entries))
bogus = sorted(set(shapes) - EVERYTHING)

print('BCOMP accepts        : %d name(s)' % len(EVERYTHING))
print('  statements         : %d' % len(STATEMENTS))
print('  restricted         : %d' % len(RESTRICTED))
print('  reserved words     : %d' % len(RESERVED))
print('  intrinsics         : %d' % len(INTRINSICS))
print('shapes given by hand : %d' % len(shapes))
print('shapes derived       : %d' % len(derived))
print('entries on the card  : %d' % len(entries))
print()
if bogus:
    print('=== IN syntax-shapes.txt, NOT ACCEPTED BY BCOMP (%d) ===' % len(bogus))
    print('  ' + ' '.join(bogus))
    print()
if missing:
    print('=== ACCEPTED BY BCOMP, NO SYNTAX LINE (%d) ===' % len(missing))
    print('  ' + ' '.join(missing))
    print()
    print('REFUSED: the card is not complete, and a lookup card that is missing')
    print('         a name is worse than none - the reader concludes it does')
    print('         not exist.  Add the lines to syntax-shapes.txt.')
    sys.exit(1)
if bogus:
    print('REFUSED: a name in the data file that BCOMP does not accept is either')
    print('         a typo or a statement that has been removed.')
    sys.exit(1)

# ------------------------------------------------------------------ the page

def kind(name):
    if name in INTRINSICS:
        return 'function'
    if name in RESTRICTED:
        return 'restricted'
    if name in STATEMENTS:
        return 'statement'
    return 'clause word'


HEAD = u"""Title: SD Basic - Syntax
Subtitle: Every statement and function, alphabetically, with its syntax and nothing else.

A lookup card, and nothing else. If you know what you want and have forgotten
how to spell it, it is here. If you want to know what it *does*, the other
seventeen documents in this set are where that lives.

*Italics* mark something you supply, **bold** a word typed as it stands, and
braces an optional part. SD folds case, so any of this may be written in
either case.

> **This page is generated, and it is checked for completeness rather than
> proof-read for it.** The roster comes from `BCOMP`'s own tables — the same
> extraction the rest of this set uses — and `tools/mksyntax.py` refuses to
> write the page if a single name accepted by the compiler has no line on it.
> Argument counts for functions are read out of `BCOMP`'s dispatch table,
> which is positional against the name list and carries each name in a
> comment; the script asserts the two agree before it uses either. The
> shapes that a count cannot express — every statement, and about twenty
> functions — come from documents 01 to 17, where they were measured.

***THREE THINGS ARE MARKED, AND THEY ARE THE ONES THAT WASTE TIME.***

| | |
|---|---|
| ***(restricted)*** | internal programs only. An ordinary account gets *"Unrecognised statement"* |
| ***(no such thing)*** | in the compiler's table with nothing behind it. It does not compile for anybody |
| ***(clause word)*** | not a statement — a word that belongs inside another one's syntax |

"""

TAIL = u"""
## See also

[SD Basic - Program Structure](01-sd-basic-program-structure.html) ·
[SD Basic - Program Control](02-sd-basic-program-control.html) ·
[SD Basic - File Handling](07-sd-basic-file-handling.html) ·
[SD Basic - System and Environment](16-sd-basic-system-and-environment.html).
"""

out = [HEAD]
letter = None
for name in sorted(entries):
    first = name[0]
    if first != letter:
        letter = first
        out.append(u'\n## %s\n\n' % letter)
        out.append(u'| | |\n|---|---|\n')
    line = entries[name]
    if kind(name) == 'restricted' and '(restricted)' not in line:
        line += u' ***(restricted)***'
    if kind(name) == 'clause word' and '(clause word)' not in line:
        line += u' ***(clause word)***'
    out.append(u'| **`%s`** | %s |\n' % (name.lower(), line))
out.append(TAIL)

text = u''.join(out)
with io.open(OUT, 'w', encoding='utf-8', newline='\n') as f:
    f.write(text)
print('wrote %s  %d bytes, %d entries, %d letter sections'
      % (OUT, len(text), len(entries), text.count('\n## ')))
sys.exit(0)
