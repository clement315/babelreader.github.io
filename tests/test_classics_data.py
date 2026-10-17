"""Independent source-integrity and morphology regressions for the reader."""
import collections, hashlib, html, importlib.util, json, re, unittest, zipfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
PROJECT=ROOT.parent
EPUB=Path(r'C:\Users\Haowen_wei\Downloads\Gesammelte Werke (Platon) (z-library.sk, 1lib.sk, z-lib.sk).epub')
def load(p):return json.loads(p.read_text(encoding='utf-8'))
class ClassicsData(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.catalog=load(ROOT/'data/classics/catalog.json');cls.pape=load(ROOT/'data/classics/pape.json')
  cls.pages={}
  for w in cls.catalog['works']:
   cls.pages[w['id']]=[load(ROOT/f'data/classics/{w["id"]}/{p}.json') for p in w['pages']]
 def analyses(self,work,form):
  for p in self.pages[work]:
   for u in p['units']:
    for i,t in enumerate(u['tokens']):
     if t==form:return p['analyses'][u['analyses'][str(i)]]
  self.fail('word not found '+form)
 def test_exact_source_greek_and_chinese(self):
  expected={'symposium':('Symposium_172a-223d_逐句精读_合订稿_原稿待校.txt',698),'philebus':('Philebus_11a-67b_逐句精读.txt',1373),'sophist':('Sophist_216a-242b_逐句精读_阶段稿.txt',664)}
  for w in self.catalog['works']:
   filename,count=expected[w['id']];source=(PROJECT/'output'/w['id']/filename).read_text(encoding='utf-8-sig')
   normalized_source=re.sub(r'\s+',' ',source)
   for old,new in {'οὕτωawi':'οὕτως','θαυμαστὴruk':'θαυμαστή','ταῦταวั':'ταῦτα'}.items():normalized_source=normalized_source.replace(old,new)
   self.assertEqual(hashlib.sha256((PROJECT/'output'/w['id']/filename).read_bytes()).hexdigest(),w['notesSha256'])
   units=[u for p in self.pages[w['id']] for u in p['units']];self.assertEqual(len(units),count)
   for u in units:
    self.assertTrue(re.sub(r'\s+',' ',u['greek']) in normalized_source,f'{w["id"]} Greek unit {u["id"]}')
    self.assertEqual(''.join(u['tokens']),u['greek'])
    self.assertNotIn('德',u['notes'])
    if u['notes'].get('中'):self.assertTrue(re.sub(r'\s+',' ',u['notes']['中']) in normalized_source,f'{w["id"]} Chinese unit {u["id"]}')
 def test_every_greek_word_clicks_to_nonempty_candidates(self):
  count=0
  for pages in self.pages.values():
   for page in pages:
    for u in page['units']:
     for i,key in u['analyses'].items():
      self.assertTrue(u['tokens'][int(i)])
      self.assertTrue(page['analyses'][key]);count+=1
  self.assertEqual(count,42750)
 def test_noun_case_gender_number_and_gloss(self):
  a=self.analyses('philebus','λόγον')
  self.assertTrue(any(x['lemma']=='λόγος' and x['pos']=='noun' and x['case']=='accusative' and x['gender']=='masculine' and x['number']=='singular' for x in a))
  self.assertTrue(any('话语' in x['zh'] for x in a));self.assertFalse(any('谚语' in x['zh'] for x in a))
 def test_verb_and_participle_fields(self):
  self.assertTrue(all(a['lemma']=='δοκέω' and a['tense']=='present' and a['mood']=='indicative' for a in self.analyses('symposium','Δοκῶ')))
  self.assertTrue(any(a['pos']=='verb' and a['mood']=='imperative' and a['person']=='2nd' for a in self.analyses('philebus','ὅρα')))
  self.assertTrue(any(a['pos']=='participle' and a['case']=='nominative' for a in self.analyses('philebus','λεγόμενος')))
 def test_neuter_syncretism_not_lost(self):
  self.assertTrue(any('nominative' in a['case'] and 'accusative' in a['case'] for a in self.analyses('philebus','τὸ')))
 def test_proper_name_is_not_a_spurious_verb(self):
  a=self.analyses('philebus','Σώκρατες')
  self.assertEqual([(x['lemma'],x['pos'],x['case']) for x in a],[('Σωκράτης','proper_noun','vocative')])
 def test_elision_and_dual(self):
  self.assertTrue(any(a['lemma']=='παρά' for a in self.analyses('philebus','παρʼ')))
  self.assertTrue(any(a['number']=='dual' for a in self.analyses('philebus','γενοίσθην')))
 def test_german_is_literal_epub_source(self):
  if not EPUB.exists():self.skipTest('Source EPUB is local to the library owner')
  with zipfile.ZipFile(EPUB) as z:
   for w in self.catalog['works']:
    text=z.read('OEBPS/Text/'+w['germanFile']).decode('utf-8')
    text=re.sub(r'\s+','',html.unescape(re.sub('<[^>]+>','',text)))
    for page in self.pages[w['id']]:
     self.assertTrue(page['german'],page['page'])
     for paragraph in page['german']:self.assertTrue(re.sub(r'\s+','',paragraph) in text,f'{w["id"]} German page {page["page"]}: {paragraph[:100]}')
     for aa in page['analyses'].values():
      for a in aa:
       if a.get('deName'):self.assertIn(a['deName'],' '.join(page['german']))
  self.assertIn('Sieh also zu, Protarchos',self.pages['philebus'][0]['german'][0])
  self.assertTrue('Willst du, dass wir' not in json.dumps(self.pages,ensure_ascii=False))
 def test_pape_entries_are_source_excerpts(self):
  source=PROJECT/'tmp/classics-source/Pape.json'
  if not source.exists():self.skipTest('Pape source data is not checked into the website')
  lookup=collections.defaultdict(list)
  for item in load(source):
   text=re.sub(r'\s+',' ',html.unescape(re.sub('<[^>]*>',' ',item['d']))).strip()
   lookup[item['w']].append(text)
  for entries in self.pape.values():
   for item in entries:self.assertIn(item['text'],lookup[item['lemma']])
 def test_partial_sophist_boundary(self):
  w=next(w for w in self.catalog['works'] if w['id']=='sophist')
  self.assertEqual(w['pages'][-1],'242');self.assertEqual(self.pages['sophist'][-1]['units'][-1]['ref'],'242b')
  self.assertIn('阶段稿',w['status'])
if __name__=='__main__':unittest.main()
