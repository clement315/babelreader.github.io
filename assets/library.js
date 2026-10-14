(() => {
  const grid=document.getElementById('book-grid');
  const search=document.getElementById('search');
  const status=document.getElementById('result-status');
  let category='全部';
  const node=(tag,cls,text)=>{const n=document.createElement(tag);n.className=cls;if(text!==undefined)n.textContent=text;return n;};
  const books=window.BABEL_BOOKS||[];
  const render=()=>{
    const q=search.value.trim().toLocaleLowerCase();
    const matches=books.filter(b=>(category==='全部'||b.category===category)&&[b.title,b.originalTitle,b.author,b.description].join(' ').toLocaleLowerCase().includes(q));
    grid.replaceChildren();
    matches.forEach((b,i)=>{
      const card=node('article','book-card');
      const cover=node('a','book-cover '+b.color);cover.href='book.html?id='+encodeURIComponent(b.id);cover.setAttribute('aria-label','查看《'+b.title+'》介绍');
      cover.append(node('span','cover-series','BIBLIOTHECA · '+String(books.indexOf(b)+1).padStart(2,'0')),node('span','cover-symbol',b.mark),node('span','cover-title',b.title),node('span','cover-original',b.originalTitle),node('span','cover-author',b.author));
      const meta=node('div','book-meta');meta.append(node('span','category',b.category),node('span',b.file?'availability ready':'availability',b.file?'可在线阅读':(b.demo?'示范书目':'仅书目')));
      const h=node('h3','');const a=node('a','',b.title);a.href=cover.href;h.append(a);
      card.append(cover,meta,h,node('p','book-author',b.author+' / '+b.language),node('p','book-description',b.description));
      const link=node('a','book-link',b.file?'打开书籍 →':'查看书目 →');link.href=cover.href;card.append(link);grid.append(card);
    });
    status.textContent=matches.length?'显示 '+matches.length+' 部作品':'没有找到对应作品，请尝试其他关键词或分类。';
  };
  search.addEventListener('input',render);
  document.querySelectorAll('[data-category]').forEach(btn=>btn.addEventListener('click',()=>{category=btn.dataset.category;document.querySelectorAll('[data-category]').forEach(b=>b.setAttribute('aria-pressed',String(b===btn)));render();}));
  render();
})();
