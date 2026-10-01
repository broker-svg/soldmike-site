/* Mika, the SoldMike chat assistant. Preview: answers are pre-written until Claude is connected through the Worker.
   Leads from the chat go to Follow Up Boss through the same Worker as the site forms. */
(function(){
  if(window.__mika) return; window.__mika=1;
  var FUB='https://dawn-sun-5ae8.broker-e2c.workers.dev';
  var reduce=window.matchMedia&&matchMedia('(prefers-reduced-motion: reduce)').matches;

  var css=''
  +'#mika-btn{position:fixed;right:max(20px,env(safe-area-inset-right,0px));bottom:calc(24px + env(safe-area-inset-bottom,0px));z-index:900;display:flex;align-items:center;gap:12px;min-height:64px;padding:6px 22px 6px 6px;border:3px solid #fff;border-radius:40px;background:#26348B;color:#fff;font:600 18px Barlow,system-ui,sans-serif;cursor:pointer;box-shadow:0 18px 40px -10px rgba(20,24,51,.55);transition:transform .25s cubic-bezier(.2,.7,.1,1)}'
  +'#mika-btn:hover{transform:translateY(-2px)}'
  +'#mika-btn .av{width:48px;height:48px}'
  +'#mika-btn.hide{transform:translateY(140%);pointer-events:none}'
  +'.menu-open #mika-btn{display:none}'
  +'@media (max-width:560px){#mika-btn{min-height:56px;font-size:17px;padding:4px 18px 4px 4px;right:14px;bottom:calc(14px + env(safe-area-inset-bottom,0px))}#mika-btn .av{width:42px;height:42px;font-size:21px}#mika-btn .lbl-long{display:none}}'
  +'.mika-av{flex:none;border-radius:50%;background:#D7141E;color:#fff;display:grid;place-items:center;font:800 24px "Barlow Condensed",sans-serif;position:relative}'
  +'.mika-av::after{content:"";position:absolute;right:1px;bottom:1px;width:12px;height:12px;border-radius:50%;background:#2BB673;border:2px solid #26348B}'
  +'#mika{position:fixed;right:max(20px,env(safe-area-inset-right,0px));bottom:calc(20px + env(safe-area-inset-bottom,0px));z-index:901;width:min(460px,calc(100vw - 40px));height:min(720px,calc(100vh - 40px));background:#fff;border-radius:14px;box-shadow:0 30px 80px -20px rgba(20,24,51,.55);display:flex;flex-direction:column;overflow:hidden;font-family:Barlow,system-ui,sans-serif;color:#141833;opacity:0;transform:translateY(24px) scale(.97);transform-origin:bottom right;pointer-events:none;transition:opacity .3s,transform .35s cubic-bezier(.2,.7,.1,1)}'
  +'#mika.open{opacity:1;transform:none;pointer-events:auto}'
  +'@media (max-width:560px){#mika{right:0;bottom:0;width:100vw;height:100%;border-radius:0}}'
  +'#mika header{background:#26348B;color:#fff;padding:18px 18px 16px 20px;display:flex;align-items:center;gap:14px}'
  +'#mika header .av{width:52px;height:52px}'
  +'#mika header b{display:block;font:800 28px/1 "Barlow Condensed",sans-serif;text-transform:uppercase;letter-spacing:.01em}'
  +'#mika header div span{display:block;font-size:15px;color:#C9D0F2;margin-top:4px}'
  +'#mika header button{margin-left:auto;width:48px;height:48px;border:0;border-radius:50%;background:rgba(255,255,255,.12);color:#fff;cursor:pointer;display:grid;place-items:center}'
  +'#mika header button:hover{background:rgba(255,255,255,.22)}'
  +'#mika .log{flex:1;overflow-y:auto;padding:22px 18px 10px;display:flex;flex-direction:column;gap:14px;scroll-behavior:smooth;background:#F7F8FB}'
  +'#mika .m{max-width:88%;font-size:19px;line-height:1.5;padding:14px 18px;border-radius:16px;white-space:pre-wrap;word-wrap:break-word}'
  +'#mika .m.bot{align-self:flex-start;background:#fff;border:1px solid #DCE0EC;border-bottom-left-radius:4px}'
  +'#mika .m.me{align-self:flex-end;background:#26348B;color:#fff;border-bottom-right-radius:4px}'
  +'#mika .m a{color:#D7141E;font-weight:600}'
  +'#mika .w{opacity:0;animation:mikaw .35s forwards}'
  +'@keyframes mikaw{to{opacity:1}}'
  +'#mika .typing{align-self:flex-start;display:flex;gap:6px;padding:16px 18px;background:#fff;border:1px solid #DCE0EC;border-radius:16px;border-bottom-left-radius:4px}'
  +'#mika .typing i{width:9px;height:9px;border-radius:50%;background:#545B78;animation:mikat 1s infinite}'
  +'#mika .typing i:nth-child(2){animation-delay:.15s}#mika .typing i:nth-child(3){animation-delay:.3s}'
  +'@keyframes mikat{0%,60%,100%{opacity:.25;transform:none}30%{opacity:1;transform:translateY(-4px)}}'
  +'#mika .chips{display:flex;flex-wrap:wrap;gap:8px;padding:2px 0 4px}'
  +'#mika .chips button{min-height:46px;padding:8px 16px;border:1.5px solid #26348B;border-radius:24px;line-height:1.25;background:#fff;color:#26348B;font:600 17px Barlow,system-ui,sans-serif;cursor:pointer;text-align:left}'
  +'#mika .chips button:hover{background:#26348B;color:#fff}'
  +'#mika .lead{align-self:stretch;background:#fff;border:1px solid #DCE0EC;border-radius:12px;padding:16px;display:flex;flex-direction:column;gap:10px}'
  +'#mika .lead label{font-size:15px;font-weight:600;color:#545B78}'
  +'#mika .lead input{width:100%;min-height:50px;border:1px solid #DCE0EC;border-radius:6px;padding:0 14px;font:400 18px Barlow,system-ui,sans-serif;color:#141833;box-sizing:border-box}'
  +'#mika .lead button{min-height:52px;border:0;border-radius:6px;background:#D7141E;color:#fff;font:600 18px Barlow,system-ui,sans-serif;cursor:pointer}'
  +'#mika .lead small{font-size:13px;color:#545B78;line-height:1.4}'
  +'#mika form.ask{display:flex;gap:10px;padding:14px 16px calc(14px + env(safe-area-inset-bottom,0px));border-top:1px solid #DCE0EC;background:#fff}'
  +'#mika form.ask input{flex:1;min-width:0;min-height:56px;border:1.5px solid #DCE0EC;border-radius:28px;padding:0 20px;font:400 19px Barlow,system-ui,sans-serif;color:#141833}'
  +'#mika form.ask input:focus{outline:none;border-color:#26348B}'
  +'#mika form.ask button{flex:none;width:56px;height:56px;border:0;border-radius:50%;background:#D7141E;color:#fff;cursor:pointer;display:grid;place-items:center}'
  +'#mika .foot{font-size:12px;color:#545B78;text-align:center;padding:0 16px 10px;background:#fff}'
  +'#mika :focus-visible,#mika-btn:focus-visible{outline:3px solid #FF5A5F;outline-offset:2px}'
  +'@media (prefers-reduced-motion:reduce){#mika,#mika-btn{transition:none}#mika .w{animation:none;opacity:1}}';
  var st=document.createElement('style'); st.textContent=css; document.head.appendChild(st);

  var X='<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round"><path d="M6 6l12 12M18 6L6 18"/></svg>';
  var SEND='<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h13M13 6l6 6-6 6"/></svg>';

  var btn=document.createElement('button');
  btn.id='mika-btn'; btn.type='button'; btn.setAttribute('aria-controls','mika'); btn.setAttribute('aria-expanded','false');
  btn.innerHTML='<span class="mika-av av" aria-hidden="true">M</span>Ask Mika<span class="lbl-long">&nbsp;a question</span>';
  var box=document.createElement('section');
  box.id='mika'; box.setAttribute('role','dialog'); box.setAttribute('aria-label','Chat with Mika, the SoldMike assistant'); box.setAttribute('aria-hidden','true');
  box.innerHTML='<header><span class="mika-av av" aria-hidden="true">M</span><div><b>Mika</b><span>SoldMike assistant · Michael follows up personally</span></div><button type="button" class="x" aria-label="Close chat">'+X+'</button></header>'
    +'<div class="log" aria-live="polite"></div>'
    +'<form class="ask"><label for="mika-in" style="position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0)">Type your question</label><input id="mika-in" type="text" autocomplete="off" placeholder="Type your question…"><button type="submit" aria-label="Send">'+SEND+'</button></form>'
    +'<div class="foot">Preview: sample answers until the live assistant is connected.</div>';
  document.body.appendChild(btn); document.body.appendChild(box);
  var log=box.querySelector('.log'), input=box.querySelector('#mika-in'), started=false;

  function scroll(){log.scrollTop=log.scrollHeight;}
  function me(t){var d=document.createElement('div');d.className='m me';d.textContent=t;log.appendChild(d);scroll();}
  // answers flow in word by word; [text](url) becomes a link
  function bot(text,then){
    var ty=document.createElement('div');ty.className='typing';ty.innerHTML='<i></i><i></i><i></i>';ty.setAttribute('aria-label','Mika is typing');log.appendChild(ty);scroll();
    setTimeout(function(){
      ty.remove();
      var d=document.createElement('div');d.className='m bot';log.appendChild(d);
      var parts=text.split(/(\[[^\]]+\]\([^)]+\))/), words=[];
      parts.forEach(function(p){var mm=p.match(/^\[([^\]]+)\]\(([^)]+)\)$/);if(mm)words.push({a:mm[1],h:mm[2]});else p.split(/(\s+)/).forEach(function(w){if(w)words.push(w);});});
      var i=0;
      (function step(){
        if(i>=words.length){scroll();if(then)then();return;}
        var w=words[i++],el;
        if(typeof w==='object'){el=document.createElement('a');el.href=w.h;el.textContent=w.a;}
        else if(/^\s+$/.test(w)){d.appendChild(document.createTextNode(w));step();return;}
        else{el=document.createElement('span');el.textContent=w;}
        el.className='w';d.appendChild(el);scroll();
        setTimeout(step,reduce?0:38);
      })();
    },reduce?0:650);
  }
  function chips(list){
    var c=document.createElement('div');c.className='chips';
    list.forEach(function(t){var b=document.createElement('button');b.type='button';b.textContent=t;b.onclick=function(){c.remove();ask(t);};c.appendChild(b);});
    log.appendChild(c);scroll();
  }
  function leadForm(topic){
    var f=document.createElement('form');f.className='lead';
    var id='ml'+Date.now();
    f.innerHTML='<div><label for="'+id+'n">Your name</label><input id="'+id+'n" name="name" autocomplete="name"></div>'
      +'<div><label for="'+id+'p">Phone or email</label><input id="'+id+'p" name="contact" autocomplete="tel"></div>'
      +'<button type="submit">Have Michael follow up</button><small>By sending, I agree to be contacted by RE/MAX Premier The OP Team by call, text and email. Reply STOP to opt out.</small>';
    f.onsubmit=function(e){
      e.preventDefault();
      var n=f.elements.name.value.trim(), c=f.elements.contact.value.trim();
      if(!n||!c){bot('I just need your name and a phone number or email so Michael can reach you.');return;}
      var parts=n.split(/\s+/), isMail=c.indexOf('@')>0, sb=f.querySelector('button');
      sb.disabled=true; sb.textContent='Sending…';
      var convo=[].map.call(log.querySelectorAll('.m'),function(m){return (m.classList.contains('me')?'Visitor: ':'Mika: ')+m.textContent;}).join(' | ').slice(-1500);
      fetch(FUB,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({firstName:parts[0],lastName:parts.slice(1).join(' '),email:isMail?c:'',phone:isMail?'':c,message:'[Chat with Mika] Topic: '+topic+'. Conversation: '+convo+' (page: '+location.pathname+')',property:'soldmike.com, Chat'})})
        .then(function(r){return r.json();}).then(function(r){if(!r.success)throw 0;f.remove();bot('Thanks, '+parts[0]+'. Michael has your message and will be in touch shortly. Anything else I can help with?');})
        .catch(function(){sb.disabled=false;sb.textContent='Have Michael follow up';bot('That did not go through. You can call or text Michael directly at 647-694-3109.');});
    };
    log.appendChild(f);scroll();setTimeout(function(){f.elements.name.focus();},50);
  }

  var A=[
    [/worth|value|apprais|evaluat|price my/i,'Home values depend most on what similar homes nearby sold for in the last few months. Michael pulls those sales and sends you a price range with the comparables attached, no obligation.\n\nWant him to do that for your home?','Home value',true],
    [/cost to sell|selling cost|fees|commission|net/i,'The main costs of selling in Ontario are the real estate commission plus 13% HST on it, legal fees, and paying out your mortgage, including any penalty. Sellers don’t pay land transfer tax.\n\nYou can run your own numbers in the [cost to sell calculator](/sell/cost-to-sell-vaughan/).','Cost to sell',false],
    [/down ?payment|deposit|afford|mortgage|pre-?approv/i,'In Canada you need at least 5% down on the first $500,000 and 10% on the portion between $500,000 and $1.5 million. Homes at $1.5 million or more need 20% down.\n\nMichael can connect you with a mortgage agent for a pre-approval if that helps.','Down payment',true],
    [/famil|school|neighbo|area|live|woodbridge|kleinburg|maple|vellore|king|nobleton|caledon|bolton/i,'Great question. Woodbridge, Vellore, Kleinburg and Maple are all popular with families, each for different reasons: schools, lot sizes, commute and price.\n\nThe [neighbourhood guides](/neighbourhoods/) compare them. Tell me what matters most to you and Michael can shortlist the right areas.','Neighbourhoods',true],
    [/show|see (the|a) (home|house)|tour|visit|book/i,'Happy to set up a showing. Michael can usually get you in within a day or two.\n\nLeave your name and number and he will confirm a time.','Showing',true],
    [/buy first|sell first|both/i,'It depends on how much risk you can carry. Selling first gives you a firm budget; buying first means you might carry two homes for a while.\n\nMichael can walk through your numbers and timing with you.','Buy or sell first',true]
  ];
  function ask(t){
    me(t);
    for(var i=0;i<A.length;i++){
      if(A[i][0].test(t)){var a=A[i];bot(a[1],function(){if(a[3])leadForm(a[2]);else chips(["What's my home worth?",'Talk to Michael']);});return;}
    }
    if(/talk|call|michael|human|agent|contact/i.test(t)){bot('Of course. Leave your name and number and Michael will reach out personally.',function(){leadForm('Wants to talk to Michael');});return;}
    bot('Good question. I want you to get the right answer, so I’ll pass this to Michael and he’ll reply personally.',function(){leadForm('Question: '+t);});
  }
  function open(){
    box.classList.add('open');box.setAttribute('aria-hidden','false');btn.classList.add('hide');btn.setAttribute('aria-expanded','true');
    if(!started){started=true;bot('Hi, I’m Mika, Michael’s assistant. Ask me anything about buying or selling in Vaughan and the GTA.',function(){chips(["What's my home worth?",'What does it cost to sell?','Best areas for families','How much do I need for a down payment?']);});}
    setTimeout(function(){input.focus();},300);
  }
  function close(){box.classList.remove('open');box.setAttribute('aria-hidden','true');btn.classList.remove('hide');btn.setAttribute('aria-expanded','false');btn.focus();}
  btn.onclick=open;
  box.querySelector('.x').onclick=close;
  box.addEventListener('keydown',function(e){if(e.key==='Escape')close();});
  box.querySelector('form.ask').onsubmit=function(e){e.preventDefault();var t=input.value.trim();if(!t)return;input.value='';var c=log.querySelector('.chips');if(c)c.remove();ask(t);};
  window.openMika=open;
  window.askMika=function(t){started=true;open();setTimeout(function(){ask(t);},350);};
})();
