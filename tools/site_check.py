#!/usr/bin/env python3
"""soldmike.com health check (Oct 14 2026). Keeps the Search Console warnings from coming back.

  python3 tools/site_check.py --local   # before a push: sitemap.xml only lists built, indexable pages (run by the pre-push hook)
  python3 tools/site_check.py           # live: both sitemaps, redirects, robots.txt, listing pages (Monday worker)

Prints one line per problem and exits 1 if anything is wrong; prints "OK ..." and exits 0 when clean.
"""
import json, os, random, re, sys, time, urllib.request, urllib.error

SITE = 'https://soldmike.com'
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130 Safari/537.36 SoldMikeHealthCheck'
PRIVATE = ('/hq/', '/admin/', '/saved/', '/alerts/', '/leads/')
problems = []


def locs(xml):
    return re.findall(r'<loc>([^<]+)</loc>', xml)


def page_issues(url, html):
    out = []
    if re.search(r'<meta[^>]+name="robots"[^>]+noindex', html, re.I):
        out.append('noindex page in sitemap')
    m = re.search(r'<link rel="canonical" href="([^"]+)"', html)
    if not m:
        out.append('no canonical tag')
    elif m.group(1) != url:
        out.append('canonical points elsewhere: ' + m.group(1))
    if any(p in url for p in PRIVATE):
        out.append('private page in sitemap')
    return out


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *a, **k):
        return None


def get(url, follow=False):
    opener = urllib.request.build_opener() if follow else urllib.request.build_opener(NoRedirect)
    req = urllib.request.Request(url, headers={'User-Agent': UA})
    try:
        r = opener.open(req, timeout=30)
        return r.status, r.headers.get('Location'), r.read().decode('utf-8', 'replace')
    except urllib.error.HTTPError as e:
        return e.code, e.headers.get('Location'), ''
    except Exception as e:  # network trouble counts as a problem, not a crash
        return 0, None, str(e)


def local():
    xml = open(os.path.join(ROOT, 'sitemap.xml')).read()
    for url in locs(xml):
        path = url[len(SITE):] if url.startswith(SITE) else url
        f = os.path.join(ROOT, path.lstrip('/'), 'index.html') if path.endswith('/') else os.path.join(ROOT, path.lstrip('/'))
        if not os.path.exists(f):
            problems.append(f'{url}: in sitemap.xml but no built page ({os.path.relpath(f, ROOT)})')
            continue
        for p in page_issues(url, open(f, encoding='utf-8', errors='replace').read()):
            problems.append(f'{url}: {p}')
    return len(locs(xml))


def live(sample=40):
    n = 0
    s, _, xml = get(SITE + '/sitemap.xml')
    if s != 200:
        problems.append(f'/sitemap.xml returned {s}')
    for url in locs(xml):
        s, loc, html = get(url)
        n += 1
        if s != 200:
            problems.append(f'{url}: {s}' + (f' -> {loc}' if loc else ''))
            continue
        for p in page_issues(url, html):
            problems.append(f'{url}: {p}')
        time.sleep(0.3)
    s, _, hx = get(SITE + '/homes/sitemap.xml')
    homes = locs(hx)
    if s != 200 or not homes:
        problems.append(f'/homes/sitemap.xml returned {s} with {len(homes)} URLs')
    random.seed()
    for url in random.sample(homes, min(sample, len(homes))):
        s, loc, html = get(url)
        n += 1
        if s != 200:
            problems.append(f'{url}: {s}' + (f' -> {loc}' if loc else '') + ' (listing in /homes/ sitemap is not live)')
        else:
            for p in page_issues(url, html):
                problems.append(f'{url}: {p}')
            if 'og:image' not in html:
                problems.append(f'{url}: no share photo (og:image)')
        time.sleep(0.7)  # stay well under the per-IP limit
    # one hop to the canonical host, https only
    for u in ('http://soldmike.com/', 'https://www.soldmike.com/', 'http://www.soldmike.com/'):
        s, loc, _ = get(u)
        if s not in (301, 308) or loc != SITE + '/':
            problems.append(f'{u}: expected one 301 to {SITE}/, got {s} -> {loc}')
    s, _, robots = get(SITE + '/robots.txt')
    for need in ('Sitemap: https://soldmike.com/sitemap.xml', 'Sitemap: https://soldmike.com/homes/sitemap.xml', 'Disallow: /hq/'):
        if need not in robots:
            problems.append(f'robots.txt is missing "{need}"')
    return n, len(homes)


if __name__ == '__main__':
    if '--local' in sys.argv:
        n = local()
        label = f'{n} sitemap.xml pages built and indexable'
    else:
        n, h = live()
        label = f'{n} pages checked, /homes/ sitemap has {h} listings'
    if '--json' in sys.argv:
        print(json.dumps({'ok': not problems, 'summary': label, 'problems': problems}))
    elif problems:
        print('\n'.join(problems))
    else:
        print('OK: ' + label)
    sys.exit(1 if problems else 0)
