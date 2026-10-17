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
   if w['id']=='parmenides':continue # Checked against the complete TEI below.
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
  self.assertEqual(count,57994)
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
    text=' '.join(z.read('OEBPS/Text/'+name).decode('utf-8') for name in w.get('germanFiles',[w['germanFile']]))
    text=re.sub(r'\s+','',html.unescape(re.sub('<[^>]+>','',text)))
    text=re.sub(r'\(\d{1,3}\)','',text) # Editorial page markers may split a sentence.
    for page in self.pages[w['id']]:
     self.assertTrue(page['german'],page['page'])
     for paragraph in page['german']:self.assertTrue(re.sub(r'\s+','',paragraph) in text,f'{w["id"]} German page {page["page"]}: {paragraph[:100]}')
     for u in page['units']:
      quote=u['reading']['de']
      self.assertTrue(re.search(r'[A-Za-zÄÖÜäöüß]',quote))
      self.assertTrue(re.sub(r'\s+','',quote) in text,f'{w["id"]} German unit {u["id"]}: {quote[:100]}')
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
  self.assertEqual(w['range'],'216a–242b')
  self.assertNotIn('status',w)
  self.assertIn('deshalb also gehe nur dreist zu.',self.pages['sophist'][-1]['units'][-1]['reading']['de'])
  self.assertNotIn('Jeder scheint',self.pages['sophist'][-1]['units'][-1]['reading']['de'])
 def test_reading_notes_have_only_three_display_fields(self):
  for work,pages in self.pages.items():
   for page in pages:
    for u in page['units']:
     self.assertEqual(set(u['notes']),{'中','结构'})
     for key in ['zh','de','structure']:self.assertTrue(u['reading'][key].strip(),(work,u['id'],key))
     self.assertEqual(u['reading']['zh'],u['notes']['中'])
     self.assertEqual(u['reading']['structure'],u['notes']['结构'])
     self.assertNotRegex(u['reading']['structure'],r'主语为.*；谓语：|锁死|精妙|经典预提|句法与风格')
 def test_first_philebus_german_sentences_are_distinct(self):
  a,b,c=self.pages['philebus'][0]['units'][:3]
  self.assertTrue(a['reading']['de'].endswith('gesprochen sein.'))
  self.assertEqual(b['reading']['de'],'Wollen wir sie uns beide noch einmal wiederholen?')
  self.assertEqual(c['reading']['de'],'Protarchos: Allerdings.')
 def test_word_panel_has_no_repeated_sentence_notes(self):
  script=(ROOT/'assets/classics.js').read_text(encoding='utf-8')
  self.assertNotIn('showContext',script)
  self.assertNotIn('panel-context',script)
  self.assertNotIn('原精读稿',script)
  editor=(ROOT/'assets/classics-editor.js').read_text(encoding='utf-8')
  for label in ['中文译文','施莱尔马赫译文','结构分析']:self.assertIn(label,editor)
 def test_complete_parmenides_matches_canonical_greek(self):
  import xml.etree.ElementTree as ET
  tree=ET.parse(ROOT/'tools/parmenides-source.xml');ns={'t':'http://www.tei-c.org/ns/1.0'}
  def text(e):
   out=[e.text or '']
   for child in e:
    if child.tag.rsplit('}',1)[-1] not in ('del','note'):out.append(text(child))
    out.append(child.tail or '')
   return ''.join(out)
  units=[u for p in self.pages['parmenides'] for u in p['units']]
  self.assertEqual(len(units),1369);self.assertEqual([u['id'] for u in units],list(range(1,1370)))
  self.assertEqual(units[0]['ref'],'126a');self.assertEqual(units[-1]['ref'],'166c')
  self.assertEqual(re.sub(r'\s+','',''.join(u['greek'] for u in units)),re.sub(r'\s+','',text(tree.find('.//t:body',ns))))
  self.assertEqual(units[-1]['reading']['de'],'Vollkommen wahr.')
  for u in units:self.assertEqual(''.join(u['tokens']),u['greek'])
 def test_parmenides_uses_supplied_chinese_notes(self):
  source=Path(r'C:\Users\Haowen_wei\Desktop\Parmenides.txt')
  if not source.exists():self.skipTest('Reference TXT belongs to the library owner')
  text=re.sub(r'\s+',' ',source.read_text(encoding='utf-8-sig'))
  units=[u for p in self.pages['parmenides'] for u in p['units']]
  for u in units[:1235]:self.assertIn(re.sub(r'\s+',' ',u['reading']['zh']),text)
 def test_parmenides_inflected_forms_and_corrections(self):
  self.assertTrue(any(a['lemma']=='ἀφικνέομαι' and a['tense']=='aorist' and a['person']=='1st' and a['number']=='plural' for a in self.analyses('parmenides','ἀφικόμεθα')))
  self.assertEqual([(a['lemma'],a['pos'],a['case']) for a in self.analyses('parmenides','Ἰβυκείου')],[('Ἰβύκειος','adjective','genitive')])
  self.assertTrue(all(a['lemma']=='ἔνειμι' and a['mood']=='optative' for a in self.analyses('parmenides','ἐνείη')))
 def test_owner_edits_survive_rebuilding_and_do_not_cross_greek(self):
  import tempfile
  spec=importlib.util.spec_from_file_location('owner_notes',ROOT/'tools/owner_notes.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
  u=json.loads(json.dumps(self.pages['parmenides'][0]['units'][0]));u['reading'].update(zh='馆主保存的译文',structure='馆主保存的说明',ownerEdited=True)
  with tempfile.TemporaryDirectory(prefix='classics-owner-',dir=PROJECT/'tmp') as folder:
   self.assertTrue(Path(folder).resolve().is_relative_to((PROJECT/'tmp').resolve()))
   Path(folder,'126.json').write_text(json.dumps({'units':[u]}),encoding='utf-8')
   saved=module.read_owner_notes(Path(folder))
   rebuilt=json.loads(json.dumps(self.pages['parmenides'][0]['units'][0]));module.restore_owner_notes(rebuilt,saved)
   self.assertEqual(rebuilt['reading']['zh'],'馆主保存的译文');self.assertTrue(rebuilt['reading']['ownerEdited'])
   changed=json.loads(json.dumps(self.pages['parmenides'][0]['units'][0]));changed['greek']+='ἕν';module.restore_owner_notes(changed,saved)
   self.assertNotIn('ownerEdited',changed['reading'])
if __name__=='__main__':unittest.main()
