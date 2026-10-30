/* Tenant Recipes unified search: instant grouped results, autocomplete (ghost text + suggestions), typo tolerance,
   synonyms and a question map. Index: search/index.json, built at build time. Runs fully in the browser. */
(function(){
"use strict";
var me=document.currentScript,ROOT=me?new URL("../",me.src).href:"/";
var IDX=null,LOAD=null,DOCS=[],VOC=[],VOCSET={},SYN=[],QS=[],SUG=[];
var STOP={"how":1,"do":1,"i":1,"to":1,"the":1,"a":1,"an":1,"in":1,"on":1,"of":1,"for":1,"my":1,"what":1,"is":1,"are":1,"can":1,"should":1,"with":1,"and":1,"before":1,"after":1,"does":1,"it":1,"we":1,"our":1,"you":1,"your":1,"from":1,"by":1,"at":1,"be":1,"who":1,"which":1,"why":1,"when":1,"me":1,"get":1,"need":1,"about":1,"or":1};
var GROUPS=[["Vulnerability","Vulnerabilities"],["Recipe","Recipes"],["Guide","Guides"],["Hardening","Hardening"],["Tool","Tools"],["News","News"],["Page","Pages"]];
function esc(s){return String(s).replace(/[&<>"]/g,function(c){return{"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]})}
function norm(s){return String(s||"").toLowerCase().replace(/[\u2018\u2019]/g,"'").replace(/[\u201c\u201d]/g,'"').replace(/\s+/g," ").trim()}
function words(s){return norm(s).split(/[^a-z0-9\-\.']+/).map(function(w){return w.replace(/^[\-\.']+|[\-\.']+$/g,"")}).filter(Boolean)}
function load(){if(LOAD)return LOAD;LOAD=fetch(ROOT+"search/index.json").then(function(r){return r.json()}).then(function(j){IDX=j;SYN=j.syn;QS=j.q.map(function(x){return{q:x[0],u:x[1],w:words(x[0]).filter(function(w){return!STOP[w]})}});
SUG=j.sug.map(function(s){return{s:s,n:norm(s)}});
DOCS=j.docs.map(function(d){var strong=norm([d.t,(d.cve||[]).join(" "),d.p||"",(d.g||[]).join(" "),d.c||""].join(" "));
var hay=strong+" "+norm((d.s||"")+" "+(d.x||""));words(hay).forEach(function(w){if(w.length>2&&!VOCSET[w]){VOCSET[w]=1;VOC.push(w)}});
return{d:d,t:norm(d.t),strong:strong,hay:hay,cve:(d.cve||[]).map(norm)}});return j});return LOAD}
function lev(a,b,max){if(Math.abs(a.length-b.length)>max)return max+1;var pp=null,p=[],i,j;for(j=0;j<=b.length;j++)p[j]=j;
for(i=1;i<=a.length;i++){var c=[i],mn=i;for(j=1;j<=b.length;j++){var x=Math.min(p[j]+1,c[j-1]+1,p[j-1]+(a[i-1]===b[j-1]?0:1));
if(pp&&j>1&&a[i-1]===b[j-2]&&a[i-2]===b[j-1])x=Math.min(x,pp[j-2]+1);c[j]=x;if(x<mn)mn=x}pp=p;p=c;if(mn>max)return max+1}return p[b.length]}
function known(w){if(VOCSET[w])return true;if(/\d/.test(w))return true;for(var i=0;i<VOC.length;i++)if(VOC[i].indexOf(w)===0)return true;return false}
function fix(w){if(w.length<4||known(w))return w;var max=w.length<=6?1:2,best=null,bd=max+1;
for(var i=0;i<VOC.length;i++){var v=VOC[i];if(Math.abs(v.length-w.length)>max||v[0]!==w[0]&&max<2)continue;var d=lev(w,v,max);if(d<bd||(d===bd&&best&&v.length<best.length)){bd=d;best=v}}return best||w}
/* parse: query -> concepts [{alts:[...], syn:bool}] + corrected string */
function parse(q){var ws=words(q),meaningful=ws.filter(function(w){return!STOP[w]});
var fixed=meaningful.map(fix),corr=fixed.join(" "),changed=fixed.some(function(w,i){return w!==meaningful[i]});
var used={},concepts=[],s=" "+corr+" ";
SYN.forEach(function(g){g.forEach(function(term){if(s.indexOf(" "+term+" ")>=0){var tw=term.split(" "),hit=tw.every(function(w){return!used[w]});if(hit){tw.forEach(function(w){used[w]=1});concepts.push({alts:[term].concat(g.filter(function(x){return x!==term})),o:term})}}})});
fixed.forEach(function(w){if(!used[w]){var alts=[w];SYN.forEach(function(g){if(g.indexOf(w)>=0)g.forEach(function(x){if(x!==w)alts.push(x)})});concepts.push({alts:alts,o:w})}});
return{c:concepts,corr:corr,changed:changed,raw:ws}}
function search(q){if(!IDX)return null;var P=parse(q);if(!P.c.length)return{p:P,r:[]};var n=P.c.length,need=n<=2?n:Math.ceil(n*0.6),qn=norm(q),out=[];
var best={};QS.forEach(function(x){var ov=0;P.c.forEach(function(c){if(c.alts.some(function(a){return x.q.indexOf(a)>=0}))ov++});if(n>=2&&ov>=Math.max(2,Math.ceil(n*0.6))&&ov/Math.max(1,x.w.length)>=0.5)best[x.u]=(best[x.u]||0)+ov*8});
DOCS.forEach(function(D){var sc=0,hit=0;P.c.forEach(function(c){var m=0;c.alts.forEach(function(a,i){var f=i===0?1:0.7,v=0;if(D.t.indexOf(a)>=0)v=6;else if(D.strong.indexOf(a)>=0)v=4;else if(D.hay.indexOf(a)>=0)v=1.5;if(D.cve.indexOf(a)>=0)v=20;m=Math.max(m,v*f)});if(m){hit++;sc+=m}});
if(hit<need)return;if(D.t.indexOf(qn)===0)sc+=8;var b=best[D.d.u];if(b)sc+=30+b;out.push({s:sc,D:D,best:!!b})});
out.sort(function(a,b){return b.s-a.s||(b.D.d.d||"").localeCompare(a.D.d.d||"")});return{p:P,r:out}}
function suggest(q,P){var qn=norm(q);if(qn.length<2)return[];var last=P?P.corr:qn,res=[],qw=words(qn),cw=P?words(P.corr):qw;
SUG.forEach(function(x){var sc=0;if(x.n.indexOf(qn)===0)sc=100-x.n.length/4;else{var sw=x.n.split(/[^a-z0-9\-\.']+/);
var ok=cw.length&&cw.every(function(w){return sw.some(function(v){return v.indexOf(w)===0})});if(ok)sc=50-x.n.length/4;else if((qw.length>1||qn.length>=4)&&x.n.indexOf(qn)>0)sc=40;else if(P&&P.c.length&&P.c.every(function(c){return c.alts.some(function(a){return a.indexOf(" ")>0?x.n.indexOf(a)>=0:sw.some(function(v){return v.indexOf(a)===0})})}))sc=30-x.n.length/4}
if(sc>0){if(/^(how|what|who|which)\b/.test(qn)&&/^(how|what|who|which)\b/.test(x.n))sc+=20;res.push([sc,x.s])}});
res.sort(function(a,b){return b[0]-a[0]});var seen={},o=[];for(var i=0;i<res.length&&o.length<5;i++){var k=res[i][1].toLowerCase();if(k!==qn&&!seen[k]){seen[k]=1;o.push(res[i][1])}}return o}
function meta(d){var m=[d.c];if(d.cve&&d.cve.length)m.push(d.cve.slice(0,2).join(", ")+(d.cve.length>2?" +"+(d.cve.length-2):""));return m.filter(Boolean).join(" · ")}
function group(r,lim){var by={},order=[];r.forEach(function(x){var k=x.D.d.k;if(!by[k]){by[k]=[];order.push(k)}by[k].push(x)});
var label={};GROUPS.forEach(function(g){label[g[0]]=g[1]});return order.map(function(k){return{k:k,l:label[k]||k,items:lim?by[k].slice(0,lim):by[k],n:by[k].length}})}
function hl(t,P){var s=esc(t);if(!P)return s;P.c.forEach(function(c){c.alts.slice(0,3).forEach(function(a){if(a.length<2)return;var re=new RegExp("("+a.replace(/[.*+?^${}()|[\]\\]/g,"\\$&")+")","ig");s=s.replace(re,"<mark>$1</mark>")})});return s.replace(/<mark>([^<]*)<mark>([^<]*)<\/mark>([^<]*)<\/mark>/g,"<mark>$1$2$3</mark>")}
var uid=0;
/* ---------- dropdown combobox ---------- */
function attach(inp,opts){opts=opts||{};if(inp._sx)return;inp._sx=1;var id="sx"+(++uid),form=inp.form;
var wrap=document.createElement("span");wrap.className="sx-gw";inp.parentNode.insertBefore(wrap,inp);wrap.appendChild(inp);
var ghost=document.createElement("span");ghost.className="sx-ghost";ghost.setAttribute("aria-hidden","true");wrap.insertBefore(ghost,inp);
var pop=document.createElement("div");pop.className="sx-pop";pop.id=id+"-l";pop.setAttribute("role","listbox");pop.setAttribute("aria-label","Search suggestions and results");pop.hidden=true;
(opts.popParent||form||inp.parentNode).appendChild(pop);
inp.setAttribute("role","combobox");inp.setAttribute("aria-autocomplete","both");inp.setAttribute("aria-expanded","false");inp.setAttribute("aria-controls",pop.id);inp.setAttribute("autocomplete","off");
var act=-1,opt=[],gtext="";
function copyFont(){var cs=getComputedStyle(inp);["fontSize","fontFamily","fontWeight","letterSpacing","paddingLeft","paddingRight","paddingTop","paddingBottom","lineHeight","textIndent"].forEach(function(p){ghost.style[p]=cs[p]})}
function setGhost(sugs){var v=inp.value;gtext="";if(v&&sugs.length&&document.activeElement===inp){var s=sugs[0];if(s.toLowerCase().indexOf(v.toLowerCase())===0&&s.length>v.length)gtext=v+s.slice(v.length)}
ghost.innerHTML=gtext?'<span class="sx-gv">'+esc(v)+"</span>"+esc(gtext.slice(v.length)):""}
function close(){pop.hidden=true;inp.setAttribute("aria-expanded","false");inp.removeAttribute("aria-activedescendant");act=-1;ghost.innerHTML="";gtext=""}
function go(href){location.href=href}
function all(){return ROOT+"search/index.html?q="+encodeURIComponent(inp.value.trim())}
function render(){var q=inp.value.trim();if(!q){close();return}
load().then(function(){var R=search(q),sugs=suggest(q,R&&R.p),h="",k=0;copyFont();setGhost(sugs);
if(R&&R.p.changed)h+='<p class="sx-fix">Showing results for <strong>'+esc(R.p.corr)+"</strong></p>";
if(sugs.length){h+='<div class="sx-sec" role="group" aria-label="Suggestions"><p class="sx-h" aria-hidden="true">Suggestions</p>';
sugs.forEach(function(s){h+='<div class="sx-o sx-sug" role="option" id="'+id+"-"+(k++)+'" data-q="'+esc(s)+'" aria-selected="false"><svg class="ic" viewBox="0 0 24 24" aria-hidden="true"><circle cx="11" cy="11" r="6"/><path d="M20 20l-4.5-4.5"/></svg><span>'+hl(s,R&&R.p)+"</span></div>"});h+="</div>"}
var G=R?group(R.r,4):[];G.forEach(function(g){h+='<div class="sx-sec" role="group" aria-label="'+esc(g.l)+'"><p class="sx-h" aria-hidden="true">'+esc(g.l)+(g.n>g.items.length?' <span>'+g.n+"</span>":"")+"</p>";
g.items.forEach(function(x){var d=x.D.d;h+='<a class="sx-o sx-res'+(x.best?" sx-best":"")+'" role="option" id="'+id+"-"+(k++)+'" href="'+ROOT+esc(d.u)+'" aria-selected="false"><strong>'+hl(d.t,R.p)+"</strong><span>"+(x.best?'<em>Best match</em> · ':"")+esc(meta(d))+"</span></a>"});h+="</div>"});
var n=R?R.r.length:0;h+='<a class="sx-o sx-all" role="option" id="'+id+"-"+(k++)+'" href="'+esc(all())+'" aria-selected="false">'+(n?"See all "+n+" result"+(n===1?"":"s"):"No matches yet: search everything")+" for \u201c"+esc(q)+"\u201d \u2192</a>";
pop.innerHTML=h;opt=[].slice.call(pop.querySelectorAll(".sx-o"));act=-1;pop.hidden=false;inp.setAttribute("aria-expanded","true");inp.removeAttribute("aria-activedescendant")})}
function mark(i){opt.forEach(function(o,j){o.setAttribute("aria-selected",j===i?"true":"false");o.classList.toggle("on",j===i)});act=i;if(i>=0){inp.setAttribute("aria-activedescendant",opt[i].id);opt[i].scrollIntoView({block:"nearest"})}else inp.removeAttribute("aria-activedescendant")}
function pick(o){if(o.classList.contains("sx-sug")){inp.value=o.getAttribute("data-q");render();inp.focus()}else go(o.href)}
inp.addEventListener("input",render);inp.addEventListener("focus",function(){load();if(inp.value.trim())render()});
inp.addEventListener("keydown",function(e){var k=e.key;
if(k==="ArrowDown"||k==="ArrowUp"){if(pop.hidden){render();return}e.preventDefault();if(!opt.length)return;var i=k==="ArrowDown"?(act+1)%opt.length:(act<=0?opt.length-1:act-1);mark(i)}
else if(k==="Enter"){if(act>=0&&!pop.hidden){e.preventDefault();pick(opt[act])}else if(form){e.preventDefault();go(all())}}
else if(k==="Escape"){if(!pop.hidden){e.preventDefault();close()}else if(opts.onEsc)opts.onEsc()}
else if((k==="Tab"&&!e.shiftKey||k==="ArrowRight"&&inp.selectionStart===inp.value.length)&&gtext){e.preventDefault();inp.value=gtext;render()}});
pop.addEventListener("mousedown",function(e){var o=e.target.closest(".sx-o");if(o&&o.classList.contains("sx-sug")){e.preventDefault();pick(o)}});
document.addEventListener("click",function(e){if(!wrap.contains(e.target)&&!pop.contains(e.target))close()});
if(form)form.addEventListener("submit",function(e){e.preventDefault();go(all())});
if(inp.value.trim()&&document.activeElement===inp)render();return{close:close,render:render}}
/* ---------- header overlay ---------- */
var ov=null;function openOverlay(){if(!ov){ov=document.createElement("div");ov.className="sx-ov";ov.setAttribute("role","dialog");ov.setAttribute("aria-modal","true");ov.setAttribute("aria-label","Search Tenant Recipes");
ov.innerHTML='<div class="sx-box"><form class="fd-s sx-f" action="'+ROOT+'search/index.html" method="get" role="search"><svg class="ic" viewBox="0 0 24 24" aria-hidden="true"><circle cx="11" cy="11" r="6"/><path d="M20 20l-4.5-4.5"/></svg>'
+'<label class="sr" for="sx-ov-q">Search everything</label><input id="sx-ov-q" name="q" type="search" placeholder="Search recipes, CVEs, guides\u2026"><button class="sx-x" type="button" aria-label="Close search">Esc</button></form></div>';
document.body.appendChild(ov);var i=ov.querySelector("input");attach(i,{onEsc:closeOverlay});ov.querySelector(".sx-x").onclick=closeOverlay;ov.addEventListener("mousedown",function(e){if(e.target===ov)closeOverlay()})}
ov.hidden=false;document.documentElement.classList.add("sx-lock");var inp=ov.querySelector("input");setTimeout(function(){inp.focus();inp.select()},0);load()}
function closeOverlay(){if(ov){ov.hidden=true;document.documentElement.classList.remove("sx-lock")}}
/* ---------- results page ---------- */
function page(inp){var r=document.getElementById("sxp-r"),n=document.getElementById("sxp-n"),ch=document.getElementById("sxp-chips"),cur="All";
var p=new URLSearchParams(location.search).get("q");if(p)inp.value=p;
function draw(){var q=inp.value.trim();if(!q){r.innerHTML="";n.textContent="Type to search recipes, guides, vulnerabilities, hardening and news.";ch.innerHTML="";return}
load().then(function(){var R=search(q),G=group(R.r,0),types=["All"].concat(G.map(function(g){return g.k}));if(types.indexOf(cur)<0)cur="All";
ch.innerHTML=types.map(function(t){var g=G.filter(function(x){return x.k===t})[0];return'<button type="button" class="chip'+(t===cur?" on":"")+'" data-t="'+t+'" aria-pressed="'+(t===cur)+'">'+(t==="All"?"All":esc(g.l))+" <span>"+(t==="All"?R.r.length:g.n)+"</span></button>"}).join("");
n.innerHTML=(R.p.changed?"Showing results for <strong>"+esc(R.p.corr)+"</strong> · ":"")+R.r.length+" result"+(R.r.length===1?"":"s")+" for \u201c"+esc(q)+"\u201d";
r.innerHTML=G.filter(function(g){return cur==="All"||g.k===cur}).map(function(g){return'<section class="sxp-g"><h2>'+esc(g.l)+" <span>"+g.n+'</span></h2><ol class="ss-r">'+g.items.map(function(x){var d=x.D.d;
return'<li><a href="'+ROOT+esc(d.u)+'"><span class="ss-k">'+(x.best?"Best match · ":"")+esc(meta(d))+"</span><strong>"+hl(d.t,R.p)+"</strong><span>"+esc(d.s||"")+"</span></a></li>"}).join("")+"</ol></section>"}).join("")||'<p>No matches. Try fewer or different words, a product name or a CVE id.</p>'})}
ch.addEventListener("click",function(e){var b=e.target.closest("button[data-t]");if(b){cur=b.getAttribute("data-t");draw()}});
var t;inp.addEventListener("input",function(){clearTimeout(t);t=setTimeout(function(){var u=new URL(location);inp.value?u.searchParams.set("q",inp.value):u.searchParams.delete("q");history.replaceState(null,"",u);draw()},120)});
if(inp.form)inp.form.addEventListener("submit",function(e){e.preventDefault();draw()});draw()}
function init(){document.querySelectorAll("input[data-sx]").forEach(function(i){var w=i.getAttribute("data-ph-wide");if(w&&innerWidth>640)i.placeholder=w;attach(i)});var pg=document.querySelector("input[data-sx-page]");if(pg)page(pg);
document.querySelectorAll("[data-sx-open]").forEach(function(a){a.addEventListener("click",function(e){if(e.metaKey||e.ctrlKey)return;e.preventDefault();openOverlay()})});
document.addEventListener("keydown",function(e){var t=e.target,typing=t&&(t.tagName==="INPUT"||t.tagName==="TEXTAREA"||t.isContentEditable);
if(e.key==="/"&&!typing&&!e.metaKey&&!e.ctrlKey){e.preventDefault();var h=document.querySelector("input[data-sx]");if(h&&h.getBoundingClientRect().bottom>0&&h.getBoundingClientRect().top<innerHeight)h.focus();else if(pg)pg.focus();else openOverlay()}
else if(e.key==="Escape"&&ov&&!ov.hidden)closeOverlay()})}
if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",init);else init();
window.TRSearch={search:function(q){return load().then(function(){return search(q)})},suggest:function(q){return load().then(function(){return suggest(q,parse(q))})}};
})();
