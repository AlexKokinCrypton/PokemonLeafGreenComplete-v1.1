# Russian localization donor

Source: user-provided Russian Pokémon LeafGreen ROM (Stealth / Shedevr translation lineage).

Recovered so far:
- normal full-width font
- male full-width font
- female full-width font

The donor ROM uses a custom character mapping. These files are preserved as donor assets only and are not yet wired into the build, because doing so before reconstructing the ROM's character map would make the existing English source strings render incorrectly.

Next localization step:
1. reconstruct custom byte -> Cyrillic mapping from the extracted font;
2. decode translated strings from the donor ROM;
3. map decoded strings back to decomp source labels/scripts;
4. replace font assets + charmap in source;
5. add the new project-specific Russian strings in the same terminology/style.
