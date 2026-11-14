"""Polite sequential fetcher. Usage: python -I fetch.py <urls.txt> <fresh_out_dir> <sources.tsv>
One connection at a time, >= 3.5 s between requests, generic UA. Stops on 403/429 or challenge-looking pages.
Records url, datetime, status, bytes, sha256, local file in sources.tsv. Skips URLs already recorded with 200."""
import sys, os, time, hashlib, urllib.request, urllib.error, datetime, re

UA = 'Mozilla/5.0 (compatible; research-fetch)'
GAP = 3.5
STAMP = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.last_request')


def wait_gap():
    try:
        last = float(open(STAMP).read().strip())
    except Exception:
        last = 0.0
    d = time.time() - last
    if d < GAP:
        time.sleep(GAP - d)


def mark():
    with open(STAMP, 'w') as f:
        f.write(str(time.time()))


def local_name(url):
    n = re.sub(r'[^A-Za-z0-9._-]+', '_', url.split('://', 1)[-1])
    return n[-150:]


def main():
    urls_file, out, src = sys.argv[1], sys.argv[2], sys.argv[3]
    limit = int(sys.argv[4]) if len(sys.argv) > 4 else 10**9
    os.makedirs(out, exist_ok=True)
    done = set()
    if os.path.exists(src):
        for line in open(src, encoding='utf-8'):
            p = line.rstrip('\n').split('\t')
            if len(p) > 2 and p[2] == '200':
                done.add(p[0])
    else:
        with open(src, 'w', encoding='utf-8', newline='\n') as f:
            f.write('url\tdatetime_utc\tstatus\tbytes\tsha256\tlocal_file\n')
    urls = [u.strip() for u in open(urls_file, encoding='utf-8') if u.strip() and not u.startswith('#')]
    n = 0
    for u in urls:
        if u in done:
            continue
        if n >= limit:
            break
        wait_gap()
        req = urllib.request.Request(u, headers={'User-Agent': UA, 'Accept': '*/*'})
        status, body = None, b''
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                status = r.status
                body = r.read()
        except urllib.error.HTTPError as e:
            status = e.code
            try:
                body = e.read()
            except Exception:
                body = b''
        except Exception as e:
            status = 'ERR:' + type(e).__name__
        mark()
        n += 1
        h = hashlib.sha256(body).hexdigest()
        fn = local_name(u)
        if status == 200:
            with open(os.path.join(out, fn), 'wb') as f:
                f.write(body)
        ts = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
        with open(src, 'a', encoding='utf-8', newline='\n') as f:
            f.write(f'{u}\t{ts}\t{status}\t{len(body)}\t{h}\t{fn if status == 200 else ""}\n')
        print(status, len(body), u, flush=True)
        low = body[:4000].lower()
        if status in (403, 429) or (status == 200 and (b'captcha' in low or b'access denied' in low
                                                         or b'challenge-platform' in low)):
            print('STOP: block/challenge at', u, flush=True)
            sys.exit(3)
    print('fetched', n, flush=True)


if __name__ == '__main__':
    main()
