/*
* Nodes & Relationships
*/

// LangInfo
CREATE CONSTRAINT LangInfo_Name IF NOT EXISTS
FOR (l:LangInfo) REQUIRE l.Name IS UNIQUE;

LOAD CSV WITH HEADERS FROM "file:///Users/niluje/Dev/TAL-S1-BDD/data/LangInfo.csv" AS row
MERGE (l:LangInfo {Name: row.LangName})
SET
	l.Creator = row.Creator,
	l.World = row.World,
	l.Spoken = toBoolean(row.Spoken),
	l.Written = toBoolean(row.Written),
	l.Usage = row.Usage,
	l.Description = row.Description;

// PhonemeFeature
CREATE CONSTRAINT PhonemeFeature_Name IF NOT EXISTS
FOR (pf:PhonemeFeature) REQUIRE pf.Name IS UNIQUE;

LOAD CSV WITH HEADERS FROM "file:///Users/niluje/Dev/TAL-S1-BDD/data/PhonemeFeature-Exported.csv" AS row
MERGE (f:PhonemeFeature {Name: row.Name});

// MorphoSyntax
LOAD CSV WITH HEADERS FROM "file:///Users/niluje/Dev/TAL-S1-BDD/data/MorphoSyntax.csv" AS row
MATCH (l:LangInfo {Name: row.LangID})
SET
	l.WordOrder = row.WordOrder,
	l.PluralCount = toInteger(row.PluralCount),
	l.CaseCount = toInteger(row.CaseCount),
	l.AdjectiveBeforeNoun = toBoolean(toInteger(row.AdjectiveBeforeNoun)),
	l.AdjectiveAfterNoun = toBoolean(toInteger(row.AdjectiveAfterNoun)),
	l.AdjectiveAgreement = toBoolean(toInteger(row.AdjectiveAgreement))

// Lexicon
CREATE CONSTRAINT Lexicon_Native_Word IF NOT EXISTS
FOR (nw:Native_Word) REQUIRE nw.Word IS UNIQUE;
CREATE CONSTRAINT Lexicon_EN_Word IF NOT EXISTS
FOR (enw:EN_Word) REQUIRE enw.Word IS UNIQUE;
CREATE CONSTRAINT Lexicon_FR_Word IF NOT EXISTS
FOR (frw:FR_Word) REQUIRE frw.Word IS UNIQUE;
CREATE CONSTRAINT Lexicon_IPA_Word IF NOT EXISTS
FOR (ipaw:IPA_Word) REQUIRE ipaw.Transcription IS UNIQUE;

LOAD CSV WITH HEADERS FROM "file:///Users/niluje/Dev/TAL-S1-BDD/data/Lexicon.csv" AS row
MERGE (nw:Native_Word {Word: row.Native_Word})
MERGE (enw:EN_Word {Word: row.EN_Word})
MERGE (frw:FR_Word {Word: row.FR_Word})
MERGE (ipaw:IPA_Word {Transcription: COALESCE(row.IPA_Word, "N/A")})

WITH row, nw, enw, frw, ipaw
MATCH (l:LangInfo {Name: row.LangID})

MERGE (l)-[r:HAS_WORD]->(nw)
SET r.type = "Lexicon"
MERGE (nw)-[r2:IN_EN]->(enw)
SET r2.type = "Lexicon"
MERGE (nw)-[r3:IN_FR]->(frw)
SET r3.type = "Lexicon"
MERGE (nw)-[r4:IN_IPA]->(ipaw)
SET r4.type = "Lexicon";

// Prosody
CREATE CONSTRAINT Prosody_PhonemicStress IF NOT EXISTS
FOR (ps:PhonemicStress) REQUIRE ps.Value IS UNIQUE;
CREATE CONSTRAINT Prosody_SyllableWeightStress IF NOT EXISTS
FOR (sws:SyllableWeightStress) REQUIRE sws.Value IS UNIQUE;

LOAD CSV WITH HEADERS FROM "file:///Users/niluje/Dev/TAL-S1-BDD/data/Prosody.csv" AS row
MERGE (ps:PhonemicStress {Value: toBoolean(toInteger(row.PhonemicStress))})
MERGE (sws:SyllableWeightStress {Value: toBoolean(toInteger(row.SyllableWeightStress))})

WITH row, ps, sws
MATCH (l:LangInfo {Name: row.LangID})

MERGE (l)-[r:PHONEMIC_STRESS]->(ps)
SET r.type = "Prosody"
MERGE (l)-[r2:SYLLABLE_WEIGHT_STRESS]->(sws)
SET r2.type = "Prosody";

// Inspiration
CREATE CONSTRAINT Inspiration_NaturalLanguage IF NOT EXISTS
FOR (nl:NaturalLanguage) REQUIRE nl.Name IS UNIQUE;
CREATE CONSTRAINT Inspiration_ProsodyFeature IF NOT EXISTS
FOR (pf:ProsodyFeature) REQUIRE pf.Name IS UNIQUE;
CREATE CONSTRAINT Inspiration_MorphoSyntaxFeature IF NOT EXISTS
FOR (msf:MorphoSyntaxFeature) REQUIRE msf.Name IS UNIQUE;

LOAD CSV WITH HEADERS FROM "file:///Users/niluje/Dev/TAL-S1-BDD/data/Inspiration.csv" AS row
MERGE (nl:NaturalLanguage {Name: row.NaturalLanguage})
MERGE (pf:ProsodyFeature {Name: COALESCE(row.ProsodyFeature, "N/A")})
MERGE (msf:MorphoSyntaxFeature {Name: COALESCE(row.MorphoSyntaxFeature, "N/A")})
WITH row, nl, pf, msf
MATCH (l:LangInfo {Name: row.LangID})

MERGE (l)-[r:INSPIRED_BY]->(nl)
SET r.type = "Inspiration"
MERGE (nl)-[r2:PROSODY_FEATURE]->(pf)
SET r2.type = "Inspiration"
MERGE (nl)-[r3:MORPHOSYNTAX_FEATURE]->(msf)
SET r3.type = "Inspiration";

LOAD CSV WITH HEADERS FROM "file:///Users/niluje/Dev/TAL-S1-BDD/data/Inspiration.csv" AS row
MATCH (l:LangInfo {Name: row.LangID})
MATCH (nl:NaturalLanguage {Name: row.NaturalLanguage})
MATCH (phf:PhonemeFeature {Name: row.PhonologyFeature})

MERGE (nl)-[r:PHONOLOGY_FEATURE]->(phf)
SET r.type = "Inspiration";

// PhonemeBank
CREATE CONSTRAINT PhonemeBank_IPA IF NOT EXISTS
FOR (p:Phoneme) REQUIRE p.IPA IS UNIQUE;

LOAD CSV WITH HEADERS FROM "file:///Users/niluje/Dev/TAL-S1-BDD/data/PhonemeBank-Exported.csv" AS row
MERGE (p:Phoneme {IPA: row.IPA, Type: row.Type, Modifiers: row.Modifiers})

LOAD CSV WITH HEADERS FROM "file:///Users/niluje/Dev/TAL-S1-BDD/data/PhonemeBank-Exported.csv" AS row
MATCH (p:Phoneme {IPA: row.IPA})
MATCH (f:PhonemeFeature {Name: row.Feature})

MERGE (p)-[r:PHONEME_FEATURE]->(f)
SET r.type = "Phoneme";

LOAD CSV WITH HEADERS FROM "file:///Users/niluje/Dev/TAL-S1-BDD/data/PhonemeBank-Exported.csv" AS row
MATCH (p:Phoneme {IPA: row.IPA, Type: "Vowel"})
SET
	p.Vowel_Height = row.Vowel_Height,
	p.Vowel_Backness = row.Vowel_Backness,
	p.Vowel_Roundness = row.Vowel_Roundness

LOAD CSV WITH HEADERS FROM "file:///Users/niluje/Dev/TAL-S1-BDD/data/PhonemeBank-Exported.csv" AS row
MATCH (p:Phoneme {IPA: row.IPA, Type: "Consonnant"})
SET
	p.Consonant_Voicing = toBoolean(row.Consonant_Voicing),
	p.Consonant_ArticulationManner = row.Consonant_ArticulationManner,
	p.Consonant_ArticulationPlace = row.Consonant_ArticulationPlace

// Phonology
LOAD CSV WITH HEADERS FROM "file:///Users/niluje/Dev/TAL-S1-BDD/data/Phonology.csv" AS row
MATCH (l:LangInfo {Name: row.LangID})
MATCH (p:Phoneme {IPA: row.PhonemeID})

MERGE (l)-[r:HAS_PHONEME]->(p)
SET r.type = "Phonology";

/*
* Queries
*/

// Phonemes used in SVO Langs:
MATCH (l:LangInfo {WordOrder: "SVO"})-[:HAS_PHONEME]->(p:Phoneme)
RETURN l, p;

// Phoneme Features comparison
MATCH (l:LangInfo)-[:HAS_PHONEME]->(p:Phoneme)-[:PHONEME_FEATURE]->(f:PhonemeFeature)
RETURN l, p, f;

// Compare MorphoSyntax feats for Langs w/ Diphthongs
MATCH (l:LangInfo)-[:HAS_PHONEME]->(p:Phoneme)-[:PHONEME_FEATURE]->(pf:PhonemeFeature {Name: "Diphthong"})
RETURN l.WordOrder, p, l.CaseCount, p;

// Count Vowels
MATCH (l:LangInfo)-[r:HAS_PHONEME]->(p:Phoneme {Type: "Vowel"})
WITH l AS Lang, collect(p) as Phonemes, count(p) AS Vowels
RETURN Lang, Phonemes, Vowels;

// Match shared phonemes
MATCH (l1:LangInfo)-[r1:HAS_PHONEME]->(p:Phoneme)<-[r2:HAS_PHONEME]-(l2:LangInfo)
RETURN l1, l2, p;

// Lookup fire & co
MATCH (w:EN_Word {Word: "fire"})<-[:IN_EN]-(n)<-[:HAS_WORD]-(l), (n)-[:IN_IPA]->(i)
RETURN w, n, i, l;

MATCH (w:EN_Word)<-[:IN_EN]-(n)<-[:HAS_WORD]-(l),
      (n)-[:IN_IPA]->(i)
WHERE w.Word IN ["fire", "greetings"]
RETURN w, n, i, l;

// Match Phonemes w/ rels
MATCH (x)--(p:Phoneme)--(y)
RETURN x, p, y;
