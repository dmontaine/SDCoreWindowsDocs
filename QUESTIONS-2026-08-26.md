Title: Questions on the first document set
Subtitle: Not part of the tester set — a review list, 26 Aug 2026.

Everything below is written so you can answer in a word or a sentence. **Nothing
here blocked the drafting**; the eleven pages are complete and consistent under
the assumption stated with each question. Where I guessed, the guess is named.

***THIS FILE IS NOT PART OF THE TESTER SET.*** Delete or move it before the set
goes out.

## A. One defect found while writing

***1. THE CHANGELOG SENDS USERS TO AN `sd.conf` THAT DOES NOT EXIST.***

The entry of 21 Aug 2026, *"THE API IS REACHED AT ITS OWN PORT NOW"*, ends:

> *"to turn the API off altogether, comment out the APIPORT line in
> `C:\ProgramData\SD\sdsys\sd.conf` and restart SD"*

The file is at **`C:\ProgramData\SD\sd.conf`** — `gplsrc/sddefs.h:262`
(`SD_CONFIG_DEFAULT`) and `sd.iss:407`, which installs it to `{#DataDir}`, not
into `sdsys`. The 21 Aug entry names `sdsys\sd.conf` twice.

I have written the correct path in the documents. **The changelog ships to
users and still carries the wrong one.** Do you want a correction entry, or a
silent fix?

## B. Scope of the set

**2. "Do not document any features missing from SD Core" versus the topic
*Historical features not available in SD Core*.**

I read the first as *do not write usage documentation for things that are not
there*, and the second as *tell a tester what is gone so they stop looking for
it*. So page 10 is a list of removals with what to use instead, and describes
none of the removed features.

**Is that the split you intended?** The alternative readings are that page 10
should go entirely, or that it should be a bare list with no explanation.

**~~3. Where does this set ultimately live?~~ ANSWERED 26 Aug 2026.**

> *"There will be a separate repository on github for all the documentation we
> create. It will not have the no binary bits rule."*

Recorded in PROJECT_STATUS. **Two follow-on questions it raises are 15 and 16
below** — neither is urgent, but both are easier to settle before the
repository exists than after.

**Noted and not acted on:** the 25 Aug reasoning for keeping documentation in
the code repository was that a detached copy drifts — *"on 25 Aug alone, four
statements in the installer dialogs had quietly stopped being true."* That was
outweighed rather than answered, so **drift is now caught by a person or not at
all.** The practical consequence is that a release which changes a dialog, a
verb or a message needs somebody to re-read the affected pages; nothing will
fail if one goes stale.

**~~4. Three topics testers will want that are not on your list.~~ ANSWERED
26 Aug 2026 — all three written.**

| | |
|---|---|
| [Your first thirty minutes](01a-first-run.html) | install → account → file → a second user over ssh, in eight steps |
| [Running SD](01b-running-sd.html) | the service, `sd -start` / `-stop`, and the unclean-shutdown case |
| [Client distribution](06a-client-distribution.html) | which DLL, 32- versus 64-bit, and the one file no installer can update |

***THEY ARE NUMBERED `01a`, `01b` AND `06a` SO THEY SIT IN READING ORDER
WITHOUT RENUMBERING THE NINE YOU ALREADY HAVE.*** The walkthrough in particular
had to come straight after installation rather than at the end of the set. **If
you would rather have a clean `01`–`13`, say so** — it is one commit now and a
worse one later, once the set grows.

**Two things in those pages are worth a specific look:**

- **The walkthrough opens by telling the tester to sign out of Windows and back
  in.** That is not padding — the installing user's token cannot carry
  `sdusers` until they do, and the symptom reads as a broken install. It is
  also why the post-install check offered at the end of the installer is always
  the incomplete run.
- **Client distribution names `C:\Program Files (x86)\BLC\mvDeveloper\qmclilib.dll`
  as the one file no installer or `PATH` entry can update**, because Windows
  searches an executable's own directory first. That is the most likely way to
  test an old client without realising it. **Confirm you are happy naming
  mvDeveloper and that path in a document testers will read.**

**And one thing I could not settle** — question 18 below.

## C. Specific features

**5. `create.account other`.**

`CREATEA`'s own header says it is *"maintained for backwards compatibility"*
and *"will require manual editing of the accounts record to specify the group
the account belongs to."*

**I left it out of the account-types page deliberately** — documenting a form
that needs hand-editing to work invites people to use it. Confirm, or should it
be documented with the caveat?

**6. `batch.jobs` — scheduled jobs.** Currently a section on the *Other
hardening* page. It is arguably a feature rather than hardening, and testers
running overnight reports will look for it under its own name. Own page?

**7. The `limitssh` question that PROJECT_STATUS records as yours.**

On a machine whose `sshd_config` is **stock** — no `AllowGroups` line — the
default-ticked *limit ssh* task edits an ssh server SD did not install, because
refusal 2 in `allow-ssh-groups.ps1` only fires when a policy line already
exists.

The ssh page currently describes the behaviour as it is. **If you rule on this,
the page changes.** Not a documentation question, but it is on the critical
path for what page 5 says.

**8. `sdapi` group wording.** I wrote *"a member of the `sdapi` group, which no
account joins unless you put it there"*. Strictly, `create.account user x api`
or `... both` joins it for you. Is the changelog's original wording still
accurate, or should it read *"which an account joins only when you give it API
access"*?

## D. House style, so a later round matches

**9. Product name.** The banner says **SD CORE**. I have used *SD Core for
Windows* in page titles and the header bar, and *SD Core* in prose. Confirm.

**10. Version string.** The release stamp is **W1.0-0** and the folder you
named is **1.0-0**. Pages show `W1.0-0` in the header bar. Confirm which a
tester should quote in a report.

**11. "Verbs" or "commands"?** SD's source and the tier lists say *verbs*;
OpenQM's documentation says *commands*. I have used **verbs** when talking
about what a VOC contains and **commands** when talking about what a person
types. Fine, or pick one?

**12. Lower case in the documents.** The sample you approved shows commands in
lower case and I have kept that throughout, including for verbs whose changelog
entries are written in capitals. Confirm — it is a one-line change to the
renderer either way.

## E. Things I could not check

**13. The Turkish and Azeri fix.** Page 7 describes it from the changelog. It
has not been exercised on such a locale as far as the record shows. Worth
telling testers to try, or leave the claim as written?

**14. Remote administration over ssh.** PROJECT_STATUS records that a local
account arriving over the network gets a **filtered** token, so an SD
administrator over ssh may be unable to elevate and so unable to reach SDSYS —
and that this **has never been measured**. Page 5 says exactly that, including
that it is unmeasured. **Do you want that stated to testers**, or held back
until somebody measures it?

## F. Raised by the new documentation repository

Added 26 Aug 2026, after the decision that documentation gets its own GitHub
repository without the no-binaries rule. **Neither is urgent, and both are
cheaper to settle before the repository exists than after.**

**15. Does the toolchain move with the documentation?**

`mkdoc.py` (Markdown → HTML) and `mkpdf.ps1` (HTML → PDF) are both in
`sd4windows\sdb_ai\sd64\gplbld`, and both are on `assert-current`'s
`$neverShipped` list so they cost no install cycle.

| | |
|---|---|
| **Leave them in `gplbld`** | one toolchain, already wired into the guard. But the documentation repository then cannot build its own pages without a checkout of `sd4windows` |
| **Move them to the doc repository** | it becomes self-contained. Requires removing both from `$neverShipped` in the same commit, or the guard reports the tree stale by their absence |

**No recommendation — it depends on whether anyone but you will build the
documentation.** If the answer is "only me, on this machine", leaving them is
simpler.

**16. Are the rendered PDFs tracked, or generated on demand?**

***YOUR ANSWER TO WHY THE PDFs EXIST MOSTLY SETTLES THIS.*** You said they are
the deliverable: zipped with the installer, shared on pCloud, eventually
SourceForge.

**A release artefact does not need to be in git history to do its job** — it
needs to be **reproducible at release time** from tracked source, which
`mkdoc.py` + `mkpdf.ps1` already are. So the current `.gitignore` fits your
workflow as it stands, and the only open part is convenience:

| | |
|---|---|
| **Leave them ignored** *(current)* | clean history. You render before each release and zip the result |
| **Track them** | a clone carries the deliverable with no toolchain — useful if anyone else ever assembles a release. Costs ~200 KB of binary diff per edited page, for ever |

***THE PDFs ARE NOT AT RISK EITHER WAY.*** `.gitignore` keeps them out of
history; it does not delete them. All twelve are on disk beside the Markdown
and in your P-drive copy.

**17. Do you want a release step, rather than assembling the zip by hand?**

Raised by the same answer. A short script would: render every page fresh from
the Markdown, check that no PDF is older than its source, zip them with a
version-stamped name, and print the SHA256 so what you upload can be verified
against what you built.

***THE REASON IT IS WORTH MORE THAN THE TEN MINUTES IT SAVES:*** the
separate-documentation-repository decision gave up the only automatic check
that a page still matches the product. **Zipping by hand adds a second way to
drift** — shipping a PDF rendered before the last Markdown fix, which nothing
would catch and which looks exactly like a correct release.

Say the word and I will write it; it is half an hour and it wants to exist
before the first release, not after.

**18. How are the client libraries published for this release?**

Raised while writing [Client distribution](06a-client-distribution.html), and I
could not answer it from the record. The two client repositories each have
their own Inno installer (`sdclient.iss`, `qmclient.iss`), and no built DLL is
committed to either — a clone builds.

**What a tester cannot work out is what they will actually be handed:** a
client installer zipped beside the server one, a separate download, or nothing
yet. The page currently says *"if you need a client and cannot find one, ask
rather than building from source"*, which is honest but is a placeholder.

***THIS INTERACTS WITH THE pCloud/SourceForge PLAN***: if the release is one
zip containing the installer and the PDFs, the client installers are either in
it or they are a second download, and the documentation should say which.
