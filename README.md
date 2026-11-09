**Без локального Python:** [пошаговая инструкция по HTML → CSV → GitHub Actions](БЕЗ_PYTHON_ИНСТРУКЦИЯ.md).

**EN/RU bilingual implementation:** see [BILINGUAL_EN_RU.md](BILINGUAL_EN_RU.md) for fonts, language selection, translation import, build instructions and current QA limitations.

# Pokémon LeafGreen Complete v1.1 — customization and localization

**LeafGreen Complete** contains gameplay modifications described in
[`PLG_COMPLETE_CHANGELOG.md`](PLG_COMPLETE_CHANGELOG.md).

**Standalone offline HTML translator (recommended):** Double-click
[`tools/localization/leafgreen-offline-editor.html`](tools/localization/leafgreen-offline-editor.html)
from your file manager. It already contains all 11,967 source strings; no server, Python or
Internet is needed. Protected game tokens are non-editable chips. Click **Save string** and,
when ready, **Download CSV**, then copy the resulting `en_ru.csv` over
`localization/en_ru.csv` in this repository. Use **Load CSV** to reopen your work.

**Alternative (direct CSV saving via local Python server):**

```bash
python3 tools/localization/translate.py serve
```

Open <http://127.0.0.1:8765> in your browser. See
[`localization/README_RU.md`](localization/README_RU.md) for instructions (Russian).
The English resources are preserved. Language selection and Cyrillic font support are present in source code, but an emulator-tested ROM build is **not yet confirmed**.

**Gift-fix notes and gameplay testing status:**
[`REWARD_FIX_AND_TESTING_RU.md`](REWARD_FIX_AND_TESTING_RU.md).

---

# Pokémon FireRed and LeafGreen

This is a decompilation of English Pokémon FireRed and LeafGreen.

It builds the following ROM images:

* [**pokefirered.gba**](https://datomatic.no-intro.org/?page=show_record&s=23&n=1616) `sha1: 41cb23d8dccc8ebd7c649cd8fbb58eeace6e2fdc`
* [**pokeleafgreen.gba**](https://datomatic.no-intro.org/?page=show_record&s=23&n=1617) `sha1: 574fa542ffebb14be69902d1d36f1ec0a4afd71e`
* [**pokefirered_rev1.gba**](https://datomatic.no-intro.org/?page=show_record&s=23&n=1672) `sha1: dd5945db9b930750cb39d00c84da8571feebf417`
* [**pokeleafgreen_rev1.gba**](https://datomatic.no-intro.org/index.php?page=show_record&s=23&n=1668) `sha1: 7862c67bdecbe21d1d69ce082ce34327e1c6ed5e`
* [**pokefirered_switch.gba**](https://datomatic.no-intro.org/index.php?page=show_record&s=23&n=x550) `sha1: baa452d0b24629dd7782cfc07a8984085dde1311`
* [**pokeleafgreen_switch.gba**](https://datomatic.no-intro.org/index.php?page=show_record&s=23&n=x551) `sha1: 62b9fc77549dbc67032eb6cbd0ea6ad3b825690f`

To set up the repository, see [INSTALL.md](INSTALL.md).

For contacts and other pret projects, see [pret.github.io](https://pret.github.io/).
