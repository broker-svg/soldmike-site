#!/usr/bin/env python3
"""Builds every inner page of soldmike.com from the PAGES data below.
Run: python3 build.py   (writes <slug>/index.html, sitemap.xml, CONTENT-TODO.md)
Anything in todo() is content still to write; CONTENT-TODO.md lists them all."""
import json, os, html
from datetime import date

SITE = 'https://soldmike.com'
PHONE = '647-694-3109'
EMAIL = 'mike@theopteam.ca'
ADDRESS = {'street': '3550 Rutherford Rd, Unit 80', 'city': 'Vaughan', 'region': 'ON', 'postal': 'L4H 3T8'}
BROKERAGE = 'RE/MAX Premier The OP Team Inc., Brokerage'
AREAS = ['Vaughan', 'Woodbridge', 'Kleinburg', 'Maple', 'Caledon', 'King', 'East Gwillimbury', 'Toronto']
TODOS = []
LICENSED = 'December 2011'
DESIGNATION_NAMES = ['ABR® (Accredited Buyer Representative)', 'SRS (Seller Representative Specialist)', 'RENE (Real Estate Negotiation Expert)', 'Accredited GreenBroker® – Commercial']
PROFILES = [
    'https://www.google.com/maps/place/data=!4m2!3m1!1s0x882b2ffe673f1b5d:0x97e6bee0f5d0c849',  # Google Business Profile
    'https://www.remax.ca/on/michael-barillari-101747-ag',
    'https://www.realtor.ca/agent/1949177/michael-barillari-3550-rutherford-rd-80-vaughan-ontario-l4h3t8',
    'https://rankmyagent.com/michaelbarillari',
    'https://www.linkedin.com/in/soldmike/',
]
SHOW_TODOS = False
HOMES_LIVE = True  # True once soldmike.com runs through Cloudflare and /homes/ listing pages are served by the Worker  # unfinished content stays out of the public pages; CONTENT-TODO.md still lists it
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
        'knowsLanguage': ['English', 'Italian'],
        'hasCredential': [{'@type': 'EducationalOccupationalCredential', 'name': n} for n in DESIGNATION_NAMES],
        'sameAs': PROFILES,
    }

def crumbs_schema(trail):
    return {'@context': 'https://schema.org', '@type': 'BreadcrumbList', 'itemListElement': [
        {'@type': 'ListItem', 'position': i + 1, 'name': n, 'item': SITE + u} for i, (n, u) in enumerate(trail)]}

def faq_schema(qs):
    return {'@context': 'https://schema.org', '@type': 'FAQPage', 'mainEntity': [
        {'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': a}} for q, a in qs if not a.startswith('[')]}

# ---------- building blocks ----------
NAV = [
    ('Buy', [('/listings/', 'Search homes'), ('/buy/', 'Buying with us'), ('/buy/buyer-guide/', 'Buyer guide: 15 steps'), ('/free-guide/', 'Free PDF guides'), ('/buy/pre-construction/', 'Pre-construction'), ('/saved/', 'Saved homes & searches'), ('/open-house/', 'Open houses')]),
    ('Sell', [('/sell/home-value/', "What's my home worth?"), ('/sell/', 'Selling with us'), ('/sell/seller-guide/', 'Seller guide: 15 steps'), ('/free-guide/', 'Free PDF guides'), ('/sell/cost-to-sell-vaughan/', 'Cost to sell calculator'), ('/sell/how-we-market/', 'How we market your home'), ('/sell/pre-listing/', 'Pre-listing package')]),
    ('Neighbourhoods', [('/neighbourhoods/', 'All neighbourhoods')] + [('/neighbourhoods/%s/' % s, n) for s, n in [('woodbridge', 'Woodbridge'), ('vellore', 'Vellore Village'), ('kleinburg', 'Kleinburg'), ('maple', 'Maple'), ('caledon-bolton', 'Caledon & Bolton'), ('king-city-nobleton', 'King City & Nobleton'), ('sharon-east-gwillimbury', 'Sharon & East Gwillimbury'), ('toronto', 'Toronto')]]),
    ('Results', [('https://soldmike.ca/sellers/team-sold-listings', 'Recent sales'), ('/results/', 'Case studies'), ('/reviews/', 'Client reviews'), ('/market-reports/', 'Market reports')]),
    ('Questions', [('/questions/', 'All questions'), ('/questions/buying/', 'Buyer questions'), ('/questions/selling/', 'Seller questions')]),
    ('TorontoPropertyMedia.ca', 'https://torontopropertymedia.ca/'),
    ('About', [('/about/', 'Michael Barillari'), ('/about/the-op-team/', 'The OP Team'), ('/videos/', 'Videos'), ('/join/', 'Join the team'), ('/contact/', 'Contact')]),
]

def header(path):
    out = []
    for label, items in NAV:
        if isinstance(items, str):
            out.append('<a href="%s" target="_blank" rel="noopener">%s</a>' % (items, e(label)))
            continue
        cur = any(path.startswith(u) and u != '/' for u, _ in items)
        links = ''.join('<a href="%s"%s>%s</a>' % (u, ' aria-current="page"' if u == path else '', e(t)) for u, t in items)
        out.append('<div class="dd"><button type="button" aria-expanded="false"%s>%s</button><div class="menu">%s</div></div>'
                   % (' style="color:var(--red)"' if cur else '', label, links))
    return ('<a class="skip" href="#main">Skip to content</a>'
            '<header class="top"><div class="wrap"><a class="logo" href="/" aria-label="SoldMike home"><img src="/logo.png" alt="RE/MAX Premier The OP Team, SoldMike"></a>'
            '<button class="burger" type="button" aria-label="Menu" aria-expanded="false" aria-controls="nav"><span></span><span></span><span></span></button>'
            '<nav class="nav" id="nav" aria-label="Main">%s<a class="btn" href="/sell/home-value/">Home value</a></nav></div></header>') % ''.join(out)

def footer():
    cols = ''.join('<div><strong>%s</strong>%s</div>' % (l, ''.join('<a href="%s">%s</a>' % (u, e(t)) for u, t in items[:5])) for l, items in NAV[:4] if not isinstance(items, str))
    return ('<footer><div class="wrap"><div class="fcols">'
            '<div><img src="/logo-soldmike-white.png" alt="RE/MAX Premier The OP Team, SoldMike" style="width:220px;height:auto">'
            '<span>Michael Barillari, Broker, SOLDMIKE. %s Independently owned and operated.</span>'
            '<span>%s, %s, %s %s</span><span>Call or text %s</span><span>%s</span><a href="/admin/" rel="nofollow" style="margin-top:6px">Team login</a></div>%s</div>'
            '<div class="legal"><span>The trademarks REALTOR®, REALTORS®, and the REALTOR® logo are controlled by The Canadian Real Estate Association (CREA) and identify real estate professionals who are members of CREA. The trademarks MLS®, Multiple Listing Service® and the associated logos are owned by CREA. <a href="/privacy/" style="color:var(--pale)">Privacy</a> · <a href="/terms/" style="color:var(--pale)">Terms</a> · <a href="/admin/" style="color:var(--pale)" rel="nofollow">Team login</a></span>'
            '<a href="https://www.realtor.ca/en" target="_blank" rel="noopener" class="rca-foot" aria-label="Powered by REALTOR.ca"><img src="https://www.realtor.ca/images/en-ca/powered_by_realtor.svg" width="125" alt="Powered by REALTOR.ca" loading="lazy" style="background:#fff;border-radius:4px;padding:4px"></a></div></div></footer>'
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
    if not SHOW_TODOS:
        return ''
    li = ''.join('<li>%s</li>' % e(i) for i in items)
    return '<div class="todo"><strong>Content to write</strong><ul>%s</ul></div>' % li

def band(inner, cls='', id=None, narrow=False):
    return '<section class="band %s"%s><div class="wrap%s">%s</div></section>' % (cls, ' id="%s"' % id if id else '', ' narrow' if narrow else '', inner)

def head_block(h2, p=None):
    return '<div class="head"><h2>%s</h2>%s</div>' % (e(h2), '<p>%s</p>' % p if p else '')

def prose(*ps):
    return '<div class="prose">%s</div>' % ''.join(p if p.startswith('<') else '<p>%s</p>' % p for p in ps)

def cards(items):
    items = [(u, t, s if not unfinished(s) else '') for u, t, s in items if not unfinished(t)]
    return '<div class="cards">%s</div>' % ''.join('<a href="%s" class="rv"><b>%s</b><span>%s</span></a>' % (u, e(t), e(s)) for u, t, s in items)

def steps(items):
    return '<ol class="steps">%s</ol>' % ''.join('<li class="rv"><div><b>%s</b><p>%s</p></div></li>' % (e(t), e(d)) for t, d in items)

def unfinished(v):
    return '[' in v

def kv(rows):
    rows = [(a, b) for a, b in rows if not unfinished(b)]
    out = '<dl class="kv">%s</dl>' % ''.join('<div><dt>%s</dt><dd>%s</dd></div>' % (e(a), e(b)) for a, b in rows)
    return out.replace('LIVECOUNT', '<span data-area-count="%s">…</span>' % (PAGE or '').strip('/').split('/')[-1])

def faq(qs):
    out = ''
    for q, a in qs:
        if a.startswith('['):
            todo('Answer: ' + q)
    qs = [(q, a) for q, a in qs if not a.startswith('[')]
    for i, (q, a) in enumerate(qs):
        body = '<p>%s</p>' % a
        out += '<details%s><summary>%s<span class="plus" aria-hidden="true">+</span></summary><div class="a">%s</div></details>' % (' open' if i == 0 else '', e(q), body)
    return '<div class="faq">%s</div>' % out

FORMS = {
    'value': ('Home value request', 'Send me my home value', [('full', 'address', 'Property address', 'text', 'Street, city'), ('', 'name', 'Your name', 'text', ''), ('', 'phone', 'Phone', 'tel', ''), ('full', 'email', 'Email', 'email', ''), ('full', 'plan', "I'm planning to", ['Sell in the next 3 months', 'Sell in 3 to 12 months', 'Sell and buy', 'Just curious'], ''), ('full', 'when', 'How would you like it?', ['Email me my price range (within 24 hours)', 'Call me right away to talk it through'], '')], 'Sent. Michael will send your price range within 24 hours, or call you right away if you asked for a call.'),
    'contact': ('Contact', 'Send message', [('', 'name', 'Your name', 'text', ''), ('', 'phone', 'Phone', 'tel', ''), ('full', 'email', 'Email', 'email', ''), ('full', 'topic', 'I want to', ['Buy a home', 'Sell a home', 'Buy and sell', 'Ask a question', 'Talk about joining the team'], ''), ('full', 'message', 'Message', 'area', '')], 'Sent. Michael will reply today.'),
    'buyer': ('Buyer consultation', 'Book a buyer consultation', [('', 'name', 'Your name', 'text', ''), ('', 'phone', 'Phone', 'tel', ''), ('full', 'email', 'Email', 'email', ''), ('', 'area', 'Area', ['Woodbridge', 'Vaughan', 'Kleinburg', 'King', 'Caledon', 'Toronto', 'Not sure yet'], ''), ('', 'budget', 'Budget', ['Under $1M', '$1M to $1.5M', '$1.5M to $2M', '$2M to $3M', '$3M+'], '')], 'Sent. Michael will call you to set up a time.'),
    'precon': ('Pre-construction list', 'Get the VIP list', [('', 'name', 'Your name', 'text', ''), ('', 'phone', 'Phone', 'tel', ''), ('full', 'email', 'Email', 'email', ''), ('full', 'type', 'Interested in', ['Condo', 'Townhome', 'Detached', 'Investment'], '')], "You're on the list. Michael will send new launches as they come up."),
    'guide': ('Free guide', 'Get the free guide', [('', 'name', 'Your name', 'text', ''), ('', 'email', 'Email', 'email', ''), ('full', 'which', 'Which guide', ['Selling a home in Vaughan', 'Buying a home in Vaughan'], '')], 'Sent. Your guide is ready to download.'),
    'join': ('Join the team', "Let's talk", [('', 'name', 'Your name', 'text', ''), ('', 'phone', 'Phone', 'tel', ''), ('full', 'email', 'Email', 'email', ''), ('full', 'stage', 'Where are you at', ['Thinking about getting licensed', 'In the licensing courses', 'Newly licensed', 'Licensed and looking for a new team'], '')], 'Sent. Michael will reach out to set up a coffee.'),
    'report': ('Market report', 'Email me the monthly report', [('', 'name', 'Your name', 'text', ''), ('', 'email', 'Email', 'email', ''), ('full', 'area', 'Area', ['Vaughan', 'Woodbridge', 'Kleinburg', 'King', 'Caledon', 'East Gwillimbury'], '')], "Done. You'll get the next report on the 5th."),
}
GUIDES = {'Selling a home in Vaughan': '/guides/selling-a-home-in-vaughan.pdf', 'Buying a home in Vaughan': '/guides/buying-a-home-in-vaughan.pdf'}
def form(kind, uid='', pick=None):
    lead, btn, fields, done = FORMS[kind]
    if pick:  # preselect and lock one option (e.g. the seller guide on the seller guide page)
        fields = [(sp, n, l, [pick] if n == 'which' else t, ph) for sp, n, l, t, ph in fields]
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
    dl = ' data-dl="%s"' % e(json.dumps(GUIDES)) if kind == 'guide' else ''
    return ('<form class="form" data-lead="%s" data-done="%s"' + dl + ' aria-label="%s">%s<button class="btn full" type="submit">%s</button>'
            '<p class="msg full" role="status"></p><p class="fine full">By sending, I agree to be contacted by RE/MAX Premier The OP Team by call, text and email. To opt out, reply STOP or click unsubscribe.</p></form>') % (e(lead), e(done), e(lead), out, e(btn))

def cta(h, p, kind='value'):
    return '<section class="cta"><div class="wrap"><div><h2>%s</h2><p>%s</p></div>%s</div></section>' % (e(h), p, form(kind, '-cta'))

CREA_NOTE = ('<p class="crea-note">The information contained on this site is based in whole or in part on information that is provided by members of The Canadian Real Estate Association (CREA), who are responsible for its accuracy. CREA reproduces and distributes this information as a service for its members and assumes no responsibility for its accuracy. Listings refresh every day. Deemed reliable but not guaranteed.</p>')
def live_grid(area, n=3):
    """Live MLS® listings for an area, filled by /assets/listings.js from the listings Worker."""
    return '<div class="lgrid" data-listings data-area="%s" data-n="%d"></div>' % (area, n)

# ---------- page writer ----------
SITEMAP = []
LISTING_HEAD = '<link rel="stylesheet" href="/assets/listings.css?v=11">'
LEAFLET_HEAD = '<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.css">'
LEAFLET_JS = '<script src="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.js" defer></script>'
LISTING_JS = '<script src="/assets/listings.js?v=5" defer></script><script src="/assets/account.js?v=3" defer></script>'

def page(path, title, desc, trail, body, schema=None, noindex=False, head='', js=''):
    global PAGE
    sch = [agent_schema(), crumbs_schema(trail)] + (schema or [])
    doc = ('<!doctype html><html lang="en-CA"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">'
           '<title>%s</title><meta name="description" content="%s"><link rel="canonical" href="%s%s">'
           '<meta property="og:type" content="website"><meta property="og:title" content="%s"><meta property="og:description" content="%s"><meta property="og:url" content="%s%s"><meta property="og:image" content="%s/hero.jpg">'
           '%s<link rel="icon" href="/logo.png"><link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
           '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@500;600;700;800&family=Barlow:wght@400;500;600&display=swap">'
           '<link rel="stylesheet" href="/assets/site.css?v=8">%s%s</head><body>%s<main id="main">%s</main>%s<script src="/assets/site.js?v=9" defer></script>%s<script src="/assets/chat.js?v=7" defer></script></body></html>'
           ) % (e(title), e(desc), SITE, path, e(title), e(desc), SITE, path, SITE,
                '<meta name="robots" content="noindex">' if noindex else '',
                ''.join('<script type="application/ld+json">%s</script>' % json.dumps(s, ensure_ascii=False) for s in sch), head,
                header(path), body, footer(), js)
    out = path.strip('/') + '/index.html' if path != '/' else 'index.html'
    os.makedirs(os.path.dirname(out) or '.', exist_ok=True)
    open(out, 'w', encoding='utf-8').write(doc)
    if not noindex: SITEMAP.append(path)

H = [('Home', '/')]
def P(path, *body_parts, title, desc, trail, schema=None, noindex=False, head='', js=''):
    global PAGE
    PAGE = path
    body = ''.join(b() if callable(b) else b for b in body_parts)
    page(path, title, desc, H + trail, body, schema, noindex, head, js)

# =====================================================================
# BUY
# =====================================================================
PAGE = '/listings/'
AREA_OPTS = [('', 'All areas'), ('woodbridge', 'Woodbridge'), ('vellore', 'Vellore Village'), ('kleinburg', 'Kleinburg'), ('maple', 'Maple'), ('vaughan', 'All of Vaughan'), ('king-city-nobleton', 'King City & Nobleton'), ('caledon-bolton', 'Caledon & Bolton'), ('sharon-east-gwillimbury', 'East Gwillimbury'), ('richmond-hill', 'Richmond Hill'), ('aurora', 'Aurora'), ('newmarket', 'Newmarket'), ('markham', 'Markham'), ('brampton', 'Brampton'), ('mississauga', 'Mississauga'), ('toronto', 'Toronto')]
def sel(name, label, opts, extra=False):
    return '<div%s><label' % (' class="xf"' if extra else '') + ' for="f-%s">%s</label><select id="f-%s" name="%s">%s</select></div>' % (name, label, name, name, ''.join('<option value="%s">%s</option>' % (v, e(t)) for v, t in opts))
PRICES = [500000, 750000, 1000000, 1250000, 1500000, 2000000, 2500000, 3000000, 5000000]
def SEARCH_BLOCK():
    # full search (box, filters, results, map); used on /listings/ and /buy/
    return (
    '<div class="ls" data-listings><form id="lsForm" aria-label="Search listings" role="search">'
    '<div class="sbox"><label for="f-q" class="sr">Search</label><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="M20 20l-3.5-3.5"/></svg>'
    '<input id="f-q" name="q" type="search" enterkeyhint="search" autocomplete="off" placeholder="Address, MLS®, city or area"><button class="btn" type="submit">Search</button></div>'
    '<div class="filters">'
    + sel('area', 'Area', AREA_OPTS)
    + sel('lease', 'For', [('', 'Sale'), ('1', 'Rent')])
    + sel('type', 'Type', [('', 'Any type'), ('detached', 'Detached'), ('semi', 'Semi-detached'), ('town', 'Townhouse'), ('condo', 'Condo apartment'), ('other', 'Other')], True)
    + sel('min', 'Min price', [('', 'No min')] + [(str(p), '$%s' % format(p, ',')) for p in PRICES], True)
    + sel('max', 'Max price', [('', 'No max')] + [(str(p), '$%s' % format(p, ',')) for p in PRICES])
    + sel('beds', 'Beds', [('', 'Any')] + [(str(b), '%d+' % b) for b in range(1, 6)])
    + sel('baths', 'Baths', [('', 'Any')] + [(str(b), '%d+' % b) for b in range(1, 5)], True)
    + sel('sort', 'Sort', [('new', 'Newest'), ('plow', 'Price, low to high'), ('phigh', 'Price, high to low')], True)
    + '<button type="button" class="btn ghost xfb" onclick="var f=this.parentNode;f.classList.toggle(\'all\');this.textContent=f.classList.contains(\'all\')?\'Fewer filters\':\'More filters\'">More filters</button></div></form>'
    '<div class="ls-bar"><p id="lsInfo" aria-live="polite"></p><button type="button" class="btn ghost hidemap" id="lsHide">Hide map</button><div class="viewt" role="group" aria-label="View"><button type="button" data-view="list" aria-pressed="true">List</button><button type="button" data-view="map" aria-pressed="false">Map</button></div></div>'
    '<div class="ls-wrap" id="lsWrap" data-view="list"><div class="ls-listcol"><div class="lgrid" id="lsList"></div><button class="btn navy" id="lsMore" type="button" hidden>Show more homes</button></div>'
    '<div class="ls-mapcol"><div><div id="lsMap" role="region" aria-label="Map of results"></div><button class="btn navy" id="lsArea" type="button" hidden>Search this map area</button>'
    '<p style="margin:10px 0 0;font-size:14px"><button type="button" id="lsClearArea" style="border:0;background:none;padding:0;color:var(--navy);font-weight:600;cursor:pointer;text-decoration:underline">Clear map area</button></p></div></div></div>'
    '<div class="rca-row"><a class="btn ghost" href="/saved/">Your saved homes</a><a href="https://www.realtor.ca/en" target="_blank" rel="noopener"><img src="https://www.realtor.ca/images/en-ca/powered_by_realtor.svg" width="125" alt="Powered by REALTOR.ca"></a></div>'
    + CREA_NOTE + '</div>')

P('/listings/',
  lambda: hero([('Home', '/'), ('Search homes', '/listings/')], 'Homes for sale in Vaughan & the GTA', 'MLS® listings from Toronto to King and Caledon, refreshed every day. Save the ones you like and Michael can show you any of them.'),
  lambda: band(
    SEARCH_BLOCK(), 'lsband'),
  title='Homes for Sale in Vaughan, Woodbridge & the GTA | SoldMike',
  desc='Search MLS® listings in Vaughan, Woodbridge, Kleinburg, King, Caledon and Toronto, refreshed daily. Map search, saved homes and showings with Michael Barillari.',
  trail=[('Search homes', '/listings/')],
  head=LISTING_HEAD + LEAFLET_HEAD, js=LISTING_JS + LEAFLET_JS + '<script src="/assets/search.js?v=3" defer></script>')

P('/listings/home/',
  '<div class="ld" id="ld" data-listings><p class="ld-loading">Loading this home…</p></div>',
  title='Home for sale | SoldMike', desc='MLS® listing details, photos and showings with Michael Barillari, Broker.',
  trail=[('Search homes', '/listings/'), ('Listing', '/listings/home/')],
  head=LISTING_HEAD + LEAFLET_HEAD, js=LISTING_JS + LEAFLET_JS + '<script src="/assets/home.js?v=9" defer></script>', noindex=True)  # shell for /listings/home/?id= and the Worker's /homes/ pages (the Worker strips this noindex)

SAVED_JS = """<script>
document.addEventListener('DOMContentLoaded',function(){
  var SM=window.SM,esc=SM.esc,box=document.getElementById('acctBox'),g=document.getElementById('savedGrid'),sl=document.getElementById('searchList');
  function homes(){var ids=SM.saved();if(!ids.length){g.innerHTML='<p class="empty">No saved homes yet. <a href="/listings/">Search homes</a> and tap the heart to save one.</p>';return;}
    SM.loading(g,3);SM.get('/api/cards?ids='+ids.join(',')).then(function(r){SM.cards(g,r.items,'');});}
  function qs(q){var p=new URLSearchParams();Object.keys(q||{}).forEach(function(k){p.set(k,q[k]);});return p.toString();}
  function render(){
    var a=SM.account;
    if(!SM.signedIn()){box.innerHTML='<div class="acct"><div><h2>Sign in to keep them everywhere</h2><p>Your saved homes and searches on every phone and computer, and new matches by email the morning they list. Sign in with Google or any email address.</p></div><button class="btn" type="button" id="siBtn">Sign in</button></div>';
      document.getElementById('siBtn').onclick=function(){SM.signIn().then(render).catch(function(){});};
      sl.innerHTML='<p class="empty">Sign in, then tap <b>Save this search</b> on the <a href="/listings/">search page</a>.</p>';homes();return;}
    if(!a){box.innerHTML='<p>Loading your account…</p>';return;}
    box.innerHTML='<div class="acct"><div><h2>Hi'+(a.me.first?' '+esc(a.me.first):'')+'</h2><p>Signed in as <b>'+esc(a.me.email)+'</b>. Your saved homes and searches follow you to any device.</p></div><button class="btn ghost" type="button" id="soBtn">Sign out</button></div>';
    document.getElementById('soBtn').onclick=function(){SM.signOut();render();};
    var ss=a.searches.filter(function(s){return s.active;});
    sl.innerHTML=ss.length?ss.map(function(s){return '<div class="srow"><div><b>'+esc(s.label)+'</b><small>'+(a.me.alerts?'New matches by email':'No emails')+'</small></div><a class="btn ghost" href="/listings/?'+qs(s.q)+'">View</a><button class="btn ghost" type="button" data-rm="'+s.id+'">Remove</button></div>';}).join('')
      :'<p class="empty">No saved searches yet. On the <a href="/listings/">search page</a>, set your filters and tap <b>Save this search</b>.</p>';
    [].forEach.call(sl.querySelectorAll('[data-rm]'),function(btn){btn.onclick=function(){SM.accountCall('/api/me/search/remove',{id:+btn.dataset.rm}).then(SM.accountApply);};});
    homes();
  }
  document.addEventListener('sm:account',render);render();
});
</script>"""
P('/saved/',
  lambda: hero([('Home', '/'), ('Saved homes', '/saved/')], 'Your saved homes and searches', 'Save homes and searches, see them on every device, and get new matches the morning they hit the market.'),
  lambda: band('<div id="acctBox"></div>', 'tint'),
  lambda: band(head_block('Saved searches') + '<div id="searchList" class="slist"></div>'),
  lambda: band(head_block('Saved homes', 'Tap the heart on any home to save it here.') + '<div class="lgrid" id="savedGrid" data-listings></div>' + CREA_NOTE),
  lambda: band('<div class="two"><div class="prose"><h2>Rather talk to Michael?</h2><p>Tell Michael what you are looking for and he will send new listings that fit and set up showings when you are ready.</p></div>' + form('buyer') + '</div>', 'tint'),
  title='Saved Homes & Searches | SoldMike', desc='Save homes and searches and get new MLS® listings by email.', trail=[('Saved homes', '/saved/')], noindex=True,
  head=LISTING_HEAD + '<style>.acct{display:flex;gap:20px;align-items:center;justify-content:space-between;flex-wrap:wrap}.acct h2{margin:0 0 6px}.acct p{margin:0;max-width:60ch}.slist{display:flex;flex-direction:column;gap:10px}.srow{display:flex;gap:10px;align-items:center;flex-wrap:wrap;padding:14px 16px;border:1px solid var(--line);border-radius:8px;background:#fff}.srow>div{flex:1 1 260px}.srow small{display:block;color:var(--muted)}</style>',
  js=LISTING_JS + SAVED_JS)

P('/buy/',
  lambda: hero([('Home', '/'), ('Buy', '/buy/')], 'Buying a home in Vaughan', 'How we help you find the right home, win it at the right price and get to closing day without surprises.', '/l1.jpg'),
  lambda: band(head_block('Search homes for sale', 'Every MLS® listing from Toronto to King and Caledon, refreshed daily. Use the map or search by address, MLS® number, city or neighbourhood.') + SEARCH_BLOCK(), 'lsband'),
  lambda: band(head_block('Where to start') + cards([
      ('/listings/', 'Search homes', 'Every MLS® listing, refreshed daily'),
      ('/buy/buyer-guide/', 'Buyer guide', 'The 15 steps from your why to closing day'),
      ('/neighbourhoods/', 'Neighbourhoods', 'Prices, schools and streets by community'),
      ('/buy/pre-construction/', 'Pre-construction', 'New launches and VIP pricing'),
      ('/questions/buying/', 'Buyer questions', 'Straight answers to what buyers ask us'),
  ])),
  lambda: band(head_block('Why buyers work with Michael') + '<div class="cards">' + ''.join('<div class="rv" style="background:var(--white);padding:26px 22px;display:flex;flex-direction:column;gap:10px"><b style="font-family:var(--display);font-size:22px;text-transform:uppercase;color:var(--navy)">%s</b><span style="color:var(--muted)">%s</span></div>' % (e(t), e(d)) for t, d in [('Local since 2011', 'Michael has helped buyers in Vaughan, Woodbridge, Kleinburg, King and Caledon since 2011. He knows the streets, the schools and what homes really sell for.'), ('Accredited Buyer Representative', 'Michael holds the ABR® designation, training focused on representing buyers, not sellers.'), ('Offers that win', 'As a Real Estate Negotiation Expert (RENE), Michael builds offers that stand out on offer night and protects you when you negotiate one-on-one.'), ('A team behind you', 'The OP Team brings 2,000+ transactions of combined experience, plus pre-construction access and help in English and Italian.')]) + '</div>' + todo('One real buyer story: area, what they wanted, how you won it'), 'tint'),
  lambda: cta('Start with a 20-minute call', 'Tell us what you need, your budget and timing. We set up your search the same day.', 'buyer'),
  title='Buying a Home in Vaughan & Woodbridge | SoldMike', desc='How Michael Barillari and The OP Team help buyers in Vaughan, Woodbridge and the GTA find, win and close on the right home.',
  trail=[('Buy', '/buy/')],
  head=LISTING_HEAD + LEAFLET_HEAD, js=LISTING_JS + LEAFLET_JS + '<script src="/assets/search.js?v=3" defer></script>')

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
  lambda: band('<div class="two"><div class="stack">' + prose('<h2>Take it with you</h2>', 'Get all 15 steps as a free 10-page PDF, with a checklist for every step and a page for your notes.') + '</div>' + form('guide', '-bg', 'Buying a home in Vaughan') + '</div>', 'tint'),
  lambda: cta('Questions about a step?', 'Michael answers buyers personally, usually the same day.', 'contact'),
  title='How to Buy a Home in Ontario: 15 Steps | SoldMike', desc='The 15 steps of buying a home in Vaughan and the GTA, from pre-approval and closing costs to offers, conditions and closing day.',
  trail=[('Buy', '/buy/'), ('Buyer guide', '/buy/buyer-guide/')],
  schema=[{'@context': 'https://schema.org', '@type': 'HowTo', 'name': 'How to buy a home in Ontario', 'step': [{'@type': 'HowToStep', 'position': i + 1, 'name': t, 'text': d} for i, (t, d) in enumerate(BUY_STEPS)]}])

P('/buy/pre-construction/',
  lambda: hero([('Home', '/'), ('Buy', '/buy/'), ('Pre-construction', '/buy/pre-construction/')], 'Pre-construction in Vaughan & York Region', 'New condos, towns and detached homes before they hit the public market, with VIP pricing and incentives.'),
  lambda: band('<div class="two"><div class="stack">' + prose(
      'Buying pre-construction means buying from a builder before the home is built, often years ahead of closing. The price is set today, deposits are spread out, and you choose finishes.',
      'It also comes with risks: closing delays, development charges, assignment rules and HST on new homes. We walk you through the agreement before you sign.') +
      prose('<h2>What to know before you sign</h2>',
            '<b>You have 10 days to change your mind on a new condo.</b> Under section 73 of Ontario\u2019s Condominium Act, buyers of a new condo from a builder can cancel within 10 calendar days of receiving the signed agreement and the disclosure documents, and get their deposit back. This does not apply to resale homes or assignments.',
            '<b>Deposits are protected, up to a limit.</b> Tarion protects deposits on new condos up to $20,000, and the Condominium Act requires deposits above that to be held in trust or secured. Freehold homes have their own Tarion deposit protection limits.',
            '<b>Check the builder.</b> Every new-home builder in Ontario must be licensed by the Home Construction Regulatory Authority (HCRA). You can look them up in the Ontario Builder Directory before you sign.',
            '<b>Watch the closing costs.</b> New homes can add development charges, utility hook-ups and HST adjustments at closing. We read the agreement with you and your lawyer so there are no surprises.') +
      todo('Current projects you can offer access to (name, builder, location, price from, deposit structure)', 'Your pre-construction track record or partnerships') +
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
      ('/results/', 'Case studies', 'How we sold three homes, start to finish'),
  ])),
  lambda: band(head_block('Why sellers choose Michael') + '<div class="cards">' + ''.join('<div class="rv" style="background:var(--white);padding:26px 22px;display:flex;flex-direction:column;gap:10px"><b style="font-family:var(--display);font-size:22px;text-transform:uppercase;color:var(--navy)">%s</b><span style="color:var(--muted)">%s</span></div>' % (e(t), e(d)) for t, d in [
      ('2,000+ transactions of experience', 'Michael and The OP Team have handled more than 2,000 transactions combined. That experience shows up in pricing, negotiation and the details that keep a deal together.'),
      ('Sell for more', 'Michael is a Real Estate Negotiation Expert (RENE). Priced right and launched well, homes draw multiple offers: 32 Highland Park Blvd in Markham sold $210K over asking.'),
      ('Sell faster', 'A strong launch brings buyers in the first week: 6 days in Markham, 15 days in Vaughan, 21 days for a $3.5M home in Toronto.'),
      ('Show your pride of ownership', 'Our own production team, Toronto Property Media, shoots every listing with photos, drone, video and twilight, so your home looks the way you know it.'),
  ]) + '</div><p style="margin-top:18px"><a href="/results/" style="font-weight:600">See recent sales</a></p>' + todo('One seller quote with name and neighbourhood'), 'tint'),
  lambda: cta("What's your home worth today?", 'Tell us the address. Michael sends a price range based on real recent sales near you, no obligation.'),
  title='Sell Your Home in Vaughan & Woodbridge | SoldMike', desc='Sell your Vaughan or Woodbridge home with Michael Barillari: pricing from real sales, in-house photo, drone and video, and a launch plan built for offers.',
  trail=[('Sell', '/sell/')])

P('/sell/home-value/',
  lambda: hero([('Home', '/'), ('Sell', '/sell/'), ('Home value', '/sell/home-value/')], "What's my home worth?", 'A price range for your home based on what similar homes nearby actually sold for, sent with the comparables attached.'),
  lambda: band('<div class="two">' + form('value') + '<div class="stack">' + prose(
      '<h2>How we price it</h2>',
      'Online estimates guess from averages. We look at the homes that sold closest to yours in the last few months, then adjust for size, lot, finishes, basement and parking.',
      'You get a range, the sales we used, and what we would list at if you sold today. No obligation and no pressure to list.') +
      '</div></div>'),
  lambda: band(head_block('Questions sellers ask first') + faq([
      ('How accurate is an online home value?', 'Often off by tens of thousands of dollars, because it cannot see inside your home or know which nearby sales are truly comparable. A local agent pricing from recent sales is more reliable.'),
      ('Does asking for a value commit me to anything?', 'No. You get the price range and the comparables. What you do with them is up to you.'),
      ('How long does it take?', 'Usually within 24 hours, often the same day. If you would rather talk now, ask for a call and Michael can walk you through a price range over the phone right away.'),
  ]), 'tint'),
  title="What's My Home Worth? Free Home Value in Vaughan | SoldMike", desc='Get a free price range for your Vaughan, Woodbridge or Kleinburg home, based on real recent sales near you.',
  trail=[('Sell', '/sell/'), ('Home value', '/sell/home-value/')],
  schema=[faq_schema([('How accurate is an online home value?', 'Often off by tens of thousands of dollars, because it cannot see inside your home or know which nearby sales are truly comparable. A local agent pricing from recent sales is more reliable.'), ('Does asking for a value commit me to anything?', 'No. You get the price range and the comparables. What you do with them is up to you.'), ('How long does it take?', 'Usually within 24 hours, often the same day. If you would rather talk now, ask for a call and Michael can walk you through a price range over the phone right away.')])])

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
  lambda: band('<div class="two"><div class="stack">' + prose('<h2>Take it with you</h2>', 'Get all 15 steps as a free 10-page PDF, with a checklist for every step and a page for your notes.') + '</div>' + form('guide', '-sg', 'Selling a home in Vaughan') + '</div>', 'tint'),
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

LAUNCH = [('Pricing meeting', 'We pull the recent sales on your street, set the list price and decide on an offer date or offers any time.'), ('Prep', 'A short list of repairs, paint and decluttering, plus a staging consultation.'), ('Media day', 'Toronto Property Media shoots photos, drone, video, twilight and a floor plan.'), ('Coming soon', 'Your home is teased on social media, to our buyer list and to the agent network before it hits the MLS®.'), ('MLS® go-live', 'The listing goes live with the full photo set and video.'), ('Launch week', 'Social ads, an email to our buyer list, open houses and agent showings, with feedback after every showing.'), ('Offer review', 'We compare every offer on price, deposit, conditions and closing date, not just the top number.'), ('Weekly updates', 'You get an update every week until the deal is firm, then we coordinate everything through closing.')]

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
  lambda: band(head_block('Your launch plan', 'The same eight steps for every listing.') + steps(LAUNCH) + todo('Link one full listing video (YouTube)', 'Before/after staging example'), 'tint'),
  lambda: cta('See what your home could look like', "Get your home's value and a walk-through of our marketing plan."),
  title='How We Market Your Home: Photos, Drone & Video | SoldMike', schema=[{'@context': 'https://schema.org', '@type': 'HowTo', 'name': 'How we launch a listing', 'step': [{'@type': 'HowToStep', 'position': i + 1, 'name': t, 'text': d} for i, (t, d) in enumerate(LAUNCH)]}], desc='Every SoldMike listing gets professional photos, drone, video and twilight shots from Toronto Property Media.',
  trail=[('Sell', '/sell/'), ('How we market', '/sell/how-we-market/')])

# =====================================================================
# NEIGHBOURHOODS
# =====================================================================
HOOD_INFO = json.load(open('neighbourhoods.json', encoding='utf-8'))  # schools, parks, commute etc. per area

def living(slug, name):
    d = HOOD_INFO.get(slug)
    if not d:
        return todo('Schools, parks, shopping, commute, what is changing')
    def lst(rows):
        return '<ul>%s</ul>' % ''.join('<li><b>%s</b>: %s</li>' % (e(a), e(b)) for a, b in rows)
    return prose('<h3>Schools</h3>', lst(d['schools']), '<h3>Parks and recreation</h3>', lst(d['parks']), '<h3>Shopping and dining</h3>', lst(d['shopping']),
                 '<h3>Getting around</h3>', e(d['commute']), '<h3>What is changing</h3>', lst(d['changing'])) + '<p class="fine">School boundaries change; confirm your address with the school board before you buy.</p>'

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
  lambda: band(cards([('/neighbourhoods/%s/' % s, n, ', '.join(p for p, _ in HOOD_INFO[s]['pockets'][:3]) if s in HOOD_INFO else 'Guide') for s, n, _, _, pk in HOODS])),
  lambda: cta('Not sure which area fits?', 'Tell us what matters most and we will shortlist the neighbourhoods for you.', 'buyer'),
  title='Vaughan & GTA Neighbourhood Guides | SoldMike', desc='Guides to Woodbridge, Vellore, Kleinburg, Maple, Caledon, King City, Nobleton, Sharon and Toronto: prices, schools and what is selling.',
  trail=[('Neighbourhoods', '/neighbourhoods/')])

for slug, name, intro, photo, pockets in HOODS:
    path = '/neighbourhoods/%s/' % slug
    info = HOOD_INFO.get(slug, {})
    pockets = [p for p, _ in info['pockets']] if info else pockets
    qs = [('Is %s a good place to raise a family?' % name, info.get('family_answer', '[Answer yes or no in the first sentence, then schools, parks and community.]')),
          ('How much is a detached home in %s?' % name, '[Price range in the first sentence, from recent sales.]'),
          ('How long does it take to sell a house in %s?' % name, '[Average days on market in the first sentence, then what speeds it up.]'),
          ('How do I get to downtown Toronto from %s?' % name, info.get('commute_answer', '[Drive and transit options in the first sentence.]'))]
    P(path,
      lambda name=name, intro=intro, photo=photo, slug=slug: hero([('Home', '/'), ('Neighbourhoods', '/neighbourhoods/'), (name, '/neighbourhoods/%s/' % slug)], '%s homes for sale & market guide' % name, e(intro) + '<br><small style="color:var(--pale)">Written by Michael Barillari, Broker · Updated %s</small>' % date.today().strftime('%B %Y'), photo),
      lambda name=name, pockets=pockets, slug=slug: band('<div class="two"><div class="stack"><h2>%s at a glance</h2>' % e(name) + kv([
          ('Average sold price, last 90 days', '[$X,XXX,XXX]'), ('Average days on market', '[X] days'), ('Homes for sale right now', 'LIVECOUNT'),
          ('Most common home type', '[Detached]'), ('Homes the OP Team has sold here', '[X]')]) +
          '</div><div class="stack"><h2>Pockets of %s</h2>' % e(name) + cards([('/listings/?area=%s' % slug, p, w) for p, w in (HOOD_INFO[slug]['pockets'] if slug in HOOD_INFO else [(p, '') for p in pockets])]) + '</div></div>'),
      lambda name=name, slug=slug: band(head_block('For sale in %s' % name, 'The newest MLS® listings, refreshed every day.') + live_grid(slug, 6) +
          '<div class="rca-row"><a class="btn navy" href="/listings/?area=%s">See all %s listings</a><a href="https://www.realtor.ca/en" target="_blank" rel="noopener"><img src="https://www.realtor.ca/images/en-ca/powered_by_realtor.svg" width="125" alt="Powered by REALTOR.ca"></a></div>' % (slug, e(name)) + CREA_NOTE, 'tint'),
      lambda name=name, slug=slug: band(head_block('Living in %s' % name) + living(slug, name), narrow=True),
      lambda name=name, qs=qs: band(head_block('%s questions, answered' % name) + faq(qs), 'tint'),
      lambda name=name: cta('Own in %s? See what it is worth.' % name, 'A price range based on real sales on your street.'),
      title='%s Homes for Sale & Area Guide | SoldMike' % name, desc=intro[:155],
      trail=[('Neighbourhoods', '/neighbourhoods/'), (name, path)], head=LISTING_HEAD, js=LISTING_JS,
      schema=[{'@context': 'https://schema.org', '@type': 'Place', 'name': name + ', Ontario', 'address': {'@type': 'PostalAddress', 'addressLocality': name.split(' & ')[0], 'addressRegion': 'ON', 'addressCountry': 'CA'}}])

# =====================================================================
# RESULTS
# =====================================================================
CASES = [
    ('226-via-borghese', '226 Via Borghese St', 'Vellore Village, Vaughan', '$1.69M', '', '[X]%'),
    ('49-walter-proctor', '49 Walter Proctor Rd', 'East Gwillimbury', '[$X,XXX,XXX]', '[X]', 'Over asking'),
    ('2-la-maria-lane', '2 La Maria Lane', 'Maple, Vaughan', '[$X,XXX,XXX]', '[X]', '[X]%'),
]
# the story of each sale: (challenge, what we did, result)
STORIES = {
    '49-walter-proctor': ('The family was selling and buying at the same time, so they needed a strong sale and a smart purchase, with the timing of both lined up.',
                          'We priced the home from recent sales in East Gwillimbury and launched it with full media to draw as many buyers as possible in the first week. On the purchase side, Michael negotiated hard on the home they were buying so they did not overpay.',
                          'The home sold over asking, and the family bought their next home on strong terms. They enjoyed the whole experience so much that they recorded a video testimonial for us.'),
    '226-via-borghese': ('The buyer side on this deal was combative from the first offer, pushing hard on price and terms.',
                         'Michael stayed firm, kept the negotiation on the facts and protected the sellers on every point that mattered, from price to conditions and closing.',
                         'The home sold for $1.69M on the best terms available for the sellers, and they were very happy with how we handled a tough negotiation.'),
    '2-la-maria-lane': ('The home was tenant-occupied, which can make a sale slow and stressful for an owner.',
                    'We guided the sellers through having the tenants move out properly, then got the home cleaned up, prepared and staged before the photos and launch.',
                    'The sellers were very happy with how smooth the process was and excited to move on to their next chapter.'),
}
P('/results/',
  lambda: hero([('Home', '/'), ('Results', '/results/')], 'Case studies', 'How we sold three homes, and what we did when it got hard.'),
  lambda: band('<div class="tbl"><table><thead><tr><th scope="col">Home</th><th scope="col">Area</th><th scope="col">Sold for</th><th scope="col">Days</th><th scope="col">Sale vs list</th><th scope="col"></th></tr></thead><tbody>' +
               ''.join('<tr class="rv"><td class="big">%s</td><td>%s</td><td class="sold">%s</td><td>%s</td><td>%s</td><td><a href="/results/%s/">Case study</a></td></tr>' % (e(a), e(ar), *[('' if unfinished(v) else v) for v in (p, d, s)], sl) for sl, a, ar, p, d, s in CASES) +
               '</tbody></table></div>'),
  lambda: band('<div style="display:flex;flex-wrap:wrap;gap:16px 28px;align-items:center;justify-content:space-between"><div><h2 style="margin:0 0 6px">See all of our recent sales</h2><p style="margin:0;color:var(--muted);max-width:60ch">The full, up-to-date list of homes The OP Team has sold, with prices, is on our sold listings page. A free sign-up is needed to see sold prices.</p></div><a class="btn" href="https://soldmike.ca/sellers/team-sold-listings" target="_blank" rel="noopener">See all recent sales</a></div>', 'tint'),
  lambda: cta('Want results like these?', 'It starts with pricing your home from real sales.'),
  title='Recent Home Sales in Vaughan & Woodbridge | SoldMike', desc='Homes sold by Michael Barillari and The OP Team in Vaughan, Woodbridge and York Region, with days on market and how we did it.',
  trail=[('Case studies', '/results/')])

for sl, a, ar, p, d, s in CASES:
    P('/results/%s/' % sl,
      lambda a=a, ar=ar, sl=sl, p=p: hero([('Home', '/'), ('Results', '/results/'), (a, '/results/%s/' % sl)], 'How we sold %s' % a, e(ar) + ('' if unfinished(p) else ' · Sold for %s' % p)),
      lambda d=d, s=s, p=p, ar=ar, sl=sl: band('<div class="two"><div class="stack"><h2>The numbers</h2>' + kv([r for r in [('Sold for', p), ('Days on market', d), ('Sale vs list', s), ('Area', ar), ('Property type', '[Detached]')] if r[1]]) + '</div><div class="stack"><h2>The story</h2>' +
          prose('<h3>The challenge</h3>', STORIES[sl][0], '<h3>What we did</h3>', STORIES[sl][1], '<h3>The result</h3>', STORIES[sl][2]) + todo('2 to 4 photos from the shoot', 'Final sale price and days on market') + '</div></div>'),
      lambda: cta('Selling a home like this?', 'Get a price range and the plan we would use.'),
      title='How We Sold %s | SoldMike' % a, desc='Case study: how Michael Barillari sold %s in %s.' % (a, ar),
      trail=[('Results', '/results/'), (a, '/results/%s/' % sl)])

P('/reviews/',
  lambda: hero([('Home', '/'), ('Reviews', '/reviews/')], 'What clients say', 'Real Google reviews of The OP Team, Michael\u2019s team at RE/MAX Premier, in the clients\u2019 own words.'),
  lambda: band('<div style="display:flex;flex-wrap:wrap;gap:16px 28px;align-items:center;justify-content:space-between"><div><div style="font-family:var(--display);font-weight:800;font-size:56px;line-height:1;color:var(--navy)">4.9 <span style="color:var(--red)">★</span></div><p style="margin:6px 0 0;color:var(--muted)">The OP Team on Google, from 125 reviews</p></div>'
               '<a class="btn" href="https://www.google.com/maps/place/The+OP+Team/data=!4m2!3m1!1s0x882b2f5d27d9d35d:0x7678e686b4e8701b" target="_blank" rel="noopener">Read all 125 reviews on Google</a></div>', 'tint'),
  lambda: band('<div class="grid3">' + '<figure class="rv" style="margin:0;padding-top:18px;border-top:3px solid var(--red);display:flex;flex-direction:column;gap:12px"><div style="color:var(--red);letter-spacing:3px" aria-label="5 stars">★★★★★</div><blockquote style="margin:0;font-size:18px;line-height:1.55"><p style="margin:0 0 10px">We had a very good experience working with Adam and The OP Team during the sale of our property. The marketing campaign was well organized and effective, and he ensured the property received strong exposure. There were a good number of showings, even in challenging weather conditions, which demonstrated his commitment to the process.</p><p style="margin:0 0 10px">His efforts resulted in multiple offers, and the transaction was managed in a structured and professional manner. He handled last-minute, unforeseen issues efficiently and kept the process moving smoothly.</p><p style="margin:0 0 10px">Overall, his teamwork, communication, and problem-solving approach made the experience positive. We appreciated working with Adam and have already referred him to our friends.</p><p style="margin:0 0 10px">Highly recommended!</p></blockquote><figcaption style="color:var(--muted);font-weight:600">Joy, Seller · Google review of The OP Team</figcaption></figure><figure class="rv" style="margin:0;padding-top:18px;border-top:3px solid var(--red);display:flex;flex-direction:column;gap:12px"><div style="color:var(--red);letter-spacing:3px" aria-label="5 stars">★★★★★</div><blockquote style="margin:0;font-size:18px;line-height:1.55"><p style="margin:0 0 10px">Nick and his team are amazing and I would highly recommend them to anyone looking to invest in real estate. I own 2 properties and both homes were purchased through The OP Team. Transactions were stress free, the advice I received from Nick was honest and they helped us find our family home and our rental property. Nick negotiated to ensure we got the best deal and listened to our wants and needs and delivered! 5 stars to you! Thank you for everything guys!</p></blockquote><figcaption style="color:var(--muted);font-weight:600">Shay J., Buyer and investor · Google review of The OP Team</figcaption></figure><figure class="rv" style="margin:0;padding-top:18px;border-top:3px solid var(--red);display:flex;flex-direction:column;gap:12px"><div style="color:var(--red);letter-spacing:3px" aria-label="5 stars">★★★★★</div><blockquote style="margin:0;font-size:18px;line-height:1.55"><p style="margin:0 0 10px">Terrific brokerage. They are friendly, knowledgeable, experienced, and great people. When you work with them, you’re on a winning team. Guaranteed!</p></blockquote><figcaption style="color:var(--muted);font-weight:600">Jordan R., Client · Google review of The OP Team</figcaption></figure>' + '</div>'),
  lambda: band('<div style="display:flex;flex-wrap:wrap;gap:16px 28px;align-items:center;justify-content:space-between"><div><h2 style="margin:0 0 6px">Worked with Michael?</h2><p style="margin:0;color:var(--muted)">A quick Google review helps other families find him. It takes a minute.</p></div><a class="btn" href="https://g.page/r/CUnI0PXgvuaXECE/review" target="_blank" rel="noopener">Review Michael on Google</a></div>', 'tint'),
  lambda: cta('Ready to be the next review?', 'Start with a free home value or a buyer consultation.'),
  title='Client Reviews | Michael Barillari, SoldMike', desc='Google reviews of The OP Team at RE/MAX Premier (4.9 stars, 125 reviews) from buyers and sellers in Vaughan and Woodbridge.',
  trail=[('Reviews', '/reviews/')])

P('/market-reports/',
  lambda: hero([('Home', '/'), ('Market reports', '/market-reports/')], 'Vaughan market reports', 'Every month on the 5th: what sold, for how much, how fast, and what it means for you.'),
  lambda: band('<div class="two"><div class="stack">' + prose('<h2>Get the report by email</h2>', 'Each month we break down what sold in Vaughan, Woodbridge, Kleinburg, King and Caledon, for how much and how fast, and what it means if you are buying or selling. Sign up and the next report comes straight to your inbox.') +
               todo('Publish one report on the 5th of every month: average price, sales, new listings, days on market, sale-to-list, by area', 'Embed or link the matching YouTube market update') + '</div>' + form('report') + '</div>'),
  noindex=True,  # until the first report is published
  title='Vaughan Real Estate Market Reports | SoldMike', desc='Monthly Vaughan and Woodbridge real estate market reports: prices, sales, days on market and what it means for buyers and sellers.',
  trail=[('Market reports', '/market-reports/')])

P('/market-reports/vaughan-october-2026/',
  lambda: hero([('Home', '/'), ('Market reports', '/market-reports/'), ('October 2026', '/market-reports/vaughan-october-2026/')], 'Vaughan real estate market: October 2026', 'Published [October 5, 2026] by Michael Barillari, Broker.'),
  lambda: band('<div class="stack">' + kv([('Average sold price', '[$X,XXX,XXX]'), ('Change vs last year', '[X]%'), ('Homes sold', '[X]'), ('New listings', '[X]'), ('Average days on market', '[X]'), ('Average sale-to-list', '[X]%')]) +
               todo('Lead with the one-sentence answer: is it a buyer’s or seller’s market this month and why', 'Breakdown by Woodbridge, Kleinburg, Maple, Vellore', 'What it means for buyers / for sellers', 'Source: TRREB Market Watch') + '</div>', narrow=True),
  lambda: cta('What does this mean for your home?', 'Get a price range from this month’s sales.'),
  noindex=True,  # numbers still to come from Michael
  title='Vaughan Real Estate Market Report, October 2026 | SoldMike', desc='Vaughan real estate market update for October 2026: average price, sales, days on market and sale-to-list ratio.',
  trail=[('Market reports', '/market-reports/'), ('October 2026', '/market-reports/vaughan-october-2026/')],
  schema=[{'@context': 'https://schema.org', '@type': 'Article', 'headline': 'Vaughan real estate market: October 2026', 'author': {'@id': SITE + '/#michael'}}])

# =====================================================================
# QUESTIONS
# =====================================================================
BUY_QS = [
    ('How much do I need for a down payment in Ontario?', 'At least 5% of the first $500,000 and 10% of the portion between $500,000 and $1.5 million. Homes priced at $1.5 million or more need 20% down.'),
    ('What closing costs should buyers budget for?', 'Plan for about 2% of the purchase price on top of your down payment. Most of it is Ontario land transfer tax (about $22,500 on a $1.3 million home in Vaughan), plus legal fees, title insurance, a home inspection and adjustments for property tax the seller prepaid. Toronto buyers also pay the municipal land transfer tax, which roughly doubles the tax.'),
    ('Do first-time buyers get a land transfer tax rebate?', 'Yes. Ontario refunds up to $4,000 of the provincial land transfer tax, and the City of Toronto refunds up to $4,475 of its municipal tax, so a first-time buyer in Toronto can save up to $8,475. You must never have owned a home anywhere in the world and must move in within nine months. Your lawyer claims the refund at closing.'),
    ('Should I buy first or sell first?', 'In most cases, sell first, or line up both closings for the same day. Selling first tells you exactly how much you can spend and avoids carrying two homes. Buying first gives you time to find the right home but can force a rushed sale; if you do, ask your lender about a bridge loan to cover the gap.'),
    ('How do bidding wars work in Ontario?', 'When a seller sets an offer date, every buyer sends their best offer by that date and the seller can accept, sign back or turn down any of them. Since December 1, 2023, sellers in Ontario may choose to share the details of competing offers, but many still do not. To compete, come in with a strong price, a solid deposit and as few conditions as possible, with your financing and inspection sorted before the offer date.'),
    ('Is it better to buy pre-construction or resale?', 'It depends on when you need to move. Resale lets you move in within months, see exactly what you are buying and avoid construction delays. Pre-construction spreads out the deposit and gets you a brand-new home, but closings can be delayed for years and you may pay extra development charges at closing. Buyers who need a home soon usually do better with resale.'),
    ('How long does it take to buy a house?', 'Most buyers take one to three months to find the right home, then 30 to 90 days to close. Getting pre-approved before you start saves time, and a firm deal can close in about 30 days if your lender and lawyer are ready.'),
    ('Do I need a home inspection?', 'Yes, for almost every resale home. An inspection usually costs $400 to $700 in the GTA and takes two to three hours. When there is an offer date, buyers often inspect before it so they can make a firm offer.'),
    ('What is a status certificate?', 'A package from a condo corporation showing its finances, reserve fund, rules and any lawsuits. Buyers usually make their offer conditional on their lawyer reviewing it.'),
    ('How much deposit do I need when I buy a house in Ontario?', 'In the GTA, a deposit of about 5% of the price is common, usually due within 24 hours of your offer being accepted. It is held in trust by the listing brokerage and counts toward your down payment on closing.'),
    ('How much is land transfer tax on a $1.5 million home in Vaughan?', 'About $26,475. Ontario charges 0.5% on the first $55,000, 1% up to $250,000, 1.5% up to $400,000 and 2% up to $2 million. First-time buyers can get up to $4,000 of that refunded. In Toronto you also pay a municipal land transfer tax of about the same amount.'),
    ('Can I back out of buying a house in Ontario?', 'Not once the deal is firm. Resale homes have no cooling-off period, so your conditions (financing, inspection, status certificate) are your way out, and only until their deadlines. New condos bought from a builder are the exception, with a 10-day cooling-off period.'),
    ('What is the mortgage stress test?', 'Lenders check that you could still afford your payments at a higher rate: currently the greater of 5.25% or your mortgage rate plus 2%. It lowers how much you can borrow, so get pre-approved before you start looking.'),
    ('Does it cost me anything to use a buyer agent?', "Usually nothing out of pocket. In most sales, the seller's brokerage offers to pay the buyer's brokerage from the sale proceeds. Since December 1, 2023, buyers sign a written buyer representation agreement that sets the commission, and if the seller offers less than that amount, the buyer may owe the difference. Michael goes through this with you before you see a single home."),
]
SELL_QS = [
    ('How much is my Woodbridge home worth?', 'It depends most on what similar homes on nearby streets sold for in the last few months. We pull those sales and send you a price range with the comparables attached.'),
    ('When is the best time to sell in Vaughan?', 'Spring, from March to early June, usually brings the most buyers in Vaughan, with a second, smaller wave in September and October. Families want to move before the new school year, so both listings and sales rise in spring. The best time for you also depends on how many similar homes are for sale; fewer listings in winter can mean less competition for your home.'),
    ('What does it cost to sell a house in Ontario?', 'The main costs are real estate commission plus 13% HST on it, legal fees, and paying out your mortgage, including any penalty. Sellers do not pay land transfer tax.'),
    ('Should I stage my home?', 'Yes, in most cases. Staged homes photograph better and help buyers picture living there, and most buyers see your home online before they see it in person. Cost ranges from a few hundred dollars for a consultation using your own furniture to several thousand for a vacant home. Michael tells you which rooms matter most.'),
    ('Should I hold an offer date or take offers any time?', 'Hold an offer date when you expect several buyers, and take offers any time when the market is slower or the home is one of a kind. An offer date, usually about a week after listing, gives every buyer time to see the home and can create competition. If few buyers are active it can backfire, so we look at showings and the market that week before deciding.'),
    ('What renovations add the most value before selling?', 'Paint, lighting and small repairs return the most. Fresh neutral paint, bright modern light fixtures, fixing leaky taps, cracked tiles and worn caulking, and a tidy front yard cost little and change how buyers see the home. Big projects like a new kitchen rarely pay back their full cost right before a sale.'),
    ('How long does it take to sell a house in Vaughan?', '[Average days on market in the first sentence, from TRREB data.]'),
    ('Can I sell my house while I still have a mortgage?', 'Yes. Your lawyer pays out the mortgage from the sale proceeds on closing day. Ask your lender about any prepayment penalty first.'),
    ('Do I need a lawyer to sell my house in Ontario?', 'Yes. A real estate lawyer transfers the title to the buyer, pays out your mortgage from the sale proceeds and handles the closing funds. Hire one as soon as your deal is firm.'),
    ('What is a bully offer?', 'An offer sent before the seller\u2019s offer date, usually strong and open for only a few hours, to try to buy the home before other buyers compete. The seller can accept it, counter it or ignore it and wait for the offer date.'),
    ('Do I pay capital gains tax when I sell my home?', 'Usually not on your principal residence: the principal residence exemption generally covers the gain on the home you live in. Investment and rental properties are taxable, so talk to your accountant before you sell one.'),
    ('Can I sell my house with tenants in it?', 'Yes. The tenancy carries on with the new owner unless the buyer, or a close family member, will move in. In that case the tenant gets an N12 notice with at least 60 days, ending on the last day of a rental period, and one month\u2019s rent as compensation. We plan the timing with you before listing.'),
    ('What happens if my home does not sell?', 'We change something: usually the price, the presentation or the plan. If a home sits, buyers are telling us the price does not match what they see. We review showing feedback, compare against what sold nearby, refresh the photos and description, and decide together whether to adjust the price or relaunch.'),
    ('Why choose a local Vaughan realtor?', 'A local realtor knows the streets, the recent sales and the buyers in your area, which means sharper pricing and better negotiation. Michael has been licensed since December 2011, works out of the RE/MAX Premier office on Rutherford Road in Vaughan, and his own media company, Toronto Property Media, shoots every listing.'),
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
# designation logos under Michael's photo (official artwork, same height, white on navy)
DESIGNATIONS = ('<div class="desig white" aria-label="Designations">'
    + ''.join('<figure><span><img class="c" src="/assets/designations/%s.png" alt="%s"><img class="w" src="/assets/designations/%s-white.png" alt="" aria-hidden="true"></span><figcaption><b>%s</b>%s</figcaption></figure>' % (f, alt, f, ab, full)
              for f, alt, ab, full in [('rene', 'RENE, Real Estate Negotiation Expert', 'RENE', 'Real Estate Negotiation Expert'),
                                       ('srs', 'SRS, Seller Representative Specialist', 'SRS', 'Seller Representative Specialist'),
                                       ('abr', 'ABR, Accredited Buyer Representative', 'ABR®', 'Accredited Buyer Representative')])
    + '</div>')

P('/about/',
  lambda: hero([('Home', '/'), ('About', '/about/')], 'Michael Barillari, Broker', 'SOLDMIKE. RE/MAX Premier The OP Team, Vaughan & Woodbridge.'),
  lambda: band('<div class="person"><div><div class="pic"><img src="/mike.png" alt="Michael Barillari"></div>' + DESIGNATIONS + '</div><div class="stack">' + prose(
      'Michael Barillari is a Broker with RE/MAX Premier The OP Team in Vaughan. Licensed since %s, he helps buyers and sellers across Vaughan, Woodbridge, Kleinburg, King, Caledon, Toronto and the rest of the GTA.' % LICENSED,
      'He works with first-time buyers, growing families, luxury and estate homes, investors and commercial clients. His approach is friendly, fair and firm: honest advice on price, strong negotiation, and a marketing plan built around how buyers actually search today.',
      'Michael holds the ABR® (Accredited Buyer Representative), SRS (Seller Representative Specialist) and RENE (Real Estate Negotiation Expert) designations, and is an Accredited GreenBroker® for commercial property. He speaks English and Italian.',
      'He brings a passion for architecture and development to every home he prices and markets, and he runs Toronto Property Media, which shoots the photos, drone, video and twilight images for every listing he sells.',
      '<h2>Find Michael online</h2>',
      '<p><a href="%s" target="_blank" rel="noopener">Google</a> · <a href="%s" target="_blank" rel="noopener">RE/MAX</a> · <a href="%s" target="_blank" rel="noopener">REALTOR.ca</a> · <a href="%s" target="_blank" rel="noopener">RankMyAgent (5.0 stars, 14 reviews)</a> · <a href="%s" target="_blank" rel="noopener">LinkedIn</a></p>' % tuple(PROFILES)) +
      todo('A short personal story: how you started and what you do differently', 'Awards (verifiable)', 'A personal line: family, community, what you do outside work') + '</div></div>'),
  lambda: band(cards([('/about/the-op-team/', 'The OP Team', 'Who you work with'), ('/videos/', 'Videos', 'Market updates and neighbourhood tours'), ('/reviews/', 'Reviews', 'What clients say'), ('/join/', 'Join the team', 'Getting started as a realtor')]), 'tint'),
  lambda: cta('Talk to Michael', 'Buying, selling or just have a question. Call or text %s.' % PHONE, 'contact'),
  title='Michael Barillari, Broker | SOLDMIKE | RE/MAX Premier The OP Team', desc='Michael Barillari, Broker, RE/MAX Premier The OP Team, licensed since 2011. ABR, SRS, RENE. Serving Vaughan, Woodbridge, Kleinburg, King, Caledon and Toronto.',
  trail=[('About', '/about/')],
  schema=[{'@context': 'https://schema.org', '@type': 'Person', 'name': 'Michael Barillari', 'jobTitle': 'Broker', 'worksFor': {'@type': 'Organization', 'name': BROKERAGE}, 'url': SITE + '/about/', 'image': SITE + '/mike.png', 'knowsLanguage': ['English', 'Italian'], 'hasCredential': [{'@type': 'EducationalOccupationalCredential', 'name': n} for n in DESIGNATION_NAMES], 'sameAs': PROFILES}])

P('/about/the-op-team/',
  lambda: hero([('Home', '/'), ('About', '/about/'), ('The OP Team', '/about/the-op-team/')], 'The OP Team', 'RE/MAX Premier The OP Team Inc., Brokerage.'),
  lambda: band(prose(
      'The OP Team is a real estate team at RE/MAX Premier in Vaughan, led by Nick Oppedisano and Angela Oppedisano. The team helps buyers, sellers and investors across Toronto, York, Peel, Durham, Simcoe and Halton Hills.',
      'Together, Michael Barillari and The OP Team have more than 2,000 transactions of combined experience, and The OP Team holds a 4.9-star Google rating from 125 reviews.',
      '<h2>What the team does</h2>',
      '<ul><li>Selling homes, with in-house photos, drone, video and twilight by Toronto Property Media</li><li>Buying resale and pre-construction homes</li><li>Leasing and investment properties</li><li>Free home valuations</li></ul>',
      'Their tagline says it best: <i>Put us on your lawn, your house will be gone!</i>',
      '<p><a class="btn ghost" href="https://theopteam.ca/" target="_blank" rel="noopener">Visit theopteam.ca</a> <a class="btn ghost" href="/reviews/">Read client reviews</a></p>') +
      todo('Team members: photo, name, role, one line each'), narrow=True),
  lambda: cta('Work with the team', 'Start with Michael. He brings in the right people at each step.', 'contact'),
  title='The OP Team | RE/MAX Premier | SoldMike', desc='RE/MAX Premier The OP Team Inc., Brokerage: the team behind SoldMike in Vaughan and Woodbridge.',
  trail=[('About', '/about/'), ('The OP Team', '/about/the-op-team/')])

P('/videos/',
  lambda: hero([('Home', '/'), ('Videos', '/videos/')], 'Videos', 'Market updates, neighbourhood tours and listing films from Michael and Toronto Property Media.', '/hero.jpg'),
  lambda: band(todo('Link the YouTube channel once it launches', 'Feature 3 videos: a monthly market update, a neighbourhood tour, a listing film', 'Title each by area so AI tools can quote them (for example "Woodbridge market update, October 2026")'), narrow=True),
  noindex=True,  # thin until written
  title='Real Estate Videos: Vaughan Market Updates & Tours | SoldMike', desc='Vaughan market updates, neighbourhood tours and listing videos from Michael Barillari.',
  trail=[('Videos', '/videos/')])

P('/join/',
  lambda: hero([('Home', '/'), ('Join the team', '/join/')], 'Getting started as a realtor', 'Thinking about a career in real estate, or licensed and looking for a team? Here is how we help new agents get going.'),
  lambda: band('<div class="two"><div class="stack">' + prose('<h2>How to get licensed in Ontario</h2>',
      '<ol><li><b>Take the pre-registration program.</b> The Ontario Real Estate Salesperson Program (delivered by Humber Polytechnic and partner colleges) has five courses and two simulations, to be finished within 24 months.</li>'
      '<li><b>Join a brokerage and register with RECO</b> within 12 months of finishing. This is where The OP Team comes in.</li>'
      '<li><b>Finish the post-registration (articling) courses</b> within your first 24 months as a registered salesperson.</li></ol>',
      'Most people finish the courses in 9 to 18 months while working. Budget roughly $4,500 to $5,500 for tuition and exams.',
      '<h2>Why start with The OP Team</h2>',
      'You learn from agents with 2,000+ transactions of combined experience, at a RE/MAX office in Vaughan, with in-house media from Toronto Property Media for your listings. Michael started in 2011 and is happy to talk about what the first year really looks like.') + todo('What new agents get: training, leads, media, systems, mentorship (confirm specifics)', 'What success looks like in year one') + '</div>' + form('join') + '</div>'),
  title='Join The OP Team | Getting Started as a Realtor | SoldMike', desc='Thinking about becoming a realtor in Ontario or looking for a new team? Join The OP Team at RE/MAX Premier.',
  trail=[('Join the team', '/join/')])

P('/contact/',
  lambda: hero([('Home', '/'), ('Contact', '/contact/')], 'Contact Michael', 'Call or text %s, email %s, or send a message below.' % (PHONE, EMAIL)),
  lambda: band('<div class="two">' + form('contact') + '<div class="stack">' + kv([('Call or text', PHONE), ('Email', EMAIL), ('Office', '%s, %s' % (ADDRESS['street'], ADDRESS['city'])), ('Brokerage', 'RE/MAX Premier The OP Team')]) +
               '<a class="btn ghost" href="https://www.google.com/maps/search/%s" target="_blank" rel="noopener" style="align-self:flex-start">Open the office in Google Maps</a>' % (ADDRESS['street'] + ' ' + ADDRESS['city']).replace(' ', '+') +
               todo('Office hours') + '</div></div>'),
  title='Contact Michael Barillari | SoldMike', desc='Contact Michael Barillari, Broker, RE/MAX Premier The OP Team. Call or text %s.' % PHONE,
  trail=[('Contact', '/contact/')])

P('/free-guide/',
  lambda: hero([('Home', '/'), ('Free guide', '/free-guide/')], 'Free guides to buying and selling in Vaughan', 'The full plan we use with our clients, step by step, in a 10-page PDF you can keep.'),
  lambda: band('<div class="two"><div class="stack">' + prose('<h2>What is inside</h2>',
      '<b>Selling a home in Vaughan:</b> the 15 steps from pricing and prep to offers and closing day, with what you walk away with and how we launch a listing.',
      '<b>Buying a home in Vaughan:</b> the 15 steps from pre-approval and closing costs to winning the offer and getting your keys.',
      'Every step has a checklist, plus Michael\u2019s tips from selling in Vaughan since 2011.') + '</div>' + form('guide') + '</div>'),
  title='Free Guides: Buying and Selling a Home in Vaughan | SoldMike', desc='Download free step-by-step PDF guides to buying and selling a home in Vaughan, with a checklist for every step.', trail=[('Free guide', '/free-guide/')])

P('/privacy/',
  lambda: hero([('Home', '/'), ('Privacy', '/privacy/')], 'Privacy policy', 'How we collect, use and protect your personal information.'),
  lambda: band(prose(
      '<h2>What we collect</h2>',
      'When you fill in a form on this site, sign in at one of our open houses, book a showing or ask about a home, we collect the details you give us, such as your name, email, phone and property address, to reply to you and provide real estate services. Your information goes to Michael Barillari and is stored in our customer relationship system (Follow Up Boss). We do not sell your information.',
      '<h2>Homes you view and save</h2>',
      'After you have sent us your contact details, the listings you view and save on this site (address, MLS® number, price and a link) are recorded in your file in our customer relationship system, so Michael can follow up with homes that fit. This is done automatically by the website. If you have not given us your contact details, your browsing is not linked to you.',
      '<h2>Listing statistics for CREA</h2>',
      'Listings on this site come from The Canadian Real Estate Association (CREA). When you open a listing, we send CREA a record of the view with a random device ID and your IP address, as CREA requires, so listing brokerages can see where their listings are viewed. No name, email or phone number is sent.',
      '<h2>Stored in your browser</h2>',
      'Your saved homes, your answer to the terms-of-use notice, the random device ID and, after you send a form, your contact details (so forms fill in for you) are stored in your own browser. You can clear them at any time by clearing this site\'s data in your browser.',
      '<h2>Other services</h2>',
      'Listing photos load from CREA\'s servers and maps load from OpenStreetMap, so those services receive your IP address when you view them. We protect the listings on this site from automated copying; requests that look automated may be blocked and their IP addresses logged.',
      '<h2>Your choices</h2>',
      'You can ask to see, correct or delete your information at any time, or ask us to stop recording the homes you view, by emailing %s.' % EMAIL) + '<div style="margin-top:20px">' + todo('Have the brokerage review this policy (PIPEDA, CASL for emails, listing activity sent to Follow Up Boss, CREA analytics)') + '</div>', narrow=True),
  title='Privacy Policy | SoldMike', desc='Privacy policy for soldmike.com.', trail=[('Privacy', '/privacy/')], noindex=True)

P('/terms/',
  lambda: hero([('Home', '/'), ('Terms', '/terms/')], 'Terms of use', 'The rules for using this website and its listing information. By using this site you agree to these terms.'),
  lambda: band(prose(
      '<h2>Who runs this site</h2>',
      'This website is operated by Michael Barillari, Broker, of %s, a brokerage and salesperson who are members of The Canadian Real Estate Association (CREA).' % BROKERAGE,
      '<h2>Listing content</h2>',
      'REALTOR®, REALTORS®, and the REALTOR® logo are certification marks that are owned by REALTOR® Canada Inc. and licensed exclusively to The Canadian Real Estate Association (CREA). These certification marks identify real estate professionals who are members of CREA and who must abide by CREA’s By-Laws, Rules, and the REALTOR® Code. The MLS® trademark and the MLS® logo are owned by CREA and identify the quality of services provided by real estate professionals who are members of CREA.',
      'The information contained on this site is based in whole or in part on information that is provided by members of The Canadian Real Estate Association (CREA), who are responsible for its accuracy. CREA reproduces and distributes this information as a service for its members and assumes no responsibility for its accuracy.',
      'The listing content on this website is protected by copyright and other laws, and is intended solely for the private, non-commercial use by individuals. Any other reproduction, distribution or use of the content, in whole or in part, is specifically forbidden. The prohibited uses include commercial use, “screen scraping”, “database scraping”, and any other activity intended to collect, store, reorganize or manipulate data on the pages produced by or displayed on this website.',
      '<h2>Using this site</h2>',
      'This site is for consumers with a genuine interest in buying, selling or leasing real estate. Listing information is refreshed at least once every 24 hours and is deemed reliable but not guaranteed accurate. Each listing shows the brokerage that listed it; homes listed by other brokerages are not our listings, and Michael Barillari can help you with any of them as a buyer’s agent.',
      'Automated access to this site, including bots, scrapers and bulk downloading of listings, is not allowed and may be blocked. Suspected scraping is reported to CREA.',
      'Calculators and estimates on this site are for information only and are not financial, legal or mortgage advice.') + '<div style="margin-top:20px">' + todo('Have the brokerage review these terms') + '</div>', narrow=True),
  title='Terms of Use | SoldMike', desc='Terms of use for soldmike.com, including the CREA listing content terms.', trail=[('Terms', '/terms/')], noindex=True)

# ---------- new-listing alerts (each visitor's own link from the alert email) ----------
ALERTS_JS = """<script>
(function(){
  function go(){var SM=window.SM;if(!SM){return setTimeout(go,50);}
    var q=new URLSearchParams(location.search),t=q.get('t')||'',s=q.get('s')||'',box=document.getElementById('alBox'),h=document.getElementById('alHead');
    if(!t){h.textContent='This page opens from your new-listing email.';return;}
    SM.get('/api/alerts/get?t='+encodeURIComponent(t)+'&s='+encodeURIComponent(s)).then(function(j){
      h.textContent=(j.first?j.first+', here are ':'Here are ')+'the new listings that match your search.';
      document.getElementById('alLabel').textContent=j.search?j.search.label:'';
      SM.cards(box,j.items,'No new matches yet. We check every morning and email you when something new comes up.');
      var st=document.getElementById('alStop');
      if(j.unsub||!j.search||!j.search.active){st.innerHTML='<p>New-listing emails are off for you. Want them back? <a href="/contact/">Let Michael know</a>.</p>';return;}
      st.hidden=false;
      document.getElementById('alStopBtn').onclick=function(){var b=this;b.disabled=true;
        SM.post('/api/alerts/stop',{t:t}).then(function(r){if(!r.ok)throw 0;st.innerHTML='<p><b>Done.</b> You will not get any more new-listing emails from this site.</p>';}).catch(function(){b.disabled=false;alert('That did not go through. Please try again or email '+'"""+EMAIL+"""'+'.');});};
    }).catch(function(){h.textContent='This link has expired.';box.innerHTML='<p><a class="btn" href="/listings/">Search all homes</a></p>';});
  }
  go();
})();
</script>"""
P('/alerts/',
  lambda: hero([('Home', '/'), ('Your new listings', '/alerts/')], 'Your new listings', '<span id="alHead">Loading…</span>'),
  lambda: band('<p id="alLabel" style="font-weight:600;color:var(--navy);margin:0 0 18px"></p><div class="lgrid" id="alBox"></div>'
      '<div class="rca-row"><a class="btn ghost" href="/listings/">Search all homes</a><a href="https://www.realtor.ca/en" target="_blank" rel="noopener"><img src="https://www.realtor.ca/images/en-ca/powered_by_realtor.svg" width="125" alt="Powered by REALTOR.ca"></a></div>'
      '<div id="alStop" hidden style="margin-top:28px;padding-top:20px;border-top:1px solid var(--line)"><p>Don’t want these emails any more?</p><button class="btn ghost" type="button" id="alStopBtn">Stop new-listing emails</button></div>'
      + CREA_NOTE, 'lsband'),
  title='Your New Listings | SoldMike', desc='New listings that match your saved search.', trail=[('Your new listings', '/alerts/')], noindex=True,
  head=LISTING_HEAD, js=LISTING_JS + ALERTS_JS)

# ---------- pre-listing package (send to sellers before the listing appointment) ----------
PRELIST_VIDEO = ''  # YouTube video ID for Michael's intro video, e.g. 'dQw4w9WgXcQ'; the video block shows once set
def tiles(rows):
    return '<div class="cards">' + ''.join('<div class="rv" style="background:var(--white);padding:26px 22px;display:flex;flex-direction:column;gap:10px"><b style="font-family:var(--display);font-size:22px;text-transform:uppercase;color:var(--navy)">%s</b><span style="color:var(--muted)">%s</span></div>' % (e(t), d) for t, d in rows) + '</div>'
def statrow(rows):
    return '<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:24px">' + ''.join('<div><div style="font-family:var(--display);font-weight:800;font-size:52px;line-height:1;color:var(--navy)">%s</div><p style="margin:6px 0 0;color:var(--muted)">%s</p></div>' % (n, e(t)) for n, t in rows) + '</div>'
GF = '/media/gentle-fox/'
PHOTOS = [(GF + f + '.jpg', a, c) for f, a, c in [('twilight-street', 'Stone home at twilight', 'Twilight'), ('drone-front', 'Drone view of the home and street', 'Drone'), ('kitchen', 'Kitchen island with bar stools', 'Kitchen'), ('backyard-twilight', 'Backyard and pool at twilight', 'Twilight'), ('drone-overhead', 'Overhead drone view of the backyard pool', 'Drone'), ('kitchen-2', 'Kitchen with stainless appliances', 'Kitchen'), ('primary-bedroom', 'Primary bedroom', 'Bedroom'), ('pool', 'Backyard pool and cabana', 'Outdoor living'), ('details', 'Range and stone countertop', 'Details')]]
def bullets(rows):
    return '<ul style="list-style:none;padding:0;margin:0;display:flex;flex-direction:column;gap:12px">' + ''.join('<li style="display:flex;gap:12px;align-items:flex-start"><span style="flex:none;width:26px;height:26px;border-radius:50%%;background:var(--red);color:#fff;display:grid;place-items:center;font-weight:700;font-size:14px">✓</span><span>%s</span></li>' % r for r in rows) + '</ul>'
P('/sell/pre-listing/',
  lambda: hero([('Home', '/'), ('Sell', '/sell/'), ('Pre-listing package', '/sell/pre-listing/')], 'Your home, presented by SoldMike', 'How we price it, show it and sell it. Take a look before we meet.', GF + 'twilight-street.jpg'),
  lambda: band(statrow([('2,000+', 'transactions, Michael and The OP Team combined'), ('4.9<span style="color:var(--red)">★</span>', 'Google rating, 125 reviews'), ('2011', 'selling in Vaughan since'), ('RENE', 'Negotiation Expert · SRS · ABR®')]) + '<p class="fine" style="margin-top:16px">Transactions: The OP Team and Michael Barillari combined, as of October 2026. Google rating of The OP Team as of October 2026.</p>'),
  lambda: band(head_block('A message from Michael') + '<div style="position:relative;padding-top:56.25%%;border-radius:8px;overflow:hidden"><iframe src="https://www.youtube-nocookie.com/embed/%s" title="Michael Barillari introduces his selling plan" style="position:absolute;inset:0;width:100%%;height:100%%;border:0" allow="encrypted-media; picture-in-picture" allowfullscreen loading="lazy"></iframe></div>' % PRELIST_VIDEO, narrow=True) if PRELIST_VIDEO else '',
  lambda: band(head_block('Your home, on every screen', 'Real work from a recent listing, 38 Gentle Fox Dr, shot by our own team at Toronto Property Media.') +
      '<div style="display:grid;grid-template-columns:minmax(0,2fr) minmax(0,1fr);gap:24px;align-items:start" class="gfmedia">'
      '<figure style="margin:0"><div style="position:relative;padding-top:56.25%;border-radius:8px;overflow:hidden;background:#000"><iframe src="https://player.vimeo.com/video/1230922393?title=0&amp;byline=0&amp;portrait=0&amp;dnt=1" title="Video tour of 38 Gentle Fox Dr" style="position:absolute;inset:0;width:100%;height:100%;border:0" allow="autoplay; fullscreen; picture-in-picture" allowfullscreen loading="lazy"></iframe></div><figcaption class="fine" style="margin-top:8px"><b>Cinematic video tour</b> for MLS®, YouTube and social media</figcaption></figure>'
      '<figure style="margin:0;max-width:360px;justify-self:center;width:100%"><div style="border:10px solid #141833;border-radius:34px;overflow:hidden;background:#fff"><iframe src="https://www.instagram.com/reel/Dd6ckWQx664/embed/" title="Instagram reel of 38 Gentle Fox Dr" style="display:block;width:100%;height:620px;border:0" loading="lazy" scrolling="no"></iframe></div><figcaption class="fine" style="margin-top:8px;text-align:center"><b>Reels</b> for Instagram, Facebook and TikTok</figcaption></figure></div>'
      '<style>@media(max-width:760px){.gfmedia{grid-template-columns:1fr!important}}</style>', 'tint'),
  lambda: band(head_block('Photos that sell', 'Twilight, drone and interiors. Most buyers see your home online first.') + '<div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:10px">' + ''.join(
      '<figure style="margin:0;position:relative"><img src="%s" alt="%s" loading="lazy" style="width:100%%;aspect-ratio:3/2;object-fit:cover;border-radius:6px;display:block"><figcaption style="position:absolute;left:10px;bottom:10px;background:rgba(20,24,51,.8);color:#fff;font-weight:600;font-size:14px;padding:4px 10px;border-radius:4px">%s</figcaption></figure>' % (i, e(a), e(c))
      for i, a, c in PHOTOS) + '</div><p style="margin-top:20px"><a class="btn ghost" href="/sell/how-we-market/">How we market a home</a> <a class="btn ghost" href="https://torontopropertymedia.ca/" target="_blank" rel="noopener">Toronto Property Media</a></p>'),
  lambda: band(head_block('We start with you') + tiles([
      ('Your price', 'What you hope for, and what you need to net.'),
      ('Your timing', 'When you move, and whether you are buying too.'),
      ('Your why', 'Moving up, downsizing, relocating or an estate.'),
      ('Your concerns', 'Kids, pets, tenants, repairs. We plan around them.')]), 'tint'),
  lambda: band(head_block('The SoldMike advantage') + tiles([
      ('Our own media team', 'Photos, drone, video, twilight and reels by Toronto Property Media.'),
      ('Priced from real sales', 'The homes that sold near you, not online guesses.'),
      ('Trained negotiator', 'RENE and SRS designations. It shows on offer night.'),
      ('Prep and staging', 'A clear prep list, staging advice and trusted trades.'),
      ('No buyer missed', 'Every inquiry and visitor followed up, fast.')])),
  lambda: band(head_block('Your 8-step launch plan') + steps(LAUNCH), 'tint'),
  lambda: band('<div class="two"><div class="stack"><h2>How we price it</h2>' + bullets(['Recent sales closest to your home', 'Your competition: what is for sale right now', 'A price range, our list price and your net after costs']) +
      '<p style="margin-top:8px"><a class="btn" href="/sell/home-value/">Get your home value</a> <a class="btn ghost" href="/sell/cost-to-sell-vaughan/">Cost to sell</a></p></div><div class="stack"><h2>How we win the offer</h2>' +
      bullets(['Offer date or any time, chosen for your home', 'Every offer compared: price, deposit, conditions, closing', 'Feedback after every showing, an update every week, Michael with you on offer night']) + '</div></div>'),
  lambda: band(head_block('Homes we have sold') + cards([('/results/%s/' % sl, a, ar) for sl, a, ar, _, _, _ in CASES]) +
      '<p style="margin-top:20px"><a class="btn ghost" href="https://soldmike.ca/sellers/team-sold-listings" target="_blank" rel="noopener">See all recent sales</a> <a class="btn ghost" href="/reviews/">Read client reviews</a></p>', 'tint'),
  lambda: band('<div class="two"><div class="stack">' + prose('<h2>Take the seller guide with you</h2>', 'All 15 steps, with a checklist for each, in a free 10-page PDF.') + '</div>' + form('guide', '-pl', 'Selling a home in Vaughan') + '</div>'),
  lambda: cta("Let's get your home SOLDMIKE", 'Book your listing consultation. Call or text %s, or send your address below.' % PHONE),
  title='Pre-Listing Package: How We Sell Your Home | SoldMike', desc='Before we meet: our video tours, reels, photography, 8-step launch plan, pricing and offer strategy, and homes Michael Barillari has sold.',
  trail=[('Sell', '/sell/'), ('Pre-listing package', '/sell/pre-listing/')])


# ---------- homepage menu (index.html is hand-edited; its menu comes from NAV so it always matches) ----------
def home_nav():
    out = []
    for label, items in NAV:
        if isinstance(items, str):
            out.append('<a href="%s" target="_blank" rel="noopener">%s</a>' % (items, e(label)))
            continue
        links = ''.join('<a href="%s">%s</a>' % (u, e(t)) for u, t in items)
        out.append('<div class="dd"><button type="button" aria-expanded="false">%s</button><div class="menu">%s</div></div>' % (label, links))
    return '<nav class="nav" id="mainnav" aria-label="Main">%s<a class="btn" href="/sell/home-value/">Home value</a></nav>' % ''.join(out)
idx = open('index.html', encoding='utf-8').read()
a, b = idx.index('<!--NAV-->') + len('<!--NAV-->'), idx.index('<!--/NAV-->')
open('index.html', 'w', encoding='utf-8').write(idx[:a] + '\n    ' + home_nav() + '\n    ' + idx[b:])

# ---------- 404, sitemap, robots, checklist ----------
PAGE = '/404'
page404 = ('<!doctype html><html lang="en-CA"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Page not found | SoldMike</title><meta name="robots" content="noindex">'
           '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@700;800&family=Barlow:wght@400;600&display=swap"><link rel="stylesheet" href="/assets/site.css?v=8"></head><body>'
           + header('/404') + '<main id="main">' + hero([('Home', '/'), ('Not found', '/404')], 'That page has moved', 'The page you were looking for is not here. Try one of these instead.') +
           band(cards([('/listings/', 'Search homes', 'Every MLS® listing'), ('/sell/home-value/', 'Home value', 'What your home is worth'), ('/neighbourhoods/', 'Neighbourhoods', 'Area guides'), ('/contact/', 'Contact', 'Talk to Michael')])) + '</main>' + footer() + '<script src="/assets/site.js?v=9" defer></script><script src="/assets/chat.js?v=7" defer></script></body></html>')
open('404.html', 'w', encoding='utf-8').write(page404)

today = date.today().isoformat()
urls = ['/'] + SITEMAP
open('sitemap.xml', 'w').write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' +
                               ''.join('  <url><loc>%s%s</loc><lastmod>%s</lastmod></url>\n' % (SITE, u, today) for u in urls) + '</urlset>\n')
# AI crawlers may read the guides and answers, never the listing pages (CREA DDF Rules 5(k) anti-scraping; PropTx: no listing data to AI)
AI_BOTS_OPEN = ['GPTBot', 'OAI-SearchBot', 'ChatGPT-User', 'ClaudeBot', 'Claude-SearchBot', 'Claude-User', 'PerplexityBot', 'Perplexity-User', 'Google-Extended', 'Applebot-Extended']
AI_BOTS_BLOCKED = ['CCBot', 'Bytespider', 'meta-externalagent', 'Amazonbot', 'cohere-ai', 'Diffbot', 'Timpibot', 'AI2Bot']
LISTING_PATHS = ['/homes/', '/listings/', '/saved/', '/alerts/', '/leads/', '/admin/']
robots = 'User-agent: *\nAllow: /\n' + ''.join('Disallow: %s\n' % p for p in LISTING_PATHS[2:]) + '\n'
robots += ''.join('User-agent: %s\n' % b for b in AI_BOTS_OPEN) + 'Allow: /\n' + ''.join('Disallow: %s\n' % p for p in LISTING_PATHS) + '\n'
robots += ''.join('User-agent: %s\n' % b for b in AI_BOTS_BLOCKED) + 'Disallow: /\n\n'
robots += 'Sitemap: %s/sitemap.xml\n' % SITE + ('Sitemap: %s/homes/sitemap.xml\n' % SITE if HOMES_LIVE else '')
open('robots.txt', 'w').write(robots)

with open('CONTENT-TODO.md', 'w') as f:
    f.write('# soldmike.com content to write\n\nGenerated by build.py on %s. Every yellow "Content to write" box on the site is listed here, page by page.\n\n' % today)
    seen = {}
    for p, items in TODOS:
        seen.setdefault(p, []).extend(items)
    for p, items in seen.items():
        f.write('## %s%s\n' % (SITE, p) + ''.join('- [ ] %s\n' % i for i in items) + '\n')
print('pages:', len(SITEMAP), 'todo items:', sum(len(i) for _, i in TODOS))
