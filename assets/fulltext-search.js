/* Shared UI for book-scoped search; text never leaves the reader's browser. */
window.BABEL_FULLTEXT = (() => {
  const strings={
    zh:{open:'全文搜索',title:'搜索当前作品',placeholder:'输入原文或关键词',search:'搜索',close:'关闭搜索',hint:'Ctrl+F / ⌘+F 打开；首次搜索需要建立索引。',empty:'请输入搜索内容。',working:'正在检索：{done} / {total}',done:'找到 {count} 条结果。',limited:'仅显示前 {count} 条结果，请使用更长的关键词缩小范围。',partial:'有 {count} 个章节未能读取，结果可能不完整。',none:'未找到结果。',error:'搜索未完成，请重试。',ready:'输入关键词后按 Enter 搜索。'},
    de:{open:'Volltextsuche',title:'Dieses Werk durchsuchen',placeholder:'Originaltext oder Suchbegriff',search:'Suchen',close:'Suche schließen',hint:'Ctrl+F / ⌘+F öffnet die Suche; beim ersten Mal wird ein Index aufgebaut.',empty:'Bitte einen Suchbegriff eingeben.',working:'Suche läuft: {done} / {total}',done:'{count} Treffer gefunden.',limited:'Nur die ersten {count} Treffer werden angezeigt. Bitte die Suche eingrenzen.',partial:'{count} Kapitel konnten nicht gelesen werden; Ergebnisse sind möglicherweise unvollständig.',none:'Keine Treffer gefunden.',error:'Die Suche konnte nicht abgeschlossen werden. Bitte erneut versuchen.',ready:'Suchbegriff eingeben und Enter drücken.'},
    la:{open:'Quaerere',title:'Hoc opus perquirere',placeholder:'Verba quaerenda',search:'Quaere',close:'Quaestionem claude',hint:'Ctrl+F / ⌘+F: index primo usu paratur.',empty:'Verba quaerenda inscribe.',working:'Quaeritur: {done} / {total}',done:'Inventa: {count}.',limited:'Prima tantum {count} monstrantur; plura verba adde.',partial:'Partes non lectae: {count}; inventa fortasse desunt.',none:'Nihil inventum est.',error:'Quaestio non perfecta est; iterum tenta.',ready:'Verba inscribe et Enter preme.'}
  };
  function create({mount,search,onJump}) {
    let run=0,lastFocus=null,statusKey='ready',statusParams={},results=[];
    const language=()=>{const l=window.BABEL_I18N?.language||document.documentElement.lang;return l?.startsWith('de')?'de':l?.startsWith('la')?'la':'zh';};
    const tr=(key,params={})=>strings[language()][key].replace(/\{(\w+)\}/g,(_,k)=>String(params[k]??''));
    const make=(tag,cls,text)=>{const n=document.createElement(tag);if(cls)n.className=cls;if(text)n.textContent=text;return n;};
    const open=make('button','fulltext-open');open.type='button';mount.append(open);
    const panel=make('aside','fulltext-panel');panel.hidden=true;panel.setAttribute('role','region');panel.setAttribute('aria-label',tr('title'));
    const header=make('div','fulltext-header'),title=make('h2'),close=make('button');close.type='button';header.append(title,close);
    const form=make('form','fulltext-form'),input=make('input');input.type='search';input.autocomplete='off';const submit=make('button');submit.type='submit';form.append(input,submit);
    const hint=make('p','fulltext-hint'),status=make('p','fulltext-status'),list=make('ol','fulltext-results');status.setAttribute('role','status');status.setAttribute('aria-live','polite');panel.append(header,form,hint,status,list);document.body.append(panel);
    const setStatus=(key,params={})=>{statusKey=key;statusParams=params;status.textContent=tr(key,params);};
    const localize=()=>{open.textContent=tr('open');title.textContent=tr('title');panel.setAttribute('aria-label',tr('title'));input.placeholder=tr('placeholder');input.setAttribute('aria-label',tr('placeholder'));submit.textContent=tr('search');close.textContent=tr('close');hint.textContent=tr('hint');setStatus(statusKey,statusParams);};
    const show=()=>{if(open.disabled)return;lastFocus=document.activeElement;panel.hidden=false;input.focus();input.select();};
    const hide=()=>{run++;panel.hidden=true;if(lastFocus?.isConnected)lastFocus.focus();};
    const keydown=e=>{if((e.ctrlKey||e.metaKey)&&!e.altKey&&e.key.toLowerCase()==='f'){e.preventDefault();show();}else if(e.key==='Escape'&&!panel.hidden){e.preventDefault();hide();}};
    document.addEventListener('keydown',keydown);open.addEventListener('click',show);close.addEventListener('click',hide);
    form.addEventListener('submit',async e=>{e.preventDefault();const id=++run,q=input.value.trim();list.replaceChildren();results=[];if(!q){setStatus('empty');return;}setStatus('working',{done:0,total:'…'});
      try{const outcome=await search(q,(done,total)=>{if(id===run)setStatus('working',{done,total});},()=>id!==run);if(id!==run)return;results=outcome.results;
        for(const item of results){const li=make('li'),button=make('button');button.type='button';button.append(make('strong','',item.label),make('span','',item.snippet));button.addEventListener('click',async()=>{try{const ok=await onJump(item);if(ok!==false)hide();}catch{setStatus('error');}});li.append(button);list.append(li);}
        if(outcome.failed)setStatus('partial',{count:outcome.failed});else if(outcome.limited)setStatus('limited',{count:results.length});else if(!results.length)setStatus('none');else setStatus('done',{count:results.length});
      }catch{if(id===run)setStatus('error');}
    });
    document.addEventListener('babel:language',localize);localize();
    return {keydown,reset(){run++;list.replaceChildren();results=[];input.value='';setStatus('ready');},setEnabled(value){open.disabled=!value;if(!value){run++;panel.hidden=true;}}};
  }
  return {create};
})();
