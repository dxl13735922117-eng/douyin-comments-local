// SPDX-License-Identifier: MIT
// Minimal DOM test doubles: deterministic unit tests, not a real-browser claim.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');
class Element {
  constructor(tag,attrs={},children=[]) {
    this.nodeType=1; this.tagName=tag.toUpperCase();this.attrs={...attrs};
    this.childNodes=children.map(x=>typeof x==='string'?{nodeType:3,textContent:x}:x);
    for (const c of this.childNodes)c.parentElement=this;
    this.parentElement=null;
  }
  hasAttribute(k){return Object.hasOwn(this.attrs,k);}
  getAttribute(k){return this.attrs[k]??null;}
  getClientRects(){return this.attrs.hidden!==undefined||this.attrs.contents?[]:[{}];}
  matches(s){
    return s.split(',').some(p=>{
      p=p.trim();
      if(p==='*')return true;
      if(p.startsWith('.'))return (this.attrs.class||'').split(' ').includes(p.slice(1));
      if(p==='[hidden]')return this.hasAttribute('hidden');
      if(p==='[aria-hidden="true"]')return this.attrs['aria-hidden']==='true';
      return this.tagName===p.toUpperCase();
    });
  }
  closest(s){for(let n=this;n;n=n.parentElement)if(n.matches(s))return n;return null;}
  querySelectorAll(s){
    const result=[];
    const walk=n=>{for(const c of n.childNodes)if(c.nodeType===1){if(c.matches(s))result.push(c);walk(c);}};
    walk(this);return result;
  }
  querySelector(s){return this.querySelectorAll(s)[0]||null;}
  get innerText(){return this.childNodes.map(n=>n.nodeType===3?n.textContent:n.innerText).join('');}
}
const e=(tag,attrs,...children)=>new Element(tag,attrs,children);
const item=(id,text,children=[])=>e('div',{class:'item'},
  e('i',{class:'id','data-id':id}),e('a',{class:'author'},'虚构用户'),
  e('span',{class:'body'},...text),e('span',{class:'likes'},'2'),e('span',{class:'time'},'昨天'),...children);
const reply=item('r1',['虚构回复']);
const top=item('t1',['混合',e('img',{alt:'[笑]'}),'表情'],[reply,e('button',{},'展开更多')]);
const second=item('t2',['第二条']);
const hidden=item('h1',['隐藏']);hidden.attrs.hidden='';
const root=e('div',{class:'root'},top,second,hidden);
const doc=e('document',{},root,e('span',{class:'counter',contents:true},e('b',{},'7')));
doc.title='虚构页面';
const source=fs.readFileSync(path.join(__dirname,'..','skills','douyin-comments-local','scripts','read_comments.js'),'utf8');
const reader=vm.runInNewContext('('+source+')',{document:doc});
const cfg={video_id:'123',root:'.root',top:'.item',body:'.body',author:'.author',likes:'.likes',
  time:'.time',id_node:'.id',id_attribute:'data-id',id_prefix:'',counter:'.counter',limit:1};
const batch=reader(cfg);
assert.equal(batch.comments.length,1);
assert.equal(batch.comments[0].text,'混合[笑]表情');
assert.equal(batch.comments[0].replies.length,1);
assert.equal(batch.comments[0].replies[0].cid,'r1');
assert.equal(batch.matched_top_nodes,2);
assert.equal(batch.has_more,true);
assert.equal(batch.unexpanded[0].parent_cid,'t1');
assert.equal(batch.page_count_text,'7');
assert.equal(reader({...cfg,offset:1}).comments[0].cid,'t2');
assert.throws(()=>reader({...cfg,root:'.missing'}),/exactly one/);
assert.throws(()=>reader({...cfg,body:'.missing'}),/no readable body/);
assert.throws(()=>reader({...cfg,video_id:'bad'}),/video_id/);
assert.equal(root.querySelectorAll('.item').length,4); // Nothing was removed or mutated.
console.log('DOM reader unit cases passed (synthetic DOM, not end-to-end).');
