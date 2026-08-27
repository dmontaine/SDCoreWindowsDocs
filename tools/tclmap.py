#
# tclmap.py <sdb_ai/sd64/sdsys/newvoc>
#
# Assign every SD TCL verb to exactly one document, and CHECK THAT THE DOCUMENT
# ACTUALLY DOCUMENTS IT.  docmap.py does the first half for the SD BASIC roster;
# this does both halves for the verbs.
#
# ***WHY THE SECOND HALF EXISTS.***  On 27 Aug 2026 the TCL coverage was
# recorded as "127 of 144, 17 left".  It was 118, and ten verbs had no page.
# Seven of the ten were counted as covered because their NAME appeared
# somewhere - `listu` inside a warning on another page, `lock` inside the word
# "unlock", `create.account` inside a keyword table on the editor page.  The
# count had been answering "does this string occur" and the question is "is this
# verb explained here".  A map alone cannot tell the difference, so this script
# does not trust its own map: for every verb it also requires evidence on the
# page.
#
# EVIDENCE IS DELIBERATELY NARROW.  A verb counts as documented on a page only
# if the page mentions it backticked - `verb` - or begins a line with it inside
# a fenced code block, which is what the syntax blocks look like.  Prose alone
# is not evidence.  If that is too strict for a real page, widen the page, not
# this test.
#
# THE ROSTER IS COMPUTED, NEVER TYPED.  144 = the 123 verb records in newvoc
# plus the 21 in newvoc/TIER.ADD.ADMINISTRATOR, which do not overlap.  A VOC
# record is a verb if the first character of field 1 is V, or - for the four
# records that are a keyword AND a verb - the first character of field 3.
#
# EXITS NON-ZERO on: a verb assigned nowhere, a verb assigned twice, a verb
# assigned to a page that does not evidence it, an assignment naming a verb
# that is not on the roster, or a roster that came out empty.
#
import io
import os
import re
import sys

if len(sys.argv) < 2:
    sys.exit('usage: tclmap.py <path to sdsys/newvoc>')

NEWVOC = sys.argv[1]
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ---------------------------------------------------------------- the roster

def field(rec, n):
    return rec[n - 1] if len(rec) >= n else ''

roster = set()
for name in sorted(os.listdir(NEWVOC)):
    path = os.path.join(NEWVOC, name)
    if not os.path.isfile(path):
        continue
    with io.open(path, encoding='latin-1', newline='') as f:
        rec = [l.rstrip('\r\n') for l in f.read().split('\n')]
    t1 = field(rec, 1)[:1].upper()
    t3 = field(rec, 3)[:1].upper()
    if t1 == 'V' or (t1 == 'K' and t3 == 'V'):
        roster.add(name.lower())

admin_list = os.path.join(NEWVOC, 'TIER.ADD.ADMINISTRATOR')
with io.open(admin_list, encoding='latin-1', newline='') as f:
    admin = [l.strip() for l in f.read().split('\n')[1:] if l.strip()]
admin = set(v.lower() for v in admin)

overlap = roster & admin
if overlap:
    sys.exit('newvoc and TIER.ADD.ADMINISTRATOR overlap: %s' % sorted(overlap))

roster |= admin
if len(roster) < 100:
    sys.exit('REFUSED: roster came out as %d verbs - that is not a roster'
             % len(roster))

# ------------------------------------------------------------ the assignment
#
# Each entry is (set, markdown filename, verbs).  Keep it in page order.

DOCS = [
 ('User', '19-sd-tcl-command-processor.md', """
   abort alias clear.abort clear.data clear.input clear.stack cleardata clr cs
   display get.stack go if list.vars logto message off option pause quit
   report.src save.stack set set.exit.status stop who who.am.i break
 """),
 ('User', '20-sd-tcl-files-and-records.md', """
   analyse.file analyze.file clear.file cname configure.file copy copyp
   create.file ct delete delete.file dump fstat hsm list.files rename set.file
   set.trigger
 """),
 ('User', '21-sd-tcl-query-processor.md', """
   count list list.item list.label reformat search show sort sort.item
   sort.label sreformat sum
 """),
 ('User', '22-sd-tcl-select-lists.md', """
   clear.select clearselect copy.list delete.list form.list get.list list.diff
   list.inter list.union merge.list nselect qselect save.list select sselect
 """),
 ('User', '23-sd-tcl-alternate-key-indexes.md', """
   build.index create.index delete.index list.index make.index
 """),
 ('User', '24-sd-tcl-programs-and-the-catalogue.md', """
   basic catalog catalogue cd compile.dict debug delete.catalog
   delete.catalogue delete.common format generate list.common map run
 """),
 ('User', '25-sd-tcl-ed.md', """
   ed
 """),
 ('User', '26-sd-tcl-edit.md', """
   edit
 """),
 ('User', '27-sd-tcl-micro.md', """
   micro
 """),
 ('User', '28-sd-tcl-printing-and-spooling.md', """
   printer setptr sp.close sp.open sp.view spool como report.style
 """),
 ('User', '29-sd-tcl-the-terminal-and-the-session.md', """
   autologout bell clear.prompts clearinput clearprompts date date.format echo
   hush logmsg pterm sleep term time
 """),
 ('User', '30-sd-tcl-processes-and-phantoms.md', """
   pdebug pdump phantom pstat status
 """),
 ('User', '31-sd-tcl-locks.md', """
   release
 """),
 ('Administrator', '01-accounts-and-security.md', """
   clean.account config create.account delete.account encrypt.field grant
   list.grants modify.account modify.password revoke set.date update.account
 """),
 ('Administrator', '02-sessions-and-locks.md', """
   clear.locks list.locks list.readu listu lock logout unlock
 """),
 ('Administrator', '03-operating-system-access.md', """
   sh !
 """),
]

# Verbs deliberately not given a page of their own, with the reason.  These
# still have to be justified out loud rather than silently dropped.
# Nothing is exempt today, and that is the intended state.  An entry here has to
# carry the reason it is not on a page, so that "we skipped it" cannot look the
# same as "it is covered".  set.date lived here for one revision on a reason
# that turned out to be false - it was named on a USER page, not an
# administrator one - which is exactly the failure this dictionary invites.
EXEMPT = {}

# ------------------------------------------------------------------ evidence

def evidence(setname, filename):
    """Names backticked on the page, plus names starting a line in a fence."""
    path = os.path.join(HERE, setname, 'markdown', filename)
    if not os.path.exists(path):
        return None
    with io.open(path, encoding='utf-8', newline='') as f:
        text = f.read()
    found = set(m.lower() for m in re.findall(r'`([a-z!][a-z0-9._!]*)`', text))
    in_fence = False
    for line in text.split('\n'):
        if line.startswith('```'):
            in_fence = not in_fence
            continue
        if in_fence:
            m = re.match(r'^:?([a-z!][a-z0-9._!]*)', line.strip())
            if m:
                found.add(m.group(1).lower())
    return found

# ------------------------------------------------------------------- checking

assigned = {}
problems = []

for setname, filename, block in DOCS:
    verbs = block.split()
    ev = evidence(setname, filename)
    if ev is None:
        problems.append('MISSING PAGE   %s/%s' % (setname, filename))
        continue
    if not ev:
        problems.append('NO EVIDENCE AT ALL on %s/%s - refusing to score it'
                        % (setname, filename))
        continue
    for v in verbs:
        if v not in roster:
            problems.append('NOT A VERB     %-18s claimed by %s/%s'
                            % (v, setname, filename))
            continue
        if v in assigned:
            problems.append('ASSIGNED TWICE %-18s %s and %s'
                            % (v, assigned[v], filename))
            continue
        assigned[v] = '%s/%s' % (setname, filename)
        if v not in ev:
            problems.append('NO EVIDENCE    %-18s assigned to %s/%s but the '
                            'page neither backticks it nor opens a syntax line '
                            'with it' % (v, setname, filename))

for v in EXEMPT:
    if v in roster:
        assigned[v] = 'exempt'

missing = sorted(roster - set(assigned))
for v in missing:
    problems.append('NO PAGE        %-18s is a verb and is on no page' % v)

print('roster        : %d verbs' % len(roster))
print('assigned      : %d' % len([v for v in assigned if assigned[v] != 'exempt']))
print('exempt        : %d  %s' % (len(EXEMPT), ', '.join(sorted(EXEMPT))))
print('documents     : %d across %d set(s)'
      % (len(DOCS), len(set(d[0] for d in DOCS))))
print()

if problems:
    print('=== %d PROBLEM(S) ===' % len(problems))
    for p in problems:
        print('  ' + p)
    sys.exit(1)

print('every verb is on exactly one page, and every page evidences the verbs '
      'assigned to it.')
