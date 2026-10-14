// 新增书籍时，复制一条记录并修改字段。file 为相对于网站根目录的 EPUB 路径。
window.BABEL_BOOKS = [
  {id:'patristics',title:'教父作品',originalTitle:'OPERA PATRUM',author:'待选编',category:'教父作品',language:'希腊文 · 拉丁文 → 中文',color:'green',mark:'P',description:'早期基督教作者的著作与诠释，关注思想、文本与文学表达。具体作者、底本和篇目将按翻译计划填写。',translator:'待填写',edition:'待填写所据原文版本与出版信息。',updated:'',file:null,demo:true},
  {id:'iliad',title:'伊利亚特',originalTitle:'Ἰλιάς',author:'荷马',category:'伊利亚特',language:'希腊文 → 中文',color:'ochre',mark:'Ι',description:'围绕阿喀琉斯的愤怒展开的荷马史诗。译介将保留篇章与行号，并结合必要的译注与版本说明。',translator:'待填写',edition:'待填写所据原文版本与出版信息。',updated:'',file:null,demo:true},
  {id:'scholia',title:'古代注疏',originalTitle:'SCHOLIA',author:'待选编',category:'古代注疏',language:'希腊文 · 拉丁文 → 中文',color:'wine',mark:'Σ',description:'古人围绕经典文本留下的注释、解释与评议，为理解词句、典故与古代阅读传统提供线索。',translator:'待填写',edition:'待填写所据原文版本与出版信息。',updated:'',file:null,demo:true},
  {id:'latin-metrics',title:'拉丁格律学',originalTitle:'METRICA LATINA',author:'待选编',category:'拉丁格律学',language:'拉丁文 → 中文',color:'slate',mark:'M',description:'有关拉丁诗歌音节长短、音步与诗体的文献。选编篇目、术语说明与底本信息将随译作逐步补充。',translator:'待填写',edition:'待填写所据原文版本与出版信息。',updated:'',file:null,demo:true}
];

// 阅读样本只供阅览室试读，不占用四张展示封面。
window.BABEL_READING_SAMPLE = {id:'reading-demo',title:'巴别塔阅读样本',file:'books/reading-demo.epub'};
