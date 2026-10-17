"""Import user reading notes, Greek morphology, Pape and the supplied German EPUB.

No translation model or remote translation service is used. Run with --help.
"""
import argparse, collections, difflib, hashlib, html, json, re, shutil, sqlite3, unicodedata, zipfile, xml.etree.ElementTree as ET
from pathlib import Path
from html.parser import HTMLParser

REPO = Path(__file__).resolve().parents[1]
WORKS = [
 ('symposium','会饮篇','Symposium','Συμπόσιον','tlg011','172a–223d','全篇合订；172a–185e原稿待校','Symposium_172a-223d_逐句精读_合订稿_原稿待校.txt','part0017.xhtml',172,223),
 ('philebus','斐勒布篇','Philebus','Φίληβος','tlg010','11a–67b','全篇精读稿','Philebus_11a-67b_逐句精读.txt','part0019.xhtml',11,67),
 ('sophist','智者篇','Sophist','Σοφιστής','tlg007','216a–242b','阶段稿；精读尚未覆盖242b之后','Sophist_216a-242b_逐句精读_阶段稿.txt','part0015.xhtml',216,242),
]
FIELDS = ['拉丁转写','代词','名词','形容词','动词','小品词','连接词','结构','句法与风格','生词','德','中']
def norm(s):
 s=s.translate(str.maketrans({"'":'', 'ʼ':'','᾽':'','’':''}))
 return ''.join(c for c in unicodedata.normalize('NFD',s.lower()) if unicodedata.category(c)!='Mn' and c.isalpha()).replace('ς','σ')
def plain(s): return re.sub(r'\s+',' ',html.unescape(re.sub('<[^>]*>',' ',s))).strip()
def dump(p,data):
 p.parent.mkdir(parents=True,exist_ok=True)
 p.write_text(json.dumps(data,ensure_ascii=False,separators=(',',':')),encoding='utf-8')
def tokens(text):
 # Preserve punctuation and spaces exactly; marks and elision belong to words.
 result=re.findall(r"[^\W\d_]+[\u0300-\u036f]*[ʼ᾽’']?|[^\w\u0300-\u036f]+|[\d_]+",text,re.UNICODE)
 seams={'καὶΠρώταρχος':['καὶ','Πρώταρχος'],'νομίμωςοὐδ’':['νομίμως','οὐδ’']}
 return [part for t in result for part in seams.get(t,[t])]
def isgreek(t): return any(('GREEK' in unicodedata.name(c,'')) and c.isalpha() for c in t)
def morph_entry(lemma,pos,raw,lookup,glosses,pape):
 lemma=re.sub(r'\d+$','',lemma)
 e={'lemma':lemma,'pos':{'proper':'proper_noun'}.get(pos,pos),'raw':raw,'lookup':lookup,'zh':glosses.get(norm(lemma),''),'de':norm(lemma) if norm(lemma) in pape else ''}
 maps={
  'case':{'nom':'nominative','gen':'genitive','dat':'dative','acc':'accusative','voc':'vocative'},
  'gender':{'masc':'masculine','fem':'feminine','neut':'neuter'},
  'number':{'sg':'singular','pl':'plural','dual':'dual'},
  'tense':{'pres':'present','imperf':'imperfect','aor':'aorist','perf':'perfect','plup':'pluperfect','fut':'future'},
  'voice':{'act':'active','mid':'middle','pass':'passive','mp':'mediopassive'},
  'mood':{'ind':'indicative','subj':'subjunctive','opt':'optative','imperat':'imperative','inf':'infinitive'},
  'person':{'1st':'1st','2nd':'2nd','3rd':'3rd'},
  'degree':{'comp':'comparative','superl':'superlative'}
 }
 for field,m in maps.items():
  found=[v for k,v in m.items() if re.search(r'(?<![a-z])'+k+r'(?![a-z])',raw)]
  e[field]='/'.join(found)
 if re.search(r'(?<![a-z])part(?![a-z])',raw):e['pos']='participle'
 return e
EDITORIAL={
 'Μαντινικὴ':('Μαντινικός','adjective','fem nom sg'),
 'Μαντινικῆς':('Μαντινικός','adjective','fem gen sg'),
 'διεμνημόνευεν':('διαμνημονεύω','verb','imperf ind act 3rd sg'),
 'καταδεδαρθηκὼς':('καταδαρθάνω','participle','perf part act masc nom sg'),
 'Ἀκουσίλεως':('Ἀκουσίλαος','proper','masc gen sg'),
 'Ἀριστογείτονος':('Ἀριστογείτων','proper','masc gen sg'),
 'Ἀριστόδημος':('Ἀριστόδημος','proper','masc nom sg'),
 'ἐπέθεσαν':('ἐπιτίθημι','verb','aor ind act 3rd pl'),
 'Ἐρυξίμαχον':('Ἐρυξίμαχος','proper','masc acc sg'),
 'Ἡράκλειτος':('Ἡράκλειτος','proper','masc nom sg'),
 'Θεῦθ':('Θεύθ','proper','indeclinable'),
 'γενοίσθην':('γίγνομαι','verb','aor opt mid 3rd dual'),
 'καθαπερεὶ':('καθαπερεί','conjunction','indeclinable'),
 'ἀμετρώτερον':('ἄμετρος','adjective','neut nom/voc/acc sg comp'),
 'ἔθεμέν':('τίθημι','verb','aor ind act 1st pl'),
 'ἔθεμεν':('τίθημι','verb','aor ind act 1st pl'),
}
NAMES={
 'Σωκράτης':('Sokrates',{'nom':'Σωκράτης','gen':'Σωκράτους','dat':'Σωκράτει','acc':'Σωκράτη Σωκράτην','voc':'Σώκρατες'}),
 'Πρώταρχος':('Protarchos',{'nom':'Πρώταρχος','gen':'Πρωτάρχου','dat':'Πρωτάρχῳ','acc':'Πρώταρχον','voc':'Πρώταρχε'}),
 'Φίληβος':('Philebos',{'nom':'Φίληβος','gen':'Φιλήβου','dat':'Φιλήβῳ','acc':'Φίληβον','voc':'Φίληβε'}),
 'Ἀγάθων':('Agathon',{'nom':'Ἀγάθων','gen':'Ἀγάθωνος','dat':'Ἀγάθωνι','acc':'Ἀγάθωνα'}),
 'Ἀλκιβιάδης':('Alkibiades',{'nom':'Ἀλκιβιάδης','gen':'Ἀλκιβιάδου','dat':'Ἀλκιβιάδῃ','acc':'Ἀλκιβιάδην','voc':'Ἀλκιβιάδη'}),
 'Ἀπολλόδωρος':('Apollodoros',{'nom':'Ἀπολλόδωρος','gen':'Ἀπολλοδώρου','dat':'Ἀπολλοδώρῳ','acc':'Ἀπολλόδωρον','voc':'Ἀπολλόδωρε'}),
 'Ἀριστόδημος':('Aristodemos',{'nom':'Ἀριστόδημος','gen':'Ἀριστοδήμου','dat':'Ἀριστοδήμῳ','acc':'Ἀριστόδημον','voc':'Ἀριστόδημε'}),
 'Ἀριστοφάνης':('Aristophanes',{'nom':'Ἀριστοφάνης','gen':'Ἀριστοφάνους','dat':'Ἀριστοφάνει','acc':'Ἀριστοφάνη','voc':'Ἀριστόφανες'}),
 'Ἐρυξίμαχος':('Eryximachos',{'nom':'Ἐρυξίμαχος','gen':'Ἐρυξιμάχου','dat':'Ἐρυξιμάχῳ','acc':'Ἐρυξίμαχον','voc':'Ἐρυξίμαχε'}),
 'Φαῖδρος':('Phaidros',{'nom':'Φαῖδρος','gen':'Φαίδρου','dat':'Φαίδρῳ','acc':'Φαῖδρον','voc':'Φαῖδρε'}),
 'Θεόδωρος':('Theodoros',{'nom':'Θεόδωρος','gen':'Θεοδώρου','dat':'Θεοδώρῳ','acc':'Θεόδωρον','voc':'Θεόδωρε'}),
 'Θεαίτητος':('Theaitetos',{'nom':'Θεαίτητος','gen':'Θεαιτήτου','dat':'Θεαιτήτῳ','acc':'Θεαίτητον','voc':'Θεαίτητε'}),
}
NAME_FORMS={norm(form):(lemma,case) for lemma,(_,cases) in NAMES.items() for case,forms in cases.items() for form in forms.split()}
def corpus_words(path,glosses,pape):
 beta=dict(zip('abgdezhqiklmn coprstufxyw'.replace(' ',''),'αβγδεζηθικλμνξοπρστυφχψω'))
 pages=collections.defaultdict(list)
 tree=ET.parse(path)
 for s in tree.findall('.//sentence'):
  for w in s.findall('word'):
   form=''.join(beta.get(c,'') for c in w.get('form','').lower())
   candidates=[]
   for l in w.findall('lemma'):
    if not l.get('entry'):continue
    for a in l.findall('analysis'):
     candidates.append(morph_entry(l.get('entry'),l.get('POS',''),a.get('morph',''),'diorisis',glosses,pape))
   pages[s.get('location','').split('.')[0]].append((norm(form),candidates))
 return pages
def note_candidates(unit,word,analyses):
 note=unit['notes'].get('动词','')
 if not note:return analyses
 # The supplied grammatical notes take precedence over automatic homonyms.
 hit=re.search(re.escape(word)+r'(?![\u0370-\u03ff\u1f00-\u1fff])(?:（([^）]*)）)?([^；;。]*)',note)
 if not hit:return analyses
 parent=hit[1] or '';description=parent+' '+(hit[2] or '')
 constraints={}
 lemma=re.match(r'(?:词条\s*)?([\u0370-\u03ff\u1f00-\u1fff]+)',parent)
 if lemma:constraints['lemma']=lemma[1]
 for field,values in {
  'tense':[('未完成','imperfect'),('不定过去','aorist'),('过去完成','pluperfect'),('完成','perfect'),('现在','present'),('将来','future')],
  'mood':[('直陈','indicative'),('虚拟','subjunctive'),('命令','imperative'),('祈愿','optative'),('不定式','infinitive')],
  'voice':[('主动','active'),('被动','passive'),('关身','middle')],
  'number':[('单数','singular'),('复数','plural'),('双数','dual')],
  'person':[('第一人称','1st'),('第二人称','2nd'),('第三人称','3rd')]
 }.items():
  for term,value in values:
   if term in description:constraints[field]=value;break
 compact=re.search(r'([一二三])([单复双])',description)
 if compact:constraints.update(person={'一':'1st','二':'2nd','三':'3rd'}[compact[1]],number={'单':'singular','复':'plural','双':'dual'}[compact[2]])
 compact_voice=re.search(r'(?:现在|不定过去|完成|将来|未完成过去?)(主|中|被)(?:直陈|虚拟|命令|祈愿|分词|不定式)',description)
 if compact_voice:constraints['voice']={'主':'active','中':'middle','被':'passive'}[compact_voice[1]]
 if '分词' in description:constraints['pos']='participle'
 if not constraints:return analyses
 matches=[dict(a,lookup='notes') for a in analyses if all(value==a.get(key) or (key=='voice' and value=='middle' and a.get(key)=='mediopassive') for key,value in constraints.items())]
 return matches or analyses
def parse_notes(path):
 text=path.read_text(encoding='utf-8-sig')
 units=[]
 header_pattern=r'\[(\d+[a-e][^\]\n]*；[^\]\n]+)\]'
 for m in re.finditer(header_pattern+r'(.*?)(?='+header_pattern.replace('(','(?:',1)+r'|\Z)',text,re.S):
  header,body=m.groups()
  if not re.match(r'\d+[a-e]',header): continue
  body=re.sub(r'('+ '|'.join(FIELDS)+r')[：:]',r'\n\1：',body)
  lines=body.splitlines(); greek=[]; fields={}; current=None
  for line in lines:
   line=line.strip()
   if re.match(r'^第[一二三]部分|^底本：Perseus|^指定入口：https',line):break
   f=re.match(r'^('+ '|'.join(FIELDS)+r')[：:](.*)',line)
   if f:
    current=f[1]; fields[current]=(fields.get(current,'')+' '+f[2].strip()).strip()
   elif not current and isgreek(line):
    original=re.split(r'[（(](?:校勘)?注[：:]',line,maxsplit=1)
    candidate=original[0].strip()
    if not re.search(r'[\u4e00-\u9fff]',candidate):greek.append(candidate)
    if len(original)>1:fields['原稿附注']=original[1].strip(')）')
   elif current and line and not re.match(r'^第.+部分|^\d+[a-e][–-]|^《|^柏拉图|^本文件|^续编|^原稿',line):
    fields[current]+=' '+line
  if not greek: continue
  ref=re.match(r'\d+[a-e]',header)[0]
  parts=header.split('；')
  fields.pop('德',None)  # Earlier generated German is deliberately excluded.
  for key,value in list(fields.items()):
   value=re.sub(r'德\s*[^；;）]*?[／/]中\s*','',value)
   if key=='生词':
    value='；'.join(re.sub(r'([＝=])[^；]*[／/]',r'\1',part) for part in value.split('；'))
   fields[key]=value
  greek_text=' '.join(greek)
  for old,new in {'οὕτωawi':'οὕτως','θαυμαστὴruk':'θαυμαστή','ταῦταวั':'ταῦτα'}.items():
   if old in greek_text:
    greek_text=greek_text.replace(old,new)
    fields['导入校记']=(fields.get('导入校记','')+f' 原稿“{old}”含异常字符，网页作“{new}”；前两处依原稿自附校注，第三处移除误混入的泰文字母。').strip()
  units.append({'id':len(units)+1,'ref':ref,'label':parts[0],'speaker':parts[1] if len(parts)>1 else '', 'greek':greek_text,'notes':fields})
 return units,hashlib.sha256(path.read_bytes()).hexdigest()
class Paragraphs(HTMLParser):
 def __init__(self): super().__init__(); self.blocks=[];self.active=False;self.buf=[]
 def handle_starttag(self,t,a):
  if t in ('p','h1','h2','h3','h4'): self.active=True;self.buf=[]
  if t=='br' and self.active:self.buf.append('\n')
 def handle_data(self,d):
  if self.active:self.buf.append(d)
 def handle_endtag(self,t):
  if t in ('p','h1','h2','h3','h4') and self.active:
   self.blocks.append((t,re.sub(r'\s+',' ',''.join(self.buf)).strip()));self.active=False
def german_pages(z,file,start,end):
 parser=Paragraphs();parser.feed(z.read('OEBPS/Text/'+file).decode('utf-8'))
 pages=collections.defaultdict(list);page=None
 for tag,para in parser.blocks:
  if page is not None and tag in ('h1','h2','h3'):break
  if tag!='p':continue
  pieces=re.split(r'\((\d{1,3})\)',para)
  if page is not None and pieces[0]:pages[page].append(pieces[0].strip())
  for i in range(1,len(pieces),2):
   number=int(pieces[i])
   if start<=number<=end+1:page=number
   if page is not None and page<=end and pieces[i+1].strip():pages[page].append(pieces[i+1].strip())
 return {str(k):v for k,v in pages.items() if start<=k<=end}
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--project',type=Path,default=REPO.parent);ap.add_argument('--resources',type=Path,default=REPO.parent/'tmp/classics-source');ap.add_argument('--german-epub',type=Path,required=True);args=ap.parse_args()
 out=REPO/'data/classics';resources=args.resources
 c=sqlite3.connect(f'file:{(resources/"morph.db").as_posix()}?mode=ro',uri=True);c.row_factory=sqlite3.Row
 # Pape data shape is normalized below. Dictionary text is never generated.
 raw=json.loads((resources/'Pape.json').read_text(encoding='utf-8-sig'))
 pape={}
 if isinstance(raw,dict):
  for key,value in raw.items():pape.setdefault(norm(key),[]).append({'lemma':key,'text':plain(value if isinstance(value,str) else json.dumps(value,ensure_ascii=False))})
 else:
  for item in raw:
   key=item.get('w') or item.get('lemma') or item.get('headword') or item.get('orth')
   if key:pape.setdefault(norm(key),[]).append({'lemma':key,'text':plain(item.get('d') or item.get('definition') or item.get('entry') or item.get('text') or json.dumps(item,ensure_ascii=False))})
 catalog=[];all_report={};form_cache={};words={};gloss_by_form={};input_units={}
 for slug,*_ in WORKS:
  spec=next(w for w in WORKS if w[0]==slug)
  units,sha=parse_notes(args.project/'output'/slug/spec[7]);input_units[slug]=(units,sha)
  for u in units:
   for t in tokens(u['greek']):
    if isgreek(t):words[t]=norm(t)
   # Chinese explanations are taken from the supplied notes, never from DE MT.
   for item in re.split('[；;]',u['notes'].get('生词','')):
    match=re.fullmatch(r'\s*([\u0370-\u03ff\u1f00-\u1fff]+)(?:（[^）]*）)?[＝=](.+)',item)
    if not match:continue
    meaning=match[2].strip()
    if re.search('[\u4e00-\u9fff]',meaning):gloss_by_form.setdefault(norm(match[1]),meaning)
 # The corpus preserves accents. Exact accents are preferred, grave accents
 # are compared as acute, then normalized fallback is explicitly recorded.
 def accent(s):return unicodedata.normalize('NFC',unicodedata.normalize('NFD',s.lower()).replace('\u0300','\u0301')).replace('ς','σ').translate(str.maketrans({'ʼ':"'",'᾽':"'",'’':"'"}))
 overrides={}
 for pos,lemmas in {
  'article':'ὁ',
  'pronoun':'ἐγώ σύ ἡμεῖς ὑμεῖς αὐτός οὗτος ἐκεῖνος ὅδε ὅς τίς τις ὅστις ὅσος οἷος τοιοῦτος ἑαυτοῦ ἀλλήλων ἑκάτερος ἕκαστος ἐμός σός ἡμέτερος ὑμέτερος',
  'adjective':'πᾶς μόνος ἄλλος ἕτερος πρῶτος δεύτερος τρίτος πρότερος ὕστερος πολύς ὀλίγος μέγας μικρός σμικρός ἀγαθός κακός καλός αἰσχρός δίκαιος ἄδικος ἀληθής ψευδής ὀρθός ἴσος ὅμοιος ἀνόμοιος ὅλος ἄπειρος θνητός ἀθάνατος θεῖος σοφός δυνατός ἀδύνατος ἡδύς πλείων πλεῖστος βελτίων κρείττων χείρων ἥσσων κάλλιστος ἄριστος νέος παλαιός πλούσιος πένης εὐδαίμων ἐναντίος ἀναγκαῖος σαφής ἀσαφής ἀμελέτητος',
  'conjunction':'καί τε ἀλλά ἤ εἰ ἐάν ὅτι ἵνα ὅταν ἐπεί ἐπειδή ὥστε οὔτε μήτε',
  'particle':'δέ μέν γάρ οὖν δή γε ἄν ἦ ἄρα ἆρα μῶν μέντοι μήν τοίνυν',
  'adverb':'οὐ μή οὐδέ μηδέ οὐκοῦν οὔκουν νῦν νυνί τότε ἤδη ἔτι πάλιν αὖ οὕτως οὕτω πάνυ μάλα μάλιστα μᾶλλον ἧττον ἥκιστα ἅμα πῶς πως πού που ποτέ ποτε ἀεί ἐνθάδε ἐνταῦθα ἐκεῖ εὖ κακῶς καλῶς',
  'preposition':'ἐν εἰς ἐκ ἀπό πρός περί κατά διά μετά παρά ὑπό ἐπί ὑπέρ ἀμφί ἀνά πρό ἀντί ἄνευ ἕνεκα',
  'numeral':'δύο τρεῖς εἷς ἄμφω',
  'interjection':'ὦ',
 }.items():
  for lemma in lemmas.split():overrides[lemma]=pos
 for word,n in words.items():
  key=n+("'" if word.endswith(("'",'ʼ','᾽','’')) else '')
  rows=[dict(r) for r in c.execute('SELECT * FROM morphology WHERE form_normalized=?',(key,))]
  exact=[r for r in rows if accent(r['form'])==accent(word)]
  chosen=exact or rows
  result=[];seen=set()
  for r in chosen:
   sig=tuple(r[k] for k in ['lemma','pos','morphology'])
   if sig in seen:continue
   seen.add(sig)
   lemma=re.sub(r'\d+$','',r['lemma'])
   pos=overrides.get(lemma,{'adv':'adverb','prep':'preposition','conj':'conjunction','exclam':'interjection','pron':'pronoun','adj':'adjective'}.get(r['pos'],r['pos']))
   if r['pos'] in ('verb','participle'):pos=r['pos']
   entry={'lemma':lemma,'pos':pos,'raw':r['morphology'],'tense':r['tense'],'voice':r['voice'],'mood':r['mood'],'person':r['person'],'number':r['number'],'case':r['case_name'],'gender':r['gender'],'degree':r['degree'],'lookup':'accent' if exact else 'normalized','zh':gloss_by_form.get(norm(lemma)) or gloss_by_form.get(n,'')}
   for field,short in [('case',{'nom':'nominative','gen':'genitive','dat':'dative','acc':'accusative','voc':'vocative'}),('gender',{'masc':'masculine','fem':'feminine','neut':'neuter'})]:
    found=[v for k,v in short.items() if re.search(r'(?<![a-z])'+k+r'(?![a-z])',r['morphology'])]
    if found:entry[field]='/'.join(found)
   if 'inf' in r['morphology'].split():entry['mood']='infinitive'
   if 'mid/pass' in r['morphology']:entry['voice']='middle/passive'
   entry['de']=norm(lemma) if norm(lemma) in pape else ''
   result.append(entry)
  form_cache[word]=result
 # Supplemental Chinese glosses are editorial entries; DE remains source text.
 supplemental=json.loads((REPO/'tools/classics-zh.json').read_text(encoding='utf-8'))
 supplemental.update(json.loads((REPO/'tools/classics-zh-extra.json').read_text(encoding='utf-8')))
 supplemental.update(json.loads((REPO/'tools/classics-zh-more.json').read_text(encoding='utf-8')))
 for analyses in form_cache.values():
  for a in analyses:
   if not a['zh']:a['zh']=supplemental.get(a['lemma'],'')
 all_glosses=dict(gloss_by_form);all_glosses.update({norm(k):v for k,v in supplemental.items()})
 used=set()
 with zipfile.ZipFile(args.german_epub) as z:
  for slug,title,latin,grc,tlg,scope,status,filename,de_file,start,end in WORKS:
   units,sha=input_units[slug];de=german_pages(z,de_file,start,end);pages=collections.defaultdict(list);wordcount=known=de_count=zh_count=context_count=0;unknown=set()
   for u in units:
    ts=tokens(u['greek']);assert ''.join(ts)==u['greek'],u['id']
    u['tokens']=ts;pages[re.match(r'\d+',u['ref'])[0]].append(u)
   corpus_path=next(resources.glob(f'Plato* - {latin} (*).xml'))
   corpus=corpus_words(corpus_path,all_glosses,pape)
   for page,us in pages.items():
    positions=[(u,i,w) for u in us for i,w in enumerate(u['tokens']) if isgreek(w)]
    source=corpus.get(page,[])
    matched={}
    matcher=difflib.SequenceMatcher(None,[norm(w) for _,_,w in positions],[x[0] for x in source],autojunk=False)
    for left,right,size in matcher.get_matching_blocks():
     for offset in range(size):matched[left+offset]=source[right+offset][1]
    pool={};pool_keys={}
    for u in us:u['analyses']={}
    for offset,(u,i,w) in enumerate(positions):
     analyses=(matched.get(offset) or [])+form_cache[w]
     analyses=note_candidates(u,w,analyses)
     if norm(w) in NAME_FORMS:
      lemma,case=NAME_FORMS[norm(w)];analyses=[morph_entry(lemma,'proper',f'masc {case} sg','editorial',all_glosses,pape)]
     if w in ['Φίληβος','Φίληβός','Φιλήβου','Φιλήβῳ','Φίληβον','Φίληβε']:
      case={'Φίληβος':'nom','Φίληβός':'nom','Φιλήβου':'gen','Φιλήβῳ':'dat','Φίληβον':'acc','Φίληβε':'voc'}[w]
      analyses=[morph_entry('Φίληβος','proper',f'masc {case} sg','editorial',all_glosses,pape)]
     if not analyses and w in EDITORIAL:
      lemma,pos,raw=EDITORIAL[w];analyses=[morph_entry(lemma,pos,raw,'editorial',all_glosses,pape)]
     for a in analyses:
      name=NAMES.get(a['lemma'])
      if name and name[0] in ' '.join(de.get(page,[])):a['deName']=name[0]
     # Preserve all analyses within each corpus lemma, removing duplicates only.
     analyses=list({json.dumps({k:v for k,v in a.items() if k!='lookup'},ensure_ascii=False,sort_keys=True):a for a in reversed(analyses)}.values())
     signature=json.dumps(analyses,ensure_ascii=False,sort_keys=True)
     if signature not in pool_keys:
      key=str(len(pool_keys));pool_keys[signature]=key;pool[key]=analyses
     u['analyses'][str(i)]=pool_keys[signature]
     wordcount+=1;known+=bool(analyses);de_count+=any(a['de'] or a.get('deName') for a in analyses);zh_count+=any(a['zh'] for a in analyses);context_count+=bool(matched.get(offset))
     if not analyses:unknown.add(w)
     used.update(a['de'] for a in analyses if a['de'])
    ws={w:form_cache[w] for u in us for w in u['tokens'] if isgreek(w)}
    dump(out/slug/(page+'.json'),{'work':slug,'page':page,'units':us,'analyses':pool,'german':de.get(page,[]),'germanSource':{'file':de_file,'page':page,'alignment':'Stephanus整页；并非逐句对齐'}})
   meta={'id':slug,'title':title,'latin':latin,'greekTitle':grc,'range':scope,'status':status,'pages':list(pages),'units':len(units),'words':wordcount,'source':f'https://scaife.perseus.org/library/urn:cts:greekLit:tlg0059.{tlg}/','germanTranslator':'Friedrich Daniel Ernst Schleiermacher','germanTitle':'Gesammelte Werke','germanEdition':'用户提供的EPUB；书内标注Akademie Verlag Berlin 1986','germanFile':de_file,'notesSha256':sha,'morphologyCoverage':known/wordcount,'germanLexiconCoverage':de_count/wordcount,'chineseGlossCoverage':zh_count/wordcount,'corpusAlignmentCoverage':context_count/wordcount}
   dump(out/slug/'catalog.json',meta);catalog.append(meta);all_report[slug]={**meta,'unknownForms':sorted(unknown)}
 dump(out/'pape.json',{k:pape[k] for k in used})
 dump(out/'catalog.json',{'release':'20261017-classics-1','works':catalog,'dictionary':'Wilhelm Pape, Handwörterbuch der griechischen Sprache · PTA电子本','germanPolicy':'德文原译直接摘自用户提供的EPUB；德文词典条目直接摘自Pape；未使用机器翻译。'})
 dump(REPO/'docs/classics-import-report.json',all_report)
 print(json.dumps({k:{x:v[x] for x in ['units','words','morphologyCoverage','germanLexiconCoverage','chineseGlossCoverage']} for k,v in all_report.items()},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
