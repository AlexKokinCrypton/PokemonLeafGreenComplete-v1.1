#!/usr/bin/env python3
"""Validate Cyrillic GBA glyph atlases and build a ROM-ready translation lookup.

The English glyph atlases are NEVER modified. Russian letters use the previously
unallocated CHAR_EXTRA_SYMBOL (0xF9) subrange 0x80..0xC1, so they can coexist
with both English text and player-name placeholders in the same message.
"""
from __future__ import annotations

import ast
import csv
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CSV = ROOT / 'localization/en_ru.csv'
FONTS = ROOT / 'graphics/fonts'
DONOR = ROOT / 'translation_donor/fonts'
UPPER = 'АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ'
LOWER = UPPER.lower()
assert len(UPPER) == len(LOWER) == 33
LETTERS = UPPER + LOWER
# Grounded in donor atlas grid, manually checked by glyph inspection.
DONOR_INDEX = dict(zip(UPPER, list(range(0x40, 0x49)) + list(range(0x56, 0x60))
                      + list(range(0x61, 0x67)) + list(range(0x68, 0x70))))
DONOR_INDEX.update(dict(zip(LOWER, [0x70] + list(range(0x75, 0x7C)) + list(range(0x7F, 0x98)))))
assert len(DONOR_INDEX) == 66
GLYPH_BASE = 0x80


def build_fonts():
    """Check committed native-pixel Cyrillic atlases and refresh glyph widths.

    Unlike the old donor downscaler, this does not resize or alter the bitmap
    glyphs. This prevents the blurry/squashed font from reappearing when the
    localization generator is run without --texts-only.
    """
    from PIL import Image
    normal_widths = None
    small_widths = None
    for name in ('normal', 'male', 'female', 'small'):
        font_path = FONTS / f'russian_{name}.png'
        im = Image.open(font_path)
        is_small = name == 'small'
        cols = 32 if is_small else 16
        cell_width = 8 if is_small else 16
        expected = (256, 48 if is_small else 80)
        if im.size != expected or im.mode != 'P':
            raise ValueError(f'Invalid Cyrillic atlas {font_path}: {im.size}, {im.mode}')
        widths = []
        for i, letter in enumerate(LETTERS):
            cell = im.crop((i % cols * cell_width, i // cols * 16,
                            (i % cols + 1) * cell_width, (i // cols + 1) * 16))
            fg_pixels = [(x, y) for y in range(16) for x in range(cell_width)
                         if cell.getpixel((x, y)) == 1]
            if not fg_pixels:
                raise ValueError(f'Missing Cyrillic glyph {letter} ({name})')
            width = min(cell_width, max(x for x, _ in fg_pixels) + 2)
            widths.append(width)
        if is_small:
            small_widths = widths
        elif normal_widths is None:
            normal_widths = widths
    (ROOT / 'src/russian_glyph_widths.generated.inc').write_text(
        '/* Generated from native-pixel FRLG-style Cyrillic atlases; no resampling. */\n'
        f'static const u8 sRussianNormalGlyphWidths[66] = {{{", ".join(map(str, normal_widths))}}};\n'
        f'static const u8 sRussianSmallGlyphWidths[66] = {{{", ".join(map(str, small_widths))}}};\n')
    return normal_widths


def read_charmap():
    # English charset section, before the Japanese overlap definitions.
    text = (ROOT / 'charmap.txt').read_text()
    latin_ending = text.index('@ Hiragana')
    chars = {}
    tokens = {}
    offset = 0
    for original in text.splitlines(keepends=True):
        in_latin = offset < latin_ending
        offset += len(original)
        line = original.split('@', 1)[0].strip()
        match = re.match(r'(.+?)\s*=\s*((?:[0-9A-Fa-f]{2}(?:\s+|$))+)', line)
        if not match:
            continue
        left, right = match.group(1).strip(), match.group(2).strip()
        value = bytes(int(x, 16) for x in right.split())
        if left.startswith("'") and left.endswith("'"):
            if not in_latin:
                continue
            try:
                v = ast.literal_eval(left)
            except (SyntaxError, ValueError):
                continue
            if len(v) == 1:
                chars[v] = value
        else:
            tokens[left] = value
    return chars, tokens


def encode(text: str) -> bytes:
    chars, tokens = read_charmap()
    out = bytearray()
    i = 0
    while i < len(text):
        c = text[i]
        if c in LETTERS:
            out.extend([0xF9, GLYPH_BASE + LETTERS.index(c)])
            i += 1
        elif c == '{':
            end = text.find('}', i + 1)
            if end < 0:
                raise ValueError(f'Unclosed token in {text!r}')
            name = text[i + 1:end]
            if name not in tokens:
                raise ValueError(f'Unsupported token {{{name}}} in {text!r}')
            out.extend(tokens[name]);i=end+1
        elif c == '\\' and i + 1 < len(text):
            esc = text[i + 1]
            escape = {'n': 0xFE, 'p': 0xFB, 'l': 0xFA}
            if esc in escape:
                out.append(escape[esc])
            elif esc in ('\\', '"', "'"):
                out.extend(chars[esc])
            else:
                raise ValueError(f'Unsupported escape \\{esc} in {text!r}')
            i += 2
        elif c == '$':
            if i != len(text)-1:
                raise ValueError('EOS is only allowed at the end of a string')
            out.append(0xFF);i += 1
        elif c in chars:
            out.extend(chars[c]);i += 1
        else:
            raise ValueError(f'Character {c!r} is not supported by the GBA EN/RU font encoding')
    if not out or out[-1] != 0xFF:
        out.append(0xFF)
    return bytes(out)


def emit(data):
    return ' { ' + ', '.join('0x%02X' % b for b in data) + ' }'


def validated_global(row):
    symbol = row['symbol']
    if not re.fullmatch(r'[A-Za-z_]\w*', symbol):
        return False
    path = ROOT / row['file']
    if row['type'] == 'asm':
        # Do not reference local (. single colon) labels from another object.
        return bool(re.search(r'(?m)^\s*' + re.escape(symbol) + r'::', path.read_text()))
    # Only global C u8 arrays can be referenced across translation units.
    if row['type'] == 'c':
        return bool(re.search(r'(?m)^\s*const\s+u8\s+' + re.escape(symbol) + r'\s*\[\s*\]\s*=\s*_\(', path.read_text()))
    return False


def build_lookup():
    from translate import protected_tokens, check_translation
    with CSV.open(encoding='utf-8-sig', newline='') as fp:
        rows = list(csv.DictReader(fp))
    lines = [
        '/* Generated from localization/en_ru.csv; DO NOT EDIT BY HAND. */',
        'struct LocalizedTextPair { const u8 *english; const u8 *russian; };',
        'static const u8 sLanguageNameEnglish[] = { ' + ', '.join(f'0x{x:02X}' for x in encode('ENGLISH')) + ' };',
        'static const u8 sLanguageNameRussian[] = { ' + ', '.join(f'0x{x:02X}' for x in encode('РУССКИЙ')) + ' };',
        'static const u8 sLanguageLabelRussian[] = { ' + ', '.join(f'0x{x:02X}' for x in encode('ЯЗЫК')) + ' };',
        'static const u8 sLanguageLabelEnglish[] = { ' + ', '.join(f'0x{x:02X}' for x in encode('LANGUAGE')) + ' };'
    ]
    pair = []
    omitted = []
    used = set()
    for row in rows:
        if not row['russian'].strip():
            continue
        errors = check_translation(row)
        if errors:
            raise ValueError(row['key'] + ': ' + '; '.join(errors))
        if not validated_global(row):
            omitted.append(row['key']);continue
        symbol = row['symbol']
        if symbol in used:
            omitted.append(row['key']);continue
        used.add(symbol)
        data = encode(row['russian'])
        # A deliberately high per-string cap; GBA text boxes may need wrapping.
        if len(data) > 1024:
            raise ValueError(f'{row["key"]} is too large for gStringVar4')
        name = f'sLocalizedRussian_{len(pair)}'
        lines.append(f'extern const u8 {symbol}[];')
        lines.append(f'static const u8 {name}[] = {emit(data)};')
        pair.append((symbol, name))
    lines.append(f'static const struct LocalizedTextPair sLocalizedTextPairs[{max(1,len(pair))}] = {{')
    if not pair:
        lines.append('    { NULL, NULL },')
    else:
        lines.extend(f'    {{ {a}, {b} }},' for a,b in pair)
    lines.append('};')
    (ROOT/'src/localization_ru.generated.inc').write_text('\n'.join(lines)+'\n')
    print(f'Generated lookup: {len(pair)} mapped strings; {len(omitted)} omitted (local/unsupported source symbol).')
    if omitted:
        (ROOT/'localization/UNMAPPED_TRANSLATIONS.txt').write_text('\n'.join(omitted)+'\n')
    else:
        (ROOT/'localization/UNMAPPED_TRANSLATIONS.txt').unlink(missing_ok=True)
    return len(pair)


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Generate bilingual ROM text and optional donor bitmap fonts')
    parser.add_argument('--texts-only', action='store_true', help='Only generate C text lookup from the HTML editor CSV; no Pillow dependency')
    args = parser.parse_args()
    if not args.texts_only:
        build_fonts()
    build_lookup()
    print('Russian font glyphs:', len(LETTERS), 'extended byte range: F9 80..F9 C1')

if __name__ == '__main__':
    main()
