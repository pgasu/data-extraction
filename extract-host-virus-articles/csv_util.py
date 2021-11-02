#!/usr/bin/env python3

import csv

def standardize_csvfile(filename1, filename2, filename3):

	standard_file_content = read_standard_columns_from_csvfile(filename1)
	genus_synonyms = extract_genus_synonyms(filename2)
	excluded_names = extract_excluded_names(filename3)

#	Create a new file for species lumping all synonyms for each species in a single row

	with open('NAm_Rodent_Lit_Search.csv', 'w', newline='') as f:
		fieldnames = ['genus.x', 'specificEpithet.x', 'Genus synonyms', 'Epithet synonyms', 'Synonym edits', 'Main common name', 'Other common names', 'Excluded names']
		writer = csv.DictWriter(f, fieldnames=fieldnames)
		writer.writeheader()
		
		for key, value in standard_file_content.items():
			genus, epithet = key.split()
			epithet_synonyms = value[0]
			genus_syns = '|'.join(genus_synonyms[genus])
			main_common_name = value[1]
			other_common_name = value[2]
			exc_names = excluded_names[key] if key in excluded_names else ''
			writer.writerow({'genus.x': genus, 'specificEpithet.x': epithet, 'Genus synonyms':genus_syns, 'Epithet synonyms':epithet_synonyms,
			 				'Main common name': main_common_name, 'Other common names': other_common_name, 'Excluded names': exc_names})

def read_standard_columns_from_csvfile(filename):

	genus_epithet_details = {}

	with open(filename) as f:
		rows = csv.DictReader(f)
		for row in rows:
			genus_epithet = row['genus.x'] + " " + row['specificEpithet.x']

			if genus_epithet in genus_epithet_details:
				genus_epithet_details[genus_epithet][0] += "|" + row['synonym']
			else:
				genus_epithet_details[genus_epithet] = [row['synonym'], row['mainCommonName'], row['otherCommonNames']]

	return genus_epithet_details

def extract_genus_synonyms(filename):

	genus_synonyms = {}

	with open(filename) as f:
		rows = csv.DictReader(f)
		for row in rows:
			genus = row['genus']

			if genus in genus_synonyms:
				genus_synonyms[genus].append(row['synonym'])
			else:
				genus_synonyms[genus] = [row['synonym']]

	return genus_synonyms

def extract_excluded_names(filename):
	excluded_names = {}

	with open(filename) as f:
		rows = csv.DictReader(f)
		for row in rows:
			key = row['genus.x'] + ' ' + row['specificEpithet.x']
			excluded_names[key] = row['Excluded names']

	return excluded_names