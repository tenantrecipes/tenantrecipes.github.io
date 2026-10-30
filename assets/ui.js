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
/* Patch Tuesday countdown: second Tuesday of the month, 10:00 America/Los_Angeles (DST-aware via Intl). */
(function(){
function init(){var w=document.querySelectorAll("[data-pt]");if(!w.length||!window.Intl)return;
var fmt;try{fmt=new Intl.DateTimeFormat("en-US",{timeZone:"America/Los_Angeles",hourCycle:"h23",year:"numeric",month:"numeric",day:"numeric",hour:"numeric",minute:"numeric"})}catch(e){return}
function wall(t){var o={};fmt.formatToParts(new Date(t)).forEach(function(p){o[p.type]=+p.value});return Date.UTC(o.year,o.month-1,o.day,o.hour%24,o.minute)}
function la(y,m,d,h){var g=Date.UTC(y,m,d,h),t=g-(wall(g)-g);return g-(wall(t)-t)}
function release(y,m){var w0=new Date(Date.UTC(y,m,1)).getUTCDay();return la(y,m,1+((2-w0+7)%7)+7,10)}
var DAY=864e5;
function target(now){var p=wall(now),d=new Date(p),y=d.getUTCFullYear(),m=d.getUTCMonth(),t=release(y,m);
if(now>=t+DAY){m++;if(m>11){m=0;y++}t=release(y,m)}return t}
function pl(n,s){return n+" "+s+(n===1?"":"s")}
function tick(){var now=Date.now(),t=target(now),loc=new Date(t).toLocaleString(undefined,{weekday:"short",day:"numeric",month:"short",hour:"2-digit",minute:"2-digit"});
w.forEach(function(el){var tx=el.querySelector(".pt-t"),live=now>=t;el.classList.toggle("live",live);
if(live){var lt=el.getAttribute("data-latest");tx.innerHTML="<b>Patch Tuesday is live.</b> Microsoft's updates came out at 10:00 PT ("+loc+" your time)."+(lt?' <a href="'+lt+'">Read our summary →</a>':"")}
else{var s=Math.floor((t-now)/6e4),d=Math.floor(s/1440),h=Math.floor(s%1440/60),mi=s%60;
tx.innerHTML="Next release in <b>"+pl(d,"day")+", "+pl(h,"hour")+", "+pl(mi,"minute")+"</b> · <span class=\"pt-w\">"+loc+" your time (10:00 PT)</span>"}})}
tick();setInterval(tick,30000)}
if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",init);else init()})();
