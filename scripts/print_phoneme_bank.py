#!/usr/bin/env python3

# See also: gruut-ipa, ipasymbols, and, most importantly: panphon
import ipapy

def print_phoneme_bank():
	"""Print the phoneme bank to stdout"""
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
			print(p.manner)
			print(p.place)
			if p.modifiers:
				print(" ".join(p.modifiers))
		elif p.is_diacritic:
			print(p)
			print(p.name.replace(" diacritic", ""))
		elif p.is_suprasegmental:
			print(p)
			print(p.name.replace(" suprasegmental", ""))
		elif p.is_tone:
			print(p)
			print(p.name.replace(" tone", ""))

if __name__ == "__main__":
	print_phoneme_bank()
