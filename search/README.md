# Per-book search indexes

The EPUB bundles cover the 27 EPUBs in the catalogue. `epub-map.json` maps catalogue IDs to separate bundles. `classics/` contains one bundle per Plato close-reading work, indexing Greek original text only. Pagefind 1.6.0 Extended is MIT licensed: https://github.com/Pagefind/pagefind.

The reader uses Pagefind to prioritize sections and also checks the literal section map, preserving substring and polytonic Greek searches. Each book gets its own bundle; no library-wide index is generated. The reader falls back to loading EPUB sections if the prepared bundle is missing or its spine differs.

When an EPUB changes, regenerate its bundle and section map together with `tools/build-epub-pagefind.py` and Pagefind Extended, then commit both. If the book's contents change without changing the spine, the old text map can miss matches; always rebuild it after edits. `sections.json` records the source EPUB SHA-256 for maintenance. Similarly, regenerate the classics bundles using `tools/build-classics-pagefind.py` after editing original Greek text or its page data. The Summa reader is not indexed by this feature.

Example from the repository root:

```sh
python tools/build-epub-pagefind.py books/Eustathii_commentarii_ad_Homeri_Iliadem_Tomus_I_1.epub search/eustathius-iliad --pagefind pagefind_extended
```
