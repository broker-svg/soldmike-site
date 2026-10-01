(function(){
  var FUB='https://dawn-sun-5ae8.broker-e2c.workers.dev';
  var reduce=window.matchMedia&&matchMedia('(prefers-reduced-motion: reduce)').matches;

  // mobile menu + dropdowns
  var burger=document.querySelector('.burger'), nav=document.getElementById('nav');
  if(burger){burger.addEventListener('click',function(){var o=nav.classList.toggle('open');burger.setAttribute('aria-expanded',o);});}
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
        f.reset(); msg.className='msg'; msg.textContent=f.dataset.done||'Sent. Michael will be in touch shortly.'; btn.textContent=t; btn.disabled=false;
      }).catch(function(){
        msg.className='msg err'; msg.textContent='That did not go through. Call or text Michael at 647-278-2237.'; btn.textContent=t; btn.disabled=false;
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
