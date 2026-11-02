#!/usr/bin/env python3
"""get_live_data.py - download the recent orbit-file (TLE) history of Starlink satellites from Space-Track
and write live_tles.json for the Live forecasts page.

Needs only Python 3.8+ (no extra packages) and a free Space-Track account (https://www.space-track.org).

    python get_live_data.py                       asks for the Space-Track login (typed password is hidden; nothing is stored)
    python get_live_data.py --count 300           number of satellites (default 250)
    python get_live_data.py --days 21             days of history per satellite (default 21; the page needs at least 12)
    python get_live_data.py --norad 44713,44714   only these satellites
    python get_live_data.py --out live_tles.json

The login is sent only to www.space-track.org. Space-Track allows about 30 requests a minute; the script waits between requests.
Please keep to the Space-Track user agreement when you share the output file.
"""
import argparse, getpass, http.cookiejar, json, os, sys, time, datetime
import urllib.error, urllib.parse, urllib.request

BASE = os.environ.get('SPACETRACK_BASE', 'https://www.space-track.org')
PAUSE = float(os.environ.get('SPACETRACK_PAUSE', '2.5'))


class Session:
    def __init__(self):
        self.jar = http.cookiejar.CookieJar()
        self.op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(self.jar))
        self.op.addheaders = [('User-Agent', 'starlink-live-forecasts/1.0 (research)')]

    def login(self, user, password):
        data = urllib.parse.urlencode({'identity': user, 'password': password}).encode('ascii')
        with self.op.open(BASE + '/ajaxauth/login', data, timeout=60) as r:
            body = r.read().decode('utf-8', 'replace')
        if 'Failed' in body or not len(self.jar):
            raise SystemExit('Space-Track did not accept this login. Check the e-mail address and password (log in once at https://www.space-track.org in a browser).')

    def get(self, path, tries=4):
        url = BASE + '/basicspacedata/query/' + urllib.parse.quote(path, safe="/,~<>-:=._")
        for k in range(tries):
            try:
                with self.op.open(url, timeout=180) as r:
                    return r.read().decode('utf-8', 'replace')
            except urllib.error.HTTPError as e:
                if e.code in (429, 500, 502, 503, 504) and k < tries - 1:
                    wait = 30 * (k + 1)
                    print('  Space-Track answered %d, waiting %d s ...' % (e.code, wait))
                    time.sleep(wait)
                    continue
                raise SystemExit('Space-Track error %d for %s' % (e.code, path[:120]))
            except urllib.error.URLError as e:
                if k < tries - 1:
                    time.sleep(10)
                    continue
                raise SystemExit('Could not reach Space-Track: %s' % e.reason)

    def logout(self):
        try:
            self.op.open(BASE + '/ajaxauth/logout', timeout=30).read()
        except Exception:
            pass


def rows(text, what):
    try:
        d = json.loads(text)
    except ValueError:
        raise SystemExit('Unexpected answer from Space-Track for %s: %s' % (what, text[:200]))
    if isinstance(d, dict):
        raise SystemExit('Space-Track returned an error for %s: %s' % (what, str(d)[:200]))
    return d


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--count', type=int, default=250)
    ap.add_argument('--days', type=int, default=21)
    ap.add_argument('--norad', default='')
    ap.add_argument('--out', default='live_tles.json')
    a = ap.parse_args()
    if not (12 <= a.days <= 60):
        raise SystemExit('--days must be between 12 and 60')
    user = os.environ.get('SPACETRACK_USER') or input('Space-Track e-mail / user name: ').strip()
    password = os.environ.get('SPACETRACK_PASS') or getpass.getpass('Space-Track password (hidden, not stored): ')
    s = Session()
    print('Logging in ...')
    s.login(user, password)
    try:
        if a.norad.strip():
            ids = [int(x) for x in a.norad.replace(' ', '').split(',') if x]
        else:
            print('Listing current Starlink satellites ...')
            cat = rows(s.get('class/gp/OBJECT_NAME/~~STARLINK/DECAY_DATE/null-val/EPOCH/>now-4/MEAN_MOTION/14.8--15.9/orderby/NORAD_CAT_ID asc/format/json/predicates/NORAD_CAT_ID,OBJECT_NAME,EPOCH'), 'the catalogue')
            allids = sorted(set(int(r['NORAD_CAT_ID']) for r in cat))
            print('  %d Starlink satellites with a recent orbit file' % len(allids))
            if not allids:
                raise SystemExit('No satellites found.')
            step = max(1, len(allids) / float(a.count))
            ids = sorted(set(allids[int(i * step)] for i in range(min(a.count, len(allids)))))
            time.sleep(PAUSE)
        print('Downloading %d days of orbit files for %d satellites ...' % (a.days, len(ids)))
        out, B = {}, 8
        for k in range(0, len(ids), B):
            chunk = ids[k:k + B]
            txt = s.get('class/gp_history/NORAD_CAT_ID/%s/EPOCH/>now-%d/orderby/NORAD_CAT_ID asc,EPOCH asc/format/json/predicates/NORAD_CAT_ID,OBJECT_NAME,EPOCH,TLE_LINE1,TLE_LINE2' % (','.join(map(str, chunk)), a.days))
            for r in rows(txt, 'the history'):
                l1, l2 = (r.get('TLE_LINE1') or '').strip(), (r.get('TLE_LINE2') or '').strip()
                if len(l1) < 69 or len(l2) < 69:
                    continue
                n = int(r['NORAD_CAT_ID'])
                e = out.setdefault(n, {'n': n, 'name': (r.get('OBJECT_NAME') or ('NORAD %d' % n)).strip(), 'seen': set(), 't': []})
                key = l1[18:32]
                if key in e['seen']:
                    continue
                e['seen'].add(key)
                e['t'].append([l1, l2])
            print('  %d / %d satellites' % (min(k + B, len(ids)), len(ids)))
            time.sleep(PAUSE)
    finally:
        s.logout()
    sats = []
    for n in sorted(out):
        e = out[n]
        e['t'].sort(key=lambda p: p[0][18:32])      # same year digits, so the epoch text sorts in time order within one window
        if len(e['t']) >= 10:
            sats.append({'n': e['n'], 'name': e['name'], 't': e['t']})
    if not sats:
        raise SystemExit('No satellite had at least 10 orbit files in the window. Nothing written.')
    doc = {'format': 1, 'generated_utc': datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC'), 'source': 'Space-Track gp_history', 'days': a.days, 'sats': sats}
    with open(a.out, 'w') as f:
        json.dump(doc, f, separators=(',', ':'))
    print('\nWrote %s: %d satellites, %.1f MB.' % (a.out, len(sats), os.path.getsize(a.out) / 1e6))
    print('Next: open live.html, click "Load a satellite data file" and choose %s.' % a.out)
    print('To show it on the website too, upload %s next to live.html (check the Space-Track user agreement first).' % a.out)


if __name__ == '__main__':
    main()
