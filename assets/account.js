/* Visitor accounts for soldmike.com: "Sign in with Google", saved homes and saved searches on every device.
   Needs listings.js (SM). The session token lives in this browser only; listing data never goes anywhere but our own Worker. */
(function(){
  var GOOGLE_CLIENT_ID=''; // set once Michael creates the Google sign-in key (public value, not a secret)
  var SM=window.SM; if(!SM)return;
  var esc=SM.esc;
  function tok(){return SM.store('sm_session')||'';}
  function call(path,body){
    return fetch(SM.api+path,{method:body?'POST':'GET',headers:Object.assign({'Authorization':'Bearer '+tok()},body?{'Content-Type':'application/json'}:{}),body:body?JSON.stringify(body):undefined})
      .then(function(r){return r.json().then(function(j){if(r.status===401){SM.store('sm_session','');SM.account=null;}if(!r.ok)throw j.error||'error';return j;});});
  }
  function apply(j){
    SM.account=j;
    // homes saved on this device and on the account are the same list
    try{localStorage.setItem('sm_saved',JSON.stringify(j.saved.slice(0,50)));}catch(e){}
    // a signed-in visitor is a known lead, so their views/saves reach Michael like any form lead
    if(j.me&&j.me.email)try{localStorage.setItem('sm_lead',JSON.stringify({firstName:j.me.first||'',lastName:j.me.last||'',email:j.me.email}));}catch(e){}
    [].forEach.call(document.querySelectorAll('.save[data-id]'),function(b){b.setAttribute('aria-pressed',j.saved.indexOf(b.dataset.id)>=0);});
    document.dispatchEvent(new CustomEvent('sm:account',{detail:j}));
    return j;
  }
  SM.signedIn=function(){return !!tok();};
  SM.signOut=function(){var t=tok();if(t)call('/api/me/logout',{}).catch(function(){});SM.store('sm_session','');SM.account=null;
    try{localStorage.removeItem('sm_lead');}catch(e){}document.dispatchEvent(new CustomEvent('sm:account',{detail:null}));};

  // keep the heart buttons in sync with the account
  var orig=SM.toggleSave;
  SM.toggleSave=function(id){orig(id);if(!tok())return;var on=SM.isSaved(id);call('/api/me/save',{key:String(id),on:on}).then(apply).catch(function(){});};

  // ---------- sign-in dialog ----------
  var gisLoading=null;
  function loadGis(){if(window.google&&google.accounts)return Promise.resolve();if(gisLoading)return gisLoading;
    gisLoading=new Promise(function(res,rej){var s=document.createElement('script');s.src='https://accounts.google.com/gsi/client';s.async=true;s.onload=res;s.onerror=rej;document.head.appendChild(s);});return gisLoading;}
  function css(){if(document.getElementById('acctCss'))return;var st=document.createElement('style');st.id='acctCss';
    st.textContent='#acctDlg{border:0;border-radius:12px;padding:0;width:min(440px,calc(100vw - 32px));box-shadow:0 30px 60px rgba(10,14,40,.35);font-family:Barlow,system-ui,sans-serif;color:#141833}#acctDlg::backdrop{background:rgba(20,24,51,.6)}#acctDlg .in{padding:28px 26px 22px;display:flex;flex-direction:column;gap:14px}#acctDlg h2{margin:0;font-family:"Barlow Condensed",sans-serif;font-weight:800;font-size:34px;line-height:1;text-transform:uppercase}#acctDlg p{margin:0;color:#545B78;font-size:17px;line-height:1.5}#acctDlg .gbtn{min-height:44px;display:flex;justify-content:center}#acctDlg .x{align-self:center;border:0;background:none;color:#545B78;text-decoration:underline;cursor:pointer;font-size:15px;padding:8px}#acctDlg .fine{font-size:13px}#acctDlg .err{color:#D7141E;font-weight:600}#acctDlg label.ck{display:flex;gap:10px;align-items:flex-start;font-size:16px;cursor:pointer}#acctDlg label.ck input{width:22px;height:22px;flex:none;margin-top:2px;accent-color:#1D2870}#acctDlg .row{display:flex;gap:10px}#acctDlg .row button{flex:1;min-height:50px;border-radius:4px;border:0;font:600 17px Barlow,system-ui,sans-serif;cursor:pointer}#acctDlg .ok{background:#D7141E;color:#fff}#acctDlg .no{background:#fff;border:1px solid #DCE0EC!important;color:#141833}#acctDlg .or{text-align:center;color:#545B78;font-size:14px;display:flex;align-items:center;gap:10px}#acctDlg .or::before,#acctDlg .or::after{content:"";flex:1;height:1px;background:#DCE0EC}#acctDlg .ef{display:flex;flex-direction:column;gap:10px}#acctDlg .ef input{min-height:52px;border:1px solid #DCE0EC;border-radius:4px;padding:0 14px;font:400 18px Barlow,system-ui,sans-serif}#acctDlg .ef .ok{min-height:50px;border:0;border-radius:4px;font:600 17px Barlow,system-ui,sans-serif;cursor:pointer;background:#D7141E;color:#fff}#acctDlg .ef .ok:disabled{opacity:.6}';
    document.head.appendChild(st);}
  function dlg(html){css();var d=document.getElementById('acctDlg');if(!d){d=document.createElement('dialog');d.id='acctDlg';document.body.appendChild(d);}
    d.innerHTML='<div class="in">'+html+'</div>';if(!d.open)d.showModal();return d;}
  SM.signIn=function(why){
    return new Promise(function(res,rej){
      var d=dlg('<h2>Sign in</h2><p>'+esc(why||'Save homes and searches on every device, and get new matches by email.')+'</p><div class="gbtn" id="gBtn"></div><p class="err" id="gErr" hidden></p>'
        +'<div class="or">or use any email</div><form id="eForm" class="ef"><input id="eIn" type="email" autocomplete="email" placeholder="Your email" required><button type="submit" class="ok">Email me a code</button></form>'
        +'<form id="cForm" class="ef" hidden><p style="font-size:16px">We sent a 6-digit code to <b id="cTo"></b>. It can take a minute. Check spam if you don’t see it.</p><input id="cIn" inputmode="numeric" autocomplete="one-time-code" maxlength="6" placeholder="6-digit code" required><button type="submit" class="ok">Sign in</button></form><p class="err" id="eErr" hidden></p>'
        +'<p class="fine">By signing in you agree to be contacted by RE/MAX Premier The OP Team about homes you save. See our <a href="/privacy/">Privacy Policy</a>.</p><button type="button" class="x" id="gClose">Not now</button>');
      var done=false;
      document.getElementById('gClose').onclick=function(){d.close();if(!done)rej('closed');};
      var err=document.getElementById('gErr');
      function finish(j){SM.store('sm_session',j.token);apply(j);
        var mine=(SM.saved()||[]).filter(function(k){return j.saved.indexOf(k)<0;});
        return (mine.length?call('/api/me/save',{keys:mine}).then(apply):Promise.resolve(j)).then(function(j){done=true;d.close();res(j);});}
      function post(path,body){return fetch(SM.api+path,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)}).then(function(x){return x.json().then(function(j){if(!x.ok)throw j.error;return j;});});}
      var eErr=document.getElementById('eErr'),em='';
      function bad(e){eErr.hidden=false;eErr.textContent=typeof e==='string'?e:'That did not work. Please try again.';}
      document.getElementById('eForm').onsubmit=function(ev){ev.preventDefault();var b=this.querySelector('button');em=document.getElementById('eIn').value.trim();b.disabled=true;eErr.hidden=true;
        post('/api/auth/code',{email:em}).then(function(){document.getElementById('eForm').hidden=true;document.getElementById('cTo').textContent=em;document.getElementById('cForm').hidden=false;document.getElementById('cIn').focus();}).catch(bad).then(function(){b.disabled=false;});};
      document.getElementById('cForm').onsubmit=function(ev){ev.preventDefault();var b=this.querySelector('button');b.disabled=true;eErr.hidden=true;
        post('/api/auth/verify',{email:em,code:document.getElementById('cIn').value}).then(finish).catch(function(e){b.disabled=false;bad(e);});};
      if(!GOOGLE_CLIENT_ID){document.getElementById('gBtn').hidden=true;return;}
      loadGis().then(function(){
        google.accounts.id.initialize({client_id:GOOGLE_CLIENT_ID,callback:function(r){
          err.hidden=true;
          fetch(SM.api+'/api/auth/google',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({credential:r.credential})})
            .then(function(x){return x.json().then(function(j){if(!x.ok)throw j.error;return j;});})
            .then(finish)
            .catch(function(e){err.hidden=false;err.textContent=typeof e==='string'?e:'That did not work. Please try again.';});
        }});
        google.accounts.id.renderButton(document.getElementById('gBtn'),{theme:'outline',size:'large',text:'signin_with',shape:'rectangular',width:300});
      }).catch(function(){err.hidden=false;err.textContent='Google sign-in could not load. Check your connection and try again.';});
    });
  };
  function ensure(why){return tok()?Promise.resolve(SM.account):SM.signIn(why);}

  // ---------- "Save this search" (search page and Buy page) ----------
  var LABEL={detached:'Detached homes',semi:'Semi-detached homes',town:'Townhouses',condo:'Condos',other:'Homes'};
  function describe(q){var t=LABEL[q.type]||(q.lease==='1'?'Rentals':'Homes');var area=document.querySelector('#f-area option[value="'+(q.area||'')+'"]');
    var m=function(n){n=+n;return n>=1e6?'$'+(+(n/1e6).toFixed(2))+'M':'$'+Math.round(n/1000)+'K';};
    var b=[t+' in '+(q.area&&area?area.textContent:'all areas')];if(q.min&&q.max)b.push(m(q.min)+' to '+m(q.max));else if(q.min)b.push('from '+m(q.min));else if(q.max)b.push('up to '+m(q.max));
    if(q.beds)b.push(q.beds+'+ beds');if(q.baths)b.push(q.baths+'+ baths');return b.join(', ');}
  function current(){var f=document.getElementById('lsForm'),q={};if(!f)return q;['area','lease','type','min','max','beds','baths'].forEach(function(k){var e=f.elements[k];if(e&&e.value)q[k]=e.value;});return q;}
  SM.saveSearch=function(){
    ensure('Sign in to save this search and get new matches by email.').then(function(){
      var q=current(),d=dlg('<h2>Save this search</h2><p><b style="color:#1D2870">'+esc(describe(q))+'</b></p>'
        +'<label class="ck"><input type="checkbox" id="ssAlerts"><span>Email me new listings that match. I can stop them any time.</span></label><p class="err" id="ssErr" hidden></p>'
        +'<div class="row"><button type="button" class="ok" id="ssOk">Save search</button><button type="button" class="no" id="ssNo">Cancel</button></div>');
      document.getElementById('ssNo').onclick=function(){d.close();};
      document.getElementById('ssOk').onclick=function(){var b=this;b.disabled=true;
        call('/api/me/search',{q:q,alerts:document.getElementById('ssAlerts').checked}).then(apply).then(function(){
          dlg('<h2>Search saved</h2><p>See it any time on <a href="/saved/">your saved homes and searches</a>.</p><div class="row"><button type="button" class="ok" id="ssDone">Done</button></div>');
          document.getElementById('ssDone').onclick=function(){document.getElementById('acctDlg').close();};
        }).catch(function(e){b.disabled=false;var er=document.getElementById('ssErr');er.hidden=false;er.textContent=typeof e==='string'?e:'That did not work. Please try again.';});};
    }).catch(function(){});
  };
  document.addEventListener('DOMContentLoaded',function(){
    var bar=document.querySelector('.ls-bar');
    if(bar&&!document.getElementById('lsSaveSearch')){var b=document.createElement('button');b.type='button';b.className='btn ghost';b.id='lsSaveSearch';b.textContent='Save this search';b.onclick=SM.saveSearch;bar.insertBefore(b,bar.querySelector('.hidemap')||bar.lastChild);}
  });

  // signed in already: refresh the account (and repair a lost session quietly)
  if(tok())call('/api/me').then(apply).catch(function(){});
  SM.accountCall=call; SM.accountApply=apply;
})();
