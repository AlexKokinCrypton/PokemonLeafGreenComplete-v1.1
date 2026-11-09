#!/usr/bin/env python3
"""Pokemon LeafGreen Complete: reversible EN/RU translation catalog.

No external dependencies and no changes to the English game files.
This editor exports translations; runtime resources are generated separately by build_bilingual.py.
"""
from __future__ import annotations

import argparse
import collections
import csv
import json
import re
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlsplit
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CSV = ROOT / "localization" / "en_ru.csv"
COLUMNS = ["key", "type", "file", "symbol", "english", "russian", "status"]
LABEL = re.compile(r'^\s*([A-Za-z_][\w.]*)::?\s*(?:@.*)?$')
ASM_STRING = re.compile(r'^\s*\.string\s+"((?:\\.|[^"\\])*)"\s*(?:@.*)?$')
# C macro _(\"...\"); kept as references, not rewritten automatically.
C_MACRO = re.compile(r'\b_\(\s*((?:"(?:\\.|[^"\\])*"\s*)+)\)', re.MULTILINE)
C_STR = re.compile(r'"((?:\\.|[^"\\])*)"')
# The user must never be able to edit game control codes in the translation UI.
# Lock *all* {...} codes, every backslash escape, and the GBA $ terminator.
LOCKED = re.compile(r'\{[^{}]*\}|\\.|(?<!\\)\$')
CONTROL = re.compile(r'\{[^}]+\}')


def protected_tokens(value: str) -> list[str]:
    return LOCKED.findall(value)


def editing_parts(value: str) -> list[str]:
    """Split into editable fields, between immutable control-token chips."""
    return LOCKED.split(value)


def join_editing_parts(source: str, parts: list[str]) -> str:
    """Reconstruct using the ORIGINAL protected tokens, never client input."""
    tokens = protected_tokens(source)
    if not isinstance(parts, list) or len(parts) != len(tokens) + 1 or not all(isinstance(p, str) for p in parts):
        raise ValueError('Invalid number or type of editable fields')
    for part in parts:
        if LOCKED.search(part):
            raise ValueError('Control sequences are locked; edit only natural-language text')
        if '\r' in part or '\n' in part:
            raise ValueError('Real newlines are not allowed in text fields; the \n token is locked')
        if len(part) > 10000:
            raise ValueError('Editable field too long')
    return ''.join(part + (tokens[i] if i < len(tokens) else '') for i, part in enumerate(parts))
VALID_ESCAPES = set('npl\\\"0')


def parse_asm(path: Path) -> list[dict[str, str]]:
    results = []
    text = path.read_text(encoding='utf-8')
    lines = text.splitlines()
    current = None
    fragments = []
    state = 0  # 0 no, 1 label seen, 2 gathering

    def flush():
        nonlocal current, fragments, state
        if current and fragments:
            rel = path.relative_to(ROOT).as_posix()
            results.append(dict(key=f'asm:{rel}#{current}', type='asm', file=rel,
                                symbol=current, english=''.join(fragments), russian='', status='untranslated'))
        current, fragments, state = None, [], 0

    for line in lines:
        match = LABEL.match(line)
        if match:
            flush()
            current = match.group(1)
            state = 1
            continue
        match = ASM_STRING.match(line)
        if match and state:
            fragments.append(match.group(1))
            state = 2
            continue
        if state and (not line.strip() or line.lstrip().startswith('@')):
            continue
        if state:
            flush()
    flush()
    return results


def parse_c(path: Path) -> list[dict[str, str]]:
    text = path.read_text(encoding='utf-8')
    rel = path.relative_to(ROOT).as_posix()
    result = []
    for match in C_MACRO.finditer(text):
        line = text.count('\n', 0, match.start()) + 1
        val = ''.join(C_STR.findall(match.group(1)))
        if not val:
            continue
        preceding = text[max(0, match.start() - 170):match.start()]
        decl = re.search(r'(?m)(?:^|[;\n])\s*(?:(?:static|const)\s+)*(?:u8|s8|char)\s+([A-Za-z_]\w*)\s*\[[^]\n]*\]\s*=\s*$', preceding)
        symbol = decl.group(1) if decl else f'line_{line}'
        result.append(dict(key=f'c:{rel}#{symbol}:{line}', type='c', file=rel,
                           symbol=symbol, english=val, russian='', status='untranslated'))
    return result


def scan() -> list[dict[str, str]]:
    result = []
    for path in sorted((ROOT / 'data').rglob('*')):
        if path.is_file() and path.suffix in ('.inc', '.s'):
            result.extend(parse_asm(path))
    for top in ('src', 'include'):
        for path in sorted((ROOT / top).rglob('*')):
            if path.is_file() and path.suffix in ('.c', '.h'):
                result.extend(parse_c(path))
    keys = [r['key'] for r in result]
    dupe = [k for k, v in collections.Counter(keys).items() if v > 1]
    if dupe:
        raise ValueError(f'Duplicate IDs: {dupe[:5]}')
    return result


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding='utf-8-sig', newline='') as fp:
        rdr = csv.DictReader(fp)
        if not set(COLUMNS).issubset(set(rdr.fieldnames or [])):
            raise ValueError('Wrong CSV columns. Expected ' + ', '.join(COLUMNS))
        rows = list(rdr)
    keys = [row['key'] for row in rows]
    if len(set(keys)) != len(keys):
        raise ValueError('Duplicate key in translation CSV')
    return rows


def write_csv(path: Path, rows: list[dict[str, str]]):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', encoding='utf-8-sig', newline='') as fp:
        writer = csv.DictWriter(fp, fieldnames=COLUMNS)
        writer.writeheader()
        writer.writerows([{k: row.get(k, '') for k in COLUMNS} for row in rows])


def export(args):
    target = Path(args.output)
    found = scan()
    preserved = 0
    if target.exists():
        existing = {row['key']: row for row in read_csv(target)}
        for row in found:
            old = existing.get(row['key'])
            if not old:
                continue
            row['russian'] = old.get('russian', '')
            if row['russian']:
                preserved += 1
                row['status'] = ('translated' if row['english'] == old['english'] else 'source_changed')
    write_csv(target, found)
    counts = collections.Counter(row['type'] for row in found)
    print(f'Exported {len(found)} strings to {target} ({counts["asm"]} ASM, {counts["c"]} C). Preserved {preserved} RU translations.')


def check_translation(row):
    errors = []
    tr = row['russian']
    if not tr:
        return errors
    en = row['english']
    if row['status'] == 'source_changed':
        errors.append('English source changed since translation; re-review required')
    if protected_tokens(en) != protected_tokens(tr):
        errors.append('Locked control tokens changed, removed, added, or reordered')
    if en.endswith('$') and not tr.endswith('$'):
        errors.append('Missing required $ string terminator')
    if en.count('$') != tr.count('$'):
        errors.append('Changed count of $ terminators')
    if en.count('\\p') != tr.count('\\p'):
        errors.append('Changed count of \\p paragraph breaks (review manually)')
    # Do not permit bare escape sequences that may break charmap parsing.
    for m in re.finditer(r'\\(.)', tr):
        if m.group(1) not in VALID_ESCAPES and m.group(1) not in 'v':
            errors.append('Unknown string escape \\' + m.group(1))
            break
    if '"' in tr.replace('\\"', ''):
        errors.append('Unescaped double quote')
    return errors


def validate(args):
    rows = read_csv(Path(args.input))
    found = {row['key']: row for row in scan()}
    errors, warnings = [], []
    translated = 0
    for row in rows:
        key = row['key']
        if key not in found:
            warnings.append(f'{key}: source ID not present in repo')
            continue
        if row['english'] != found[key]['english']:
            errors.append(f'{key}: English source differs from current repo; run export to synchronize')
        if row['russian']:
            translated += 1
            errors.extend(f'{key}: {err}' for err in check_translation(row))
    print(f'Catalog: {len(rows)} strings; RU translated: {translated}; missing RU: {len(rows) - translated}; errors: {len(errors)}; warnings: {len(warnings)}')
    for w in warnings[:20]:
        print('WARN:', w)
    for e in errors[:40]:
        print('ERROR:', e)
    if len(errors) > 40:
        print(f'... and {len(errors) - 40} more errors')
    if translated:
        print('NOTE: This staged export is for review only. To integrate ROM texts use build_bilingual.py.')
    return 1 if errors else 0


def build(args):
    rows = read_csv(Path(args.input))
    current = {row['key']: row for row in scan()}
    errors = []
    for row in rows:
        if not row['russian']:
            continue
        if row['key'] not in current or row['english'] != current[row['key']]['english']:
            errors.append(f'{row["key"]}: stale or missing source')
        errors.extend(f'{row["key"]}: {err}' for err in check_translation(row))
    if errors:
        for e in errors[:30]:
            print('ERROR:', e, file=sys.stderr)
        return 1

    out = Path(args.output)
    if out.is_relative_to(ROOT):
        # The generated source tree must not accidentally overwrite original files.
        pass
    out.mkdir(parents=True, exist_ok=True)
    asm_by_path = collections.defaultdict(list)
    c_by_path = collections.defaultdict(list)
    for row in rows:
        if not row['russian']:
            continue
        if row['type'] == 'asm':
            asm_by_path[row['file']].append(row)
        else:
            c_by_path[row['file']].append(row)
    # Keep originals intact. ASM files are staging data for later bilingual runtime wiring.
    for original, entries in asm_by_path.items():
        dest = out / 'asm' / (original + '.ru.inc')
        dest.parent.mkdir(parents=True, exist_ok=True)
        lines = ['@ Generated translation staging resource, DO NOT include in ROM yet.',
                 '@ Cyrillic graphics, encoding and runtime language-selection are not wired.',
                 '@ Original English labels and files remain unchanged.', '']
        for entry in entries:
            value = entry['russian'].replace('"', r'\"')
            lines.extend([entry['symbol'] + '_RU::', f'    .string "{value}"', ''])
        dest.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    # C macro strings are reference entries; do not attempt unsafe auto C source rewriting.
    refs = [dict(key=r['key'], file=r['file'], symbol=r['symbol'], russian=r['russian'])
            for entries in c_by_path.values() for r in entries]
    (out / 'c_text_references.json').write_text(json.dumps(refs, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f'Generated {len(asm_by_path)} RU ASM staging files and {len(refs)} C references in {out}.')
    print('English resources are untouched. This is NOT a bilingual ROM build.')
    return 0



def serve(args):
    """Simple offline editor that never exposes token text in editable inputs."""
    csv_path = Path(args.input).resolve()
    if not csv_path.exists():
        print(f'Catalog not found: {csv_path}. Run export first.', file=sys.stderr)
        return 1
    rows = read_csv(csv_path)
    index = {r['key']: r for r in rows}
    page = (Path(__file__).with_name('editor.html')).read_bytes()

    class Handler(BaseHTTPRequestHandler):
        def send_payload(self, obj, status=200):
            payload = json.dumps(obj, ensure_ascii=False).encode('utf-8')
            self.send_response(status)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Content-Length', str(len(payload)))
            self.send_header('Cache-Control', 'no-store')
            self.end_headers()
            self.wfile.write(payload)

        def do_GET(self):
            request = urlsplit(self.path)
            if request.path == '/':
                self.send_response(200)
                self.send_header('Content-Type', 'text/html; charset=utf-8')
                self.send_header('Content-Length', str(len(page)))
                self.end_headers()
                self.wfile.write(page)
            elif request.path == '/api/list':
                params = parse_qs(request.query)
                q = params.get('q', [''])[0].strip().casefold()
                status = params.get('status', ['all'])[0]
                try:
                    offset = max(0, int(params.get('offset', ['0'])[0]))
                except ValueError:
                    offset = 0
                filtered = [r for r in rows
                            if (not q or q in (r['english'] + ' ' + r['russian'] + ' ' + r['key']).casefold())
                            and (status == 'all' or (status == 'translated') == bool(r['russian']))]
                self.send_payload({'total': len(filtered), 'offset': offset,
                                   'entries': [{k: r[k] for k in ('key', 'english', 'russian', 'status')}
                                               for r in filtered[offset:offset + 35]]})
            elif request.path == '/api/item':
                key = parse_qs(request.query).get('key', [''])[0]
                row = index.get(key)
                if not row:
                    self.send_payload({'error': 'Entry not found'}, 404)
                    return
                original = protected_tokens(row['english'])
                current = row['russian'] if row['russian'] else row['english']
                valid = protected_tokens(current) == original
                self.send_payload({**row, 'tokens': original,
                                   'english_parts': editing_parts(row['english']),
                                   'parts': editing_parts(current) if valid else [],
                                   'valid': valid, 'is_draft': not bool(row['russian'])})
            else:
                self.send_payload({'error': 'Not found'}, 404)

        def do_POST(self):
            if urlsplit(self.path).path != '/api/save':
                self.send_payload({'error': 'Not found'}, 404)
                return
            if self.headers.get('X-Local-Translator') != '1':
                self.send_payload({'error': 'Invalid request'}, 403)
                return
            try:
                length = int(self.headers.get('Content-Length', '0'))
                if not 0 < length < 200000:
                    raise ValueError('Invalid request size')
                data = json.loads(self.rfile.read(length))
                key = data.get('key')
                row = index.get(key)
                if row is None:
                    raise ValueError('Unknown translation key')
                if data.get('clear') is True:
                    row['russian'] = ''
                    row['status'] = 'untranslated'
                else:
                    translation = join_editing_parts(row['english'], data.get('parts', []))
                    candidate = {**row, 'russian': translation, 'status': 'translated'}
                    problems = check_translation(candidate)
                    if problems:
                        raise ValueError('; '.join(problems))
                    row['russian'] = translation
                    row['status'] = 'translated'
                write_csv(csv_path, rows)
                self.send_payload({'ok': True, 'key': key, 'status': row['status']})
            except (ValueError, TypeError, json.JSONDecodeError) as e:
                self.send_payload({'error': str(e)}, 400)

        def log_message(self, format, *args):
            return  # Keep terminal clear while editing

    address = ('127.0.0.1', args.port)
    server = ThreadingHTTPServer(address, Handler)
    print(f'LeafGreen translator is ready at http://127.0.0.1:{server.server_port}')
    print('Tokens are locked in the UI and restored server-side from the English source.')
    print('Press Ctrl+C to stop. The catalog is saved to:', csv_path)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('\nStopped')
    finally:
        server.server_close()
    return 0


def main():
    parser = argparse.ArgumentParser(description='Bilingual translation catalog for LeafGreen Complete (EN originals + RU sidecar)')
    sub = parser.add_subparsers(dest='command', required=True)
    exp = sub.add_parser('export', help='Scan source and create/update bilingual CSV without erasing RU edits')
    exp.add_argument('-o', '--output', default=str(DEFAULT_CSV))
    exp.set_defaults(fn=export)
    val = sub.add_parser('validate', help='Check translation control tokens and English source drift')
    val.add_argument('-i', '--input', default=str(DEFAULT_CSV))
    val.set_defaults(fn=validate)
    build_cmd = sub.add_parser('build', help='Generate non-invasive staged RU text resources (not a ROM)')
    build_cmd.add_argument('-i', '--input', default=str(DEFAULT_CSV))
    build_cmd.add_argument('-o', '--output', default=str(ROOT / 'localization/generated/ru'))
    build_cmd.set_defaults(fn=build)
    web_cmd = sub.add_parser('serve', help='Run offline web editor with UNEDITABLE control-token chips')
    web_cmd.add_argument('-i', '--input', default=str(DEFAULT_CSV))
    web_cmd.add_argument('-p', '--port', type=int, default=8765)
    web_cmd.set_defaults(fn=serve)
    args = parser.parse_args()
    sys.exit(args.fn(args) or 0)


if __name__ == '__main__':
    main()
