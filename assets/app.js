/* Homepage library: topic filter + search. Tags are computed at build time (build_ux.tags_for). Supports ?t=<tag>&q=<text>. */
(function(){var R=window.RECIPES,g=document.getElementById("grid"),q=document.getElementById("q")||{value:""},c=document.getElementById("chips"),n=document.getElementById("count");if(!g)return;
var cnt={};R.forEach(function(r){r.tg.forEach(function(t){cnt[t]=(cnt[t]||0)+1})});
var order=["Copilot","Conditional Access","Identity","Intune","Purview & DLP","Agents","Licensing","Security","News / Retirement","PowerShell & Graph","Prompts"];
var tags=["All"].concat(order.filter(function(t){return cnt[t]}));
var P=new URLSearchParams(location.search),cur=P.get("t")||"All";if(tags.indexOf(cur)<0)cur="All";if(q.addEventListener)q.value=P.get("q")||"";
var M=["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"];function fd(d){var p=d.split("-");return +p[2]+" "+M[+p[1]-1]+" "+p[0]}
function h(s){return String(s).replace(/[&<>"]/g,function(x){return{"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[x]})}
tags.forEach(function(k){var b=document.createElement("button");b.type="button";b.className="chip"+(k==cur?" on":"");b.setAttribute("aria-pressed",k==cur);
b.innerHTML=h(k)+(k=="All"?"":' <span>'+cnt[k]+"</span>");b.onclick=function(){cur=k;[].forEach.call(c.children,function(x){x.classList.toggle("on",x===b);x.setAttribute("aria-pressed",x===b)});sync();draw()};c.appendChild(b)});
function sync(){var u=new URLSearchParams(location.search);cur=="All"?u.delete("t"):u.set("t",cur);q.value?u.set("q",q.value):u.delete("q");var s=u.toString();history.replaceState(null,"",location.pathname+(s?"?"+s:"")+"#library")}
function draw(){var t=q.value.toLowerCase().trim();var f=R.filter(function(r){return(cur=="All"||r.tg.indexOf(cur)>=0)&&(r.title+" "+r.problem+" "+r.steps.join(" ")+" "+r.tg.join(" ")).toLowerCase().indexOf(t)>=0});
n.textContent=f.length+" recipe"+(f.length==1?"":"s")+(cur!="All"?" tagged "+cur:"")+(t?" matching \u201c"+q.value+"\u201d":"");
g.innerHTML=f.map(function(r){return'<a class="card" href="recipes/'+r.id+'.html"><div class="tag">'+h(r.category)+'</div><h3>'+h(r.title)+'</h3><p class="clamp">'+h(r.problem)+'</p><span class="cm">'+(r.v?'<span class="cm-ok"><svg width="1em" height="1em" class="ic" viewBox="0 0 24 24" aria-hidden="true"><path d="M5 12.5l4.2 4.2L19 7"/></svg>Verified '+fd(r.v)+"</span>":"")+"<span>"+r.steps.length+" steps</span><span>"+r.n+" source"+(r.n==1?"":"s")+"</span></span></a>"}).join("")}
if(q.addEventListener)q.oninput=function(){sync();draw()};draw();})();
