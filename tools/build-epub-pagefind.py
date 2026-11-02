"""Build an isolated Pagefind bundle and literal-text map for one EPUB.

Example: python tools/build-epub-pagefind.py book.epub search/my-book --pagefind pagefind_extended
Requires Pagefind Extended (for Chinese text). Rebuild after editing the EPUB.
"""
import argparse
import hashlib
import html
import json
import posixpath
import subprocess
import tempfile
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET


def local(tag):
    return tag.rsplit('}', 1)[-1].lower()


def text_nodes(element):
    if local(element.tag) in {'head', 'script', 'style', 'noscript'}:
        return ''
    result = [element.text or '']
    for child in element:
        result.append(text_nodes(child))
        result.append(child.tail or '')
    return ''.join(result)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('epub', type=Path)
    parser.add_argument('output', type=Path)
    parser.add_argument('--pagefind', required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(args.epub) as book, tempfile.TemporaryDirectory() as directory:
        container = ET.fromstring(book.read('META-INF/container.xml'))
        rootfile = next(e.attrib['full-path'] for e in container.iter() if local(e.tag) == 'rootfile')
        package = ET.fromstring(book.read(rootfile))
        manifest = {e.attrib['id']: e.attrib for e in package.iter() if local(e.tag) == 'item'}
        spine = [e.attrib['idref'] for e in package.iter() if local(e.tag) == 'itemref']
        sections = []
        for ordinal, idref in enumerate(spine):
            item = manifest[idref]
            href = item['href'].split('#', 1)[0]
            path = posixpath.normpath(posixpath.join(posixpath.dirname(rootfile), href))
            document = ET.fromstring(book.read(path))
            text = text_nodes(document)
            sections.append({'href': href, 'text': text})
            page = f'<!doctype html><html lang="zh"><head><meta charset="utf-8"><title>{ordinal}</title></head><body><main data-pagefind-body>{html.escape(text)}</main></body></html>'
            Path(directory, f'{ordinal:04}.html').write_text(page, encoding='utf-8')
        subprocess.run([args.pagefind, '--site', directory, '--output-path', str(args.output.resolve() / 'pagefind')], check=True)
        (args.output / 'sections.json').write_text(json.dumps({'sha256': hashlib.sha256(args.epub.read_bytes()).hexdigest(), 'sections': sections}, ensure_ascii=False, separators=(',', ':')), encoding='utf-8')
        print(f'Indexed {len(sections)} sections from {args.epub.name}')


if __name__ == '__main__':
    main()
