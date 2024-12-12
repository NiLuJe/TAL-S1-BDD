#!/bin/sh

# Lookup Feature
sqlite3 -header -csv DB/conlangs.db "SELECT PhonemeID, IPA, Type, Vowel_Height, Vowel_Backness, Vowel_Roundness, Consonant_Voicing, Consonant_ArticulationManner, Consonant_ArticulationPlace, Modifiers, PhonemeFeature.Name AS Feature FROM PhonemeBank LEFT JOIN PhonemeFeature ON PhonemeBank.Feature = PhonemeFeature.ID;" > data/PhonemeBank.csv
