#!/usr/bin/env python3

import requests
import os
import csv
import time
import pandas as pd

api_key = '310a232c07175b642551785374fdecd7e508'
species_synonyms = {}
genus_synonyms = {}

def get_synonyms_list_per_species(filename):
	"""
	The argument (filename) should be a csv file with required columns: 'genus.x', 'specificEpithet.x', 'synonym', 'Synonym edits', 'mainCommonName', 'otherCommonNames'
	and 'Excluded names'. 
	The csv file  displays synonyms for a species on separate rows. The function lumps synonyms for each species and creates a dictionary mapping each species
	to a list of its synonyms and other properties, and return the dictionary
	"""

	species_synonyms = {}

	with open(filename) as f:
		rows = csv.DictReader(f)
		for row in rows:
			genus = row['genus.x']
			epithet = row['specificEpithet.x']
			synonyms = row['synonym']
			synonym_edit = row['Synonym edits']
			main_common_name = row['mainCommonName']
			other_common_name = row['otherCommonNames']
			excluded_names = row['Excluded names']

			genus_plus_epithet = genus + " " + epithet
			if genus_plus_epithet in species_synonyms:
				species_synonyms[genus_plus_epithet][0] += "|" + synonyms
			else:
				species_synonyms[genus_plus_epithet] = [synonyms, synonym_edit, main_common_name, other_common_name, excluded_names]

		return species_synonyms


def get_synonyms_list_per_genus(filename):
	"""
	The function creates and returns a dictionary mapping each genus to a list of its synonyms
	The argument (filename) should be a csv file with required columns: 'genus', and 'synonym'
	"""

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


if __name__=='__main__':

	# species_synonyms = get_synonyms_list_per_species('NAm_Rodent_Lit_Search_MDD_v1.6_allSynonyms.csv')
	# genus_synonyms = get_synonyms_list_per_genus('MDD_genus_syn_8Oct2021_NAmRodentia.csv')

# Create a new file for species lumping all synonyms for each species in a single row
	# with open('NAm_Rodent_Lit_Search_All_Synonyms.csv', 'w', newline='') as f:
	# 	fieldnames = ['genus.x', 'specificEpithet.x', 'Genus synonyms', 'Epithet synonyms', 'Synonym edits', 'Main common name', 'Other common names', 'Excluded names']
	# 	writer = csv.DictWriter(f, fieldnames=fieldnames)
	# 	writer.writeheader()
	#	
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


# Create a new file for Genus level queries lumping all main and other common names (per genus)
	genus_common_names = {}
	with open('NAm_Rodent_Lit_Search_All_Synonyms.csv') as f:
		rows = csv.DictReader(f)
		for row in rows:
			genus = row['genus.x']
			genus_syns = row['Genus synonyms']
			main_common_name = row['Main common name']
			other_common_name = row['Other common names']
			excluded_names = row['Excluded names']

			if genus in genus_common_names:
				genus_common_names[genus][1] += "|"+main_common_name
				if other_common_name != "":
					genus_common_names[genus][2] += "|"+other_common_name
			else:
				genus_common_names[genus] = [genus_syns, main_common_name, other_common_name, excluded_names]

	with open('NAm_Rodent_Lit_Search_Genus.csv', 'w', newline='') as f:
		fieldnames = ['genus.x', 'Genus synonyms', 'Main common name', 'Other common names', 'Excluded names']
		writer = csv.DictWriter(f, fieldnames=fieldnames)

		writer.writeheader()
		for key, value in genus_common_names.items():
			genus_syns = value[0]
			main_common_name = value[1]
			other_common_name = value[2]
			excluded_names = value[3]
			writer.writerow({'genus.x': key, 'Genus synonyms':genus_syns,'Main common name': main_common_name, 'Other common names': other_common_name, 'Excluded names': excluded_names})

# 	response_to_queries ={}

# #Query PMC and download citations of resulting articles as .ris file for each genus

# 	df = pd.read_csv('NAm_Rodent_Lit_Search_Genus.csv')
# 	#df['Excluded names'] = df['Excluded names'].astype(int).astype(str)
# 	print(df.dtypes)

# 	for index, row in df.iterrows():
# 		print(row['genus.x'])
# 		print(type(row['Excluded names']))
# 		genus = row['genus.x']
# 		synonyms = row['Genus synonyms'].split('|')
# 		common_names = [name for name in ((row['Main common name'] + '|' + row['Other common names']).split('|')) if pd.isnull(row['Excluded names']) or name not in (row['Excluded names'].split('|'))]
# 		common_names = [name for name in common_names if name]
# 		search_query = '(Virus OR viruses OR viral) AND ('
# 		if len(common_names)>0:
# 			for name in common_names:
# 				search_query += '"' + name + '" OR '

# 		for genus_syn in synonyms:
# 			search_query += '"' + genus_syn + '" OR '
# 		search_query = search_query[0:-4]
# 		search_query += ')'

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
# 		id_list = response.json()['esearchresult']['idlist']
# 		id_list = [int(idx) for idx in id_list]
# 		df.at[index, "PubMed Central search query"] = search_query
# 		df.at[index, "Response"] = len(id_list)
# 		df.to_csv('NAm_Rodent_Lit_Search_Genus.csv', index=False)

# 		params = {
# 			'tool':'ASU_BioKIC',
# 			'email':'prashant.gupta.2@asu.edu',
# 			'api_key':api_key,
# 			'id': id_list,
# 			'download':'Y',
# 			'format':'ris'
# 		}
# 		response = requests.get('https://api.ncbi.nlm.nih.gov/lit/ctxp/v1/pmc', params=params)
# 		if response.status_code == 414:
# 			continue
# 		filename = genus + '.ris'
# 		open(filename, 'wb').write(response.content)

# 	with open('NAm_Rodent_Lit_Search_Genus.csv') as f:
# 		rows = csv.DictReader(f)
# 		for row in rows:
# 			genus = row['genus.x']
# 			synonyms = row['Genus synonyms'].split('|')
# 			common_names = [name for name in ((row['Main common name'] + '|' + row['Other common names']).split('|')) if row['Excluded names']=='' or name not in (row['Excluded names'].split('|'))]
# 			common_names = [name for name in common_names if name]
# 			search_query = '(Virus OR viruses OR viral) AND ('
# 			if len(common_names)>0:
# 				for name in common_names:
# 					search_query += '"' + name + '" OR '

# 			for genus_syn in synonyms:
# 				search_query += '"' + genus_syn + '" OR '
# 			search_query = search_query[0:-4]
# 			search_query += ')'

# 			parameters = {
# 				'tool':'ASU_BioKIC',
# 				'email':'prashant.gupta.2@asu.edu',
# 				'api_key':api_key,
# 				'db': 'pmc',
# 				'term': search_query,
# 				'retmax':100000,
# 				'retmode':'json'	
# 				}
# 			response = requests.post('https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi', params=parameters)
# 			id_list = response.json()['esearchresult']['idlist']
# 			id_list = [int(idx) for idx in id_list]

# 			response_to_queries[genus] = [search_query, len(id_list)]

# 			params = {
# 				'tool':'ASU_BioKIC',
# 				'email':'prashant.gupta.2@asu.edu',
# 				'api_key':api_key,
# 				'id': id_list,
# 				'download':'Y',
# 				'format':'ris'
# 			}
# 			response = requests.get('https://api.ncbi.nlm.nih.gov/lit/ctxp/v1/pmc', params=params)
# 			print(response)
# 			if response.status_code == 414:
# 				response_to_queries[genus].append('Status_code: 414')
# 				continue
# 			filename = genus + '.ris'
# 			open(filename, 'wb').write(response.content)
# 			response_to_queries[genus].append(filename)

	
# # Update the csv file with search_query, response as in number of articles, and the name of downloaded .ris file (or the status code if the query is too large)
# 	with 


			
			
