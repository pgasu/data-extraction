#!/usr/bin/env python3

import requests, os, csv, time, argparse
import pandas as pd
from requests.exceptions import ConnectionError
from query import query_database
from api_call import pmc_api_search_article_ids, pmc_multiple_api_call
from csv_util import standardize_csvfile

#Query PMC and download citations of resulting articles as .ris file for each genus
if __name__=='__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('--input', help='name of input file. The file must contain the fields to be queried')
	parser.add_argument('--excluded', help='name of file containing genus/species/common names to be excluded')
	parser.add_argument('--query-type', choices=['q1', 'q2', 'q3', 'q4', 'q5'], help="""Type of search queries to use: 
						q1: genus name, 
						q2: genus name OR genus synonyms, 
						q3: genus name OR genus synonyms or common names, 
						q4: scientific name OR synonyms(combinations of genus and epithet synonyms), 
						q5: scientific name or synonyms or common names""")
	parser.add_argument('--database-list', nargs='*', help='list of databases to be queried, e.g. ["pmc", "pubmed", "scopus", "Google Scholar"]')

	args=parser.parse_args()
	input_file = args.input
	if input_file == None: input_file = 'MDD_v1.6_allSynonyms_NAm_Rodentia.csv'


	standardize_csvfile('MDD_v1.6_allSynonyms_NAm_Rodentia.csv', 'MDD_genus_syn_8Oct2021_NAmRodentia.csv', 'NAm_Rodent_Excluded_Names.csv')

	with open('NAm_Rodent_Lit_Search.csv') as f:
		rows = list(csv.DictReader(f))
		search_result = query_database(rows, 'pmc')

	all_ids = []
	unique_ids = []
	for key, value in search_result.items():
		# if (len(value[6])<500):
		all_ids.extend(value[6])
	unique_ids = list(set(all_ids))
	print(len(all_ids), len(unique_ids))



	# updated_file = {}
	# citations_file = open('genus_combined_citations_new.ris', 'ab+')
	# while True:
	# 	print("New run")
	# 	missed_keys = False
	# 	for key, value in response_to_queries.items():
	# 		if (key in updated_file and len(updated_file[key])==8):
	# 			continue

	# 		id_list = value[6]

	# 		headers = {
	# 			'tool':'Data_extraction/0.1.0',
	# 			'email':'pgupt109@asu.edu'
	# 		}
	# 		params = {
	# 			'id': id_list,
	# 			'download':'Y',
	# 			'format':'ris'
	# 		}
	# 		try:
	# 			response = requests.get('https://api.ncbi.nlm.nih.gov/lit/ctxp/v1/pmc', params=params, headers=headers)
	# 			updated_file[key] = value
	# 			print(key, response.status_code, len(value))
	# 			if response.status_code != 200:
	# 				updated_file[key].append('Status_code: '+str(response.status_code))
	# 				continue
	# 			filename = key + '.ris'
	# 			# open(filename, 'wb').write(response.content)
	# 			citations_file.write(response.content)
	# 			updated_file[key].append(filename)
	# 		except ConnectionError as e:
	# 			missed_keys = True
	# 			print(e)
	# 			time.sleep(10)


	# 	if missed_keys == False:
	# 		break
	# citations_file.close()


	with open('NAm_Rodent_Lit_Search_Result.csv', 'w', newline='') as f:
		fieldnames = ['genus.x', 'Genus synonyms', 'Main common name', 'Other common names', 'Excluded names', 'PubMed Central search query', 'Search result']
		writer = csv.DictWriter(f, fieldnames=fieldnames)
		writer.writeheader()
		
		for key, value in search_result.items():
			genus = key
			genus_syns = value[1]
			main_common_name = value[2]
			other_common_name = value[3]
			excluded_names = value[4]
			search_query = value[5]
			result = len(value[6])
			writer.writerow({'genus.x': genus, 'Genus synonyms':genus_syns, 'Main common name': main_common_name, 'Other common names': other_common_name, 
							'Excluded names': excluded_names, 'PubMed Central search query': search_query, 'Search result': result})




	
# # Update the csv file with search_query, response as in number of articles, and the name of downloaded .ris file (or the status code if the query is too large)
# 	with 


			
			
