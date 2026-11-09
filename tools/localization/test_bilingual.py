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

    def test_all_font_glyphs_have_pixels(self):
        for name in ('normal', 'male', 'female'):
            donor = Image.open(b.DONOR / f'rus_{name}.png')
            generated = Image.open(b.FONTS / f'russian_{name}.png')
            self.assertEqual(generated.size, (256, 80))
            for i, c in enumerate(b.LETTERS):
                src_idx = b.DONOR_INDEX[c]
                src = donor.crop((src_idx % 16 * 16, src_idx // 16 * 16,
                                  (src_idx % 16 + 1) * 16, (src_idx // 16 + 1) * 16))
                dst = generated.crop((i % 16 * 16, i // 16 * 16,
                                      (i % 16 + 1) * 16, (i // 16 + 1) * 16))
                self.assertEqual(list(src.getdata()), list(dst.getdata()), (name, c))
                self.assertIn(1, list(dst.getdata()), (name, c))
        self.assertEqual(Image.open(b.FONTS / 'russian_small.png').size, (256, 48))

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
