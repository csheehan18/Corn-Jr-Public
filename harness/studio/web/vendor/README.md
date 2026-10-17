# Vendored libraries

The studio page is static files with no build step, so the four libraries it
runs on are copied here as ES modules and loaded through the import map in
`../index.html`. Nothing is fetched from the internet at runtime, and nothing
here is edited by hand: `scripts/check_studio.py` holds each file to the
sha256 below, so a hand edit or a half-finished upgrade fails the sweep
instead of shipping.

| file | package | version | sha256 |
|---|---|---|---|
| `preact.js` | `preact` (`dist/preact.module.js`) | 10.29.8 | `712517dd2a42c3c22b5ab0264ad7e9a2b1e8be6cf97fa00dbedd98203617e616` |
| `hooks.js` | `preact` (`hooks/dist/hooks.module.js`) | 10.29.8 | `210b89579f3e0dcbb425feb8fbb8e907f843ea3113dd1069a00ebc242908b9d7` |
| `htm.js` | `htm` (`dist/htm.module.js`) | 3.1.1 | `ab33dd3f38059b9be4d5f5350128eefb2356639c4e0bbe9d9e8b3ba75847e9e4` |
| `signals-core.js` | `@preact/signals-core` (`dist/signals-core.module.js`) | 1.14.4 | `09550c9fea0ab36b1c12e9ff0bdc2a26ed310dd5a386197371f3677f44dae63a` |
| `signals.js` | `@preact/signals` (`dist/signals.module.js`) | 2.11.2 | `dfece8a0726af95f3df335b6ca94e402cfc313b4d880fdeb67f1c6b2ba2a322f` |

Each file is the package's own minified ES module with its trailing
`//# sourceMappingURL=` line removed (the maps are not shipped, and a
dangling reference is a 404 in every console). Their licences are in
`LICENSES.txt` and attributed in the repo's `NOTICE`.

**Why these.** Preact is React's component model in about 4 KB gzipped;
htm gives it JSX-like templates without a compiler; signals make a streamed
token update one text node instead of re-rendering the conversation. The 10.x
line was chosen over Preact 11 (released 2026-09-30) for maturity; signals
2.11 supports both.

**To upgrade**, from an empty scratch folder (`npm pack` downloads and
verifies the tarball and runs no install scripts):

```
npm pack preact@<v> htm@<v> @preact/signals@<v> @preact/signals-core@<v>
```

extract each, copy the five files above with the `sourceMappingURL` line
stripped, update `LICENSES.txt`, and replace the versions and hashes in this
table -- the guard reads them from here.
