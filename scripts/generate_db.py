#!/usr/bin/env python3

from pathlib import Path
import sqlite3

# Path shenanigans, relative to this script
BASE_DIR = Path(__file__).parent.parent.resolve()
DB_PATH = Path(BASE_DIR / "DB" / "conlangs.db")
SCHEMA_PATH = Path(BASE_DIR / "data" / "conlangs_schema.sql")

def create_db(path: str|Path):
	con = sqlite3.connect(path)
	cur = con.cursor()

	with open(SCHEMA_PATH) as f:
		cur.executescript(f.read())

	con.close()

def main():
	while True:
		action = input("[C]reate / [G]enerate >>> ")
		match action.strip().upper():
			case "C":
				create_db(DB_PATH)
			case "G":
				print("NYI")
			case "":
				break
			case _:
				print("Unsupported action")

# Only run when called as a script, not an import
if __name__ == "__main__":
	main()
