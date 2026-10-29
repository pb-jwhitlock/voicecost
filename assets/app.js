(function(){
  // ---- sortable tables
  document.querySelectorAll('table.sortable').forEach(function(t){
    t.querySelectorAll('th[data-sort]').forEach(function(th){
      th.addEventListener('click',function(){
        var idx=Array.prototype.indexOf.call(th.parentNode.children,th), num=th.dataset.sort==='num';
        var asc=!th.classList.contains('asc');
        th.parentNode.querySelectorAll('th').forEach(function(h){h.classList.remove('asc','desc')});
        th.classList.add(asc?'asc':'desc');
        var tb=t.tBodies[0], rows=Array.from(tb.rows);
        rows.sort(function(a,b){
          var x=a.cells[idx], y=b.cells[idx];
          var vx=x.dataset.v!==undefined?x.dataset.v:x.textContent.trim(), vy=y.dataset.v!==undefined?y.dataset.v:y.textContent.trim();
          if(num){vx=parseFloat(vx);vy=parseFloat(vy);return asc?vx-vy:vy-vx}
          return asc?vx.localeCompare(vy):vy.localeCompare(vx);
        });
        rows.forEach(function(r){tb.appendChild(r)});
      });
    });
  });
  // ---- "main products only" toggles
  document.querySelectorAll('.only-head').forEach(function(cb){
    var sec=cb.closest('section'), t=sec.querySelector('table');
    function ap(){t.classList.toggle('hide-head',cb.checked)}
    cb.addEventListener('change',ap); ap();
  });
  // ---- calculator
  var D=window.VC_CALC; if(!D) return;
  var P=window.VC_PRESET||{}, mode=P.mode||'diy';
  function $(id){return document.getElementById(id)}
  function money(x,d){return '$'+x.toLocaleString('en-US',{minimumFractionDigits:d,maximumFractionDigits:d})}
  function fill(sel,opts,extra,pick){
    var s=$(sel); s.innerHTML='';
    (extra||[]).forEach(function(o){s.add(new Option(o.label,o.id))});
    opts.forEach(function(o,i){var lab=o.label+' — '+(o.price<1?'$'+(+o.price.toFixed(4)):'$'+o.price.toFixed(2))+(o.high?'–$'+o.high:'');s.add(new Option(lab,o.id||('p'+i)))});
    if(pick) s.value=pick;
  }
  var llm=D.llm.map(function(o,i){return {id:'llm'+i,label:o.label,price:o.price}});
  var tel=D.tel.map(function(o,i){return {id:'tel'+i,label:o.label,price:o.price}});
  fill('c-stt',D.stt,null,P.stt);
  fill('c-tts',D.tts,null,P.tts);
  fill('c-plat',D.platform,[{id:'none',label:'None / self-hosted — $0'}],P.plat);
  fill('c-agent',D.agent,null,P.agent);
  fill('c-llm',llm,[{id:'custom',label:'Custom…'}],'llm0');
  fill('c-llm2',llm,[{id:'custom',label:'Custom…'}],'llm0');
  fill('c-tel',tel,[{id:'none',label:'None (web / app calls) — $0'}],'tel0');
  if(!P.plat && D.platform.length) $('c-plat').value=D.platform[0].id;
  function find(list,id){for(var i=0;i<list.length;i++) if(list[i].id===id) return list[i]; return null}
  function llmPrice(sel){var v=$(sel).value; if(v==='custom') return parseFloat($('c-llm-c').value)||0; var o=find(llm,v); return o?o.price:0}
  function setMode(m){mode=m;document.querySelectorAll('.calc .tab').forEach(function(b){b.classList.toggle('on',b.dataset.mode===m)});
    document.querySelector('.calc .diy').hidden=m!=='diy';document.querySelector('.calc .all').hidden=m!=='all';calc()}
  document.querySelectorAll('.calc .tab').forEach(function(b){b.addEventListener('click',function(){setMode(b.dataset.mode)})});
  function calc(){
    var min=parseFloat($('c-min').value)||0, calls=parseFloat($('c-calls').value)||0, parts=[], note='';
    var showCustom=(mode==='diy'&&$('c-llm').value==='custom')||(mode==='all'&&$('c-agent-llm').checked&&$('c-llm2').value==='custom');
    $('c-llm-cw').style.display=showCustom?'block':'none';
    if(mode==='diy'){
      var stt=find(D.stt,$('c-stt').value), tts=find(D.tts,$('c-tts').value), plat=find(D.platform,$('c-plat').value);
      var share=(parseFloat($('c-share').value)||0)/100, cpm=parseFloat($('c-cpm').value)||0;
      if(stt) parts.push(['Speech-to-text',stt.price]);
      parts.push(['LLM',llmPrice('c-llm')]);
      if(plat) parts.push(['Platform',plat.price]);
      if(tts) parts.push(['Text-to-speech',tts.price*cpm*share/1e6,(tts.vid==='elevenlabs'&&D.aff&&D.aff.elevenlabs)?D.aff.elevenlabs.url:'']);
      note='TTS cost = price per 1M chars × '+cpm+' chars/min × '+Math.round(share*100)+'% talk share.';
    } else {
      var ag=find(D.agent,$('c-agent').value);
      if(ag){parts.push(['Agent platform',ag.price]); if(ag.high) note='This platform lists a range ($'+ag.price+'–$'+ag.high+'/min); the low end is used.';
        if(ag.scope==='bundled') note+=(note?' ':'')+'Bundled rate: check whether the LLM is included.';}
      if($('c-agent-llm').checked) parts.push(['LLM',llmPrice('c-llm2')]);
    }
    var t=find(tel,$('c-tel').value); if(t) parts.push(['Telephony',t.price]);
    var perMin=parts.reduce(function(a,p){return a+p[1]},0), mx=Math.max.apply(null,parts.map(function(p){return p[1]}).concat([1e-9]));
    $('r-min').textContent=money(perMin,4); $('r-call').textContent=money(perMin*min,3); $('r-month').textContent=money(perMin*min*calls,0);
    $('r-bars').innerHTML=parts.map(function(p){var lab=p[0]; if(p[2]){var l=document.createElement('a');l.href=p[2];l.rel='sponsored noopener';l.target='_blank';l.setAttribute('data-aff','1');l.textContent=p[0];lab=l.outerHTML} return '<div class="bar">'+lab+' <b style="float:right">$'+p[1].toFixed(4)+'/min</b><i style="width:'+Math.max(2,p[1]/mx*100)+'%"></i></div>'}).join('');
    $('r-note').textContent=note+(note?' ':'')+'Prices from '+D.date+'.';
    var vids=[]; (mode==='diy'?[find(D.stt,$('c-stt').value),find(D.platform,$('c-plat').value),find(D.tts,$('c-tts').value)]:[find(D.agent,$('c-agent').value)]).forEach(function(o){if(o&&o.vid&&D.aff&&D.aff[o.vid]&&vids.indexOf(o.vid)<0)vids.push(o.vid)});
    var rt=$('r-try'); if(rt){rt.hidden=!vids.length; rt.innerHTML=vids.length?vids.map(function(v){var a=D.aff[v];var l=document.createElement('a');l.href=a.url;l.rel='sponsored noopener';l.target='_blank';l.className='visit';l.setAttribute('data-aff','1');l.textContent='Try '+a.name+' \u2197';return l.outerHTML}).join(' ')+' <span class="muted">Affiliate link'+(vids.length>1?'s':'')+' · <a href="'+rt.dataset.disc+'">disclosure</a></span>':'';}
  }
  document.querySelectorAll('.calc input,.calc select').forEach(function(el){el.addEventListener('input',calc);el.addEventListener('change',calc)});
  setMode(mode);
})();
function vcNewsletter(f){return true}
