(function(root){
 'use strict';
 const fields=[['zh','中文译文','zh-CN'],['de','施莱尔马赫译文','de'],['structure','结构分析','zh-CN']];
 const clone=value=>JSON.parse(JSON.stringify(value));
 const empty=work=>({format:'babel-classics-notes',version:1,work,units:{}});
 const base=u=>({zh:u.reading?.zh||u.notes?.['中']||'',de:u.reading?.de||'',structure:u.reading?.structure||u.notes?.['结构']||''});
 const matches=(u,d)=>d&&u.ref===d.ref&&u.greek===d.greek;
 function validate(value,work){
  if(!value||value.format!=='babel-classics-notes'||value.version!==1||value.work!==work||!value.units||Array.isArray(value.units)||typeof value.units!=='object')throw Error('这不是当前作品的笔记备份。请先选择对应作品。');
  const result=empty(work),entries=Object.entries(value.units);
  if(entries.length>10000)throw Error('备份中的笔记数量过多。');
  for(const [id,d] of entries){
   if(!/^[1-9]\d*$/.test(id)||!d||typeof d.greek!=='string'||d.greek.length>30000||!/^\d+[a-e]$/.test(d.ref||'')||!d.reading)throw Error('备份中的句子信息不完整。');
   const reading={};
   for(const [key] of fields){if(typeof d.reading[key]!=='string'||d.reading[key].length>100000)throw Error('备份中的笔记格式有误。');reading[key]=d.reading[key];}
   result.units[id]={ref:d.ref,greek:d.greek,reading};
  }
  return result;
 }
 function patchPage(page,backup){
  if(page.work!==backup.work)throw Error('作品不一致。');
  const result=clone(page);
  for(const u of result.units){
   const d=backup.units[u.id];if(!d)continue;
   if(!matches(u,d))throw Error('第 '+u.id+' 句的原文或编号已变动，请核对备份。');
   u.reading={...u.reading,...d.reading,ownerEdited:true};u.notes={'中':d.reading.zh,'结构':d.reading.structure};
   if(u.reading.alignment)delete u.reading.alignment;
  }
  return result;
 }
 function create(options){
  const {get,onRender,onStatus}=options,$=id=>document.getElementById(id);
  let meta,page,backup,editing=false,busy=false;
  const pending=new Map(),key=work=>'babel-classics-notes-v1:'+work;
  const message=text=>{$('edit-status').textContent=text;};
  const load=work=>{const raw=localStorage.getItem(key(work));return raw?validate(JSON.parse(raw),work):empty(work);};
  const write=value=>{localStorage.setItem(key(value.work),JSON.stringify(value));};
  const count=()=>Object.keys(backup?.units||{}).length;
  const controls=()=>{
   $('edit-toggle').setAttribute('aria-pressed',String(editing));$('edit-toggle').textContent=editing?'结束编辑':'编辑笔记';
   $('edit-save').hidden=!editing;$('edit-help').hidden=!editing;
   for(const id of ['edit-toggle','edit-save','edit-export','edit-import'])$(id).disabled=busy||!page;
   $('edit-count').textContent=count()?count()+' 条本机笔记':'';
  };
  const reading=u=>pending.get(u.id)||(matches(u,backup?.units[u.id])?backup.units[u.id].reading:base(u));
  function save(){
   if(!page)return false;
   if(!pending.size){message('本页没有尚未保存的修改。');return true;}
   try{
    const next=load(meta.id);
    for(const u of page.units){
     const value=pending.get(u.id);if(!value)continue;
     if(fields.every(([k])=>value[k]===base(u)[k]))delete next.units[u.id];
     else next.units[u.id]={ref:u.ref,greek:u.greek,reading:{...value}};
    }
    write(next);backup=next;pending.clear();controls();onRender();message('已保存到本机。导出后上传 GitHub，即可更新网站。');return true;
   }catch(e){message('未能保存：浏览器存储不可用或空间不足。请勿关闭当前页。');return false;}
  }
  function renderFields(u,host,el){
   const value=reading(u);
   for(const [field,label,lang] of fields){
    const section=el('section','note-field');
    if(editing){
     const id='edit-'+field+'-'+u.id,labelNode=el('label','note-label',label);labelNode.htmlFor=id;
     const area=el('textarea','note-input');area.id=id;area.lang=lang;area.rows=field==='structure'?4:3;area.value=value[field];area.spellcheck=false;
     area.addEventListener('input',()=>{const next={...reading(u),[field]:area.value};pending.set(u.id,next);message('有尚未保存的修改。');});
     section.append(labelNode,area);
    }else{const p=el('p','',value[field]||(field==='de'?u.reading.deNote||'':''));p.lang=field==='de'&&!value[field]?'zh-CN':lang;section.append(el('h3','note-label',label),p);}
    host.append(section);
   }
  }
  function download(blob,name){
   const url=URL.createObjectURL(blob),a=document.createElement('a');a.href=url;a.download=name;document.body.append(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(url),30000);
  }
  async function pagesFor(value,m){
   const wanted=[...new Set(Object.values(value.units).map(d=>d.ref.match(/^\d+/)[0]))];
   if(wanted.some(p=>!m.pages.includes(p)))throw Error('备份含有本作品未收录的页码。');
   const result=[];
   for(let start=0;start<wanted.length;start+=6)result.push(...await Promise.all(wanted.slice(start,start+6).map(p=>get(m.id+'/'+p+'.json'))));
   for(const [id,d] of Object.entries(value.units))if(!result.some(p=>p.units.some(u=>String(u.id)===id&&matches(u,d))))throw Error('备份中的第 '+id+' 句与网站原文不符。');
   return result;
  }
  async function exportNotes(){
   if(pending.size&&!save())return;
   const value=clone(backup),m=meta;if(!count()){message('本作品还没有本机修改。');return;}
   busy=true;controls();message('正在准备导出文件…');
   try{
    if(!root.JSZip)throw Error('导出工具未能载入，请刷新后重试。');
    const zip=new root.JSZip(),pages=await pagesFor(value,m);
    for(const p of pages)zip.file('data/classics/'+m.id+'/'+p.page+'.json',JSON.stringify(patchPage(p,value)));
    zip.file('笔记备份.json',JSON.stringify(value,null,2));
    zip.file('上传说明.txt','《'+m.title+'》笔记修改\n\n1. 解压此文件。\n2. 打开 GitHub 上的网站仓库首页，选择 Add file → Upload files。\n3. 将解压得到的 data 文件夹拖入上传区；页面应显示 data/classics/'+m.id+'/页码.json。\n4. 核对路径后提交 Commit changes，等待网站部署完成。\n\n笔记备份.json 用于网页“导入备份”，不需要上传到网站。\n本压缩包仅包含有修改的页面，其他仓库文件无需删除。\n');
    download(await zip.generateAsync({type:'blob',compression:'DEFLATE'}),m.id+'-notes-'+new Date().toISOString().slice(0,10)+'.zip');
    message('已导出修改文件与笔记备份。解压后按“上传说明”操作即可。');
   }catch(e){message('导出未完成：'+e.message);}finally{busy=false;controls();}
  }
  async function importNotes(file){
   if(!file)return;if(pending.size&&!save())return;
   if(file.size>25000000){message('备份文件过大。');return;}
   const m=meta;busy=true;controls();
   try{
    let text;
    if(file.name.toLowerCase().endsWith('.zip')){
     if(!root.JSZip)throw Error('导入工具未能载入。');
     const zip=await root.JSZip.loadAsync(file),entry=zip.file('笔记备份.json');
     if(!entry)throw Error('压缩包内没有笔记备份.json。');text=await entry.async('string');
    }else text=await file.text();
    if(text.length>5000000)throw Error('备份内容过大。');
    const imported=validate(JSON.parse(text),m.id);await pagesFor(imported,m);
    const next=load(m.id);Object.assign(next.units,imported.units);write(next);
    if(meta.id===m.id){backup=next;onRender();}message('已导入 '+Object.keys(imported.units).length+' 条笔记，并保存到本机。');
   }catch(e){message('导入未完成：'+e.message);}finally{busy=false;controls();$('edit-file').value='';}
  }
  $('edit-toggle').addEventListener('click',()=>{if(pending.size&&!save())return;editing=!editing;controls();onRender();message(editing?'可直接修改三个笔记栏，完成后点击“保存本页”。':'已回到阅读模式。');});
  $('edit-save').addEventListener('click',save);$('edit-export').addEventListener('click',exportNotes);$('edit-import').addEventListener('click',()=>$('edit-file').click());
  $('edit-file').addEventListener('change',e=>importNotes(e.target.files[0]));
  document.addEventListener('keydown',e=>{if(editing&&(e.ctrlKey||e.metaKey)&&e.key.toLowerCase()==='s'){e.preventDefault();save();}});
  root.addEventListener('beforeunload',e=>{if(pending.size){e.preventDefault();e.returnValue='';}});
  return {
   get editing(){return editing;},renderFields,
   beforeNavigate(){if(!pending.size)return true;if(!root.confirm('本页有尚未保存的修改。确定放弃这些修改并离开吗？'))return false;pending.clear();return true;},
   setPage(m,p){meta=m;page=p;pending.clear();try{backup=load(m.id);message('');}catch{backup=empty(m.id);message('无法读取本机笔记。你仍可阅读和导入备份。');}controls();}
  };
 }
 const api={fields,base,empty,validate,patchPage,create};
 if(typeof module!=='undefined'&&module.exports)module.exports=api;else root.BABEL_CLASSICS_EDITOR=api;
})(typeof window==='undefined'?globalThis:window);
