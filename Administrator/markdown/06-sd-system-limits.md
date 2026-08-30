Title: SD System Limits
Subtitle: Maximum sizes, counts and depths that apply across SD Core for Windows.

This page collects the system limits measured on SD Core for Windows
W1.0-0. Values are observed, not quoted from documentation of another
product.

## Data limits

| | |
|---|---|
| Maximum record size | 2 GB (addressable space) |
| Maximum field count per record | unlimited (constrained by record size) |
| Maximum field length | unlimited (constrained by record size) |
| Maximum value count per field | unlimited (constrained by record size) |
| Maximum subvalue count per value | unlimited (constrained by record size) |
| Maximum record id length | 255 characters (directory file), 250 (dynamic file) |

## File limits

| | |
|---|---|
| Maximum open files per session | set by `NUMFILES` in `sd.conf` |
| Maximum group size (dynamic file) | set by `GRPSIZE` in `sd.conf` |
| Maximum alternate key index size | unlimited (disk-constrained) |

## Lock limits

| | |
|---|---|
| Maximum locks per session | set by `NUMLOCKS` in `sd.conf` |
| Maximum file locks | one per file |
| Maximum record locks | unlimited (constrained by `NUMLOCKS`) |

## Program limits

| | |
|---|---|
| Maximum program size | unlimited (disk-constrained) |
| Maximum subroutine call depth | unlimited (stack-constrained) |
| Maximum matrix dimensions | two-dimensional |
| Maximum matrix size per dimension | unlimited (memory-constrained) |
| Maximum common block size | unlimited (memory-constrained) |
| Maximum argument count to `call` / `subroutine` | 20 (API), unlimited (SDBasic) |
| Maximum `execute` command length | unlimited (memory-constrained) |

## Select list limits

| | |
|---|---|
| Maximum select list items | unlimited (disk-constrained) |
| Maximum active select lists | 32 (numbered 0-31, plus stack-based) |
| Maximum select list id length | 250 characters |

## Configuration limits

| | |
|---|---|
| Configuration parameters | ~30 active parameters in `sd.conf` |
| `NETFILES` | accepted but inert (QMNet removed) |
| `FILERULE` | accepted but inert (QMNet removed) |
| `CREATUSR` | accepted but ignored |

## Terminal limits

| | |
|---|---|
| Terminal page width | default 120, settable with `term` |
| Terminal page depth | default 36, settable with `term` |
| Minimum page size | 10 lines × 20 columns |
| Terminfo definitions shipped | 63, compiling to 100 terminal names |

## VOC limits

| | |
|---|---|
| VOC records per account (administrator) | 416 |
| VOC records per account (programmer) | 396 |
| VOC records per account (standard) | 354 |
| VOC record id length | 255 characters |

## Account limits

| | |
|---|---|
| Maximum accounts | unlimited (disk-constrained) |
| Account name length | 32 characters |
| Users per group account | unlimited (Windows group-constrained) |
| Grants per account | unlimited (Windows group-constrained) |
