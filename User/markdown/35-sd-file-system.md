Title: SD File System Concepts
Subtitle: The two file types, group structure, overflow, on-disk layout, and how the hash algorithm works.

SD stores data in files, and each file is one of two types: a
**directory file** or a **dynamic file**. The two have different
on-disk layouts, different performance characteristics, and different
rules for what can read them.

## Directory files

A directory file is an **ordinary Windows folder** with one file per
record. The record id is the file name.

| | |
|---|---|
| On disk | `C:\ProgramData\SD\user_accounts\<account>\<filename>\` |
| Record id | the file name |
| Readable by | any Windows program (Notepad, Excel, etc.) |
| Record ids | matched case insensitively |
| `create.file` option | `no.case` for explicit case-insensitive ids |

The `bp` file is a directory file. VOC, `batch.jobs`, `os.users`, and
the dictionaries are all directory files.

> SD writes directory file records with CR+LF line endings so that
> Windows programs can open them. Reading handles CR+LF, LF, and CR on
> its own.

## Dynamic files

A dynamic file is stored in SD's own binary format. It has a hash-based
group structure and resizes automatically as data grows or shrinks.

| | |
|---|---|
| On disk | binary files in the account directory |
| Record id | up to 250 characters |
| Readable by | SD only |
| Group size | set by `GRPSIZE` in `sd.conf` |
| Resizing | automatic, when the file is 80% full or 40% empty |

### Group structure

A dynamic file is divided into **groups**. Each group is a bucket that
holds records hashed to the same slot. The number of groups is always
a power of two, and it doubles or halves when the file resizes.

### Overflow

When a group has more data than fits in its primary bucket, additional
buckets are chained to it. This is **overflow**. Excessive overflow
degrades read performance because the chain has to be scanned.

`analyse.file` reports the overflow distribution; `fstat` reports the
file statistics.

### The hash algorithm

The record id is hashed to determine which group a record belongs to.
SD uses a standard hash function that distributes records evenly across
the available groups. When the file resizes, every record is rehashed to
the new group count.

## The dictionary file

Every data file has a companion dictionary file, named
`<filename>.dict`, that lives in the same account directory. The
dictionary defines the fields for the query processor. See
[SD Dictionaries - Structure](33-sd-dicts-structure.html) and
[SD Dictionaries - Conversions](34-sd-dicts-conversions.html).

## The sub-file structure

An account directory contains:

| | |
|---|---|
| `<filename>` | the data file (directory file: a folder; dynamic: binary) |
| `<filename>.dict` | the dictionary file |
| `voc` | the account's VOC |
| `bp` | the source file |
| `$hold` | the hold file (printer output) |
| `$savedlists` | saved select lists |
| `$command.stack` | the command stack |

## File analysis

```
analyse.file customers
fstat customers
```

| | |
|---|---|
| `analyse.file` | reports group distribution, overflow, and tuning recommendations |
| `fstat` | reports file statistics: record count, size, group count, min/max/average |

## Creating and configuring files

```
create.file customers
create.file orders dynamic
create.file lookup static
configure.file customers groups 64
```

| | |
|---|---|
| `create.file` | creates a file (directory or dynamic) |
| `delete.file` | deletes a file (refuses `voc` and `$acc`) |
| `clear.file` | empties a file of all records |
| `configure.file` | changes a file's configuration |

> `delete.file`'s refusal to delete `voc` and `$acc` no longer depends
> on the case you type them in.
