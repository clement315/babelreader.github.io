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
   if w['id'] not in expected:continue # Later additions are checked against complete TEI below.
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
  self.assertEqual(count,124372)
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
      if u['reading'].get('deStatus')=='not-in-source':
       self.assertEqual(w['id'],'alcibiades1');self.assertIn(u['id'],[391,407,408,792,793,1001,1002,1003,1004]);self.assertEqual(quote,'');continue
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
     for key in ['zh','de','structure']:
      if key=='de' and u['reading'].get('deStatus')=='not-in-source':self.assertTrue(u['reading']['deNote']);continue
      self.assertTrue(u['reading'][key].strip(),(work,u['id'],key))
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
 def test_complete_additions_match_requested_canonical_editions(self):
  import xml.etree.ElementTree as ET
  for slug,count,first,last in [('alcibiades1',1103,'103a','135e'),('apology',345,'17a','42a'),('alcibiades2',257,'138a','151c'),('gorgias',1720,'447a','527e'),('statesman',898,'257a','311c')]:
   source=ROOT/f'tools/{slug}-source.xml';tree=ET.parse(source);body=tree.find('.//{http://www.tei-c.org/ns/1.0}body')
   for parent in list(body.iter()):
    for child in list(parent):
     if child.tag.rsplit('}',1)[-1] in ('del','note','head','label','bibl'):
      child.text='';child[:]=[]
   original=re.sub(r'\s+','',''.join(body.itertext())).replace('>','')
   if slug=='apology':original=original.replace('ττίἄξιός','τίἄξιός').replace('ἐμαυτὸνῷὄντι','ἐμαυτὸντῷὄντι')
   units=[u for p in self.pages[slug] for u in p['units']]
   self.assertEqual(len(units),count);self.assertEqual([u['id'] for u in units],list(range(1,count+1)))
   self.assertEqual(units[0]['ref'],first);self.assertEqual(units[-1]['ref'],last)
   self.assertEqual(re.sub(r'\s+','',''.join(u['greek'] for u in units)),original)
   self.assertEqual(hashlib.sha256(source.read_bytes()).hexdigest(),next(w for w in self.catalog['works'] if w['id']==slug)['greekSourceSha256'])
   for u in units:self.assertEqual(''.join(u['tokens']),u['greek'])
 def test_additions_use_uploaded_chinese_and_documented_edits(self):
  edits=load(ROOT/'tools/additional-classics-edits.json')
  for slug,filename in [('alcibiades1','Acibiades 1.txt'),('apology','Apology.txt'),('alcibiades2','Alcibiades 2.txt')]:
   path=Path(r'C:\Users\Haowen_wei\Desktop')/filename
   if not path.exists():continue
   source=re.sub(r'\s+',' ',path.read_text(encoding='utf-8-sig'))
   for page in self.pages[slug]:
    for u in page['units']:
     expected=edits.get(f'{slug}:{u["id"]}',{}).get('zh')
     if expected:self.assertEqual(u['reading']['zh'],expected)
     else:self.assertIn(re.sub(r'\s+',' ',u['reading']['zh']),source)
 def test_additions_german_boundaries_and_explicit_omissions(self):
  units={u['id']:u for p in self.pages['alcibiades1'] for u in p['units']}
  self.assertTrue(units[1]['reading']['de'].startswith('Sokrates: O Sohn des Kleinias'))
  self.assertIn('Gutes.',units[389]['reading']['de'])
  self.assertIn('Welches von beiden',units[388]['reading']['de'])
  self.assertIn('Stärke der Stadt',units[1103]['reading']['de'])
  missing=[u['id'] for u in units.values() if u['reading'].get('deStatus')=='not-in-source']
  self.assertEqual(missing,[391,407,408,792,793,1001,1002,1003,1004])
  apology={u['id']:u for p in self.pages['apology'] for u in p['units']}
  self.assertTrue(apology[342]['reading']['de'].endswith('Das verdient an ihnen getadelt zu werden.'))
  self.assertTrue(apology[343]['reading']['de'].startswith('Soviel jedoch bitte ich'))
  self.assertIn('außer nur Gott.',apology[345]['reading']['de'])
  self.assertEqual(self.pages['apology'][-1]['germanSource']['page'],'41')
 def test_added_word_morphology_and_chinese(self):
  for work,word,lemma,case,gender in [('alcibiades1','Ἀλκιβιάδη','Ἀλκιβιάδης','vocative','masculine'),('alcibiades1','Ζωροάστρου','Ζωροάστρης','genitive','masculine'),('alcibiades1','Λαμπιδώ','Λαμπιδώ','accusative','feminine'),('apology','Θεοζοτίδου','Θεοζοτίδης','genitive','masculine')]:
   aa=self.analyses(work,word);self.assertTrue(any(a['lemma']==lemma and a['case']==case and a['gender']==gender and a['number']=='singular' for a in aa))
  self.assertTrue(any(a['lemma']=='ἐπιλανθάνομαι' and a['tense']=='aorist' and a['person']=='1st' for a in self.analyses('apology','ἐπελαθόμην')))
  self.assertTrue(any(a['lemma']=='πάσχω' and a['tense']=='perfect' and a['number']=='plural' for a in self.analyses('apology','πεπόνθατε')))
  a=self.analyses('alcibiades1','Ἐρχίασιν');self.assertEqual(a[0]['pos'],'adverb');self.assertFalse(a[0].get('case'))
  for slug in ['alcibiades1','apology','alcibiades2']:
   for page in self.pages[slug]:
    for u in page['units']:
     for key in u['analyses'].values():self.assertTrue(any(a['zh'] for a in page['analyses'][key]),(slug,u['id']))
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
 def test_alcibiades2_german_limits_and_unmarked_page(self):
  pages=self.pages['alcibiades2'];units=[u for p in pages for u in p['units']]
  self.assertEqual(units[0]['reading']['de'],'Sokrates: Gehst du etwa zu dem Gotte um zu beten, o Alkibiades?')
  self.assertEqual(units[1]['reading']['de'],'Alkibiades: Allerdings, Sokrates.')
  self.assertTrue(units[-1]['reading']['de'].endswith('unter deinen Liebhabern.'))
  self.assertEqual(next(p for p in pages if p['page']=='147')['germanSource']['page'],'146')
  self.assertTrue(units[170]['greek'].startswith('—ναί.'))
  self.assertIn('...',units[183]['greek'])
 def test_alcibiades2_contextual_participles_and_verbs(self):
  page=next(p for p in self.pages['alcibiades2'] if p['page']=='144')
  unit=next(u for u in page['units'] if u['id']==143)
  index=unit['tokens'].index('ἔχουσιν');aa=page['analyses'][unit['analyses'][str(index)]]
  self.assertTrue(all(a['pos']=='participle' and a['case']=='dative' and a['number']=='plural' for a in aa))
  a=self.analyses('alcibiades2','φρονήσει')
  self.assertTrue(all(x['lemma']=='φρόνησις' and x['pos']=='noun' and x['case']=='dative' for x in a))
  a=self.analyses('alcibiades2','περιθήσω')
  self.assertTrue(all(x['lemma']=='περιτίθημι' and x['tense']=='future' and x['person']=='1st' for x in a))
  self.assertTrue(all(a['pos']=='conjunction' for a in self.analyses('alcibiades2','ἤπερ')))
 def test_gorgias_full_range_and_uploaded_chinese(self):
  units=[u for p in self.pages['gorgias'] for u in p['units']]
  self.assertEqual(len(self.pages['gorgias']),81)
  source=PROJECT/'output/gorgias/Gorgias_447a-461b_逐句精读_阶段稿.txt'
  if source.exists():
   text=re.sub(r'\s+',' ',source.read_text(encoding='utf-8-sig'))
   for u in units[:334]:self.assertIn(re.sub(r'\s+',' ',u['reading']['zh']),text)
  self.assertEqual(units[334]['ref'],'461b')
  self.assertTrue(units[-1]['reading']['zh'].endswith('卡利克勒斯，那条路毫无价值。'))
  meta=next(w for w in self.catalog['works'] if w['id']=='gorgias')
  self.assertTrue(meta['source'].endswith('tlg023/'))
  self.assertEqual(meta['words'],26247)
  for p in self.pages['gorgias']:
   for u in p['units']:
    for key in u['analyses'].values():self.assertTrue(any(a['zh'] for a in p['analyses'][key]),u['id'])
 def test_gorgias_original_german_boundaries_and_shared_compound_sentences(self):
  units={u['id']:u for p in self.pages['gorgias'] for u in p['units']}
  self.assertEqual(units[1]['reading']['de'],'Kallikles: Zum Kriege und zur Schlacht, heißt es, o Sokrates, muß man so zurecht kommen.')
  self.assertTrue(units[2]['reading']['de'].startswith('Sokrates: Also sind wir wohl'))
  self.assertTrue(units[890]['reading']['de'].startswith('Entweder also,'))
  self.assertTrue(units[1678]['reading']['de'].startswith('Wie also Homeros'))
  self.assertEqual(units[1716]['reading']['de'],units[1717]['reading']['de'])
  self.assertIn('alle Schmeichelei',units[1715]['reading']['de'])
  self.assertTrue(units[1720]['reading']['de'].endswith('nichts wert, o Kallikles.'))
  self.assertIn('Seligen',units[1679]['reading']['de'])
  self.assertIn('必正义、虔敬',units[1437]['reading']['zh'])
 def test_gorgias_morphology_and_poetry_word_separators(self):
  self.assertTrue(any(a['lemma']=='Ἡρακλῆς' and a['case']=='genitive' for a in self.analyses('gorgias','Ἡρακλέος')))
  self.assertTrue(all(a['lemma']=='σκεῦος' and a['pos']=='noun' and a['gender']=='neuter' for a in self.analyses('gorgias','σκεύους')))
  self.assertTrue(all(a['lemma']=='σιδήρεος' and a['pos']=='adjective' for a in self.analyses('gorgias','σιδηροῖς')))
  units={u['id']:u for p in self.pages['gorgias'] for u in p['units']}
  self.assertIn('βασιλεὺς θνατῶν',units[910]['greek'])
  self.assertEqual(units[1433]['speaker'],'苏格拉底')
  self.assertEqual(units[1434]['speaker'],'苏格拉底')
 def test_statesman_complete_editorial_readings_and_word_coverage(self):
  pages=self.pages['statesman'];units=[u for p in pages for u in p['units']]
  self.assertEqual(len(pages),55)
  meta=next(w for w in self.catalog['works'] if w['id']=='statesman')
  self.assertEqual(meta['words'],16953);self.assertTrue(meta['source'].endswith('tlg008/'))
  self.assertEqual(meta['chineseGlossCoverage'],1.0)
  self.assertEqual(meta['morphologyCoverage'],1.0)
  report=load(ROOT/'docs/statesman-import-report.json')
  self.assertEqual(report['editorialChineseUnits'],898)
  self.assertEqual(report['sourceTurns'],891);self.assertEqual(report['germanTurns'],891)
  self.assertEqual(report['speakerLabelVariant']['id'],898)
  self.assertIn('编',units[-2]['reading']['zh'])
  for page in pages:
   for u in page['units']:
    self.assertRegex(u['reading']['zh'],r'[\u4e00-\u9fff]')
    for key in u['analyses'].values():self.assertTrue(any(a['zh'] for a in page['analyses'][key]),u['id'])
 def test_statesman_german_boundaries_and_final_speaker_variant(self):
  units={u['id']:u for p in self.pages['statesman'] for u in p['units']}
  self.assertTrue(units[1]['reading']['de'].startswith('Sokrates: Wahrlich viel Dank'))
  shared='Nämlich die vor Kleinheit fast schon verschwindenden'
  self.assertIn(shared,units[300]['reading']['de']);self.assertTrue(units[301]['reading']['de'].startswith(shared))
  self.assertTrue(units[660]['reading']['de'].endswith('Gesetze?'))
  self.assertTrue(units[661]['reading']['de'].startswith(units[660]['reading']['de']))
  self.assertEqual(units[898]['speaker'],'青年苏格拉底')
  self.assertTrue(units[898]['reading']['de'].startswith('Sokrates: Vortrefflich'))
  self.assertTrue(units[898]['reading']['de'].endswith('Staatsmann dargestellt.'))
 def test_statesman_rare_forms_and_contextual_morphology(self):
  a=self.analyses('statesman','συνέθεμεν')
  self.assertTrue(all(x['lemma']=='συντίθημι' and x['tense']=='aorist' and x['number']=='plural' for x in a))
  a=self.analyses('statesman','ὑπέθεσαν')
  self.assertTrue(all(x['lemma']=='ὑποτίθημι' and x['person']=='3rd' for x in a))
  a=self.analyses('statesman','θρεφθεῖσί')
  self.assertTrue(all(x['pos']=='participle' and x['case']=='dative' and x['voice']=='passive' for x in a))
  a=self.analyses('statesman','ἁμῇ')
  self.assertTrue(all(x['pos']=='adverb' and not x.get('case') for x in a))
  a=self.analyses('statesman','ἀρνὸς')
  self.assertTrue(all(x['lemma']=='ἀρήν' and x['gender']=='feminine' and x['case']=='genitive' for x in a))
if __name__=='__main__':unittest.main()
