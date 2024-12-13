#!/usr/bin/env python3

import os
from neo4j import GraphDatabase

URI = "neo4j://localhost"
AUTH = ("neo4j", os.getenv("NEO4J_PASS"))

# Drop all the things!
#MATCH (n) DETACH DELETE n;
# (Print query to) drop all constraints
#SHOW CONSTRAINTS yield name RETURN "DROP CONSTRAINT " + name + ";";

def main():
	with GraphDatabase.driver(URI, auth=AUTH) as driver:
		with driver.session(database="conlangs") as session:
			res = session.execute_read(count_vowels_tx)
			print(f"{res}")

def count_vowels_tx(tx):
	result = tx.run("""
		MATCH (l:LangInfo)-[r:HAS_PHONEME]->(p:Phoneme {Type: "Vowel"})
		WITH l AS Lang, collect(p) as Phonemes, count(p) AS Vowels
		RETURN Lang, Phonemes, Vowels;
	""")
	for row in result:
		print(row.data())

if __name__ == "__main__":
	main()
