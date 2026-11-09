#include "global.h"
#include "localization.h"

// The two-byte signature keeps old saves English by default. These bytes are
// in the formerly unused SaveBlock2 filler_90 field, not in game progress.
#define LANGUAGE_SAVE_MAGIC 0xC7

u8 GetGameLanguage(void)
{
    if (gSaveBlock2Ptr != NULL &&
        gSaveBlock2Ptr->filler_90[0] == LANGUAGE_SAVE_MAGIC &&
        gSaveBlock2Ptr->filler_90[1] == GAME_LANGUAGE_RUSSIAN)
        return GAME_LANGUAGE_RUSSIAN;
    return GAME_LANGUAGE_ENGLISH;
}

void SetGameLanguage(u8 language)
{
    if (gSaveBlock2Ptr == NULL)
        return;
    gSaveBlock2Ptr->filler_90[0] = LANGUAGE_SAVE_MAGIC;
    gSaveBlock2Ptr->filler_90[1] = language == GAME_LANGUAGE_RUSSIAN
        ? GAME_LANGUAGE_RUSSIAN : GAME_LANGUAGE_ENGLISH;
}

// This include is regenerated from localization/en_ru.csv. Only fully valid,
// translated strings are compiled; missing entries use the original English.
#include "localization_ru.generated.inc"

const u8 *GetLocalizedText(const u8 *english)
{
    u32 i;
    if (english == NULL || GetGameLanguage() != GAME_LANGUAGE_RUSSIAN)
        return english;
    for (i = 0; i < ARRAY_COUNT(sLocalizedTextPairs); i++)
    {
        if (sLocalizedTextPairs[i].english == english)
            return sLocalizedTextPairs[i].russian;
    }
    return english;
}

const u8 *GetLanguageChoiceText(u8 language)
{
    return language == GAME_LANGUAGE_RUSSIAN ? sLanguageNameRussian : sLanguageNameEnglish;
}

const u8 *GetLanguageMenuLabel(void)
{
    return GetGameLanguage() == GAME_LANGUAGE_RUSSIAN
        ? sLanguageLabelRussian : sLanguageLabelEnglish;
}
