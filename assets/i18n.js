/* 界面译文集中于此；书目和 EPUB 正文保留原来的文字。 */
(() => {
  const rows = [
    ['语言','Sprache','Lingua'],
    ['巴别塔图书馆：教父作品、荷马学、古代注疏、古典修辞学与其他古典作品的翻译、收藏与阅读。','Babel-Bibliothek: Übersetzungen, Sammlung und Lektüre von Kirchenvätern, Homer, antiken Kommentaren, Rhetorik und weiteren antiken Werken.','Bibliotheca Turris Babel: translationes et lectio operum Patrum, Homeri, commentariorum antiquorum, rhetoricae aliorumque operum antiquorum.'],
    ['巴别塔图书馆','Babel-Bibliothek','Bibliotheca Turris Babel'],
    ['跳到馆藏目录','Zum Katalog springen','Ad catalogum transire'],
    ['主导航','Hauptnavigation','Navigatio principalis'],
    ['馆藏目录','Katalog','Catalogus'],
    ['关于本馆','Über die Bibliothek','De bibliotheca'],
    ['进入阅览室','Zum Lesesaal','Ad conclave legendi'],
    ['CLASSICS · TRANSLATION · READING','ANTIKE · ÜBERSETZUNG · LEKTÜRE','LITTERAE ANTIQUAE · TRANSLATIO · LECTIO'],
    ['在语言的分岔处，','Wo die Sprachen sich verzweigen,','Ubi linguae in diversas vias abeunt,'],
    ['与古典相遇','der Antike begegnen','litteris antiquis occurrimus'],
    ['。','.','.'],
    ['一座以翻译为桥的私人图书馆。','Eine private Bibliothek, in der Übersetzung Brücken baut.','Bibliotheca privata, cuius pons est translatio.'],
    ['收藏古典文本，梳理阅读线索，让久远的声音','Antike Texte sammeln, Wege durch die Lektüre erschließen und ferne Stimmen','Textus antiquos colligimus, vias legendi aperimus, vocesque veteres'],
    ['在今天的语言中再次被听见。','in den Sprachen unserer Zeit wieder hörbar machen.','linguis hodiernis iterum audiri sinimus.'],
    ['浏览馆藏','Sammlung erkunden','Libros explorare'],
    ['读一读建馆的缘起','Wie die Bibliothek entstand','De origine bibliothecae legere'],
    ['古典学与宗教文献 · 在线阅读与 EPUB 收藏','Klassische Philologie und religiöse Texte · Online lesen und EPUBs sammeln','Litterae antiquae et religiosae · Lectio in rete et libri EPUB'],
    ['藏书之所','Ein Ort für Bücher','Locus librorum'],
    ['以层叠拱廊和阶梯表现的巴别塔线描','Linienzeichnung des Turms von Babel mit Arkaden und Treppen','Turris Babel arcubus et gradibus lineis delineata'],
    ['从一座塔，到一座书馆','Vom Turm zur Bibliothek','A turri ad bibliothecam'],
    ['教父作品','Kirchenväter','Opera Patrum'],
    ['荷马学','Homerstudien','Studia Homerica'],
    ['古代注疏','Antike Kommentare','Commentarii antiqui'],
    ['古典修辞学','Antike Rhetorik','Rhetorica antiqua'],
    ['古典作品','Antike Werke','Opera antiqua'],
    ['古典作品精读','Antike Texte genau lesen','Lectio accurata operum antiquorum'],
    ['神学著作','Theologische Werke','Opera theologica'],
    ['THE COLLECTION','DIE SAMMLUNG','LIBRI COLLECTI'],
    ['沿着一部作品，开启一段阅读。','Mit einem Werk beginnt eine neue Lektüre.','Ab uno opere nova lectio incipit.'],
    ['馆藏分类','Kategorien der Sammlung','Genera librorum'],
    ['全部馆藏','Alle Werke','Omnia opera'],
    ['搜索书名、作者或关键词','Nach Titel, Autor oder Stichwort suchen','Titulum, auctorem vel vocabulum quaerere'],
    ['搜索书名、作者…','Titel oder Autor suchen…','Titulum vel auctorem quaerere…'],
    ['馆藏 EPUB 已收录 · 译者、底本与修订信息将持续补充。','EPUBs sind verfügbar · Angaben zu Übersetzern, Textgrundlagen und Revisionen werden ergänzt.','Libri EPUB adsunt · Notitiae de translatoribus, editionibus et emendationibus paulatim addentur.'],
    ['请开启 JavaScript 查看馆藏，或直接进入阅览室打开 EPUB。','Bitte JavaScript aktivieren oder EPUBs direkt im Lesesaal öffnen.','JavaScript permitte ut catalogum videas, aut librum EPUB in conclavi legendi aperi.'],
    ['A NOTE FROM THE LIBRARY','AUS DER BIBLIOTHEK','DE CONSILIO BIBLIOTHECAE'],
    ['以翻译，','Durch Übersetzung','Translatione'],
    ['连接散落的语言。','getrennte Sprachen verbinden.','linguas dispersas coniungimus.'],
    ['因此，这城被称为巴别，因为全地的语言在那里被混淆了……','Darum erhielt die Stadt den Namen Babel, denn dort wurde die Sprache der ganzen Erde verwirrt …',''],
    ['《创世记》11:9 · 武加大译本节选','Genesis 11,9 · Auszug aus der Vulgata','Genesis 11,9 · Ex Vulgata excerptum'],
    ['中文为据拉丁文所译','Aus dem lateinischen Text übersetzt','Textus Latinus supra citatus'],
    ['巴别塔图书馆是一项个人翻译与阅读计划。它借用巴别塔的名字，希望通过翻译与注释，使散落在不同语言和时代中的文字，在中文中获得新的读者。','Die Babel-Bibliothek ist ein persönliches Übersetzungs- und Lektüreprojekt. Ihr Name erinnert an den Turm von Babel. Durch Übersetzungen und Anmerkungen sollen Texte aus verschiedenen Sprachen und Epochen neue Leser im Chinesischen finden.','Bibliotheca Turris Babel est consilium privatum translationis et lectionis. Nomen a turri Babel sumit, ut textus variis linguis et aetatibus dispersi, ope translationum et annotationum, novos lectores Sinice inveniant.'],
    ['本馆计划逐步译介部分教父著作、以《伊利亚特》为代表的古希腊作品、古代注疏，以及古典修辞学、格律学文献与其他古典作品。每部译作将尽可能注明底本，保留篇章、节号或行号，并附译注与修订记录。','Nach und nach sollen ausgewählte Werke der Kirchenväter, altgriechische Texte wie die Ilias, antike Kommentare sowie Schriften zur Rhetorik und Metrik und weitere antike Werke übersetzt werden. Jede Übersetzung soll möglichst ihre Textgrundlage nennen, Kapitel-, Abschnitts- oder Versnummern bewahren und Anmerkungen sowie einen Revisionsverlauf enthalten.','Paulatim vertentur quaedam opera Patrum, opera Graeca antiqua ut Ilias, commentarii antiqui, scripta de rhetorica et metrica aliaque opera antiqua. In singulis translationibus, quantum fieri potest, editio adhibita indicabitur; numeri capitum, sectionum vel versuum servabuntur, annotationes et emendationum memoria addentur.'],
    ['译文将在持续阅读与校订中逐步完善，也欢迎读者提出订正与讨论。愿这座小小的图书馆，为古典文字与今天的读者留下一处相遇之所。','Die Übersetzungen werden durch fortlaufende Lektüre und Überarbeitung verbessert. Hinweise, Korrekturen und Gespräche sind willkommen. Möge diese kleine Bibliothek ein Ort der Begegnung zwischen antiken Texten und heutigen Lesern sein.','Translationes continua lectione et recognitione emendabuntur. Correctiones et disputationes lectorum gratae sunt. Sit haec parva bibliotheca locus ubi litterae antiquae et lectores hodierni conveniant.'],
    ['在语言分散之处，让古典文字再次相遇。','Wo Sprachen auseinandergehen, antiken Texten wieder begegnen.','Ubi linguae disperguntur, litteris antiquis iterum occurramus.'],
    ['回到页首 ↑','Nach oben ↑','Ad initium ↑'],
    ['返回馆藏 ↗','Zur Sammlung ↗','Ad catalogum ↗'],
    ['返回馆藏','Zur Sammlung','Ad catalogum'],
    ['正在载入书目…','Werk wird geladen…','Notitiae libri leguntur…'],
    ['阅览室','Lesesaal','Conclave legendi'],
    ['章节目录','Inhaltsverzeichnis','Index capitum'],
    ['打开本机 EPUB','Lokale EPUB öffnen','EPUB e computatro aperire'],
    ['打开本机 EPUB 文件','Lokale EPUB-Datei öffnen','Librum EPUB e computatro aperire'],
    ['减小字号','Schrift verkleinern','Litteras minuere'],
    ['增大字号','Schrift vergrößern','Litteras augere'],
    ['深色阅读','Dunkler Modus','Colores obscuri'],
    ['浅色阅读','Heller Modus','Colores clari'],
    ['电子书正文','Text des E-Books','Textus libri electronici'],
    ['欢迎来到阅览室','Willkommen im Lesesaal','Salve in conclavi legendi'],
    ['从馆藏中选择一本书，或打开本机 EPUB。选择的本机文件只在浏览器中读取，不会上传。','Ein Werk aus der Sammlung wählen oder eine lokale EPUB öffnen. Lokale Dateien werden nur im Browser gelesen und nicht hochgeladen.','Librum e catalogo elige vel EPUB e computatro aperi. Fasciculi locales tantum in navigatro leguntur neque in rete mittuntur.'],
    ['试读内置样本 ↗','Leseprobe öffnen ↗','Exemplum lectionis aperire ↗'],
    ['← 上一页','← Vorige Seite','← Pagina prior'],
    ['下一页 →','Nächste Seite →','Pagina sequens →'],
    ['可调字号 · 支持章节导航','Schriftgröße anpassen · Kapitel auswählen','Magnitudinem litterarum mutare · Capitulum eligere'],
    ['请启用 JavaScript 使用 EPUB 阅读器。','Bitte JavaScript für den EPUB-Reader aktivieren.','JavaScript permitte ut libros EPUB legas.'],
    ['查看《{title}》介绍','Informationen zu {title}','De libro {title} legere'],
    ['可在线阅读','Online lesbar','In rete legendum'],
    ['示范书目','Beispieleintrag','Exemplum catalogi'],
    ['仅书目','Katalogeintrag','Notitiae tantum'],
    ['打开书籍 →','Werk öffnen →','Librum aperire →'],
    ['查看书目 →','Werk ansehen →','Notitias videre →'],
    ['显示 {count} 部作品','{count} Werke angezeigt','{count} opera ostenduntur'],
    ['显示 1 部作品','1 Werk angezeigt','1 opus ostenditur'],
    ['没有找到对应作品，请尝试其他关键词或分类。','Kein Werk gefunden. Bitte andere Stichwörter oder Kategorien versuchen.','Nullum opus inventum est. Alia vocabula vel genera tenta.'],
    ['本栏目尚未上传作品。','In dieser Kategorie sind noch keine Werke verfügbar.','Huic generi nondum opera addita sunt.'],
    ['没有找到这部作品','Werk nicht gefunden','Hoc opus non inventum est'],
    ['作品介绍','Über das Werk','De opere'],
    ['作品类型','Art des Werks','Genus operis'],
    ['学习笔记','Lernnotizen','Annotationes studiorum'],
    ['整理者','Zusammengestellt von','Ordinator'],
    ['教材作者','Autor des Lehrbuchs','Auctor libri didactici'],
    ['原作者','Autor','Auctor'],
    ['译者','Übersetzer','Translator'],
    ['所据版本','Textgrundlage','Editio adhibita'],
    ['修订日期','Letzte Revision','Dies recognitionis'],
    ['尚未填写','Noch nicht angegeben','Nondum indicatum'],
    ['模板示范内容，请替换为你的实际作品和版本信息。','Beispielinhalt: bitte durch das eigene Werk und seine Editionsangaben ersetzen.','Exemplum: opere tuo et notitiis editionis substituendum.'],
    ['在线阅读 ↗','Online lesen ↗','In rete legere ↗'],
    ['下载 EPUB ↓','EPUB herunterladen ↓','EPUB detrahere ↓'],
    ['此书目尚未附加 EPUB 文件。添加文件后即可启用阅读与下载。','Diesem Eintrag ist noch keine EPUB beigefügt. Nach dem Hinzufügen kann sie gelesen und heruntergeladen werden.','Huic libro nondum fasciculus EPUB adiunctus est. Eo addito, legi et detrahi poterit.'],
    ['以翻译，连接散落的语言。','Durch Übersetzung getrennte Sprachen verbinden.','Translatione linguas dispersas coniungimus.'],
    ['暂时无法跳转，请尝试章节目录。','Seitenwechsel derzeit nicht möglich. Bitte das Inhaltsverzeichnis verwenden.','Pagina mutari nunc non potest. Indicem capitum tenta.'],
    ['正在打开电子书','E-Book wird geöffnet','Liber electronicus aperitur'],
    ['第一次打开可能需要一些时间，请稍候。','Das erste Öffnen kann etwas dauern. Bitte einen Moment warten.','Liber primum aperitur; paulisper exspecta.'],
    ['正在读取…','Wird geladen…','Legitur…'],
    ['阅读器未能载入','Reader konnte nicht geladen werden','Instrumentum lectionis aperiri non potuit'],
    ['请检查 vendor 文件夹是否完整上传。你仍可以从作品介绍页下载 EPUB。','Bitte prüfen, ob der Ordner vendor vollständig hochgeladen wurde. Die EPUB kann weiterhin auf der Werkseite heruntergeladen werden.','Vide num directorium vendor totum additum sit. Librum EPUB ex pagina operis detrahere adhuc potes.'],
    ['阅读器组件缺失','Reader-Komponente fehlt','Pars instrumenti lectionis deest'],
    ['电子书无法打开','E-Book kann nicht geöffnet werden','Liber electronicus aperiri non potest'],
    ['请检查文件是否存在、格式是否正确，并确认没有 DRM 保护。','Bitte prüfen, ob die Datei vorhanden, das Format gültig und die Datei frei von DRM ist.','Vide num fasciculus adsit, forma recta sit et tutela DRM absit.'],
    ['打开失败','Öffnen fehlgeschlagen','Apertio non successit'],
    ['打开超时','Zeitüberschreitung beim Öffnen','Tempus aperiendi excessum est'],
    ['阅读中','Beim Lesen','Lectio'],
    ['{chapter} · 阅读位置保存在本浏览器','{chapter} · Leseposition in diesem Browser gespeichert','{chapter} · Locus lectionis in hoc navigatro servatur'],
    ['请确认 EPUB 文件已上传且可访问。若文件较大，可下载后离线阅读。','Bitte prüfen, ob die EPUB hochgeladen und erreichbar ist. Große Dateien können heruntergeladen und offline gelesen werden.','Vide num fasciculus EPUB additus sit et adiri possit. Si magnus est, eum detrahe et sine rete lege.'],
    ['打开失败：{error}','Öffnen fehlgeschlagen: {error}','Apertio non successit: {error}'],
    ['请选择 EPUB 文件','Bitte eine EPUB-Datei wählen','Fasciculum EPUB elige'],
    ['无法读取本机文件','Lokale Datei kann nicht gelesen werden','Fasciculus localis legi non potest'],
    ['这本书暂时无法阅读','Dieses Werk ist derzeit nicht lesbar','Hic liber nunc legi non potest'],
    ['没有找到书目，或该书尚未附加 EPUB 文件。请返回馆藏选择其他作品。','Der Eintrag wurde nicht gefunden oder enthält noch keine EPUB. Bitte ein anderes Werk aus der Sammlung wählen.','Notitiae libri non inventae sunt vel EPUB nondum adiunctus est. Ad catalogum redi et aliud opus elige.'],
    ['拉丁文 · 中文','Latein · Chinesisch','Latine · Sinice'],
    ['希腊文 · 中文','Griechisch · Chinesisch','Graece · Sinice'],
    ['希腊文 · 拉丁文 · 中文','Griechisch · Latein · Chinesisch','Graece · Latine · Sinice'],
    ['拉丁文 · 繁体中文','Latein · Chinesisch (traditionell)','Latine · Sinice (litteris traditis)'],
    ['希腊文 · 拉丁文 · 繁体中文','Griechisch · Latein · Chinesisch (traditionell)','Graece · Latine · Sinice (litteris traditis)'],
    ['英文 · 中文','Englisch · Chinesisch','Anglice · Sinice'],
    ['中文笔记 · 希腊文诗例 · 德语术语','Chinesische Notizen · Griechische Versbeispiele · Deutsche Fachbegriffe','Annotationes Sinicae · Exempla versuum Graecorum · Vocabula Germanica'],
    ['中文笔记 · 拉丁文诗例 · 德语术语','Chinesische Notizen · Lateinische Versbeispiele · Deutsche Fachbegriffe','Annotationes Sinicae · Exempla versuum Latinorum · Vocabula Germanica']
  ];
  const messages = Object.fromEntries(rows.map(([zh,de,la]) => [zh,{zh,de,la}]));
  const valid = lang => ['zh','de','la'].includes(lang);
  const readStored = () => {try {return localStorage.getItem('babel-language');} catch {return null;}};
  const query = new URLSearchParams(location.search).get('lang');
  const stored = readStored();
  let language = valid(query) ? query : valid(stored) ? stored : 'zh';
  const t = (key,params={}) => (messages[key]?.[language] ?? key).replace(/\{(\w+)\}/g,(_,name)=>String(params[name] ?? '{'+name+'}'));
  const ignored = '.language-switch,#book-grid,#book-detail,#reader-title,#reader-status,#placeholder-title,#placeholder-description,#chapter-select,#theme-toggle,script,style';
  const texts=[], attributes=[];
  const walker=document.createTreeWalker(document.body,NodeFilter.SHOW_TEXT);
  while(walker.nextNode()) {
    const node=walker.currentNode;
    if(node.parentElement.closest(ignored)) continue;
    const key=node.textContent.trim();
    if(messages[key]) texts.push({node,key,before:node.textContent.match(/^\s*/)[0],after:node.textContent.match(/\s*$/)[0]});
  }
  document.querySelectorAll('[placeholder],[aria-label],[alt]').forEach(node=>{
    ['placeholder','aria-label','alt'].forEach(name=>{
      const key=node.getAttribute(name);if(messages[key]) attributes.push({node,name,key});
    });
  });
  const description=document.querySelector('meta[name="description"]');
  if(description)attributes.push({node:description,name:'content',key:description.content});
  const pageTitle=document.title.startsWith('作品介绍')?'作品介绍':document.title.startsWith('阅览室')?'阅览室':null;
  const controls=[];
  const host=document.querySelector('.site-header nav,.reader-header');
  if(host) {
    const select=document.getElementById('site-language');
    const caption=host.querySelector('.language-switch span');
    controls.push({caption,select});
    select.disabled=false;
    select.addEventListener('change',()=>setLanguage(select.value));
  }
  const apply=()=>{
    document.documentElement.lang=language==='zh'?'zh-CN':language;
    texts.forEach(({node,key,before,after})=>node.textContent=before+t(key)+after);
    attributes.forEach(({node,name,key})=>node.setAttribute(name,t(key)));
    controls.forEach(({caption,select})=>{caption.textContent=t('语言');select.value=language;});
    document.querySelectorAll('.brand small,.site-footer div>span').forEach(node=>node.textContent=language==='la'?'巴别塔图书馆':'Bibliotheca Turris Babel');
    document.title=pageTitle?t(pageTitle)+' · '+t('巴别塔图书馆'):language==='la'?'Bibliotheca Turris Babel':t('巴别塔图书馆')+' · Bibliotheca Turris Babel';
    try{localStorage.setItem('babel-language',language);}catch{}
    document.dispatchEvent(new CustomEvent('babel:language',{detail:{language}}));
  };
  const setLanguage=lang=>{
    if(!valid(lang))return;
    language=lang;
    const url=new URL(location.href);url.searchParams.set('lang',language);
    try{history.replaceState(null,'',url);}catch{}
    apply();
  };
  // 在网页之间带上所选语言；直接分享带 lang 的网址也能打开对应版式。
  document.addEventListener('click',event=>{
    const link=event.target.closest('a[href]');if(!link||link.hasAttribute('download'))return;
    const url=new URL(link.href,location.href);
    if(url.origin===location.origin&&/\.html$/.test(url.pathname)){
      url.searchParams.set('lang',language);link.href=url.href;
    }
  });
  window.addEventListener('popstate',()=>{
    const lang=new URLSearchParams(location.search).get('lang');if(valid(lang)){language=lang;apply();}
  });
  window.BABEL_I18N={t,setLanguage,get language(){return language;},keys:Object.keys(messages)};
  apply();
})();
