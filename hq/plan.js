/* Michael's workout + meal plan (from the 2nd Brain: Health & Fitness, Daily Routine).
   Shared by HQ (/hq/) and the Agent Desk Personal tab (/hq/agents/#personal). Change it here once. */
(function(){
  var EX={
    squat:['Squat','3 × 8','Brace, sit between the hips, knees track over toes.',3],
    bench:['Bench press','3 × 8','Shoulder blades pinched, bar to mid-chest.',3],
    dbpress:['Seated DB shoulder press','3 × 10','Ribs down, press straight up, no arch.',3],
    plank:['Plank','3 × 45 s','Squeeze glutes, straight line head to heel.',3],
    dead:['Deadlift (RDL or conventional)','3 × 6','Flat back, bar close, push the floor away.',3],
    pull:['Pull-ups / lat pulldown','3 × 8','Full hang, pull elbows to ribs.',3],
    row:['DB row','3 × 10 / side','Hand on bench, row to the hip, pause.',3],
    cable:['Cable rotation','3 × 12 / side','Turn from the hips, arms stay long (golf turn).',3],
    rdl:['Romanian deadlift','3 × 10','Soft knees, hips back until hamstrings stretch.',3],
    incline:['Incline press','3 × 8','30° bench, control the way down.',3],
    split:['Split squat / lunge','3 × 10 / side','Front knee over mid-foot, tall chest.',3],
    pallof:['Pallof press','3 × 12 / side','Press out and hold; don\'t let the cable turn you.',3],
    deadbug:['Dead bug','3 × 10 / side','Low back pressed into the floor.',3],
    sideplank:['Side plank','3 × 30 s / side','Hips high, straight line.',3],
    birddog:['Bird dog','3 × 10 / side','Reach long, no hip rotation.',3],
    bridge:['Glute bridge','3 × 12','Squeeze at the top for 2 s.',3],
    hipflex:['Hip flexor stretch','2 × 45 s / side','Tuck the pelvis, lean gently.',2]
  };
  // index = getDay() (0 Sunday)
  var WEEK=[
    {name:'Walk or golf',sub:'Active rest · Sunday meal prep',ex:[],free:'Walk 30–60 min or play a round. Then Sunday meal prep (see Today\'s menu).'},
    {name:'Day A · Push',sub:'Legs, chest, shoulders · ~45 min',ex:['squat','bench','dbpress','plank'],gym:1},
    {name:'Optional · Walk or range',sub:'Session 4 of 5 (optional)',ex:[],free:'30–45 min brisk walk or a bucket at the range, plus 10 min of stretching. Suggested by Claude to reach 4–5 sessions a week.'},
    {name:'Day B · Pull',sub:'Back day · ~45 min',ex:['dead','pull','row','cable'],gym:1},
    {name:'Optional · Core & mobility',sub:'20 min · session 5 of 5 (optional)',ex:['deadbug','sideplank','birddog','bridge','hipflex'],opt:1},
    {name:'Day C · Athletic / golf',sub:'Full body + rotation · ~45 min',ex:['rdl','incline','split','pallof'],gym:1},
    {name:'Walk or golf',sub:'Active rest',ex:[],free:'Walk 30–60 min or play golf.'}
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
  var PREP=['Batch cook 2 proteins','Portion meals for the week','Hard-boil eggs','Wash and prep greens','Shop: fish, meat, nuts, fruit, protein powder, veg'];
  window.HQPLAN={EX:EX,WEEK:WEEK,MEALS:MEALS,MEAL_LBL:MEAL_LBL,PREP:PREP};
})();
