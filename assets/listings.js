/* Live MLS® listings for soldmike.com (CREA DDF® National Shared Pool).
   Data comes from our own Cloudflare Worker; this file only renders it.
   Rules followed here: brokerage on every card, "Powered by REALTOR.ca" logo linked to the
   listing on REALTOR.ca, CREA photos shown as supplied, terms-of-use notice that must be
   accepted or dismissed. Views/saves go to Follow Up Boss only for visitors who gave contact info. */
(function(){
  var local=/^(localhost|127\.0\.0\.1)$/.test(location.hostname);
  var API=local?'http://localhost:8787':'https://soldmike-listings.broker-e2c.workers.dev';
  var RCA_LOGO='https://www.realtor.ca/images/en-ca/powered_by_realtor.svg';
  var SM=window.SM={api:API};

  function store(k,v){try{if(v===undefined)return JSON.parse(localStorage.getItem(k)||'null');localStorage.setItem(k,JSON.stringify(v));}catch(e){return null;}}
  SM.store=store;
  var esc=SM.esc=function(s){return String(s==null?'':s).replace(/[&<>"']/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c];});};

  // anonymous device id for CREA's Analytics Web Service
  SM.uid=function(){var u=store('sm_uid');if(!u){u=(window.crypto&&crypto.randomUUID?crypto.randomUUID():String(Date.now())+Math.random().toString(16).slice(2));store('sm_uid',u);}return u;};
  // a visitor becomes a known lead once they send any form on the site
  SM.lead=function(){var l=store('sm_lead');return l&&(l.email||l.phone)?l:null;};

  SM.get=function(path){return fetch(API+path,{credentials:'omit'}).then(function(r){if(!r.ok)throw r.status;return r.json();});};
  SM.post=function(path,body){return fetch(API+path,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)}).then(function(r){return r.json();});};

  SM.money=function(n){return n==null?'':'$'+Math.round(n).toLocaleString('en-CA');};
  SM.priceText=function(l){if(l.price==null)return 'Price on request';return SM.money(l.price)+(l.lease?'/'+(String(l.freq||'month').toLowerCase().replace(/^monthly$/,'month')):'');};
  SM.addrText=function(l){return l.addr?l.addr+', '+l.city:(l.community?l.community+', ':'')+l.city;};
  SM.isNew=function(l){return l.listed&&(Date.now()-Date.parse(l.listed))<7*864e5;};
  SM.link=function(id){return '/listings/home/?id='+encodeURIComponent(id);};
  SM.rca=function(url,w){return '<a class="rca" href="'+esc(url)+'" target="_blank" rel="noopener" aria-label="View this listing on REALTOR.ca"><img src="'+RCA_LOGO+'" width="'+(w||90)+'" alt="Powered by REALTOR.ca" loading="lazy"></a>';};

  // ---------- saved homes ----------
  SM.saved=function(){return store('sm_saved')||[];};
  SM.isSaved=function(id){return SM.saved().indexOf(String(id))>=0;};
  SM.toggleSave=function(id){
    id=String(id);var s=SM.saved(),i=s.indexOf(id),on=i<0;
    if(on)s.unshift(id);else s.splice(i,1);
    store('sm_saved',s.slice(0,50));
    if(on&&SM.lead())SM.post('/api/track',{id:id,event:'save',lead:SM.lead()}).catch(function(){});
    toast(on?(SM.lead()?'Saved. Michael will keep an eye on it for you.':'Saved on this device. <a href="/saved/">See your saved homes</a>'):'Removed from saved homes');
    [].forEach.call(document.querySelectorAll('.save[data-id="'+id+'"]'),function(b){b.setAttribute('aria-pressed',on);});
    return on;
  };
  function toast(html){
    var t=document.getElementById('smToast');
    if(!t){t=document.createElement('div');t.id='smToast';t.setAttribute('role','status');document.body.appendChild(t);}
    t.innerHTML=html;t.classList.add('on');clearTimeout(t._h);t._h=setTimeout(function(){t.classList.remove('on');},3800);
  }
  SM.toast=toast;
  document.addEventListener('click',function(e){var b=e.target.closest('.save[data-id]');if(b){e.preventDefault();SM.toggleSave(b.dataset.id);}});

  var HEART='<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 20.5s-7.5-4.6-9.3-9.2C1.4 7.9 3.6 4.5 7 4.5c2 0 3.5 1.1 5 3 1.5-1.9 3-3 5-3 3.4 0 5.6 3.4 4.3 6.8-1.8 4.6-9.3 9.2-9.3 9.2z"/></svg>';
  SM.heart=HEART;

  // ---------- result card (brokerage + REALTOR.ca logo on every card) ----------
  SM.card=function(l){
    var href=SM.link(l.id), specs=[];
    if(l.beds!=null&&l.beds!=='')specs.push(esc(l.beds)+' bed');
    if(l.baths!=null)specs.push(esc(l.baths)+' bath');
    if(l.type)specs.push(esc(l.type));
    if(l.size)specs.push(esc(l.size));
    var tags='';
    if(l.lease)tags+='<span class="tag">For rent</span>';else if(SM.isNew(l))tags+='<span class="tag">New</span>';
    if(l.mine)tags+='<span class="tag op">SoldMike listing</span>';
    var img=l.photo?'<img src="'+esc(l.photo)+'" alt="'+esc(SM.addrText(l))+'" loading="lazy">':'<span class="nophoto">Photos coming</span>';
    return '<article class="card lc"><a class="ph" href="'+href+'" target="_blank" rel="noopener">'+img+tags+'</a>'
      +'<button class="save" type="button" data-id="'+esc(l.id)+'" aria-pressed="'+SM.isSaved(l.id)+'" aria-label="Save this home">'+HEART+'</button>'
      +'<div class="meta"><a class="price" href="'+href+'" target="_blank" rel="noopener">'+esc(SM.priceText(l))+'</a>'
      +'<div class="addr">'+esc(SM.addrText(l))+(l.addr?'':' <small>(address not displayed)</small>')+'</div>'
      +'<div class="specs">'+specs.join(' · ')+'</div>'
      +'<div class="brk">Listed by '+esc(l.office||'listing brokerage')+'</div>'
      +'<div class="fine"><span>MLS® '+esc(l.mls)+'</span>'+SM.rca(l.rca,90)+'</div></div></article>';
  };
  SM.cards=function(el,items,empty){
    el.innerHTML=items.length?items.map(SM.card).join(''):'<p class="empty">'+(empty||'No homes match right now. Check back tomorrow, the list refreshes every day.')+'</p>';
  };
  SM.loading=function(el,n){var h='';for(var i=0;i<(n||3);i++)h+='<div class="card lc sk"><div class="ph"></div><div class="meta"><i></i><i></i><i></i></div></div>';el.innerHTML=h;};

  // ---------- area blocks: <div data-area="woodbridge" data-n="3"> and <span data-area-count="woodbridge"> ----------
  function areas(){
    var grids=[].slice.call(document.querySelectorAll('[data-area]')), counts=[].slice.call(document.querySelectorAll('[data-area-count]'));
    var want={};grids.forEach(function(g){want[g.dataset.area]=1;SM.loading(g,+g.dataset.n||3);});counts.forEach(function(c){want[c.dataset.areaCount]=1;});
    Object.keys(want).forEach(function(a){
      SM.get('/api/area?a='+encodeURIComponent(a)).then(function(r){
        grids.filter(function(g){return g.dataset.area===a;}).forEach(function(g){SM.cards(g,r.items.slice(0,+g.dataset.n||3));});
        counts.filter(function(c){return c.dataset.areaCount===a;}).forEach(function(c){c.textContent=r.capped?'1,000+':r.count.toLocaleString('en-CA');});
      }).catch(function(){
        grids.filter(function(g){return g.dataset.area===a;}).forEach(function(g){g.innerHTML='<p class="empty">Listings are loading slowly. <a href="/listings/">Search all homes</a>.</p>';});
      });
    });
  }
  SM.areas=areas;

  // ---------- terms of use notice (CREA DDF® rule 6(d): accept or dismiss) ----------
  function terms(){
    if(store('sm_terms'))return;
    var d=document.createElement('div');d.className='terms-bar';d.setAttribute('role','region');d.setAttribute('aria-label','Terms of use');
    d.innerHTML='<p>Listings on this site come from members of The Canadian Real Estate Association (CREA). By using this site you agree to our <a href="/terms/">Terms of Use</a>, including that listing content is for your personal, non-commercial use only.</p><div><button type="button" class="btn" data-t="accept">Accept</button><button type="button" class="btn ghost" data-t="dismiss">Dismiss</button></div>';
    d.addEventListener('click',function(e){var b=e.target.closest('[data-t]');if(!b)return;store('sm_terms',{v:1,a:b.dataset.t,at:new Date().toISOString()});d.remove();});
    document.body.appendChild(d);
  }
  SM.terms=terms;

  document.addEventListener('DOMContentLoaded',function(){
    if(document.querySelector('[data-listings]'))terms();
    areas();
  });
})();
