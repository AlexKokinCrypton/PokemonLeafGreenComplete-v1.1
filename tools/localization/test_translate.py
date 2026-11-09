"""Run `python3 -m unittest discover -s tools/localization -p 'test_*.py'`."""
import importlib.util
import pathlib
import unittest

location = pathlib.Path(__file__).with_name('translate.py')
spec = importlib.util.spec_from_file_location('leafgreen_translate', location)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class LockedTokensTest(unittest.TestCase):
    def test_original_tokens_are_immutable(self):
        en = 'Hello, {PLAYER}!\\nYou got {STR_VAR_1}!\\p$'
        self.assertEqual(mod.protected_tokens(en),
                         ['{PLAYER}', r'\n', '{STR_VAR_1}', r'\p', '$'])
        parts = mod.editing_parts(en)
        self.assertEqual(len(parts), 6)
        parts[0] = 'Привет, '
        parts[2] = 'Получено '
        result = mod.join_editing_parts(en, parts)
        self.assertEqual(mod.protected_tokens(en), mod.protected_tokens(result))
        self.assertTrue(result.startswith('Привет, {PLAYER}!'))

    def test_extra_codes_cannot_be_typed(self):
        en = 'Welcome, {PLAYER}!$'
        for attempt in ['{RIVAL}', r'\n', '$', '{PLAYER}']:
            with self.subTest(attempt=attempt):
                with self.assertRaises(ValueError):
                    mod.join_editing_parts(en, ['Привет ' + attempt, '', ''])

    def test_codes_cannot_be_removed_or_reordered(self):
        en = '{PLAYER} received {STR_VAR_1}!$'
        reversed_tokens = '{STR_VAR_1} получил {PLAYER}!$'
        removed_token = '{PLAYER} получил предмет!$'
        for translation in [reversed_tokens, removed_token]:
            self.assertIn('Locked control tokens changed',
                          '; '.join(mod.check_translation({'english': en,
                                                           'russian': translation,
                                                           'status': 'translated'})))

    def test_empty_or_bad_request_rejected(self):
        en = 'Welcome, {PLAYER}!$'
        for parts in [None, 'string', ['only one'], [12, 5, 3]]:
            with self.subTest(parts=parts):
                with self.assertRaises(ValueError):
                    mod.join_editing_parts(en, parts)

    def test_english_plain_text_is_not_locked(self):
        self.assertEqual(mod.protected_tokens('Just words.'), [])
        self.assertEqual(mod.join_editing_parts('Just words.', ['Просто слова.']), 'Просто слова.')


if __name__ == '__main__':
    unittest.main()
