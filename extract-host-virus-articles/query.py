#!/usr/bin/env python3

import math, copy
from api_call import pmc_api_search_article_ids, pmc_multiple_api_call

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

	for key, value in merged_rows_with_same_genus.items():

		search_query = create_genus_union_common_names_query(value)
		api_response = pmc_api_search_article_ids(search_query)
		if type(api_response) != list and api_response.status_code == 414:
			list_of_smaller_search_queries = decompose_genus_union_common_names_query(value)
			api_response = pmc_multiple_api_call(list_of_smaller_search_queries)

		if type(api_response)==list and len(api_response)>500:
			genus_with_more_than_threshold_results.append(value['genus.x'])
		else:
			query_response[value['genus.x']] = [value['genus.x'], value['Genus synonyms'], value['Main common name'], value['Other common names'], \
													value['Excluded names'], search_query, api_response]

	for row in list_of_dicts:
		if row['genus.x'] in genus_with_more_than_threshold_results:
			search_query = create_scientific_name_union_common_names_query(row)
			api_response = pmc_api_search_article_ids(search_query)
			if type(api_response) != list and api_response.status_code == 414:
				list_of_smaller_search_queries = decompose_scientific_name_union_common_names_query(row)
				api_response = pmc_multiple_api_call(list_of_smaller_search_queries)

			if row['genus.x'] in query_response:
				unique_ids = list(set(query_response[row['genus.x']][6] + api_response))
				query_response[row['genus.x']][6] = unique_ids
			else:
				query_response[row['genus.x']] = [row['genus.x'], row['Genus synonyms'], merged_rows_with_same_genus[row['genus.x']]['Main common name'], \
													merged_rows_with_same_genus[row['genus.x']]['Other common names'], row['Excluded names'], '', api_response]

	return query_response


def create_genus_intersection_common_names_query(row):
	genus = row['genus.x']
	synonyms = [syn for syn in row['Genus synonyms'].split('|') if row['Excluded names']=='' or syn not in (row['Excluded names'].split('|'))]
	common_names = row['Main common name'] if row['Other common names']=="" else row['Main common name'] + '|' + row['Other common names']
	common_names = [name for name in common_names.split('|') if row['Excluded names']=='' or name not in (row['Excluded names'].split('|'))]

	search_query = '("Virus" OR "viruses" OR "viral") AND ('

	if len(common_names)>0:
		for name in common_names:
			search_query += '"' + name + '" OR '
	search_query = search_query[0:-4]
	search_query += ') AND ('

	for genus_syn in synonyms:
		search_query += '"' + genus_syn + '" OR '
	search_query = search_query[0:-4]
	search_query += ')'

	return search_query


def create_genus_union_common_names_query(row):
	genus = row['genus.x']
	synonyms = [syn for syn in row['Genus synonyms'].split('|') if row['Excluded names']=='' or syn not in (row['Excluded names'].split('|'))]
	common_names = row['Main common name'] if row['Other common names']=="" else row['Main common name'] + '|' + row['Other common names']
	common_names = [name for name in common_names.split('|') if row['Excluded names']=='' or name not in (row['Excluded names'].split('|'))]

	search_query = '("Virus" OR "viruses" OR "viral") AND ('

	if len(common_names)>0:
		for name in common_names:
			search_query += '"' + name + '" OR '

	for genus_syn in synonyms:
		search_query += '"' + genus_syn + '" OR '
	search_query = search_query[0:-4]
	search_query += ')'

	return search_query


def decompose_genus_union_common_names_query(row):

	list_of_search_queries = []
	genus = row['genus.x']
	synonyms = [syn for syn in row['Genus synonyms'].split('|') if row['Excluded names']=='' or syn not in (row['Excluded names'].split('|'))]
	common_names = row['Main common name'] if row['Other common names']=="" else row['Main common name'] + '|' + row['Other common names']
	common_names = [name for name in common_names.split('|') if row['Excluded names']=='' or name not in (row['Excluded names'].split('|'))]

	common_search_query = '("Virus" OR "viruses" OR "viral") AND ('

	if len(common_names)>0:
		data_chunks = [common_names[i:i+20] for i in range(0, len(common_names), 20)]
		for names in data_chunks:
			search_query - common_search_query
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


def create_scientific_name_union_common_names_query(row):
	genus = row['genus.x']
	epithet = row['specificEpithet.x']
	genus_synonyms = [syn for syn in row['Genus synonyms'].split('|') if row['Excluded names']=='' or syn not in (row['Excluded names'].split('|'))]
	epithet_synonyms = [syn for syn in row['Epithet synonyms'].split('|') if row['Excluded names']=='' or syn not in (row['Excluded names'].split('|'))]
	common_names = row['Main common name'] if row['Other common names']=="" else row['Main common name'] + '|' + row['Other common names']
	common_names = [name for name in common_names.split('|') if row['Excluded names']=='' or name not in (row['Excluded names'].split('|'))]

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

def decompose_scientific_name_union_common_names_query(row):

	list_of_search_queries = []
	genus = row['genus.x']
	epithet = row['specificEpithet.x']
	genus_synonyms = [syn for syn in row['Genus synonyms'].split('|') if row['Excluded names']=='' or syn not in (row['Excluded names'].split('|'))]
	epithet_synonyms = row['Epithet synonyms'].split('|')
	common_names = row['Main common name'] if row['Other common names']=="" else row['Main common name'] + '|' + row['Other common names']
	common_names = [name for name in common_names.split('|') if row['Excluded names']=='' or name not in (row['Excluded names'].split('|'))]

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

def create_scientific_name_intersection_common_names_query(row):
	genus = row['genus.x']
	epithet = row['specificEpithet.x']
	genus_synonyms = [syn for syn in row['Genus synonyms'].split('|') if row['Excluded names']=='' or syn not in (row['Excluded names'].split('|'))]
	epithet_synonyms = row['Epithet synonyms'].split('|')
	common_names = row['Main common name'] if row['Other common names']=="" else row['Main common name'] + '|' + row['Other common names']
	common_names = [name for name in common_names.split('|') if row['Excluded names']=='' or name not in (row['Excluded names'].split('|'))]

	search_query = '("Virus" OR "viruses" OR "viral") AND ('

	if len(common_names)>0:
		for name in common_names:
			search_query += '"' + name + '" OR '

	for genus_syn in genus_synonyms:
		for epithet_syn in epithet_synonyms:
			search_query +=  '"' + genus_syn + ' ' + epithet_syn + '" OR '

	search_query = search_query[0:-4] + ')'
	return search_query





