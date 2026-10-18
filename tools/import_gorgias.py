"""Import Perseus Gorgias, editorial Chinese, and literal Schleiermacher.

German speaker turns are verified before sentence alignment. No translator
or generated German is used. Editorial Chinese is kept in gorgias-reading/.
"""
from pathlib import Path
import argparse,collections,difflib,functools,json,math,re,xml.etree.ElementTree as ET
from import_classics import REPO,corpus_words,dump,norm,parse_notes,plain,tokens,isgreek
from import_additional_classics import source_german,PROPER,GERMAN_NAMES
from import_parmenides import import_work
from simplify_classics import clean_structure,german_segments,words

SPEC={'id':'gorgias','title':'高尔吉亚篇','latin':'Gorgias','greekTitle':'Γοργίας','range':'447a–527e','start':447,'end':527,'germanFiles':['part0009.xhtml','part0010.xhtml'],'germanHeading':'Gorgias','germanEdition':'用户提供的EPUB；本篇标注Akademie Verlag Berlin 1985','corpus':'Plato (0059) - Gorgias (023).xml','source':'https://scaife.perseus.org/library/urn:cts:greekLit:tlg0059.tlg023/','release':'20261018-classics-6','glossFiles':['additional-classics-zh','alcibiades2-zh-supplement']}
SPEAKERS={'苏格拉底':'Sokrates','卡利克勒斯':'Kallikles','凯勒丰':'Chairephon','高尔吉亚':'Gorgias','波洛斯':'Polos'}
NAMES={'Γοργίας':('高尔吉亚','Gorgias'),'Πῶλος':('波洛斯','Polos'),'Καλλικλῆς':('卡利克勒斯','Kallikles'),'Καλλίκλης':('卡利克勒斯','Kallikles'),'Ἡρακλῆς':('赫拉克勒斯','Herakles'),'Ἀρχέλαος':('阿尔刻拉奥斯','Archelaos'),'Περδίκκας':('佩尔狄卡斯','Perdikkas'),'Ἀλκέτας':('阿尔刻塔斯','Alketas'),'Ἀλέξανδρος':('亚历山德罗斯','Alexandros'),'Κλεοπάτρα':('克娄巴特拉','Kleopatra'),'Νικίας':('尼基阿斯','Nikias'),'Νικήρατος':('尼刻拉托斯','Nikeratos'),'Ἀριστοκράτης':('阿里斯托克拉忒斯','Aristokrates'),'Σκελλίας':('斯刻利阿斯','Skellias'),'Ξέρξης':('薛西斯','Xerxes'),'Πίνδαρος':('品达','Pindaros'),'Γηρυόνης':('革律翁','Geryones'),'Ἀμφίων':('安菲翁','Amphion'),'Ζῆθος':('仄托斯','Zethos'),'Κίμων':('客蒙','Kimon'),'Μιλτιάδης':('米尔提亚德斯','Miltiades'),'Θεμιστοκλῆς':('忒弥斯托克勒斯','Themistokles'),'Κρόνος':('克洛诺斯','Kronos'),'Προμηθεύς':('普罗米修斯','Prometheus'),'Ποσειδῶν':('波塞冬','Poseidon'),'Πλούτων':('普鲁同','Pluton'),'Τάρταρος':('塔耳塔罗斯','Tartaros'),'Τάνταλος':('坦塔罗斯','Tantalos'),'Τιτυός':('提提俄斯','Tityos'),'Θερσίτης':('忒尔西忒斯','Thersites'),'Λυσίμαχος':('吕西马科斯','Lysimachos')}
NAMES.update({'Καλλικλέης':NAMES['Καλλικλῆς'],'Περικλέης':('伯里克利','Perikles'),'Πέρδικκος':NAMES['Περδίκκας'],'Περδίκκης':NAMES['Περδίκκας'],'Ἄλκετος':NAMES['Ἀλκέτας'],'Ἀλκέτης':NAMES['Ἀλκέτας'],'Κλεοπάτρη':NAMES['Κλεοπάτρα'],'Κλεινίης':('克莱尼亚斯','Kleinias'),'Κινησίης':('基涅西阿斯','Kinesias'),'Κινησίας':('基涅西阿斯','Kinesias'),'Ἄνδρων':('安德戎','Andron'),'Θεαρίων':('忒阿里翁','Thearion'),'Σάραμβος':('萨兰博斯','Sarambos'),'Ῥαδάμανθυς':('拉达曼提斯','Rhadamanthys')})
SPEC['glossFiles']+=['alcibiades1-zh','alcibiades2-zh','apology-zh']

def reviewed_german_boundaries(records):
 """Retain complete literal source sentences spanning Greek unit boundaries."""
 r={u['id']:u['reading'] for u in records}
 r[849]['de']+=' '+r[850]['de']
 text=r[890]['de'];cut=text.index('Entweder also,')
 r[889]['de']+=' '+text[:cut].strip();r[890]['de']=text[cut:]
 text=r[1678]['de'];cut=text.index('Wie also Homeros')
 r[1677]['de']+=' '+text[:cut].strip();r[1678]['de']=text[cut:]
 r[1715]['de']+=' '+r[1716]['de'];r[1716]['de']=r[1717]['de']
 r[1660]['de']+=' '+r[1661]['de']

def canonical_reading(path):
 root=ET.parse(path);body=root.find('.//{http://www.tei-c.org/ns/1.0}body');chars=[];refs=[];ref=''
 def append(s):
  for c in s:
   if c!='>':chars.append(c);refs.append(ref)
 def visit(e):
  nonlocal ref
  tag=e.tag.rsplit('}',1)[-1]
  if tag=='milestone' and re.fullmatch(r'\d+[a-e]',e.get('n','')):ref=e.get('n')
  if tag in ('l','lb'):append(' ')
  append(e.text or '')
  for child in e:
   if child.tag.rsplit('}',1)[-1] not in ('del','note','head','label','bibl'):visit(child)
   append(child.tail or '')
  if tag in ('l','lb'):append(' ')
 visit(body);raw=''.join(chars)
 return raw,refs,[i for i,c in enumerate(raw) if not c.isspace()]

def reading_units(folder,source):
 original=json.loads((folder/'sentences.json').read_text(encoding='utf-8'));raw,refs,positions=canonical_reading(source)
 compact=''.join(raw[i] for i in positions);cursor=0;result=[]
 for u in original:
  display=re.sub(r'⟦.*?⟧','',u['greek']).translate(str.maketrans({'“':'','”':'','⟨':'','⟩':''}));needle=re.sub(r'\s+','',display)
  if not compact.startswith(needle,cursor):needle=needle.replace('…','')
  assert compact.startswith(needle,cursor),(u['id'],needle[:80])
  a,b=positions[cursor],positions[cursor+len(needle)-1];first,last=refs[a],refs[b]
  result.append({'id':u['id'],'ref':first,'label':first if first==last else first+'–'+last,'speaker':u['speaker'],'greek':re.sub(r'\s+',' ',raw[a:b+1]).strip()});cursor+=len(needle)
 assert cursor==len(compact);assert len(result)==1720
 return result

def editorial_readings():
 responses=json.loads((REPO/'tools/gorgias-responses.json').read_text(encoding='utf-8'));edits={}
 for path in sorted((REPO/'tools/gorgias-reading').glob('*.txt')):
  for line in path.read_text(encoding='utf-8').splitlines():
   if not line.strip():continue
   key,zh,structure=line.split('|');key=int(key);assert key not in edits,key
   edits[key]={'zh':zh,'structure':structure}
 return responses,edits

def group_turns(records,german):
 greek=[]
 for u in records:
  speaker=SPEAKERS[u['speaker']]
  if not greek or greek[-1]['speaker']!=speaker:greek.append({'speaker':speaker,'units':[]})
  greek[-1]['units'].append(u)
 turns=[];speaker=''
 for page,paras in german.items():
  for text in paras:
   m=re.match(r'^(Sokrates|Kallikles|Chairephon|Gorgias|Polos):',text)
   if m:speaker=m[1]
   assert speaker
   if not turns or turns[-1]['speaker']!=speaker:turns.append({'speaker':speaker,'parts':[]})
   turns[-1]['parts'].append({'page':page,'german':[text]})
 assert len(greek)==len(turns)==1081,(len(greek),len(turns))
 assert [t['speaker'] for t in greek]==[t['speaker'] for t in turns]
 return zip(greek,turns)

def align_turn(units,segments,anchors,lexical):
 """Monotone sentence matching inside an independently verified speaker turn."""
 n,m=len(units),len(segments)
 if n==1:return {units[0]['id']:{'text':' '.join(s['text'] for s in segments),'sourcePage':segments[0]['page'],'unitGroup':[units[0]['id']],'score':1.0}}
 ratio=sum(len(s['text']) for s in segments)/max(1,sum(len(u['greek']) for u in units));dp={(0,0):(0,None)}
 @functools.lru_cache(maxsize=None)
 def source_block(j,nb):
  quote=' '.join(s['text'] for s in segments[j:j+nb])
  return quote,set(words(quote))
 for i in range(n):
  for j in range(m):
   if (i,j) not in dp:continue
   for na,nb in [(1,k) for k in range(1,m-j+1)]+[(k,1) for k in range(2,min(6,n-i+1))]+[(2,2)]:
    if i+na>n or j+nb>m:continue
    us=units[i:i+na];ss=segments[j:j+nb]
    if abs(int(re.match(r'\d+',us[0]['ref'])[0])-int(ss[0]['page']))>1:continue
    quote,bw=source_block(j,nb);target=ratio*sum(len(u['greek']) for u in us);length=abs(math.log(max(8,target)/max(8,len(quote))))
    original=' '.join(anchors.get(u['id'],'') for u in us)
    if original:
     aw=set(words(original));similarity=2*len(aw&bw)/max(1,len(aw)+len(bw));weight=1.5
    else:
     aw=set().union(*(lexical.get(u['id'],set()) for u in us));similarity=len(aw&bw)/max(1,len(bw));weight=.3
    cost=dp[i,j][0]+length*.9+weight*(1-similarity)+.3*(na-1)+.04*(nb-1);end=(i+na,j+nb)
    if end not in dp or cost<dp[end][0]:dp[end]=(cost,(i,j,na,nb,similarity))
 assert (n,m) in dp,(units[0]['id'],n,m)
 result={};at=(n,m)
 while at!=(0,0):
  i,j,na,nb,similarity=dp[at][1];us=units[i:i+na];ss=segments[j:j+nb]
  for u in us:result[u['id']]={'text':' '.join(s['text'] for s in ss),'sourcePage':ss[0]['page'],'unitGroup':[v['id'] for v in us],'score':round(similarity,4)}
  at=(i,j)
 return result

def dictionary_anchors(records,resources):
 lexicon={norm(x['w']):' '.join(words(plain(x['d'])[:250])) for x in json.loads((resources/'Pape.json').read_text(encoding='utf-8-sig'))}
 corpus=corpus_words(resources/SPEC['corpus'],{},{});result={};pages=collections.defaultdict(list)
 for u in records:pages[re.match(r'\d+',u['ref'])[0]].append(u)
 for page,units in pages.items():
  positions=[(u,w) for u in units for w in tokens(u['greek']) if isgreek(w)];annotated=corpus.get(page,[])
  for a,b,size in difflib.SequenceMatcher(None,[norm(w) for _,w in positions],[w[0] for w in annotated],autojunk=False).get_matching_blocks():
   for offset in range(size):
    u,_=positions[a+offset];terms=result.setdefault(u['id'],set())
    for analysis in annotated[b+offset][1]:terms.update(lexicon.get(norm(analysis['lemma']),'').split())
 return result

def prepare(folder,resources,epub):
 source=resources/'gorgias-perseus-grc2.xml';records=reading_units(folder,source)
 uploaded,sha=parse_notes(folder/'Gorgias_447a-461b_逐句精读_阶段稿.txt');assert len(uploaded)==334
 responses,edits=editorial_readings();anchors={};original=(folder/'Gorgias_447a-461b_逐句精读_阶段稿.txt').read_text(encoding='utf-8-sig')
 for match in re.finditer(r'(?m)^\[.*?底本句序(\d+)\]\s*\n(.*?)(?=^\[|\Z)',original,re.S):
  de=re.search(r'(?m)^德：(.*)$',match[2])
  if de:anchors[int(match[1])]=de[1]
 for u in records:
  if u['id']<=334:
   note=uploaded[u['id']-1]['notes'];reading={'zh':note['中'],'structure':clean_structure(note['结构'])};u['verbHints']=note.get('动词','')
  elif u['id'] in edits:reading=edits[u['id']]
  else:
   zh,structure=responses[u['greek']];reading={'zh':zh,'structure':structure}
  u['reading']={**reading,'de':''}
 german=source_german(epub,SPEC);lexical=dictionary_anchors(records,resources);groups=[];report=[]
 for greek,de in group_turns(records,german):
  _,segments=german_segments(de['parts']);found=align_turn(greek['units'],segments,anchors,lexical)
  for u in greek['units']:
   item=found[u['id']];u['reading'].update(de=item['text'],sourcePage=item['sourcePage']);report.append({'id':u['id'],'ref':u['ref'],**item})
  groups.extend({tuple(v['unitGroup']):v['unitGroup'] for v in found.values() if len(v['unitGroup'])>1}.values())
 reviewed_german_boundaries(records)
 for item in report:
  item['text']=records[item['id']-1]['reading']['de']
 dump(REPO/'tools/gorgias-notes.json',records);dump(REPO/'tools/gorgias-units.json',[{k:v for k,v in u.items() if k not in ('reading','verbHints')} for u in records]);(REPO/'tools/gorgias-source.xml').write_bytes(source.read_bytes())
 dump(REPO/'docs/gorgias-alignment-review.json',report)
 dump(REPO/'docs/gorgias-import-report.json',{'id':'gorgias','range':SPEC['range'],'units':len(records),'uploadedNotes':334,'supplementaryNotes':1386,'notesSha256':sha,'sourceTurns':1081,'germanTurns':1081,'germanFiles':SPEC['germanFiles'],'germanSourcePages':list(german),'sharedGermanGroups':groups,'dictionaryCorpusSource':'Diorisis Ancient Greek Corpus, figshare file 11296247'})
 print('Prepared',len(records),'units; verified 1081 matching speaker turns.',flush=True)

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--resources',type=Path,default=REPO.parent/'tmp/classics-source');ap.add_argument('--notes-dir',type=Path,default=REPO.parent/'output/gorgias');ap.add_argument('--german-epub',type=Path,required=True);ap.add_argument('--prepare',action='store_true');args=ap.parse_args()
 if args.prepare:prepare(args.notes_dir,args.resources,args.german_epub)
 spec={**SPEC,'proper':{**PROPER,**{k:v[0] for k,v in NAMES.items()}},'germanNames':{**GERMAN_NAMES,**{k:v[1] for k,v in NAMES.items()}},'germanLoader':lambda path:source_german(path,SPEC)}
 morph=REPO/'tools/gorgias-morphology.json'
 if morph.exists():spec['morphology']=json.loads(morph.read_text(encoding='utf-8'))
 result=import_work(args.resources,args.german_epub,spec);path=REPO/'docs/gorgias-import-report.json';report=json.loads(path.read_text(encoding='utf-8'));report['coverage']={k:result[k] for k in ['words','morphologyCoverage','germanLexiconCoverage','chineseGlossCoverage','corpusAlignmentCoverage','unknownForms']};dump(path,report)

if __name__=='__main__':main()
