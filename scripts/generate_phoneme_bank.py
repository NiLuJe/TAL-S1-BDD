#!/usr/bin/env python3

import ipapy

for p in ipapy.IPA_CHARS:
	print(f"{p}: {p.name} {type(p)}")
	if p.is_vowel:
		print(p)
		print(p.height)
		print(p.backness)
		print(p.roundness)
		if p.modifiers:
			print(" ".join(p.modifiers))
	elif p.is_consonant:
		print(p)
		print(p.voicing)
		print(p.place)
		print(p.manner)
		if p.modifiers:
			print(" ".join(p.modifiers))
