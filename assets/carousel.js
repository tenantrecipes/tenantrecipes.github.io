/* Featured carousel: CSS scroll-snap + small vanilla JS. Autoplay 6 s (off with prefers-reduced-motion), pauses on hover,
   focus, touch and hidden tab; dots, prev/next, arrow keys, pause button. No dependencies. */
(function(){var box=document.querySelector(".car-box");if(!box)return;
var vp=box.querySelector(".car-vp"),S=[].slice.call(vp.children),D=[].slice.call(box.querySelectorAll(".car-dot")),n=S.length,i=0,t=0,
play=box.querySelector(".car-play"),reduce=window.matchMedia&&matchMedia("(prefers-reduced-motion: reduce)").matches,
user=!reduce,hover=false,focus=false,touched=false;
function mark(k){i=k;D.forEach(function(d,j){d.toggleAttribute("aria-current",j===k)});S.forEach(function(s,j){s.toggleAttribute("aria-hidden",j!==k);
s.querySelectorAll("a.car-t-a,.car-t a").forEach(function(a){a.tabIndex=j===k?0:-1})})}
function go(k,smooth){k=(k+n)%n;vp.scrollTo({left:k*vp.clientWidth,behavior:smooth===false||reduce?"auto":"smooth"});mark(k)}
function running(){return user&&!hover&&!focus&&!touched&&!document.hidden}
function tick(){clearTimeout(t);if(running())t=setTimeout(function(){go(i+1);tick()},6000)}
function setPlay(on){user=on;if(play){play.setAttribute("aria-label",on?"Pause automatic slide show":"Start automatic slide show");play.classList.toggle("off",!on)}tick()}
box.querySelector(".car-prev").onclick=function(){go(i-1);tick()};
box.querySelector(".car-next").onclick=function(){go(i+1);tick()};
D.forEach(function(d,j){d.onclick=function(){go(j);tick()}});
if(play&&!reduce){play.hidden=false;play.onclick=function(){touched=false;setPlay(!user)}}
var st=0;vp.addEventListener("scroll",function(){clearTimeout(st);st=setTimeout(function(){var k=Math.round(vp.scrollLeft/vp.clientWidth);if(k!==i)mark(k)},80)},{passive:true});
box.addEventListener("mouseenter",function(){hover=true;tick()});box.addEventListener("mouseleave",function(){hover=false;tick()});
box.addEventListener("focusin",function(e){focus=true;var s=e.target.closest&&e.target.closest(".car-s");if(s){var k=S.indexOf(s);if(k>=0&&k!==i)go(k,false)}tick()});
box.addEventListener("focusout",function(e){if(!box.contains(e.relatedTarget)){focus=false;tick()}});
vp.addEventListener("touchstart",function(){touched=true;tick()},{passive:true});
box.addEventListener("keydown",function(e){if(e.key==="ArrowLeft"){e.preventDefault();go(i-1)}else if(e.key==="ArrowRight"){e.preventDefault();go(i+1)}});
document.addEventListener("visibilitychange",tick);window.addEventListener("resize",function(){go(i,false)});
mark(0);setPlay(user)})();
