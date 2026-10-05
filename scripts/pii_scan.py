#!/usr/bin/env python3
"""Count pattern matches per table; write counts and file names only to PII_SCAN.md.

Matched values are never printed or stored. Categories: email addresses,
phone-number-like strings, IPv4 addresses, 0x-prefixed 40-hex blockchain addresses
(public chain data, counted separately). Names of operators are not detectable by
pattern and are not scanned for. Usage: python3 scripts/pii_scan.py
"""
import glob, gzip, json, os, re, datetime, collections

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
D = os.path.join(ROOT, 'data')
PATTERNS = {
    'email': re.compile(r'[A-Za-z0-9._%+\-]+@[A-Za-z0-9\-]+(?:\.[A-Za-z0-9\-]+)*\.[A-Za-z]{2,}'),
    'phone_like': re.compile(r'(?<![\w.])(?:\+|00)?\d{1,3}[\s.\-/]?(?:\(?\d{2,4}\)?[\s.\-/]?){2,4}\d{2,4}(?![\w.])'),
    'ipv4': re.compile(r'(?<![\d.])(?:(?:25[0-5]|2[0-4]\d|1?\d?\d)\.){3}(?:25[0-5]|2[0-4]\d|1?\d?\d)(?![\d.])'),
    'eth_address_0x40hex': re.compile(r'0x[0-9a-fA-F]{40}(?![0-9a-fA-F])'),
}
# phone-like needs at least 9 digits and must not be a plain timestamp or id
def phone_ok(m):
    digits = re.sub(r'\D', '', m)
    if not (9 <= len(digits) <= 15):
        return False
    return bool(re.search(r'[\s.\-/()+]', m)) and not re.fullmatch(r'\d{4}-\d{2}-\d{2}.*', m)


def scan_text(txt, counts):
    for name, rx in PATTERNS.items():
        if name == 'phone_like':
            counts[name] += sum(1 for m in rx.finditer(txt) if phone_ok(m.group(0)))
        else:
            counts[name] += len(rx.findall(txt))


def main():
    per_table = collections.OrderedDict()
    per_file = []
    for name in sorted(os.listdir(D)):
        p = os.path.join(D, name)
        if not os.path.isdir(p):
            continue
        tc = collections.Counter()
        for fn in sorted(glob.glob(os.path.join(p, '*'))):
            fc = collections.Counter()
            if fn.endswith('.gz'):
                with gzip.open(fn, 'rt', encoding='utf8') as f:
                    for line in f:
                        scan_text(line, fc)
            else:
                scan_text(open(fn, encoding='utf8', errors='replace').read(), fc)
            tc.update(fc)
            if any(fc.values()):
                per_file.append((os.path.relpath(fn, ROOT), dict(fc)))
        per_table[name] = tc
    keys = list(PATTERNS)
    L = ['# PII scan', '',
         f'Run {datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")} by scripts/pii_scan.py over data/.',
         'Only counts and file names are written here. Matched values are not printed or stored.',
         'Pattern matches are not confirmed personal data: phone-like also hits ids, dates and numbers in prose; 0x40hex strings are public blockchain addresses, listed apart.',
         'Operator (human) names cannot be detected by pattern and are not scanned for.', '',
         '| table | ' + ' | '.join(keys) + ' |', '|---|' + '---|' * len(keys)]
    tot = collections.Counter()
    for t, c in per_table.items():
        L.append(f'| {t} | ' + ' | '.join(str(c[k]) for k in keys) + ' |')
        tot.update(c)
    L.append('| **total** | ' + ' | '.join(str(tot[k]) for k in keys) + ' |')
    L += ['', '## Files with at least one match', '']
    for fn, fc in per_file:
        L.append(f'- {fn}: ' + ', '.join(f'{k} {v}' for k, v in fc.items() if v))
    open(os.path.join(ROOT, 'PII_SCAN.md'), 'w').write('\n'.join(L) + '\n')
    rp = os.path.join(ROOT, 'README.md')
    if os.path.exists(rp):
        rd = open(rp).read()
        if '<!--PII-->' in rd:
            tbl = ['Pattern-match counts over data/ at ' + datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d %H:%M UTC') + ' (counts only, matched values are not stored):', '',
                   '| table | ' + ' | '.join(keys) + ' |', '|---|' + '---|' * len(keys)]
            for t, c in per_table.items():
                tbl.append(f'| {t} | ' + ' | '.join(str(c[k]) for k in keys) + ' |')
            tbl.append('| **total** | ' + ' | '.join(str(tot[k]) for k in keys) + ' |')
            a, b = rd.index('<!--PII-->'), rd.index('<!--/PII-->')
            open(rp, 'w').write(rd[:a] + '<!--PII-->\n' + '\n'.join(tbl) + '\n' + rd[b:])
    print('| table | ' + ' | '.join(keys) + ' |')
    for t, c in per_table.items():
        print(f'| {t} | ' + ' | '.join(str(c[k]) for k in keys) + ' |')
    print('total', dict(tot))


if __name__ == '__main__':
    main()
