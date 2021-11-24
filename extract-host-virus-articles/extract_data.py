#!/usr/bin/env python3

import requests, os, csv, time, argparse
import pandas as pd
from requests.exceptions import ConnectionError
from query import query_database
from api_call import pmc_api_search_article_ids, pmc_multiple_api_call
from csv_util import process_csv

#Query PMC and download citations of resulting articles as .ris file for each genus
if __name__=='__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('--input', default='MDD_v1.6_allSynonyms_NAm_Rodentia.csv', \
						help='name of the input file. The file must be in CSV format and contains the fields to be queried')
	parser.add_argument('--genus_synonyms', default='MDD_genus_syn_8Oct2021_NAmRodentia.csv', \
						help='name of the file containing genus synonyms (CSV format)')
	parser.add_argument('--excluded', default = 'NAm_Rodent_Excluded_Names.csv', help='name of file containing genus/species/common names to be excluded')
	parser.add_argument('--query-type', choices=['q1', 'q2', 'q3', 'q4', 'q5'], help="""Type of search queries to use: 
						q1: genus name, 
						q2: genus name OR genus synonyms, 
						q3: genus name OR genus synonyms or common names, 
						q4: scientific name OR synonyms(combinations of genus and epithet synonyms), 
						q5: scientific name or synonyms or common names""")
	parser.add_argument('--database-list', nargs='*', help='list of databases to be queried, e.g. ["pmc", "pubmed", "scopus", "Google Scholar"]')

	args=parser.parse_args()
	input_file = args.input
	genus_syns = args.genus_synonyms
	excluded = args.excluded

	process_csv(input_file, genus_syns, excluded)

	with open('NAm_Rodent_Lit_Search.csv') as f:
		rows = list(csv.DictReader(f))
		search_result = query_database(rows, 'google scholar')

	with open('NAm_Rodent_Lit_Search_Result.csv', 'w', newline='') as f:
		fieldnames = ['genus.x', 'Genus synonyms', 'Specific epithet', 'Epithet synonyms', 'Main common name', 'Other common names', 'Excluded names', \
						'PubMed Central search query', 'Search result']
		writer = csv.DictWriter(f, fieldnames=fieldnames)
		writer.writeheader()
		
		for key, value in search_result.items():
			genus = key
			genus_syns = value[1]
			epithet = value[2]
			ep_syns = value[3]
			main_common_name = value[4]
			other_common_name = value[5]
			excluded_names = value[6]
			search_query = value[7]
			result = len(value[8])
			writer.writerow({'genus.x': genus, 'Genus synonyms':genus_syns, 'Specific epithet': epithet, 'Epithet synonyms': ep_syns, 'Main common name': main_common_name, \
							'Other common names': other_common_name, 'Excluded names': excluded_names, 'PubMed Central search query': search_query, 'Search result': result})

	all_ids = []
	unique_ids = []
	for key, value in search_result.items():
		if (len(value[8])<500):
			all_ids.extend(value[8])
	unique_ids = list(set(all_ids))
	print(len(all_ids), len(unique_ids))

	with open('pubmed_citations.ris', 'ab+') as citations_file:
		count = 0
		while True:
			missed_keys = False
			for i in range(count, len(unique_ids), 25):
				print(i)
				id_list = unique_ids[i:i+25]

				headers = {
					'tool':'Data_extraction/0.1.0',
					'email':'pgupt109@asu.edu'
				}
				params = {
					'id': id_list,
					'download':'Y',
					'format':'ris'
				}
				try:
					response = requests.get('https://api.ncbi.nlm.nih.gov/lit/ctxp/v1/pubmed', params=params, headers=headers)
					if response.status_code != 200:
						print(f'{response}')
						missed_keys = False
						break
					citations_file.write(response.content)

				except ConnectionError as e:
					missed_keys = True
					print(e)
					count = i
					break

			if missed_keys == False:
				break
