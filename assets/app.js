const R=window.RECIPES,cats=["All",...new Set(R.map(r=>r.category))];let cur="All";
const g=document.getElementById("grid"),q=document.getElementById("q"),c=document.getElementById("chips"),n=document.getElementById("count");
cats.forEach(k=>{const b=document.createElement("button");b.className="chip"+(k=="All"?" on":"");b.textContent=k;b.onclick=()=>{cur=k;[...c.children].forEach(x=>x.classList.toggle("on",x===b));draw()};c.appendChild(b)});
function draw(){const t=q.value.toLowerCase();const f=R.filter(r=>(cur=="All"||r.category==cur)&&(r.title+r.problem+r.steps.join(" ")).toLowerCase().includes(t));
n.textContent=f.length+" recipes";g.innerHTML=f.map(r=>`<a class="card" href="recipes/${r.id}.html"><div class="tag">${r.category}</div><h3>${r.title}</h3><p>${r.problem}</p></a>`).join("")}
q.oninput=draw;draw();
