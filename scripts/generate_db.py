#!/usr/bin/env python3

# See also: gruut-ipa, ipasymbols, and, most importantly: panphon
import csv
import ipapy
import os
from pathlib import Path
import sqlite3

# Path shenanigans, relative to this script
BASE_DIR = Path(__file__).parent.parent.resolve()
DB_PATH = Path(BASE_DIR / "DB" / "conlangs.db")
DATA_PATH = Path(BASE_DIR / "data")
SCHEMA_PATH = Path(DATA_PATH / "conlangs_schema.sql")

def create_db(path: str|Path):
	"""Import bare SQL schema into a brand new DB"""
	con = sqlite3.connect(path, autocommit=False)

	with open(SCHEMA_PATH) as f:
		try:
			with con:
				con.executescript(f.read())
		except sqlite3.IntegrityError as e:
				print(f"IntegrityError: {e}")

	con.close()
	print("Database created successfully!")

def generate_ipa_bank(path: str|Path):
	"""Insert IPA phones (from ipapy) into the PhonemeBank table"""
	con = sqlite3.connect(path, autocommit=False)

	try:
		with con:
			for p in ipapy.IPA_CHARS:
				if p.is_vowel:
					if p.modifiers:
						modifs = " ".join(p.modifiers)
					else:
						modifs = None
					data = (str(p), "Vowel", p.height, p.backness, p.roundness, modifs)
					con.execute("INSERT INTO PhonemeBank(IPA, Type, Vowel_Height, Vowel_Backness, Vowel_Roundness, Modifiers) VALUES(?, ?, ?, ?, ?, ?)", data)
				elif p.is_consonant:
					if p.modifiers:
						modifs = " ".join(p.modifiers)
					else:
						modifs = None
					data = (str(p), "Consonant", 1 if p.voicing == "voiced" else 0, p.manner, p.place, modifs)
					con.execute("INSERT INTO PhonemeBank(IPA, Type, Consonant_Voicing, Consonant_ArticulationManner, Consonant_ArticulationPlace, Modifiers) VALUES(?, ?, ?, ?, ?, ?)", data)
				elif p.is_diacritic:
					data = (str(p), "Diacritic", p.name.replace(" diacritic", ""))
					con.execute("INSERT INTO PhonemeBank(IPA, Type, Modifiers) VALUES(?, ?, ?)", data)
				elif p.is_suprasegmental:
					data = (str(p), "Suprasegmental", p.name.replace(" suprasegmental", ""))
					con.execute("INSERT INTO PhonemeBank(IPA, Type, Modifiers) VALUES(?, ?, ?)", data)
				elif p.is_tone:
					data = (str(p), "Tone", p.name.replace(" tone", ""))
					con.execute("INSERT INTO PhonemeBank(IPA, Type, Modifiers) VALUES(?, ?, ?)", data)
	except sqlite3.IntegrityError as e:
			print(f"IntegrityError: {e}")

	con.close()
	print("Inserted phone data successfully!")

def insert_data(path: str|Path):
	"""Import data from CSV files into the DB"""
	con = sqlite3.connect(path, autocommit=False)
	con.row_factory = sqlite3.Row

	# Get table names... but we need LangInfo & PhonemeFeature to be handled first, because they host parent keys.
	tables = [ "LangInfo", "PhonemeFeature" ]
	try:
		with con:
			for row in con.execute("SELECT name FROM sqlite_master WHERE type = ? ORDER BY name ASC", ("table", )):
				tables.append(row["name"])
	except sqlite3.IntegrityError as e:
			print(f"IntegrityError: {e}")
	# Dedupe while keeping insertion order (no OrderedSet, so we rely on dicts retainign insertion order instead)...
	tables = list(dict.fromkeys(tables))

	# Keep a cache of LangID mappings
	langs = {}

	for table in tables:
		csv_file = Path(DATA_PATH / table ).with_suffix(".csv")

		if not os.access(csv_file, os.R_OK):
			print(f"No data for table {table}")
			continue

		print(f"Importing data from {csv_file}...")
		with open(csv_file, newline = "") as f:
			# Auto-detect CSV dialect
			dialect = csv.Sniffer().sniff(f.read(1024))
			f.seek(0)

			reader = csv.DictReader(f, dialect = dialect)
			for row in reader:
				cols = list(row.keys())
				vals = list(row.values())
				# FIXME: PhonemeID lookup
				match table:
					case "LangInfo":
						# Drop LangInfo, it's the primary key, and as such, empty in our data
						langidx = cols.index("LangID")
						del(cols[langidx])
						del(vals[langidx])
					case _:
						# Lookup LangID, as we use the name in our data to make data entry easier
						langname = row["LangID"]
						langid = langs.get(langname)
						if not langid:
							print(f"Looking up LangID for {langname}... ", end = "")
							data = (langname, )
							res = con.execute("SELECT LangID FROM LangInfo WHERE LangName = ?", data)
							row = res.fetchone()
							langid = row["LangID"]
						# Replace the lang name by its id
						langidx = cols.index("LangID")
						vals[langidx] = langid
						# Cache it
						langs[langname] = langid
						# Log it
						print(langid)

				# Formatting for the prepared statement (column list)...
				c = ", ".join(cols)
				# Repeat comma-separated ? for as many columns as we have...
				l = ["?" for i in range(len(vals))]
				v = ", ".join(l)

				query = f"INSERT INTO {table}({c}) VALUES({v})"
				data = tuple(vals)
				# Print the query for debugging purposes...
				print(query)
				print(data)

				try:
					with con:
						con.execute(query, data)
				except sqlite3.IntegrityError as e:
						print(f"IntegrityError: {e}")

	con.close()
	print("Inserted data successfully!")

def main():
	while True:
		action = input("[C]reate • [P]honeme • [I]nsert >>> ")
		match action.strip().upper():
			case "C":
				create_db(DB_PATH)
			case "P":
				generate_ipa_bank(DB_PATH)
			case "I":
				insert_data(DB_PATH)
			case "":
				break
			case _:
				print("Unsupported action")

# Only run when called as a script, not an import
if __name__ == "__main__":
	main()
