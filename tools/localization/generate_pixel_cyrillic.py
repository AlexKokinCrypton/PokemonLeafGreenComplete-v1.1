#!/usr/bin/env python3
"""Draw a native-resolution Pokémon FR/LG-style Cyrillic bitmap alphabet.

Latin look-alikes are copied pixel-for-pixel from the original game glyphs.
Remaining Cyrillic shapes are hand-authored pixel stems with the *same*
palette and directional one-pixel light shadow as the Latin fonts.
No TrueType font, raster resizing or antialias filters are involved.

Run only when redesigning fonts, never as part of normal translation export.
"""
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
FONT_DIR = ROOT / "graphics/fonts"
UPPER = "АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"
LOWER = UPPER.lower()
LETTERS = UPPER + LOWER
# All custom capitals are 7 pixel-high skeletons, ascenders for ь/ъ, etc.
# '#' is dark primary ink, '.' is transparent in the hand-authored *skeleton*.
CAP = {
'Б': ["#####", "#....", "#....", "####.", "#...#", "#...#", "####."],
'Г': ["#####", "#....", "#....", "#....", "#....", "#....", "#...."],
'Д': ["..###..", "..#.#..", ".#..#..", ".#..#..", ".#..#..", "#####..", "#...##."],
'Ж': ["#.#.#..", "#.#.#..", ".###...", "..#....", ".###...", "#.#.#..", "#.#.#.."],
'З': [".###.", "#...#", "....#", "..##.", "....#", "#...#", ".###."],
'И': ["#...#", "#..##", "#.#.#", "#.#.#", "##..#", "#...#", "#...#"],
'Й': ["#...#", "#..##", "#.#.#", "#.#.#", "##..#", "#...#", "#...#"],
'Л': ["..###", "..#.#", ".#..#", ".#..#", ".#..#", "#...#", "#...#"],
'П': ["#####", "#...#", "#...#", "#...#", "#...#", "#...#", "#...#"],
'У': ["#...#", "#...#", "#...#", ".###.", "...#.", "..#..", ".#..."],
'Ф': ["..#....", ".###...", "#.#.#..", "#.#.#..", "#.#.#..", ".###...", "..#...."],
'Ц': ["#...#.", "#...#.", "#...#.", "#...#.", "#...#.", "#####.", ".....#"],
'Ч': ["#...#", "#...#", "#...#", ".####", "....#", "....#", "....#"],
'Ш': ["#.#.#..", "#.#.#..", "#.#.#..", "#.#.#..", "#.#.#..", "#.#.#..", "#####.."],
'Щ': ["#.#.#..", "#.#.#..", "#.#.#..", "#.#.#..", "#.#.#..", "#####..", ".....#."],
'Ъ': ["##.....", ".#.....", ".#.....", ".####..", ".#...#.", ".#...#.", ".####.."],
'Ы': ["#....#.", "#....#.", "#....#.", "####.#.", "#...##.", "#...##.", "####.#."],
'Ь': ["#....", "#....", "#....", "####.", "#...#", "#...#", "####."],
'Э': [".###.", "#...#", "....#", "..###", "....#", "#...#", ".###."],
'Ю': ["#..###.", "#.#...#", "#.#...#", "###...#", "#.#...#", "#.#...#", "#..###."],
'Я': [".####", "#...#", "#...#", ".####", "..#.#", ".#..#", "#...#"],
}
SMALL = {
'б':[".###.", "#....", "####.", "#...#", ".###."],
'в':["####.", "#...#", "####.", "#...#", "####."],
'г':["####.", "#....", "#....", "#....", "#...."],
'д':["..##..", ".#.#..", ".#.#..", "####..", "#...#."],
'ж':["#.#.#..", ".###...", "..#....", ".###...", "#.#.#.."],
'з':[".###.", "....#", "..##.", "....#", ".###."],
'и':["#...#", "#..##", "#.#.#", "##..#", "#...#"],
'й':["#...#", "#..##", "#.#.#", "##..#", "#...#"],
'л':["..###", "..#.#", ".#..#", ".#..#", "#...#"],
'м':["#...#", "##.##", "#.#.#", "#...#", "#...#"],
'н':["#...#", "#...#", "#####", "#...#", "#...#"],
'п':["#####", "#...#", "#...#", "#...#", "#...#"],
'т':["#####", "..#..", "..#..", "..#..", "..#.."],
'ф':["..#....", ".###...", "#.#.#..", ".###...", "..#...."],
'ц':["#...#.", "#...#.", "#...#.", "#####.", ".....#"],
'ч':["#...#", "#...#", ".####", "....#", "....#"],
'ш':["#.#.#..", "#.#.#..", "#.#.#..", "#.#.#..", "#####.."],
'щ':["#.#.#..", "#.#.#..", "#.#.#..", "#####..", ".....#."],
'ъ':["##.....", ".#.....", ".####..", ".#...#.", ".####.."],
'ы':["#....#.", "#....#.", "####.#.", "#...##.", "####.#."],
'ь':["#....", "#....", "####.", "#...#", "####."],
'э':[".###.", "....#", "..###", "....#", ".###."],
'ю':["#..###.", "#.#...#", "###...#", "#.#...#", "#..###."],
'я':[".####", "#...#", ".####", "..#.#", "#...#"],
}
# Same-shaped glyphs use the original FR/LG pixels, preserving alignment,
# outline, shadow/soft-gray and native width exactly.
COPIES = {
'А':'A','В':'B','Е':'E','К':'K','М':'M','Н':'H','О':'O','Р':'P','С':'C','Т':'T','Х':'X',
'а':'a','е':'e','к':'k','о':'o','р':'p','с':'c','у':'y','х':'x'
}
CHARMAP = {**{chr(ord('A')+i):0xBB+i for i in range(26)},
           **{chr(ord('a')+i):0xD5+i for i in range(26)}}
PALETTE = Image.open(FONT_DIR/'latin_normal.png').getpalette()


def paint_custom(rows, is_small, *, top=None, bottom_extra=None):
    """Render crisp black skeleton and the exact directional gray shadow.
    Returns one 16px-high, 8px- or 16px-wide tile. A special diacritic may
    occupy y=1..3 above baseline, and descender at y=11.
    """
    cw = 8 if is_small else 16
    if top is None:
        top = 6 if len(rows)==5 else (4 if is_small else 3)
    if not is_small and len(rows)==7:
        # GBA English NORMAL has an 8px cap vs SMALL's 7px cap.
        rows = rows[:3]+rows[3:4]+rows[3:]
    ink=set()
    for yi,row in enumerate(rows):
        for x,ch in enumerate(row):
            if ch=='#': ink.add((x,top+yi))
    if bottom_extra:
        ink.update(bottom_extra)
    if max(x for x,_ in ink)>cw-2:
        raise ValueError(('glyph too wide', cw, rows))
    tile = Image.new('P',(cw,16),color=0); tile.putpalette(PALETTE)
    # Pixel 3 is fill/background, equivalent to the original Latin glyphs.
    painted_width=max(x for x,_ in ink)+2
    for y in range(1,13 if is_small else 14):
        for x in range(painted_width): tile.putpixel((x,y),3)
    for x,y in sorted(ink):
        if y+1>=16: raise ValueError(('glyph too tall',rows))
        for px,py in ((x+1,y),(x,y+1),(x+1,y+1)):
            if px<cw and py<16 and (px,py) not in ink:
                tile.putpixel((px,py),2)
    for x,y in sorted(ink): tile.putpixel((x,y),1)
    return tile


def draw_letter(letter, is_small, latin):
    cw=8 if is_small else 16
    cols=32 if is_small else 16
    if letter in COPIES:
        g=CHARMAP[COPIES[letter]]
        return latin.crop(((g%cols)*cw,(g//cols)*16,((g%cols)+1)*cw,((g//cols)+1)*16))
    if letter in UPPER:
        base='И' if letter=='Й' else letter
        if letter=='Ё':
            tile=draw_letter('Е',is_small,latin)
        else:
            tile=paint_custom(CAP[base],is_small)
        if letter=='Ё':
            # top diacritics on distinct 1px dots, with a 1px shadow
            for x in (1,3):
                tile.putpixel((x,1 if is_small else 0),1)
                tile.putpixel((x+1,1 if is_small else 0),2)
        elif letter=='Й':
            for x,y in ((1,1 if is_small else 0),(2,2 if is_small else 1),(3,1 if is_small else 0)):
                tile.putpixel((x,y),1)
        return tile
    if letter=='ё':
        tile=draw_letter('е',is_small,latin)
        for x in (1,3):tile.putpixel((x,3),1)
        return tile
    if letter=='й':
        tile=paint_custom(SMALL['и'],is_small)
        for x,y in ((1,3),(2,4),(3,3)):tile.putpixel((x,y),1)
        return tile
    row=SMALL[letter]
    tile=paint_custom(row,is_small)
    return tile


def generate():
    results={}
    for short in (False,True):
        suffix='small' if short else 'normal'
        latin=Image.open(FONT_DIR / f'latin_{suffix}.png')
        w=8 if short else 16; cols=32 if short else 16
        im=Image.new('P',(256,48 if short else 80),color=0)
        im.putpalette(PALETTE)
        for i,c in enumerate(LETTERS):
            cell=draw_letter(c,short,latin)
            im.paste(cell,((i%cols)*w,(i//cols)*16))
        results[suffix]=im
    results['normal'].save(FONT_DIR/'russian_normal.png',optimize=True)
    for gender in ('male','female'):
        results['normal'].save(FONT_DIR/f'russian_{gender}.png',optimize=True)
    results['small'].save(FONT_DIR/'russian_small.png',optimize=True)
    print('Generated FRLG-style Cyrillic glyphs:',len(LETTERS),'for normal/male/female/small')

if __name__ == '__main__': generate()
