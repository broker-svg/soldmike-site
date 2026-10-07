"""Social share cards: one 1200x630 og/<slug>.jpg per page, so Facebook, LinkedIn, iMessage and
WhatsApp show the page's own headline and photo instead of the same hero shot every time.

Run from the repo root after build.py:  python3 tools/og.py        (only redraws cards that changed)
                                        python3 tools/og.py --all  (redraw everything)
Needs Google Chrome (headless screenshot), poppler (pdftoppm) for the guide covers, and macOS sips."""
import hashlib, html, json, os, subprocess, sys, tempfile

CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
OG = os.path.join(ROOT, 'og')
GUIDES = ['guides/selling-a-home-in-vaughan.pdf', 'guides/buying-a-home-in-vaughan.pdf']
e = html.escape

def f(p):
    return 'file://' + os.path.join(ROOT, p.lstrip('/'))

CSS = '''
*{box-sizing:border-box;margin:0}
html,body{width:1200px;height:630px;overflow:hidden;background:#141833}
body{font-family:'Barlow',system-ui,sans-serif;color:#fff;position:relative}
.ph{position:absolute;inset:0;background-size:cover;background-position:center}
.shade{position:absolute;inset:0;background:linear-gradient(90deg,rgba(20,24,51,.96) 0%,rgba(29,40,112,.88) 42%,rgba(29,40,112,.25) 75%,rgba(29,40,112,0) 100%)}
.bar{position:absolute;left:0;top:0;bottom:0;width:14px;background:#D7141E}
.in{position:absolute;left:72px;top:58px;bottom:56px;width:640px;display:flex;flex-direction:column}
.logo{height:62px;width:auto;align-self:flex-start}
.k{margin-top:auto;display:inline-block;align-self:flex-start;background:#D7141E;color:#fff;font:700 24px/1 'Barlow Condensed',sans-serif;letter-spacing:.12em;text-transform:uppercase;padding:10px 16px 9px}
h1{margin-top:18px;font:800 var(--fs,76px)/.98 'Barlow Condensed',sans-serif;text-transform:uppercase;letter-spacing:.005em;text-shadow:0 2px 18px rgba(0,0,0,.35)}
.by{margin-top:28px;display:flex;align-items:center;gap:16px;font:500 22px/1.25 'Barlow',sans-serif;color:#E6E9F7}
.by img{width:64px;height:64px;border-radius:50%;object-fit:cover;object-position:50% 18%;border:3px solid #fff}
.by b{display:block;color:#fff;font-weight:600}
.url{position:absolute;right:44px;bottom:40px;font:700 28px/1 'Barlow Condensed',sans-serif;letter-spacing:.06em;background:#fff;color:#1D2870;padding:12px 18px 10px}
.covers{position:absolute;right:40px;top:80px;width:500px;height:430px}
.covers img{position:absolute;width:255px;box-shadow:0 22px 50px rgba(0,0,0,.55);border:1px solid rgba(255,255,255,.4)}
.covers img:first-child{left:0;top:50px;transform:rotate(-7deg);z-index:1}
.covers img:last-of-type{right:0;top:0;transform:rotate(5deg)}
.free{position:absolute;right:-14px;bottom:40px;width:150px;height:150px;border-radius:50%;background:#D7141E;display:flex;align-items:center;justify-content:center;text-align:center;font:800 40px/.9 'Barlow Condensed',sans-serif;text-transform:uppercase;transform:rotate(10deg);box-shadow:0 10px 30px rgba(0,0,0,.4);z-index:2}
'''

def fs(text):
    n = len(text)
    return 92 if n <= 22 else 80 if n <= 34 else 70 if n <= 48 else 60

def card_html(c, covers):
    head = ('<!doctype html><html><head><meta charset="utf-8">'
            '<link href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@700;800&family=Barlow:wght@500;600&display=block" rel="stylesheet">'
            '<style>%s</style></head><body>' % CSS)
    if c['layout'] == 'guides':
        bg = '<div class="ph" style="background:linear-gradient(120deg,#141833,#1D2870 60%%,#2A3A9A)"></div>'
        side = '<div class="covers">%s<div class="free">Free<br>PDF</div></div>' % ''.join('<img src="%s">' % x for x in covers)
        shade = ''
    else:
        bg = '<div class="ph" style="background-image:url(\'%s\')"></div>' % f(c['photo'])
        side, shade = '', '<div class="shade"></div>'
    body = ('%s%s<div class="bar"></div>%s<div class="in"><img class="logo" src="%s"><span class="k">%s</span>'
            '<h1 style="--fs:%dpx">%s</h1><div class="by"><img src="%s"><div><b>Michael Barillari, Broker</b>RE/MAX Premier The OP Team</div></div></div>'
            '<div class="url">SOLDMIKE.COM</div></body></html>') % (
        bg, shade, side, f('/logo-soldmike-white.png'), e(c['kicker']), fs(c['headline']), e(c['headline']), f('/mike.png'))
    return head + body

def main():
    cards = json.load(open(os.path.join(OG, 'cards.json')))
    seen = json.load(open(os.path.join(OG, '.hashes.json'))) if os.path.exists(os.path.join(OG, '.hashes.json')) else {}
    tmp = tempfile.mkdtemp()
    covers = []
    for i, g in enumerate(GUIDES):
        os.makedirs(os.path.join(tempfile.gettempdir(), 'og-covers'), exist_ok=True)
        out = os.path.join(tempfile.gettempdir(), 'og-covers', 'cover%d' % i)  # fixed path so the card hash stays stable
        subprocess.run(['pdftoppm', '-f', '1', '-l', '1', '-r', '60', '-png', '-singlefile', os.path.join(ROOT, g), out], check=True)
        covers.append('file://' + out + '.png')
    made = 0
    for c in cards:
        doc = card_html(c, covers)
        h = hashlib.md5((doc + (str(os.path.getmtime(os.path.join(ROOT, c['photo'].lstrip('/')))) if c['layout'] == 'photo' else '')).encode()).hexdigest()
        jpg = os.path.join(OG, c['slug'] + '.jpg')
        if '--all' not in sys.argv and seen.get(c['slug']) == h and os.path.exists(jpg):
            continue
        src = os.path.join(tmp, c['slug'] + '.html'); png = os.path.join(tmp, c['slug'] + '.png')
        open(src, 'w').write(doc)
        subprocess.run([CHROME, '--headless=new', '--disable-gpu', '--hide-scrollbars', '--allow-file-access-from-files',
                        '--window-size=1200,630', '--virtual-time-budget=4000', '--screenshot=' + png, 'file://' + src],
                       check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run(['sips', '-s', 'format', 'jpeg', '-s', 'formatOptions', '82', png, '--out', jpg], check=True, stdout=subprocess.DEVNULL)
        seen[c['slug']] = h; made += 1
    json.dump(seen, open(os.path.join(OG, '.hashes.json'), 'w'), indent=1)
    print('share cards: %d drawn, %d unchanged' % (made, len(cards) - made))

if __name__ == '__main__':
    main()
