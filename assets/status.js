/* Status: local-time rendering and periodic refresh of /status/status.json (homepage pill + /status/ page). */
(function(){
function loc(){document.querySelectorAll("time[data-local]").forEach(function(t){var d=new Date(t.getAttribute("datetime"));if(!isNaN(d))t.textContent=d.toLocaleString(undefined,{dateStyle:"medium",timeStyle:"short"})})}
var TXT={ok:"Microsoft cloud: no reported issues",issue:"Microsoft cloud: active issues",unknown:"Microsoft cloud status"};
var OV={ok:"All monitored Microsoft cloud sources report no issues",issue:"Microsoft reports active issues",unknown:"Status sources could not be reached"};
function apply(d){var p=document.querySelector("[data-st-pill]");if(p){p.className="st-pill st-"+d.overall;p.querySelector(".st-pt").textContent=TXT[d.overall]||TXT.unknown}
var o=document.getElementById("st-over");if(o){o.className="st-over st-"+d.overall;document.getElementById("st-ot").textContent=OV[d.overall]||OV.unknown;
var t=o.querySelector("time");if(t){t.setAttribute("datetime",d.generated)}document.getElementById("st-ref").textContent="refreshed "+new Date().toLocaleTimeString(undefined,{timeStyle:"short"})}
d.sources.forEach(function(s){var c=document.querySelector('.st-card[data-k="'+s.key+'"]');if(!c)return;var lv=s.reachable?s.level:"unknown";c.className="st-card st-"+lv;
var lab={ok:"Operational",issue:"Issues reported",notice:"Advisory",unknown:"Not reachable"};c.querySelector(".st-lab").textContent=lab[lv];c.querySelector(".st-s").textContent=s.reachable?(s.status||""):"Could not be reached from our checker"});
var a=document.getElementById("st-act");if(a&&d.active){if(!d.active.length)a.innerHTML="<p>No active incidents in the public sources right now.</p>";else{a.innerHTML='<ol class="st-inc"></ol>';var ol=a.firstChild;d.active.forEach(function(i){var li=document.createElement("li");
var s=document.createElement("strong"),l=document.createElement("a");l.href=i.link;l.rel="noopener";l.textContent=i.title;s.appendChild(l);li.appendChild(s);var sp=document.createElement("span");sp.textContent=i.source_name+" · started "+(i.start?new Date(i.start).toLocaleString(undefined,{dateStyle:"medium",timeStyle:"short"}):"—")+(i.services?" · "+i.services.join(", "):"");li.appendChild(sp);
var pp=document.createElement("p");pp.textContent=i.summary||"";li.appendChild(pp);ol.appendChild(li)})}}loc()}
function refresh(){var el=document.querySelector("[data-st-json]");if(!el)return;fetch(el.getAttribute("data-st-json")+"?t="+Date.now(),{cache:"no-store"}).then(function(r){return r.ok?r.json():null}).then(function(d){if(d)apply(d)}).catch(function(){})}
loc();refresh();setInterval(function(){if(!document.hidden)refresh()},120000);
})();
