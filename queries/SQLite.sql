-- Phonemes used in SVO Langs
SELECT DISTINCT
	IPA
FROM
	PhonemeBank
	JOIN Phonology ON PhonemeBank.PhonemeID = Phonology.PhonemeID
	JOIN MorphoSyntax ON Phonology.LangID = MorphoSyntax.LangID
	JOIN LangInfo ON MorphoSyntax.LangID = LangInfo.LangID
WHERE
	MorphoSyntax.WordOrder = "SVO";

-- Phoneme Features comparison
SELECT
	LangName AS Langue,
	IPA AS Phonème,
	Name AS Propriété
FROM
	LangInfo,
	PhonemeBank,
	PhonemeFeature
	JOIN Phonology ON PhonemeBank.PhonemeID = Phonology.PhonemeID
	AND PhonemeBank.Feature = PhonemeFeature.ID
	AND Phonology.LangID = LangInfo.LangID
ORDER BY
	Langue,
	Propriété,
	Phonème;

-- Compare MorphoSyntax feats for Langs w/ Diphthongs
SELECT
	LangName AS Langue,
	IPA AS Phonème,
	WordOrder AS Ordre,
	CaseCount AS Cas
FROM
	LangInfo,
	PhonemeBank,
	MorphoSyntax
	JOIN Phonology,
	PhonemeFeature ON PhonemeBank.PhonemeID = Phonology.PhonemeID
	AND PhonemeBank.Feature = PhonemeFeature.ID
	AND Phonology.LangID = LangInfo.LangID
	AND MorphoSyntax.LangID = LangInfo.LangID
WHERE
	PhonemeFeature.Name LIKE "Diphthong"
ORDER BY
	Langue,
	Phonème;

--
SELECT
	L1.LangName AS Language_1,
	L2.LangName AS Language_2,
	COUNT(*) AS Shared_Phonemes
FROM
	Phonology AS P1
	INNER JOIN Phonology AS P2 ON P1.PhonemeID = P2.PhonemeID
	AND P1.LangID != P2.LangID
	INNER JOIN LangInfo AS L1 ON P1.LangID = L1.LangID
	INNER JOIN LangInfo AS L2 ON P2.LangID = L2.LangID
GROUP BY
	L1.LangName,
	L2.LangName
ORDER BY
	Shared_Phonemes DESC;
