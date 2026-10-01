(function(){
  var FUB='https://dawn-sun-5ae8.broker-e2c.workers.dev';
  var reduce=window.matchMedia&&matchMedia('(prefers-reduced-motion: reduce)').matches;

  // mobile menu + dropdowns
  var burger=document.querySelector('.burger'), nav=document.getElementById('nav');
  if(burger){burger.addEventListener('click',function(){var o=nav.classList.toggle('open');document.body.classList.toggle('menu-open',o);burger.setAttribute('aria-expanded',o);});}
  [].forEach.call(document.querySelectorAll('.dd>button'),function(b){
    b.addEventListener('click',function(){var d=b.parentNode,o=!d.classList.contains('open');[].forEach.call(document.querySelectorAll('.dd.open'),function(x){x.classList.remove('open');x.firstElementChild.setAttribute('aria-expanded','false');});d.classList.toggle('open',o);b.setAttribute('aria-expanded',o);});
  });
  document.addEventListener('click',function(e){if(!e.target.closest('.dd'))[].forEach.call(document.querySelectorAll('.dd.open'),function(x){x.classList.remove('open');x.firstElementChild.setAttribute('aria-expanded','false');});});

  // reveal
  if('IntersectionObserver' in window&&!reduce){
    var els=[].slice.call(document.querySelectorAll('.rv'));
    document.documentElement.classList.add('armed');
    var io=new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting){e.target.classList.add('in');io.unobserve(e.target);}});},{rootMargin:'0px 0px -6% 0px'});
    els.forEach(function(el){io.observe(el);});
    setTimeout(function(){els.forEach(function(el){el.classList.add('in');});},6000);
  }


  // centred confirmation after a form is sent
  function sentPopup(text){
    var d=document.getElementById('sentDlg');
    if(!d){
      var st=document.createElement('style');
      st.textContent='#sentDlg{border:0;border-radius:8px;padding:0;max-width:min(440px,calc(100vw - 32px));box-shadow:0 30px 60px rgba(10,14,40,.35);font-family:Barlow,system-ui,sans-serif;color:#141833;background:#fff}#sentDlg::backdrop{background:rgba(20,24,51,.6)}#sentDlg .in{padding:34px 30px 26px;display:flex;flex-direction:column;align-items:center;gap:12px;text-align:center}#sentDlg .ck{width:64px;height:64px;border-radius:50%;background:#1D2870;display:grid;place-items:center}#sentDlg .ck svg{width:30px;height:30px}#sentDlg h2{margin:6px 0 0;font-family:"Barlow Condensed",sans-serif;font-weight:800;font-size:40px;line-height:1;text-transform:uppercase}#sentDlg p{margin:0;color:#545B78;font-size:17px;line-height:1.5}#sentDlg button{margin-top:10px;min-height:48px;padding:0 28px;border:0;border-radius:4px;background:#D7141E;color:#fff;font:600 17px Barlow,system-ui,sans-serif;cursor:pointer}';
      document.head.appendChild(st);
      d=document.createElement('dialog'); d.id='sentDlg'; d.setAttribute('aria-labelledby','sentH');
      d.innerHTML='<div class="in"><div class="ck" aria-hidden="true"><svg viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12.5l4.5 4.5L19 7.5"/></svg></div><h2 id="sentH">Message sent</h2><p id="sentP"></p><button type="button">Close</button></div>';
      document.body.appendChild(d);
      d.querySelector('button').addEventListener('click',function(){d.close();});
      d.addEventListener('click',function(e){if(e.target===d)d.close();});
    }
    document.getElementById('sentP').textContent=text.replace(/^Sent\.\s*/,'');
    if(d.showModal){d.showModal();}else{d.setAttribute('open','');}
  }

  // lead forms -> Follow Up Boss (same Worker as the landing page)
  [].forEach.call(document.querySelectorAll('form[data-lead]'),function(f){
    f.addEventListener('submit',function(e){
      e.preventDefault();
      var msg=f.querySelector('.msg'), btn=f.querySelector('button[type=submit]');
      function v(n){var el=f.elements[n];return el?String(el.value).trim():'';}
      var name=v('name'), parts=name.split(/\s+/);
      if(!name||(!v('email')&&!v('phone'))){msg.className='msg err';msg.textContent='Add your name and an email or phone number so Michael can reply.';return;}
      var extra=[].slice.call(f.elements).filter(function(el){return el.name&&['name','email','phone'].indexOf(el.name)<0&&el.value;}).map(function(el){return (el.dataset.label||el.name)+': '+el.value;}).join('. ');
      btn.disabled=true; var t=btn.textContent; btn.textContent='Sending…';
      fetch(FUB,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({
        firstName:parts[0], lastName:parts.slice(1).join(' '), email:v('email'), phone:v('phone'),
        message:'['+f.dataset.lead+'] '+extra+' (page: '+location.pathname+')',
        property:'soldmike.com, '+f.dataset.lead
      })}).then(function(r){return r.json();}).then(function(r){
        if(!r.success) throw 0;
        var done=f.dataset.done||'Sent. Michael will be in touch shortly.'; f.reset(); msg.className='msg'; msg.textContent=done; btn.textContent=t; btn.disabled=false; sentPopup(done);
      }).catch(function(){
        msg.className='msg err'; msg.textContent='That did not go through. Call or text Michael at 647-694-3109.'; btn.textContent=t; btn.disabled=false;
      });
    });
  });

  // cost-to-sell calculator
  var c=document.getElementById('costcalc');
  if(c){
    function n(id){return parseFloat(String(document.getElementById(id).value).replace(/[^0-9.]/g,''))||0;}
    function $(x){return '$'+Math.round(x).toLocaleString('en-CA');}
    function run(){
      var price=n('k-price'), com=price*n('k-com')/100, hst=com*.13, legal=n('k-legal'), mort=n('k-mort'), pen=n('k-pen'), other=n('k-other');
      var net=price-com-hst-legal-mort-pen-other;
      document.getElementById('o-com').textContent=$(com);
      document.getElementById('o-hst').textContent=$(hst);
      document.getElementById('o-legal').textContent=$(legal);
      document.getElementById('o-mort').textContent=$(mort+pen);
      document.getElementById('o-other').textContent=$(other);
      document.getElementById('o-net').textContent=$(net);
    }
    c.addEventListener('input',run); c.addEventListener('submit',function(e){e.preventDefault();}); run();
  }
})();
