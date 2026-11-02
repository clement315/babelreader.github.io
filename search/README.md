# Per-book search indexes

The `eustathius-iliad` directory contains a Pagefind 1.6.0 Extended search bundle and a literal-text section map for the EPUB in the catalogue. Pagefind is MIT licensed: https://github.com/Pagefind/pagefind.

The reader uses Pagefind to prioritize sections and also checks the literal section map, preserving substring and polytonic Greek searches. Each book gets its own bundle; no library-wide index is generated. The reader falls back to loading EPUB sections if the prepared bundle is missing or its spine differs.

When the EPUB changes, regenerate the bundle and section map together with `tools/build-epub-pagefind.py` and Pagefind Extended, then commit both. If the book's contents change without changing the spine, the old text map can miss matches; always rebuild it after edits. `sections.json` records the source EPUB SHA-256 for maintenance.

Example from the repository root:

```sh
python tools/build-epub-pagefind.py books/Eustathii_commentarii_ad_Homeri_Iliadem_Tomus_I_1.epub search/eustathius-iliad --pagefind pagefind_extended
```
