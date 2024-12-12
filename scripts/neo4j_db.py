#!/usr/bin/env python3

import os
from neo4j import GraphDatabase

URI = "neo4j://localhost"
AUTH = ("neo4j", os.getenv("NEO4J_PASS"))


#MATCH (n) DETACH DELETE n;
#SHOW CONSTRAINTS yield name RETURN "DROP CONSTRAINT " + name + ";";

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
