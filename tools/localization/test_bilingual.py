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

    def test_crisp_cyrillic_atlases_and_no_resampling(self):
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
        self.assertTrue(all(5 <= w <= 10 for w in widths))
        for name, font_path in zip(('normal', 'male', 'female', 'small'), atlas_paths):
            im = Image.open(font_path)
            is_small = name == 'small'
            gw, cols = (8, 32) if is_small else (16, 16)
            self.assertEqual(im.size, (256, 48 if is_small else 80))
            self.assertEqual(im.mode, 'P')
            self.assertTrue(set(im.tobytes()).issubset({0, 1, 2, 3}))
            for i, c in enumerate(b.LETTERS):
                dst = im.crop(((i % cols) * gw, i // cols * 16,
                               (i % cols + 1) * gw, (i // cols + 1) * 16))
                active = [(x, y) for x in range(gw) for y in range(16)
                          if dst.getpixel((x, y)) == 1]
                self.assertTrue(active, (name, c))
                self.assertLessEqual(max(y for _, y in active), 14, (name, c))

    def test_option_menu_rows_and_vram_window_buffers(self):
        import re
        src = (b.ROOT / 'src/option_menu.c').read_text()
        self.assertIn('#define OPTION_ROW_HEIGHT 11', src)
        self.assertIn('MENUITEM_LANGUAGE,', src)
        self.assertIn('MENUITEM_CANCEL,', src)
        # Original help-window tile base starts at 0x16e. The extra
        # Language row must NOT enlarge the options window into that buffer.
        segment = src.split('static const struct WindowTemplate sOptionMenuWinTemplates[]', 1)[1].split('DUMMY_WIN_TEMPLATE', 1)[0]
        windows = re.findall(r'\{\s*\.bg\s*=\s*\d+.*?\.width\s*=\s*(\d+).*?\.height\s*=\s*(\d+).*?\.baseBlock\s*=\s*(0x[\da-fA-F]+|\d+)', segment, re.S)
        self.assertGreaterEqual(len(windows), 3)
        spans = [(int(base, 0), int(base, 0) + int(w) * int(h)) for w, h, base in windows[:3]]
        for left, right in zip(spans, spans[1:]):
            self.assertLessEqual(left[1], right[0], 'Option UI tile buffers overlap and corrupt the help bar')
        self.assertLessEqual(7 * 11 + 2 + 13, 12 * 8,
                             'Cancel row extends past the options window')

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
