/* Tenant Recipes UI: copy buttons on code blocks, "Copy steps" and print buttons. No dependencies. */
document.addEventListener("DOMContentLoaded",function(){
function copy(t,b,lab){function ok(){b.classList.add("ok");var s=b.querySelector("span")||b;var o=s.textContent;s.textContent="Copied";setTimeout(function(){s.textContent=lab||o;b.classList.remove("ok")},1600)}
if(navigator.clipboard&&window.isSecureContext){navigator.clipboard.writeText(t).then(ok,function(){})}else{var a=document.createElement("textarea");a.value=t;document.body.appendChild(a);a.select();try{document.execCommand("copy");ok()}catch(e){}a.remove()}}
document.querySelectorAll("pre.cb").forEach(function(p){var b=document.createElement("button");b.type="button";b.className="cp";b.textContent="Copy";b.setAttribute("aria-label","Copy command to clipboard");
b.addEventListener("click",function(){copy(p.querySelector("code").innerText,b,"Copy")});p.appendChild(b)});
document.querySelectorAll("[data-copy]").forEach(function(b){var src=document.getElementById(b.dataset.copy);if(!src)return;var lab=(b.querySelector("span")||b).textContent;
b.addEventListener("click",function(){copy(src.textContent,b,lab)})});
document.querySelectorAll("[data-print]").forEach(function(b){b.addEventListener("click",function(){window.print()})});
});
