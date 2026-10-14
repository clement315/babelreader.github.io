(() => {
  const $=id=>document.getElementById(id);
  const t=window.BABEL_I18N?.t||((key,params={})=>key.replace(/\{(\w+)\}/g,(_,name)=>String(params[name]??'{'+name+'}')));
  const controls=['prev','next','font-down','font-up','chapter-select'];
  let book=null,rendition=null,fontSize=18,storageKey='',theme='light',generation=0,resizeReady=false;
  let currentTitle='阅览室',messageKey='可调字号 · 支持章节导航',messageParams={};
  let placeholderTitle='欢迎来到阅览室',placeholderDescription='从馆藏中选择一本书，或打开本机 EPUB。选择的本机文件只在浏览器中读取，不会上传。',placeholderParams={};
  const get=(key)=>{try{return localStorage.getItem(key);}catch{return null;}};
  const set=(key,value)=>{try{localStorage.setItem(key,value);}catch{/* 阅读功能不依赖浏览器存储。 */}};
  const setStatus=(key,params={})=>{messageKey=key;messageParams=params;$('reader-status').textContent=t(key,Object.fromEntries(Object.entries(params).map(([k,v])=>[k,t(String(v))])));};
  const show=(title,description,params={})=>{placeholderTitle=title;placeholderDescription=description;placeholderParams=params;$('placeholder').hidden=false;$('placeholder-title').textContent=t(title);$('placeholder-description').textContent=t(description,params);};
  const applyTheme=()=>{
    document.body.classList.toggle('dark',theme==='dark');
    $('theme-toggle').textContent=t(theme==='dark'?'浅色阅读':'深色阅读');$('theme-toggle').setAttribute('aria-pressed',String(theme==='dark'));
    if(rendition){rendition.themes.select(theme);rendition.themes.fontSize(fontSize+'px');}
  };
  const flatten=(items,depth=0)=>items.flatMap(item=>[{...item,depth},...flatten(item.subitems||[],depth+1)]);
  const navigate=async(method,target)=>{if(!rendition)return;try{await rendition[method](target);}catch{setStatus('暂时无法跳转，请尝试章节目录。');}};
  const open=async(source,key,title)=>{
    const token=++generation;resizeReady=false;
    controls.forEach(id=>$(id).disabled=true);storageKey='babel-position:'+key;
    if(book){try{book.destroy();}catch{}book=null;rendition=null;}
    $('viewer').replaceChildren();$('chapter-select').replaceChildren(new Option(t('章节目录'),''));
    show('正在打开电子书','第一次打开可能需要一些时间，请稍候。');$('demo-link').hidden=true;
    currentTitle=title;$('reader-title').textContent=t(title);setStatus('正在读取…');
    if(typeof window.ePub!=='function'){show('阅读器未能载入','请检查 vendor 文件夹是否完整上传。你仍可以从作品介绍页下载 EPUB。');setStatus('阅读器组件缺失');return;}
    let current;
    try{
      current=window.ePub(source);book=current;
      current.on('openFailed',()=>{if(token===generation){show('电子书无法打开','请检查文件是否存在、格式是否正确，并确认没有 DRM 保护。');setStatus('打开失败');}});
      await Promise.race([current.ready,new Promise((_,reject)=>setTimeout(()=>reject(new Error('打开超时')),30000))]);
      if(token!==generation)return;
      const metadata=await current.loaded.metadata;
      currentTitle=metadata.title||title;$('reader-title').textContent=t(currentTitle);document.title=t(currentTitle)+' · '+t('阅览室');
      const viewer=$('viewer');
      rendition=current.renderTo(viewer,{width:viewer.clientWidth,height:viewer.clientHeight,spread:'none',flow:'paginated',allowScriptedContent:false});
      const style={body:{'font-family':'Georgia, "Noto Serif SC", "SimSun", serif','line-height':'1.9','padding':'16px 18px !important'},a:{color:'#9b7944'}};
      rendition.themes.register('light',{...style,body:{...style.body,color:'#263e33',background:'#f5f1e8'}});
      rendition.themes.register('dark',{...style,body:{...style.body,color:'#e8e3d5',background:'#1c2922'}});
      applyTheme();
      const nav=await current.loaded.navigation;
      const chapters=flatten(nav.toc||[]);
      chapters.forEach(ch=>$('chapter-select').add(new Option('　'.repeat(ch.depth)+ch.label.trim(),ch.href)));
      rendition.on('relocated',location=>{
        if(token!==generation)return;
        set(storageKey,location.start.cfi);
        $('prev').disabled=location.atStart;$('next').disabled=location.atEnd;
        const href=location.start.href?.split('#')[0];
        const selected=chapters.find(ch=>ch.href.split('#')[0]===href);
        if(selected)$('chapter-select').value=selected.href;
        setStatus('{chapter} · 阅读位置保存在本浏览器',{chapter:selected?selected.label.trim():'阅读中'});
      });
      const keyHandler=e=>{if(['INPUT','SELECT','TEXTAREA','BUTTON'].includes(e.target?.tagName))return;if(e.key==='ArrowLeft'){e.preventDefault();navigate('prev');}if(e.key==='ArrowRight'){e.preventDefault();navigate('next');}};
      rendition.on('keyup',keyHandler);
      // 保留一本书一个本地阅读位置，换设备后不会同步。
      const position=get(storageKey);
      try{await rendition.display(position||undefined);}catch{await rendition.display();}
      if(token!==generation)return;
      resizeReady=true;
      $('placeholder').hidden=true;controls.forEach(id=>$(id).disabled=false);
      const location=rendition.currentLocation();if(location?.atStart)$('prev').disabled=true;if(location?.atEnd)$('next').disabled=true;
    }catch(error){if(token!==generation)return;show('电子书无法打开','请确认 EPUB 文件已上传且可访问。若文件较大，可下载后离线阅读。');setStatus('打开失败：{error}',{error:error.message});}
  };
  $('prev').addEventListener('click',()=>navigate('prev'));$('next').addEventListener('click',()=>navigate('next'));
  $('chapter-select').addEventListener('change',e=>{if(e.target.value)navigate('display',e.target.value);});
  $('font-down').addEventListener('click',()=>{fontSize=Math.max(14,fontSize-2);applyTheme();});
  $('font-up').addEventListener('click',()=>{fontSize=Math.min(32,fontSize+2);applyTheme();});
  $('theme-toggle').addEventListener('click',()=>{theme=theme==='dark'?'light':'dark';applyTheme();});
  $('local-file').addEventListener('change',async e=>{const file=e.target.files[0];if(!file)return;try{if(!/\.epub$/i.test(file.name))throw new Error('请选择 EPUB 文件');$('return-link').href='index.html#catalog';await open(await file.arrayBuffer(),file.name+':'+file.size+':'+file.lastModified,file.name);}catch(error){show('无法读取本机文件',error.message);}finally{e.target.value='';}});
  const renderLocale=()=>{
    $('reader-title').textContent=t(currentTitle);
    document.title=t(currentTitle)+' · '+t('阅览室');
    $('placeholder-title').textContent=t(placeholderTitle);
    $('placeholder-description').textContent=t(placeholderDescription,placeholderParams);
    if($('chapter-select').options.length)$('chapter-select').options[0].textContent=t('章节目录');
    setStatus(messageKey,messageParams);
    applyTheme();
  };
  document.addEventListener('babel:language',renderLocale);
  renderLocale();
  document.addEventListener('keydown',e=>{if(['INPUT','SELECT','TEXTAREA','BUTTON'].includes(e.target?.tagName))return;if(e.key==='ArrowLeft'){e.preventDefault();navigate('prev');}if(e.key==='ArrowRight'){e.preventDefault();navigate('next');}});
  let sizeTimer;
  new ResizeObserver(()=>{clearTimeout(sizeTimer);sizeTimer=setTimeout(()=>{if(resizeReady&&rendition)rendition.resize($('viewer').clientWidth,$('viewer').clientHeight);},120);}).observe($('viewer'));
  const id=new URLSearchParams(location.search).get('id');
  if(id){const entry=(window.BABEL_BOOKS||[]).find(b=>b.id===id)||(window.BABEL_READING_SAMPLE?.id===id?window.BABEL_READING_SAMPLE:null);if(entry?.file){if(entry!==window.BABEL_READING_SAMPLE)$('return-link').href='book.html?id='+encodeURIComponent(id);open(entry.file,id,entry.title);}else{show('这本书暂时无法阅读','没有找到书目，或该书尚未附加 EPUB 文件。请返回馆藏选择其他作品。');}}
})();
