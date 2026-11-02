/* EPUB text is kept in reading order, including matches split across inline elements. */
(function(root){
  function parts(doc){
    const walker=doc.createTreeWalker(doc.body||doc.documentElement,4),nodes=[];let text='',node;
    while((node=walker.nextNode())){if(node.parentElement?.closest('script,style,noscript,head'))continue;const start=text.length;text+=node.data;nodes.push({node,start,end:text.length});}
    return {text,parts:nodes};
  }
  function find(section,doc,query,limit){
    const {text,parts:nodes}=parts(doc),needle=query.toLowerCase(),hay=text.toLowerCase(),out=[];if(!needle)return out;let from=0,pos;
    while(out.length<limit&&(pos=hay.indexOf(needle,from))!==-1){const end=pos+needle.length,a=nodes.find(p=>p.start<=pos&&p.end>pos),b=nodes.find(p=>p.start<end&&p.end>=end);
      if(a&&b){const range=doc.createRange();range.setStart(a.node,pos-a.start);range.setEnd(b.node,end-b.start);out.push({cfi:section.cfiFromRange(range),snippet:text.slice(Math.max(0,pos-42),Math.min(text.length,end+42)).replace(/\s+/g,' ').trim()});}from=pos+Math.max(1,needle.length);
    }return out;
  }
  const api={parts,find};if(typeof module!=='undefined'&&module.exports)module.exports=api;else root.BABEL_FULLTEXT_CORE=api;
})(typeof window!=='undefined'?window:globalThis);
