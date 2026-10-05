# Pokémon LeafGreen RU Complete — implementation checkpoint

## Implemented gameplay changes

- LeafGreen is the single target version.
- LINK CABLE item added using unused item slot 99; price ₽8000; own icon source asset.
- Celadon Department Store 4F sells Sun Stone, Moon Stone and Link Cable.
- Link Cable performs EVO_TRADE and EVO_TRADE_ITEM evolutions while preserving normal trade evolution.
- Held items are still required/consumed for trade-item evolutions.
- Explicit National Dex gate for Link Cable Johto evolutions.
- Eevee: Sun Stone -> Espeon; Moon Stone -> Umbreon, only after National Dex.
- TMs are reusable.
- HM moves can be replaced/forgotten like normal moves.
- Text speed defaults to Fast and all text speed presets are faster.
- Explicit battle-animation delays scaled to ~70% of vanilla.
- Oak gives rival's Kanto starter after 51 caught, once.
- Bill gives the remaining Kanto starter after the Ruby/Sapphire network quest, once.
- Cinnabar Lab gives the unchosen Mt. Moon fossil after National Dex, once.
- FireRed-exclusive species injected at 1% in their original FR map/method groups by borrowing probability from the common slot.
- Altering Cave: Zubat 20%; Mareep/Aipom/Pineco/Shuckle/Teddiursa/Houndour/Stantler/Smeargle 10% each.
- Mew: static Lv.40 Altering Cave event; National Dex + Ruby/Sapphire quest; fateful encounter; KO-respawn protection.
- Legendary beasts: starter dependency removed; all three roam sequentially in random order; one active at a time; KO resets same beast; Roar/run does not delete it; all three caught unlock progression flag.
- MysticTicket: Celio after all three beasts are caught; Navel Rock enabled.
- AuroraTicket: Celio after Lugia + Ho-Oh are caught and Elite Four rematch has been completed; Birth Island enabled.
- Persistent caught flags added for Articuno, Zapdos, Moltres, Mewtwo, Lugia, Ho-Oh and Deoxys.
- Elite Four respawns unique legends only if not caught.
- Snorlax safety: if both overworld Snorlax are gone and neither was caught, Route 12 Snorlax is restored after Hall of Fame.
- Safari Zone: each 1% land slot is raised to 3% by borrowing 4 percentage points total from the 20% common slot.
- Victory Road trainer parties raised by +2 levels; Elite Four unchanged.

## Validation performed

- items.json valid JSON.
- wild_encounters.json valid JSON.
- Altering Cave map.json valid JSON.
- Native pokefirered tools build successfully (mapjson/jsonproc/preproc/gbagfx/etc.).
- Event script preprocessing succeeds.
- Core modified C files (roamer/battle_main/wild_encounter/wild_pokemon_area/battle_anim/pokemon) pass preprocessing + clang syntax checks where generated binary assets are not required.
- Link Cable PNG/PAL successfully convert through gbagfx to GBA formats.

## Remaining validation / localization work

1. Full Russian source-level localization import from the user-provided translated ROM. The Russian donor fonts are already extracted and preserved; custom charmap and translated-script recovery are still in progress.
2. Final ARM/GBA link test requires `agbcc` and/or `arm-none-eabi-gcc`; this execution environment currently lacks the cross toolchain.
