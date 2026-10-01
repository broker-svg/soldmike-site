#!/usr/bin/env python3
"""Builds every inner page of soldmike.com from the PAGES data below.
Run: python3 build.py   (writes <slug>/index.html, sitemap.xml, CONTENT-TODO.md)
Anything in todo() is content still to write; CONTENT-TODO.md lists them all."""
import json, os, html
from datetime import date

SITE = 'https://soldmike.com'
PHONE = '647-278-2237'
EMAIL = 'broker@soldmike.com'
ADDRESS = {'street': '3550 Rutherford Rd, Unit 80', 'city': 'Vaughan', 'region': 'ON', 'postal': 'L4H 3T8'}
BROKERAGE = 'RE/MAX Premier The OP Team Inc., Brokerage'
AREAS = ['Vaughan', 'Woodbridge', 'Kleinburg', 'Maple', 'Caledon', 'King', 'East Gwillimbury', 'Toronto']
TODOS = []
e = html.escape

# ---------- schema ----------
def agent_schema():
    return {
        '@context': 'https://schema.org', '@type': 'RealEstateAgent', '@id': SITE + '/#michael',
        'name': 'Michael Barillari', 'alternateName': 'SOLDMIKE', 'jobTitle': 'Broker',
        'description': 'Michael Barillari, Broker, SOLDMIKE. RE/MAX Premier The OP Team, Vaughan & Woodbridge.',
        'url': SITE, 'image': SITE + '/mike.png', 'logo': SITE + '/logo.png',
        'telephone': '+1-' + PHONE, 'email': EMAIL,
        'address': {'@type': 'PostalAddress', 'streetAddress': ADDRESS['street'], 'addressLocality': ADDRESS['city'],
                    'addressRegion': ADDRESS['region'], 'postalCode': ADDRESS['postal'], 'addressCountry': 'CA'},
        'areaServed': [{'@type': 'City', 'name': a} for a in AREAS],
        'parentOrganization': {'@type': 'RealEstateAgent', 'name': BROKERAGE},
        # TODO sameAs: Instagram, YouTube, LinkedIn, Google Business Profile, Realtor.ca profile URLs
    }

def crumbs_schema(trail):
    return {'@context': 'https://schema.org', '@type': 'BreadcrumbList', 'itemListElement': [
        {'@type': 'ListItem', 'position': i + 1, 'name': n, 'item': SITE + u} for i, (n, u) in enumerate(trail)]}

def faq_schema(qs):
    return {'@context': 'https://schema.org', '@type': 'FAQPage', 'mainEntity': [
        {'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': a}} for q, a in qs if not a.startswith('[')]}

# ---------- building blocks ----------
NAV = [
    ('Buy', [('/listings/', 'Search homes'), ('/buy/', 'Buying with us'), ('/buy/buyer-guide/', 'Buyer guide: 15 steps'), ('/buy/pre-construction/', 'Pre-construction'), ('/saved/', 'Saved homes & searches')]),
    ('Sell', [('/sell/home-value/', "What's my home worth?"), ('/sell/', 'Selling with us'), ('/sell/seller-guide/', 'Seller guide: 15 steps'), ('/sell/cost-to-sell-vaughan/', 'Cost to sell calculator'), ('/sell/how-we-market/', 'How we market your home')]),
    ('Neighbourhoods', [('/neighbourhoods/', 'All neighbourhoods')] + [('/neighbourhoods/%s/' % s, n) for s, n in [('woodbridge', 'Woodbridge'), ('vellore', 'Vellore Village'), ('kleinburg', 'Kleinburg'), ('maple', 'Maple'), ('caledon-bolton', 'Caledon & Bolton'), ('king-city-nobleton', 'King City & Nobleton'), ('sharon-east-gwillimbury', 'Sharon & East Gwillimbury'), ('toronto', 'Toronto')]]),
    ('Results', [('/results/', 'Recent sales'), ('/reviews/', 'Client reviews'), ('/market-reports/', 'Market reports')]),
    ('Questions', [('/questions/', 'All questions'), ('/questions/buying/', 'Buyer questions'), ('/questions/selling/', 'Seller questions')]),
    ('About', [('/about/', 'Michael Barillari'), ('/about/the-op-team/', 'The OP Team'), ('/videos/', 'Videos'), ('/join/', 'Join the team'), ('/contact/', 'Contact')]),
]

def header(path):
    out = []
    for label, items in NAV:
        cur = any(path.startswith(u) and u != '/' for u, _ in items)
        links = ''.join('<a href="%s"%s>%s</a>' % (u, ' aria-current="page"' if u == path else '', e(t)) for u, t in items)
        out.append('<div class="dd"><button type="button" aria-expanded="false"%s>%s</button><div class="menu">%s</div></div>'
                   % (' style="color:var(--red)"' if cur else '', label, links))
    return ('<a class="skip" href="#main">Skip to content</a>'
            '<header class="top"><div class="wrap"><a class="logo" href="/" aria-label="SoldMike home"><img src="/logo.png" alt="RE/MAX Premier The OP Team, SoldMike"></a>'
            '<button class="burger" type="button" aria-label="Menu" aria-expanded="false" aria-controls="nav"><span></span><span></span><span></span></button>'
            '<nav class="nav" id="nav" aria-label="Main">%s<a class="btn" href="/sell/home-value/">Home value</a></nav></div></header>') % ''.join(out)

def footer():
    cols = ''.join('<div><strong>%s</strong>%s</div>' % (l, ''.join('<a href="%s">%s</a>' % (u, e(t)) for u, t in items[:5])) for l, items in NAV[:4])
    return ('<footer><div class="wrap"><div class="fcols">'
            '<div><img src="/logo-white.png" alt="RE/MAX Premier The OP Team" style="width:220px;height:auto">'
            '<span>Michael Barillari, Broker, SOLDMIKE. %s Independently owned and operated.</span>'
            '<span>%s, %s, %s %s</span><span>Call or text %s</span><span>%s</span></div>%s</div>'
            '<div class="legal"><span>The trademarks REALTOR®, REALTORS®, and the REALTOR® logo are controlled by The Canadian Real Estate Association (CREA) and identify real estate professionals who are members of CREA. The trademarks MLS®, Multiple Listing Service® and the associated logos are owned by CREA. <a href="/privacy/" style="color:var(--pale)">Privacy</a> · <a href="/terms/" style="color:var(--pale)">Terms</a></span>'
            '<span class="badge">Powered by <strong>REALTOR.ca</strong></span></div></div></footer>'
            ) % (BROKERAGE, ADDRESS['street'], ADDRESS['city'], ADDRESS['region'], ADDRESS['postal'], PHONE, EMAIL, cols)

def hero(trail, h1, lede, photo=None):
    cr = '<nav class="crumbs" aria-label="Breadcrumb">' + ' / '.join(
        ('<a href="%s">%s</a>' % (u, e(n))) if i < len(trail) - 1 else '<span aria-current="page">%s</span>' % e(n)
        for i, (n, u) in enumerate(trail)) + '</nav>'
    bg = '<div class="bg" style="background-image:url(%s)" aria-hidden="true"></div>' % photo if photo else ''
    return '<section class="phero%s">%s<div class="wrap">%s<h1>%s</h1><p class="lede">%s</p></div></section>' % (' photo' if photo else '', bg, cr, e(h1), lede)

PAGE = None
def todo(*items):
    TODOS.append((PAGE, items))
    li = ''.join('<li>%s</li>' % e(i) for i in items)
    return '<div class="todo"><strong>Content to write</strong><ul>%s</ul></div>' % li

def band(inner, cls='', id=None, narrow=False):
    return '<section class="band %s"%s><div class="wrap%s">%s</div></section>' % (cls, ' id="%s"' % id if id else '', ' narrow' if narrow else '', inner)

def head_block(h2, p=None):
    return '<div class="head"><h2>%s</h2>%s</div>' % (e(h2), '<p>%s</p>' % p if p else '')

def prose(*ps):
    return '<div class="prose">%s</div>' % ''.join(p if p.startswith('<') else '<p>%s</p>' % p for p in ps)

def cards(items):
    return '<div class="cards">%s</div>' % ''.join('<a href="%s" class="rv"><b>%s</b><span>%s</span></a>' % (u, e(t), e(s)) for u, t, s in items)

def steps(items):
    return '<ol class="steps">%s</ol>' % ''.join('<li class="rv"><div><b>%s</b><p>%s</p></div></li>' % (e(t), e(d)) for t, d in items)

def kv(rows):
    return '<dl class="kv">%s</dl>' % ''.join('<div><dt>%s</dt><dd>%s</dd></div>' % (e(a), e(b)) for a, b in rows)

def faq(qs):
    out = ''
    for i, (q, a) in enumerate(qs):
        body = todo('Answer: ' + q) if a.startswith('[') else '<p>%s</p>' % a
        out += '<details%s><summary>%s<span class="plus" aria-hidden="true">+</span></summary><div class="a">%s</div></details>' % (' open' if i == 0 else '', e(q), body)
    return '<div class="faq">%s</div>' % out

FORMS = {
    'value': ('Home value request', 'Send me my home value', [('full', 'address', 'Property address', 'text', 'Street, city'), ('', 'name', 'Your name', 'text', ''), ('', 'phone', 'Phone', 'tel', ''), ('full', 'email', 'Email', 'email', ''), ('full', 'plan', "I'm planning to", ['Sell in the next 3 months', 'Sell in 3 to 12 months', 'Sell and buy', 'Just curious'], '')], 'Sent. Michael will send your price range with the comparable sales attached.'),
    'contact': ('Contact', 'Send message', [('', 'name', 'Your name', 'text', ''), ('', 'phone', 'Phone', 'tel', ''), ('full', 'email', 'Email', 'email', ''), ('full', 'topic', 'I want to', ['Buy a home', 'Sell a home', 'Buy and sell', 'Ask a question', 'Talk about joining the team'], ''), ('full', 'message', 'Message', 'area', '')], 'Sent. Michael will reply today.'),
    'buyer': ('Buyer consultation', 'Book a buyer consultation', [('', 'name', 'Your name', 'text', ''), ('', 'phone', 'Phone', 'tel', ''), ('full', 'email', 'Email', 'email', ''), ('', 'area', 'Area', ['Woodbridge', 'Vaughan', 'Kleinburg', 'King', 'Caledon', 'Toronto', 'Not sure yet'], ''), ('', 'budget', 'Budget', ['Under $1M', '$1M to $1.5M', '$1.5M to $2M', '$2M to $3M', '$3M+'], '')], 'Sent. Michael will call you to set up a time.'),
    'precon': ('Pre-construction list', 'Get the VIP list', [('', 'name', 'Your name', 'text', ''), ('', 'phone', 'Phone', 'tel', ''), ('full', 'email', 'Email', 'email', ''), ('full', 'type', 'Interested in', ['Condo', 'Townhome', 'Detached', 'Investment'], '')], "You're on the list. Michael will send new launches as they come up."),
    'guide': ('Free guide', 'Send me the guide', [('', 'name', 'Your name', 'text', ''), ('', 'email', 'Email', 'email', ''), ('full', 'which', 'Which guide', ['Selling in Vaughan', 'Buying your first home', 'Moving up to a bigger home'], '')], 'Sent. Check your inbox.'),
    'join': ('Join the team', "Let's talk", [('', 'name', 'Your name', 'text', ''), ('', 'phone', 'Phone', 'tel', ''), ('full', 'email', 'Email', 'email', ''), ('full', 'stage', 'Where are you at', ['Thinking about getting licensed', 'In the licensing courses', 'Newly licensed', 'Licensed and looking for a new team'], '')], 'Sent. Michael will reach out to set up a coffee.'),
    'report': ('Market report', 'Email me the monthly report', [('', 'name', 'Your name', 'text', ''), ('', 'email', 'Email', 'email', ''), ('full', 'area', 'Area', ['Vaughan', 'Woodbridge', 'Kleinburg', 'King', 'Caledon', 'East Gwillimbury'], '')], "Done. You'll get the next report on the 5th."),
}
def form(kind, uid=''):
    lead, btn, fields, done = FORMS[kind]
    out = ''
    for span, name, label, typ, ph in fields:
        fid = '%s-%s%s' % (kind, name, uid)
        cls = ' class="full"' if span else ''
        if isinstance(typ, list):
            ctl = '<select id="%s" name="%s" data-label="%s">%s</select>' % (fid, name, e(label), ''.join('<option>%s</option>' % e(o) for o in typ))
        elif typ == 'area':
            ctl = '<textarea id="%s" name="%s" data-label="%s"></textarea>' % (fid, name, e(label))
        else:
            auto = {'name': 'name', 'email': 'email', 'phone': 'tel'}.get(name, 'off')
            ctl = '<input id="%s" name="%s" type="%s" autocomplete="%s" data-label="%s"%s>' % (fid, name, typ, auto, e(label), ' placeholder="%s"' % e(ph) if ph else '')
        out += '<div%s><label for="%s">%s</label>%s</div>' % (cls, fid, e(label), ctl)
    return ('<form class="form" data-lead="%s" data-done="%s" aria-label="%s">%s<button class="btn full" type="submit">%s</button>'
            '<p class="msg full" role="status"></p><p class="fine full">Goes straight to Michael. No spam, and you can opt out any time.</p></form>') % (e(lead), e(done), e(lead), out, e(btn))

def cta(h, p, kind='value'):
    return '<section class="cta"><div class="wrap"><div><h2>%s</h2><p>%s</p></div>%s</div></section>' % (e(h), p, form(kind, '-cta'))

LISTINGS = [
    ('/listing.html', '/l1.jpg', '$1,649,000', 'Sample listing, Vellore Village', '4 bed · 4 bath · Detached', 'The OP Team', 'woodbridge'),
    ('/listing.html', '/l2.jpg', '$1,189,000', 'Sample listing, Islington Woods', '3 bed · 3 bath · Townhouse', '[Listing brokerage]', 'woodbridge'),
    ('/listing.html', '/l6.jpg', '$1,875,000', 'Sample listing, Sonoma Heights', '4 bed · 4 bath · Detached', 'The OP Team', 'woodbridge'),
    ('/listing.html', '/l4.jpg', '$3,295,000', '3 Westbrooke Lane, Nobleton', '5 bed · 6 bath · Detached', 'The OP Team', 'north'),
    ('/listing.html', '/l5.jpg', '$1,849,000', 'Sample listing, Tottenham', '4 bed · 4 bath · Detached', '[Listing brokerage]', 'north'),
    ('/listing.html', '/l3.jpg', '$1,399,000', 'Sample listing, Aurora', '3 bed · 3 bath · Detached', '[Listing brokerage]', 'north'),
]
def listing_grid(rows):
    return '<div class="grid3">%s</div>' % ''.join(
        '<a class="card rv" href="%s"><div class="ph"><img src="%s" alt="" loading="lazy"><span class="tag">Sample</span></div><div class="meta"><div class="price">%s</div><div class="addr">%s</div><div class="specs">%s</div><div class="fine"><span>Listed by: %s</span><span>MLS® [number]</span></div></div></a>'
        % (u, img, p, e(a), s, e(b)) for u, img, p, a, s, b, _ in rows)

# ---------- page writer ----------
SITEMAP = []
def page(path, title, desc, trail, body, schema=None, noindex=False):
    global PAGE
    sch = [agent_schema(), crumbs_schema(trail)] + (schema or [])
    doc = ('<!doctype html><html lang="en-CA"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">'
           '<title>%s</title><meta name="description" content="%s"><link rel="canonical" href="%s%s">'
           '<meta property="og:type" content="website"><meta property="og:title" content="%s"><meta property="og:description" content="%s"><meta property="og:url" content="%s%s"><meta property="og:image" content="%s/hero.jpg">'
           '%s<link rel="icon" href="/logo.png"><link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
           '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@500;600;700;800&family=Barlow:wght@400;500;600&display=swap">'
           '<link rel="stylesheet" href="/assets/site.css">%s</head><body>%s<main id="main">%s</main>%s<script src="/assets/site.js" defer></script></body></html>'
           ) % (e(title), e(desc), SITE, path, e(title), e(desc), SITE, path, SITE,
                '<meta name="robots" content="noindex">' if noindex else '',
                ''.join('<script type="application/ld+json">%s</script>' % json.dumps(s, ensure_ascii=False) for s in sch),
                header(path), body, footer())
    out = path.strip('/') + '/index.html' if path != '/' else 'index.html'
    os.makedirs(os.path.dirname(out) or '.', exist_ok=True)
    open(out, 'w', encoding='utf-8').write(doc)
    if not noindex: SITEMAP.append(path)

H = [('Home', '/')]
def P(path, *body_parts, title, desc, trail, schema=None, noindex=False):
    global PAGE
    PAGE = path
    body = ''.join(b() if callable(b) else b for b in body_parts)
    page(path, title, desc, H + trail, body, schema, noindex)

# =====================================================================
# BUY
# =====================================================================
PAGE = '/listings/'
P('/listings/',
  lambda: hero([('Home', '/'), ('Search homes', '/listings/')], 'Homes for sale in Vaughan & the GTA', 'Every MLS® listing, refreshed daily. Save the ones you like and get new matches by email.'),
  lambda: band(
    '<form class="filters" aria-label="Search listings" onsubmit="event.preventDefault()">'
    '<div><label for="f-area">Area</label><select id="f-area"><option>All areas</option><option>Woodbridge</option><option>Vellore</option><option>Kleinburg</option><option>Maple</option><option>King</option><option>Caledon</option><option>Toronto</option></select></div>'
    '<div><label for="f-type">Type</label><select id="f-type"><option>Any type</option><option>Detached</option><option>Semi-detached</option><option>Townhouse</option><option>Condo</option></select></div>'
    '<div><label for="f-min">Min price</label><select id="f-min"><option>No min</option><option>$750,000</option><option>$1,000,000</option><option>$1,500,000</option></select></div>'
    '<div><label for="f-max">Max price</label><select id="f-max"><option>No max</option><option>$1,500,000</option><option>$2,000,000</option><option>$3,000,000</option></select></div>'
    '<div><label for="f-beds">Bedrooms</label><select id="f-beds"><option>Any</option><option>2+</option><option>3+</option><option>4+</option><option>5+</option></select></div>'
    '<button class="btn" type="submit">Search</button></form>'
    '<div class="mapbox"><p class="note">Live map search turns on when the TRREB listing feed is connected. These are sample homes from our own shoots.</p></div>'
    + listing_grid(LISTINGS) +
    '<div style="display:flex;justify-content:space-between;align-items:center;gap:12px;margin-top:28px;flex-wrap:wrap"><a class="btn navy" href="/saved/">Save this search</a><span class="badge">Powered by <strong>REALTOR.ca</strong></span></div>'),
  title='Homes for Sale in Vaughan, Woodbridge & the GTA | SoldMike',
  desc='Search every MLS® listing in Vaughan, Woodbridge, Kleinburg, King, Caledon and Toronto. Save homes and get new listings by email.',
  trail=[('Search homes', '/listings/')])

P('/saved/',
  lambda: hero([('Home', '/'), ('Saved homes', '/saved/')], 'Your saved homes and searches', 'Create a free account to save homes, save searches and get new matches the morning they hit the market.'),
  lambda: band('<div class="two"><div class="prose"><p>With an account you can:</p><ul><li>Save homes and compare them side by side</li><li>Save a search and get new matches by email</li><li>See sold prices and price history (once registered, as TRREB requires)</li><li>Book a showing in two taps</li></ul>'
               + todo('Accounts, saved searches and alerts are built in phase 3, after the TRREB feed is approved. Until then this form adds the person to Follow Up Boss as a buyer.') +
               '</div>' + form('buyer') + '</div>'),
  title='Saved Homes & Searches | SoldMike', desc='Save homes and searches and get new MLS® listings by email.', trail=[('Saved homes', '/saved/')], noindex=True)

P('/buy/',
  lambda: hero([('Home', '/'), ('Buy', '/buy/')], 'Buying a home in Vaughan', 'How we help you find the right home, win it at the right price and get to closing day without surprises.', '/l1.jpg'),
  lambda: band(head_block('Where to start') + cards([
      ('/listings/', 'Search homes', 'Every MLS® listing, refreshed daily'),
      ('/buy/buyer-guide/', 'Buyer guide', 'The 15 steps from your why to closing day'),
      ('/neighbourhoods/', 'Neighbourhoods', 'Prices, schools and streets by community'),
      ('/buy/pre-construction/', 'Pre-construction', 'New launches and VIP pricing'),
      ('/questions/buying/', 'Buyer questions', 'Straight answers to what buyers ask us'),
  ])),
  lambda: band(head_block('Why buyers work with Michael') + todo(
      '3 to 4 short reasons buyers choose you (local knowledge, offer strategy, negotiation, TPM media for when they sell)',
      'One real buyer story: area, what they wanted, how you won it'), 'tint'),
  lambda: cta('Start with a 20-minute call', 'Tell us what you need, your budget and timing. We set up your search the same day.', 'buyer'),
  title='Buying a Home in Vaughan & Woodbridge | SoldMike', desc='How Michael Barillari and The OP Team help buyers in Vaughan, Woodbridge and the GTA find, win and close on the right home.',
  trail=[('Buy', '/buy/')])

BUY_STEPS = [
    ('Know your why', 'More space, a better school, a shorter commute. Your reason decides what to look for and what to skip.'),
    ('Interview realtors', 'Meet two or three agents. Ask how they price, how they win in multiple offers and how they communicate.'),
    ('Get pre-approved', 'A lender confirms what you can borrow and holds a rate. Sellers take pre-approved buyers more seriously.'),
    ('Know your closing costs', 'Plan for land transfer tax (double in Toronto), legal fees, title insurance and adjustments on top of the down payment.'),
    ('Choose your neighbourhood', 'Compare prices, schools, commute and resale value street by street before you fall for a house.'),
    ('Tour homes', 'See them in person. Look past the staging at layout, light, roof, windows and the furnace age.'),
    ('Check the value', 'We pull recent sales nearby so you know what the home is really worth before you write.'),
    ('Write the offer', 'Price, deposit, conditions and closing date. Each one is a lever in the negotiation.'),
    ('Negotiate', 'We work the price and terms with the listing agent, in a bidding war or one-on-one.'),
    ('Submit your deposit', 'Your deposit goes to the listing brokerage in trust, usually within 24 hours of acceptance.'),
    ('Clear your conditions', 'Financing, home inspection, status certificate for condos. Each one has a deadline.'),
    ('Go firm', 'Once conditions are waived the deal is firm. Now it is about getting to closing.'),
    ('Lawyer and insurance', 'Your lawyer searches title and prepares the closing. Home insurance has to be in place before closing day.'),
    ('Final walkthrough', 'See the home again before closing to confirm everything is as agreed.'),
    ('Closing day', 'Funds move through the lawyers, the deed registers, and you pick up the keys.'),
]
P('/buy/buyer-guide/',
  lambda: hero([('Home', '/'), ('Buy', '/buy/'), ('Buyer guide', '/buy/buyer-guide/')], 'Buying a home in Ontario: the 15 steps', 'The full process from deciding to buy to getting the keys, in the order it actually happens.'),
  lambda: band(steps(BUY_STEPS)),
  lambda: band(todo('Turn each step into its own short page or video (the Tuesday post series already has the 15 titles)', 'Add a downloadable PDF version as a lead magnet'), 'tint', narrow=True),
  lambda: cta('Questions about a step?', 'Michael answers buyers personally, usually the same day.', 'contact'),
  title='How to Buy a Home in Ontario: 15 Steps | SoldMike', desc='The 15 steps of buying a home in Vaughan and the GTA, from pre-approval and closing costs to offers, conditions and closing day.',
  trail=[('Buy', '/buy/'), ('Buyer guide', '/buy/buyer-guide/')],
  schema=[{'@context': 'https://schema.org', '@type': 'HowTo', 'name': 'How to buy a home in Ontario', 'step': [{'@type': 'HowToStep', 'position': i + 1, 'name': t, 'text': d} for i, (t, d) in enumerate(BUY_STEPS)]}])

P('/buy/pre-construction/',
  lambda: hero([('Home', '/'), ('Buy', '/buy/'), ('Pre-construction', '/buy/pre-construction/')], 'Pre-construction in Vaughan & York Region', 'New condos, towns and detached homes before they hit the public market, with VIP pricing and incentives.'),
  lambda: band('<div class="two"><div class="stack">' + prose(
      'Buying pre-construction means buying from a builder before the home is built, often years ahead of closing. The price is set today, deposits are spread out, and you choose finishes.',
      'It also comes with risks: closing delays, development charges, assignment rules and HST on new homes. We walk you through the agreement before you sign.') +
      todo('Current projects you can offer access to (name, builder, location, price from, deposit structure)', 'Your pre-construction track record or partnerships', 'Note: the 10-day cooling-off period for new condos in Ontario') +
      '</div>' + form('precon') + '</div>'),
  title='Pre-Construction Homes in Vaughan & York Region | SoldMike', desc='VIP access to new pre-construction condos, towns and detached homes in Vaughan and York Region.',
  trail=[('Buy', '/buy/'), ('Pre-construction', '/buy/pre-construction/')])

# =====================================================================
# SELL
# =====================================================================
P('/sell/',
  lambda: hero([('Home', '/'), ('Sell', '/sell/')], 'Selling your home with SoldMike', 'Pricing from real sales on your street, professional media from our own production team, and a launch plan built to bring in offers.', '/lp/1.jpg'),
  lambda: band(head_block('Start here') + cards([
      ('/sell/home-value/', "What's my home worth?", 'A price range from real recent sales near you'),
      ('/sell/seller-guide/', 'Seller guide', 'The 15 steps from your why to closing day'),
      ('/sell/cost-to-sell-vaughan/', 'Cost to sell', 'See what you walk away with'),
      ('/sell/how-we-market/', 'How we market', 'Photos, drone, video and twilight by Toronto Property Media'),
      ('/results/', 'Recent sales', 'What sold, how fast, and how we did it'),
  ])),
  lambda: band(head_block('Why sellers choose Michael') + todo(
      'Your selling numbers: average days on market and sale-to-list %, verified from MLS (RECO requires provable stats)',
      '3 short reasons sellers pick you: pricing, in-house media, offer strategy',
      'One seller quote with name and neighbourhood'), 'tint'),
  lambda: cta("What's your home worth today?", 'Tell us the address. Michael sends a price range based on real recent sales near you, no obligation.'),
  title='Sell Your Home in Vaughan & Woodbridge | SoldMike', desc='Sell your Vaughan or Woodbridge home with Michael Barillari: pricing from real sales, in-house photo, drone and video, and a launch plan built for offers.',
  trail=[('Sell', '/sell/')])

P('/sell/home-value/',
  lambda: hero([('Home', '/'), ('Sell', '/sell/'), ('Home value', '/sell/home-value/')], "What's my home worth?", 'A price range for your home based on what similar homes nearby actually sold for, sent with the comparables attached.'),
  lambda: band('<div class="two"><div class="stack">' + prose(
      '<h2>How we price it</h2>',
      'Online estimates guess from averages. We look at the homes that sold closest to yours in the last few months, then adjust for size, lot, finishes, basement and parking.',
      'You get a range, the sales we used, and what we would list at if you sold today. No obligation and no pressure to list.') +
      '</div>' + form('value') + '</div>'),
  lambda: band(head_block('Questions sellers ask first') + faq([
      ('How accurate is an online home value?', 'Often off by tens of thousands of dollars, because it cannot see inside your home or know which nearby sales are truly comparable. A local agent pricing from recent sales is more reliable.'),
      ('Does asking for a value commit me to anything?', 'No. You get the price range and the comparables. What you do with them is up to you.'),
      ('How long does it take?', '[Your real turnaround, for example same day or within 24 hours]'),
  ]), 'tint'),
  title="What's My Home Worth? Free Home Value in Vaughan | SoldMike", desc='Get a free price range for your Vaughan, Woodbridge or Kleinburg home, based on real recent sales near you.',
  trail=[('Sell', '/sell/'), ('Home value', '/sell/home-value/')],
  schema=[faq_schema([('How accurate is an online home value?', 'Often off by tens of thousands of dollars, because it cannot see inside your home or know which nearby sales are truly comparable. A local agent pricing from recent sales is more reliable.'), ('Does asking for a value commit me to anything?', 'No. You get the price range and the comparables. What you do with them is up to you.')])])

SELL_STEPS = [
    ('Know your why', 'Moving up, downsizing, relocating. Your reason sets the timeline and the strategy.'),
    ('Interview realtors', 'Compare how each agent prices, markets and negotiates. Ask to see their recent sales.'),
    ('Price it right', 'Price from recent sales nearby, not from what you need or what a neighbour hopes for.'),
    ('Know your net', 'Subtract commission, HST, legal fees and your mortgage payout to see what you walk away with.'),
    ('Prep your home', 'Repairs, paint, declutter. Small fixes buyers notice pay for themselves.'),
    ('Stage to sell', 'Staging helps buyers picture living there and makes the photos work harder.'),
    ('Professional media', 'Photos, drone, video and twilight shots. Most buyers see your home online first.'),
    ('Choose your strategy', 'Offer date or offers any time. The right choice depends on your home and the market that week.'),
    ('Launch the listing', 'MLS®, social media, email to our buyer list and the agent network, all on day one.'),
    ('Showings and open houses', 'Keep the home show-ready and get feedback from every showing.'),
    ('Review offers', 'We compare price, deposit, conditions and closing date, not just the top number.'),
    ('Negotiate and accept', 'Sign backs and counter offers until the terms work for you.'),
    ('Conditions come off', "The buyer's financing and inspection conditions are waived and the deal goes firm."),
    ('Lawyer and mortgage discharge', 'Your lawyer prepares the closing and pays out your mortgage from the sale proceeds.'),
    ('Closing day', 'Keys are handed over and your proceeds arrive from your lawyer.'),
]
P('/sell/seller-guide/',
  lambda: hero([('Home', '/'), ('Sell', '/sell/'), ('Seller guide', '/sell/seller-guide/')], 'Selling a home in Ontario: the 15 steps', 'Everything that happens between deciding to sell and handing over the keys, in order.'),
  lambda: band(steps(SELL_STEPS)),
  lambda: band(todo('Turn each step into its own short page or video (the Thursday post series already has the 15 titles)', 'Add a downloadable PDF version as a lead magnet'), 'tint', narrow=True),
  lambda: cta("Start with your home's value", 'Step 3 is pricing it right. We can do that for you this week.'),
  title='How to Sell a Home in Ontario: 15 Steps | SoldMike', desc='The 15 steps of selling a home in Vaughan and the GTA, from pricing and staging to offers, conditions and closing day.',
  trail=[('Sell', '/sell/'), ('Seller guide', '/sell/seller-guide/')],
  schema=[{'@context': 'https://schema.org', '@type': 'HowTo', 'name': 'How to sell a home in Ontario', 'step': [{'@type': 'HowToStep', 'position': i + 1, 'name': t, 'text': d} for i, (t, d) in enumerate(SELL_STEPS)]}])

COST_QS = [
    ('How much does it cost to sell a house in Vaughan?', 'The main costs are real estate commission plus 13% HST on that commission, legal fees, and paying out your mortgage, including any prepayment penalty. Sellers in Ontario do not pay land transfer tax; the buyer does.'),
    ('Do sellers pay land transfer tax in Ontario?', 'No. Land transfer tax is paid by the buyer. Sellers pay commission, HST on the commission, legal fees and any mortgage penalty.'),
    ('Is HST charged on real estate commission?', 'Yes. In Ontario, 13% HST is charged on the commission.'),
]
P('/sell/cost-to-sell-vaughan/',
  lambda: hero([('Home', '/'), ('Sell', '/sell/'), ('Cost to sell', '/sell/cost-to-sell-vaughan/')], 'What does it cost to sell a house in Vaughan?', 'Enter your numbers to see your costs and what you walk away with. Sellers in Ontario pay no land transfer tax.'),
  lambda: band('<form class="calc" id="costcalc" aria-label="Cost to sell calculator"><div class="form" style="grid-template-columns:1fr 1fr">'
               '<div class="full"><label for="k-price">Expected sale price</label><input id="k-price" inputmode="numeric" value="1,500,000"></div>'
               '<div><label for="k-com">Total commission (%)</label><input id="k-com" inputmode="decimal" value="4"></div>'
               '<div><label for="k-legal">Legal fees ($)</label><input id="k-legal" inputmode="numeric" value="1,500"></div>'
               '<div><label for="k-mort">Mortgage balance ($)</label><input id="k-mort" inputmode="numeric" value="600,000"></div>'
               '<div><label for="k-pen">Prepayment penalty ($)</label><input id="k-pen" inputmode="numeric" value="0"></div>'
               '<div class="full"><label for="k-other">Staging, repairs, moving ($)</label><input id="k-other" inputmode="numeric" value="5,000"></div>'
               '<p class="fine full">Commission is negotiable; enter the rate you agree to. Your lawyer and lender confirm the exact legal fee and penalty.</p></div>'
               '<div class="out" aria-live="polite"><div class="row"><span>Commission</span><span id="o-com"></span></div><div class="row"><span>HST on commission (13%)</span><span id="o-hst"></span></div>'
               '<div class="row"><span>Legal fees</span><span id="o-legal"></span></div><div class="row"><span>Mortgage payout and penalty</span><span id="o-mort"></span></div>'
               '<div class="row"><span>Staging, repairs, moving</span><span id="o-other"></span></div><small style="margin-top:12px">You walk away with</small><div class="net" id="o-net"></div></div></form>'),
  lambda: band(head_block('Cost to sell, answered') + faq(COST_QS), 'tint'),
  lambda: cta('Want the exact number?', 'Michael prices your home from real sales and runs your net with you before you list.'),
  title='Cost to Sell a House in Vaughan, Ontario (Calculator) | SoldMike', desc='Calculate the cost of selling a house in Vaughan: commission, HST, legal fees and mortgage payout, and see your net proceeds.',
  trail=[('Sell', '/sell/'), ('Cost to sell', '/sell/cost-to-sell-vaughan/')], schema=[faq_schema(COST_QS)])

P('/sell/how-we-market/',
  lambda: hero([('Home', '/'), ('Sell', '/sell/'), ('How we market', '/sell/how-we-market/')], 'How we market your home', 'Our own production company, Toronto Property Media, shoots every listing: photos, drone, video, twilight and floor plans.', '/l4.jpg'),
  lambda: band('<div class="grid3">%s</div>' % ''.join(
      '<figure class="card rv" style="margin:0"><div class="ph"><img src="%s" alt="%s" loading="lazy"></div><figcaption class="meta"><div class="addr">%s</div><div class="specs">%s</div></figcaption></figure>' % (i, e(a), e(t), e(d))
      for i, a, t, d in [('/lp/1.jpg', 'Front of a stone home at dusk', 'Twilight photos', 'The shot that stops the scroll'),
                         ('/lp/2.jpg', 'Aerial view of a street at dusk', 'Drone', 'The lot, the street and what is nearby'),
                         ('/lp/7.jpg', 'Bright white kitchen', 'Interiors', 'Wide, bright and true to the room'),
                         ('/hero.jpg', 'Aerial flyover of Woodbridge', 'Video', 'Cinematic tours for MLS®, YouTube and social'),
                         ('/lp/15.jpg', 'Covered patio', 'Lifestyle', 'Show how it feels to live there'),
                         ('/lp/12.jpg', 'Ensuite with freestanding tub', 'Details', 'The finishes buyers pay for')])),
  lambda: band(head_block('Your launch plan') + todo('Your real launch checklist: staging, media day, MLS® go-live, social, email to buyer list, agent network, open houses', 'Link one full listing video (YouTube)', 'Before/after staging example'), 'tint'),
  lambda: cta('See what your home could look like', "Get your home's value and a walk-through of our marketing plan."),
  title='How We Market Your Home: Photos, Drone & Video | SoldMike', desc='Every SoldMike listing gets professional photos, drone, video and twilight shots from Toronto Property Media.',
  trail=[('Sell', '/sell/'), ('How we market', '/sell/how-we-market/')])

# =====================================================================
# NEIGHBOURHOODS
# =====================================================================
HOODS = [
    ('woodbridge', 'Woodbridge', 'Woodbridge is a family-focused community in the City of Vaughan, known for its strong Italian-Canadian roots, the Humber River trails and quick access to Highways 400, 407 and 427.', '/hero.jpg', ['Vellore Village', 'Sonoma Heights', 'East Woodbridge', 'Elder Mills', 'Islington Woods', 'Woodbridge Core']),
    ('vellore', 'Vellore Village', 'Vellore Village is in northwest Woodbridge, in the City of Vaughan, made up mostly of newer family subdivisions with parks, schools and quick access to Highway 400.', '/l1.jpg', ['[Pocket 1]', '[Pocket 2]', '[Pocket 3]']),
    ('kleinburg', 'Kleinburg', 'Kleinburg is a historic village in the City of Vaughan set along the Humber River valley, home to the McMichael Canadian Art Collection, a walkable village core and large estate lots.', None, ['Village core', '[Estate area]', '[Newer subdivisions]']),
    ('maple', 'Maple', 'Maple is a community in the City of Vaughan with family neighbourhoods, Maple GO station on the Barrie line, and Canada’s Wonderland nearby.', None, ['[Pocket 1]', '[Pocket 2]', '[Pocket 3]']),
    ('caledon-bolton', 'Caledon & Bolton', 'Bolton is the largest community in the Town of Caledon, in Peel Region, offering newer subdivisions, a historic downtown and quick access to the countryside.', None, ['Bolton', '[Caledon East]', '[Country properties]']),
    ('king-city-nobleton', 'King City & Nobleton', 'King City and Nobleton are villages in the Township of King, north of Vaughan, known for estate homes, larger lots and quiet streets, with King City GO on the Barrie line.', '/lp/2.jpg', ['King City', 'Nobleton', '[Schomberg]']),
    ('sharon-east-gwillimbury', 'Sharon & East Gwillimbury', 'Sharon is a growing community in the Town of East Gwillimbury, York Region, home to the Sharon Temple National Historic Site and many newer family subdivisions.', None, ['Sharon', '[Queensville]', '[Holland Landing]']),
    ('toronto', 'Toronto', 'We help clients buy and sell condos and freehold homes across Toronto, from first condos downtown to family homes in the west end.', None, ['[Area 1]', '[Area 2]', '[Area 3]']),
]
P('/neighbourhoods/',
  lambda: hero([('Home', '/'), ('Neighbourhoods', '/neighbourhoods/')], 'Neighbourhood guides', "Prices, schools, streets and what's selling, one page per community.", '/aerial.jpg'),
  lambda: band(cards([('/neighbourhoods/%s/' % s, n, ', '.join(p for p in pk if not p.startswith('['))[:60] or 'Guide') for s, n, _, _, pk in HOODS])),
  lambda: cta('Not sure which area fits?', 'Tell us what matters most and we will shortlist the neighbourhoods for you.', 'buyer'),
  title='Vaughan & GTA Neighbourhood Guides | SoldMike', desc='Guides to Woodbridge, Vellore, Kleinburg, Maple, Caledon, King City, Nobleton, Sharon and Toronto: prices, schools and what is selling.',
  trail=[('Neighbourhoods', '/neighbourhoods/')])

for slug, name, intro, photo, pockets in HOODS:
    path = '/neighbourhoods/%s/' % slug
    qs = [('Is %s a good place to raise a family?' % name, '[Answer yes or no in the first sentence, then schools, parks and community.]'),
          ('How much is a detached home in %s?' % name, '[Price range in the first sentence, from recent sales.]'),
          ('How long does it take to sell a house in %s?' % name, '[Average days on market in the first sentence, then what speeds it up.]'),
          ('How do I get to downtown Toronto from %s?' % name, '[Drive and transit options in the first sentence.]')]
    P(path,
      lambda name=name, intro=intro, photo=photo, slug=slug: hero([('Home', '/'), ('Neighbourhoods', '/neighbourhoods/'), (name, '/neighbourhoods/%s/' % slug)], '%s homes for sale & market guide' % name, e(intro) + '<br><small style="color:var(--pale)">Written by Michael Barillari, Broker · Updated [month, year]</small>', photo),
      lambda name=name, pockets=pockets: band('<div class="two"><div class="stack"><h2>%s at a glance</h2>' % e(name) + kv([
          ('Average sold price, last 90 days', '[$X,XXX,XXX]'), ('Average days on market', '[X] days'), ('Homes for sale right now', '[Live count]'),
          ('Most common home type', '[Detached]'), ('Homes the OP Team has sold here', '[X]')]) +
          '</div><div class="stack"><h2>Pockets of %s</h2>' % e(name) + cards([('/listings/', p, '[One line on who it suits]') for p in pockets]) + '</div></div>'),
      lambda name=name: band(head_block('For sale in %s' % name) + listing_grid([l for l in LISTINGS][:3]) +
          '<div style="margin-top:24px;display:flex;justify-content:space-between;flex-wrap:wrap;gap:12px"><a href="/listings/" style="font-weight:600">See all %s listings</a><span class="badge">Powered by <strong>REALTOR.ca</strong></span></div>' % e(name), 'tint'),
      lambda name=name: band(head_block('Living in %s' % name) + todo('Schools (public, Catholic, French) and what they are known for', 'Parks, trails and community centres', 'Shopping, restaurants and places locals love', 'Commute: highways, GO, TTC/YRT', 'What is changing: new builds, transit, development') , narrow=True),
      lambda name=name, qs=qs: band(head_block('%s questions, answered' % name) + faq(qs), 'tint'),
      lambda name=name: cta('Own in %s? See what it is worth.' % name, 'A price range based on real sales on your street.'),
      title='%s Homes for Sale & Neighbourhood Guide | SoldMike' % name, desc=intro[:155],
      trail=[('Neighbourhoods', '/neighbourhoods/'), (name, path)],
      schema=[{'@context': 'https://schema.org', '@type': 'Place', 'name': name + ', Ontario', 'address': {'@type': 'PostalAddress', 'addressLocality': name.split(' & ')[0], 'addressRegion': 'ON', 'addressCountry': 'CA'}}])

# =====================================================================
# RESULTS
# =====================================================================
CASES = [
    ('226-via-borghese', '226 Via Borghese St', 'Vellore Village, Vaughan', '$1,790,000', '[X]', '[X]%'),
    ('49-walter-proctor', '49 Walter Proctor Rd', 'East Gwillimbury', '[$X,XXX,XXX]', '[X]', '[X]%'),
    ('179-lio-ave', '179 Lio Ave', 'Woodbridge', '[$X,XXX,XXX]', '[X]', '[X]%'),
]
P('/results/',
  lambda: hero([('Home', '/'), ('Results', '/results/')], 'Recent sales', 'What sold, how fast, and what we did to get it there.'),
  lambda: band('<div class="tbl"><table><thead><tr><th scope="col">Home</th><th scope="col">Area</th><th scope="col">Sold for</th><th scope="col">Days</th><th scope="col">Sale vs list</th><th scope="col"></th></tr></thead><tbody>' +
               ''.join('<tr class="rv"><td class="big">%s</td><td>%s</td><td class="sold">%s</td><td>%s</td><td>%s</td><td><a href="/results/%s/">Case study</a></td></tr>' % (e(a), e(ar), p, d, s, sl) for sl, a, ar, p, d, s in CASES) +
               '</tbody></table></div>' + '<div style="margin-top:24px">' + todo('Add every sale from the last 24 months with verified days on market and sale-to-list % (RECO: accurate and provable)', 'Sold data on the site likely needs the TRREB VOW feed; until then enter sales by hand') + '</div>'),
  lambda: cta('Want results like these?', 'It starts with pricing your home from real sales.'),
  title='Recent Home Sales in Vaughan & Woodbridge | SoldMike', desc='Homes sold by Michael Barillari and The OP Team in Vaughan, Woodbridge and York Region, with days on market and how we did it.',
  trail=[('Results', '/results/')])

for sl, a, ar, p, d, s in CASES:
    P('/results/%s/' % sl,
      lambda a=a, ar=ar, sl=sl, p=p: hero([('Home', '/'), ('Results', '/results/'), (a, '/results/%s/' % sl)], 'How we sold %s' % a, '%s · Sold for %s' % (e(ar), p)),
      lambda d=d, s=s, p=p, ar=ar: band('<div class="two"><div class="stack"><h2>The numbers</h2>' + kv([('Sold for', p), ('Days on market', d), ('Sale vs list', s), ('Area', ar), ('Property type', '[Detached]')]) + '</div><div class="stack"><h2>The story</h2>' +
          todo('The challenge (for example: listed before and did not sell, tough market, unique home)', 'What we did: pricing, staging, media, offer strategy', 'The result in one sentence, then a quote from the seller', '2 to 4 photos from the shoot') + '</div></div>'),
      lambda: cta('Selling a home like this?', 'Get a price range and the plan we would use.'),
      title='How We Sold %s, %s | SoldMike' % (a, ar), desc='Case study: how Michael Barillari sold %s in %s.' % (a, ar),
      trail=[('Results', '/results/'), (a, '/results/%s/' % sl)])

P('/reviews/',
  lambda: hero([('Home', '/'), ('Reviews', '/reviews/')], 'What clients say', 'Real reviews from buyers and sellers, in their words.'),
  lambda: band('<div class="grid3">' + ''.join('<figure class="rv" style="margin:0;padding-top:18px;border-top:3px solid var(--red);display:flex;flex-direction:column;gap:12px"><div style="color:var(--red);letter-spacing:3px" aria-label="5 stars">★★★★★</div><blockquote style="margin:0;font-size:19px">"[Real Google review %d: names Michael, the neighbourhood and what he did]"</blockquote><figcaption style="color:var(--muted);font-weight:600">[Client name], [Area]</figcaption></figure>' % i for i in range(1, 7)) + '</div><div style="margin-top:28px">' +
               todo('Paste in your best Google reviews word for word (real reviews only)', 'Google rating and review count for the schema markup', 'Link to your Google Business Profile reviews') + '</div>'),
  lambda: cta('Ready to be the next review?', 'Start with a free home value or a buyer consultation.'),
  title='Client Reviews | Michael Barillari, SoldMike', desc='Reviews of Michael Barillari, Broker, RE/MAX Premier The OP Team, from buyers and sellers in Vaughan and Woodbridge.',
  trail=[('Reviews', '/reviews/')])

P('/market-reports/',
  lambda: hero([('Home', '/'), ('Market reports', '/market-reports/')], 'Vaughan market reports', 'Every month on the 5th: what sold, for how much, how fast, and what it means for you.'),
  lambda: band('<div class="two"><div class="stack">' + cards([('/market-reports/vaughan-october-2026/', 'October 2026', 'Vaughan market report')]) +
               todo('Publish one report on the 5th of every month: average price, sales, new listings, days on market, sale-to-list, by area', 'Embed or link the matching YouTube market update') + '</div>' + form('report') + '</div>'),
  title='Vaughan Real Estate Market Reports | SoldMike', desc='Monthly Vaughan and Woodbridge real estate market reports: prices, sales, days on market and what it means for buyers and sellers.',
  trail=[('Market reports', '/market-reports/')])

P('/market-reports/vaughan-october-2026/',
  lambda: hero([('Home', '/'), ('Market reports', '/market-reports/'), ('October 2026', '/market-reports/vaughan-october-2026/')], 'Vaughan real estate market: October 2026', 'Published [October 5, 2026] by Michael Barillari, Broker.'),
  lambda: band('<div class="stack">' + kv([('Average sold price', '[$X,XXX,XXX]'), ('Change vs last year', '[X]%'), ('Homes sold', '[X]'), ('New listings', '[X]'), ('Average days on market', '[X]'), ('Average sale-to-list', '[X]%')]) +
               todo('Lead with the one-sentence answer: is it a buyer’s or seller’s market this month and why', 'Breakdown by Woodbridge, Kleinburg, Maple, Vellore', 'What it means for buyers / for sellers', 'Source: TRREB Market Watch') + '</div>', narrow=True),
  lambda: cta('What does this mean for your home?', 'Get a price range from this month’s sales.'),
  title='Vaughan Real Estate Market Report, October 2026 | SoldMike', desc='Vaughan real estate market update for October 2026: average price, sales, days on market and sale-to-list ratio.',
  trail=[('Market reports', '/market-reports/'), ('October 2026', '/market-reports/vaughan-october-2026/')],
  schema=[{'@context': 'https://schema.org', '@type': 'Article', 'headline': 'Vaughan real estate market: October 2026', 'author': {'@id': SITE + '/#michael'}}])

# =====================================================================
# QUESTIONS
# =====================================================================
BUY_QS = [
    ('How much do I need for a down payment in Ontario?', 'At least 5% of the first $500,000 and 10% of the portion between $500,000 and $1.5 million. Homes priced at $1.5 million or more need 20% down.'),
    ('What closing costs should buyers budget for?', 'Land transfer tax (plus the municipal tax in Toronto), legal fees, title insurance, adjustments for prepaid property tax, and home inspection. [Add a typical total for a Vaughan home.]'),
    ('Do first-time buyers get a land transfer tax rebate?', '[Answer in the first sentence: Ontario and Toronto first-time buyer rebates and their current maximums.]'),
    ('Should I buy first or sell first?', '[Answer in the first sentence, then the trade-offs.]'),
    ('How do bidding wars work in Ontario?', '[Answer in the first sentence: offer dates, registered offers, escalation not allowed, how to compete.]'),
    ('Is it better to buy pre-construction or resale?', '[Answer in the first sentence, then the trade-offs.]'),
    ('How long does it take to buy a house?', '[Answer in the first sentence: search time plus a typical 30 to 90 day closing.]'),
    ('Do I need a home inspection?', '[Answer in the first sentence, then when and how much.]'),
    ('What is a status certificate?', 'A package from a condo corporation showing its finances, reserve fund, rules and any lawsuits. Buyers usually make their offer conditional on their lawyer reviewing it.'),
    ('Does it cost me anything to use a buyer agent?', '[Answer in the first sentence: how buyer agent compensation works in Ontario today.]'),
]
SELL_QS = [
    ('How much is my Woodbridge home worth?', 'It depends most on what similar homes on nearby streets sold for in the last few months. We pull those sales and send you a price range with the comparables attached.'),
    ('When is the best time to sell in Vaughan?', '[Answer in the first sentence, then the reasoning, backed by local numbers.]'),
    ('What does it cost to sell a house in Ontario?', 'The main costs are real estate commission plus 13% HST on it, legal fees, and paying out your mortgage, including any penalty. Sellers do not pay land transfer tax.'),
    ('Should I stage my home?', '[Answer in the first sentence, then cost and what it changes.]'),
    ('Should I hold an offer date or take offers any time?', '[Answer in the first sentence, then when each works.]'),
    ('What renovations add the most value before selling?', '[Answer in the first sentence: paint, lighting, small repairs vs big renos.]'),
    ('How long does it take to sell a house in Vaughan?', '[Average days on market in the first sentence, from TRREB data.]'),
    ('Can I sell my house while I still have a mortgage?', 'Yes. Your lawyer pays out the mortgage from the sale proceeds on closing day. Ask your lender about any prepayment penalty first.'),
    ('What happens if my home does not sell?', '[Answer in the first sentence, then what we change: price, media, strategy.]'),
    ('Why choose a local Vaughan realtor?', '[Answer in the first sentence, then local results.]'),
]
P('/questions/',
  lambda: hero([('Home', '/'), ('Questions', '/questions/')], 'Questions buyers and sellers ask us', 'Straight answers, with the answer in the first sentence.'),
  lambda: band('<div class="two"><div class="stack"><h2>Buying</h2>' + ''.join('<a href="/questions/buying/" style="font-weight:600">%s</a>' % e(q) for q, _ in BUY_QS[:6]) + '<a class="btn navy" href="/questions/buying/" style="align-self:flex-start">All buyer questions</a></div>'
               '<div class="stack"><h2>Selling</h2>' + ''.join('<a href="/questions/selling/" style="font-weight:600">%s</a>' % e(q) for q, _ in SELL_QS[:6]) + '<a class="btn navy" href="/questions/selling/" style="align-self:flex-start">All seller questions</a></div></div>'),
  lambda: cta('Have a question we did not answer?', 'Ask Michael directly. He replies personally.', 'contact'),
  title='Real Estate Questions Answered | Vaughan & GTA | SoldMike', desc='Straight answers to the questions buyers and sellers in Vaughan and the GTA ask most.',
  trail=[('Questions', '/questions/')])
for kind, qs, label in [('buying', BUY_QS, 'Buyer'), ('selling', SELL_QS, 'Seller')]:
    P('/questions/%s/' % kind,
      lambda kind=kind, label=label: hero([('Home', '/'), ('Questions', '/questions/'), ('%s questions' % label, '/questions/%s/' % kind)], '%s questions, answered' % label, 'The questions %ss in Vaughan ask us most, each answered in the first sentence.' % label.lower()),
      lambda qs=qs: band(faq(qs), narrow=True),
      lambda: cta('Still have a question?', 'Ask Michael directly. He replies personally.', 'contact'),
      title='%s Questions: Real Estate in Vaughan & Ontario | SoldMike' % label, desc='Answers to the top %s questions about real estate in Vaughan and Ontario.' % label.lower(),
      trail=[('Questions', '/questions/'), ('%s questions' % label, '/questions/%s/' % kind)], schema=[faq_schema(qs)])

# =====================================================================
# ABOUT
# =====================================================================
P('/about/',
  lambda: hero([('Home', '/'), ('About', '/about/')], 'Michael Barillari, Broker', 'SOLDMIKE. RE/MAX Premier The OP Team, Vaughan & Woodbridge.'),
  lambda: band('<div class="person"><div class="pic"><img src="/mike.png" alt="Michael Barillari"></div><div class="stack">' + prose(
      'Michael Barillari is a Broker with RE/MAX Premier The OP Team, helping buyers and sellers across Vaughan, Woodbridge, Kleinburg, King, Caledon and Toronto.',
      'He also runs Toronto Property Media, which shoots the photos, drone, video and twilight images for every listing he sells.') +
      todo('Your story in 3 short paragraphs: how you started, why real estate, what you do differently', 'Credentials: Broker licence year, designations, awards (verifiable)', 'Languages spoken', 'A personal line: family, community, what you do outside work') + '</div></div>'),
  lambda: band(cards([('/about/the-op-team/', 'The OP Team', 'Who you work with'), ('/videos/', 'Videos', 'Market updates and neighbourhood tours'), ('/reviews/', 'Reviews', 'What clients say'), ('/join/', 'Join the team', 'Getting started as a realtor')]), 'tint'),
  lambda: cta('Talk to Michael', 'Buying, selling or just have a question. Call or text %s.' % PHONE, 'contact'),
  title='Michael Barillari, Broker | SOLDMIKE | RE/MAX Premier The OP Team', desc='Michael Barillari, Broker, SOLDMIKE. RE/MAX Premier The OP Team, serving Vaughan, Woodbridge, Kleinburg, King, Caledon and Toronto.',
  trail=[('About', '/about/')],
  schema=[{'@context': 'https://schema.org', '@type': 'Person', 'name': 'Michael Barillari', 'jobTitle': 'Broker', 'worksFor': {'@type': 'Organization', 'name': BROKERAGE}, 'url': SITE + '/about/', 'image': SITE + '/mike.png'}])

P('/about/the-op-team/',
  lambda: hero([('Home', '/'), ('About', '/about/'), ('The OP Team', '/about/the-op-team/')], 'The OP Team', 'RE/MAX Premier The OP Team Inc., Brokerage.'),
  lambda: band(todo('What The OP Team is and how the team works for clients', 'Team members: photo, name, role, one line each', 'Team results (verifiable)', 'Link to theopteam.ca'), narrow=True),
  lambda: cta('Work with the team', 'Start with Michael. He brings in the right people at each step.', 'contact'),
  title='The OP Team | RE/MAX Premier | SoldMike', desc='RE/MAX Premier The OP Team Inc., Brokerage: the team behind SoldMike in Vaughan and Woodbridge.',
  trail=[('About', '/about/'), ('The OP Team', '/about/the-op-team/')])

P('/videos/',
  lambda: hero([('Home', '/'), ('Videos', '/videos/')], 'Videos', 'Market updates, neighbourhood tours and listing films from Michael and Toronto Property Media.', '/hero.jpg'),
  lambda: band(todo('Link the YouTube channel once it launches', 'Feature 3 videos: a monthly market update, a neighbourhood tour, a listing film', 'Title each by area so AI tools can quote them (for example "Woodbridge market update, October 2026")'), narrow=True),
  title='Real Estate Videos: Vaughan Market Updates & Tours | SoldMike', desc='Vaughan market updates, neighbourhood tours and listing videos from Michael Barillari.',
  trail=[('Videos', '/videos/')])

P('/join/',
  lambda: hero([('Home', '/'), ('Join the team', '/join/')], 'Getting started as a realtor', 'Thinking about a career in real estate, or licensed and looking for a team? Here is how we help new agents get going.'),
  lambda: band('<div class="two"><div class="stack">' + prose('<h2>What you get</h2>') + todo('What new agents get: training, leads, media, systems, mentorship', 'How to get licensed in Ontario (Humber courses, RECO registration) in a short list', 'What success looks like in year one') + '</div>' + form('join') + '</div>'),
  title='Join The OP Team | Getting Started as a Realtor | SoldMike', desc='Thinking about becoming a realtor in Ontario or looking for a new team? Join The OP Team at RE/MAX Premier.',
  trail=[('Join the team', '/join/')])

P('/contact/',
  lambda: hero([('Home', '/'), ('Contact', '/contact/')], 'Contact Michael', 'Call or text %s, email %s, or send a message below.' % (PHONE, EMAIL)),
  lambda: band('<div class="two"><div class="stack">' + kv([('Call or text', PHONE), ('Email', EMAIL), ('Office', '%s, %s' % (ADDRESS['street'], ADDRESS['city'])), ('Brokerage', 'RE/MAX Premier The OP Team')]) +
               '<a class="btn ghost" href="https://www.google.com/maps/search/%s" target="_blank" rel="noopener" style="align-self:flex-start">Open the office in Google Maps</a>' % (ADDRESS['street'] + ' ' + ADDRESS['city']).replace(' ', '+') +
               todo('Confirm the one office address to use everywhere (3550 Rutherford Rd Unit 80 vs Unit 43 on the RE/MAX page)', 'Office hours') + '</div>' + form('contact') + '</div>'),
  title='Contact Michael Barillari | SoldMike', desc='Contact Michael Barillari, Broker, RE/MAX Premier The OP Team. Call or text %s.' % PHONE,
  trail=[('Contact', '/contact/')])

P('/free-guide/',
  lambda: hero([('Home', '/'), ('Free guide', '/free-guide/')], 'Free guide: selling your home in Vaughan', 'The full plan we use to sell homes in Vaughan, from pricing to closing, in one PDF.'),
  lambda: band('<div class="two"><div class="stack">' + todo('Create the PDF lead magnet (can reuse the 15 seller steps)', 'Connect delivery: the form adds the lead to FUB; FUB action plan emails the PDF') + '</div>' + form('guide') + '</div>'),
  title='Free Guide to Selling Your Home in Vaughan | SoldMike', desc='Download the free guide to selling your home in Vaughan.', trail=[('Free guide', '/free-guide/')])

P('/privacy/',
  lambda: hero([('Home', '/'), ('Privacy', '/privacy/')], 'Privacy policy', 'How we collect, use and protect your personal information.'),
  lambda: band(prose('When you fill in a form on this site we collect the details you give us, such as your name, email, phone and property address, to reply to you and provide real estate services. Your information goes to Michael Barillari and is stored in our customer relationship system. We do not sell your information.',
                     'You can ask to see, correct or delete your information at any time by emailing %s.' % EMAIL) + '<div style="margin-top:20px">' + todo('Have the brokerage review this policy (PIPEDA, CASL for emails, cookies/analytics once added)') + '</div>', narrow=True),
  title='Privacy Policy | SoldMike', desc='Privacy policy for soldmike.com.', trail=[('Privacy', '/privacy/')], noindex=True)

P('/terms/',
  lambda: hero([('Home', '/'), ('Terms', '/terms/')], 'Terms of use', 'The rules for using this website and its listing information.'),
  lambda: band(prose('Listing information on this site is provided for consumers’ personal, non-commercial use and may not be used for any purpose other than to identify prospective properties consumers may be interested in purchasing. Information is deemed reliable but not guaranteed.',
                     'The trademarks REALTOR®, REALTORS®, and the REALTOR® logo are controlled by The Canadian Real Estate Association (CREA). The trademarks MLS®, Multiple Listing Service® and the associated logos are owned by CREA.') + '<div style="margin-top:20px">' + todo('Add the exact terms of use TRREB/PropTx requires for IDX and VOW (VOW users must accept terms before seeing sold data)') + '</div>', narrow=True),
  title='Terms of Use | SoldMike', desc='Terms of use for soldmike.com.', trail=[('Terms', '/terms/')], noindex=True)

# ---------- 404, sitemap, robots, checklist ----------
PAGE = '/404'
page404 = ('<!doctype html><html lang="en-CA"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Page not found | SoldMike</title><meta name="robots" content="noindex">'
           '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@700;800&family=Barlow:wght@400;600&display=swap"><link rel="stylesheet" href="/assets/site.css"></head><body>'
           + header('/404') + '<main id="main">' + hero([('Home', '/'), ('Not found', '/404')], 'That page has moved', 'The page you were looking for is not here. Try one of these instead.') +
           band(cards([('/listings/', 'Search homes', 'Every MLS® listing'), ('/sell/home-value/', 'Home value', 'What your home is worth'), ('/neighbourhoods/', 'Neighbourhoods', 'Area guides'), ('/contact/', 'Contact', 'Talk to Michael')])) + '</main>' + footer() + '<script src="/assets/site.js" defer></script></body></html>')
open('404.html', 'w', encoding='utf-8').write(page404)

today = date.today().isoformat()
urls = ['/', '/listing.html'] + SITEMAP
open('sitemap.xml', 'w').write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' +
                               ''.join('  <url><loc>%s%s</loc><lastmod>%s</lastmod></url>\n' % (SITE, u, today) for u in urls) + '</urlset>\n')
open('robots.txt', 'w').write('User-agent: *\nAllow: /\nDisallow: /saved/\n\nUser-agent: GPTBot\nAllow: /\n\nUser-agent: OAI-SearchBot\nAllow: /\n\nUser-agent: ClaudeBot\nAllow: /\n\nUser-agent: PerplexityBot\nAllow: /\n\nUser-agent: Google-Extended\nAllow: /\n\nSitemap: %s/sitemap.xml\n' % SITE)

with open('CONTENT-TODO.md', 'w') as f:
    f.write('# soldmike.com content to write\n\nGenerated by build.py on %s. Every yellow "Content to write" box on the site is listed here, page by page.\n\n' % today)
    seen = {}
    for p, items in TODOS:
        seen.setdefault(p, []).extend(items)
    for p, items in seen.items():
        f.write('## %s%s\n' % (SITE, p) + ''.join('- [ ] %s\n' % i for i in items) + '\n')
print('pages:', len(SITEMAP), 'todo items:', sum(len(i) for _, i in TODOS))
