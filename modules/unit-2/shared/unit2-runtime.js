(() => {
  'use strict';
  const L = window.LESSON;
  const state = {screen:0, activityScore:0, activityMax:L.activity.max || 1, activityDone:false, briefReady:false};
  const $ = (s, root=document) => root.querySelector(s);
  const $$ = (s, root=document) => [...root.querySelectorAll(s)];
  const esc = value => String(value || '').replace(/[&<>'"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[c]));
  const toast = message => { const t=$('#toast'); t.textContent=message; t.classList.add('show'); setTimeout(()=>t.classList.remove('show'),2300); };
  const label = ['Enter','Explore','Decide','Apply','Complete'];

  document.body.innerHTML = `
    <main class="shell">
      <header class="topbar">
        <div class="brand"><a class="brand-mark" href="../../../index.html" aria-label="Course home">U2</a><div><strong>VENTURE LAB</strong><span>Unit II · Creating Entrepreneurial Venture</span></div></div>
        <div class="stepper" aria-label="Topic progress">${label.map((x,i)=>`<i class="step-dot${i===0?' on':''}" title="${x}"></i>`).join('')}</div>
        <div class="lesson-count">Topic ${L.number} of 15</div>
      </header>
      <section class="screen active" id="screen-0">
        <div class="hero"><div class="hero-copy">
          <div class="kicker">${esc(L.kicker)}</div><h1>${esc(L.title)}</h1><p class="lede">${esc(L.subtitle)}</p>
          <div class="mission-chip"><span>◎</span><div><b>Your mission</b><br>${esc(L.mission)}</div></div>
        <div><button class="btn" data-go="1">Enter the topic <span>→</span></button></div>
        </div><div class="hero-art"><img src="${esc(L.image)}" alt="${esc(L.imageAlt)}"><div class="hero-label"><small>Real-world setting</small>${esc(L.context)}</div></div></div>
      </section>
      <section class="screen" id="screen-1"><div class="page">
        <div class="page-head"><div><div class="kicker">Explore · Build the foundation</div><h2>Know what you are doing</h2><p>${esc(L.learn.why)}</p></div><button class="btn secondary" data-go="0">← Back</button></div>
        <div class="instruction"><strong>What to do:</strong> Read the three steps, learn the key terms and study the worked example. Nothing is timed.</div>
        <div class="grid">${L.learn.steps.map((x,i)=>`<article class="card soft"><div class="num">${i+1}</div><h3>${esc(x.title)}</h3><p>${esc(x.text)}</p></article>`).join('')}</div>
        <div class="grid two" style="margin-top:18px">${L.learn.terms.map(x=>`<div class="term"><b>${esc(x.term)}</b><span>${esc(x.meaning)}</span></div>`).join('')}</div>
        <div class="example"><strong>Worked example</strong><p>${esc(L.learn.example)}</p></div>
        ${L.number===15?'<div class="official-source"><strong>Current official source</strong><p>Registration rules can change. Verify the live process before acting.</p><a href="https://udyamregistration.gov.in/" target="_blank" rel="noopener">Open the Government of India Udyam portal ↗</a></div>':''}
        <div class="actions"><button class="btn" data-go="2">I understand — start the activity →</button></div>
      </div></section>
      <section class="screen" id="screen-2"><div class="page">
        <div class="page-head"><div><div class="kicker">Decide · Interactive challenge</div><h2>${esc(L.activity.heading)}</h2><p>${esc(L.activity.intro)}</p></div><button class="btn secondary" data-go="1">← Review guide</button></div>
        <div class="instruction"><strong>Your task:</strong> ${esc(L.activity.instruction)}</div>
        <div class="activity-stage" id="activity"></div>
        <div class="actions between"><button class="btn ghost" id="reset-activity">Reset activity</button><button class="btn" id="to-apply" disabled>Continue to application →</button></div>
      </div></section>
      <section class="screen" id="screen-3"><div class="page">
        <div class="page-head"><div><div class="kicker">Apply · Make it yours</div><h2>${esc(L.apply.heading)}</h2><p>${esc(L.apply.intro)}</p></div><button class="btn secondary" data-go="2">← Revise activity</button></div>
        <div class="instruction"><strong>Your task:</strong> Complete the prompts in your own words. Your writing stays only in this browser.</div>
        <div class="card"><form class="apply-form" id="apply-form">${L.apply.fields.map((f,i)=>`<div class="field"><label for="field-${i}">${esc(f.label)}</label><small>${esc(f.help)}</small><textarea id="field-${i}" required minlength="${f.min || 8}" placeholder="${esc(f.placeholder)}"></textarea></div>`).join('')}<button class="btn warn" type="submit">Generate my ${esc(L.apply.outputName)} →</button></form>
        <div class="generated" id="generated"><h3>${esc(L.apply.outputName)}</h3><p>${esc(L.apply.outputIntro)}</p><dl id="generated-content"></dl><div class="actions between"><button class="btn secondary" id="edit-brief" type="button">← Edit my response</button><button class="btn" id="complete-lesson" type="button">Complete topic →</button></div></div></div>
      </div></section>
      <section class="screen" id="screen-4"><div class="page complete-wrap">
        <div class="badge">✓</div><div class="kicker">Mission completed</div><h2>${esc(L.complete.title)}</h2>
        <div class="final-score" id="final-score">0%</div><p class="lede" style="margin-left:auto;margin-right:auto">${esc(L.complete.message)}</p>
        <div class="takeaways">${L.complete.takeaways.map(x=>`<div class="takeaway">${esc(x)}</div>`).join('')}</div>
        <div class="example"><strong>Transfer question</strong><p>${esc(L.complete.transfer)}</p></div>
        <div class="actions" style="justify-content:center"><button class="btn secondary" data-go="3">← Review my work</button><button class="btn" id="restart">Restart topic</button></div>
      </div></section>
    </main><div class="toast" id="toast" role="status" aria-live="polite"></div>`;

  function go(n){ state.screen=n; $$('.screen').forEach((s,i)=>s.classList.toggle('active',i===n)); $$('.step-dot').forEach((d,i)=>d.classList.toggle('on',i<=n)); window.scrollTo(0,0); }
  $$('[data-go]').forEach(b=>b.addEventListener('click',()=>go(+b.dataset.go)));
  $('#to-apply').addEventListener('click',()=>go(3));
  $('#restart').addEventListener('click',()=>location.reload());
  $('#reset-activity').addEventListener('click',()=>{state.activityDone=false;state.activityScore=0;$('#to-apply').disabled=true;renderActivity();toast('Activity reset. Try it again.');});
  $('#apply-form').addEventListener('submit', e=>{
    e.preventDefault();
    const values=L.apply.fields.map((f,i)=>({label:f.label,value:$(`#field-${i}`).value.trim()}));
    if(values.some(v=>v.value.length<8)){toast('Please add a little more detail to each answer.');return;}
    $('#generated-content').innerHTML=values.map(v=>`<dt>${esc(v.label)}</dt><dd>${esc(v.value)}</dd>`).join('');
    $('#apply-form').style.display='none';$('#generated').classList.add('show');state.briefReady=true;
    toast('Generated. Review it before you complete the topic.');
  });
  $('#edit-brief').addEventListener('click',()=>{$('#generated').classList.remove('show');$('#apply-form').style.display='grid';$('#field-0').focus();});
  $('#complete-lesson').addEventListener('click',()=>{const percent=Math.round((state.activityScore/state.activityMax)*100);$('#final-score').textContent=`${percent}%`;go(4);});
  function done(score=state.activityMax){state.activityScore=Math.max(0,Math.min(score,state.activityMax));state.activityDone=true;$('#to-apply').disabled=false;toast('Challenge complete. You can continue or reset and try again.');}

  function renderActivity(){
    const modes={explore:renderExplore,funnel:renderFunnel,branch:renderBranch,sequence:renderSequence,detective:renderDetective,simulator:renderSimulator,matrix:renderMatrix,compare:renderCompare};
    modes[L.activity.mode]();
  }

  function renderExplore(){
    let seen=new Set(), active=0, notes={}; const items=L.activity.items;
    $('#activity').innerHTML=`<div class="tool-row" id="tools"></div><div class="dashboard"><div class="card soft" id="concept"></div><div class="card soft"><h3>Your concept notes</h3><p>Write one change this tool could create. Short notes are enough.</p><textarea id="concept-note" style="width:100%;min-height:160px;border:1px solid #395673;border-radius:14px;background:#08192b;color:white;padding:14px"></textarea><button class="btn" id="save-note" style="margin-top:12px">Save this change</button><p id="seen-count" aria-live="polite"></p></div></div>`;
    const draw=()=>{ $('#tools').innerHTML=items.map((x,i)=>`<button class="tool${i===active?' active':''}" data-i="${i}">${esc(x.name)}</button>`).join(''); const x=items[active]; $('#concept').innerHTML=`<div class="num">${active+1}</div><h3>${esc(x.name)}</h3><p>${esc(x.meaning)}</p><div class="example"><strong>Try asking</strong><p>${esc(x.question)}</p><strong>Example</strong><p>${esc(x.example)}</p></div>`;$('#concept-note').value=notes[active]||'';$('#seen-count').textContent=`${seen.size} of ${items.length} tools applied`;
      $$('#tools .tool').forEach(b=>b.onclick=()=>{active=+b.dataset.i;draw();});
    };
    draw();
    $('#save-note').onclick=()=>{const v=$('#concept-note').value.trim();if(v.length<5){toast('Add one clear change before saving.');return;}notes[active]=v;seen.add(active);draw();if(seen.size===items.length)done(items.length);else toast('Saved. Choose another transformation tool.');};
  }

  function renderFunnel(){
    const ideas=L.activity.ideas; let selected=-1;
    $('#activity').innerHTML=`<div class="grid two">${ideas.map((x,i)=>`<article class="card soft"><div class="kicker">Idea ${i+1}</div><h3>${esc(x.name)}</h3><p>${esc(x.desc)}</p>${['Desirability','Feasibility','Viability'].map((k,j)=>`<div class="slider-row"><label>${k}</label><input type="range" min="1" max="5" value="3" data-idea="${i}" data-dim="${j}" aria-label="${k} score for ${esc(x.name)}"><output>3</output></div>`).join('')}<button class="btn secondary choose" data-i="${i}">Send through funnel</button></article>`).join('')}</div><div class="feedback" id="funnel-feedback"></div>`;
    $$('input[type=range]').forEach(r=>r.oninput=()=>r.nextElementSibling.value=r.value);
    $$('.choose').forEach(b=>b.onclick=()=>{selected=+b.dataset.i;$$('.choose').forEach(x=>x.classList.remove('active'));b.classList.add('active');const scores=$$(`input[data-idea="${selected}"]`).map(x=>+x.value);const total=scores.reduce((a,v)=>a+v,0);const f=$('#funnel-feedback');f.className='feedback show '+(selected===L.activity.best?'good':'bad');f.innerHTML=`<strong>${selected===L.activity.best?'Evidence-led choice':'Pause and compare the evidence'}</strong><p>${esc(selected===L.activity.best?L.activity.success:L.activity.retry)}</p><p>Your score: <b>${total}/15</b>. A high total is useful only when each rating is supported by evidence.</p><button class="btn" id="lock-funnel">Lock this decision</button>`;$('#lock-funnel').onclick=()=>done(selected===L.activity.best?L.activity.max:Math.max(1,L.activity.max-1));});
  }

  function renderBranch(){
    let step=0, score=0, meters={evidence:35,rapport:45,bias:45};
    $('#activity').innerHTML=`<div class="meter-grid">${Object.keys(meters).map(k=>`<div class="meter-box"><label><span>${k[0].toUpperCase()+k.slice(1)}</span><span id="m-${k}-v">${meters[k]}</span></label><div class="meter"><i id="m-${k}" style="width:${meters[k]}%"></i></div></div>`).join('')}</div><div class="chat" id="chat"></div><div class="choice-list" id="branch-choices"></div><div class="feedback" id="branch-feedback"></div>`;
    const update=()=>Object.keys(meters).forEach(k=>{$(`#m-${k}`).style.width=`${meters[k]}%`;$(`#m-${k}-v`).textContent=meters[k]});
    const next=()=>{const q=L.activity.scenes[step];$('#chat').innerHTML=`<div class="bubble them"><div class="speaker">${esc(q.speaker||'Founder')}</div>${esc(q.line)}</div>`;$('#branch-choices').innerHTML=q.choices.map((c,i)=>`<button class="choice" data-i="${i}">${esc(c.text)}</button>`).join('');$('#branch-feedback').className='feedback';$$('#branch-choices .choice').forEach(b=>b.onclick=()=>{const c=q.choices[+b.dataset.i];$$('#branch-choices .choice').forEach(x=>x.disabled=true);b.classList.add(c.good?'correct':'wrong');Object.keys(c.delta||{}).forEach(k=>meters[k]=Math.max(0,Math.min(100,meters[k]+c.delta[k])));update();if(c.good)score++;const f=$('#branch-feedback');f.className=`feedback show ${c.good?'good':'bad'}`;f.innerHTML=`<strong>${c.good?'Useful move':'A weaker move'}</strong><p>${esc(c.feedback)}</p><button class="btn" id="branch-next">${step===L.activity.scenes.length-1?'Finish conversation':'Continue conversation →'}</button>`;$('#branch-next').onclick=()=>{step++;if(step>=L.activity.scenes.length){done(score);f.innerHTML=`<strong>Conversation complete</strong><p>You made ${score} evidence-led decisions out of ${L.activity.scenes.length}. Review the meter pattern, then continue.</p>`;$('#branch-choices').innerHTML='';}else next();};});};next();
  }

  function renderSequence(){
    let arr=[...L.activity.items].sort((a,b)=>a.start-b.start);
    const draw=()=>{$('#activity').innerHTML=`<div class="sequence">${arr.map((x,i)=>`<div class="seq-item"><div class="grip">${i+1}</div><div><h3>${esc(x.name)}</h3><p>${esc(x.clue)}</p></div><div class="seq-controls"><button data-i="${i}" data-d="-1" aria-label="Move ${esc(x.name)} up">↑</button><button data-i="${i}" data-d="1" aria-label="Move ${esc(x.name)} down">↓</button></div></div>`).join('')}</div><div class="actions"><button class="btn warn" id="check-order">Check my roadmap</button></div><div class="feedback" id="sequence-feedback"></div>`;$$('.seq-controls button').forEach(b=>b.onclick=()=>{const i=+b.dataset.i,j=i+(+b.dataset.d);if(j<0||j>=arr.length)return;[arr[i],arr[j]]=[arr[j],arr[i]];draw();});$('#check-order').onclick=()=>{const correct=arr.filter((x,i)=>x.order===i+1).length;const f=$('#sequence-feedback');f.className=`feedback show ${correct===arr.length?'good':'bad'}`;f.innerHTML=`<strong>${correct===arr.length?'Roadmap approved':'Roadmap needs revision'}</strong><p>${correct} of ${arr.length} stages are in the correct position. ${esc(correct===arr.length?L.activity.success:L.activity.retry)}</p>`;if(correct===arr.length)done(correct);};};draw();
  }

  function renderDetective(){
    let answered=0, score=0; const cats=L.activity.categories;
    $('#activity').innerHTML=`<div class="evidence-board">${L.activity.evidence.map((x,i)=>`<article class="evidence" data-i="${i}"><div class="kicker">Evidence ${i+1}</div><h3>${esc(x.text)}</h3><div class="tag-row">${cats.map(c=>`<button class="tag" data-cat="${esc(c)}">${esc(c)}</button>`).join('')}</div><div class="feedback"></div></article>`).join('')}</div>`;
    $$('.evidence').forEach(card=>{$$('.tag',card).forEach(b=>b.onclick=()=>{if(card.dataset.done)return;card.dataset.done='1';answered++;const x=L.activity.evidence[+card.dataset.i],good=b.dataset.cat===x.answer;if(good)score++;b.classList.add('selected');$$('.tag',card).forEach(t=>t.disabled=true);const f=$('.feedback',card);f.className=`feedback show ${good?'good':'bad'}`;f.innerHTML=`<strong>${good?'Correct classification':`Best fit: ${esc(x.answer)}`}</strong><p>${esc(x.feedback)}</p>`;if(answered===L.activity.evidence.length)done(score);});});
  }

  function renderSimulator(){
    const vals={};L.activity.controls.forEach(c=>vals[c.key]=c.value);
    $('#activity').innerHTML=`<div class="dashboard"><div class="card soft"><h3>${esc(L.activity.consoleTitle)}</h3><p>${esc(L.activity.consoleHelp)}</p>${L.activity.controls.map(c=>`<div class="slider-row"><label for="s-${c.key}">${esc(c.label)}</label><input id="s-${c.key}" type="range" min="${c.min}" max="${c.max}" value="${c.value}" data-key="${c.key}"><output>${c.value}</output></div>`).join('')}<button class="btn warn" id="test-sim">Test this decision</button></div><div class="card soft"><div class="score-orb" id="orb"><span><b id="sim-score">0</b><small>fit score</small></span></div><div class="feedback show" id="sim-feedback"><strong>Adjust the controls</strong><p>${esc(L.activity.startFeedback)}</p></div></div></div>`;
    const calc=()=>{let score=100;L.activity.controls.forEach(c=>score-=Math.abs(vals[c.key]-c.target)*c.weight);return Math.max(0,Math.round(score));};
    $$('input[type=range]').forEach(r=>r.oninput=()=>{vals[r.dataset.key]=+r.value;r.nextElementSibling.value=r.value;const s=calc();$('#sim-score').textContent=s;$('#orb').style.setProperty('--fill',`${s}%`);});
    $('#test-sim').onclick=()=>{const s=calc(),ok=s>=L.activity.pass;const f=$('#sim-feedback');f.className=`feedback show ${ok?'good':'bad'}`;f.innerHTML=`<strong>${ok?'Decision is balanced':'Trade-off needs attention'}</strong><p>${esc(ok?L.activity.success:L.activity.retry)} Current fit: ${s}%.</p>`;if(ok)done(Math.round((s/100)*L.activity.max));};$$('input[type=range]')[0].dispatchEvent(new Event('input'));
  }

  function renderMatrix(){
    let score=0,step=0;const rows=L.activity.rows,forms=L.activity.forms;
    $('#activity').innerHTML=`<div class="matrix"><table><thead><tr><th>Decision factor</th>${forms.map(x=>`<th>${esc(x)}</th>`).join('')}</tr></thead><tbody>${rows.map(r=>`<tr><td>${esc(r.factor)}</td>${r.values.map(v=>`<td>${esc(v)}</td>`).join('')}</tr>`).join('')}</tbody></table></div><div class="card soft" style="margin-top:20px" id="matrix-case"></div>`;
    const draw=()=>{const q=L.activity.cases[step];$('#matrix-case').innerHTML=`<div class="kicker">Founder case ${step+1} of ${L.activity.cases.length}</div><h3>${esc(q.case)}</h3><p>${esc(q.need)}</p><div class="choice-list">${forms.map((f,i)=>`<button class="choice" data-i="${i}">${esc(f)}</button>`).join('')}</div><div class="feedback" id="matrix-feedback"></div>`;$$('.choice',$('#matrix-case')).forEach(b=>b.onclick=()=>{const i=+b.dataset.i,ok=i===q.answer;if(ok)score++;$$('.choice',$('#matrix-case')).forEach(x=>x.disabled=true);b.classList.add(ok?'correct':'wrong');const f=$('#matrix-feedback');f.className=`feedback show ${ok?'good':'bad'}`;f.innerHTML=`<strong>${ok?'Suitable choice':`Better choice: ${esc(forms[q.answer])}`}</strong><p>${esc(q.feedback)}</p><button class="btn" id="matrix-next">${step===L.activity.cases.length-1?'Finish cases':'Next case →'}</button>`;$('#matrix-next').onclick=()=>{step++;if(step===L.activity.cases.length)done(score);else draw();};});};draw();
  }

  function renderCompare(){
    let step=0,score=0;const a=L.activity.options[0],b=L.activity.options[1];
    $('#activity').innerHTML=`<div class="compare-panels"><article class="compare-panel"><h3>${esc(a.name)}</h3><p>${esc(a.summary)}</p><ul>${a.points.map(x=>`<li>${esc(x)}</li>`).join('')}</ul></article><div class="versus">VS</div><article class="compare-panel"><h3>${esc(b.name)}</h3><p>${esc(b.summary)}</p><ul>${b.points.map(x=>`<li>${esc(x)}</li>`).join('')}</ul></article></div><div class="card soft" style="margin-top:20px" id="compare-case"></div>`;
    const draw=()=>{const q=L.activity.cases[step];$('#compare-case').innerHTML=`<div class="kicker">Decision ${step+1}</div><h3>${esc(q.case)}</h3><p>${esc(q.need)}</p><div class="choice-list"><button class="choice" data-i="0">${esc(a.name)}</button><button class="choice" data-i="1">${esc(b.name)}</button></div><div class="feedback" id="compare-feedback"></div>`;$$('.choice',$('#compare-case')).forEach(x=>x.onclick=()=>{const ok=+x.dataset.i===q.answer;if(ok)score++;$$('.choice',$('#compare-case')).forEach(z=>z.disabled=true);x.classList.add(ok?'correct':'wrong');const f=$('#compare-feedback');f.className=`feedback show ${ok?'good':'bad'}`;f.innerHTML=`<strong>${ok?'Reasoned choice':'Reconsider the priority'}</strong><p>${esc(q.feedback)}</p><button class="btn" id="compare-next">${step===L.activity.cases.length-1?'Finish comparison':'Next decision →'}</button>`;$('#compare-next').onclick=()=>{step++;if(step===L.activity.cases.length)done(score);else draw();};});};draw();
  }
  renderActivity();
})();
