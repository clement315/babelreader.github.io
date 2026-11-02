const assert=require('node:assert/strict');
const vm=require('node:vm');
const fs=require('node:fs');
class Element{
 constructor(tag){this.tagName=tag.toUpperCase();this.children=[];this.listeners={};this.hidden=false;this.disabled=false;this.isConnected=true;this.value='';this.textContent='';}
 append(...nodes){this.children.push(...nodes);}
 replaceChildren(...nodes){this.children=nodes;}
 setAttribute(k,v){this[k]=v;}
 addEventListener(k,fn){(this.listeners[k]??=[]).push(fn);}
 focus(){document.activeElement=this;}
 select(){}
 async fire(type,event={}){for(const fn of this.listeners[type]||[])await fn({preventDefault(){},...event});}
}
const document={body:new Element('body'),documentElement:{lang:'zh-CN'},listeners:{},activeElement:null,createElement:t=>new Element(t),addEventListener(k,fn){(this.listeners[k]??=[]).push(fn);}};
const window={};
vm.runInNewContext(fs.readFileSync('assets/fulltext-search.js','utf8'),{window,document});
let jumped=null;
const mount=new Element('div');
const ui=window.BABEL_FULLTEXT.create({mount,search:async(q,progress)=>{progress(1,1);return {results:[{label:'Section',snippet:'Before '+q+' after',cfi:'epubcfi(test)'}]};},onJump:async item=>{jumped=item;return true;}});
const panel=document.body.children[0],form=panel.children[1],input=form.children[0],status=panel.children[3],list=panel.children[4];
ui.setEnabled(false);let blocked=false;ui.keydown({ctrlKey:true,key:'f',preventDefault(){blocked=true;}});assert.equal(panel.hidden,true);
ui.setEnabled(true);ui.keydown({ctrlKey:true,key:'f',preventDefault(){blocked=true;}});assert.equal(panel.hidden,false);assert.equal(blocked,true);assert.equal(document.activeElement,input);
input.value='λόγος';
(async()=>{await form.fire('submit');assert.equal(list.children.length,1);assert.match(status.textContent,/1/);await list.children[0].children[0].fire('click');assert.equal(jumped.cfi,'epubcfi(test)');assert.equal(panel.hidden,true);ui.reset();assert.equal(list.children.length,0);console.log('Search UI: shortcut, result rendering, navigation and reset passed.');})().catch(e=>{console.error(e);process.exitCode=1;});
