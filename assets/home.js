/* Listing detail page: /listings/home/?id=<ListingKey>. Same layout as the sample listing.html.
   Shows feed text as received (no edits), brokerage near the title, REALTOR.ca logo linked to the
   listing, CREA photos as supplied. "Ask Michael" / "Book a showing" go straight to Follow Up Boss. */
(function(){
  var SM=window.SM, esc=SM.esc, root=document.getElementById('ld');
  var id=new URLSearchParams(location.search).get('id')||'';
  var ARW='<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="M15 5l-7 7 7 7"/></svg>';
  var ARW2='<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="M9 5l7 7-7 7"/></svg>';
  var GRID='<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/></svg>';
  var PIN='<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M12 21s-7-6.2-7-11.5A7 7 0 0 1 19 9.5C19 14.8 12 21 12 21z"/><circle cx="12" cy="9.5" r="2.5"/></svg>';
  var HOODS=[['vellore','Vellore Village',[43.815,43.875,-79.60,-79.525]],['kleinburg','Kleinburg',[43.82,43.90,-79.67,-79.59]],['maple','Maple',[43.83,43.88,-79.53,-79.46]],['woodbridge','Woodbridge',[43.76,43.86,-79.66,-79.52]],['king-city-nobleton','King City & Nobleton',[43.89,44.02,-79.72,-79.48]]];

  if(!/^[\w-]{1,30}$/.test(id)){gone();return;}
  SM.get('/api/listing?id='+encodeURIComponent(id)+'&u='+encodeURIComponent(SM.uid())).then(function(l){
    if(l.gone){gone();return;}
    render(l);
    // known lead viewed a listing -> FUB timeline (once per listing per day)
    var k='sm_v_'+id, today=new Date().toISOString().slice(0,10);
    if(SM.lead()&&SM.store(k)!==today){SM.store(k,today);SM.post('/api/track',{id:id,event:'view',lead:SM.lead()}).catch(function(){});}
  }).catch(function(){root.innerHTML='<div class="wrap" style="padding-block:80px"><h1>We could not load this home</h1><p>Please refresh, or <a href="/listings/">search all homes</a>.</p></div>';});

  function gone(){
    document.title='This home is no longer available | SoldMike';
    root.innerHTML='<div class="wrap" style="padding-block:80px;display:flex;flex-direction:column;gap:18px;align-items:flex-start"><h1>This home is no longer on the market</h1><p style="font-size:19px;color:var(--muted);max-width:56ch">It may have sold or been taken off the MLS®. Michael can tell you what it sold for and show you similar homes.</p><div style="display:flex;gap:10px;flex-wrap:wrap"><a class="btn" href="/listings/">Search homes for sale</a><a class="btn ghost" href="/contact/">Ask Michael</a></div></div>';
  }

  function val(v,k){
    if(v==null||v==='')return '';
    if(Array.isArray(v))return v.join(', ');
    if(v===true)return 'Yes'; if(v===false)return 'No';
    if(/Amount|Fee$/.test(k)&&typeof v==='number')return SM.money(v);
    if(/Date$/.test(k))return String(v).replace(/"/g,'').slice(0,10);
    return String(v);
  }
  function kv(f,rows){
    var h='';rows.forEach(function(r){var v=r[2]?r[2](f):val(f[r[1]],r[1]);if(v)h+='<div><dt>'+esc(r[0])+'</dt><dd>'+esc(v)+'</dd></div>';});
    return h?'<dl class="kv">'+h+'</dl>':'';
  }

  function render(l){
    var d=l.d||{}, f=d.facts||{}, P=d.photos||[], N=P.length, title=l.addr||(l.community||l.city);
    var place=[l.community,l.city,'Ontario'].filter(Boolean).join(', ');
    document.title=(l.addr?l.addr+', '+l.city:place)+' | '+SM.priceText(l)+' | SoldMike';
    var md=document.querySelector('meta[name=description]');if(md)md.setAttribute('content',[l.beds&&l.beds+' bed',l.baths&&l.baths+' bath',l.type,'for '+(l.lease?'rent':'sale')+' in '+l.city,'MLS® '+l.mls].filter(Boolean).join(' · '));
    var cn=document.querySelector('link[rel=canonical]');if(cn)cn.href='https://soldmike.com'+SM.link(id);

    var slides='',rail='',all='';
    P.forEach(function(p,i){
      var alt=esc(p.c||('Photo '+(i+1)+' of '+title));
      slides+='<div class="slide'+(i?'':' on')+'" style="--bg:url(&quot;'+esc(p.u)+'&quot;)" role="group" aria-roledescription="slide" aria-label="'+(i+1)+' of '+N+'"'+(i?' aria-hidden="true"':'')+'><img src="'+esc(p.u)+'" alt="'+alt+'"'+(i>1?' loading="lazy"':'')+'></div>';
      rail+='<li><button type="button" data-i="'+i+'" aria-label="Show photo '+(i+1)+'"'+(i?'':' aria-current="true"')+'><img src="'+esc(p.u)+'" alt="" loading="lazy"></button></li>';
      all+='<button type="button" data-i="'+i+'" aria-label="Open photo '+(i+1)+'"><img src="'+esc(p.u)+'" alt="" loading="lazy"></button>';
    });
    var facts=[[l.beds,'bedrooms'],[l.baths,'bathrooms'],[l.size?l.size.replace(/square feet/i,'').trim():'','sq ft'],[f.LotSizeDimensions,'lot size'],[f.ParkingTotal,'parking'],[l.type,'type']]
      .filter(function(x){return x[0]!=null&&x[0]!=='';}).slice(0,6);
    var tags=(l.lease?'<span class="chip red">For rent</span>':SM.isNew(l)?'<span class="chip red">New</span>':'')+(l.mine?'<span class="chip red">SoldMike listing</span>':'');
    var hood=null;HOODS.forEach(function(h){var b=h[2];if(!hood&&l.lat>=b[0]&&l.lat<b[1]&&l.lng>=b[2]&&l.lng<b[3])hood=h;});
    if(!hood&&/^toronto/i.test(l.city))hood=['toronto','Toronto'];
    var gq=encodeURIComponent(l.addr?l.addr+', '+l.city+', ON':l.lat+','+l.lng);
    var where=l.addr?l.addr+', '+l.city:'MLS® '+l.mls+', '+l.city;

    var h='';
    if(N){
      h+='<section class="stage" id="stage" tabindex="0" aria-roledescription="carousel" aria-label="Photos. Use left and right arrow keys to browse.">'
        +'<div id="slides">'+slides+'</div><div class="credit">'+tags+'</div><div class="caption" id="cap"></div>'
        +(N>1?'<button class="arrow prev" id="prev" type="button" aria-label="Previous photo">'+ARW+'</button><button class="arrow next" id="next" type="button" aria-label="Next photo">'+ARW2+'</button>':'')
        +'<div class="hud"><div class="left"><button class="pill" id="openAll" type="button">'+GRID+'View all '+N+' photos</button><a class="pill" href="#location">'+PIN+'Map</a></div><div class="count" aria-live="polite"><span id="n">1</span> / '+N+'</div></div></section>'
        +'<nav class="rail" aria-label="Photo thumbnails"><ol id="rail">'+rail+'</ol></nav>';
    }
    h+='<div class="wrap"><div class="title"><div>'+(N?'':'<div class="tags">'+tags+'</div>')
      +'<h1>'+esc(title)+'</h1><p class="sub">'+esc(place)+(l.type?' · '+esc(l.type):'')+'</p>'
      +'<p class="brk">Listing brokerage: <b>'+esc(l.office||'not provided')+'</b></p></div>'
      +'<div class="price"><b>'+esc(SM.priceText(l))+'</b><span>'+(f.TaxAnnualAmount?'Taxes '+esc(SM.money(f.TaxAnnualAmount))+(f.TaxYear?' ('+esc(f.TaxYear)+')':'')+' · ':'')+'MLS® '+esc(l.mls)+'</span>'
      +'<div class="acts"><button class="save big" type="button" data-id="'+esc(l.id)+'" aria-pressed="'+SM.isSaved(l.id)+'" aria-label="Save this home">'+SM.heart+'<span>Save</span></button>'+SM.rca(l.rca,125)+'</div></div></div>';
    if(facts.length)h+='<div class="facts" aria-label="Key facts">'+facts.map(function(x){return '<div><b>'+esc(x[0])+'</b><span>'+x[1]+'</span></div>';}).join('')+'</div>';

    h+='<div class="body"><div class="main">';
    h+='<section class="desc" aria-labelledby="d-h"><h2 id="d-h">About this home</h2>'+(d.remarks?'<p>'+esc(d.remarks)+'</p>':'<p>No description provided.</p>')+'</section>';
    var tabs=[
      ['Interior',kv(f,[['Bedrooms above grade','BedroomsAboveGrade'],['Bedrooms below grade','BedroomsBelowGrade'],['Partial bathrooms','BathroomsPartial'],['Heating','Heating'],['Cooling','Cooling'],['Basement','Basement'],['Flooring','Flooring'],['Fireplaces','FireplacesTotal'],['Fireplace','FireplaceFeatures'],['Appliances','Appliances'],['Accessibility','AccessibilityFeatures'],['Security','SecurityFeatures']])],
      ['Exterior & lot',kv(f,[['Style','ArchitecturalStyle'],['Construction','ConstructionMaterials'],['Exterior','ExteriorFeatures'],['Roof','Roof'],['Foundation','FoundationDetails'],['Parking','ParkingFeatures'],['Parking spaces','ParkingTotal'],['Lot size','LotSizeDimensions'],['Lot area','',function(x){return x.LotSizeArea?x.LotSizeArea+' '+(x.LotSizeUnits||''):'';}],['Frontage','',function(x){return x.FrontageLengthNumeric?x.FrontageLengthNumeric+' '+(x.FrontageLengthNumericUnits||''):'';}],['Lot features','LotFeatures'],['Pool','PoolFeatures'],['Fencing','Fencing'],['View','View'],['Waterfront','WaterfrontFeatures'],['Water body','WaterBodyName'],['Water','WaterSource'],['Sewer','Sewer'],['Utilities','Utilities'],['Electric','Electric'],['Road','RoadSurfaceType']])],
      ['Building',kv(f,[['Building type','StructureType'],['Ownership','CommonInterest'],['Property type','PropertySubType'],['Storeys','Stories'],['Year built','YearBuilt'],['Condition','PropertyCondition'],['Maintenance fee','',function(x){return x.AssociationFee?SM.money(x.AssociationFee)+(x.AssociationFeeFrequency?' '+x.AssociationFeeFrequency:''):'';}],['Fee includes','AssociationFeeIncludes'],['Building features','BuildingFeatures'],['Community features','CommunityFeatures'],['Units','NumberOfUnitsTotal'],['Current use','CurrentUse'],['Business type','BusinessType']])],
      ['Rooms',(d.rooms||[]).length?'<div class="tbl"><table><thead><tr><th scope="col">Room</th><th scope="col">Level</th><th scope="col">Size</th>'+((d.rooms||[]).some(function(r){return r.f;})?'<th scope="col">Features</th>':'')+'</tr></thead><tbody>'+d.rooms.map(function(r){return '<tr><td>'+esc(r.t)+'</td><td>'+esc(r.l)+'</td><td>'+esc(r.dim)+'</td>'+((d.rooms||[]).some(function(x){return x.f;})?'<td>'+esc(r.f)+'</td>':'')+'</tr>';}).join('')+'</tbody></table></div>':''],
      ['Taxes & more',kv(f,[['Annual taxes','TaxAnnualAmount'],['Tax year','TaxYear'],['Zoning','Zoning'],['Zoning description','ZoningDescription'],['Inclusions','Inclusions'],['Available','AvailabilityDate'],['Listing board','ListAOR']])]
    ].filter(function(t){return t[1];});
    if(tabs.length){
      h+='<section aria-labelledby="det-h"><h2 id="det-h">Property details</h2><div class="tabs" role="tablist" aria-label="Detail groups">'
        +tabs.map(function(t,i){return '<button type="button" role="tab" id="t'+i+'" aria-controls="p'+i+'" aria-selected="'+(i===0)+'">'+esc(t[0])+'</button>';}).join('')+'</div>'
        +tabs.map(function(t,i){return '<div role="tabpanel" id="p'+i+'" aria-labelledby="t'+i+'"'+(i?' hidden':'')+'>'+t[1]+'</div>';}).join('')+'</section>';
    }
    h+='<section id="location" aria-labelledby="loc-h"><h2 id="loc-h">Location</h2><div class="loc"><div class="map" id="lmap"></div><div><ul>'
      +'<li><span>Area</span><span>'+esc(place)+'</span></li>'+(l.addr?'':'<li><span>Address</span><span>Not displayed by the listing brokerage</span></li>')
      +'</ul><p style="margin:16px 0 0;display:flex;flex-direction:column;gap:8px"><a href="https://www.google.com/maps/search/?api=1&query='+gq+'" target="_blank" rel="noopener" style="font-weight:600">Open in Google Maps</a>'
      +(hood?'<a href="/neighbourhoods/'+hood[0]+'/" style="font-weight:600">Read the '+esc(hood[1])+' neighbourhood guide</a>':'')+'</p></div></div></section>';
    if(!l.lease&&l.price)h+='<section aria-labelledby="m-h"><h2 id="m-h">Monthly payment</h2><form class="calc" id="calc"><div><label for="c-price">Price</label><input id="c-price" inputmode="numeric" value="'+Math.round(l.price).toLocaleString('en-CA')+'"></div><div><label for="c-down">Down payment</label><select id="c-down"><option value="5">5%</option><option value="10">10%</option><option value="20" selected>20%</option><option value="25">25%</option><option value="35">35%</option></select></div><div><label for="c-rate">Rate (%)</label><input id="c-rate" inputmode="decimal" value="4.29"></div><div><label for="c-am">Amortization</label><select id="c-am"><option value="25" selected>25 years</option><option value="30">30 years</option></select></div><div class="out"><b id="c-out">$0</b><span>per month</span><small>Mortgage principal and interest only, compounded semi-annually as Canadian fixed rates are. Under 20% down needs mortgage insurance, not included. An estimate, not a quote.</small></div></form></section>';
    h+='<p class="crea-note">Listing information is provided by '+esc(l.office||'the listing brokerage')+' through CREA\'s DDF®. The information contained on this site is based in whole or in part on information that is provided by members of The Canadian Real Estate Association (CREA), who are responsible for its accuracy. CREA reproduces and distributes this information as a service for its members and assumes no responsibility for its accuracy. Deemed reliable but not guaranteed.</p>';
    h+='</div>';

    // agent card: book a showing / ask Michael (sent straight to Follow Up Boss)
    var lead=SM.lead()||{}, nm=[lead.firstName,lead.lastName].filter(Boolean).join(' ');
    h+='<aside class="aside" id="showing" aria-label="Book a showing or ask a question"><div class="agent"><div class="who"><img src="/mike.png" alt=""><div><strong>Michael Barillari</strong><span>Broker, RE/MAX Premier The OP Team</span></div></div>'
      +'<div class="atabs" role="tablist"><button type="button" role="tab" aria-selected="true" data-k="showing">Book a showing</button><button type="button" role="tab" aria-selected="false" data-k="ask">Ask Michael about this home</button></div>'
      +'<form id="inq" data-kind="showing"><div class="only-showing"><span class="lbl">Pick a day to see it</span><div class="days" id="days"></div></div>'
      +'<div class="only-showing"><label for="b-time">Time</label><select id="b-time" name="time"><option>Morning</option><option selected>Afternoon</option><option>Evening</option></select></div>'
      +'<div class="only-ask" hidden><label for="b-msg">Your question</label><textarea id="b-msg" name="message" rows="4">Hi Michael, I would like more information about '+esc(where)+'.</textarea></div>'
      +'<div class="two"><div><label for="b-name">Name</label><input id="b-name" name="name" autocomplete="name" value="'+esc(nm)+'"></div><div><label for="b-phone">Phone</label><input id="b-phone" name="phone" type="tel" autocomplete="tel" value="'+esc(lead.phone||'')+'"></div></div>'
      +'<div><label for="b-email">Email</label><input id="b-email" name="email" type="email" autocomplete="email" value="'+esc(lead.email||'')+'"></div>'
      +'<button class="btn" type="submit" id="inqBtn">Request a showing</button><p class="ok msg" role="status"></p>'
      +'<p class="fine">By sending, I agree to be contacted by RE/MAX Premier The OP Team by call, text and email. To opt out, reply STOP or click unsubscribe.</p></form>'
      +'<p class="alt">Listed by '+esc(l.office||'the listing brokerage')+'. Michael can show you any home on MLS®, whoever lists it.</p></div></aside>';
    h+='</div></div>';
    h+='<section class="similar" aria-labelledby="s-h"><div class="wrap"><h2 id="s-h">Similar homes nearby</h2><div class="grid3" id="similar"></div></div></section>';
    if(N)h+='<dialog id="dlg" aria-labelledby="dlg-h"><div class="dlg-head"><h2 id="dlg-h">All '+N+' photos</h2><button class="btn ghost" type="button" id="closeAll">Close</button></div><div class="all" id="all">'+all+'</div></dialog>';
    root.innerHTML=h;
    wire(l,P);
  }

  function wire(l,P){
    var N=P.length, cur=0;
    if(N){
      var S=[].slice.call(document.getElementById('slides').children), rail=document.getElementById('rail'), T=[].slice.call(rail.querySelectorAll('button'));
      var cap=document.getElementById('cap'), n=document.getElementById('n'), stage=document.getElementById('stage');
      var go=function(i){
        i=(i+N)%N;if(i===cur)return;
        S[cur].classList.remove('on');S[cur].setAttribute('aria-hidden','true');T[cur].removeAttribute('aria-current');
        cur=i;S[cur].classList.add('on');S[cur].removeAttribute('aria-hidden');T[cur].setAttribute('aria-current','true');
        n.textContent=cur+1;cap.textContent=P[cur].c||'';
        var b=T[cur],r=rail.getBoundingClientRect(),br=b.getBoundingClientRect();
        if(br.left<r.left+40||br.right>r.right-40)rail.scrollLeft+=br.left-r.left-(r.width-br.width)/2;
      };
      cap.textContent=P[0].c||'';
      if(N>1){document.getElementById('prev').onclick=function(){go(cur-1);};document.getElementById('next').onclick=function(){go(cur+1);};}
      rail.addEventListener('click',function(e){var b=e.target.closest('button');if(b)go(+b.dataset.i);});
      stage.addEventListener('keydown',function(e){if(e.key==='ArrowLeft'){go(cur-1);e.preventDefault();}if(e.key==='ArrowRight'){go(cur+1);e.preventDefault();}});
      var x0=null;
      stage.addEventListener('touchstart',function(e){x0=e.touches[0].clientX;},{passive:true});
      stage.addEventListener('touchend',function(e){if(x0===null)return;var dx=e.changedTouches[0].clientX-x0;if(Math.abs(dx)>40)go(cur+(dx<0?1:-1));x0=null;});
      var dlg=document.getElementById('dlg');
      document.getElementById('openAll').onclick=function(){if(dlg.showModal)dlg.showModal();};
      document.getElementById('closeAll').onclick=function(){dlg.close();};
      document.getElementById('all').addEventListener('click',function(e){var b=e.target.closest('button');if(!b)return;dlg.close();go(+b.dataset.i);stage.scrollIntoView({behavior:'smooth',block:'start'});stage.focus({preventScroll:true});});
    }
    // detail tabs
    var tabs=[].slice.call(root.querySelectorAll('.tabs [role=tab]'));
    tabs.forEach(function(t){t.addEventListener('click',function(){tabs.forEach(function(x){var on=x===t;x.setAttribute('aria-selected',on);document.getElementById(x.getAttribute('aria-controls')).hidden=!on;});});});
    // map
    if(l.lat!=null&&window.L){
      var m=L.map('lmap',{scrollWheelZoom:false,zoomControl:true}).setView([l.lat,l.lng],l.addr?15:13);
      L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png',{maxZoom:18,attribution:'&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'}).addTo(m);
      if(l.addr)L.marker([l.lat,l.lng],{icon:L.divIcon({className:'pin solo',html:'<span>'+esc(SM.priceText(l))+'</span>',iconSize:null})}).addTo(m);
      else L.circle([l.lat,l.lng],{radius:700,color:'#1D2870',weight:2,fillOpacity:.08}).addTo(m);
    }
    // payment calculator
    var f=document.getElementById('calc');
    if(f){
      var num=function(s){return parseFloat(String(s).replace(/[^0-9.]/g,''))||0;};
      var calc=function(){var P0=num(f['c-price'].value)*(1-num(f['c-down'].value)/100),r=num(f['c-rate'].value)/100,mo=num(f['c-am'].value)*12;var i=Math.pow(1+r/2,1/6)-1,pay=i?P0*i/(1-Math.pow(1+i,-mo)):P0/mo;document.getElementById('c-out').textContent='$'+Math.round(pay).toLocaleString('en-CA');};
      f.addEventListener('input',calc);f.addEventListener('submit',function(e){e.preventDefault();});calc();
    }
    // showing days: next 8 days
    var days=document.getElementById('days'),dn=['Sun','Mon','Tue','Wed','Thu','Fri','Sat'],mn=['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'],dh='';
    for(var k=1;k<=8;k++){var dt=new Date();dt.setDate(dt.getDate()+k);dh+='<button type="button" aria-pressed="'+(k===1)+'" data-day="'+dn[dt.getDay()]+' '+mn[dt.getMonth()]+' '+dt.getDate()+'"><small>'+dn[dt.getDay()]+'</small><b>'+dt.getDate()+'</b><small>'+mn[dt.getMonth()]+'</small></button>';}
    days.innerHTML=dh;
    days.addEventListener('click',function(e){var b=e.target.closest('button');if(!b)return;[].forEach.call(days.children,function(x){x.setAttribute('aria-pressed',x===b);});});
    // showing / ask tabs
    var form=document.getElementById('inq'), btn=document.getElementById('inqBtn'), msg=form.querySelector('.msg');
    var at=[].slice.call(root.querySelectorAll('.atabs button'));
    at.forEach(function(b){b.addEventListener('click',function(){
      var k=b.dataset.k;form.dataset.kind=k;at.forEach(function(x){x.setAttribute('aria-selected',x===b);});
      [].forEach.call(form.querySelectorAll('.only-showing'),function(x){x.hidden=k!=='showing';});
      [].forEach.call(form.querySelectorAll('.only-ask'),function(x){x.hidden=k!=='ask';});
      btn.textContent=k==='showing'?'Request a showing':'Send my question';
    });});
    if(location.hash==='#ask')at[1].click();
    form.addEventListener('submit',function(e){
      e.preventDefault();
      var name=form.elements.name.value.trim(),parts=name.split(/\s+/),email=form.elements.email.value.trim(),phone=form.elements.phone.value.trim();
      if(!name||(!email&&!phone)){msg.className='ok msg err';msg.textContent='Add your name and an email or phone number so Michael can reply.';return;}
      var kind=form.dataset.kind, day=(days.querySelector('[aria-pressed=true]')||{}).dataset;
      var body={id:id,kind:kind,firstName:parts[0],lastName:parts.slice(1).join(' '),email:email,phone:phone};
      if(kind==='showing'){body.day=day&&day.day;body.time=form.elements.time.value;}else body.message=form.elements.message.value;
      btn.disabled=true;var t=btn.textContent;btn.textContent='Sending…';
      SM.post('/api/inquiry',body).then(function(r){
        if(!r.ok)throw 0;
        SM.store('sm_lead',{firstName:body.firstName,lastName:body.lastName,email:email,phone:phone});
        var done=kind==='showing'?'Sent. Michael will confirm your showing time.':'Sent. Michael will get back to you about this home.';
        msg.className='ok msg';msg.textContent=done;btn.textContent=t;btn.disabled=false;
        if(window.smSent)window.smSent(done);
      }).catch(function(){msg.className='ok msg err';msg.textContent='That did not go through. Call or text Michael at 647-694-3109.';btn.textContent=t;btn.disabled=false;});
    });
    // similar homes nearby: same type and sale/rent, close by
    var sim=document.getElementById('similar');
    if(l.lat!=null){
      SM.loading(sim,3);
      var bb=[l.lat-.03,l.lng-.045,l.lat+.03,l.lng+.045].map(function(v){return v.toFixed(3);}).join(',');
      var tp={'Apartment':'condo'}[l.type];
      SM.get('/api/search?bbox='+bb+(l.lease?'&lease=1':'')+(tp?'&type='+tp:'')).then(function(r){
        var items=r.items.filter(function(x){return x.id!==l.id;}).slice(0,3);
        if(items.length)SM.cards(sim,items);else sim.closest('.similar').remove();
      }).catch(function(){sim.closest('.similar').remove();});
    }else sim.closest('.similar').remove();
  }
})();
