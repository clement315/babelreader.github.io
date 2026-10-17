"""Import the complete Parmenides and preserve the supplied German quotations."""
from pathlib import Path
import argparse,collections,difflib,hashlib,html,json,re,sqlite3,unicodedata,zipfile,xml.etree.ElementTree as ET
from import_classics import Paragraphs,norm,plain,tokens,isgreek,morph_entry,note_candidates,corpus_words,dump,REPO
from owner_notes import read_owner_notes,restore_owner_notes

GERMAN_FILES=['part0005.xhtml','part0006.xhtml']

def german_pages(epub):
 pages=collections.defaultdict(list);active=False;page=None;finished=False
 with zipfile.ZipFile(epub) as z:
  for filename in GERMAN_FILES:
   parser=Paragraphs();parser.feed(z.read('OEBPS/Text/'+filename).decode('utf-8'))
   for tag,para in parser.blocks:
    if not active:
     if tag.startswith('h') and '(126)' in para and 'Parmenides' in para:active=True;page='126'
     continue
    if tag in ('h1','h2','h3'):finished=True;break
    if tag!='p':continue
    pieces=re.split(r'\((1[2-6]\d)\)',para)
    if pieces[0].strip():pages[page].append(pieces[0].strip())
    for i in range(1,len(pieces),2):
     page=pieces[i]
     if pieces[i+1].strip():pages[page].append(pieces[i+1].strip())
   if finished:break
 assert list(pages)==[str(p) for p in range(126,167)],list(pages)
 return dict(pages)

def import_work(resources,epub,spec=None):
 spec=spec or {};slug=spec.get('id','parmenides')
 records=json.loads((REPO/f'tools/{slug}-notes.json').read_text(encoding='utf-8'))
 source=ET.parse(REPO/f'tools/{slug}-source.xml')
 ns={'t':'http://www.tei-c.org/ns/1.0'}
 def greek_text(e):
  result=[e.text or '']
  for c in e:
   if c.tag.rsplit('}',1)[-1] not in ('del','note','head','label','bibl'):result.append(greek_text(c))
   result.append(c.tail or '')
  return ''.join(result)
 def compact(s):
  value=re.sub(r'\s+','',s).replace('>','')
  if slug=='apology':value=value.replace('ττίἄξιός','τίἄξιός').replace('ἐμαυτὸνῷὄντι','ἐμαυτὸντῷὄντι')
  return value
 assert compact(''.join(u['greek'] for u in records))==compact(greek_text(source.find('.//t:body',ns)))
 german=spec['germanLoader'](epub) if 'germanLoader' in spec else german_pages(epub)
 german_files=spec.get('germanFiles',GERMAN_FILES);german_all=compact(' '.join(' '.join(p) for p in german.values()))
 for u in records:assert compact(u['reading']['de']) in german_all,u['id']
 lexicon=collections.defaultdict(list)
 for item in json.loads((resources/'Pape.json').read_text(encoding='utf-8-sig')):
  lexicon[norm(item['w'])].append({'lemma':item['w'],'text':plain(item['d'])})
 glosses={}
 for name in ['classics-zh','classics-zh-extra','classics-zh-more','parmenides-zh','parmenides-zh-supplement',*spec.get('glossFiles',[]),f'{slug}-zh',f'{slug}-zh-supplement']:
  path=REPO/f'tools/{name}.json'
  if path.exists():glosses.update({norm(k):v for k,v in json.loads(path.read_text(encoding='utf-8')).items()})
 proper={'Παρμενίδης':'巴门尼德','Ζήνων':'芝诺','Κέφαλος':'刻法洛斯','Ἀδείμαντος':'阿得曼托斯','Γλαύκων':'格劳孔','Ἀντιφῶν':'安提丰','Πυθόδωρος':'皮托多罗斯','Πυριλάμπης':'皮里兰佩斯','Ἀριστοτέλης':'亚里士多德','Σωκράτης':'苏格拉底','Κλαζομεναί':'克拉佐迈奈','Μελίτη':'墨利忒','Κεραμεικός':'刻拉墨科斯','Παναθήναια':'泛雅典娜节'}
 proper.update(spec.get('proper',{}))
 glosses.update({norm(k):v for k,v in proper.items()})
 corpus=corpus_words(resources/spec.get('corpus','Plato (0059) - Parmenides (009).xml'),glosses,lexicon)
 # Reuse established word-class labels for common function words.
 classes=collections.defaultdict(collections.Counter)
 for work in ['symposium','philebus','sophist']:
  for p in (REPO/f'data/classics/{work}').glob('*.json'):
   if p.name=='catalog.json':continue
   for candidates in json.loads(p.read_text(encoding='utf-8'))['analyses'].values():
    for a in candidates:classes[a['lemma']][a['pos']]+=1
 posmap={k:v.most_common(1)[0][0] for k,v in classes.items()}
 posmap.update({k:'proper_noun' for k in proper})
 conn=sqlite3.connect(f'file:{(resources/"morph.db").as_posix()}?mode=ro',uri=True);conn.row_factory=sqlite3.Row
 def accent(s):return unicodedata.normalize('NFC',unicodedata.normalize('NFD',s.lower()).replace('\u0300','\u0301')).replace('ς','σ').translate(str.maketrans({'ʼ':"'",'᾽':"'",'’':"'"}))
 form_cache={}
 def lookup(word):
  if word in form_cache:return form_cache[word]
  key=norm(word)+("'" if word.endswith(("'",'ʼ','᾽','’')) else '')
  rows=[dict(x) for x in conn.execute('SELECT * FROM morphology WHERE form_normalized=?',(key,))]
  exact=[r for r in rows if accent(r['form'])==accent(word)];result=[]
  for r in exact or rows:
   lemma=re.sub(r'\d+$','',r['lemma']);pos=posmap.get(lemma,{'adv':'adverb','prep':'preposition','conj':'conjunction','exclam':'interjection','pron':'pronoun','adj':'adjective'}.get(r['pos'],r['pos']))
   if r['pos'] in ('verb','participle'):pos=r['pos']
   a=morph_entry(lemma,pos,r['morphology'],'accent' if exact else 'normalized',glosses,lexicon)
   for f,col in [('tense','tense'),('voice','voice'),('mood','mood'),('person','person'),('number','number'),('degree','degree')]:
    if not a.get(f) and r[col]:a[f]=r[col]
   result.append(a)
  form_cache[word]=result;return result
 by_page=collections.defaultdict(list);owner=read_owner_notes(REPO/f'data/classics/{slug}')
 for record in records:
  u={k:v for k,v in record.items() if k!='verbHints'}
  restore_owner_notes(u,owner)
  u['notes']={'中':u['reading']['zh'],'结构':u['reading']['structure']};u['tokens']=tokens(u['greek']);u['analyses']={}
  assert ''.join(u['tokens'])==u['greek']
  by_page[re.match(r'\d+',u['ref'])[0]].append(u)
 wordcount=known=zhcount=decount=contextcount=0;used=set();unknown=set()
 for page,units in by_page.items():
  positions=[(u,i,w) for u in units for i,w in enumerate(u['tokens']) if isgreek(w)]
  words=corpus.get(page,[]);matched={}
  for left,right,size in difflib.SequenceMatcher(None,[norm(w) for _,_,w in positions],[w[0] for w in words],autojunk=False).get_matching_blocks():
   for offset in range(size):matched[left+offset]=words[right+offset][1]
  pool={};signatures={}
  for offset,(u,i,w) in enumerate(positions):
   aa=(matched.get(offset) or [])+lookup(w)
   aa=note_candidates({'notes':{'动词':records[u['id']-1].get('verbHints','')}},w,aa)
   editorial={'Ἰβυκείου':('Ἰβύκειος','adjective','masc gen sg'),'ἐνείη':('ἔνειμι','verb','pres opt act 3rd sg'),'ἐνεῖναι':('ἔνειμι','verb','pres inf act'),'ἐνῇ':('ἔνειμι','verb','pres subj act 3rd sg'),'ἔκλεψε':('κλέπτω','verb','aor ind act 3rd sg'),'ὑποθησόμεθα':('ὑποτίθημι','verb','fut ind mid 1st pl'),'μεταθεῖς':('μετατίθημι','participle','aor part act masc nom sg'),'ἡσυχάζον':('ἡσυχάζω','participle','pres part act neut nom/voc/acc sg')}
   editorial.update(spec.get('morphology',{}))
   if w in editorial:
    lemma,pos,raw=editorial[w];aa=[morph_entry(lemma,pos,raw,'editorial',glosses,lexicon)]
   for a in aa:
    if a['lemma'] in proper:a['pos']='proper_noun'
    elif a['pos'] not in ('verb','participle'):a['pos']=posmap.get(a['lemma'],a['pos'])
    if not a.get('zh'):a['zh']=glosses.get(norm(a['lemma']),'')
    name={'Παρμενίδης':'Parmenides','Ζήνων':'Zenon','Κέφαλος':'Kephalos','Ἀδείμαντος':'Adeimantos','Γλαύκων':'Glaukon','Ἀντιφῶν':'Antiphon','Πυθόδωρος':'Pythodoros','Πυριλάμπης':'Pyrilampes','Ἀριστοτέλης':'Aristoteles','Σωκράτης':'Sokrates','Κλαζομεναί':'Klazomenai','Μελίτη':'Melite'}.get(a['lemma'])
    name=spec.get('germanNames',{}).get(a['lemma'],name)
    context=german.get(page,german[str(max(int(p) for p in german if int(p)<=int(page)))])
    if name and name in ' '.join(context):a['deName']=name
   names=[a for a in aa if a['pos']=='proper_noun' and a['lemma'] in proper]
   if names:aa=names
   aa=list({json.dumps({k:v for k,v in a.items() if k not in ('lookup','raw')},ensure_ascii=False,sort_keys=True):a for a in reversed(aa)}.values())
   sig=json.dumps(aa,ensure_ascii=False,sort_keys=True)
   if sig not in signatures:signatures[sig]=str(len(pool));pool[signatures[sig]]=aa
   u['analyses'][str(i)]=signatures[sig]
   wordcount+=1;known+=bool(aa);zhcount+=any(a.get('zh') for a in aa);decount+=any(a.get('de') or a.get('deName') for a in aa);contextcount+=bool(matched.get(offset))
   if not aa:unknown.add(w)
   used.update(a['de'] for a in aa if a.get('de'))
  source_page=page if page in german else str(max(int(p) for p in german if int(p)<=int(page)))
  dump(REPO/f'data/classics/{slug}/{page}.json',{'work':slug,'page':page,'units':units,'analyses':pool,'german':german[source_page],'germanSource':{'files':german_files,'page':source_page,'alignment':'句段摘录见units.reading'}})
 conn.close()
 metadata={'id':slug,'title':spec.get('title','巴门尼德篇'),'latin':spec.get('latin','Parmenides'),'greekTitle':spec.get('greekTitle','Παρμενίδης'),'range':spec.get('range','126a–166c'),'pages':list(by_page),'units':len(records),'words':wordcount,'source':spec.get('source','https://scaife.perseus.org/library/urn:cts:greekLit:tlg0059.tlg009/'),'germanTranslator':'Friedrich Daniel Ernst Schleiermacher','germanTitle':'Gesammelte Werke','germanEdition':spec.get('germanEdition','用户提供的EPUB；本篇标注Akademie Verlag Berlin 1985'),'germanFile':german_files[-1],'germanFiles':german_files,'morphologyCoverage':known/wordcount,'germanLexiconCoverage':decount/wordcount,'chineseGlossCoverage':zhcount/wordcount,'corpusAlignmentCoverage':contextcount/wordcount,'greekSourceSha256':hashlib.sha256((REPO/f'tools/{slug}-source.xml').read_bytes()).hexdigest()}
 dump(REPO/f'data/classics/{slug}/catalog.json',metadata)
 catalog=json.loads((REPO/'data/classics/catalog.json').read_text(encoding='utf-8'));catalog['works']=[w for w in catalog['works'] if w['id']!=slug]+[metadata];catalog['release']=max(catalog.get('release',''),spec.get('release','20261017-classics-3'));dump(REPO/'data/classics/catalog.json',catalog)
 pape=json.loads((REPO/'data/classics/pape.json').read_text(encoding='utf-8'));pape.update({k:lexicon[k] for k in used});dump(REPO/'data/classics/pape.json',pape)
 print(json.dumps({**metadata,'unknownForms':sorted(unknown)},ensure_ascii=False,indent=2))
 return {**metadata,'unknownForms':sorted(unknown)}

if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--resources',type=Path,default=REPO.parent/'tmp/classics-source');ap.add_argument('--german-epub',type=Path,required=True);args=ap.parse_args()
 import_work(args.resources,args.german_epub)
