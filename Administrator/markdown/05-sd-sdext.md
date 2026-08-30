Title: SD SDEXT Extension
Subtitle: The keys and functions SDEXT provides, and how to use them.

The SDEXT extension provides a set of keys that give SDBasic programs
access to system-level capabilities beyond the standard function set.
The `op_sdext.c` source ships in SD Core for Windows.

> ***The Python portion of SDEXT has been removed.*** The C sources,
> the Makefile flags, 20 `GPL.BP/PY_*` programs, `SYSCOM/SDPYFUNC.H`,
> the `SD_Py*` error codes and the Python SDEXT keys have all gone.
> The remaining SDEXT functionality — encryption keys, hex and base64
> encoding — is present and documented here.

## What SDEXT is

SDEXT is a set of keys that can be used with the `key()` function (or
the `@` system variables where applicable) to access extended
functionality. The keys are defined in the SDEXT source and are
available to any program that includes the appropriate `*include`
record.

## The keys

### Encryption keys

| Key | Purpose |
|---|---|
| `SD_SALT` | the salt used in key derivation for `sdencrypt()` / `sddecrypt()` |
| `SD_KEYFROMPW` | derives an encryption key from a password |

These keys are used by the encryption functions described in
[SD Encryption](04-sd-encryption.html).

### Encoding keys

| Key | Purpose |
|---|---|
| Hex encoding | convert binary data to a hexadecimal string |
| Base64 encoding | convert binary data to a base64 string |

These are used when encrypted data needs to be stored as text — in a
field that only holds printable characters, or in a sequential file
that must remain text-safe.

## How to use SDEXT

The keys are accessed through SDBasic's `key()` function or the
appropriate system interface. An `*include` record makes the key
names available to a program.

## What is not in SDEXT

| Removed | Reason |
|---|---|
| `SD_PY*` keys | Embedded Python was dropped from SD Core |
| `SDPYFUNC.H` | The Python function header was deleted |
| `PY_*` programs | 20 Python programs in `GPL.BP` were deleted |
| `OP_SDPYOBJ` opcode | retired to `op_illegal` |

The Python SDEXT keys are gone and any program referencing them will
not compile. If a program tests for a Python SDEXT key, the test can
be deleted — the state it tested for can never be reached.
