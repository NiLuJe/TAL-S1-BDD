#!/usr/bin/env python3

import os
from neo4j import GraphDatabase

URI = "neo4j://localhost"
AUTH = ("neo4j", os.getenv("NEO4J_PASS"))

# Drop all the things!
#MATCH (n) DETACH DELETE n;
# (Print query to) drop all constraints
#SHOW CONSTRAINTS yield name RETURN "DROP CONSTRAINT " + name + ";";

##
## Nodes & Relationships
##

# LangInfo
"""
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
"""

# PhonemeFeature
"""
CREATE CONSTRAINT PhonemeFeature_Name IF NOT EXISTS
FOR (pf:PhonemeFeature) REQUIRE pf.Name IS UNIQUE;

LOAD CSV WITH HEADERS FROM "file:///Users/niluje/Dev/TAL-S1-BDD/data/PhonemeFeature.csv" AS row
MERGE (f:PhonemeFeature {Name: row.Name});
"""

# MorphoSyntax
"""
CREATE CONSTRAINT MorphoSyntax_WordOrder IF NOT EXISTS
FOR (wo:WordOrder) REQUIRE wo.Order IS UNIQUE;
CREATE CONSTRAINT MorphoSyntax_PluralCount IF NOT EXISTS
FOR (pc:PluralCount) REQUIRE pc.Count IS UNIQUE;
CREATE CONSTRAINT MorphoSyntax_CaseCount IF NOT EXISTS
FOR (cc:CaseCount) REQUIRE cc.Count IS UNIQUE;
CREATE CONSTRAINT MorphoSyntax_AdjectiveBeforeNoun IF NOT EXISTS
FOR (abn:AdjectiveBeforeNoun) REQUIRE abn.Value IS UNIQUE;
CREATE CONSTRAINT MorphoSyntax_AdjectiveAfterNoun IF NOT EXISTS
FOR (aan:AdjectiveAfterNoun) REQUIRE aan.Value IS UNIQUE;
CREATE CONSTRAINT MorphoSyntax_AdjectiveAgreement IF NOT EXISTS
FOR (aa:AdjectiveAgreement) REQUIRE aa.Value IS UNIQUE;

LOAD CSV WITH HEADERS FROM "file:///Users/niluje/Dev/TAL-S1-BDD/data/MorphoSyntax.csv" AS row
MERGE (wo:WordOrder {Order: row.WordOrder})
MERGE (pc:PluralCount {Count: toInteger(row.PluralCount)})
MERGE (cc:CaseCount {Count: toInteger(row.CaseCount)})
MERGE (abn:AdjectiveBeforeNoun {Value: toBoolean(toInteger(row.AdjectiveBeforeNoun))})
MERGE (aan:AdjectiveAfterNoun {Value: toBoolean(toInteger(row.AdjectiveAfterNoun))})
MERGE (aa:AdjectiveAgreement {Value: toBoolean(toInteger(row.AdjectiveAgreement))})
WITH row, wo, pc, cc, abn, aan, aa
MATCH (l:LangInfo {Name: row.LangID})

MERGE (l)-[r:WORD_ORDER]->(wo)
SET r.type = "MorphoSyntax"
MERGE (l)-[r2:PLURAL_COUNT]->(pc)
SET r2.type = "MorphoSyntax"
MERGE (l)-[r3:CASE_COUNT]->(cc)
SET r3.type = "MorphoSyntax"
MERGE (l)-[r4:ADJ_BEFORE_NOUN]->(abn)
SET r4.type = "MorphoSyntax"
MERGE (l)-[r5:ADJ_AFTER_NOUN]->(aan)
SET r5.type = "MorphoSyntax"
MERGE (l)-[r6:ADJ_AGREEMENT]->(aa)
SET r6.type = "MorphoSyntax";
"""

# Lexicon
"""
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
"""

# Prosody
"""
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
"""

# Inspiration
"""
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
"""

# PhonemeBank
"""
CREATE CONSTRAINT PhonemeBank_IPA IF NOT EXISTS
FOR (p:Phoneme) REQUIRE p.IPA IS UNIQUE;
CREATE CONSTRAINT PhonemeBank_Type IF NOT EXISTS
FOR (t:PhonemeType) REQUIRE t.Type IS UNIQUE;
CREATE CONSTRAINT PhonemeBank_Vowel_Height IF NOT EXISTS
FOR (vh:Vowel_Height) REQUIRE vh.Description IS UNIQUE;
CREATE CONSTRAINT PhonemeBank_Vowel_Backness IF NOT EXISTS
FOR (vb:Vowel_Backness) REQUIRE vb.Description IS UNIQUE;
CREATE CONSTRAINT PhonemeBank_Vowel_Roundness IF NOT EXISTS
FOR (vr:Vowel_Roundness) REQUIRE vr.Description IS UNIQUE;
CREATE CONSTRAINT PhonemeBank_Consonant_Voicing IF NOT EXISTS
FOR (cv:Consonant_Voicing) REQUIRE cv.Value IS UNIQUE;
CREATE CONSTRAINT PhonemeBank_Consonant_ArticulationManner IF NOT EXISTS
FOR (cam:Consonant_ArticulationManner) REQUIRE cam.Description IS UNIQUE;
CREATE CONSTRAINT PhonemeBank_Consonant_ArticulationPlace IF NOT EXISTS
FOR (cap:Consonant_ArticulationPlace) REQUIRE cap.Description IS UNIQUE;
CREATE CONSTRAINT PhonemeBank_Modifiers IF NOT EXISTS
FOR (m:Modifiers) REQUIRE m.Description IS UNIQUE;

LOAD CSV WITH HEADERS FROM "file:///Users/niluje/Dev/TAL-S1-BDD/data/PhonemeBank.csv" AS row
MERGE (p:Phoneme {IPA: row.IPA})
MERGE (t:PhonemeType {Type: row.Type})
MERGE (vh:Vowel_Height {Description: COALESCE(row.Vowel_Height, "N/A")})
MERGE (vb:Vowel_Backness {Description: COALESCE(row.Vowel_Backness, "N/A")})
MERGE (vr:Vowel_Roundness {Description: COALESCE(row.Vowel_Roundness, "N/A")})
MERGE (cv:Consonant_Voicing {Value: COALESCE(toBooleanOrNull(toInteger(row.Consonant_Voicing)), "N/A")})
MERGE (cam:Consonant_ArticulationManner {Description: COALESCE(row.Consonant_ArticulationManner, "N/A")})
MERGE (cap:Consonant_ArticulationPlace {Description: COALESCE(row.Consonant_ArticulationPlace, "N/A")})
MERGE (m:Modifiers {Description: COALESCE(row.Modifiers, "N/A")})

WITH row, p, t, vh, vb, vr, cv, cam, cap, m
MERGE (p)-[r:PHONEME_TYPE]->(t)
SET r.type = "Phoneme"
MERGE (p)-[r2:VOWEL_HEIGHT]->(vh)
SET r2.type = "Phoneme"
MERGE (p)-[r3:VOWEL_BACKNESS]->(vb)
SET r3.type = "Phoneme"
MERGE (p)-[r4:VOWEL_ROUNDNESS]->(vr)
SET r4.type = "Phoneme"
MERGE (p)-[r5:CONSONNANT_VOICING]->(cv)
SET r5.type = "Phoneme"
MERGE (p)-[r6:CONSONNANT_ARTICULATION_MANNER]->(cam)
SET r6.type = "Phoneme"
MERGE (p)-[r7:CONSONNANT_ARTICULATION_PLACE]->(cap)
SET r7.type = "Phoneme"
MERGE (p)-[r8:PHONEME_MODIFIERS]->(m)
SET r8.type = "Phoneme";

LOAD CSV WITH HEADERS FROM "file:///Users/niluje/Dev/TAL-S1-BDD/data/PhonemeBank.csv" AS row
MATCH (p:Phoneme {IPA: row.IPA})
MATCH (f:PhonemeFeature {Name: row.Feature})

MERGE (p)-[r:PHONEME_FEATURE]->(f)
SET r.type = "Phoneme";

LOAD CSV WITH HEADERS FROM "file:///Users/niluje/Dev/TAL-S1-BDD/data/PhonemeBank.csv" AS row
MATCH (p:Phoneme {IPA: row.IPA})
MATCH (t:PhonemeType {Type: row.Type})
SET p.Type = t.Type;

# Or:
#MATCH (p:Phoneme)-[:PHONEME_TYPE]->(pt:PhonemeType {Type: "Vowel"})
#SET p.Type = pt.Type;
"""

# Phonology
"""
LOAD CSV WITH HEADERS FROM "file:///Users/niluje/Dev/TAL-S1-BDD/data/Phonology.csv" AS row
MATCH (l:LangInfo {Name: row.LangID})
MATCH (p:Phoneme {IPA: row.PhonemeID})

MERGE (l)-[r:HAS_PHONEME]->(p)
SET r.type = "Phonology";
"""

##
## Queries
##

# Phonemes used in SVO Langs:
"""
MATCH (l:LangInfo)-[:HAS_PHONEME]->(p:Phoneme),
      (l)-[:WORD_ORDER]->(wo:WordOrder {Order: "SVO"})
RETURN l, p;
"""

# Phoneme Features comparison
"""
MATCH (l:LangInfo)-[:HAS_PHONEME]->(p:Phoneme)-[:PHONEME_FEATURE]->(f:PhonemeFeature)
RETURN l, p, f;
"""

# Compare MorphoSyntax feats for Langs w/ Diphthongs
"""
MATCH (l:LangInfo)-[:HAS_PHONEME]->(p:Phoneme)-[:PHONEME_FEATURE]->(pf:PhonemeFeature {Name: "Diphthong"})
MATCH (l)-[:WORD_ORDER]->(wo:WordOrder)
MATCH (l)-[:CASE_COUNT]->(cc:CaseCount)
RETURN l, p, wo, cc;
"""

# Count Vowels:
"""
MATCH (l:LangInfo)-[r:HAS_PHONEME]->(p:Phoneme)-[:PHONEME_TYPE]->(pt:PhonemeType {Type: "Vowel"})
WITH l AS Lang, collect(p) as Phonemes, count(p) AS Vowels
RETURN Lang, Phonemes, Vowels;

MATCH (l:LangInfo)-[r:HAS_PHONEME]->(p:Phoneme {Type: "Vowel"})
WITH l AS Lang, collect(p) as Phonemes, count(p) AS Vowels
RETURN Lang, Phonemes, Vowels;
"""

# Lookup fire
"""
MATCH (w:EN_Word {Word: "fire"})<-[:IN_EN]-(n)<-[:HAS_WORD]-(l), (n)-[:IN_IPA]->(i)
RETURN w, n, i, l;

MATCH (w:EN_Word)<-[:IN_EN]-(n)<-[:HAS_WORD]-(l),
      (n)-[:IN_IPA]->(i)
WHERE w.Word IN ["fire", "greetings"]
RETURN w, n, i, l;
"""

# Match shared phonemes
"""
MATCH (l1:LangInfo)-[r1:HAS_PHONEME]->(p:Phoneme)<-[r2:HAS_PHONEME]-(l2:LangInfo)
RETURN l1, l2, p;
"""

def main():
	with GraphDatabase.driver(URI, auth=AUTH) as driver:
		with driver.session(database="conlangs") as session:
			for i in range(100):
				name = f"Thor{i}"
				org_id = session.execute_write(employ_person_tx, name)
				print(f"User {name} added to organization {org_id}")


def employ_person_tx(tx, name):
	# Create new Person node with given name, if not exists already
	result = tx.run("""
		MERGE (p:Person {name: $name})
		RETURN p.name AS name
		""", name=name
	)

	# Obtain most recent organization ID and the number of people linked to it
	result = tx.run("""
		MATCH (o:Organization)
		RETURN o.id AS id, COUNT{(p:Person)-[r:WORKS_FOR]->(o)} AS employees_n
		ORDER BY o.created_date DESC
		LIMIT 1
	""")
	org = result.single()

	if org is not None and org["employees_n"] == 0:
		raise Exception("Most recent organization is empty.")
		# Transaction will roll back -> not even Person is created!

	# If org does not have too many employees, add this Person to that
	if org is not None and org.get("employees_n") < 10:
		result = tx.run("""
			MATCH (o:Organization {id: $org_id})
			MATCH (p:Person {name: $name})
			MERGE (p)-[r:WORKS_FOR]->(o)
			RETURN $org_id AS id
			""", org_id=org["id"], name=name
		)

	# Otherwise, create a new Organization and link Person to it
	else:
		result = tx.run("""
			MATCH (p:Person {name: $name})
			CREATE (o:Organization {id: randomuuid(), created_date: datetime()})
			MERGE (p)-[r:WORKS_FOR]->(o)
			RETURN o.id AS id
			""", name=name
		)

	# Return the Organization ID to which the new Person ends up in
	return result.single()["id"]


if __name__ == "__main__":
	main()
