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
