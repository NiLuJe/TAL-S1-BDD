#!/bin/sh

sqlite3 -header -csv DB/conlangs.db "SELECT * FROM PhonemeBank;" > data/PhonemeBank.csv
