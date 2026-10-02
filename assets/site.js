(function(){
  var FUB='https://dawn-sun-5ae8.broker-e2c.workers.dev';
  // the site's own lead list (leads page); listings Worker
  var LAPI=/^(localhost|127\.0\.0\.1)$/.test(location.hostname)?'http://localhost:8787':'https://soldmike-listings.broker-e2c.workers.dev';
  window.smLeadLog=function(l){try{fetch(LAPI+'/api/lead',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(l)}).catch(function(){});}catch(x){}};
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

  window.smSent=sentPopup;

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
        // remember the lead in this browser so the listing pages can log their views/saves in FUB
        try{localStorage.setItem('sm_lead',JSON.stringify({firstName:parts[0],lastName:parts.slice(1).join(' '),email:v('email'),phone:v('phone')}));}catch(x){}
        smLeadLog({firstName:parts[0],lastName:parts.slice(1).join(' '),email:v('email'),phone:v('phone'),source:f.dataset.lead,page:location.pathname});
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

// ---------- account button, top right of every page ----------
(function(){
  var LAPI=/^(localhost|127\.0\.0\.1)$/.test(location.hostname)?'http://localhost:8787':'https://soldmike-listings.broker-e2c.workers.dev';
  function get(k){try{return JSON.parse(localStorage.getItem(k)||'null');}catch(e){return null;}}
  function esc(s){return String(s==null?'':s).replace(/[&<>"']/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c];});}
  var st=document.createElement('style');
  st.textContent='.acct-w{position:relative;order:5;margin-left:8px;flex:none}'
    +'.acct-b{display:inline-flex;align-items:center;gap:8px;min-height:44px;padding:0 12px;border:1px solid var(--line,#DCE0EC);border-radius:22px;background:transparent;color:var(--ink,#141833);font:600 15px Barlow,system-ui,sans-serif;cursor:pointer;white-space:nowrap}'
    +'.acct-b svg{width:20px;height:20px;flex:none}.acct-b:hover{color:var(--red,#D7141E)}'
    +'#top:not(.solid) .acct-b{color:#fff;border-color:rgba(255,255,255,.6)}'
    +'.acct-m{position:absolute;right:0;top:calc(100% + 8px);min-width:250px;background:#fff;border:1px solid #DCE0EC;border-radius:8px;box-shadow:0 18px 40px -18px rgba(20,24,51,.35);padding:8px;display:none;flex-direction:column;z-index:60}'
    +'.acct-w.open .acct-m{display:flex}.acct-m p{margin:6px 12px 8px;font-size:14px;color:#545B78;line-height:1.4;word-break:break-all}'
    +'.acct-m a,.acct-m button{display:block;text-align:left;padding:11px 12px;border-radius:4px;text-decoration:none;color:#141833;font:500 16px Barlow,system-ui,sans-serif;background:none;border:0;cursor:pointer}'
    +'.acct-m a:hover,.acct-m button:hover{background:#F2F4F9;color:#D7141E}'
    +'@media (min-width:1261px) and (max-width:1439px){.acct-b .t{display:none}.acct-b{padding:0 11px}}'
    +'@media (max-width:1260px){.acct-w{order:0;margin-left:auto;margin-right:8px}}'
    +'@media (max-width:480px){.acct-b .t{max-width:70px;overflow:hidden;text-overflow:ellipsis}}';
  document.head.appendChild(st);
  var ICON='<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><circle cx="12" cy="8" r="4"/><path d="M4 21c1.5-4 4.5-6 8-6s6.5 2 8 6"/></svg>';
  var w=document.createElement('div');w.className='acct-w';
  function render(){
    var me=get('sm_me'),signed=!!get('sm_session')&&me;
    w.innerHTML='<button type="button" class="acct-b" aria-haspopup="true" aria-expanded="false">'+ICON+'<span class="t">'+(signed?esc(me.first||'My account')+' ▾':'Sign in')+'</span></button>'
      +(signed?'<div class="acct-m" role="menu"><p>Signed in as<br><b>'+esc(me.email)+'</b></p><a href="/saved/" role="menuitem">Saved homes &amp; searches</a><a href="/listings/" role="menuitem">Search homes</a><button type="button" role="menuitem" class="so">Sign out</button></div>':'');
    var b=w.querySelector('.acct-b');b.setAttribute('aria-label',signed?'Your account':'Sign in');
    b.onclick=function(e){e.stopPropagation();
      if(!signed){if(window.SM&&SM.signIn)SM.signIn().catch(function(){});else location.href='/saved/';return;}
      var o=w.classList.toggle('open');b.setAttribute('aria-expanded',o);};
    var so=w.querySelector('.so');
    if(so)so.onclick=function(){
      if(window.SM&&SM.signOut)SM.signOut();
      else{var t=get('sm_session');if(t)fetch(LAPI+'/api/me/logout',{method:'POST',headers:{'Authorization':'Bearer '+t,'Content-Type':'application/json'},body:'{}'}).catch(function(){});
        ['sm_session','sm_me','sm_lead'].forEach(function(k){try{localStorage.removeItem(k);}catch(e){}});}
      try{localStorage.removeItem('sm_me');}catch(e){}
      w.classList.remove('open');render();if(location.pathname==='/saved/')location.reload();};
  }
  document.addEventListener('click',function(e){if(!w.contains(e.target))w.classList.remove('open');});
  document.addEventListener('sm:account',render);
  // inner pages: before the burger; homepage: before the Menu button
  var inner=document.querySelector('header.top .wrap .burger'), home=document.getElementById('mbtn');
  if(inner)inner.parentNode.insertBefore(w,inner); else if(home)home.parentNode.insertBefore(w,home); else return;
  render();
})();
