"""Regression checks for OCR punctuation repair and protected reader data."""
import hashlib
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from repair_summa_punctuation import repair, FALLBACK


def protected(value):
    if isinstance(value, dict):
        return {k:protected(v) for k,v in value.items()
                if k not in ('zh', 'release', 'punctuation_revision') and not k.endswith('_zh')}
    if isinstance(value, list):
        return [protected(v) for v in value]
    return value


def protected_digest(files, fallback):
    payload = {name:protected(obj) for name,obj in sorted(files.items())}
    payload['summa-fallback'] = protected(fallback)
    return hashlib.sha256(json.dumps(payload,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode('utf8')).hexdigest()


class PunctuationTests(unittest.TestCase):
    def test_reviewed_ocr_shapes(self):
        cases = {
            'r動物J': '「動物」',
            'r動物j': '「動物」',
            '「動物j是類名。': '「動物」是類名。',
            'í動物J': '「動物」',
            'ï動物」': '「動物」',
            '說: I動物J': '說: 「動物」',
            '說: 1動物」。': '說: 「動物」。',
            '說: ["動物J': '說: 「動物」',
            '說: 1"動物J': '說: 「動物」',
            '「動物_I': '「動物」',
            '《基本教理手冊))': '《基本教理手冊》',
            '《基本教理手冊>>': '《基本教理手冊》',
            '(<<物理學》卷三)': '(《物理學》卷三)',
            '(((物理學》卷三)': '(《物理學》卷三)',
            '((創世紀》第一章20節)': '(《創世紀》第一章20節)',
            '(<創世紀》第一章20節)': '(《創世紀》第一章20節)',
            '((基本教理手冊))': '《基本教理手冊》',
            '<(物理學》': '《物理學》',
            '《上天(天使)階級論>>': '《上天(天使)階級論》',
            '《信經「不拘誰」))': '《信經「不拘誰」》',
            '付出谷紀》第十六章)': '(《出谷紀》第十六章)',
            '「外引『內引J結束J': '「外引『內引』結束」',
        }
        for before,after in cases.items():
            with self.subTest(before=before):
                self.assertEqual(repair(before),after)
                self.assertEqual(repair(after),after)

    def test_preserves_ordinary_text(self):
        cases = [
            'ratio, spiritus, caritas, alícuí; J. N. D. Kelly',
            'I q. 1 a. 1; III; r = 2; 第1章; 貝IJ如此; 褻j費',
            '《基本教理手冊》(Enchiridion)與(自然的(或本性的)愛)',
            '「J. N. D. Kelly」與「r值」',
            '「從今而後，是有福的!的確，聖神說。」',
            '「我的百姓啊j那些稱你有福的，欺騙了你。」',
            '「褻j賈比發虛誓更壞。」',
            '1自多祿當然有人的本性，重點在這rj固」人。',
            '(f果祿)京徒說: 1-可朽壞的不能承受不可朽壞的」。',
            '「外引『內引』結束」',
        ]
        for text in cases:
            with self.subTest(text=text):
                self.assertEqual(repair(text),text)

    def test_published_corpus_and_fallback(self):
        files = {f.relative_to(ROOT).as_posix():json.loads(f.read_text(encoding='utf8'))
                 for f in (ROOT/'data/summa').rglob('*.json')}
        fallback = json.loads(FALLBACK.search((ROOT/'summa.html').read_text(encoding='utf8'))[2])
        catalog = files['data/summa/catalog.json']
        report = json.loads((ROOT/'docs/summa/punctuation-repairs.json').read_text(encoding='utf8'))
        self.assertEqual(protected_digest(files,fallback),report['protected_data_sha256'])
        questions = [files[f'data/summa/{part["id"]}/q{q["number"]}.json']
                     for part in catalog['parts'] for q in part['questions']]
        self.assertEqual(len(questions),613)
        self.assertEqual(sum(len(q['articles']) for q in questions),3125)
        self.assertEqual(sum(len(a['rows']) for q in questions for a in q['articles']),39507)
        self.assertEqual(fallback['question'],files['data/summa/I/q1.json'])
        self.assertEqual(fallback['release'],catalog['release'])
        self.assertEqual(files['data/summa/proofreading.json']['release'],catalog['release'])
        def visit(obj):
            if isinstance(obj,dict):
                for k,v in obj.items():
                    if isinstance(v,str) and (k=='zh' or k.endswith('_zh')):
                        self.assertEqual(repair(v),v)
                    else:
                        visit(v)
            elif isinstance(obj,list):
                for v in obj:
                    visit(v)
        for obj in files.values():
            visit(obj)
        visit(fallback)
        corpus_text = json.dumps(questions,ensure_ascii=False)
        self.assertNotIn('《基本教理手冊))',corpus_text)
        self.assertNotIn('《基本教理手冊>>',corpus_text)
        self.assertNotIn('r動物',corpus_text)


if __name__ == '__main__':
    unittest.main()
