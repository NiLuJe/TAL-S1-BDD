#!/usr/bin/env python3

import csv
# See also: gruut-ipa, ipasymbols, and, most importantly: panphon
import ipapy
import os
from pathlib import Path
import sqlite3
import unicodedata

# Path shenanigans, relative to this script
BASE_DIR = Path(__file__).parent.parent.resolve()
DB_PATH = Path(BASE_DIR / "DB" / "conlangs.db")
DATA_PATH = Path(BASE_DIR / "data")
SCHEMA_PATH = Path(DATA_PATH / "conlangs_schema.sql")

# Keep a cache of foreign key mappings
MAP_LANGS = {}
MAP_PHONEMES = {}
MAP_FEATURES = {}

def create_db(path: str | Path):
	"""Import bare SQL schema into a brand new DB"""
	con = sqlite3.connect(path, autocommit = False)

	with open(SCHEMA_PATH) as f:
		try:
			with con:
				con.executescript(f.read())
		except sqlite3.IntegrityError as e:
				print(f"!! IntegrityError: {e}")

	con.close()
	print("Database created successfully!")

def generate_ipa_bank(path: str | Path):
	"""Insert IPA phones (from ipapy) into the PhonemeBank table"""
	con = sqlite3.connect(path, autocommit = False)
	con.row_factory = sqlite3.Row

	try:
		with con:
			for p in ipapy.IPA_CHARS:
				if p.is_vowel:
					if p.modifiers:
						modifs = " ".join(p.modifiers)
					else:
						modifs = None
					# Use the backness as the feature
					feat = lookup_or_insert_feat(con, p.backness.title().replace("-", ""))
					data = (str(p), "Vowel", p.height, p.backness, p.roundness, modifs, feat)
					print(data)
					con.execute("INSERT INTO PhonemeBank(IPA, Type, Vowel_Height, Vowel_Backness, Vowel_Roundness, Modifiers, Feature) VALUES(?, ?, ?, ?, ?, ?, ?)", data)
				elif p.is_consonant:
					if p.modifiers:
						modifs = " ".join(p.modifiers)
					else:
						modifs = None
					# NOTE: We extract a coarser feature marker for simplicity's sake.
					#       The last element of the articulation manner is usually a fine choice,
					#       except for ejectives, which isn't the final element, but which we do want to keep separate...
					manners = p.manner.split("-")
					try:
						ejective = manners.index("ejective")
						feat = lookup_or_insert_feat(con, manners[ejective].title())
					except ValueError:
						feat = lookup_or_insert_feat(con, manners[-1].title())
					data = (str(p), "Consonant", 1 if p.voicing == "voiced" else 0, p.manner, p.place, modifs, feat)
					print(data)
					con.execute("INSERT INTO PhonemeBank(IPA, Type, Consonant_Voicing, Consonant_ArticulationManner, Consonant_ArticulationPlace, Modifiers, Feature) VALUES(?, ?, ?, ?, ?, ?, ?)", data)
				elif p.is_diacritic:
					modifs = p.name.replace(" diacritic", "")
					# Use the modifiers as the feature
					feat = lookup_or_insert_feat(con, modifs.title().replace("-", ""))
					data = (str(p), "Diacritic", modifs, feat)
					print(data)
					con.execute("INSERT INTO PhonemeBank(IPA, Type, Modifiers, Feature) VALUES(?, ?, ?, ?)", data)
				elif p.is_suprasegmental:
					modifs = p.name.replace(" suprasegmental", "")
					# Use the modifiers as the feature
					feat = lookup_or_insert_feat(con, modifs.title().replace("-", ""))
					data = (str(p), "Suprasegmental", modifs, feat)
					print(data)
					con.execute("INSERT INTO PhonemeBank(IPA, Type, Modifiers, Feature) VALUES(?, ?, ?, ?)", data)
				elif p.is_tone:
					modifs = p.name.replace(" tone", "")
					# Use the modifiers as the feature
					feat = lookup_or_insert_feat(con, modifs.title().replace("-", ""))
					data = (str(p), "Tone", modifs, feat)
					print(data)
					con.execute("INSERT INTO PhonemeBank(IPA, Type, Modifiers, Feature) VALUES(?, ?, ?, ?)", data)
	except sqlite3.IntegrityError as e:
			print(f"!! IntegrityError: {e}")

	con.close()
	print("Inserted phone data successfully!")

def lookup_lang_id(con: sqlite3.Connection, lang_name: str) -> int:
	"""Lookup the LangID of a given lang"""
	lang_id = MAP_LANGS.get(lang_name)
	if lang_id:
		# Cache hit
		return lang_id

	print(f"Looking up LangID for {lang_name}... ", end = "")
	try:
		with con:
			data = (lang_name, )
			res = con.execute("SELECT LangID FROM LangInfo WHERE LangName = ?", data)
			row = res.fetchone()
			lang_id = row["LangID"]
			# Log it
			print(lang_id)
			# Cache it
			MAP_LANGS[lang_name] = lang_id
			return lang_id
	except sqlite3.IntegrityError as e:
			print(f"!! IntegrityError: {e}")

	print()
	raise ValueError(f"Unknown language {lang_name}!")

def lookup_feat_id(con: sqlite3.Connection, feature_name: str) -> int | None:
	"""Lookup the ID of a given PhonemeFeature"""
	# NOTE: PhonemeFeature can be NULL (i.e., the empty string in the CSV data)...
	if not feature_name:
		return None

	feature_id = MAP_FEATURES.get(feature_name)
	if feature_id:
		# Cache hit
		return feature_id

	print(f"Looking up PhonemeFeature for {feature_name}... ", end = "")
	try:
		with con:
			data = (feature_name, )
			res = con.execute("SELECT ID FROM PhonemeFeature WHERE Name = ?", data)
			row = res.fetchone()
			if row:
				feature_id = row["ID"]
			else:
				feature_id = None
			# Log it
			print(feature_id )
			# Cache it
			MAP_FEATURES[feature_name] = feature_id
			return feature_id
	except sqlite3.IntegrityError as e:
			print(f"!! IntegrityError: {e}")

	print()
	raise ValueError(f"Unknown feature {feature_name}!")

def insert_feat(con: sqlite3.Connection, feature_name: str) -> None:
	"""Insert a new PhonemeFeature"""
	print(f"Inserting PhonemeFeature {feature_name}... ", end = "")
	try:
		with con:
			data = (feature_name, )
			con.execute("INSERT INTO PhonemeFeature(Name) VALUES(?)", data)
	except sqlite3.IntegrityError as e:
			print(f"!! IntegrityError: {e}")

	print()

def lookup_or_insert_feat(con: sqlite3.Connection, feature_name: str) -> int | None:
	feat_id = lookup_feat_id(con, feature_name)
	if feat_id is None:
		insert_feat(con, feature_name)
		return lookup_feat_id(con, feature_name)
	return feat_id

def lookup_phoneme_id(con: sqlite3.Connection, phoneme: str) -> int:
	"""Lookup the PhonemeID of a given IPA string"""

	phoneme_id = MAP_PHONEMES.get(phoneme)
	if phoneme_id:
		# Cache hit
		return phoneme_id

	print(f"Looking up PhonemeID for {phoneme}... ")
	try:
		with con:
			data = (phoneme, )
			res = con.execute("SELECT PhonemeID FROM PhonemeBank WHERE IPA = ?", data)
			row = res.fetchone()
			if row is None:
				# Fallback values for the new phoneme row
				right_row = { "Type": "Unknown", "Modifiers": None, "Feature": None }
				left_row = { "Type": "Unknown", "Modifiers": None, "Feature": None }
				type = "Unknown"
				modifier = None
				feature = None

				# Grok the feature automagically
				# NOTE: Decompose to NFD to be able to lookup diacritics on their own...
				nfd_phoneme = unicodedata.normalize("NFD", phoneme)
				# NOTE: we'll mostly assume diphones here, or phone + diacritic pairs
				if len(nfd_phoneme) > 1:
					# Try for trailing diacritics first
					diacritic = nfd_phoneme[-1]
					data = (diacritic, )
					print(f"Looking up right {diacritic}...")
					res = con.execute("SELECT PhonemeID, Type, Modifiers, Feature FROM PhonemeBank WHERE IPA = ?", data)
					row = res.fetchone()
					if row:
						right_row = dict(row)
						print(f"right_row: {right_row}")

						phone = nfd_phoneme[-2]
						data = (phone, )
						print(f"Looking up left {phone}...")
						res = con.execute("SELECT PhonemeID, Type, Modifiers, Feature FROM PhonemeBank WHERE IPA = ?", data)
						row = res.fetchone()
						if row:
							left_row = dict(row)
							print(f"left_row: {left_row}")

					# Crappy heuristics...
					match right_row["Type"]:
						case "Tone" | "Suprasegmental" | "Diacritic":
							# Inherit the diacritic's modifiers & feature
							modifier = right_row["Modifiers"]
							feature = right_row["Feature"]
							# Inherit the phone's type
							type = left_row["Type"]
						case _:
							if left_row["Type"] == right_row["Type"]:
								type = left_row["Type"]
								if type == "Consonant":
									if nfd_phoneme[-2] == "t" or nfd_phoneme[-2] == "d":
										# Assume Affricate
										# NOTE: Shouldn't be necessary if the iput data uses the proper modern U+0361 ligature!
										feature = lookup_feat_id(con, "Affricate")
									else:
										# Trust the leading consonant's feature (i.e., articulation manner)
										feature = left_row["Feature"]
								elif type == "Vowel":
									feature = lookup_feat_id(con, "Diphthong")
							else:
								type = "Vowel"
								feature = lookup_feat_id(con, "Diphthong")

				data = (phoneme, type, modifier, feature)
				print(f"Inserting new phoneme into PhonemeBank: {data}")
				con.execute("INSERT INTO PhonemeBank(IPA, Type, Modifiers, Feature) VALUES(?, ?, ?, ?)", data)

				data = (phoneme, )
				res = con.execute("SELECT PhonemeID FROM PhonemeBank WHERE IPA = ?", data)
				row = res.fetchone()
			phoneme_id = row["PhonemeID"]
			# Log it
			print(f"{phoneme} is @ rowid {phoneme_id}")
			# Cache it
			MAP_PHONEMES[phoneme] = phoneme_id
			return phoneme_id
	except sqlite3.IntegrityError as e:
			print(f"!! IntegrityError: {e}")

	print()
	raise ValueError(f"Unknown phoneme {phoneme}!")

def insert_data(path: str | Path):
	"""Import data from CSV files into the DB"""
	con = sqlite3.connect(path, autocommit = False)
	con.row_factory = sqlite3.Row

	# Get table names... but we need LangInfo & PhonemeFeature to be handled first, because they host parent keys.
	tables = [ "LangInfo", "PhonemeFeature" ]
	try:
		with con:
			for row in con.execute("SELECT name FROM sqlite_master WHERE type = ? ORDER BY name ASC", ("table", )):
				tables.append(row["name"])
	except sqlite3.IntegrityError as e:
			print(f"!! IntegrityError: {e}")
	# Dedupe while keeping insertion order (no OrderedSet, so we rely on dicts retaining insertion order instead)...
	tables = list(dict.fromkeys(tables))
	# Do not import PhonemeBank.csv, that's only for Neo4j
	tables.remove("PhonemeBank")

	for table in tables:
		csv_file = Path(DATA_PATH / table).with_suffix(".csv")

		if not os.access(csv_file, os.R_OK):
			print(f"No data for table {table}")
			continue

		print(f"Importing data from {csv_file}...")
		with open(csv_file, newline = "") as f:
			# Auto-detect CSV dialect
			dialect = csv.Sniffer().sniff(f.read(1024))
			f.seek(0)

			# NOTE: We need to cast some magic in order to make data entry easier, which is why we can't use pandas' read_csv & to_sql methods...
			reader = csv.DictReader(f, dialect = dialect)
			for row in reader:
				match table:
					case "LangInfo":
						# Drop LangID, it's the primary key/rowid, and as such, empty in our data
						del(row["LangID"])
					case _:
						# Drop rowid (if any)
						row.pop("ID", None)

						# Can't do fall-through in Python, so we branch again for table-specific shenanigans...
						if table == "Inspiration":
							# Lookup PhonologyFeature
							feature = row["PhonologyFeature"]
							feat_id = lookup_feat_id(con, feature)
							# Replace the feature name by its id
							row["PhonologyFeature"] = feat_id
						elif table == "Phonology":
							# Lookup PhonemeID
							phoneme = row["PhonemeID"]
							phoneme_id = lookup_phoneme_id(con, phoneme)
							# Replace the feature name by its id
							row["PhonemeID"] = phoneme_id

						# Lookup LangID (if any), as we use the name and not the db's rowid in our data to make data entry easier
						lang_name = row.get("LangID")
						if lang_name:
							lang_id = lookup_lang_id(con, lang_name)
							# Replace the lang name by its id
							row["LangID"] = lang_id

				# Formatting for the prepared statement (column list)...
				columns = ", ".join(row.keys())
				# Repeat comma-separated ? for as many columns as we have...
				qmarks = ["?" for i in range(len(row))]
				val_placeholders = ", ".join(qmarks)

				query = f"INSERT INTO {table}({columns}) VALUES({val_placeholders})"
				data = tuple(row.values())
				# Print the query for debugging purposes...
				print(query)
				print(data)

				try:
					with con:
						con.execute(query, data)
				except sqlite3.IntegrityError as e:
						print(f"!! IntegrityError: {e}")

	con.close()
	print("Inserted data successfully!")

def main():
	"""Main entry point"""
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
