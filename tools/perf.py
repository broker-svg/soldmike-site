"""Speed pass for soldmike.com pages (Nov 15 2026 SEO audit).

build.py calls optimize(html, path) on every page it writes, and on the hand-written index.html.
  - photos: a .webp copy sits beside every .jpg/.png (made by make_webp, needs `cwebp` from Homebrew);
    <img> tags and inline background photos point at the .webp, and every <img> gets its real width/height
    so the page does not jump while loading. Share cards (og/) stay JPG: Facebook and LinkedIn want JPG.
  - fonts: Barlow + Barlow Condensed are served from /assets/fonts/ (no Google Fonts stylesheet blocking the first paint).
Running it twice changes nothing the second time.
"""
import json, os, re, shutil, subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MANIFEST = os.path.join(ROOT, 'assets', 'img.json')
SKIP_DIRS = {'.git', 'og', 'hq', 'tools', 'node_modules', '.claude'}
MAX_W = {'.jpg': 1920, '.jpeg': 1920, '.png': 1000}

FONTS = [('Barlow', 400, 'barlow-400'), ('Barlow', 500, 'barlow-500'), ('Barlow', 600, 'barlow-600'),
         ('Barlow Condensed', 500, 'barlow-condensed-500'), ('Barlow Condensed', 600, 'barlow-condensed-600'),
         ('Barlow Condensed', 700, 'barlow-condensed-700'), ('Barlow Condensed', 800, 'barlow-condensed-800')]
FONT_CSS = ''.join("@font-face{font-family:'%s';font-style:normal;font-weight:%d;font-display:swap;src:url(/assets/fonts/%s.woff2) format('woff2')}" % f for f in FONTS)
FONT_HEAD = ('<link rel="preload" href="/assets/fonts/barlow-400.woff2" as="font" type="font/woff2" crossorigin>'
             '<link rel="preload" href="/assets/fonts/barlow-condensed-700.woff2" as="font" type="font/woff2" crossorigin>'
             '<style id="fonts">' + FONT_CSS + '</style>')


def _size(p):
    out = subprocess.run(['sips', '-g', 'pixelWidth', '-g', 'pixelHeight', p], capture_output=True, text=True).stdout
    w, h = re.search(r'pixelWidth: (\d+)', out), re.search(r'pixelHeight: (\d+)', out)
    return (int(w.group(1)), int(h.group(1))) if w and h else None


def make_webp():
    """A .webp beside every photo (only when it comes out smaller), and assets/img.json with each photo's real size."""
    man = json.load(open(MANIFEST)) if os.path.exists(MANIFEST) else {}
    cwebp = shutil.which('cwebp')
    for d, dirs, files in os.walk(ROOT):
        dirs[:] = [x for x in dirs if x not in SKIP_DIRS]
        for f in files:
            ext = os.path.splitext(f)[1].lower()
            if ext not in MAX_W: continue
            src = os.path.join(d, f); key = '/' + os.path.relpath(src, ROOT)
            out = os.path.splitext(src)[0] + '.webp'; m = man.get(key, {})
            if m.get('mtime') == int(os.path.getmtime(src)) and (not m.get('webp') or os.path.exists(out)): continue
            sz = _size(src)
            if not sz: continue
            m = {'w': sz[0], 'h': sz[1], 'mtime': int(os.path.getmtime(src))}
            if cwebp:
                args = [cwebp, '-quiet', '-q', '80', '-alpha_q', '90'] + (['-resize', str(MAX_W[ext]), '0'] if sz[0] > MAX_W[ext] else []) + [src, '-o', out]
                if subprocess.run(args).returncode == 0 and os.path.getsize(out) < os.path.getsize(src) * 0.9:
                    m['webp'] = os.path.splitext(key)[0] + '.webp'
                elif os.path.exists(out): os.remove(out)
            man[key] = m
    for k in [k for k in man if not os.path.exists(ROOT + k)]: del man[k]
    json.dump(man, open(MANIFEST, 'w'), indent=0, sort_keys=True)
    return man


_MAN = None
def _man():
    global _MAN
    if _MAN is None: _MAN = json.load(open(MANIFEST)) if os.path.exists(MANIFEST) else {}
    return _MAN


def _key(src, base):
    if re.match(r'^(https?:)?//|^data:', src): return None
    src = src.split('?')[0]
    return src if src.startswith('/') else os.path.normpath(os.path.join(base, src))


def optimize(html, path='/'):
    man = _man(); base = path if path.endswith('/') else os.path.dirname(path) + '/'
    by_webp = {m['webp']: m for m in man.values() if m.get('webp')}

    def img(mt):
        tag = mt.group(0); s = re.search(r'\bsrc="([^"]+)"', tag)
        if not s: return tag
        key = _key(s.group(1), base); m = man.get(key) or by_webp.get(key)
        if not m: return tag
        if m.get('webp') and key != m['webp']: tag = tag.replace(s.group(0), 'src="%s"' % m['webp'])
        if not re.search(r'\bwidth="', tag): tag = tag[:-1].rstrip('/').rstrip() + ' width="%d" height="%d">' % (m['w'], m['h'])
        return tag
    html = re.sub(r'<img\b[^>]*>', img, html)

    def bg(mt):
        key = _key(mt.group(1).strip('\'"'), base); m = man.get(key)
        return 'url(%s)' % m['webp'] if m and m.get('webp') else mt.group(0)
    html = re.sub(r'url\(([^)]+\.(?:jpe?g|png))\)', bg, html)
    html = re.sub(r'(<video\b[^>]*\bposter=")([^"]+)(")', lambda mt: mt.group(1) + ((man.get(_key(mt.group(2), base)) or {}).get('webp') or mt.group(2)) + mt.group(3), html)

    # fonts from our own server
    html = re.sub(r'<link rel="preconnect" href="https://fonts\.(?:googleapis|gstatic)\.com"[^>]*>\s*', '', html)
    html = re.sub(r'<link rel="stylesheet" href="https://fonts\.googleapis\.com/css2[^"]*">', '' if 'id="fonts"' in html else FONT_HEAD, html)

    # the first big photo is what the visitor sees first: fetch it early
    if 'rel="preload" as="image"' not in html:
        first = re.search(r'<div class="bg" style="background-image:url\(([^)]+)\)"', html)
        if first: html = html.replace('</head>', '<link rel="preload" as="image" href="%s" fetchpriority="high"></head>' % first.group(1), 1)
    html = re.sub(r'<img class="poster"(?![^>]*fetchpriority)', '<img class="poster" fetchpriority="high"', html)
    return html


if __name__ == '__main__':
    m = make_webp()
    print('photos:', len(m), 'with webp:', sum(1 for x in m.values() if x.get('webp')))
