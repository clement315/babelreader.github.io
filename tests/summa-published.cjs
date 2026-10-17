const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const { pathToFileURL } = require('node:url');
const { chromium } = require('playwright');
const repository=path.resolve(__dirname,'..');
const catalog=JSON.parse(fs.readFileSync(path.join(repository,'data/summa/catalog.json'),'utf8'));
const corpus=catalog.parts.flatMap(p=>p.questions.map(q=>JSON.parse(fs.readFileSync(path.join(repository,`data/summa/${p.id}/q${q.number}.json`),'utf8'))));
const base = process.env.SUMMA_BASE || 'http://127.0.0.1:8767';
const output = process.env.SUMMA_QA_OUTPUT || path.resolve(__dirname,'../../reader_qa');
const report = { checks: [], errors: [] };
const ok = (name, detail) => report.checks.push({ name, passed: true, ...(detail ? {detail} : {}) });
(async () => {
 fs.mkdirSync(output,{recursive:true});
 const browser = await chromium.launch({ ...(process.platform === 'win32' ? {channel:'msedge'} : {}), headless:true });
 try {
  const context=await browser.newContext({viewport:{width:1440,height:1000},reducedMotion:'reduce'});
  const page=await context.newPage(); const requests=[];
  page.on('pageerror',e=>report.errors.push(String(e)));
  page.on('request',r=>{if(r.url().includes('/data/summa/'))requests.push(r.url());});
  const ready=async(p,badge)=>{await p.waitForSelector('.article');await p.waitForFunction(()=>document.getElementById('question-content').getAttribute('aria-busy')==='false');if(badge)await p.waitForFunction(b=>document.getElementById('location-badge').textContent===b,badge);};
  await page.goto(base+'/summa.html?part=I&q=1&art=1');await ready(page,'ST.I.Q1.A1');
  assert.equal(await page.locator('.article').count(),10);
  assert.equal(await page.locator('.sidebar').getAttribute('inert'),null);
  const basePath = new URL(base).pathname.replace(/\/$/,'');
  assert.deepEqual(requests.map(u=>new URL(u).pathname),[basePath+'/data/summa/catalog.json',basePath+'/data/summa/I/q1.json']);
  assert(requests.every(u=>new URL(u).searchParams.get('v')===catalog.release));
  assert.equal(await page.locator('.question-node').count(),613);assert.equal(await page.locator('a.article-link[href]').count(),3125);
  ok('Loads catalog and current question only',requests.length);
  const chineseText = (await page.locator('#question-content [lang="zh-Hant"]').allTextContents()).join('\n');
  assert(chineseText.includes('「地球是圓的」'));
  assert(chineseText.includes('《教會階級論》'));
  assert(!chineseText.includes('《基本教理手冊))'));
  ok('Corrected Chinese quotation and title marks render from question JSON');
  const geometry=await page.evaluate(()=>[...document.querySelectorAll('.bilingual-row:not(.column-heads)')].map(row=>{const cells=[...row.children].filter(n=>n.classList.contains('cell'));return cells.length===2?{kind:row.dataset.kind,topDelta:Math.abs(cells[0].getBoundingClientRect().top-cells[1].getBoundingClientRect().top),columns:getComputedStyle(row).gridTemplateColumns,gap:getComputedStyle(row).columnGap}:null;}).filter(Boolean));
  assert(geometry.every(r=>r.topDelta<.6&&r.gap==='40px'));
  const stress=await page.evaluate(()=>{const row=document.querySelector('[data-kind="objection"]');const chinese=row.querySelector('[lang="zh-Hant"]');chinese.style.minHeight='650px';const next=row.nextElementSibling;const good=next.getBoundingClientRect().top>=Math.max(...[...row.children].map(c=>c.getBoundingClientRect().bottom));chinese.style.minHeight='';return good;});
  assert(stress);ok('Bilingual Grid rows align; long-cell stress does not overlap',geometry.length);
  assert.equal(await page.locator('.back-link').getAttribute('href'),'./index.html?lang=la');
  await page.selectOption('#reading-mode','latin');assert(new URL(page.url()).searchParams.get('mode')==='latin');
  assert.equal(await page.locator('#question-content .cell[lang="zh-Hant"]:visible').count(),0);
  await page.selectOption('#reading-mode','chinese');assert.equal(await page.locator('#question-content .cell[lang="la"]:visible').count(),0);
  await page.selectOption('#reading-mode','parallel');ok('Three reading modes and URL persistence');
  await page.click('#next-article');await ready(page,'ST.I.Q1.A2');
  await page.goBack();await ready(page,'ST.I.Q1.A1');ok('Article navigation, cache and browser history');
  await page.evaluate(()=>window.SummaReader.navigate({part:'I',q:1,art:10}));await ready(page,'ST.I.Q1.A10');
  await page.click('#next-article');await ready(page,'ST.I.Q2.A1');
  assert.equal(await page.locator('#article-1 .subtitle .cell[lang="la"] h3').textContent(),'Utrum Deum esse sit per se notum');
  assert.equal(await page.locator('.question-heading .cell[lang="la"] h1').textContent(),'De Deo, an Deus sit');
  ok('Aquinas.cc Latin question and article titles render in the left column');
  await page.screenshot({path:path.join(output,'summa-q2-titles.png')});
  await page.click('#prev-article');await ready(page,'ST.I.Q1.A10');ok('Previous/next crosses question boundary');
  const last=await page.evaluate(async()=>{const c=await fetch('./data/summa/catalog.json').then(r=>r.json());return c.parts[0].questions.at(-1).articles.at(-1).number;});
  await page.evaluate(n=>window.SummaReader.navigate({part:'I',q:119,art:n}),last);await ready(page,`ST.I.Q119.A${last}`);
  await page.click('#next-article');await ready(page,'ST.I_II.Q1.A1');ok('Next crosses part boundary');
  for(const [part,q,art] of [['II_II',48,1],['III',90,1],['SUPPL',99,5]]){
   await page.evaluate(v=>window.SummaReader.navigate(v),{part,q,art});await ready(page,`ST.${part}.Q${q}.A${art}`);
  }
  assert(!(await page.locator('#next-article').isDisabled()));await page.click('#next-article');await ready(page,'ST.SUPPL.App1.A1');
  await page.evaluate(()=>SummaReader.navigate({part:'APPENDICES',q:2,art:2}));await ready(page,'ST.SUPPL.App2.A2');assert(await page.locator('#next-article').isDisabled());ok('All five parts and both appendices navigate with correct boundaries');
  for(const q of [71,72]){
   await page.evaluate(q=>SummaReader.navigate({part:'I',q,art:1}),q);await ready(page,`ST.I.Q${q}.A1`);
   assert.equal(await page.locator('.unsegmented-link').count(),0);
   assert((await page.locator(`[data-row-id="I.q0${q}.a001.respondeo"] [lang="zh-Hant"]`).textContent()).includes('我解答如下'));
  }ok('PDF-corrected I Q71 and Q72 Chinese rows are aligned');
  await page.evaluate(()=>SummaReader.navigate({part:'II_II',q:170,art:2}));await ready(page,'ST.II_II.Q170.A2');
  assert((await page.locator('#question-content>p.notice').textContent()).includes('474'));
  assert((await page.locator('[data-row-id="II_II.q170.a002.ad3"] [lang="zh-Hant"]').textContent()).includes('相反端莊'));
  ok('Source PDF page gap is marked and surviving Article 2 text is in the correct article');
  await page.evaluate(()=>window.SummaReader.navigate({part:'SUPPL',q:64,art:10}));await ready(page,'ST.SUPPL.Q64.A10');
  assert((await page.locator('#article-10 .article-notice').textContent()).includes('中文'));ok('Missing Chinese article is explicit, not fabricated');
  await page.evaluate(()=>window.SummaReader.navigate({part:'I',q:1,art:1}));await ready(page,'ST.I.Q1.A1');
  await page.click('#theme-toggle');assert(await page.locator('body').evaluate(n=>n.classList.contains('dark')));
  await page.reload();await ready(page,'ST.I.Q1.A1');assert(await page.locator('body').evaluate(n=>n.classList.contains('dark')));
  await page.click('#theme-toggle');ok('Dark theme persists and restores');
  const wordHook=await page.evaluate(()=>{let value='';window.SUMMA_LOOKUP=d=>value=d.word;const p=document.querySelector('#article-1 .cell[lang="la"] p');const text=[...p.childNodes].find(n=>n.nodeType===Node.TEXT_NODE);const word=text.textContent.match(/[A-Za-z]+/)[0];const start=text.textContent.indexOf(word);const range=document.createRange();range.setStart(text,start);range.setEnd(text,start+word.length);const s=getSelection();s.removeAllRanges();s.addRange(range);p.dispatchEvent(new MouseEvent('dblclick',{bubbles:true}));s.removeAllRanges();return value===word;});
  assert(wordHook);ok('Latin word lookup integration hook');
  await page.evaluate(()=>{window.scrollTo(0,0);});await page.screenshot({path:path.join(output,'summa-desktop.png')});
  // Rapid navigation aborts stale fetches; q3 must be the final rendered state.
  await page.route('**/data/summa/I/q4.json*',async route=>{await new Promise(r=>setTimeout(r,350));await route.continue().catch(()=>{});});
  const fourth=page.waitForRequest('**/data/summa/I/q4.json*');
  await page.evaluate(()=>{window.SummaReader.navigate({part:'I',q:4,art:1});});await fourth;
  await page.evaluate(()=>{window.SummaReader.navigate({part:'I',q:5,art:1});});
  await ready(page,'ST.I.Q5.A1');await page.waitForTimeout(400);assert((await page.locator('#question-content').textContent()).includes('Quaestio 5'));ok('Stale requests cannot overwrite later navigation');
  await page.unroute('**/data/summa/I/q4.json*');
  const missing=await context.newPage();missing.on('pageerror',e=>report.errors.push(String(e)));
  await missing.route('**/data/summa/I/q2.json*',r=>r.fulfill({status:404,body:'Not found'}));
  await missing.goto(base+'/summa.html?part=I&q=2&art=1');await missing.waitForSelector('.error-panel');
  assert.equal(await missing.locator('.article').count(),0);ok('Missing question has a recoverable error, not stale text');await missing.close();
  await page.goto(base+'/summa.html?part=INVALID&q=1&art=1');await page.waitForSelector('.error-panel');ok('Invalid routes rejected');
  const fallback=await context.newPage();fallback.on('pageerror',e=>report.errors.push(String(e)));
  await fallback.route('**/data/summa/catalog.json*',r=>r.fulfill({status:404,body:'Not found'}));
  await fallback.goto(base+'/summa.html?part=III&q=2&art=1');await ready(fallback,'ST.I.Q1.A1');
  assert((await fallback.locator('#reader-notice').textContent()).includes('內置'));assert.equal(new URL(fallback.url()).searchParams.get('part'),'I');
  ok('Catalog failure falls back honestly to embedded Q1');await fallback.close();
  const file=await context.newPage();file.on('pageerror',e=>report.errors.push(String(e)));
  await file.goto(pathToFileURL(path.resolve(__dirname,'../summa.html')).href+'?part=I&q=1&art=3');await ready(file,'ST.I.Q1.A3');
  assert.equal(await file.locator('.article').count(),10);assert((await file.locator('#catalog-count').textContent()).includes('示例'));assert((await file.locator('#article-1 .subtitle .cell[lang="la"] h3').textContent()).startsWith('Utrum'));ok('Direct file:// opening uses genuine Q1 without CORS fetch');await file.close();
  const mobile=await browser.newContext({viewport:{width:390,height:844},isMobile:true,hasTouch:true,reducedMotion:'reduce'});
  const phone=await mobile.newPage();phone.on('pageerror',e=>report.errors.push(String(e)));
  await phone.goto(base+'/summa.html?part=I&q=1&art=1');await ready(phone,'ST.I.Q1.A1');
  assert(await phone.locator('body').evaluate(n=>n.classList.contains('sidebar-hidden')));
  const small=await phone.evaluate(()=>{const row=document.querySelector('[data-kind="objection"]');const cells=row.querySelectorAll('.cell');return {overflow:document.documentElement.scrollWidth>innerWidth,ordered:cells[1].getBoundingClientRect().top>=cells[0].getBoundingClientRect().bottom,grid:getComputedStyle(row).gridTemplateColumns};});
  assert(!small.overflow&&small.ordered);ok('390px mobile has alternating cells and no horizontal overflow',small);
  await phone.click('#toggle-sidebar');assert.equal(await phone.locator('#toggle-sidebar').getAttribute('aria-expanded'),'true');
  await phone.locator('[data-part="I"] .question-node').nth(1).locator('summary').click();await ready(phone,'ST.I.Q2.A1');
  assert(await phone.locator('body').evaluate(n=>n.classList.contains('sidebar-hidden')));ok('Mobile tree navigation closes overlay and updates active question');
  await phone.evaluate(()=>window.SummaReader.navigate({part:'I',q:1,art:1}));await ready(phone,'ST.I.Q1.A1');
  await phone.evaluate(()=>window.scrollTo(0,0));await phone.screenshot({path:path.join(output,'summa-mobile.png')});
  await phone.setViewportSize({width:320,height:740});
  assert(await phone.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));ok('320px small-screen layout has no overflow');
  await mobile.close();
  await page.goto(base+'/index.html?lang=la');await page.waitForSelector('.book-card');
  const card=page.locator('.book-card').filter({has:page.locator('h3',{hasText:'神学大全'})});assert.equal(await card.count(),1);
  assert(new URL(await card.locator('.book-link').getAttribute('href'),base).pathname.endsWith('/summa.html'));await card.locator('.book-link').click();await ready(page,'ST.I.Q1.A1');ok('Unified bookshelf opens JSON reader');
  await page.goto(base+'/book.html?id=summa-theologiae');await page.waitForSelector('#book-detail .hero-actions a');
  assert(new URL(await page.locator('#book-detail .hero-actions a').getAttribute('href'),base).pathname.endsWith('/summa.html'));assert.equal(await page.locator('a[download]').count(),0);ok('Book detail routes to JSON reader without fake EPUB download');
  await page.goto(base+'/summa.html?part=I&q=1&art=1');await ready(page,'ST.I.Q1.A1');
  let rowTotal=0;let articleTotal=0;
  for(const q of corpus){
   const counted=await page.evaluate(async q=>{
    await SummaReader.navigate({part:q.part,q:q.question,art:1});
    if(SummaReader.location.part!==q.part||SummaReader.location.q!==q.question)throw Error(q.id+' route');
    if(document.querySelectorAll('.article').length!==q.articles.length)throw Error(q.id+' article count');
    const norm=s=>(s||'').replace(/\s+/g,'');let rows=0;
    for(const a of q.articles){
     const node=document.getElementById('article-'+a.number);
     for(const row of a.rows){
      const dom=node.querySelector(`[data-row-id="${row.id}"]`);if(!dom)throw Error(row.id+' missing');
      for(const lang of ['la','zh']){
       const cell=dom.querySelector('[lang="'+(lang==='la'?'la':'zh-Hant')+'"]');
       const selector=row.kind==='article-heading'?'h2':row.kind==='subtitle'?'h3':'p';
       const text=[...cell.querySelectorAll(selector)].map(p=>p.textContent).join('');
       if(norm(text)!==norm(row[lang]||'—')&&!(row[lang]===''&&selector==='p'&&text===''))throw Error(row.id+' '+lang);
      }rows++;
     }
    }
    if(q.prologue.zh||q.prologue.la){for(const lang of ['la','zh']){
     const cell=document.querySelector('#question-prologue [lang="'+(lang==='la'?'la':'zh-Hant')+'"]');
     if(norm([...cell.querySelectorAll('p')].map(p=>p.textContent).join(''))!==norm(q.prologue[lang]))throw Error(q.id+' prologue '+lang);
    }}return rows;
   },q);rowTotal+=counted;articleTotal+=q.articles.length;
   if((corpus.indexOf(q)+1)%100===0)console.log('Rendered and compared '+(corpus.indexOf(q)+1)+'/613 questions');
  }
  assert.equal(rowTotal,39507);assert.equal(articleTotal,3125);
  ok('Every bilingual row in all 613 reading units equals the corrected data',{questions:corpus.length,articles:articleTotal,rows:rowTotal});
  assert.deepEqual(report.errors,[]);await context.close();
 } finally {await browser.close();}
 fs.writeFileSync(path.join(output,'browser-validation.json'),JSON.stringify(report,null,2));
 console.log(JSON.stringify(report,null,2));
})().catch(error=>{report.failure=String(error.stack||error);fs.writeFileSync(path.join(output,'browser-validation.json'),JSON.stringify(report,null,2));console.error(error);process.exit(1);});
