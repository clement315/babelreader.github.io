"""Publish a proofread standalone reader as a shell plus per-question JSON.

Usage: python tools/import_proofread_summa.py /path/to/proofread/summa.html
The supplied bilingual text is copied exactly; this tool never translates it.
"""
from pathlib import Path
import argparse,copy,hashlib,json,re

def write(path,text):
    path.parent.mkdir(parents=True,exist_ok=True)
    temp=path.with_name(path.name+'.import-tmp')
    temp.write_text(text,encoding='utf8',newline='\n');temp.replace(path)

def encoded(obj):return json.dumps(obj,ensure_ascii=False,separators=(',',':'))

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('reader',type=Path)
    parser.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1])
    args=parser.parse_args();root=args.root.resolve()
    html=args.reader.read_text(encoding='utf8')
    pattern=r'(<script id="summa-fallback" type="application/json">)(.*?)(</script>)'
    match=re.search(pattern,html,re.S)
    if not match:raise ValueError('Missing embedded reader data')
    data=json.loads(match[2]);assert data.get('standalone') and data.get('proofreading')
    assert len(data['questions'])==613
    digest=hashlib.sha256(args.reader.read_bytes()).hexdigest()
    version='proofread-1-'+digest[:12]
    public_metadata=copy.deepcopy(data['proofreading'])
    public_metadata.pop('source_pdf',None)
    public_metadata['source_document']='Summa theologiae.pdf'
    catalog=copy.deepcopy(data['catalog']);catalog['release']=version
    catalog['scope']=data['scope'];catalog['proofreading']=public_metadata
    write(root/'data/summa/catalog.json',encoded(catalog)+'\n')
    for q in data['questions'].values():
        write(root/f'data/summa/{q["part"]}/q{q["question"]}.json',encoded(q)+'\n')
    write(root/'data/summa/proofreading.json',encoded({'release':version,'proofreading':public_metadata,
          'source_gaps':data.get('proofreading_source_gaps',[])})+'\n')
    fallback_part=copy.deepcopy(catalog['parts'][0])
    fallback_part['questions']=[q for q in fallback_part['questions'] if q['number']==1]
    fallback={'standalone':False,'release':version,'catalog':{'schema_version':1,'title':catalog['title'],'parts':[fallback_part]},
              'question':data['questions']['I:1'],'scope':data['scope'],
              'general_prologue':data['general_prologue'],'part_prologues':data['part_prologues'],
              'proofreading':public_metadata}
    html=html[:match.start(2)]+encoded(fallback).replace('<','\\u003c')+html[match.end(2):]
    # Locate the one inline dictionary adapter by its distinctive content.
    adapter=re.search(r'<script>\s*/\* Optional adapters.*?</script>',html,re.S)
    assert adapter,'Missing dictionary adapter'
    html=html[:adapter.start()]+f'<script src="./assets/summa-integrations.js?v={version}" defer></script>'+html[adapter.end():]
    old="async function fetchJSON(url,signal){const response=await fetch(url,{signal});"
    new="async function fetchJSON(url,signal){const versioned=new URL(url,location.href);versioned.searchParams.set('v',fallback.release);const response=await fetch(versioned,{signal});"
    assert html.count(old)==1;html=html.replace(old,new)
    old=next(line for line in html.splitlines() if "$('catalog-count').textContent=" in line)
    new="""      const main=state.catalog.parts.filter(p=>p.id!=='APPENDICES');const appendices=state.catalog.parts.find(p=>p.id==='APPENDICES');
      const questions=main.reduce((n,p)=>n+p.questions.length,0);const articles=main.reduce((n,p)=>n+p.questions.reduce((m,q)=>m+q.articles.length,0),0);
      $('catalog-count').textContent=state.fallback?'內置第一問示例 · 10 節':`正文 ${questions} 問 · ${articles} 節${appendices?'｜附錄 '+appendices.questions.length+' 題 · '+appendices.questions.reduce((n,q)=>n+q.articles.length,0)+' 節':''}`;"""
    html=html.replace(old,new)
    marker='五部正文 ＋ 補編附錄・繁體離線本'
    assert marker in html;html=html.replace(marker,'五部正文 ＋ 補編附錄・繁體中文')
    # A short editorial status belongs to the reader, not to the translated text.
    insert='<p>原PDF校對初修 · 尚待逐字校訂 <a href="./docs/summa/revisions.txt" target="_blank" rel="noopener">修訂記錄</a></p>'
    pos=html.index('<div class="sidebar-brand">');end=html.index('</p></div>',pos)+len('</p>')
    html=html[:end]+insert+html[end:]
    write(root/'summa.html',html)
    # The adapter is independent of the EPUB reader and accepts existing hooks.
    assert (root/'assets/summa-integrations.js').exists()
    for q in data['questions'].values():
        actual=json.loads((root/f'data/summa/{q["part"]}/q{q["question"]}.json').read_text(encoding='utf8'))
        assert actual==q,q['id']
    report={'release':version,'source_reader_sha256':digest,'question_files':613,
            'articles':sum(len(q['articles']) for q in data['questions'].values()),
            'all_question_data_exactly_preserved':True,'reader_bytes':(root/'summa.html').stat().st_size,
            'catalog_bytes':(root/'data/summa/catalog.json').stat().st_size,'proofreading_changes':public_metadata['changes']}
    write(root/'docs/summa/import-validation.json',json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(report,ensure_ascii=False,indent=2))

if __name__=='__main__':main()
