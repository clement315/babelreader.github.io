"""Add dialogues from the owner's notes and specified editions.

German is retrieved verbatim from the supplied EPUB; no translator is called.
"""
from pathlib import Path
import argparse,collections,hashlib,json,re,sqlite3,xml.etree.ElementTree as ET,zipfile
from import_classics import Paragraphs,REPO,norm,tokens,isgreek,dump
from import_parmenides import import_work
from simplify_classics import german_segments,align_units,clean_structure

WORKS={
 'alcibiades1':{'id':'alcibiades1','title':'阿尔西比亚德斯 1','latin':'Alcibiades 1','greekTitle':'Ἀλκιβιάδης αʹ','range':'103a–135e','start':103,'end':135,'tlg':'tlg013','filename':'Acibiades 1.txt','corpus':'Plato (0059) - Alcibiades 1 (013).xml','germanFiles':['part0020.xhtml'],'germanHeading':'Alkibiades','germanEdition':'用户提供的EPUB；本篇标注Akademie Verlag Berlin 1987','expected':1103},
 'apology':{'id':'apology','title':'申辩篇','latin':'Apology','greekTitle':'Ἀπολογία Σωκράτους','range':'17a–42a','start':17,'end':42,'tlg':'tlg002','filename':'Apology.txt','corpus':'Plato (0059) - Apology (002).xml','germanFiles':['part0006.xhtml','part0007.xhtml'],'germanHeading':'Des Sokrates Verteidigung','germanEdition':'用户提供的EPUB；本篇标注Akademie Verlag Berlin 1985','expected':345},
 'alcibiades2':{'id':'alcibiades2','title':'阿尔西比亚德斯 2','latin':'Alcibiades 2','greekTitle':'Ἀλκιβιάδης βʹ','range':'138a–151c','start':138,'end':151,'tlg':'tlg014','filename':'Alcibiades 2.txt','corpus':'Plato (0059) - Alcibiades 2 (014).xml','germanFiles':['part0008.xhtml'],'germanHeading':'Alkibiades','germanEdition':'用户提供的EPUB；本篇标注Akademie Verlag Berlin 1985','expected':257,'germanUnmarkedPages':[147],'release':'20261018-classics-5'}
}
PROPER={'Σωκράτης':'苏格拉底','Ἀλκιβιάδης':'阿尔西比亚德斯','Κλεινίας':'克莱尼亚斯','Δεινομάχη':'狄诺玛刻','Περικλῆς':'伯里克利','Ξάνθιππος':'克桑提波斯','Κύρος':'居鲁士','Δαρεῖος':'大流士','Ἀρταξέρξης':'阿尔塔克塞尔克塞斯','Ἀγησίλαος':'阿格西拉奥斯','Τισσαφέρνης':'提萨斐尔涅斯','Ἀναξαγόρας':'阿那克萨戈拉','Δάμων':'达蒙','Πρωταγόρας':'普罗泰戈拉','Χαιρεφῶν':'凯勒丰','Μέλητος':'米勒托斯','Ἄνυτος':'阿尼托斯','Λύκων':'吕孔','Ἀντιφῶν':'安提丰','Ἀριστοφάνης':'阿里斯托芬','Ἀχιλλεύς':'阿基琉斯','Θέτις':'忒提斯','Ἕκτωρ':'赫克托耳','Πάτροκλος':'帕特罗克洛斯','Ἀπόλλων':'阿波罗','Ζεύς':'宙斯','Ἀθηνᾶ':'雅典娜','Πυθία':'皮提亚，德尔斐女祭司','Σαλαμίς':'萨拉米斯','Ἀμφίπολις':'安菲波利斯','Ποτείδαια':'波提狄亚','Δήλιον':'得利翁','Ἀθήνη':'雅典','Ἑλλάς':'希腊','Λακεδαίμων':'拉刻代蒙','Πέρσης':'波斯人','Τροία':'特洛伊','Πρίαμος':'普里阿摩斯','Κάμβυσις':'冈比西斯','Λεωτυχίδης':'列奥提喀德斯','Ἀγησίπολις':'阿格西波利斯','Ἄγις':'阿吉斯','Εὐρυσάκης':'欧律萨克斯','Δαίδαλος':'代达罗斯','Ἥφαιστος':'赫淮斯托斯','Ἑρμῆς':'赫尔墨斯','Φειδίας':'斐狄亚斯','Ζήνων':'芝诺','Πυθόδωρος':'皮托多罗斯','Καλλίας':'卡利阿斯','Εὔηνος':'欧厄诺斯','Πλάτων':'柏拉图','Κρίτων':'克里同','Κριτόβουλος':'克里托布洛斯','Ἀπολλόδωρος':'阿波罗多洛斯','Ἀδείμαντος':'阿得曼托斯','Ἀντισθένης':'安提斯泰尼','Αἰσχίνης':'埃斯基涅斯','Δημόδοκος':'德摩多科斯','Πάραλος':'帕拉洛斯','Ἀντιοχίς':'安提俄喀斯部落','Λέων':'列昂','Ἀριστείδης':'阿里斯提德斯','Πάμφιλος':'潘菲洛斯','Στίληππος':'斯提利波斯','Εὔμαχος':'欧马科斯','Αἰαντόδωρος':'埃安托多洛斯','Διόνυσος':'狄俄尼索斯','Μίνως':'弥诺斯','Ῥαδάμανθυς':'拉达曼提斯','Αἰακός':'埃阿科斯','Τριπτόλεμος':'特里普托勒摩斯','Ὀρφεύς':'俄耳甫斯','Μουσαῖος':'缪塞俄斯','Ἡσίοδος':'赫西俄德','Ὅμηρος':'荷马','Παλαμήδης':'帕拉墨德斯','Αἴας':'埃阿斯','Λαέρτης':'拉厄耳忒斯','Ὀδυσσεύς':'奥德修斯','Σίσυφος':'西西弗斯','Ἀγαμέμνων':'阿伽门农'}
GERMAN_NAMES={'Σωκράτης':'Sokrates','Ἀλκιβιάδης':'Alkibiades','Κλεινίας':'Kleinias','Περικλῆς':'Perikles','Δεινομάχη':'Deinomache','Χαιρεφῶν':'Chairephon','Μέλητος':'Melitos','Ἄνυτος':'Anytos','Λύκων':'Lykon','Πλάτων':'Platon','Κρίτων':'Kriton','Ἀναξαγόρας':'Anaxagoras','Καλλίας':'Kallias','Εὔηνος':'Euenos','Ἀπόλλων':'Apollon','Ἡσίοδος':'Hesiodos','Ὅμηρος':'Homeros'}

WORKS['alcibiades2'].update(
 proper={'Οἰδίπους':'俄狄浦斯','Ἀρχέλαος':'阿尔刻拉奥斯','Ὀρέστης':'俄瑞斯忒斯','Ἀλκμέων':'阿尔克迈翁','Κρέων':'克瑞翁','Τειρεσίας':'忒瑞西阿斯','Ἄμμων':'阿蒙神','Διομήδης':'狄俄墨得斯','Εὐριπίδης':'欧里庇得斯','Μαργίτης':'马尔吉忒斯'},
 germanNames={'Οἰδίπους':'Oidipus','Ἀρχέλαος':'Archelaos','Ὀρέστης':'Orestes','Ἀλκμέων':'Alkmaion','Κρέων':'Kreon','Τειρεσίας':'Teiresias','Ἄμμων':'Ammon','Διομήδης':'Diomedes','Εὐριπίδης':'Euripides'})

def source_german(epub,spec):
 pages=collections.defaultdict(list);active=False;page=None;done=False
 marks=r'\(('+ '|'.join(str(i) for i in range(spec['start'],spec['end']+1))+r')\)'
 with zipfile.ZipFile(epub) as z:
  for filename in spec['germanFiles']:
   p=Paragraphs();p.feed(z.read('OEBPS/Text/'+filename).decode('utf-8'))
   for tag,para in p.blocks:
    if not active:
     if tag=='h3' and para==spec['germanHeading']:active=True
     continue
    if tag in ('h1','h2','h3'):done=True;break
    if tag!='p':continue
    parts=re.split(marks,para)
    if page and parts[0].strip():pages[page].append(parts[0].strip())
    for i in range(1,len(parts),2):
     page=parts[i]
     if parts[i+1].strip():pages[page].append(parts[i+1].strip())
   if done:break
 expected=[i for i in range(spec['start'],spec['end']+(0 if spec['id']=='apology' else 1)) if i not in spec.get('germanUnmarkedPages',[])]
 assert list(map(int,pages))==expected,(spec['id'],list(pages))
 return dict(pages)

def canonical_text(path):
 root=ET.parse(path);body=root.find('.//{http://www.tei-c.org/ns/1.0}body');chars=[];refs=[];ref=''
 def append(s):
  for c in s:
   if c!='>':chars.append(c);refs.append(ref)
 def visit(e):
  nonlocal ref
  if e.tag.rsplit('}',1)[-1]=='milestone' and re.fullmatch(r'\d+[a-e]',e.get('n','')):ref=e.get('n')
  append(e.text or '')
  for child in e:
   if child.tag.rsplit('}',1)[-1] not in ('del','note','head','label','bibl'):visit(child)
   append(child.tail or '')
 visit(body);text=''.join(chars);positions=[i for i,c in enumerate(text) if not c.isspace()]
 return text,refs,positions

def parse_uploaded(path,source):
 text=path.read_text(encoding='utf-8-sig');heads=list(re.finditer(r'(?m)^(\d+)\.\s*\[([^]]+)\]\s*([^\n]+)',text));raw,refs,positions=canonical_text(source)
 compact=''.join(raw[i] for i in positions);cursor=0;units=[];seen={};duplicates=[]
 for n,m in enumerate(heads):
  fields={}
  for line in text[m.end():heads[n+1].start() if n+1<len(heads) else len(text)].splitlines():
   if '：' in line:
    k,v=line.split('：',1);fields[k.strip()]=v.strip()
  greek=re.sub(r'\s+',' ',m[3]).strip();key=(int(m[1]),re.sub(r'\s+','',greek))
  if path.name=='Alcibiades 2.txt':
   if int(m[1])==171:greek='—'+greek
   greek=greek.replace('…','...');key=(int(m[1]),re.sub(r'\s+','',greek))
  if key in seen:
   seen[key]['fields']=fields;duplicates.append({'sourceId':int(m[1]),'index':n+1});continue
  assert compact.startswith(key[1],cursor),(path.name,m[1],greek[:90],compact[cursor:cursor+90])
  start=refs[positions[cursor]];end=refs[positions[cursor+len(key[1])-1]];cursor+=len(key[1])
  assert all(fields.get(k) for k in ['中','结构','德']),(path.name,m[1])
  u={'id':len(units)+1,'sourceId':int(m[1]),'ref':start,'label':start if start==end else start+'–'+end,'speaker':m[2].split('；')[1] if '；' in m[2] else '苏格拉底','greek':greek,'fields':fields};units.append(u);seen[key]=u
 assert cursor==len(compact),(path.name,cursor,len(compact))
 return units,duplicates

def concise_structure(unit,conn):
 text=unit['fields']['结构'];greek=unit['greek'];words=re.findall(r'[^\W\d_]+[ʼ᾽’\']?',greek)
 generic=any(s in text for s in ['谓语动词：','主语／主格线索','依附于相应谓语','依语境','按格数与主语或名词联系','留意与格'])
 if not generic:return clean_structure(text.replace('无明示限定动词；须承接前句补出判断或系词；无明示宾格宾语。','谓语由上一问补出，这里只作简短回答。'))
 hints=unit['fields'].get('动词','');finite=[];inf=[]
 for m in re.finditer(r'([\u0370-\u03ff\u1f00-\u1fff]+[ʼ᾽’\']?)（([^）]+)）',hints):
  form,description=m.groups()
  if '不定式' in description:inf.append(form)
  elif any(x in description for x in ['直陈式','虚拟式','命令式','希求式','祈愿式']):
   key=norm(form)+("'" if form.endswith(('ʼ','᾽','’',"'")) else '')
   rows=conn.execute('SELECT pos,mood FROM morphology WHERE form_normalized=?',(key,)).fetchall()
   if any(r[0]=='verb' and r[1] in ('indicative','subjunctive','optative','imperative') for r in rows):finite.append(form)
 finite=list(dict.fromkeys(finite));inf=list(dict.fromkeys(inf));result=[]
 def has(w):return w in words
 if any(has(w) for w in ['ἐάν','ἐὰν','ἐάνπερ','ἐὰνπερ']):
  result.append('ἐάν 引出尚待实现的条件，后面的主句说明条件成立时的结果。')
 elif has('εἰ'):
  result.append('εἰ 从句提出假设'+('，ἄν 所在的主句再说明由此推得的结果。' if any(has(w) for w in ['ἄν','ἂν']) else '，主句在这个前提下继续发问或作出判断。'))
 elif has('πότερον') and has('ἢ'):result.append('πότερον 与 ἤ 配合，提出两个需要分辨的选择。')
 elif any(has(w) for w in ['ὅταν','ἐπειδάν','ἐπειδὰν']):result.append('时间从句使用虚拟式，指每逢所说情形发生之时；主句说明相应的情况。')
 elif any(has(w) for w in ['οἶμαι','οἶμαί','οἴει','νομίζω','νομίζεις','ἡγοῦμαι','ἡγῇ','δοκεῖς','δοκεῖ']) and inf:
  verb=next(w for w in words if w in ['οἶμαι','οἶμαί','οἴει','νομίζω','νομίζεις','ἡγοῦμαι','ἡγῇ','δοκεῖς','δοκεῖ']);result.append(verb+' 引出判断，'+ '、'.join(inf[:2])+' 所在的不定式结构补充判断的内容。')
 elif any(has(w) for w in ['δεῖ','χρή','χρὴ','χρῆν','ἀνάγκη']) and inf:
  verb=next(w for w in words if w in ['δεῖ','χρή','χρὴ','χρῆν','ἀνάγκη']);result.append(verb+' 表示必要，'+inf[0]+' 以不定式说明所涉及的事情。')
 elif has('ὥστε'):result.append('ὥστε 引出结果，说明前面所说的情形会造成什么。')
 elif has('ἵνα'):result.append('ἵνα 从句说明目的，须与主句的动作连起来理解。')
 elif has('ὅτι'):result.append('ὅτι 引出具体说明，嵌入前面的言说、认识或判断之中。')
 elif any(has(w) for w in ['ὅς','ὃς','ὃ','ἃ','ὧν','ᾧ','ὅσα','ὅσοι']):
  w=next(w for w in words if w in ['ὅς','ὃς','ὃ','ἃ','ὧν','ᾧ','ὅσα','ὅσοι']);result.append(w+' 引出关系从句，把所说的人或事限定得更具体。')
 if has('μὲν') and any(has(w) for w in ['δέ','δὲ']):result.append('μέν 与 δέ 分列前后两项，使两方面的情况相互对照。')
 elif has('οὔτε') and words.count('οὔτε')>1:result.append('οὔτε 重复使用，将几项否定并列在同一判断之下。')
 elif has('ἀλλά') or has('ἀλλὰ'):result.append('ἀλλά 转入正面的或经过修正的说法，与前面的否定相对。')
 if len(result)<2 and finite:
  selected=[w for w in finite if w not in ['ἔστιν','ἐστὶν','ἐστιν','ἐστίν','εἶναι']][:2] or finite[:1]
  result.append(('、'.join(selected)+' 是句中的限定动词，'+('发问时省略的内容承接前句。' if len(words)<=8 else '叙述或判断由这些动词展开。')))
 if not result:
  if inf:result.append('、'.join(inf[:2])+' 为不定式，动作的承担者和相关判断从上下文承接。')
  else:result.append('这是一句承接上文的简短回答，省略的谓语由前一句补足。')
 return clean_structure(''.join(result[:2]))

def prepare(spec,epub,resources,notes_dir):
 slug=spec['id'];path=notes_dir/spec['filename'];source=resources/f'{slug}-perseus-grc2.xml';units,duplicates=parse_uploaded(path,source)
 assert len(units)==spec['expected'],(slug,len(units))
 german=source_german(epub,spec);_,segments=german_segments([{'page':p,'german':v} for p,v in german.items()])
 omitted={391,407,408,792,793,1001,1002,1003,1004} if slug=='alcibiades1' else set()
 found=align_units([u for u in units if u['id'] not in omitted],segments,[u['fields']['德'] for u in units],max_b=20,strict_speakers=slug.startswith('alcibiades'))
 for i in omitted:found[i]={'text':'','sourcePage':'115' if i<=408 else '128' if i<=793 else '133','score':1,'status':'not-in-source'}
 conn=sqlite3.connect(f'file:{(resources/"morph.db").as_posix()}?mode=ro',uri=True);out=[];glosses={}
 edits_path=REPO/'tools/additional-classics-edits.json';edits=json.loads(edits_path.read_text(encoding='utf-8')) if edits_path.exists() else {}
 for u in units:
  record={k:u[k] for k in ['id','ref','label','speaker','greek']};f=found[u['id']]
  if slug=='apology' and record['id']==271:
   assert record['greek'].startswith('τ τί ἄξιός') and 'ἐμαυτὸν ῷ ὄντι' in record['greek']
   record['greek']=record['greek'][2:].replace('ἐμαυτὸν ῷ ὄντι','ἐμαυτὸν τῷ ὄντι')
  reading={'zh':u['fields']['中'],'de':f['text'],'structure':concise_structure(u,conn),'sourcePage':f['sourcePage']}
  if u['id'] in omitted:reading.update(deStatus='not-in-source',deNote='所提供的施莱尔马赫译本未收此句。')
  if u['id']==391 and slug=='alcibiades1':reading['deNote']='此处的肯定答语在所提供的施莱尔马赫译本中未单独译出。'
  reading.update(edits.get(f'{slug}:{u["id"]}',{}));record['reading']=reading;record['verbHints']=u['fields'].get('动词','');out.append(record)
  for m in re.finditer(r'([\u0370-\u03ff\u1f00-\u1fff]+)＝(.*?)(?=；[\u0370-\u03ff\u1f00-\u1fff]+＝|$)',u['fields'].get('生词','')):
   meaning=re.split('[／/]',m[2])[-1].strip('中 ：。 ')
   if re.search('[\u4e00-\u9fff]',meaning):glosses.setdefault(m[1],meaning)
 conn.close();dump(REPO/f'tools/{slug}-notes.json',out);dump(REPO/f'tools/{slug}-zh.json',glosses)
 (REPO/f'tools/{slug}-source.xml').write_bytes(source.read_bytes())
 report={'id':slug,'units':len(out),'range':spec['range'],'notesFile':path.name,'notesSha256':hashlib.sha256(path.read_bytes()).hexdigest(),'duplicateCopiesRemoved':duplicates,'germanFiles':spec['germanFiles'],'germanSegments':len(segments),'germanSourcePages':list(german),'alignmentMean':sum(f['score'] for f in found.values())/len(found),'low':[{'id':i,'score':f['score'],'de':f['text']} for i,f in found.items() if f['score']<.15]}
 report['groups']=list({tuple(f.get('unitGroup',[])):{'ids':f['unitGroup'],'de':f['text'],'score':f['score']} for f in found.values() if len(f.get('unitGroup',[]))>1}.values())
 report['germanOmissions']=sorted(omitted)
 report['correspondenceCorrections']={k:v['de'] for k,v in edits.items() if k.startswith(slug+':') and 'de' in v}
 dump(REPO/f'docs/{slug}-import-report.json',report);print(slug,'prepared',len(out),'German segments',len(segments),'low scores',len(report['low']))

def import_added(resources,epub,prepare_sources=False,notes_dir=None,only=None):
 for slug,spec in WORKS.items():
  if only and slug not in only:continue
  if prepare_sources:prepare(spec,epub,resources,notes_dir)
  if not (REPO/f'tools/{slug}-notes.json').exists():continue
  settings={**spec,'source':f'https://scaife.perseus.org/library/urn:cts:greekLit:tlg0059.{spec["tlg"]}/','release':spec.get('release','20261018-classics-4'),'proper':{**PROPER,**spec.get('proper',{})},'germanNames':{**GERMAN_NAMES,**spec.get('germanNames',{})},'glossFiles':['additional-classics-zh'],'germanLoader':lambda path,s=spec:source_german(path,s)}
  morph_path=REPO/f'tools/{slug}-morphology.json'
  if morph_path.exists():settings['morphology']=json.loads(morph_path.read_text(encoding='utf-8'))
  result=import_work(resources,epub,settings)
  report=REPO/f'docs/{slug}-import-report.json';data=json.loads(report.read_text(encoding='utf-8'));data['coverage']={k:result[k] for k in ['words','morphologyCoverage','germanLexiconCoverage','chineseGlossCoverage','unknownForms']};dump(report,data)

if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--resources',type=Path,default=REPO.parent/'tmp/classics-source');ap.add_argument('--german-epub',type=Path,required=True);ap.add_argument('--prepare',action='store_true');ap.add_argument('--notes-dir',type=Path,default=Path(r'C:\Users\Haowen_wei\Desktop'));ap.add_argument('--work',action='append',choices=list(WORKS));args=ap.parse_args()
 import_added(args.resources,args.german_epub,args.prepare,args.notes_dir,args.work)
