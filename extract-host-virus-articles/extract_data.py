#!/usr/bin/env python3

import requests
import os
import csv

api_key = '310a232c07175b642551785374fdecd7e508'
species_synonyms = {}
genus_synonyms = {}

if __name__=='__main__':


	# with open('NAm_Rodent_Lit_Search.csv') as f:
	# 	rows = csv.DictReader(f)
	# 	for row in rows:
	# 		genus = row['genus.x']
	# 		epithet = row['specificEpithet.x']
	# 		synonyms = row['synonym']
	# 		synonym_edit = row['Synonym edits']
	# 		main_common_name = row['mainCommonName']
	# 		other_common_name = row['otherCommonNames']
	# 		excluded_names = row['Excluded names']

	# 		genus_plus_epithet = genus + " " + epithet
	# 		if genus_plus_epithet in species_synonyms:
	# 			species_synonyms[genus_plus_epithet][0] += "|" + synonyms
	# 		else:
	# 			species_synonyms[genus_plus_epithet] = [synonyms, synonym_edit, main_common_name, other_common_name, excluded_names]


	# with open('MDD_v1.6_allSynonyms_NAm_Rodentia.csv') as f:
	# 	rows = csv.DictReader(f)
	# 	for row in rows:
	# 		genus_plus_epithet = row['genus.x'] + ' ' + row['specificEpithet.x']
	# 		if genus_plus_epithet in species_synonyms:
	# 			species_synonyms[genus_plus_epithet].append(row['synonym'])
	# 		else:
	# 			species_synonyms[genus_plus_epithet] = [row['synonym']]

	# with open('MDD_genus_syn_8Oct2021_NAmRodentia.csv') as f:
	# 	rows = csv.DictReader(f)
	# 	for row in rows:
	# 		genus = row['genus']
	# 		if genus in genus_synonyms:
	# 			genus_synonyms[genus].append(row['synonym'])
	# 		else:
	# 			genus_synonyms[genus] = [row['synonym']]

	# with open('test.csv', 'w', newline='') as f:
	# 	fieldnames = ['genus.x', 'specificEpithet.x', 'Genus synonyms', 'Epithet synonyms', 'Synonym edits', 'Main common name', 'Other common names', 'Excluded names']
	# 	writer = csv.DictWriter(f, fieldnames=fieldnames)

	# 	writer.writeheader()
	# 	for key, value in species_synonyms.items():
	# 		genus, epithet = key.split()
	# 		epithet_synonyms = value[0]
	# 		genus_syns = '|'.join(genus_synonyms[genus])
	# 		synonym_edits = value[1]
	# 		main_common_name = value[2]
	# 		other_common_name = value[3]
	# 		excluded_names = value[4]
	# 		writer.writerow({'genus.x': genus, 'specificEpithet.x': epithet, 'Genus synonyms':genus_syns, 'Epithet synonyms':epithet_synonyms, 'Synonym edits':synonym_edits,
	# 		 				'Main common name': main_common_name, 'Other common names': other_common_name, 'Excluded names': excluded_names})


	with open('NAm_Rodent_Lit_Search_All_Synonyms.csv') as f:
		rows = csv.DictReader(f)
		for row in rows:
			genus = row['genus.x']
			genus_syns = row['Genus synonyms']
			main_common_name = row['Main common name']
			other_common_name = row['Other common names']
			excluded_names = row['Excluded names']

			if genus in genus_synonyms:
				pass
			else:
				genus_synonyms[genus] = [genus_syns, main_common_name, other_common_name, excluded_names]

	with open('NAm_Rodent_Lit_Search_Genus.csv', 'w', newline='') as f:
		fieldnames = ['genus.x', 'Genus synonyms', 'Main common name', 'Other common names', 'Excluded names']
		writer = csv.DictWriter(f, fieldnames=fieldnames)

		writer.writeheader()
		for key, value in genus_synonyms.items():
			genus_syns = value[0]
			main_common_name = value[1]
			other_common_name = value[2]
			excluded_names = value[3]
			writer.writerow({'genus.x': key, 'Genus synonyms':genus_syns,'Main common name': main_common_name, 'Other common names': other_common_name, 'Excluded names': excluded_names})


	# with open('NAm_Rodent_Lit_Search_All_Synonyms.csv') as f:
	# 	rows = csv.DictReader(f)
	# 	for row in rows:
	# 		genus = row['genus.x']
	# 		epithet = row['specificEpithet.x']
	# 		common_names = (row['otherCommonNames'] + '|' + row['mainCommonName']).split('|')
	# 		genus_synonyms_list = list(set(genus_synonyms[genus] + [genus]))
	# 		species_synonyms_list = list(set(species_synonyms[genus+' '+epithet] + [epithet]))
			
	# 		search_query = '(Virus OR viruses OR viral) AND ('
	# 		if len(common_names)>0:
	# 			for name in common_names:
	# 				search_query += '"' + name + '" OR '

	# 		# for genus_syn in genus_synonyms_list:
	# 		# 	for species_syn in species_synonyms_list:
	# 		# 		search_query += '"' + genus_syn + ' ' + species_syn + '" OR '

	# 		for genus_syn in genus_synonyms_list:
	# 			search_query += '"' + genus_syn + '" OR '
	# 		search_query = search_query[0:-4]
	# 		search_query += ')'

	# 		print(search_query)
	# 		#search_query = '(Virus OR viruses OR viral) AND (Aplodontia rufa OR Aplodontia leporina OR Aplodontia californica OR "Aplodontia major" OR "Aplodontia olympica" OR "Aplodontia pacifica" OR "Aplodontia phaea" OR "Aplodontia rainieri" OR "Aplodontia chryseola" OR "Aplodontia nigra" OR "Aplodontia columbiana" OR "Aplodontia grisea" OR "Aplodontia humboldtiana" OR "Mountain Beaver" OR "Sewellel" OR "Point Arena Mountain Beaver" OR "Point Reyes Mountain Beaver" OR "Haploodus nigra" OR "Haploodus leporina" OR "Haploodus phaea" OR "Haploodus olympica" OR "Haploodus humboldtiana" OR "Haploodus rufa" OR "Haploodus grisea" OR "Haploodus major" OR "Haploodus chryseola" OR "Haploodus californica" OR "Haploodus columbiana" OR "Haploodus pacifica" OR "Haploodus rainieri")'
	# 		parameters = {
	# 			'tool':'ASU_BioKIC',
	# 			'email':'prashant.gupta.2@asu.edu',
	# 			'api_key':api_key,
	# 			'db': 'pmc',
	# 			'term': search_query,
	# 			'retmax':100000,
	# 			'retmode':'json'	
	# 			}
	# 		response = requests.post('https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi', params=parameters)
	# 		print(len(response.json()['esearchresult']['idlist']))

			
			
