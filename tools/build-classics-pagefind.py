"""Build one Pagefind index and exact Greek text map per close-reading work."""
import argparse
import html
import json
import subprocess
import tempfile
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('data', type=Path, help='Path to data/classics')
    parser.add_argument('output', type=Path, help='Parent for per-work bundles')
    parser.add_argument('--pagefind', required=True)
    args = parser.parse_args()
    catalog = json.loads((args.data / 'catalog.json').read_text(encoding='utf8'))
    for work in catalog['works']:
        wid = work['id']
        metadata = json.loads((args.data / wid / 'catalog.json').read_text(encoding='utf8'))
        entries = []
        output = args.output / wid
        output.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory() as directory:
            for i, page in enumerate(metadata['pages']):
                data = json.loads((args.data / wid / f'{page}.json').read_text(encoding='utf8'))
                units = [{'page': page, 'unitId': u['id'], 'ref': u['ref'], 'label': u['label'], 'text': ''.join(u['tokens'])} for u in data['units']]
                entries.extend(units)
                text = ' '.join(u['text'] for u in units)
                pagehtml = f'<!doctype html><html lang="el"><head><meta charset="utf-8"><title>{i}</title></head><body><main data-pagefind-body>{html.escape(text)}</main></body></html>'
                Path(directory, f'{i:04}.html').write_text(pagehtml, encoding='utf8')
            subprocess.run([args.pagefind, '--site', directory, '--output-path', str((output / 'pagefind').resolve()), '--quiet'], check=True)
        (output / 'units.json').write_text(json.dumps({'work': wid, 'pages': metadata['pages'], 'entries': entries}, ensure_ascii=False, separators=(',', ':')), encoding='utf8')
        print(f'{wid}: {len(metadata["pages"])} pages, {len(entries)} units', flush=True)


if __name__ == '__main__':
    main()
