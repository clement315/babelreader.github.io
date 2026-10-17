"""Repair recognisable OCR substitutions for Chinese quotation/title marks.

Only Chinese-language fields are visited. Latin text, source references and
ordinary parentheses are never rewritten. Run without --write to audit only.
"""
from pathlib import Path
import argparse
import collections
import hashlib
import json
import re

HAN = r'\u3400-\u9fff'
LATIN = r'A-Za-zÀ-ÖØ-öø-ÿ'
TITLE_ATOM = r'(?:[^\n《》<>()（）〈〉「」『』，。;；:：!?！？]|\([^()\n]{1,15}\)|「[^「」\n]{1,20}」)'
TITLE = rf'{TITLE_ATOM}{{1,50}}'
FALLBACK = re.compile(r'(<script id="summa-fallback" type="application/json">)(.*?)(</script>)', re.S)
# Individually reviewed delimiter fragments. Damaged Chinese words in the
# surrounding OCR are deliberately retained rather than guessed from Latin.
REVIEWED_FRAGMENTS = {
    '《靈魂論J卷': '《靈魂論》卷',
    '《證道集第二': '《證道集》第二',
    '《創世紀;第三': '《創世紀》第三',
    '《信經「不拘誰JJ': '《信經「不拘誰」》',
    '《堅持:))': '《堅持:》',
    '《辜!說:))': '《辜!說:》',
    '「論四末j': '「論四末」',
    '「天主的手臂y': '「天主的手臂」',
    '的靈魂論》': '的《靈魂論》',
    '在可靈魂論》': '在《靈魂論》',
    '範圍內疑問指南》': '範圍內《疑問指南》',
    '因此，創世紀》': '因此，《創世紀》',
    '在「論天主聖三》': '在《論天主聖三》',
    '在已形上學》': '在《形上學》',
    '〜神名論》': '《神名論》',
    '((j!m拉達書》': '《j!m拉達書》',
    '((om:慕爾紀上》': '《om:慕爾紀上》',
    '<<德哥!I篇》': '《德哥!I篇》',
    '<<司l!導文獻選集》': '《司l!導文獻選集》',
    '<<ð論:命七天創造工程》': '《ð論:命七天創造工程》',
    '<<1不拘誰」信經》': '《「不拘誰」信經》',
    '《論神職人員行為準頁。>>': '《論神職人員行為準頁。》',
}


def repair_pass(text, counts=None, events=None):
    counts = counts if counts is not None else collections.Counter()

    def sub(rule, pattern, replacement, condition=None):
        nonlocal text
        def replace(m):
            if condition and not condition(m):
                return m[0]
            value = replacement(m) if callable(replacement) else m.expand(replacement)
            if value != m[0]:
                counts[rule] += 1
                if events is not None:
                    events.append((rule, m[0], value, text[max(0,m.start()-25):m.end()+60]))
            return value
        text = re.sub(pattern, replace, text)

    for before, after in REVIEWED_FRAGMENTS.items():
        sub('reviewed_fragment', re.escape(before), lambda m, value=after: value)

    def title_open(m):
        opening = m[0][:len(m[0])-len(m[1])]
        # ((書名》卷一) can contain an outer citation parenthesis plus a
        # damaged book opener. Preserve that parenthesis when the reference
        # has an otherwise unmatched closing parenthesis. Triple openers
        # already leave their outer parenthesis outside this match.
        keep_outer = False
        if opening.startswith('(') and not (m.start() and text[m.start()-1] == '('):
            tail = text[m.end():]
            if tail.startswith(('))', '>>', ')>', '>)')):
                tail = tail[2:]
            elif tail.startswith('》'):
                tail = tail[1:]
            tail = re.split('[。\n]', tail, maxsplit=1)[0]
            depth = 0
            for ch in tail:
                if ch == '(':
                    depth += 1
                elif ch == ')':
                    if depth == 0:
                        keep_outer = True
                        break
                    depth -= 1
        return ('(' if keep_outer else '') + '《' + m[1]

    # A doubled OCR glyph denotes a title mark. An outer citation parenthesis
    # remains outside the match: (<<書名》 -> (《書名》, (((書名》 -> (《書名》.
    sub('title_open_double', rf'(?:<<|<\(|\(<|\(\()({TITLE})(?=》|>>|\)\)|\)>|>\))', title_open)
    sub('title_open_single', rf'[<(]({TITLE})(?=》)', title_open)
    sub('title_close_double', rf'《({TITLE})(?:\)\)|>>|\)>|>\))', r'《\1》')
    sub('title_close_single', rf'《({TITLE})[)〉>]', r'《\1》')
    sub('title_open_slash_tilde', rf'[\\~]{{1,2}}([{HAN}][{HAN}·・]{{0,25}})》', r'《\1》')
    sub('title_mismatched_open', rf'[〈「]([{HAN}][{HAN}·・]{{0,25}})》', r'《\1》')
    sub('title_close_stroke', rf'《([{HAN}][{HAN}·・]{{0,30}})[卜~Yh3J](?=卷|第|關於|\(|\')', r'《\1》')
    sub('title_close_double_accent', rf'《([{HAN}][{HAN}·・]{{0,30}})(?:ìì|~ì)(?=\()', r'《\1》')
    sub('title_citation_fused_open', r'付出谷紀》', '(《出谷紀》')
    sub('title_parenthetical_angels', r'《上天[lft]天使》階級論》', '《上天(天使)階級論》')

    # These isolated glyphs are the common OCR readings of 「. A Latin word
    # (ratio, spiritus, etc.) cannot satisfy both boundaries of these rules.
    sub('quote_open_r_accent', rf'(?<![{LATIN}「『])[ríìï](?=\s*(?:[{HAN}「『]|\([{HAN}]|[-一]J))', '「')
    sub('quote_open_accent_latin', rf'(?<![{LATIN}])[íï](?=[A-Z][^「」\n]{{1,100}}(?:J|」))', '「')
    sub('quote_open_scan_cluster', rf'(?<![{LATIN}0-9])(?:\["{{1,2}}|1"{{1,2}}|[lI]"{{1,2}}|l\')(?=\s*[{HAN}「『])', '「')
    sub('quote_open_I', rf'(^|[\s:：,，;；。\(（\[\'」])I(?=[{HAN}][^「」\n]{{0,600}}(?:」|[Jj](?![{LATIN}])))', r'\1「')
    def unquoted(m):
        prefix = text[:m.end()-1]
        return prefix.count('「') + prefix.count('『') <= prefix.count('」') + prefix.count('』')
    def speech_boundary(m):
        if not unquoted(m):
            return False
        end = text.find('」', m.end())
        # A second damaged opener is evidence that the first stroke belongs
        # to a damaged word or list number, rather than the quotation.
        return not re.search(rf'(?<![{LATIN}])[ríïìI1f]', text[m.end():end])
    sub('quote_open_speech_stroke', rf'([:：]\s*)[fItli1](?=[{HAN}][^「」\n]{{0,600}}」)', r'\1「', speech_boundary)
    sub('quote_open_short_term', r'(^|[，、;；\s]|為|與|稱|是|或)(?:1|f|I)(?=(?:善|一|多|位格|本性|愛|發言|花|動物|存在|什麼|天主|人|唯獨)[^「」\n，。;；:：]{0,25}」)', r'\1「', speech_boundary)
    sub('quote_open_r_dash', rf'(?<![{LATIN}])r-(?=[{HAN}][^「」\n]{{0,600}}[J」])', '「')
    sub('quote_close_underscore_I', rf'([「『][^「」『』\n]{{1,600}})_I(?![{LATIN}])', lambda m: m[1] + ('』' if m[1][0] == '『' else '」'))

    # Resolve a closing OCR glyph only while an explicit opening mark is
    # active. In particular IJ (often a broken 則), j inside a word and Latin
    # initial J are not blanket substitutions.
    chars = list(text)
    stack = []
    for i, ch in enumerate(text):
        if ch in '「『':
            stack.append(ch)
        elif ch in '」』':
            if stack:
                stack.pop()
        elif stack and ch in 'Jjy':
            before = text[i-1] if i else ''
            after = text[i+1] if i+1 < len(text) else ''
            opening = max(text.rfind('「', 0, i), text.rfind('『', 0, i))
            if not text[opening+1:i].strip() or (after and after in '」』'):
                continue
            if ch == 'J' and re.match(r'J\.\s*[A-Z]', text[i:]):
                continue
            if before and not re.match(rf'[{LATIN}]', before) and not re.match(rf'[{LATIN}]', after):
                # j embedded in a damaged Chinese character (褻j費, 前j我)
                # is not punctuation. Uppercase J and y are unambiguous at
                # an active quotation boundary; j needs a boundary cue.
                if ch == 'j' and re.match(rf'[{HAN}]', after):
                    opening = max(text.rfind('「', 0, i), text.rfind('『', 0, i))
                    content = text[opening+1:i]
                    next_mark = re.search('[「」『』]', text[i+1:])
                    short_term = bool(re.fullmatch(rf'[{HAN}]{{1,32}}', content))
                    sentence_end = before in '。.!?！？'
                    if (not short_term and not sentence_end) or (next_mark and next_mark[0] in '」』'):
                        continue
                chars[i] = '』' if stack.pop() == '『' else '」'
                counts['quote_close_' + ch] += 1
    return ''.join(chars)


def repair(text, counts=None, events=None):
    for _ in range(5):
        fixed = repair_pass(text, counts, events)
        if fixed == text:
            return fixed
        text = fixed
    raise ValueError('Punctuation repair did not stabilise')


def transform(obj, counts, changes, path=()):
    if isinstance(obj, dict):
        for key, value in obj.items():
            if isinstance(value, str) and (key == 'zh' or key.endswith('_zh')):
                fixed = repair(value, counts)
                if fixed != value:
                    changes.append('/'.join(map(str, path + (key,))))
                    obj[key] = fixed
            else:
                transform(value, counts, changes, path + (key,))
    elif isinstance(obj, list):
        for i, value in enumerate(obj):
            transform(value, counts, changes, path + (i,))


def encoded(obj):
    return json.dumps(obj, ensure_ascii=False, separators=(',', ':'))


def protected(value):
    if isinstance(value, dict):
        return {k:protected(v) for k,v in value.items()
                if k not in ('zh', 'release', 'punctuation_revision') and not k.endswith('_zh')}
    if isinstance(value, list):
        return [protected(v) for v in value]
    return value


def pending_marks(obj, filename):
    """Return review leads, not a claim that every unmatched mark is wrong."""
    leads = []
    def visit(value, path=()):
        if isinstance(value, dict):
            for key, item in value.items():
                if isinstance(item, str) and (key == 'zh' or key.endswith('_zh')):
                    for opening, closing, label in [('《', '》', 'title'), ('「', '」', 'quotation')]:
                        stack = []
                        for pos, ch in enumerate(item):
                            if ch == opening:
                                stack.append(pos)
                            elif ch == closing:
                                if stack:
                                    stack.pop()
                                else:
                                    leads.append({'file': filename, 'field': '/'.join(map(str,path+(key,))), 'kind': label+'-closing', 'context': item[max(0,pos-30):pos+55]})
                        for pos in stack:
                            leads.append({'file': filename, 'field': '/'.join(map(str,path+(key,))), 'kind': label+'-opening', 'context': item[max(0,pos-20):pos+85]})
                else:
                    visit(item, path+(key,))
        elif isinstance(value, list):
            for i, item in enumerate(value):
                visit(item, path+(i,))
    visit(obj)
    return leads


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    root = args.root.resolve()
    report = {'files': {}, 'rules': collections.Counter()}
    protected_data = {}
    for file in sorted((root / 'data/summa').rglob('*.json')):
        obj = json.loads(file.read_text(encoding='utf8'))
        protected_data[file.relative_to(root).as_posix()] = protected(obj)
        counts, changes = collections.Counter(), []
        transform(obj, counts, changes)
        if changes:
            name = file.relative_to(root).as_posix()
            report['files'][name] = {'fields': len(changes), 'repairs': sum(counts.values())}
            report['rules'].update(counts)
            if args.write:
                file.write_text(encoded(obj) + '\n', encoding='utf8', newline='\n')
    file = root / 'summa.html'
    html = file.read_text(encoding='utf8')
    match = FALLBACK.search(html)
    obj = json.loads(match[2])
    protected_data['summa-fallback'] = protected(obj)
    report['protected_data_sha256'] = hashlib.sha256(json.dumps(protected_data,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode('utf8')).hexdigest()
    counts, changes = collections.Counter(), []
    transform(obj, counts, changes)
    if changes:
        report['files']['summa.html'] = {'fields': len(changes), 'repairs': sum(counts.values())}
        report['rules'].update(counts)
        if args.write:
            html = html[:match.start(2)] + encoded(obj).replace('<', '\\u003c') + html[match.end(2):]
            file.write_text(html, encoding='utf8', newline='\n')
    report['changed_files'] = len(report['files'])
    report['changed_fields'] = sum(x['fields'] for x in report['files'].values())
    report['repairs'] = sum(report['rules'].values())
    print(json.dumps({k:v for k,v in report.items() if k!='files'}, ensure_ascii=False, indent=2))
    if args.write and report['repairs']:
        catalog_file = root / 'data/summa/catalog.json'
        catalog = json.loads(catalog_file.read_text(encoding='utf8'))
        digest = hashlib.sha256()
        for part in catalog['parts']:
            for question in part['questions']:
                digest.update((root / f'data/summa/{part["id"]}/q{question["number"]}.json').read_bytes())
        digest.update(encoded([obj['general_prologue'], obj['part_prologues']]).encode('utf8'))
        release = 'punctuation-20261017-' + digest.hexdigest()[:12]
        report['previous_release'] = catalog['release']
        report['release'] = release
        revision = {'release': release, 'date': '2026-10-17', 'repairs': report['repairs'],
                    'scope': '中文引號與書名號OCR專項修復（含目錄與內置文本）',
                    'policy': '依可辨識的標點形狀與上下文修復；嚴重亂碼留待原頁核對。',
                    'latin_preserved': True}
        catalog['release'] = release
        catalog['punctuation_revision'] = revision
        catalog_file.write_text(encoded(catalog)+'\n', encoding='utf8', newline='\n')
        proofreading_file = root / 'data/summa/proofreading.json'
        proofreading = json.loads(proofreading_file.read_text(encoding='utf8'))
        proofreading['release'] = release
        proofreading['punctuation_revision'] = revision
        proofreading_file.write_text(encoded(proofreading)+'\n', encoding='utf8', newline='\n')
        obj['release'] = release
        obj['punctuation_revision'] = revision
        match = FALLBACK.search(html)
        html = html[:match.start(2)] + encoded(obj).replace('<', '\\u003c') + html[match.end(2):]
        file.write_text(html, encoding='utf8', newline='\n')
        pending = []
        for question_file in sorted((root/'data/summa').glob('*/q*.json')):
            pending.extend(pending_marks(json.loads(question_file.read_text(encoding='utf8')), question_file.relative_to(root).as_posix()))
        pending.extend(pending_marks({k:obj[k] for k in ['general_prologue','part_prologues']}, 'summa.html'))
        report['pending_mark_candidates'] = len(pending)
        (root / 'docs/summa/punctuation-pending.json').write_text(json.dumps({'note': '標點未配對的人工複核線索；包含原有嚴重亂碼與可能跨段引文，不等同於已確認錯誤。', 'candidates': pending}, ensure_ascii=False, indent=2)+'\n', encoding='utf8')
        (root / 'docs/summa/punctuation-repairs.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n', encoding='utf8')


if __name__ == '__main__':
    main()
