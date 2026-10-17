(() => {
  const grid=document.getElementById('book-grid');
  const search=document.getElementById('search');
  const status=document.getElementById('result-status');
  const t=window.BABEL_I18N?.t||((key,params={})=>key.replace(/\{(\w+)\}/g,(_,name)=>String(params[name]??'{'+name+'}')));
  let category='全部';
  const node=(tag,cls,text)=>{const n=document.createElement(tag);n.className=cls;if(text!==undefined)n.textContent=text;return n;};
  const books=window.BABEL_BOOKS||[];
  const render=()=>{
    const q=search.value.trim().toLocaleLowerCase();
    const matches=books.filter(b=>(category==='全部'||b.category===category)&&[b.title,b.originalTitle,b.author,b.description,t(b.category)].join(' ').toLocaleLowerCase().includes(q));
    grid.replaceChildren();
    matches.forEach((b,i)=>{
      const readable=Boolean(b.file||b.readUrl);
      const card=node('article','book-card');
      const cover=node('a','book-cover '+b.color);cover.href=b.readUrl||'book.html?id='+encodeURIComponent(b.id);cover.setAttribute('aria-label',t('查看《{title}》介绍',{title:b.title}));
      cover.append(node('span','cover-series','BIBLIOTHECA · '+String(books.indexOf(b)+1).padStart(2,'0')),node('span','cover-symbol',b.mark),node('span','cover-title',b.coverTitle||b.title),node('span','cover-original',b.originalTitle),node('span','cover-author',b.author));
      const meta=node('div','book-meta');meta.append(node('span','category',t(b.category)),node('span',readable?'availability ready':'availability',t(readable?'可在线阅读':(b.demo?'示范书目':'仅书目'))));
      const h=node('h3','');const a=node('a','',b.title);a.href=cover.href;h.append(a);
      card.append(cover,meta,h,node('p','book-author',b.author+' / '+t(b.language)),node('p','book-description',b.description));
      const link=node('a','book-link',t(readable?'打开书籍 →':'查看书目 →'));link.href=cover.href;card.append(link);grid.append(card);
      card.querySelectorAll('.cover-title,.cover-author,h3,.book-description').forEach(n=>n.lang='zh-CN');
    });
    status.textContent=matches.length?(matches.length===1?t('显示 1 部作品'):t('显示 {count} 部作品',{count:matches.length})):t(q?'没有找到对应作品，请尝试其他关键词或分类。':'本栏目尚未上传作品。');
  };
  search.addEventListener('input',render);
  document.addEventListener('babel:language',render);
  document.querySelectorAll('[data-category]').forEach(btn=>btn.addEventListener('click',()=>{category=btn.dataset.category;document.querySelectorAll('[data-category]').forEach(b=>b.setAttribute('aria-pressed',String(b===btn)));render();}));
  render();
})();
