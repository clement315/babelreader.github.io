(() => {
  const book=(window.BABEL_BOOKS||[]).find(b=>b.id===new URLSearchParams(location.search).get('id'));
  const main=document.getElementById('book-detail');
  const t=window.BABEL_I18N?.t||((key,params={})=>key.replace(/\{(\w+)\}/g,(_,name)=>String(params[name]??'{'+name+'}')));
  const el=(tag,cls,text)=>{const n=document.createElement(tag);n.className=cls;if(text!==undefined)n.textContent=text;return n;};
  const render=()=>{
  main.replaceChildren();
  if(!book){const a=el('a','button',t('返回馆藏'));a.href='index.html#catalog';main.append(el('h1','',t('没有找到这部作品')),a);return;}
  document.title=book.title+' · '+t('巴别塔图书馆');
  const cover=el('div','book-cover detail-cover '+book.color);cover.append(el('span','cover-series','BIBLIOTHECA TURRIS BABEL'),el('span','cover-symbol',book.mark),el('span','cover-title',book.coverTitle||book.title),el('span','cover-original',book.originalTitle),el('span','cover-author',book.author));
  const copy=el('section','detail-copy');copy.append(el('p','eyebrow',t(book.category)),el('h1','',book.title),el('p','original-title',book.originalTitle),el('p','detail-description',book.description));
  const dl=el('dl','book-facts');
  const authors=book.type==='notes'?[['作品类型','学习笔记'],['整理者',book.author],...(book.sourceAuthor?[['教材作者',book.sourceAuthor]]:[])]:[['原作者',book.author],['译者',book.translator]];
  [...authors,['语言',book.language],['所据版本',book.edition],['修订日期',book.updated||'尚未填写']].forEach(([k,v])=>{dl.append(el('dt','',t(k)),el('dd','',t(v)));});copy.append(dl);
  if(book.demo)copy.append(el('p','demo-notice',t('模板示范内容，请替换为你的实际作品和版本信息。')));
  if(book.reader==='summa'){const actions=el('div','hero-actions');const read=el('a','button',t('在线阅读 ↗'));read.href=book.readUrl;actions.append(read);copy.append(actions);}
  else if(book.file){const actions=el('div','hero-actions');const read=el('a','button',t('在线阅读 ↗'));read.href='reader.html?id='+encodeURIComponent(book.id);const download=el('a','text-link',t('下载 EPUB ↓'));download.href=book.file;download.setAttribute('download','');actions.append(read,download);copy.append(actions);}else{copy.append(el('p','missing-file',t('此书目尚未附加 EPUB 文件。添加文件后即可启用阅读与下载。')));}
  main.append(cover,copy);
  main.querySelectorAll('.cover-title,.cover-author,h1,.detail-description').forEach(n=>n.lang='zh-CN');
  };
  document.addEventListener('babel:language',render);
  render();
})();
