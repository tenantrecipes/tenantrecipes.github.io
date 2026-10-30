(function(){var S=window.SEARCH||[],q=document.getElementById("ss-q"),r=document.getElementById("ss-r"),n=document.getElementById("ss-n"),ch=document.getElementById("ss-chips"),cur="All";
function h(s){return String(s).replace(/[&<>"]/g,function(c){return{"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]})}
["All","Recipe","Guide","Security","Page"].forEach(function(k){var b=document.createElement("button");b.type="button";b.className="chip"+(k=="All"?" on":"");b.textContent=k=="All"?"Everything":k+(k=="Page"?"s":k=="Security"?"":"s");b.onclick=function(){cur=k;[].forEach.call(ch.children,function(x){x.classList.toggle("on",x===b)});draw()};ch.appendChild(b)});
function draw(){var t=q.value.trim().toLowerCase(),w=t.split(/\s+/).filter(Boolean),out=[];
S.forEach(function(d){if(cur!="All"&&d.k!=cur)return;var ti=d.t.toLowerCase(),hay=(d.t+" "+d.c+" "+d.s+" "+d.x).toLowerCase(),sc=0;
for(var i=0;i<w.length;i++){if(hay.indexOf(w[i])<0)return;sc+=ti.indexOf(w[i])>=0?5:1;if((d.s||"").toLowerCase().indexOf(w[i])>=0)sc+=2}out.push([sc,d])});
if(w.length)out.sort(function(a,b){return b[0]-a[0]});
n.textContent=w.length?out.length+" result"+(out.length==1?"":"s")+" for \u201c"+q.value.trim()+"\u201d":out.length+" pages";
r.innerHTML=out.slice(0,80).map(function(x){var d=x[1];return '<li><a href="'+h(d.u)+'"><span class="ss-k">'+h(d.k)+' · '+h(d.c)+'</span><strong>'+h(d.t)+'</strong><span>'+h(d.s)+'</span></a></li>'}).join("")}
var p=new URLSearchParams(location.search).get("q");if(p)q.value=p;q.addEventListener("input",function(){draw();var u=new URL(location);if(q.value)u.searchParams.set("q",q.value);else u.searchParams.delete("q");history.replaceState(null,"",u)});draw()})();
