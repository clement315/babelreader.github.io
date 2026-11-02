const assert=require('node:assert/strict');
const {parts,find}=require('../assets/fulltext-core.js');

function documentFrom(items){
 const nodes=items.map(([data,ignored=false])=>({data,parentElement:{closest:()=>ignored?{}:null}}));
 return {body:{},createTreeWalker(){let i=0;return {nextNode:()=>nodes[i++]||null};},createRange(){return {setStart(node,offset){this.start={node,offset};},setEnd(node,offset){this.end={node,offset};}};}};
}
const doc=documentFrom([['In prin'],['cipio '],['SCRIPT',true],['erat Verbum. '],['Verbum erat.']]);
const section={cfiFromRange(r){return `${r.start.node.data}:${r.start.offset}..${r.end.node.data}:${r.end.offset}`;}};
assert.equal(parts(doc).text,'In principio erat Verbum. Verbum erat.');
const crossing=find(section,doc,'principio',10);
assert.equal(crossing.length,1);
assert.equal(crossing[0].cfi,'In prin:3..cipio :5');
assert.equal(find(section,doc,'VERBUM',10).length,2);
assert.equal(find(section,doc,'verbum',1).length,1);
assert.equal(find(section,doc,'script',10).length,0);
assert.equal(find(section,doc,'',10).length,0);
console.log('EPUB text search: cross-node ranges, case, limits, and excluded text passed.');
