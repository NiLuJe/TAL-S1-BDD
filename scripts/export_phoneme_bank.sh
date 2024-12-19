#!/bin/sh

# Lookup Feature
QUERY="
SELECT
	PhonemeID,
	IPA,
	Type,
	Vowel_Height,
	Vowel_Backness,
	Vowel_Roundness,
	Consonant_Voicing,
	Consonant_ArticulationManner,
	Consonant_ArticulationPlace,
	Modifiers,
	PhonemeFeature.Name AS Feature
FROM
	PhonemeBank
	LEFT JOIN PhonemeFeature ON PhonemeBank.Feature = PhonemeFeature.ID;
"
sqlite3 -header -csv DB/conlangs.db "${QUERY}" > data/PhonemeBank-Exported.csv

# Export PhonemeFeature, too, since we add stuff to it during PhonemeBank creation
sqlite3 -header -csv DB/conlangs.db "SELECT * FROM PhonemeFeature;" > data/PhonemeFeature-Exported.csv
