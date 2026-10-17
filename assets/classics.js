(() => {
 'use strict';
 const $=id=>document.getElementById(id), layout=document.querySelector('.close-layout');
 const release='20261017-classics-2';
 let catalog,meta,pageData,lexicon,currentWord,activeButton,generation=0,lookupGeneration=0,font=25;
 const cache=new Map();
 const readStore=k=>{try{return localStorage.getItem(k);}catch{return null;}};
 const save=(k,v)=>{try{localStorage.setItem(k,v);}catch{}};
 const el=(tag,cls,text)=>{const e=document.createElement(tag);if(cls)e.className=cls;if(text!==undefined)e.textContent=text;return e;};
 const get=async path=>{
  const url=`data/classics/${path}?v=${release}`;
  if(!cache.has(url))cache.set(url,fetch(url).then(r=>{if(!r.ok)throw Error('资料未能载入（'+r.status+'）');return r.json();}).catch(e=>{cache.delete(url);throw e;}));
  return cache.get(url);
 };
 const labels={noun:'名词 · Substantiv',verb:'动词 · Verb',adjective:'形容词 · Adjektiv',adverb:'副词 · Adverb',pronoun:'代词 · Pronomen',article:'冠词 · Artikel',particle:'小品词 · Partikel',preposition:'介词 · Präposition',conjunction:'连词 · Konjunktion',interjection:'感叹词 · Interjektion',participle:'分词 · Partizip',numeral:'数词 · Numerale',proper_noun:'专有名词 · Eigenname',nominative:'主格 · Nominativ',genitive:'属格 · Genitiv',dative:'与格 · Dativ',accusative:'宾格 · Akkusativ',vocative:'呼格 · Vokativ',masculine:'阳性 · Maskulinum',feminine:'阴性 · Femininum',neuter:'中性 · Neutrum',singular:'单数 · Singular',plural:'复数 · Plural',dual:'双数 · Dual',present:'现在时 · Präsens',imperfect:'未完成过去时 · Imperfekt',aorist:'不定过去时 · Aorist',perfect:'完成时 · Perfekt',pluperfect:'过去完成时 · Plusquamperfekt',future:'将来时 · Futur',future_perfect:'将来完成时 · Futur II',active:'主动 · Aktiv',middle:'中动 · Medium',passive:'被动 · Passiv',mediopassive:'中被动 · Mediopassiv',indicative:'直陈式 · Indikativ',subjunctive:'虚拟式 · Konjunktiv',optative:'祈愿式 · Optativ',imperative:'命令式 · Imperativ',infinitive:'不定式 · Infinitiv','1st':'第一人称 · 1. Person','2nd':'第二人称 · 2. Person','3rd':'第三人称 · 3. Person',comparative:'比较级 · Komparativ',superlative:'最高级 · Superlativ',positive:'原级 · Positiv'};
 const translate=v=>v?v.split('/').map(x=>labels[x]||x).join(' / '):'未标注';
 const greek=s=>/[\u0370-\u03ff\u1f00-\u1fff]/u.test(s)&&/\p{Letter}/u.test(s);
 const closePanel=(focus=false)=>{
  lookupGeneration++;
  $('word-panel').hidden=true;layout.classList.remove('has-panel');
  if(activeButton){activeButton.setAttribute('aria-pressed','false');if(focus)activeButton.focus();}
  currentWord=null;
 };
 const inspect=async(button,u,word,index)=>{
  const lookup=++lookupGeneration;
  if(activeButton)activeButton.setAttribute('aria-pressed','false');activeButton=button;button.setAttribute('aria-pressed','true');currentWord=word;
  $('word-panel').hidden=false;layout.classList.add('has-panel');
  const host=$('word-content');host.replaceChildren(el('h2','selected-form',word),el('p','selected-context',`${meta.title} · ${u.label}`));
  const analyses=pageData.analyses[u.analyses[index]]||[];
  host.append(el('p','analysis-notice',analyses.length>1?`${analyses.length} 种可能的分析，请结合上下文判断。`:analyses.length?'':'暂无词形分析。'));
  try{if(!lexicon)lexicon=await get('pape.json');}catch{host.append(el('p','analysis-notice','Pape词典暂时未能载入。重新点击词语可重试。'));}
  if(currentWord!==word||lookup!==lookupGeneration)return;
  for(const [i,a] of analyses.entries()){
   const card=el('section','candidate');card.append(el('span','candidate-number',`候选 ${i+1}`),el('h3','',a.lemma),el('span','pos-pill',labels[a.pos]||'词类未标注'));
   const dl=el('dl','morph-grid');
   for(const [key,title] of [['case','格 · Kasus'],['gender','性 · Genus'],['number','数 · Numerus'],['tense','时态 · Tempus'],['voice','语态 · Diathese'],['mood','语气 · Modus'],['person','人称 · Person'],['degree','级 · Grad']]){
    if(a[key])dl.append(el('dt','',title),el('dd','',translate(a[key])));
   }
   if(dl.children.length)card.append(dl);
   card.append(el('span','gloss-label','中文释义'),el('p','zh-gloss',a.zh||'暂无中文释义。'));
   card.append(el('span','gloss-label','DEUTSCH · PAPE 原词条'));
   const entries=lexicon?.[a.de]||[];
   if(a.deName){const name=el('p','pape-entry',a.deName+' · Schleiermacher 本页译名');name.lang='de';card.append(name);}
   if(!entries.length&&!a.deName)card.append(el('p','zh-gloss','暂无 Pape 词条。'));
   for(const entry of entries){
    const snippet=el('p','pape-entry',entry.text.slice(0,220)+(entry.text.length>220?'…':''));snippet.lang='de';card.append(snippet);
    const d=el('details','pape-entry');d.append(el('summary','',entry.lemma+' · 展开完整词条'));const full=el('div','pape-full',entry.text);full.lang='de';d.append(full);card.append(d);
   }
   const raw=el('details','raw-morph');raw.append(el('summary','','词形标签'),el('p','',a.raw));card.append(raw);
   const source=el('a','source-link','Pape · PTA电子本 ↗');source.href='https://github.com/PatristicTextArchive/pta_lexika';source.target='_blank';source.rel='noopener';card.append(source);host.append(card);
  }
  $('word-panel').scrollTop=0;
 };
 const renderUnits=()=>{
  const fragment=document.createDocumentFragment();
  for(const u of pageData.units){
   const section=el('article','greek-unit');section.id='unit-'+u.id;section.dataset.ref=u.ref;
   const head=el('div','unit-head');head.append(el('span','ref',u.label),el('span','',u.speaker));
   const note=el('button','unit-note','句读笔记');note.type='button';note.setAttribute('aria-expanded','false');note.setAttribute('aria-controls','note-'+u.id);head.append(note);
   const p=el('p','greek-line');p.lang='grc';
   for(const [index,token] of u.tokens.entries()){
    if(!greek(token)){p.append(document.createTextNode(token));continue;}
    const word=el('button','greek-word',token);word.type='button';word.setAttribute('aria-label',token+'：查看形态与释义');word.setAttribute('aria-pressed','false');word.addEventListener('click',()=>inspect(word,u,token,index));p.append(word);
   }
   const details=el('div','unit-translation');details.id='note-'+u.id;details.hidden=true;
   const reading=u.reading||{zh:u.notes['中'],de:'',structure:u.notes['结构']};
   for(const [key,label,lang] of [['zh','中文译文','zh-CN'],['de','施莱尔马赫译文','de'],['structure','结构分析','zh-CN']]){
    const field=el('section','note-field');const paragraph=el('p','',reading[key]||'');paragraph.lang=lang;
    field.append(el('h3','note-label',label),paragraph);details.append(field);
   }
   note.addEventListener('click',()=>{details.hidden=!details.hidden;note.setAttribute('aria-expanded',String(!details.hidden));});
   section.append(head,p,details);fragment.append(section);
  }
  $('reading-content').replaceChildren(fragment);
 };
 const error=(message,work,page)=>{
  $('reading-content').replaceChildren();const box=el('div','close-error');box.append(el('p','',message));const retry=el('button','retry-button','重新载入');retry.addEventListener('click',()=>navigate(work,page,false));box.append(retry);$('reading-content').append(box);
 };
 const navigate=async(work,page,push=true,ref='')=>{
  const token=++generation;closePanel();$('reading-content').setAttribute('aria-busy','true');$('reader-status').textContent='正在载入…';$('reading-content').replaceChildren();
  try{
   const nextMeta=await get(`${work}/catalog.json`);if(token!==generation)return;
   const nextPage=String(page||nextMeta.pages[0]);
   if(!nextMeta.pages.includes(nextPage))throw Error(`这份${nextMeta.title}精读稿没有收录第${nextPage}页。`);
   const data=await get(`${work}/${nextPage}.json`);if(token!==generation)return;
   meta=nextMeta;pageData=data;
   $('work-select').value=work;$('page-select').replaceChildren(...meta.pages.map(p=>new Option(p,p)));$('page-select').value=nextPage;$('page-select').disabled=false;
   $('work-title').textContent=meta.title;$('work-subtitle').textContent=meta.greekTitle+' · '+meta.latin;
   $('work-range').textContent='收录范围 '+meta.range;$('greek-source').href=meta.source;
   $('page-label').textContent='STEPHANUS '+nextPage;
   const index=meta.pages.indexOf(nextPage);$('prev-page').disabled=index===0;$('next-page').disabled=index===meta.pages.length-1;
   renderUnits();$('reader-status').textContent=`第 ${index+1} / ${meta.pages.length} 页 · 点击词语查阅`;
   const url=new URL(location.href);url.searchParams.set('work',work);url.searchParams.set('page',nextPage);if(ref)url.searchParams.set('ref',ref);else url.searchParams.delete('ref');
   if(push)history.pushState(null,'',url);else history.replaceState(null,'',url);
   save('babel-classics:'+work,nextPage);document.title=meta.title+' '+nextPage+' · 古典作品精读';
   if(ref){const unit=[...document.querySelectorAll('.greek-unit')].find(n=>n.dataset.ref===ref);if(unit){unit.classList.add('is-current');unit.scrollIntoView({block:'start'});}}
  }catch(e){if(token===generation){$('reader-status').textContent='载入未完成';error(e.message+' 请使用左侧目录选择已收录的页码。',work,page);}}
  finally{if(token===generation)$('reading-content').setAttribute('aria-busy','false');}
 };
 $('close-panel').addEventListener('click',()=>closePanel(true));document.addEventListener('keydown',e=>{if(e.key==='Escape')closePanel(true);});
 $('work-select').addEventListener('change',e=>navigate(e.target.value,readStore('babel-classics:'+e.target.value)));
 $('page-select').addEventListener('change',e=>navigate(meta.id,e.target.value));
 for(const [id,step] of [['prev-page',-1],['next-page',1]])$(id).addEventListener('click',()=>{const p=meta.pages[meta.pages.indexOf(pageData.page)+step];if(p){navigate(meta.id,p);$('greek-text').scrollIntoView({block:'start'});}});
 $('jump-form').addEventListener('submit',e=>{e.preventDefault();const value=$('jump-ref').value.trim();const m=/^(\d+)([a-e])?$/.exec(value);if(m)navigate(meta.id,m[1],true,m[2]?value:'');else $('reader-status').textContent='请输入页码或小节，例如172或172a。';});
 const fontSize=()=>document.body.style.setProperty('--reading-size',font+'px');
 $('font-down').addEventListener('click',()=>{font=Math.max(18,font-2);fontSize();});$('font-up').addEventListener('click',()=>{font=Math.min(38,font+2);fontSize();});
 const theme=dark=>{document.body.classList.toggle('dark',dark);$('theme-toggle').setAttribute('aria-pressed',String(dark));save('babel-classics-theme',dark?'dark':'light');};
 theme(readStore('babel-classics-theme')==='dark');$('theme-toggle').addEventListener('click',()=>theme(!document.body.classList.contains('dark')));
 window.addEventListener('popstate',()=>{const p=new URLSearchParams(location.search);navigate(p.get('work')||'symposium',p.get('page'),false,p.get('ref')||'');});
 get('catalog.json').then(c=>{
  catalog=c;$('work-select').replaceChildren(...c.works.map(w=>new Option(`${w.title} · ${w.latin}`,w.id)));$('work-select').disabled=false;
  const params=new URLSearchParams(location.search),work=params.get('work')||c.works[0].id;
  if(!c.works.some(w=>w.id===work))throw Error('未找到这部作品。');
  return navigate(work,params.get('page')||readStore('babel-classics:'+work),false,params.get('ref')||'');
 }).catch(e=>{error(e.message,'symposium','172');$('reader-status').textContent='作品目录未能载入';$('reading-content').setAttribute('aria-busy','false');});
})();
