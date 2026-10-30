/* Tenant Recipes UI: copy buttons on code blocks. No dependencies. */
document.addEventListener("DOMContentLoaded",function(){document.querySelectorAll("pre.cb").forEach(function(p){
var b=document.createElement("button");b.type="button";b.className="cp";b.textContent="Copy";b.setAttribute("aria-label","Copy command to clipboard");
b.addEventListener("click",function(){var t=p.querySelector("code").innerText;function ok(){b.textContent="Copied";b.classList.add("ok");setTimeout(function(){b.textContent="Copy";b.classList.remove("ok")},1600)}
if(navigator.clipboard&&window.isSecureContext){navigator.clipboard.writeText(t).then(ok,function(){})}else{var a=document.createElement("textarea");a.value=t;document.body.appendChild(a);a.select();try{document.execCommand("copy");ok()}catch(e){}a.remove()}});
p.appendChild(b)})});
