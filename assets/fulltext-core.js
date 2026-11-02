/* EPUB text is kept in reading order, including matches split across inline elements. */
(function(root){
  function parts(doc){
    const walker=doc.createTreeWalker(doc.body||doc.documentElement,4),nodes=[];let text='',node;
    while((node=walker.nextNode())){if(node.parentElement?.closest('script,style,noscript,head'))continue;const start=text.length;text+=node.data;nodes.push({node,start,end:text.length});}
    return {text,parts:nodes};
  }
  const fold=text=>text.normalize('NFC').toLowerCase().replace(/ς/g,'σ');
  function occurrences(text,query,limit){
    const needle=fold(query),out=[];if(!needle)return out;
    let hay='';const starts=[],ends=[];
    // Preserve offsets in the original UTF-16 text when accents or case fold change length.
    for(const m of text.matchAll(/\P{M}\p{M}*|\p{M}+/gu)){
      const chunk=fold(m[0]);hay+=chunk;
      for(let i=0;i<chunk.length;i++){starts.push(m.index);ends.push(m.index+m[0].length);}
    }
    let from=0,pos;while(out.length<limit&&(pos=hay.indexOf(needle,from))!==-1){out.push({start:starts[pos],end:ends[pos+needle.length-1]});from=pos+needle.length;}return out;
  }
  function find(section,doc,query,limit){
    const {text,parts:nodes}=parts(doc),out=[];
    for(const {start,end} of occurrences(text,query,limit)){
      const a=nodes.find(p=>p.start<=start&&p.end>start),b=nodes.find(p=>p.start<end&&p.end>=end);
      if(a&&b){const range=doc.createRange();range.setStart(a.node,start-a.start);range.setEnd(b.node,end-b.start);out.push({cfi:section.cfiFromRange(range),snippet:text.slice(Math.max(0,start-42),Math.min(text.length,end+42)).replace(/\s+/g,' ').trim()});}
    }return out;
  }
  const api={parts,find,fold,occurrences};if(typeof module!=='undefined'&&module.exports)module.exports=api;else root.BABEL_FULLTEXT_CORE=api;
})(typeof window!=='undefined'?window:globalThis);
