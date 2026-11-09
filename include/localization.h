#ifndef GUARD_LOCALIZATION_H
#define GUARD_LOCALIZATION_H

#include "global.h"

#define GAME_LANGUAGE_ENGLISH 0
#define GAME_LANGUAGE_RUSSIAN 1
// The existing SaveBlock2 filler is used; no offsets in the save are moved.
u8 GetGameLanguage(void);
void SetGameLanguage(u8 language);
const u8 *GetLocalizedText(const u8 *english);
const u8 *GetLanguageChoiceText(u8 language);
const u8 *GetLanguageMenuLabel(void);

#endif // GUARD_LOCALIZATION_H
