/* Michael's workout + meal plan (from the 2nd Brain: Health & Fitness, Daily Routine).
   Shared by HQ (/hq/) and the Agent Desk Personal tab (/hq/agents/#personal). Change it here once.
   Oct 13 2026: Michael's update — daily minimum is 25 push-ups + a walk; gym 2–3 days a week focused on legs and back;
   grocery list for the week's menu; small moving figures that show each exercise. */
(function(){
  // key: [name, sets × reps, form cue, sets]
  var EX={
    squat:['Barbell squat','3 × 8','Brace, sit between the hips, knees track over toes.',3],
    goblet:['Goblet squat','3 × 10','Hold one dumbbell at the chest, elbows inside the knees, sit tall.',3],
    split:['Split squat / lunge','3 × 10 / side','Front knee over mid-foot, tall chest, back knee drops straight down.',3],
    bridge:['Glute bridge','3 × 12','Drive through the heels, squeeze at the top for 2 s.',3],
    dead:['Deadlift','3 × 6','Flat back, bar close to the shins, push the floor away.',3],
    rdl:['Romanian deadlift','3 × 10','Soft knees, hips back until the hamstrings stretch, bar stays close.',3],
    pull:['Pull-ups / lat pulldown','3 × 8','Full hang, pull elbows down to the ribs.',3],
    row:['One-arm DB row','3 × 10 / side','Hand on the bench, row to the hip, pause.',3],
    crow:['Seated cable row','3 × 12','Sit tall, pull the handle to the belly, squeeze the shoulder blades.',3],
    bench:['Bench press','3 × 8','Shoulder blades pinched, bar to mid-chest.',3],
    dbpress:['Seated DB shoulder press','3 × 10','Ribs down, press straight up, no arch.',3],
    incline:['Incline press','3 × 8','30° bench, control the way down.',3],
    cable:['Cable rotation','3 × 12 / side','Turn from the hips, arms stay long (golf turn).',3],
    pallof:['Pallof press','3 × 12 / side','Press out and hold; don\'t let the cable turn you.',3],
    plank:['Plank','3 × 45 s','Squeeze glutes, straight line head to heel.',3],
    deadbug:['Dead bug','3 × 10 / side','Low back pressed into the floor.',3],
    sideplank:['Side plank','3 × 30 s / side','Hips high, straight line.',3],
    birddog:['Bird dog','3 × 10 / side','Reach long, no hip rotation.',3],
    hipflex:['Hip flexor stretch','2 × 45 s / side','Tuck the pelvis, lean gently.',2],
    dbinc:['Incline DB press','3 × 10','30° bench, press up and slightly in, control down.',3],
    fly:['DB chest fly','3 × 12','Soft elbows, open wide until the chest stretches, hug back up.',3],
    dips:['Dips (or bench dips)','3 × 8–10','Lean slightly forward, lower until elbows hit 90°.',3],
    lateral:['Lateral raise','3 × 12','Light weight, lead with the elbows, stop at shoulder height.',3],
    reardelt:['Rear-delt fly','3 × 12','Hinge forward, flat back, open the arms out wide.',3],
    facepull:['Face pull','3 × 15','Rope at face height, pull to the eyes, elbows high.',3],
    shrug:['DB shrug','3 × 12','Straight up to the ears, pause, slow down.',3],
    curl:['DB biceps curl','3 × 10','Elbows pinned to your sides, no swinging.',3],
    hammer:['Hammer curl','3 × 10','Thumbs up, curl straight up, slow down.',3],
    pushdown:['Triceps pushdown','3 × 12','Elbows locked at your sides, push down until arms are straight.',3],
    ohext:['Overhead triceps extension','3 × 12','Elbows point up, lower the DB behind the head, press up.',3]
  };
  // Every day, no matter what: these are the minimum
  var DAILY=[
    {k:'pushups',t:'25 push-ups',sub:'8:55 AM · in one go or 2 sets',fig:'pushup'},
    {k:'walk',t:'Walk 30 min',sub:'Any time · a round of golf counts',fig:'walk'}
  ];
  // Every workout in the system. Any of them can be done on any day (Agent Desk › Personal › All workouts).
  var ROUTINES={
    legs:{name:'Gym · Legs',sub:'Legs + core · ~45 min',ex:['squat','split','bridge','plank'],gym:1},
    back:{name:'Gym · Back',sub:'Back + shoulders · ~45 min',ex:['dead','pull','row','dbpress'],gym:1},
    full:{name:'Gym · Legs & back',sub:'Full body + golf turn · ~45 min',ex:['rdl','goblet','crow','bench','cable'],gym:1},
    chest:{name:'Gym · Chest',sub:'Chest + triceps · ~40 min',ex:['bench','dbinc','fly','dips'],gym:1},
    shoulders:{name:'Gym · Shoulders',sub:'Shoulders + traps · ~40 min',ex:['dbpress','lateral','reardelt','facepull','shrug'],gym:1},
    arms:{name:'Gym · Arms',sub:'Biceps + triceps · ~35 min',ex:['curl','hammer','pushdown','ohext','dips'],gym:1},
    core:{name:'Core & mobility',sub:'20 min at home',ex:['deadbug','sideplank','birddog','hipflex']}
  };
  var RORDER=['legs','back','full','chest','shoulders','arms','core'];
  function R(id,o){var r={id:id},k;for(k in ROUTINES[id])r[k]=ROUTINES[id][k];for(k in (o||{}))r[k]=o[k];return r;}
  // index = getDay() (0 Sunday). gym:1 = gym day, opt:1 = optional extra
  var WEEK=[
    {name:'Walk or golf',sub:'No gym · Sunday meal prep and groceries',ex:[],free:'Longer walk (45–60 min) or a round of golf, then the Sunday meal prep and grocery run.'},
    R('legs'),
    R('core',{sub:'Optional · 20 min at home',opt:1}),
    R('back'),
    {name:'Walk or range',sub:'No gym',ex:[],free:'Your walk, or a bucket at the range plus 10 min of stretching.'},
    R('full',{sub:'Optional 3rd gym day · full body + golf turn · ~45 min',opt:1}),
    {name:'Walk or golf',sub:'No gym',ex:[],free:'Walk 30–60 min or play a round.'}
  ];
  var MEALS=[ // per weekday 0..6: breakfast, lunch, pre-gym snack, dinner
    ['Protein pancakes + berries','Grilled chicken, brown rice, veg','Cottage cheese + fruit','Steak, roasted veg, small potato'],
    ['4–5 eggs, whole-grain toast, fruit, black coffee','Grilled chicken, brown rice, greens','Fage 2% + almonds','Salmon, roasted veg, small rice'],
    ['Greek yogurt 1–1.5 cups, berries, nuts','Roast turkey, gold potato, boiled egg, veg','Shake + banana','Chicken thighs, roasted veg'],
    ['Veggie omelette, toast, black coffee','Tuna wrap salad + croutons','Fage 2% + almonds','Steak or beef, roasted veg'],
    ['4–5 eggs, whole-grain toast, Greek yogurt','Chicken or turkey, sweet potato, greens','Cottage cheese + fruit','Lobster + shrimp, veg'],
    ['Protein shake + berries','Steak, rice, greens','Shake + banana','King crab + scallops, brown rice'],
    ['Shellfish omelette, toast','Tuna salad + croutons, fruit','Greek yogurt + nuts','Shellfish + pasta, salad']
  ];
  var MEAL_LBL=['Breakfast · 7–8 AM','Lunch · 12–1 PM','Pre-gym snack','Dinner'];
  var PREP=['Grocery run (list below the menu)','Batch cook 2 proteins','Portion meals for the week','Hard-boil eggs','Wash and prep greens'];
  // One week of the menu above. [aisle, [[item, amount, est. price CAD], …]]. Prices are rough GTA grocery averages (Oct 2026), not quotes.
  var GROCERY=[
    ['Meat & fish',[['Chicken breast','1.5 kg',33],['Chicken thighs','1 kg',15],['Sliced roast turkey','500 g',14],['Steak / lean beef','1.5 kg',45],['Salmon fillets','2',14],['Shrimp','450 g',14],['Lobster tails','2',30],['King crab legs','1 lb',45],['Scallops','450 g',25],['Mixed shellfish (omelette + pasta)','500 g',14],['Tuna, canned','4 cans',10]]],
    ['Dairy & eggs',[['Eggs','3 dozen',14],['Fage 2% Greek yogurt','2 × 1 kg',19],['Cottage cheese','2 tubs',12],['String cheese','1 pack',8]]],
    ['Fruit & veg',[['Berries (blue, rasp, black)','4 packs',20],['Bananas','1 bunch',2],['Fruit (apples, oranges)','6',6],['Spinach / salad greens','2 boxes',10],['Broccoli','2 heads',6],['Carrots','1 bag',3],['Mushrooms','1 box',3.5],['Onions','3',3],['Celery','1 bunch',3.5],['Peppers + zucchini (roasting)','4',8],['Sweet potatoes','3',4.5],['Gold potatoes, small','1 bag',6]]],
    ['Bread, rice & pantry',[['Whole-grain bread','1 loaf',5],['Whole-wheat wraps','1 pack',5],['Brown rice','1 bag',6],['Pasta','1 box',3],['Croutons','1 bag',4],['Protein pancake mix','1 box',12],['Olive oil + spices','top up',10],['Black coffee','top up',14]]],
    ['Nuts, seeds & snacks',[['Almonds','1 bag',12],['Mixed nuts (walnuts, cashews, pistachios)','1 bag',14],['Chia / flax / hemp seeds','top up',9],['Love Crunch granola','1 bag',8],['Protein bars (Quest or Built)','1 box',30]]],
    ['Supplements',[['Protein powder','check level',55]]]
  ];

  /* ---------- Exercise figures ----------
     Side-view stick figure, viewBox 0 0 120 100, floor at y 92. Each move = two poses (start → work), the figure
     loops between them. Joints: h head, s shoulder, e elbow, w hand, p hip, k knee, f foot; e2/w2/k2/f2 = far-side limbs.
     x: equipment at the hand (bar, db, kb), bench: [x, y, width], pb: pull-up bar height, cab: cable anchor [x, y]. */
  var STAND={h:[60,12],s:[60,22],e:[60,37],w:[60,51],p:[60,52],k:[60,72],f:[60,92]};
  function P(base,o){var r={},k;for(k in base)r[k]=base[k];for(k in o)r[k]=o[k];return r;}
  var FIG={
    squat:{x:'bar',a:P(STAND,{h:[63,11],e:[46,30],w:[52,22],k:[62,72]}),b:{h:[70,32],s:[64,42],e:[50,50],w:[56,42],p:[50,70],k:[74,73],f:[60,92]}},
    goblet:{x:'kb',a:P(STAND,{e:[62,38],w:[68,30]}),b:{h:[66,33],s:[62,42],e:[66,56],w:[72,48],p:[50,70],k:[74,73],f:[60,92]}},
    split:{x:'db',a:{h:[60,14],s:[60,24],e:[60,39],w:[60,53],p:[60,54],k:[70,73],f:[78,92],k2:[52,73],f2:[42,92]},
                  b:{h:[60,26],s:[60,36],e:[60,51],w:[60,65],p:[60,66],k:[79,68],f:[79,92],k2:[54,88],f2:[40,91]}},
    bridge:{a:{h:[20,84],s:[30,86],e:[42,90],w:[54,90],p:[58,88],k:[74,72],f:[84,92]},
            b:{h:[20,84],s:[30,86],e:[42,90],w:[54,90],p:[54,76],k:[76,68],f:[84,92]}},
    plank:{a:{h:[24,70],s:[34,76],e:[34,90],w:[46,90],p:[64,79],k:[80,84],f:[96,89]},
           b:{h:[24,71],s:[34,76],e:[34,90],w:[46,90],p:[64,77],k:[80,83],f:[96,89]}},
    dead:{x:'bar',a:{h:[72,32],s:[66,40],e:[65,60],w:[64,82],p:[50,62],k:[68,74],f:[60,92]},b:P(STAND,{e:[60,38],w:[60,55]})},
    rdl:{x:'bar',a:P(STAND,{e:[61,38],w:[62,55],k:[61,72]}),b:{h:[83,40],s:[74,44],e:[73,58],w:[71,73],p:[46,54],k:[58,73],f:[60,92]}},
    pull:{pb:14,a:{h:[64,33],s:[58,42],e:[59,28],w:[60,14],p:[58,68],k:[60,80],f:[57,92]},
                b:{h:[63,10],s:[58,20],e:[50,26],w:[60,14],p:[58,46],k:[60,58],f:[57,70]}},
    row:{x:'db',bench:[70,64,36],a:{h:[83,46],s:[74,50],e:[74,64],w:[74,78],p:[44,54],k:[44,73],f:[44,92],e2:[80,57],w2:[84,64]},
                                b:{h:[83,46],s:[74,50],e:[58,42],w:[60,56],p:[44,54],k:[44,73],f:[44,92],e2:[80,57],w2:[84,64]}},
    crow:{cab:[112,56],bench:[28,74,44],a:{h:[47,32],s:[46,42],e:[62,50],w:[78,56],p:[44,72],k:[64,60],f:[84,74]},
                                       b:{h:[45,32],s:[44,42],e:[32,52],w:[50,56],p:[44,72],k:[64,60],f:[84,74]}},
    bench:{x:'bar',bench:[18,70,62],a:{h:[22,62],s:[32,64],e:[33,50],w:[33,36],p:[62,66],k:[80,64],f:[82,92]},
                                     b:{h:[22,62],s:[32,64],e:[24,72],w:[38,56],p:[62,66],k:[80,64],f:[82,92]}},
    dbpress:{x:'db',bench:[40,72,40],a:{h:[60,30],s:[60,40],e:[50,40],w:[54,26],p:[60,70],k:[80,70],f:[80,92]},
                                     b:{h:[60,30],s:[60,40],e:[58,24],w:[60,8],p:[60,70],k:[80,70],f:[80,92]}},
    incline:{x:'bar',bench:[18,70,62],a:{h:[30,40],s:[36,48],e:[48,46],w:[56,40],p:[56,70],k:[76,66],f:[80,92]},
                                      b:{h:[30,40],s:[36,48],e:[50,32],w:[62,22],p:[56,70],k:[76,66],f:[80,92]}},
    cable:{cab:[6,38],a:{h:[60,15],s:[60,26],e:[48,34],w:[36,42],p:[60,54],k:[52,73],f:[48,92],k2:[68,73],f2:[72,92]},
                      b:{h:[60,15],s:[60,26],e:[72,33],w:[84,40],p:[60,54],k:[52,73],f:[48,92],k2:[68,73],f2:[72,92]}},
    pallof:{cab:[6,40],a:P(STAND,{e:[66,44],w:[70,38]}),b:P(STAND,{e:[76,38],w:[90,38]})},
    deadbug:{a:{h:[22,82],s:[32,86],e:[33,74],w:[34,60],p:[60,88],k:[60,70],f:[76,70],e2:[33,74],w2:[34,60],k2:[60,70],f2:[76,70]},
             b:{h:[22,82],s:[32,86],e:[20,82],w:[8,86],p:[60,88],k:[76,82],f:[94,86],e2:[33,74],w2:[34,60],k2:[60,70],f2:[76,70]}},
    sideplank:{a:{h:[26,60],s:[34,66],e:[34,90],w:[46,90],p:[62,80],k:[78,86],f:[94,90]},
               b:{h:[26,56],s:[34,64],e:[34,90],w:[46,90],p:[62,70],k:[78,80],f:[94,90]}},
    birddog:{a:{h:[83,60],s:[74,66],e:[74,78],w:[74,90],p:[46,66],k:[46,90],f:[28,90],e2:[74,78],w2:[74,90],k2:[46,90],f2:[28,90]},
             b:{h:[83,60],s:[74,66],e:[74,78],w:[74,90],p:[46,66],k:[46,90],f:[28,90],e2:[88,62],w2:[102,60],k2:[26,66],f2:[8,64]}},
    hipflex:{a:{h:[56,32],s:[56,42],e:[66,54],w:[58,66],p:[56,72],k:[78,70],f:[80,92],k2:[44,90],f2:[26,92]},
             b:{h:[61,34],s:[61,44],e:[71,56],w:[63,68],p:[61,75],k:[80,71],f:[80,92],k2:[44,90],f2:[26,92]}},
    pushup:{a:{h:[88,56],s:[80,60],e:[80,75],w:[80,90],p:[52,72],k:[36,79],f:[16,88]},
            b:{h:[89,79],s:[80,82],e:[70,80],w:[80,90],p:[52,85],k:[36,86],f:[16,88]}},
    dbinc:{x:'db',bench:[18,70,62],a:{h:[30,40],s:[36,48],e:[48,46],w:[56,40],p:[56,70],k:[76,66],f:[80,92]},
                                    b:{h:[30,40],s:[36,48],e:[50,32],w:[62,22],p:[56,70],k:[76,66],f:[80,92]}},
    fly:{x:'db',bench:[18,70,62],a:{h:[22,62],s:[32,64],e:[33,50],w:[33,36],p:[62,66],k:[80,64],f:[82,92]},
                                 b:{h:[22,62],s:[32,64],e:[42,54],w:[54,58],p:[62,66],k:[80,64],f:[82,92]}},
    dips:{dip:[50,74,52],a:{h:[61,12],s:[60,24],e:[60,38],w:[60,52],p:[58,54],k:[50,68],f:[60,78]},
                         b:{h:[61,26],s:[60,38],e:[48,44],w:[60,52],p:[58,68],k:[50,82],f:[60,90]}},
    lateral:{x:'db',solid:1,a:{h:[60,12],s:[60,22],e:[54,36],w:[52,50],p:[60,52],k:[56,72],f:[55,92],e2:[66,36],w2:[68,50],k2:[64,72],f2:[65,92]},
                             b:{h:[60,12],s:[60,22],e:[46,24],w:[32,24],p:[60,52],k:[56,72],f:[55,92],e2:[74,24],w2:[88,24],k2:[64,72],f2:[65,92]}},
    reardelt:{x:'db',a:{h:[83,40],s:[74,44],e:[74,57],w:[74,70],p:[46,54],k:[58,73],f:[60,92]},
                     b:{h:[83,40],s:[74,44],e:[73,33],w:[72,21],p:[46,54],k:[58,73],f:[60,92]}},
    facepull:{cab:[112,20],a:P(STAND,{h:[61,12],e:[73,22],w:[86,20]}),b:P(STAND,{h:[61,12],e:[50,18],w:[64,14]})},
    shrug:{x:'db',a:P(STAND,{s:[60,25],e:[65,38],w:[67,52]}),b:P(STAND,{s:[60,20],e:[65,33],w:[67,47]})},
    curl:{x:'db',a:P(STAND,{e:[65,36],w:[68,50]}),b:P(STAND,{e:[65,36],w:[76,27]})},
    pushdown:{cab:[82,4],a:P(STAND,{e:[65,36],w:[77,29]}),b:P(STAND,{e:[65,36],w:[69,50]})},
    ohext:{x:'db',a:P(STAND,{h:[62,12],e:[68,7],w:[56,14]}),b:P(STAND,{h:[62,12],e:[68,7],w:[73,-6]})},
    walk:{a:{h:[61,12],s:[60,22],e:[54,37],w:[50,50],p:[60,52],k:[68,72],f:[74,92],e2:[66,36],w2:[72,48],k2:[54,72],f2:[46,92]},
          b:{h:[61,12],s:[60,22],e:[66,36],w:[72,48],p:[60,52],k:[54,72],f:[46,92],e2:[54,37],w2:[50,50],k2:[68,72],f2:[74,92]}}
  };
  FIG.hammer=FIG.curl;
  var still=false;try{still=window.matchMedia('(prefers-reduced-motion: reduce)').matches;}catch(e){}
  // Returns an SVG string for an exercise key ('' when there is no figure). cls is added to the <svg>.
  function fig(key,cls){var F=FIG[key];if(!F)return '';var A=F.a,B=F.b,T='2.6s',o='';
    function an(attr,a,b){return (still||a===b)?'':'<animate attributeName="'+attr+'" values="'+a+';'+b+';'+a+'" keyTimes="0;.5;1" calcMode="spline" keySplines=".45 0 .55 1;.45 0 .55 1" dur="'+T+'" repeatCount="indefinite"/>';}
    function ln(j1,j2,c){var a1=A[j1],a2=A[j2],b1=B[j1]||a1,b2=B[j2]||a2;if(!a1||!a2)return '';
      return '<line x1="'+a1[0]+'" y1="'+a1[1]+'" x2="'+a2[0]+'" y2="'+a2[1]+'"'+(c?' class="'+c+'"':'')+'>'+an('x1',a1[0],b1[0])+an('y1',a1[1],b1[1])+an('x2',a2[0],b2[0])+an('y2',a2[1],b2[1])+'</line>';}
    function dot(j,r,c){var a=A[j],b=B[j]||a;return '<circle cx="'+a[0]+'" cy="'+a[1]+'" r="'+r+'" class="'+c+'">'+an('cx',a[0],b[0])+an('cy',a[1],b[1])+'</circle>';}
    if(!F.pb)o+='<line x1="4" y1="93" x2="116" y2="93" class="fl"/>';
    if(F.bench)o+='<rect x="'+F.bench[0]+'" y="'+F.bench[1]+'" width="'+F.bench[2]+'" height="5" rx="2" class="eq"/><line x1="'+(F.bench[0]+5)+'" y1="'+(F.bench[1]+5)+'" x2="'+(F.bench[0]+5)+'" y2="92" class="eqs"/><line x1="'+(F.bench[0]+F.bench[2]-5)+'" y1="'+(F.bench[1]+5)+'" x2="'+(F.bench[0]+F.bench[2]-5)+'" y2="92" class="eqs"/>';
    if(F.dip)o+='<line x1="'+F.dip[0]+'" y1="'+F.dip[2]+'" x2="'+F.dip[1]+'" y2="'+F.dip[2]+'" class="eqs" style="stroke-width:3"/><line x1="'+F.dip[1]+'" y1="'+F.dip[2]+'" x2="'+F.dip[1]+'" y2="92" class="eqs"/>';
    if(F.pb)o+='<line x1="34" y1="'+F.pb+'" x2="86" y2="'+F.pb+'" class="eqs" style="stroke-width:3"/>';
    if(F.cab){var w=A.w,wb=B.w;o+='<rect x="'+(F.cab[0]-3)+'" y="'+(F.cab[1]-5)+'" width="6" height="10" rx="1.5" class="eq"/><line x1="'+F.cab[0]+'" y1="'+F.cab[1]+'" x2="'+w[0]+'" y2="'+w[1]+'" class="cb">'+an('x2',w[0],wb[0])+an('y2',w[1],wb[1])+'</line>';}
    var fc=F.solid?'':'far';o+=ln('s','e2',fc)+ln('e2','w2',fc)+ln('p','k2',fc)+ln('k2','f2',fc);
    if(F.solid&&F.x==='db')o+=dot('w2',4,'pl');
    o+=ln('s','p')+ln('p','k')+ln('k','f')+ln('s','e')+ln('e','w')+dot('h',6.5,'hd');
    if(F.x==='bar')o+=dot('w',8,'pl');else if(F.x==='db')o+=dot('w',4,'pl');else if(F.x==='kb')o+=dot('w',5.5,'pl');
    return '<svg class="fig'+(cls?' '+cls:'')+'" viewBox="0 0 120 100" aria-hidden="true" focusable="false">'+o+'</svg>';}

  window.HQPLAN={EX:EX,DAILY:DAILY,ROUTINES:ROUTINES,RORDER:RORDER,WEEK:WEEK,MEALS:MEALS,MEAL_LBL:MEAL_LBL,PREP:PREP,GROCERY:GROCERY,FIG:FIG,fig:fig};
})();
