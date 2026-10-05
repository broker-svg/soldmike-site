#!/usr/bin/env python3
"""Builds the two free PDF guides (seller + buyer) in the site's navy/red/white look.
Run from the repo root: python3 tools/guides.py  ->  guides/selling-a-home-in-vaughan.pdf, guides/buying-a-home-in-vaughan.pdf
Needs Google Chrome (headless print to PDF)."""
import html, os, subprocess

e = html.escape
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'

# each step: (title, one-line summary, paragraphs, checklist, Michael's tip or '')
SELL = [
    ('Know your why', 'Your reason sets the timeline and the strategy.',
     ['Moving up, downsizing, relocating for work or settling an estate: each one changes how fast you need to sell, how you price and whether you buy or sell first.',
      'Before you call anyone, get clear on where you are going next and when you need to be there.'],
     ['Write down why you are selling', 'Pick your ideal move date and your latest possible date', 'Decide where you are moving and your budget for it', 'Talk to your lender about bridge financing if you might buy first'],
     'Most sellers are also buyers. Plan both moves together so you are never stuck paying for two homes or racing to find one.'),
    ('Interview realtors', 'Compare how each agent prices, markets and negotiates.',
     ['Meet two or three agents. The right one will show you real sales near you, a written marketing plan and how they handle offers.',
      'Ask how they will reach buyers, who shoots the photos and how often you will hear from them.'],
     ['What sold near me in the last 3 months, and for how much?', 'How would you price my home, and why?', 'Who does the photos, video and drone?', 'Offer date or offers any time, and why?', 'How often will you update me?'],
     ''),
    ('Price it right', 'Price from recent sales, not from what you need.',
     ['Buyers compare your home to every other listing and to what has sold nearby. Price it in line with the market and you draw the most buyers in the first two weeks, when interest is highest.',
      'An overpriced home sits, and a home that sits starts to look like something is wrong with it.'],
     ['Review sales from the last 3 to 6 months within your neighbourhood', 'Adjust for size, lot, finishes, basement and parking', 'Look at what is for sale now: that is your competition', 'Agree on a list price and an offer strategy together'],
     'The first two weeks bring the most showings. That is when pricing matters most.'),
    ('Know your net', 'See what you walk away with before you list.',
     ['Your net is the sale price minus your costs. In Ontario, sellers do not pay land transfer tax; the buyer does.',
      'Your main costs are real estate commission plus 13% HST on it, legal fees, your mortgage payout and any prepayment penalty, and moving costs.'],
     ['Get a mortgage payout statement and ask about any penalty', 'Get a quote from a real estate lawyer', 'Budget for repairs, staging and moving', 'Run your numbers in the cost-to-sell calculator at soldmike.com'],
     'Ask your lender about porting your mortgage to the next home. It can avoid a penalty.'),
    ('Prep your home', 'Small fixes buyers notice pay for themselves.',
     ['Buyers notice the little things: a dripping tap, a scuffed wall, a burnt-out bulb. Each one makes them wonder what else was not looked after.',
      'Fix what is easy, paint what needs it and clear out what you will not take with you.'],
     ['Fresh neutral paint where walls are marked or bold', 'Fix taps, doors, trim, caulking and light bulbs', 'Declutter: clear counters, closets and shelves', 'Deep clean, including windows and carpets', 'Tidy the front: lawn, garden, door and lights'],
     ''),
    ('Stage to sell', 'Help buyers picture living there.',
     ['Staging makes rooms look bigger, brighter and easier to live in, and it makes the photos work harder online.',
      'You do not need to stage every room. Focus on the living room, kitchen and primary bedroom.'],
     ['Remove extra furniture so rooms feel open', 'Put away family photos and personal items', 'Add simple touches: fresh towels, plants, neutral bedding', 'Consider professional staging for a vacant home'],
     'An empty home looks smaller in photos. Even a few staged pieces help buyers understand the space.'),
    ('Professional media', 'Most buyers see your home online first.',
     ['Your photos are your first showing. Every listing with us gets professional photos, drone, video, twilight shots and a floor plan from our own production team, Toronto Property Media.',
      'Good media brings more buyers through the door, and more buyers means more competition.'],
     ['Finish prep and staging before media day', 'Turn on every light and open the blinds', 'Hide cars, bins, cords and pet items', 'Clear bathroom and kitchen counters completely'],
     ''),
    ('Choose your strategy', 'Offer date or offers any time.',
     ['With an offer date, buyers have about a week to see the home, then everyone sends their offer at the same time. It works best when we expect several buyers.',
      'Taking offers any time works better when the market is slower or the home is one of a kind. We decide based on your home and the market that week.'],
     ['Look at how many similar homes are for sale', 'Watch showings and interest in the first days', 'Decide how you will handle an early bully offer', 'Agree on your must-haves: price, closing date, conditions'],
     ''),
    ('Launch the listing', 'Everything goes out on day one.',
     ['Your home goes live on the MLS® and REALTOR.ca, on our social media, to our buyer list and to the agent network, all at once.',
      'The first weekend sets the tone, so we make it count.'],
     ['Coming-soon posts before the MLS® launch', 'MLS® go-live with all photos and video', 'Email to our buyer list and agent network', 'First open house the first weekend'],
     ''),
    ('Showings and open houses', 'Keep it show-ready and listen to the feedback.',
     ['Showings are booked through our system, and we ask every agent for feedback afterward.',
      'Keep the home ready with little notice: beds made, counters clear, lights on.'],
     ['Lock away valuables, medication and personal papers', 'Plan where pets go during showings', 'Leave during showings so buyers feel at home', 'Read the feedback with us every few days'],
     ''),
    ('Review offers', 'Look past the top number.',
     ['An offer is more than a price. The deposit, conditions, closing date and what is included all matter.',
      'A slightly lower offer with no conditions and a strong deposit can be safer than the highest one.'],
     ['Price', 'Deposit amount', 'Conditions: financing, inspection, sale of their home', 'Closing date', 'Inclusions: appliances, light fixtures, window coverings'],
     ''),
    ('Negotiate and accept', 'Sign backs until the terms work for you.',
     ['If an offer is close but not right, we sign it back with changes. Each offer has an irrevocable time: a deadline for you to respond.',
      'As a Real Estate Negotiation Expert (RENE), Michael keeps the negotiation focused on what matters most to you.'],
     ['Know your lowest price and best closing date before offers come in', 'Respond before the irrevocable time', 'Get everything agreed in writing'],
     ''),
    ('Conditions come off', 'The deal goes firm.',
     ['Most offers have conditions, such as financing or a home inspection, each with a deadline, often about five business days.',
      'When the buyer waives or fulfils every condition, the deal is firm and the SOLD sign goes up.'],
     ['Give the inspector access when asked', 'Track each condition deadline with us', 'Send the firm deal to your lawyer right away'],
     ''),
    ('Lawyer and mortgage discharge', 'Your lawyer handles the closing.',
     ['Your lawyer gets the payout amount from your lender, pays off your mortgage from the sale proceeds and transfers the title to the buyer.',
      'Book your movers, and line up your utilities and insurance for the move.'],
     ['Send the firm agreement to your lawyer', 'Give your lawyer your lender details', 'Book movers for closing week', 'Arrange to cancel or move utilities and insurance'],
     ''),
    ('Closing day', 'Keys handed over, proceeds in hand.',
     ['On closing day the lawyers exchange the funds and documents and the deed registers in the buyer’s name.',
      'You leave the keys as agreed and your lawyer sends you the proceeds.'],
     ['Move out and leave the home clean', 'Leave keys, garage remotes and alarm codes', 'Leave appliance manuals and warranties', 'Take final meter readings'],
     'Congratulations. We will check in after you move to make sure everything went smoothly.'),
]

BUY = [
    ('Know your why', 'Your reason decides what to look for.',
     ['More space, a better school, a shorter commute, a first home: your reason tells us what to look for and what to skip.',
      'Write down your must-haves and your nice-to-haves before you start.'],
     ['Why are you moving?', 'When do you need to be in?', 'Your must-haves: bedrooms, area, schools, parking', 'Your nice-to-haves'],
     ''),
    ('Interview realtors', 'Find someone who works for you.',
     ['Meet two or three agents. Ask how they help buyers win in multiple offers and how they will keep you updated.',
      'In Ontario you sign a written buyer representation agreement with your agent, so understand it before you sign.'],
     ['How many buyers have you helped in this area?', 'How do you win in a bidding war?', 'How will you find homes before they hit the market?', 'How does your fee work?'],
     'Michael holds the ABR® designation, Accredited Buyer Representative, with training focused on buyers.'),
    ('Get pre-approved', 'Know your budget before you fall in love.',
     ['A lender checks your income, debts and credit and confirms how much you can borrow. Many will hold a rate for up to 120 days.',
      'Lenders also test whether you could afford payments at a higher rate (the stress test), so your budget may be lower than you expect.'],
     ['Gather pay stubs, tax returns and bank statements', 'Talk to a bank and a mortgage broker', 'Get your pre-approval in writing', 'Know your monthly comfort zone, not just the maximum'],
     ''),
    ('Know your closing costs', 'Budget for more than the down payment.',
     ['Plan for about 2% of the price on top of your down payment. Most of it is Ontario land transfer tax: about $22,500 on a $1.3 million home in Vaughan.',
      'In Toronto you also pay a municipal land transfer tax. First-time buyers can get up to $4,000 back from Ontario, plus up to $4,475 from Toronto.'],
     ['Land transfer tax', 'Legal fees and title insurance', 'Home inspection', 'Adjustments for prepaid property tax', 'Moving costs'],
     ''),
    ('Choose your neighbourhood', 'Compare before you fall for a house.',
     ['Prices, schools, commute and resale value can change street by street.',
      'Our neighbourhood guides at soldmike.com cover Woodbridge, Vellore, Kleinburg, Maple, King, Caledon, East Gwillimbury and Toronto.'],
     ['Drive the area at rush hour', 'Check school boundaries with the school board', 'Walk the street on a weekend', 'Ask what is planned nearby'],
     ''),
    ('Tour homes', 'Look past the staging.',
     ['See homes in person. Staging and photos are designed to impress, so look at the bones.',
      'Check the layout, light, roof, windows, furnace and air conditioner age, and any signs of water.'],
     ['Take photos and notes at every showing', 'Open closets and look under sinks', 'Ask the age of the roof, furnace and windows', 'Picture your furniture in each room'],
     ''),
    ('Check the value', 'Know what it is really worth.',
     ['Before you write an offer, we pull recent sales nearby so you know what the home is really worth.',
      'That number guides your offer, especially in a bidding war.'],
     ['Compare sales from the last 3 to 6 months', 'Adjust for size, lot, condition and parking', 'Decide your top price before offer night'],
     ''),
    ('Write the offer', 'Every term is a lever.',
     ['Your offer sets the price, deposit, conditions, closing date and what is included.',
      'In a competitive market, a clean offer with a strong deposit can beat a higher price with conditions.'],
     ['Price', 'Deposit: about 5% is common in the GTA', 'Conditions: financing, inspection, status certificate', 'Closing date', 'Inclusions'],
     ''),
    ('Negotiate', 'Win it at the right price.',
     ['One-on-one, we negotiate price and terms with the listing agent. In multiple offers, everyone sends their best offer and the seller chooses.',
      'As a Real Estate Negotiation Expert (RENE), Michael builds offers that stand out without overpaying.'],
     ['Know your walk-away price', 'Have your deposit ready', 'Be reachable on offer night'],
     ''),
    ('Submit your deposit', 'Usually within 24 hours.',
     ['Once your offer is accepted, your deposit goes to the listing brokerage, held in trust, usually within 24 hours.',
      'It counts toward your down payment on closing day.'],
     ['Have the funds ready before offer night', 'Use a bank draft or wire as instructed', 'Keep your receipt'],
     ''),
    ('Clear your conditions', 'Each condition has a deadline.',
     ['Common conditions are financing, a home inspection and, for condos, a review of the status certificate by your lawyer. Each has a deadline, often about five business days.',
      'If a condition is not met, you can walk away and get your deposit back.'],
     ['Send the deal to your lender right away', 'Book your home inspection', 'Get the status certificate to your lawyer for a condo', 'Waive conditions only when you are satisfied'],
     ''),
    ('Go firm', 'The home is yours, pending closing.',
     ['Once every condition is waived, the deal is firm. Resale homes in Ontario have no cooling-off period, so this is the point of no return.',
      'Now it is about getting to closing.'],
     ['Send the firm deal to your lawyer', 'Lock in your mortgage', 'Plan your move'],
     ''),
    ('Lawyer and insurance', 'Paperwork before the keys.',
     ['Your lawyer searches the title, arranges title insurance and prepares the closing documents.',
      'Your lender needs proof of home insurance before closing day.'],
     ['Hire a real estate lawyer', 'Get home insurance in place', 'Send the down payment and closing costs to your lawyer', 'Set up utilities for closing day'],
     ''),
    ('Final walkthrough', 'See it again before closing.',
     ['Most offers include visits before closing. Use the last one to check everything is as agreed.',
      'Make sure included items are there and nothing is damaged.'],
     ['Check appliances and included items', 'Run taps, test lights and the furnace', 'Note anything wrong and tell us right away'],
     ''),
    ('Closing day', 'Funds move, the deed registers, you get the keys.',
     ['On closing day your lawyer sends the funds, the deed registers in your name and you pick up the keys.',
      'Welcome home.'],
     ['Pick up keys as arranged with your lawyer', 'Change the locks and garage codes', 'Keep your closing documents somewhere safe'],
     'Congratulations. When you are ready to sell one day, we will be here.'),
]

CSS = '''
@page{size:Letter;margin:0}
*{box-sizing:border-box}
body{margin:0;font-family:Barlow,Arial,sans-serif;color:#141833;font-size:12.5pt;line-height:1.5;-webkit-print-color-adjust:exact;print-color-adjust:exact}
.page{width:8.5in;height:11in;position:relative;overflow:hidden;page-break-after:always;background:#fff}
.page:last-child{page-break-after:auto}
h1,h2,h3,.disp{font-family:'Barlow Condensed','Arial Narrow',sans-serif;text-transform:uppercase;margin:0;line-height:.95}
.cover{background:#1D2870;color:#fff;padding:.9in .8in}
.cover .photo{position:absolute;left:0;right:0;bottom:1.6in;height:4.6in;background-size:cover;background-position:center}
.cover .photo:before{content:'';position:absolute;inset:0;background:linear-gradient(#1D2870 0%,rgba(29,40,112,0) 45%)}
.cover .kick{font-family:'Barlow Condensed',sans-serif;font-weight:700;letter-spacing:.14em;color:#FF5A5F;font-size:16pt}
.cover h1{font-size:64pt;font-weight:800;margin:.25in 0 .3in}
.cover p{font-size:16pt;color:#C9D0F2;max-width:5.6in}
.cover .bar{position:absolute;left:0;right:0;bottom:0;height:1.6in;background:#fff;display:flex;align-items:center;justify-content:space-between;padding:0 .8in}
.cover .bar img{height:.95in}
.cover .bar span{font-size:11pt;color:#545B78;text-align:right}
.cover .line{width:1.2in;height:6px;background:#D7141E;margin-top:.35in}
.inner{padding:.75in .8in .9in}
.top{display:flex;justify-content:space-between;align-items:center;border-bottom:2px solid #1D2870;padding-bottom:.12in;margin-bottom:.3in;font-family:'Barlow Condensed',sans-serif;font-weight:700;letter-spacing:.08em;color:#1D2870;text-transform:uppercase;font-size:10.5pt}
.top b{color:#D7141E}
.step{margin-bottom:.4in}
.step .n{font-family:'Barlow Condensed',sans-serif;font-weight:700;color:#D7141E;letter-spacing:.12em;font-size:11pt}
.step h2{font-size:34pt;font-weight:800;color:#1D2870;margin:.03in 0 .04in}
.step .sum{font-size:14pt;font-weight:600;margin:0 0 .08in}
.step p{margin:0 0 .08in}
.step ul{list-style:none;padding:0;margin:.1in 0 0;display:grid;grid-template-columns:1fr 1fr;gap:.05in .25in}
.step li{padding-left:.28in;position:relative;font-size:11.5pt}
.step li:before{content:'';position:absolute;left:0;top:.04in;width:.15in;height:.15in;border:2px solid #1D2870;border-radius:2px}
.tip{background:#F2F4F9;border-left:5px solid #D7141E;padding:.1in .16in;margin-top:.12in;font-size:11.5pt}
.tip b{font-family:'Barlow Condensed',sans-serif;text-transform:uppercase;letter-spacing:.06em;color:#D7141E}
.notes h3{font-size:20pt;font-weight:800;color:#1D2870;margin:.15in 0 .1in}.notes .ln{border-bottom:1px solid #DCE0EC;height:.42in}
.foot{position:absolute;bottom:.4in;left:.8in;right:.8in;display:flex;justify-content:space-between;font-size:9.5pt;color:#545B78;border-top:1px solid #DCE0EC;padding-top:.08in}
.back{background:#1D2870;color:#fff;padding:.9in .8in}
.back h2{font-size:44pt;font-weight:800;margin-bottom:.2in}
.back p{font-size:15pt;color:#C9D0F2;max-width:6in}
.back .card{background:#fff;color:#141833;border-radius:6px;padding:.35in .4in;margin-top:.45in}
.back .card h3{font-size:26pt;font-weight:800;color:#1D2870}
.back .card .role{color:#545B78;margin:.04in 0 .18in}
.back .card .row{display:flex;gap:.35in;font-size:13pt;flex-wrap:wrap}
.back .card .row b{color:#D7141E;font-family:'Barlow Condensed',sans-serif;text-transform:uppercase;letter-spacing:.06em;display:block;font-size:10pt}
.desig{display:flex;gap:.3in;margin-top:.25in;align-items:center}
.desig img{height:.55in}
.cta{display:inline-block;margin-top:.4in;background:#D7141E;color:#fff;font-family:'Barlow Condensed',sans-serif;font-weight:700;font-size:18pt;text-transform:uppercase;padding:.14in .35in;border-radius:4px;text-decoration:none}
.fine{font-size:8.5pt;color:#C9D0F2;position:absolute;bottom:.4in;left:.8in;right:.8in}
'''

def doc(kind, steps):
    sell = kind == 'sell'
    title = 'Selling a home in Vaughan' if sell else 'Buying a home in Vaughan'
    other = 'BUYING' if not sell else 'SELLING'
    lede = ('The 15 steps from deciding to sell to handing over the keys, with a checklist for each one.' if sell
            else 'The 15 steps from deciding to buy to getting your keys, with a checklist for each one.')
    logo = 'file://' + os.path.join(ROOT, 'logo.png')
    pages = ['<section class="page cover"><div class="kick">FREE GUIDE · THE OP TEAM</div><h1>%s</h1><p>%s</p><div class="line"></div><div class="photo" style="background-image:url(%s)"></div>'
             '<div class="bar"><img src="%s" alt="RE/MAX Premier The OP Team"><span>Michael Barillari, Broker<br>RE/MAX Premier The OP Team<br>647-694-3109 · soldmike.com</span></div></section>' % (e(title), e(lede), 'file://' + os.path.join(ROOT, 'lp/1.jpg' if sell else 'l1.jpg'), logo)]
    per = 2
    for start in range(0, len(steps), per):
        body = ''
        for i, (t, sm, ps, cl, tip) in enumerate(steps[start:start + per], start + 1):
            body += ('<div class="step"><div class="n">STEP %d OF 15</div><h2>%s</h2><p class="sum">%s</p>%s<ul>%s</ul>%s</div>'
                     % (i, e(t), e(sm), ''.join('<p>%s</p>' % e(p) for p in ps), ''.join('<li>%s</li>' % e(c) for c in cl),
                        '<div class="tip"><b>Michael’s tip:</b> %s</div>' % e(tip) if tip else ''))
        pages.append('<section class="page"><div class="inner"><div class="top"><span>%s A HOME · <b>%s</b></span><span>SOLDMIKE.COM</span></div>%s</div>'
                     '<div class="foot"><span>Michael Barillari, Broker · RE/MAX Premier The OP Team</span><span>Call or text 647-694-3109</span></div></section>'
                     % (other, ('STEP %d' % (start + 1)) if start + 1 == min(start + per, 15) else 'STEPS %d\u2013%d' % (start + 1, min(start + per, 15)), body + ('<div class="notes"><h3>Your notes</h3>' + '<div class="ln"></div>' * 9 + '</div>' if start + per > 15 else '')))
    des = ''.join('<img src="file://%s" alt="">' % os.path.join(ROOT, 'assets/designations/%s-white.png' % d) for d in ('rene', 'srs', 'abr'))
    pages.append('<section class="page back"><h2>%s</h2><p>%s</p>'
                 '<div class="card"><h3>Michael Barillari</h3><div class="role">Broker · RE/MAX Premier The OP Team · Licensed since 2011</div>'
                 '<div class="row"><div><b>Call or text</b>647-694-3109</div><div><b>Email</b>mike@theopteam.ca</div><div><b>Web</b>soldmike.com</div></div>'
                 '<div class="row" style="margin-top:.15in"><div><b>Office</b>3550 Rutherford Rd, Unit 80, Vaughan, ON L4H 3T8</div></div></div>'
                 '<div class="desig">%s</div><a class="cta" href="https://soldmike.com/%s">%s</a>'
                 '<div class="fine">This guide is general information, not legal, tax or mortgage advice. Rules and rates change; confirm details with your lawyer, lender and accountant. Not intended to solicit buyers or sellers already under contract. RE/MAX Premier The OP Team Inc., Brokerage. Independently owned and operated.</div></section>'
                 % ('Ready when you are' if sell else 'Let’s find your home',
                    'Michael and The OP Team have more than 2,000 transactions of combined experience, with our own media team, Toronto Property Media, behind every listing.' if sell
                    else 'Michael helps buyers across Vaughan, Woodbridge, Kleinburg, King, Caledon and Toronto, in English and Italian.',
                    des, 'sell/home-value/' if sell else 'buy/', 'Get your free home value' if sell else 'Book a buyer consultation'))
    return ('<!doctype html><html lang="en-CA"><head><meta charset="utf-8"><title>%s | Free guide | SoldMike</title>'
            '<link href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@600;700;800&family=Barlow:wght@400;600&display=swap" rel="stylesheet"><style>%s</style></head><body>%s</body></html>'
            % (e(title), CSS, ''.join(pages)))

os.makedirs(os.path.join(ROOT, 'guides'), exist_ok=True)
for kind, steps, name in [('sell', SELL, 'selling-a-home-in-vaughan'), ('buy', BUY, 'buying-a-home-in-vaughan')]:
    src = os.path.join(ROOT, 'tools', name + '.html')
    open(src, 'w', encoding='utf-8').write(doc(kind, steps))
    out = os.path.join(ROOT, 'guides', name + '.pdf')
    subprocess.run([CHROME, '--headless=new', '--disable-gpu', '--no-pdf-header-footer', '--virtual-time-budget=8000',
                    '--print-to-pdf=' + out, 'file://' + src], check=True, capture_output=True)
    print(out, os.path.getsize(out))
