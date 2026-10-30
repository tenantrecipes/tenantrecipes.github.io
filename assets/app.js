const R=window.RECIPES,cats=["All",...new Set(R.map(r=>r.category))];let cur="All";
const g=document.getElementById("grid"),q=document.getElementById("q"),c=document.getElementById("chips"),n=document.getElementById("count");
cats.forEach(k=>{const b=document.createElement("button");b.className="chip"+(k=="All"?" on":"");b.textContent=k;b.onclick=()=>{cur=k;[...c.children].forEach(x=>x.classList.toggle("on",x===b));draw()};c.appendChild(b)});
function draw(){const t=q.value.toLowerCase();const f=R.filter(r=>(cur=="All"||r.category==cur)&&(r.title+r.problem+r.steps.join(" ")).toLowerCase().includes(t));
n.textContent=f.length+" recipe"+(f.length==1?"":"s");const M=["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"],fd=d=>{const p=d.split("-");return +p[2]+" "+M[+p[1]-1]+" "+p[0]};
g.innerHTML=f.map(r=>`<a class="card" href="recipes/${r.id}.html"><div class="tag">${r.category}</div><h3>${r.title}</h3><p class="clamp">${r.problem}</p><span class="cm">${r.v?`<span class="cm-ok"><svg class="ic" viewBox="0 0 24 24" aria-hidden="true"><path d="M5 12.5l4.2 4.2L19 7"/></svg>Verified ${fd(r.v)}</span>`:""}<span>${r.steps.length} steps</span><span>${r.n} source${r.n==1?"":"s"}</span></span></a>`).join("")}
q.oninput=draw;draw();
