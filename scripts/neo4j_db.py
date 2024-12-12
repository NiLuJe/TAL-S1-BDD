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
FOR (wo:WordOrder) REQUIRE ms.Order IS UNIQUE;
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
MERGE (abn:AdjectiveBeforeNoun {Value: toBoolean(row.AdjectiveBeforeNoun)})
MERGE (aan:AdjectiveAfterNoun {Value: toBoolean(row.AdjectiveAfterNoun)})
MERGE (aa:AdjectiveAgreement {Value: toBoolean(row.AdjectiveAgreement)})

MATCH (l:LangInfo {Name: row.LangID})
MATCH (wo:WordOrder {Order: row.WordOrder})
MATCH (pc:PluralCount {Count: toInteger(row.PluralCount)})
MATCH (cc:CaseCount {Count: toInteger(row.CaseCount)})
MATCH (abn:AdjectiveBeforeNoun {Value: toBoolean(row.AdjectiveBeforeNoun)})
MATCH (aan:AdjectiveAfterNoun {Value: toBoolean(row.AdjectiveAfterNoun)})
MATCH (aa:AdjectiveAgreement {Value: toBoolean(row.AdjectiveAgreement)})
MERGE (l)-[r:WORD_ORDER]->(wo)
SET r.type = "MorphoSyntax"
MERGE (l)-[r:PLURAL_COUNT]->(pc)
SET r.type = "MorphoSyntax"
MERGE (l)-[r:CASE_COUNT]->(cc)
SET r.type = "MorphoSyntax"
MERGE (l)-[r:ADJ_BEFORE_NOUN]->(abn)
SET r.type = "MorphoSyntax"
MERGE (l)-[r:ADJ_AFTER_NOUN]->(aan)
SET r.type = "MorphoSyntax"
MERGE (l)-[r:ADJ_AGREEMENT]->(aa)
SET r.type = "MorphoSyntax";
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
