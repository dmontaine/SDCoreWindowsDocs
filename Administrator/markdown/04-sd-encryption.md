Title: SD Encryption
Subtitle: The sdencrypt and sddecrypt functions, the sodium library, and key management.

SD Core for Windows ships with libsodium-based encryption. The
`sdencrypt()` and `sddecrypt()` SDBasic functions are the supported
route for encrypting and decrypting data from programs.

> ***The `ENCRYPT.FIELD` TCL verb is gone.*** It pointed at a program
> (`$CRYPTO`) that never existed in the GPL release. Nothing replaces
> the verb that encrypted a field in place from TCL. Use the SDBasic
> functions in a program instead.

## The functions

```
sdencrypt(plaintext, key)
sddecrypt(ciphertext, key)
```

| | |
|---|---|
| `sdencrypt(plaintext, key)` | returns the ciphertext |
| `sddecrypt(ciphertext, key)` | returns the plaintext |
| key | a string used to derive the encryption key |

**These replaced the older `encrypt()` and `decrypt()` functions.**
The old names are not available.

## The library

The encryption is built on **libsodium**, a modern, audited
cryptographic library. SD links it at build time; no separate
installation is needed.

## Key management

The encryption keys are managed through the SDEXT extension. See
[SD SDEXT Extension](05-sd-sdext.html).

| Key | Purpose |
|---|---|
| `SD_SALT` | the salt used in key derivation |
| `SD_KEYFROMPW` | derives a key from a password |

The password is never stored anywhere. SD keeps a scrambled verifier
that cannot be turned back into a password. This is the same design
used for the SCRAM-SHA-256 API login.

## SCRAM-SHA-256 authentication primitives

The API login uses a challenge-response protocol built on the same
library. The primitives behind it are:

| Primitive | What it does |
|---|---|
| SHA-256 | one-way hash |
| HMAC-SHA256 | keyed hash |
| PBKDF2 | key derivation from a password |
| random bytes | nonce and salt generation |
| XOR | combining values |
| constant-time compare | comparing without timing leaks |

These are internal to the SCRAM exchange and are not called directly
from SDBasic. The `sdencrypt()` and `sddecrypt()` functions are the
application-level interface.

## Field-level encryption from SDBasic

```
* Encrypt a field before writing
key = "my-secret-key"
encrypted = sdencrypt(record<7>, key)
record<7> = encrypted
write record on customers, id
```

```
* Decrypt after reading
read record from customers, id else return
key = "my-secret-key"
plaintext = sddecrypt(record<7>, key)
record<7> = plaintext
```

> ***The key is your responsibility.*** SD does not store application
> keys. If the key is lost, the data is lost. If the key is embedded in
> a compiled program, the program source is the key — protect the
> source.

## What is not available

| | |
|---|---|
| `ENCRYPT.FIELD` verb | removed; the program behind it never shipped |
| `encrypt()` / `decrypt()` | replaced by `sdencrypt()` / `sddecrypt()` |
| Field-level encryption from TCL | gone; use a program |
