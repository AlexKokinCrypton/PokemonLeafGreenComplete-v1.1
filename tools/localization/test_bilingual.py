#!/usr/bin/env python3
"""Small deterministic checks for the bilingual data/encoding toolchain."""
import csv
import importlib.util
import sys
import unittest
from pathlib import Path
from PIL import Image

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import build_bilingual as b
import translate as t


class TestBilingual(unittest.TestCase):
    def test_unicode_alphabet_has_separate_codes(self):
        self.assertEqual(len(b.LETTERS), 66)
        self.assertEqual(len(set(b.DONOR_INDEX.values())), 66)
        for i, c in enumerate(b.LETTERS):
            self.assertEqual(b.encode(c), bytes([0xF9, 0x80 + i, 0xFF]))

    def test_both_languages_and_protected_controls(self):
        ru = 'Привет, {PLAYER}!\\n'
        encoded = b.encode(ru)
        self.assertIn(bytes([0xFD, 0x01]), encoded)
        self.assertEqual(encoded[-2:], bytes([0xFE, 0xFF]))
        self.assertEqual(b.encode('Hello, {PLAYER}!\\n')[-2:], bytes([0xFE, 0xFF]))
        self.assertEqual(t.protected_tokens('Hello, {PLAYER}!\\n'),
                         t.protected_tokens(ru))
        self.assertEqual(b.encode('РУССКИЙ')[-1], 0xFF)
        self.assertEqual(b.encode('ENGLISH')[-1], 0xFF)

    def test_unsupported_code_fails_closed(self):
        for text in ('Русский {NONEXISTENT}', 'Текст\\x', 'а$б', 'hello🙂'):
            with self.assertRaises(ValueError):
                b.encode(text)

    def test_pokemon_style_cyrillic_atlases_and_no_resampling(self):
        # Font glyphs are committed as PNG bitmaps. Regeneration may validate
        # widths but must never stretch/rewrite the glyph pixels.
        import hashlib
        atlas_paths = [b.FONTS / f'russian_{name}.png'
                       for name in ('normal', 'male', 'female', 'small')]
        before = [hashlib.sha256(p.read_bytes()).hexdigest() for p in atlas_paths]
        widths = b.build_fonts()
        after = [hashlib.sha256(p.read_bytes()).hexdigest() for p in atlas_paths]
        self.assertEqual(before, after)
        self.assertEqual(len(widths), 66)
        self.assertTrue(all(3 <= w <= 13 for w in widths))
        for name, font_path in zip(('normal', 'male', 'female', 'small'), atlas_paths):
            im = Image.open(font_path)
            is_small = name == 'small'
            gw, cols = (8, 32) if is_small else (16, 16)
            self.assertEqual(im.size, (256, 48 if is_small else 80))
            self.assertEqual(im.mode, 'P')
            self.assertTrue(set(im.tobytes()).issubset({0, 1, 2, 3}))
            self.assertIn(2, im.tobytes(), 'GBA English fonts use a one-pixel gray shade after the dark outline')
            self.assertEqual(im.getpalette(), Image.open(b.FONTS / 'latin_normal.png').getpalette())
            for i, c in enumerate(b.LETTERS):
                dst = im.crop(((i % cols) * gw, i // cols * 16,
                               (i % cols + 1) * gw, (i // cols + 1) * 16))
                active = [(x, y) for x in range(gw) for y in range(16)
                          if dst.getpixel((x, y)) == 1]
                self.assertTrue(active, (name, c))
                self.assertLessEqual(max(y for _, y in active), 12 if is_small else 13, (name, c))

    def test_cyrillic_latin_shapes_and_native_baselines(self):
        # A capital Russian А is literally the exact original English A bitmap,
        # not an imitated or resized glyph; same for every paired Latin shape.
        from generate_pixel_cyrillic import COPIES, LETTERS
        self.assertEqual(len(LETTERS), 66)
        for size in ('normal', 'small'):
            ru = Image.open(b.FONTS / f'russian_{size}.png')
            en = Image.open(b.FONTS / f'latin_{size}.png')
            cw,cols = (8,32) if size == 'small' else (16,16)
            for russian, latin in COPIES.items():
                i = LETTERS.index(russian)
                j = (0xBB + ord(latin)-ord('A')) if latin.isupper() else (0xD5 + ord(latin)-ord('a'))
                r = ru.crop(((i%cols)*cw,(i//cols)*16,(i%cols+1)*cw,(i//cols+1)*16))
                e = en.crop(((j%cols)*cw,(j//cols)*16,(j%cols+1)*cw,(j//cols+1)*16))
                self.assertEqual(r.tobytes(), e.tobytes(), (size, russian, latin))

    def test_option_menu_rows_and_vram_window_buffers(self):
        import re
        src = (b.ROOT / 'src/option_menu.c').read_text()
        self.assertIn('#define OPTION_ROW_HEIGHT 13', src)
        self.assertIn('MENUITEM_LANGUAGE,', src)
        self.assertIn('MENUITEM_CANCEL,', src)
        # Enlarge the text area without colliding with the help window or frame graphics.
        segment = src.split('static const struct WindowTemplate sOptionMenuWinTemplates[]', 1)[1].split('DUMMY_WIN_TEMPLATE', 1)[0]
        windows = re.findall(r'\{\s*\.bg\s*=\s*\d+.*?\.width\s*=\s*(\d+).*?\.height\s*=\s*(\d+).*?\.baseBlock\s*=\s*(0x[\da-fA-F]+|\d+)', segment, re.S)
        self.assertGreaterEqual(len(windows), 3)
        spans = [(int(base, 0), int(base, 0) + int(w) * int(h)) for w, h, base in windows[:3]]
        for left, right in zip(spans, spans[1:]):
            self.assertLessEqual(left[1], right[0], 'Option UI tile buffers overlap and corrupt the help bar')
        self.assertLessEqual(spans[-1][1], 0x1AA,
                             'Option UI tile buffers overlap menu frame graphics')
        self.assertEqual(int(windows[1][1]), 13)
        self.assertEqual(8 * 13, 13 * 8,
                         'Eight 13-pixel rows must fit exactly within 13 tiles')
        self.assertIn('OPTION_LABEL_X 8', src)
        self.assertIn('OPTION_VALUE_X 111', src)
        self.assertIn('OPTION_TEXT_Y 0', src)
        self.assertIn('(6 * 8)', src)

    def test_catalog_symbol_alignment(self):
        with b.CSV.open(encoding='utf-8-sig', newline='') as fp:
            rows = list(csv.DictReader(fp))
        self.assertEqual(len(rows), 11968)
        self.assertEqual(len({r['key'] for r in rows}), len(rows))
        options = next(r for r in rows if r['file'] == 'src/strings.c' and r['symbol'] == 'gText_Option')
        self.assertEqual(options['english'], 'OPTION')
        self.assertEqual(options['russian'], 'НАСТРОЙКИ')
        translated = [r for r in rows if r['russian']]
        self.assertGreaterEqual(len(translated), 21)  # Baseline UI strings plus user translations
        for row in translated:
            self.assertFalse(t.check_translation(row))
            self.assertTrue(b.validated_global(row), row['key'])

    def test_original_latin_shaders_kept(self):
        src = (b.ROOT / 'src/localization.c').read_text()
        self.assertIn('GetGameLanguage() != GAME_LANGUAGE_RUSSIAN', src)
        self.assertIn('return english;', src)
        self.assertIn('filler_90[0]', src)
        g = (b.ROOT / 'src/text.c').read_text()
        self.assertIn('IS_RUSSIAN_GLYPH', g)
        self.assertIn('sFontNormalLatinGlyphs', g)
        self.assertIn('sFontRussianNormalGlyphs', g)


if __name__ == '__main__':
    unittest.main(verbosity=2)
