"""Statesman: complete Perseus Greek and newly composed Chinese readings.

German is quoted from the owner's Schleiermacher EPUB, never translated.
Greek paragraphs follow the edition's said elements; source turns are checked
before alignment. The documented last speaker-label variant is retained.
"""
from pathlib import Path
import argparse, hashlib, json, re, xml.etree.ElementTree as ET
from import_classics import REPO, dump
from import_additional_classics import source_german, PROPER, GERMAN_NAMES
from import_parmenides import import_work
from import_gorgias import align_turn
from simplify_classics import german_segments

SPEC={'id':'statesman','title':'政治家篇','latin':'Statesman','greekTitle':'Πολιτικός','range':'257a–311c','start':257,'end':311,'germanFiles':['part0016.xhtml'],'germanHeading':'Der Staatsmann','germanEdition':'用户提供的EPUB；本篇标注Akademie Verlag Berlin 1986','corpus':'Plato (0059) - Statesman (008).xml','source':'https://scaife.perseus.org/library/urn:cts:greekLit:tlg0059.tlg008/','release':'20261025-classics-7','glossFiles':['additional-classics-zh','alcibiades1-zh','alcibiades2-zh','apology-zh','alcibiades2-zh-supplement','gorgias-zh-supplement']}
SPEAKERS={'Sokrates':'苏格拉底','Theodoros':'忒奥多罗斯','Fremder':'异乡人','Der jüngere Sokrates':'青年苏格拉底'}
NAMES={'Θεόδωρος':('忒奥多罗斯','Theodoros'),'Θεαίτητος':('泰阿泰德','Theaitetos'),'Ἄμμων':('阿蒙神','Ammon'),'Ἀτρεύς':('阿特柔斯','Atreus'),'Θυέστης':('梯厄斯忒斯','Thyestes'),'Κρόνος':('克洛诺斯','Kronos'),'Προμηθεύς':('普罗米修斯','Prometheus'),'Ἥφαιστος':('赫淮斯托斯','Hephaistos'),'Νεῖλος':('尼罗河','Nil'),'Θετταλικός':('色萨利的','Thessalischen'),'Λυδός':('吕底亚人','Lyder'),'Φρύξ':('弗里吉亚人','Phryger'),'Κένταυρος':('半人马','Kentauren'),'Σάτυρος':('萨堤尔','Satyren'),'Αἴγυπτος':('埃及','Ägypten')}

EXTRA_RESPONSES={
 'οὕτως.':['正是这样。','οὕτως 单独认可上一句的说法，谓语承前省略。'],
 'δῆλον.':['很清楚。','δῆλον 省略系词，所说清楚的内容见上一问。'],
 'ὀρθῶς.':['对。','ὀρθῶς 以副词认可前面的区分或推论。'],
 'ὀρθότατα.':['再正确不过。','ὀρθότατα 为最高级，加强对前述判断的赞同。'],
 'πῶς;':['怎么说？','πῶς 单独追问说法的含义或理由，等待对方说明。'],
 'πῇ;':['从哪条路？','πῇ 追问考察或划分所循的方向。'],
 'τὸ ποῖον;':['哪一点？','τὸ ποῖον 将问题集中在前句尚待指明的内容。'],
 'ποῖον;':['什么呢？','ποῖον 承接前句提出而尚未具体说明的事项。'],
 'τί δή;':['为什么呢？','τί δή 催对方说出前面判断的理由或具体所指。'],
 'ποῖον δή;':['究竟是什么？','ποῖον 追问具体内容，δή 加强须说清楚的语气。'],
 'τὸ ποῖον δή;':['究竟哪一点？','τὸ ποῖον 承接待说明的事项，δή 催请明确。'],
 'ἀληθέστατα.':['完全正确。','ἀληθέστατα 以最高级认可对方所说，省略言说动词。'],
 'παντάπασι μὲν οὖν.':['完全如此。','παντάπασι 加 μὲν οὖν，加强肯定，不另立转折。'],
 'πῶς εἶπες;':['你这话怎么说？','πῶς εἶπες 对刚才的表达提出澄清要求。'],
 'λέγοις ἄν.':['请说吧。','λέγοις ἄν 用潜能希求式，作有礼的邀请。'],
 'ἀληθῆ.':['是这样。','ἀληθῆ 为中性复数，省略「你说的」，确认陈述真实。'],
 'καλῶς.':['很好。','καλῶς 以副词认可刚才的表述或安排。'],
 'τίνι;':['按什么？','τίνι 用与格追问划分所凭的依据。'],
 'οὐκοῦν χρή.':['当然该这样。','χρή 的不定式内容从上文补足，οὐκοῦν 确认其必要。'],
 'ἔμοιγε.':['至少我同意。','ἔμοιγε 为判断者与格，承接上文的「看来」或「同意」。'],
 'κάλλιστʼ εἶπες.':['你说得极好。','κάλλιστα 的最高级修饰 εἶπες，认可刚才的提议。'],
 'κάλλιστʼ εἴρηκας.':['你说得极好。','εἴρηκας 用完成时，认可刚已完成的表述。'],
 'τίνων;':['哪些事情？','τίνων 为属格，承接上文关系或介词结构中的对象。'],
 'μανθάνω.':['我明白了。','μανθάνω 表示此刻领会对方的说明。'],
 'καὶ πάνυ γε.':['确实如此。','καὶ πάνυ γε 加强对上一判断的认可。'],
 'λέγεις ὀρθῶς.':['你说得对。','ὀρθῶς 修饰 λέγεις，确认对方刚作的区分。'],
 'πάντως που.':['无疑是这样。','πάντως 加强确认，που 保留对谈中的缓和口气。'],
 'ἔοικε γοῦν.':['看来确是这样。','ἔοικε 表似然，γοῦν 把同意落实在刚才的推断。'],
 'πῶς φῄς;':['你这话是什么意思？','πῶς 追问 φῄς 所说内容，要求进一步解释。'],
 'καὶ σφόδρα γε.':['确实很是如此。','σφόδρα 与 γε 加强同意的程度。'],
 'τὸ γοῦν εἰκός.':['至少很可能如此。','τὸ εἰκός 省略系词，γοῦν 限定为合乎情理的推断。'],
 'πῶς γάρ;':['怎么会呢？','πῶς γάρ 用反问认可前述否定，具体谓语从上文补出。']}

def editorial_readings():
 responses=json.loads((REPO/'tools/gorgias-responses.json').read_text(encoding='utf-8'));responses.update(EXTRA_RESPONSES)
 edits={}
 for path in sorted((REPO/'tools/statesman-reading').glob('*.txt')):
  for line in path.read_text(encoding='utf-8').splitlines():
   if not line.strip():continue
   key,zh,structure=line.split('|');key=int(key);assert key not in edits,key
   assert zh and structure;edits[key]={'zh':zh,'structure':structure}
 return responses,edits

def align_german(records,german):
 greek=[]
 for u in records:
  if not greek or greek[-1]['speaker']!=u['speaker']:greek.append({'speaker':u['speaker'],'units':[]})
  greek[-1]['units'].append(u)
 turns=[];speaker=''
 for page,paras in german.items():
  for text in paras:
   match=re.match(r'^(Der jüngere Sokrates|Sokrates|Theodoros|Fremder):',text)
   if match:speaker=SPEAKERS[match[1]]
   assert speaker
   if not turns or turns[-1]['speaker']!=speaker:turns.append({'speaker':speaker,'parts':[]})
   turns[-1]['parts'].append({'page':page,'german':[text]})
 assert len(greek)==len(turns)==891,(len(greek),len(turns))
 assert [x['speaker'] for x in greek[:-1]]==[x['speaker'] for x in turns[:-1]]
 assert greek[-1]['speaker']=='青年苏格拉底' and turns[-1]['speaker']=='苏格拉底'
 report=[]
 for a,b in zip(greek,turns):
  _,segments=german_segments(b['parts']);found=align_turn(a['units'],segments,{},{} )
  for u in a['units']:
   item=found[u['id']];u['reading'].update(de=item['text'],sourcePage=item['sourcePage'])
   report.append({'id':u['id'],'ref':u['ref'],**item})
 # One German sentence joins the end of Greek 300 to the start of 301.
 # Retain that complete literal sentence in both relevant readings.
 r={u['id']:u['reading'] for u in records}
 boundary=r[301]['de'].index('Eben so also auch,')
 r[300]['de']+=' '+r[301]['de'][:boundary].strip()
 # The translator carries 660's question across a semicolon into 661.
 boundary=r[661]['de'].index('Und was auch')
 question=r[660]['de']+' '+r[661]['de'][:boundary].strip()
 r[660]['de']=question
 r[661]['de']=question+' '+r[661]['de'][boundary:]
 for item in report:item['text']=r[item['id']]['de']
 return report

def canonical_units(source):
 body=ET.parse(source).find('.//{http://www.tei-c.org/ns/1.0}body');records=[];ref=''
 greek_speakers={'#Σωκράτης':'苏格拉底','#Θεόδωρος':'忒奥多罗斯','#Ξένος':'异乡人','#Νεώτερος Σωκράτης':'青年苏格拉底'}
 for said in body.iter('{http://www.tei-c.org/ns/1.0}said'):
  chars=[];refs=[]
  def append(text):
   for char in text:chars.append(char);refs.append(ref)
  def visit(e):
   nonlocal ref
   if e.tag.rsplit('}',1)[-1]=='milestone' and re.fullmatch(r'\d+[a-e]',e.get('n','')):ref=e.get('n')
   append(e.text or '')
   for child in e:
    if child.tag.rsplit('}',1)[-1] not in ('del','note','head','label','bibl'):visit(child)
    append(child.tail or '')
  visit(said);raw=''.join(chars);idx=[i for i,c in enumerate(raw) if not c.isspace()];first,last=refs[idx[0]],refs[idx[-1]]
  records.append({'id':len(records)+1,'ref':first,'label':first if first==last else first+'–'+last,'speaker':greek_speakers[said.get('who')],'greek':re.sub(r'\s+',' ',raw).strip()})
 assert len(records)==898
 return records

def prepare(resources,epub):
 source=resources/'statesman-perseus-grc2.xml';records=canonical_units(source);dump(REPO/'tools/statesman-units.json',records)
 glosses={}
 for line in (REPO/'tools/statesman-lexicon.txt').read_text(encoding='utf-8').splitlines():
  keys,meaning=line.split('|')
  for key in keys.split(','):glosses[key]=meaning
 dump(REPO/'tools/statesman-zh-supplement.json',glosses)
 responses,edits=editorial_readings()
 for u in records:
  if u['id'] in edits:reading=edits[u['id']]
  else:
   zh,structure=responses[u['greek']];reading={'zh':zh,'structure':structure}
  u['reading']={**reading,'de':''}
 german=source_german(epub,SPEC);alignment=align_german(records,german)
 (REPO/'tools/statesman-source.xml').write_bytes(source.read_bytes())
 dump(REPO/'tools/statesman-notes.json',records);dump(REPO/'docs/statesman-alignment-review.json',alignment)
 dump(REPO/'docs/statesman-import-report.json',{'id':'statesman','range':SPEC['range'],'units':898,'pages':55,'editorialChineseUnits':898,'individualReadings':len(edits),'reusedShortAnswers':898-len(edits),'greekSourceSha256':hashlib.sha256(source.read_bytes()).hexdigest(),'sourceTurns':891,'germanTurns':891,'germanFiles':SPEC['germanFiles'],'speakerLabelVariant':{'id':898,'ref':'311c','greek':'青年苏格拉底','german':'Sokrates'},'chineseMethod':'按馆主指定的 Plato Dialogue Style 从希腊原文重新翻译；结构逐段编写。','sharedGermanGroups':[[300,301],[660,661]],'germanAlignment':'发言次序核对后在发言内部匹配；300–301、660–661保留跨单元的完整德文原句。'})
 print('Prepared',len(records),'units; verified 891 turns (documented final label variant).',flush=True)

def settings():
 spec={**SPEC,'proper':{**PROPER,**{k:v[0] for k,v in NAMES.items() if k!='Θετταλικός'}},'germanNames':{**GERMAN_NAMES,**{k:v[1] for k,v in NAMES.items()}},'germanLoader':lambda path:source_german(path,SPEC)}
 morph=REPO/'tools/statesman-morphology.json'
 if morph.exists():spec['morphology']=json.loads(morph.read_text(encoding='utf-8'))
 return spec

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--resources',type=Path,default=REPO.parent/'tmp/classics-source');ap.add_argument('--german-epub',type=Path,required=True);ap.add_argument('--prepare',action='store_true');args=ap.parse_args()
 if args.prepare:prepare(args.resources,args.german_epub)
 result=import_work(args.resources,args.german_epub,settings());path=REPO/'docs/statesman-import-report.json';report=json.loads(path.read_text(encoding='utf-8'));report['coverage']={k:result[k] for k in ['words','morphologyCoverage','germanLexiconCoverage','chineseGlossCoverage','corpusAlignmentCoverage','unknownForms']};dump(path,report)

if __name__=='__main__':main()
