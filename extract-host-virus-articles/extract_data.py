#!/usr/bin/env python3

import requests
import os
import csv
import time
import pandas as pd
from requests.exceptions import ConnectionError
from query_util import query_database
from api_call import pmc_api_search_article_ids, pmc_multiple_api_call
from csv_util import standardize_csvfile

#Query PMC and download citations of resulting articles as .ris file for each genus
if __name__=='__main__':

	standardize_csvfile('MDD_v1.6_allSynonyms_NAm_Rodentia.csv')

	response_to_queries ={}
	genus_with_irregular_results = []

	with open('NAm_Rodent_Lit_Search_Species.csv') as f:
		rows = list(csv.DictReader(f))
		search_result = query_database(rows, 'pmc')

		for row in rows:
			# If a genus has already been queried, then we let it pass for subsequent rows - the same genus may appear in multiple rows as each row represents a specific species
			if row['genus.x'] in response_to_queries and row['genus.x'] not in genus_with_irregular_results:
				continue
			else if row['genus.x'] in genus_with_irregular_results:

			search_query = create_genus_union_common_names_query(row)
			api_response = pmc_api_search_article_ids(search_query)
			if type(api_response) != list and api_response.status_code == 414:
				list_of_smaller_search_queries = decompose_genus_union_common_names_query(row)
				api_response = pmc_multiple_api_call(list_of_smaller_search_queries)

			if type(api_response)==list and len(api_response)>500:
				genus_with_irregular_results.append(row['genus.x'])
			else:
				response_to_queries[row['genus.x']] = [row['genus.x'], row['Genus synonyms'], row['Main common name'], row['Other common names'], row['Excluded names'], search_query, api_response]


		for row in rows:
			if row['genus.x'] in genus_with_irregular_results:
				search_query = create_scientific_name_union_common_names_query(row)
				api_response = pmc_api_search_article_ids(search_query)
				if type(api_response) != list and api_response.status_code == 414:
					list_of_smaller_search_queries = decompose_scientific_name_union_common_names_query(row)
					api_response = pmc_multiple_api_call(list_of_smaller_search_queries)
					print(api_response)

				if row['genus.x'] in response_to_queries:
					response_to_queries[row['genus.x']][6].extend(api_response)
				else:
					response_to_queries[row['genus.x']] = [row['genus.x'], row['Genus synonyms'], row['Main common name'], row['Other common names'], row['Excluded names'], search_query, api_response]


	all_ids = []
	unique_ids = []
	for key, value in response_to_queries.items():
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


	with open('NAm_Rodent_Lit_Search_Genus.csv', 'w', newline='') as f:
		fieldnames = ['genus.x', 'Genus synonyms', 'Main common name', 'Other common names', 'Excluded names', 'PubMed Central search query', 'Search result']
		writer = csv.DictWriter(f, fieldnames=fieldnames)
		writer.writeheader()
		
		for key, value in response_to_queries.items():
			genus = key
			genus_syns = value[1]
			main_common_name = value[2]
			other_common_name = value[3]
			excluded_names = value[4]
			search_query = value[5]
			result = len(list(set(value[6])))
			writer.writerow({'genus.x': genus, 'Genus synonyms':genus_syns, 'Main common name': main_common_name, 'Other common names': other_common_name, 
							'Excluded names': excluded_names, 'PubMed Central search query': search_query, 'Search result': result})




	
# # Update the csv file with search_query, response as in number of articles, and the name of downloaded .ris file (or the status code if the query is too large)
# 	with 


			
			
