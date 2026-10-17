"""Prepare the three-field reading notes using existing German source quotations.

This program retrieves passages from the supplied Schleiermacher text. It does
not translate or generate German. Earlier note wording is only a search anchor.
"""
from pathlib import Path
import argparse,collections,difflib,html,json,math,re,unicodedata

ROOT=Path(__file__).resolve().parents[1]
FILES={
 'symposium':'Symposium_172a-223d_逐句精读_合订稿_原稿待校.txt',
 'philebus':'Philebus_11a-67b_逐句精读.txt',
 'sophist':'Sophist_216a-242b_逐句精读_阶段稿.txt',
}
def dump(path,data):path.write_text(json.dumps(data,ensure_ascii=False,separators=(',',':')),encoding='utf-8')
def anchors(work,project):
 text=(project/'output'/work/FILES[work]).read_text(encoding='utf-8-sig')
 pattern=r'\[(\d+[a-e][^\]\n]*；[^\]\n]+)\]'
 out=[]
 for m in re.finditer(pattern+r'(.*?)(?='+pattern.replace('(','(?:',1)+r'|\Z)',text,re.S):
  de=re.search(r'(?:^|\n|。|[”»])?德[：:]\s*(.*?)(?=中[：:]|\Z)',m[2],re.S)
  out.append(re.sub(r'\s+',' ',de[1]).strip() if de else '')
 return out
def words(text):
 text=text.lower().replace('ß','ss')
 text=re.sub(r'[äöü]',lambda m:{'ä':'a','ö':'o','ü':'u'}[m[0]],text)
 synonyms={'ja':'zustimmung','allerdings':'zustimmung','freilich':'zustimmung','gewiss':'zustimmung','ganz':'zustimmung','durchaus':'zustimmung','wahrlich':'zustimmung','richtig':'zustimmung','sicher':'zustimmung'}
 return [synonyms.get(w,w) for w in re.findall(r'[a-z]+',text)]
def german_segments(pages):
 text='';spans=[];speaker=''
 for page in pages:
  for para in page['german']:
   match=re.match(r'^(Sokrates|Alkibiades|Protarchos|Philebos|Theodoros|Theaitetos|Fremder|Apollodoros|Freund):',para)
   if match:speaker=match[1]
   start=len(text);text+=para+'\n\n';spans.append((start,len(text),page['page'],speaker))
 # Abbreviations must not break a sentence. Retain source character offsets.
 masked=re.sub(r'\b(?:o|d|h|z|B|u|a|usw|vgl)\.',lambda m:m[0][:-1]+'\u2024',text)
 cuts=[0]+[m.end() for m in re.finditer(r'[.!?;](?:[»”\"])?(?=\s|$)|\s[–—]\s',masked)]+[len(text)]
 result=[]
 for start,end in zip(cuts,cuts[1:]):
  quote=text[start:end].strip()
  if not quote:continue
  if not words(quote) and result:
   result[-1]['text']+=' '+quote;result[-1]['end']=end
   continue
  char_start=start+len(text[start:end])-len(text[start:end].lstrip())
  page,speaker=next(((p,sp) for s,e,p,sp in spans if s<=char_start<e),spans[-1][2:])
  result.append({'text':quote,'page':page,'start':start,'end':end,'speaker':speaker})
 return text,result
def align_units(units,segments,searches,max_b=7,strict_speakers=False):
 """Monotone alignment with a one-page band for sentences crossing page marks."""
 n,m=len(units),len(segments)
 anchors_by_id={u['id']:searches[u['id']-1] for u in units}
 speaker_map={'苏格拉底':'Sokrates','阿尔喀比亚德':'Alkibiades','阿尔西比亚德斯':'Alkibiades','普罗塔尔科斯':'Protarchos','斐勒布':'Philebos','忒奥多罗斯':'Theodoros','泰阿泰德':'Theaitetos','爱利亚客人':'Fremder','客人':'Fremder'}
 def greek_speakers(us):return [speaker_map.get(u['speaker'].split('（')[0],'') for u in us]
 def sequence(xs):return [x for i,x in enumerate(xs) if x and (i==0 or x!=xs[i-1])]
 tokenized=[set(words(s)) for s in [*anchors_by_id.values(),*(s['text'] for s in segments)]]
 df=collections.Counter(t for ts in tokenized for t in ts)
 weight={t:1+math.log((len(tokenized)+1)/(d+1)) for t,d in df.items()}
 def sim(a,b):
  aa=set(words(a));bb=set(words(b));common=aa&bb
  return 2*sum(weight.get(t,1) for t in common)/max(1,sum(weight.get(t,1) for t in aa)+sum(weight.get(t,1) for t in bb))
 atexts={};btexts={};asets={};bsets={}
 for i in range(n):
  for size in range(1,min(5,n-i)+1):
   atexts[i,size]=' '.join(anchors_by_id[u['id']] for u in units[i:i+size]);asets[i,size]=set(words(atexts[i,size]))
 for j in range(m):
  for size in range(1,min(max_b,m-j)+1):
   btexts[j,size]=' '.join(s['text'] for s in segments[j:j+size]);bsets[j,size]=set(words(btexts[j,size]))
 apages=[int(re.match(r'\d+',u['ref'])[0]) for u in units]
 bpages=[int(s['page']) for s in segments]
 bounds={p:(next(j for j,x in enumerate(bpages) if x>=p-1),next((j for j,x in enumerate(bpages) if x>p+1),m)) for p in set(apages)}
 speaker_sensitive=any(s['speaker'] in ('Protarchos','Theaitetos','Alkibiades') for s in segments)
 aspeakers={(i,k):sequence(greek_speakers(units[i:i+k])) for i,k in atexts}
 bspeakers={(j,k):sequence([s['speaker'] for s in segments[j:j+k]]) for j,k in btexts}
 atotal={k:sum(weight.get(t,1) for t in v) for k,v in asets.items()};btotal={k:sum(weight.get(t,1) for t in v) for k,v in bsets.items()}
 dp={(0,0):(0,None)};scores={}
 for i in range(n+1):
  lo,hi=bounds[apages[min(i,n-1)]]
  for j in range(lo,hi+1):
   if (i,j) not in dp:continue
   cost=dp[i,j][0]
   for na,nb in [(1,k) for k in range(1,max_b+1)]+[(k,1) for k in range(2,6)]+[(2,2),(2,3),(3,2)]:
    if i+na>n or j+nb>m:continue
    a=atexts[i,na];b=btexts[j,nb]
    aa=asets[i,na];bb=bsets[j,nb]
    similarity=2*sum(weight.get(t,1) for t in aa&bb)/max(1,atotal[i,na]+btotal[j,nb])
    length_a=len(a) or sum(len(u['greek'])*1.8 for u in units[i:i+na])
    length_b=len(b)
    penalty=abs(math.log(max(8,length_a)/max(8,length_b)))
    asp=aspeakers[i,na];bsp=bspeakers[j,nb]
    speaker_penalty=4 if speaker_sensitive and asp and bsp and asp!=bsp else 0
    if strict_speakers and speaker_penalty:speaker_penalty=10 if na==1 else .5
    page_penalty=.35*abs(apages[i]-bpages[j])
    step=(1-similarity)*na+min(2.5,penalty)*.28+.55*(na-1)+.08*(nb-1)+speaker_penalty+page_penalty
    target=(i+na,j+nb)
    if target not in dp or cost+step<dp[target][0]:dp[target]=(cost+step,(i,j,na,nb,similarity))
 if (n,m) not in dp:raise ValueError(f'No alignment path: {n} units, {m} source segments')
 result={};at=(n,m)
 while at!=(0,0):
  i,j,na,nb,score=dp[at][1]
  quote=' '.join(s['text'] for s in segments[j:j+nb])
  for u in units[i:i+na]:result[u['id']]={'text':quote,'sourcePage':segments[j]['page'],'unitGroup':[x['id'] for x in units[i:i+na]],'score':round(score,4),'segments':[j,j+nb]}
  at=(i,j)
 return result
def clean_structure(text):
 # Keep the grammatical explanation, removing the old rhetorical commentary.
 text=re.split(r'句法(?:与风格)?[（(：:]|句法[（(]',text,maxsplit=1)[0].strip()
 text=text.replace('主语／主格线索：','主语为').replace('主语/主格线索：','主语为').replace('主语线索：','主语为')
 text=text.replace('主语为由','主语由')
 text=re.sub(r'([^；。]*?)线索：',r'\1：',text)
 text=re.sub(r'（[^）]*(?:Schadewaldt|Wilamowitz|Riddell|准则)[^）]*）','',text)
 text=text.replace('！','。').replace('!','。')
 text=re.sub(r'\s*\b\d+\.\s*','',text)
 for old,new in [('故意压在','放在'),('压在','放在'),('甩出','接上'),('亮出','给出'),('死死钉住','限定'),('钉住','限定'),('绝非','不是'),('强力',''),('强重读','重读'),('大跨度',''),('骨架','主干'),('线索','关系')]:text=text.replace(old,new)
 text=re.sub(r'\s+',' ',text).strip('；; ')
 text=re.sub(r'([\u0370-\u03ff\u1f00-\u1fff])([\u4e00-\u9fff])',r'\1 \2',text)
 text=re.sub(r'([\u4e00-\u9fff])([\u0370-\u03ff\u1f00-\u1fff])',r'\1 \2',text)
 return text.rstrip('。')+'。'
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--project',type=Path,default=ROOT.parent);ap.add_argument('--apply',action='store_true');args=ap.parse_args()
 reports={};all_overrides={};edits=json.loads((ROOT/'tools/classics-structure-edits.json').read_text(encoding='utf-8'))
 for work in FILES:
  meta=json.loads((ROOT/f'data/classics/{work}/catalog.json').read_text(encoding='utf-8'))
  pages=[json.loads((ROOT/f'data/classics/{work}/{p}.json').read_text(encoding='utf-8')) for p in meta['pages']]
  units=[u for p in pages for u in p['units']];searches=anchors(work,args.project)
  assert len(searches)==len(units),(work,len(searches),len(units))
  text,segs=german_segments(pages)
  if work=='sophist':
   # The supplied Greek ends at 242b, earlier than the end of German page 242.
   stop=next(i for i,s in enumerate(segs) if 'deshalb also gehe nur dreist zu.' in s['text'])
   segs=segs[:stop+1]
  results=align_units(units,segs,searches)
  low=[]
  for u in units:
   found=results[u['id']]
   if found['score']<.25:low.append({'id':u['id'],'ref':u['ref'],'de':found['text'],'score':found['score']})
   key=f'{work}:{u["id"]}'
   all_overrides[key]={'zh':u['notes'].get('中',''),'de':found['text'],'structure':edits.get(key,clean_structure(u['notes'].get('结构',''))),'sourcePage':found['sourcePage'],'alignment':{'group':found['unitGroup'],'score':found['score']}}
  reports[work]={'units':len(units),'segments':len(segs),'low':low,'mean':sum(x['score'] for x in results.values())/len(results)}
  print(work,'units',len(units),'German segments',len(segs),'mean',round(reports[work]['mean'],3),'low',len(low))
 dump(ROOT/'tools/classics-reading-notes.json',all_overrides)
 dump(ROOT/'docs/classics-alignment-review.json',reports)
 if args.apply:
  for work in FILES:
   for path in (ROOT/f'data/classics/{work}').glob('*.json'):
    if path.name=='catalog.json':continue
    data=json.loads(path.read_text(encoding='utf-8'))
    for u in data['units']:
     if u.get('reading',{}).get('ownerEdited'):continue
     u['reading']=all_overrides[f'{work}:{u["id"]}'];u['notes']={'中':u['reading']['zh'],'结构':u['reading']['structure']}
    data['germanSource']['alignment']='句段摘录见units.reading；整数页文本保留作来源索引'
    dump(path,data)
if __name__=='__main__':main()
