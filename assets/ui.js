/* Tenant Recipes UI: copy buttons on code blocks, "Copy steps" and print buttons. No dependencies. */
document.addEventListener("DOMContentLoaded",function(){
function copy(t,b,lab){function ok(){b.classList.add("ok");var s=b.querySelector("span")||b;var o=s.textContent;s.textContent="Copied";setTimeout(function(){s.textContent=lab||o;b.classList.remove("ok")},1600)}
if(navigator.clipboard&&window.isSecureContext){navigator.clipboard.writeText(t).then(ok,function(){})}else{var a=document.createElement("textarea");a.value=t;document.body.appendChild(a);a.select();try{document.execCommand("copy");ok()}catch(e){}a.remove()}}
document.querySelectorAll("pre.cb").forEach(function(p){var b=document.createElement("button");b.type="button";b.className="cp";b.textContent="Copy";b.setAttribute("aria-label","Copy command to clipboard");
b.addEventListener("click",function(){copy(p.querySelector("code").innerText,b,"Copy")});p.appendChild(b)});
document.querySelectorAll("[data-copy]").forEach(function(b){var src=document.getElementById(b.dataset.copy);if(!src)return;var lab=(b.querySelector("span")||b).textContent;
b.addEventListener("click",function(){copy(src.textContent,b,lab)})});
document.querySelectorAll("[data-share-copy]").forEach(function(b){b.addEventListener("click",function(){copy(b.dataset.shareCopy,b)})});
/* X on iOS/Android: open the X app's compose screen via twitter://post; if the page is still visible after 1.5 s (app missing), fall back to the web intent. Desktop keeps the plain link. */
if(/iPhone|iPad|iPod|Android/i.test(navigator.userAgent)||(navigator.platform==="MacIntel"&&navigator.maxTouchPoints>1)){document.querySelectorAll("[data-x-app]").forEach(function(a){a.addEventListener("click",function(ev){ev.preventDefault();
var t=0,stop=function(){clearTimeout(t);document.removeEventListener("visibilitychange",vis);window.removeEventListener("pagehide",stop)},vis=function(){if(document.hidden)stop()};
document.addEventListener("visibilitychange",vis);window.addEventListener("pagehide",stop);
t=setTimeout(function(){stop();if(!document.hidden)location.href=a.href},1500);
location.href="twitter://post?message="+encodeURIComponent(a.dataset.title+" "+a.dataset.url)})})}
if(navigator.share){document.querySelectorAll("[data-share-native]").forEach(function(b){b.hidden=false;b.addEventListener("click",function(){navigator.share({title:b.dataset.title,url:b.dataset.url}).catch(function(){})})})}
document.querySelectorAll("[data-print]").forEach(function(b){b.addEventListener("click",function(){window.print()})});
});
/* Patch Tuesday countdown: second Tuesday of the month, 10:00 America/Los_Angeles (DST-aware via Intl).
   Rendered as a split-flap clock (DD:HH:MM:SS); the flip animation is skipped with prefers-reduced-motion. */
(function(){
function init(){var w=document.querySelectorAll("[data-pt]");if(!w.length||!window.Intl)return;
var fmt;try{fmt=new Intl.DateTimeFormat("en-US",{timeZone:"America/Los_Angeles",hourCycle:"h23",year:"numeric",month:"numeric",day:"numeric",hour:"numeric",minute:"numeric"})}catch(e){return}
function wall(t){var o={};fmt.formatToParts(new Date(t)).forEach(function(p){o[p.type]=+p.value});return Date.UTC(o.year,o.month-1,o.day,o.hour%24,o.minute)}
function la(y,m,d,h){var g=Date.UTC(y,m,d,h),t=g-(wall(g)-g);return g-(wall(t)-t)}
function release(y,m){var w0=new Date(Date.UTC(y,m,1)).getUTCDay();return la(y,m,1+((2-w0+7)%7)+7,10)}
var DAY=864e5,rm=window.matchMedia&&matchMedia("(prefers-reduced-motion: reduce)");
function target(now){var p=wall(now),d=new Date(p),y=d.getUTCFullYear(),m=d.getUTCMonth(),t=release(y,m);
if(now>=t+DAY){m++;if(m>11){m=0;y++}t=release(y,m)}return t}
function pl(n,s){return n+" "+s+(n===1?"":"s")}
function p2(n){return(n<10?"0":"")+n}
var U=[["d","Days"],["h","Hours"],["m","Min"],["s","Sec"]];
w.forEach(function(el){var c=el.querySelector(".pt-clock");if(!c)return;var h="";
U.forEach(function(u,i){h+=(i?'<span class="pt-sep" aria-hidden="true">:</span>':"")+'<span class="pt-u" aria-hidden="true"><span class="fl" data-u="'+u[0]+'">'
+'<span class="fl-t"><b>00</b></span><span class="fl-b"><b>00</b></span><span class="fl-ft"><b>00</b></span><span class="fl-fb"><b>00</b></span></span><i>'+u[1].toUpperCase()+'</i></span>'});
c.innerHTML=h;el._fl={};c.querySelectorAll(".fl").forEach(function(f){el._fl[f.getAttribute("data-u")]={el:f,v:null,t:0}})});
function set(f,v){if(f.v===v)return;var o=f.v===null?v:f.v,e=f.el,q=function(s){return e.querySelector(s+" b")};f.v=v;clearTimeout(f.t);
if(o===v||(rm&&rm.matches)||document.hidden){e.classList.remove("go");q(".fl-t").textContent=q(".fl-b").textContent=v;return}
e.classList.remove("go");void e.offsetWidth;q(".fl-t").textContent=v;q(".fl-b").textContent=o;q(".fl-ft").textContent=o;q(".fl-fb").textContent=v;e.classList.add("go");
f.t=setTimeout(function(){q(".fl-b").textContent=v;e.classList.remove("go")},600)}
function tick(){var now=Date.now(),t=target(now),loc=new Date(t).toLocaleString(undefined,{weekday:"short",day:"numeric",month:"short",hour:"2-digit",minute:"2-digit"});
w.forEach(function(el){var tx=el.querySelector(".pt-t"),c=el.querySelector(".pt-clock"),live=now>=t;el.classList.toggle("live",live);
if(live){if(c)c.hidden=true;if(!el._lv){var lt=el.getAttribute("data-latest");el._lv=1;
tx.innerHTML="<b>Patch Tuesday is live.</b> Microsoft's updates came out at 10:00 PT (<span class=\"pt-w\">"+loc+" your time</span>)."+(lt?' <a href="'+lt+'">Read our summary →</a>':"")}return}
el._lv=0;var r=Math.max(0,Math.floor((t-now)/1e3)),d=Math.floor(r/86400),h=Math.floor(r%86400/3600),m=Math.floor(r%3600/60),s=r%60;
var txt='Next release <span class="pt-w">'+loc+" your time</span> <span class=\"pt-w\">(10:00 PT)</span>";if(tx.innerHTML!==txt)tx.innerHTML=txt;
if(c&&el._fl){c.hidden=false;var lab="Next Patch Tuesday in "+pl(d,"day")+", "+pl(h,"hour")+", "+pl(m,"minute");if(c.getAttribute("aria-label")!==lab)c.setAttribute("aria-label",lab);
set(el._fl.d,p2(Math.min(d,99)));set(el._fl.h,p2(h));set(el._fl.m,p2(m));set(el._fl.s,p2(s))}})}
tick();setInterval(tick,1000)}
if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",init);else init()})();

/* Mobile menu: close on Escape, outside tap or link tap */
(function(){var m=document.querySelector("details.nv-m");if(!m)return;var sm=m.querySelector("summary");
sm.setAttribute("aria-haspopup","true");sm.setAttribute("aria-expanded","false");
m.addEventListener("toggle",function(){sm.setAttribute("aria-expanded",m.open?"true":"false")});
document.addEventListener("keydown",function(e){if(e.key==="Escape"&&m.open){m.open=false;sm.focus()}});
document.addEventListener("click",function(e){if(m.open&&!m.contains(e.target))m.open=false});
m.addEventListener("click",function(e){if(e.target.closest(".nv-md a"))m.open=false});})();
