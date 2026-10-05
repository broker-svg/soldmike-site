/* /listings/ search: filters + results (max 100 per search) + map. Needs listings.js and Leaflet. */
(function(){
  var SM=window.SM, esc=SM.esc;
  var form=document.getElementById('lsForm'), list=document.getElementById('lsList'), info=document.getElementById('lsInfo'), more=document.getElementById('lsMore');
  var mapEl=document.getElementById('lsMap'), areaBtn=document.getElementById('lsArea'), wrap=document.getElementById('lsWrap');
  var FIELDS=['q','area','lease','type','min','max','beds','baths','sort','mine','brk','team'];
  var state={page:0,items:[],bbox:''}, map=null, layer=null, auto=true;

  // filters <-> URL
  var qs=new URLSearchParams(location.search);
  FIELDS.forEach(function(f){if(qs.get(f)!=null&&form.elements[f])form.elements[f].value=qs.get(f);});
  if(qs.get('bbox'))state.bbox=qs.get('bbox');
  function params(){
    var p=new URLSearchParams();
    FIELDS.forEach(function(f){var v=form.elements[f]&&form.elements[f].value;if(v)p.set(f,v);});
    if(state.bbox)p.set('bbox',state.bbox);
    return p;
  }

  function run(reset){
    if(reset){state.page=0;state.items=[];SM.loading(list,6);}
    var p=params();
    history.replaceState(null,'','?'+p.toString());
    p.set('page',state.page);
    more.hidden=true;
    SM.get('/api/search?'+p.toString()).then(function(r){
      state.items=state.items.concat(r.items);
      SM.cards(list,state.items,list.dataset.empty||'No homes match these filters. Try a wider price range or another area.');
      var shown=state.items.length;
      info.innerHTML=r.total?('<b>'+(r.capped?'1,000+':r.total.toLocaleString('en-CA'))+'</b> '+(r.total===1?'home':'homes')+(r.total>100?' · showing the first '+Math.min(100,r.total)+'. Narrow your search to see the rest.':'')):'';
      more.hidden=!(shown<r.shown);
      if(reset){if(r.pins)drawPins(r.pins);else pins();}
    }).catch(function(s){
      list.innerHTML='<p class="empty">'+(s===403?'Too many searches in a row. Please wait a minute and try again.':'Search is not responding right now. Please try again shortly, or call Michael at 647-694-3109.')+'</p>';
    });
  }
  form.addEventListener('submit',function(e){e.preventDefault();state.bbox='';var q=form.elements.q;if(q)q.blur();run(true);});
  form.addEventListener('change',function(e){if(e.target.name==='q')return;if(e.target.name==='area')state.bbox='';run(true);});
  more.addEventListener('click',function(){state.page++;run(false);});

  // ---------- map (Leaflet + OpenStreetMap), pins = the same first 100 results ----------
  function short(n,lease){if(lease)return '$'+Math.round(n).toLocaleString('en-CA');return n>=1e6?'$'+(n/1e6).toFixed(n>=1e7?0:2).replace(/\.?0+$/,'')+'M':'$'+Math.round(n/1e3)+'K';}
  function initMap(){
    if(map||!window.L)return;
    map=L.map(mapEl,{scrollWheelZoom:false,zoomControl:true}).setView([43.84,-79.55],10);
    L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png',{maxZoom:18,attribution:'&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'}).addTo(map);
    layer=L.layerGroup().addTo(map);
    // only show "Search this map area" after the visitor moves the map, not when we zoom to the results
    map.on('moveend',function(){if(!auto)areaBtn.hidden=false;});
    setTimeout(function(){auto=false;},1200);
    if(lastPins)drawPins(lastPins);else pins();
  }
  var lastPins=null;
  function pins(){
    if(!map)return;
    SM.get('/api/pins?'+params().toString()).then(function(r){drawPins(r.pins);}).catch(function(){});
  }
  function drawPins(list){
    lastPins=list;
    if(!map)return;
    (function(r){
      layer.clearLayers();
      var b=[];
      r.pins.forEach(function(x){
        var m=L.marker([x.lat,x.lng],{icon:L.divIcon({className:'pin'+(x.mine?' mine':''),html:'<span>'+short(x.price,x.forlease)+'</span>',iconSize:null})});
        m.on('click',function(){
          SM.get('/api/cards?ids='+encodeURIComponent(x.key)).then(function(c){if(c.items[0])m.bindPopup('<div class="popc">'+SM.card(c.items[0])+'</div>',{maxWidth:280,minWidth:260}).openPopup();});
        });
        m.addTo(layer);b.push([x.lat,x.lng]);
      });
      auto=true;
      if(b.length&&!state.bbox)map.fitBounds(b,{padding:[30,30],maxZoom:14});
      setTimeout(function(){auto=false;},1200);
      areaBtn.hidden=true;
    })({pins:list});
  }
  areaBtn.addEventListener('click',function(){
    var b=map.getBounds();
    state.bbox=[b.getSouth(),b.getWest(),b.getNorth(),b.getEast()].map(function(v){return v.toFixed(3);}).join(',');
    form.elements.area.value='';run(true);
  });
  document.getElementById('lsClearArea').addEventListener('click',function(){state.bbox='';run(true);});

  // mobile: list / map toggle; desktop shows both
  var toggles=[].slice.call(document.querySelectorAll('[data-view]'));
  toggles.forEach(function(t){t.addEventListener('click',function(){
    var v=t.dataset.view;wrap.dataset.view=v;
    toggles.forEach(function(x){x.setAttribute('aria-pressed',x===t);});
    if(v==='map'){initMap();setTimeout(function(){map&&map.invalidateSize();},60);}
  });});
  var hide=document.getElementById('lsHide');
  if(hide){
    var setHide=function(on){wrap.classList.toggle('nomap',on);hide.textContent=on?'Show map':'Hide map';SM.store('sm_nomap',on);if(!on){initMap();setTimeout(function(){map&&map.invalidateSize();},60);}};
    hide.addEventListener('click',function(){setHide(!wrap.classList.contains('nomap'));});
    if(SM.store('sm_nomap')!==false)setHide(true); // map starts hidden; a visitor who opens it keeps it open
  }
  if(matchMedia('(min-width: 1100px)').matches&&!wrap.classList.contains('nomap'))initMap();

  run(true);
})();
