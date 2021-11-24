#!/usr/bin/env python3

import math, copy, ssl
from api_call import pmc_api_search_article_ids, pmc_multiple_api_call, scopus_api_search_article_ids
from scholarly import scholarly, ProxyGenerator
from fp.fp import FreeProxy

# q1 - genus union common names query
# q2 - scientific name union common names query

def query_database(list_of_dicts, database):

	query_response = {}
	genus_with_more_than_threshold_results = []

	# Haven't included code for querying multiple databases
	merged_rows_with_same_genus = {}

	for row in list_of_dicts:
		if row['genus.x'] in merged_rows_with_same_genus:
			if row['Main common name'] != '': merged_rows_with_same_genus[row['genus.x']]['Main common name'] += '|'+row['Main common name']
			if row['Other common names'] != '': merged_rows_with_same_genus[row['genus.x']]['Other common names'] += '|'+row['Other common names'] 
		else:
			merged_rows_with_same_genus[row['genus.x']] = copy.deepcopy(row)

	if database == 'google scholar':
		print('inside the loop')
		# ssl._create_default_https_context = ssl._create_unverified_context
		# ssl.ssl_verify = True

		

		for key, value in merged_rows_with_same_genus.items():
			search_query_list = create_google_scholar_q1(value)
			print('got the quesry list')
			bibtex_list = []
			for search_query in search_query_list:
				pg = ProxyGenerator()
				print(pg)
				#success = pg.ScraperAPI('86ec6c6fd7438f17779375e71b20810b')
				# proxy = FreeProxy(rand=True, timeout=1, country_id=['US']).get()
				# print(proxy)
				# pg.SingleProxy(http =proxy, https =proxy)

				success = pg.Luminati(usr = "lum-customer-hl_1f0a2d53-zone-unblocker", passwd="akv76bfl6rbd", proxy_port=22225) #ScraperAPI(API_KEY ='86ec6c6fd7438f17779375e71b20810b')
				# print(success)
				scholarly.use_proxy(pg)
				print('proxy done!')
				api_response = scholarly.search_pubs(search_query, citations=False)
				for pub in api_response:
						bibtex_list.append(scholarly.bibtex(pub))
				print(bibtex_list)

			if len(bibtex_list) > 500:
				print('it is greater than 500')
				genus_with_more_than_threshold_results.append(value['genus.x'])
			else:
				print(len(bibtex_list), len(list(set(bibtex_list))))
				query_response[value['genus.x']] = [value['genus.x'], value['Genus synonyms'], '', '', value['Main common name'], value['Other common names'], \
														value['Excluded names'], search_query_list, bibtex_list]

		for row in list_of_dicts:
			if row['genus.x'] in genus_with_more_than_threshold_results:
				search_query = create_google_scholar_q2(row)
				bibtex_list = []
				for search_query in search_query_list:
					api_response = scholarly.search_pubs(search_query, citations=False)
					for pub in api_response:
						bibtex_list.append(scholarly.bibtex(pub))


				if row['genus.x'] in query_response:
					bibtex_list = list(set(query_response[row['genus.x']][8] + bibtex_list))
					query_response[row['genus.x']][8] = bibtex_list
					query_response[row['genus.x']][2] += f'|{row["specificEpithet.x"]}'
					query_response[row['genus.x']][3] += f'|{row["Epithet synonyms"]}'
				else:
					query_response[row['genus.x']] = [row['genus.x'], row['Genus synonyms'], row['specificEpithet.x'], row['Epithet synonyms'], \
														merged_rows_with_same_genus[row['genus.x']]['Main common name'], \
														merged_rows_with_same_genus[row['genus.x']]['Other common names'], \
														row['Excluded names'], search_query_list, bibtex_list]



	if database == 'pmc' or database == 'pubmed':
		for key, value in merged_rows_with_same_genus.items():

			search_query = create_pmc_q1(value)
			api_response = scopus_api_search_article_ids(search_query)
			break
			if type(api_response) != list and api_response.status_code == 414:
				list_of_smaller_search_queries = decompose_pmc_q1(value)
				api_response = pmc_multiple_api_call(list_of_smaller_search_queries)

			if type(api_response)==list and len(api_response)>500:
				genus_with_more_than_threshold_results.append(value['genus.x'])
			else:
				query_response[value['genus.x']] = [value['genus.x'], value['Genus synonyms'], '', '', value['Main common name'], value['Other common names'], \
														value['Excluded names'], search_query, api_response]

		for row in list_of_dicts:
			if row['genus.x'] in genus_with_more_than_threshold_results:
				search_query = create_pmc_q2(row)
				api_response = pmc_api_search_article_ids(search_query)
				if type(api_response) != list and api_response.status_code == 414:
					list_of_smaller_search_queries = decompose_pmc_q2(row)
					api_response = pmc_multiple_api_call(list_of_smaller_search_queries)

				if row['genus.x'] in query_response:
					unique_ids = list(set(query_response[row['genus.x']][8] + api_response))
					query_response[row['genus.x']][8] = unique_ids
					query_response[row['genus.x']][2] += f'|{row["specificEpithet.x"]}'
					query_response[row['genus.x']][3] += f'|{row["Epithet synonyms"]}'
					if row['genus.x'] == 'Clethrionomys': print(query_response['Clethrionomys'])
				else:
					query_response[row['genus.x']] = [row['genus.x'], row['Genus synonyms'], row['specificEpithet.x'], row['Epithet synonyms'], \
														merged_rows_with_same_genus[row['genus.x']]['Main common name'], \
														merged_rows_with_same_genus[row['genus.x']]['Other common names'], row['Excluded names'], '', api_response]
					if row['genus.x'] == 'Clethrionomys': print(query_response['Clethrionomys'])

	return query_response


def create_pmc_q1(row):
	genus = row['genus.x']
	row['Genus synonyms'] += f'|{genus}'
	excluded_names = [] if row['Excluded names']=='' else row['Excluded names'].split('|')
	synonyms = [syn for syn in row['Genus synonyms'].split('|') if syn not in excluded_names]
	common_names = row['Main common name'] if row['Other common names']=="" else row['Main common name'] + '|' + row['Other common names']
	common_names = [name for name in common_names.split('|') if name not in excluded_names]

	search_query = '("Virus" OR "viruses" OR "viral") AND ('

	if len(common_names)>0:
		for name in common_names:
			search_query += '"' + name + '" OR '

	for genus_syn in synonyms:
		search_query += '"' + genus_syn + '" OR '
	search_query = search_query[0:-4]
	search_query += ')'

	return search_query


def decompose_pmc_q1(row):

	list_of_search_queries = []
	genus = row['genus.x']
	row['Genus synonyms'] += f'|{genus}'
	excluded_names = [] if row['Excluded names']=='' else row['Excluded names'].split('|')
	synonyms = [syn for syn in row['Genus synonyms'].split('|') if syn not in excluded_names]
	common_names = row['Main common name'] if row['Other common names']=="" else row['Main common name'] + '|' + row['Other common names']
	common_names = [name for name in common_names.split('|') if name not in excluded_names]

	common_search_query = '("Virus" OR "viruses" OR "viral") AND ('

	if len(common_names)>0:
		data_chunks = [common_names[i:i+20] for i in range(0, len(common_names), 20)]
		for names in data_chunks:
			search_query = common_search_query
			for name in names:
				search_query += '"' + name + '" OR '
			search_query = search_query[0:-4] + ')'
			list_of_search_queries.append(search_query)

	data_chunks = [synonyms[i:i+20] for i in range(0, len(synonyms), 20)]
	for genus_syns in data_chunks:
		search_query = common_search_query
		for genus_syn in genus_syns:
			search_query += '"' + genus_syn + '" OR '
		search_query = search_query[0:-4] + ')'
		list_of_search_queries.append(search_query)

	return list_of_search_queries


def create_pmc_q2(row):
	genus = row['genus.x']
	row['Genus synonyms'] += f'|{genus}'
	epithet = row['specificEpithet.x']
	row['Epithet synonyms'] += f'|{epithet}'
	excluded_names = [] if row['Excluded names']=='' else row['Excluded names'].split('|')
	genus_synonyms = list(set([syn for syn in row['Genus synonyms'].split('|') if syn not in excluded_names]))
	epithet_synonyms = list(set([syn for syn in row['Epithet synonyms'].split('|') if syn not in excluded_names]))
	common_names = row['Main common name'] if row['Other common names']=="" else row['Main common name'] + '|' + row['Other common names']
	common_names = [name for name in common_names.split('|') if name not in excluded_names]

	search_query = '("Virus" OR "viruses" OR "viral") AND ('

	if len(common_names)>0:
		for name in common_names:
			search_query += '"' + name + '" OR '

	for genus_syn in genus_synonyms:
		for epithet_syn in epithet_synonyms:
			if row['Excluded names']=='' or genus_syn + ' ' + epithet_syn not in (row['Excluded names'].split('|')):
				search_query +=  '"' + genus_syn + ' ' + epithet_syn + '" OR '

	search_query = search_query[0:-4] + ')'
	return search_query

def decompose_pmc_q2(row):

	list_of_search_queries = []
	genus = row['genus.x']
	row['Genus synonyms'] += f'|{genus}'
	epithet = row['specificEpithet.x']
	row['Epithet synonyms'] += f'|{epithet}'
	excluded_names = [] if row['Excluded names']=='' else row['Excluded names'].split('|')
	genus_synonyms = list(set([syn for syn in row['Genus synonyms'].split('|') if syn not in excluded_names]))
	epithet_synonyms = list(set([syn for syn in row['Epithet synonyms'].split('|') if syn not in excluded_names]))
	common_names = row['Main common name'] if row['Other common names']=="" else row['Main common name'] + '|' + row['Other common names']
	common_names = [name for name in common_names.split('|') if name not in excluded_names]

	common_search_query = '("Virus" OR "viruses" OR "viral") AND ('

	if len(common_names)>0:
		data_chunks = [common_names[i:i+20] for i in range(0, len(common_names), 20)]
		for names in data_chunks:
			search_query = common_search_query
			for name in names:
				search_query += '"' + name + '" OR '
			search_query = search_query[0:-4] + ')'
			list_of_search_queries.append(search_query)

	data_chunks = [epithet_synonyms[i:i+20] for i in range(0, len(epithet_synonyms), 20)]
	for genus_syn in genus_synonyms:
		for epithet_syns in data_chunks:
			search_query = common_search_query
			for epithet_syn in epithet_syns:
				search_query +=  '"' + genus_syn + ' ' + epithet_syn + '" OR '
			search_query = search_query[0:-4] + ')'
			list_of_search_queries.append(search_query)

	return list_of_search_queries

def create_google_scholar_q1(row):
	print("inside q1 creation")
	list_of_search_queries = []
	genus = row['genus.x']
	row['Genus synonyms'] += f'|{genus}'
	excluded_names = [] if row['Excluded names']=='' else row['Excluded names'].split('|')
	synonyms = list(set([syn for syn in row['Genus synonyms'].split('|') if syn not in excluded_names]))
	common_names = row['Main common name'] if row['Other common names']=="" else row['Main common name'] + '|' + row['Other common names']
	common_names = list(set([name for name in common_names.split('|') if name not in excluded_names]))
	all_options = synonyms + common_names
	assert len(all_options)>0, 'The row is missing genus name'

	search_query = '"Virus" '
	for name in all_options:
		if len(search_query + f'"{name}"|') > 252:
			list_of_search_queries.append(search_query[:-1])
			search_query = '"Virus" ' + f'"{name}"|'
		else:
			search_query += f'"{name}"|'
	list_of_search_queries.append(search_query[:-1])

	for q in list_of_search_queries:
		print(q)

	return list_of_search_queries

def create_google_scholar_q2(row):

	list_of_search_queries = []
	genus = row['genus.x']
	row['Genus synonyms'] += f'|{genus}'
	epithet = row['specificEpithet.x']
	row['Epithet synonyms'] += f'|{epithet}'
	excluded_names = [] if row['Excluded names']=='' else row['Excluded names'].split('|')
	genus_synonyms = list(set([syn for syn in row['Genus synonyms'].split('|') if syn not in excluded_names]))
	epithet_synonyms = list(set([syn for syn in row['Epithet synonyms'].split('|') if syn not in excluded_names]))
	genus_epithet_comb = [f'{gen} {ep}' for gen in genus_synonyms for ep in epithet_synonyms]
	common_names = row['Main common name'] if row['Other common names']=="" else row['Main common name'] + '|' + row['Other common names']
	common_names = list(set([name for name in common_names.split('|') if name not in excluded_names]))
	all_options = genus_epithet_comb + common_names
	assert len(all_options)>0, 'The row is missing genus name'

	search_query = '"Virus" '
	for name in all_options:
		if len(search_query + f'"{name}"|') > 252:
			list_of_search_queries.append(search_query[:-1])
			search_query = '"Virus" ' + f'"{name}"|'
		else:
			search_query += f'"{name}"|'
	list_of_search_queries.append(search_query[:-1])

	for q in list_of_search_queries:
		print(q)

	return list_of_search_queries


