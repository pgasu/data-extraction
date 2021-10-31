#!/usr/bin/env python3

from api_call import pmc_api_search_article_ids, pmc_multiple_api_call

def query_database(list_of_dicts, database):

	query_response = {}
	genus_with_more_than_threshold_results = []

	# Haven't included code for querying multiple databases

	for row in list_of_dicts:
	# If a genus has already been queried, then we let it pass for subsequent rows - the same genus may appear in multiple rows as each row represents a specific species
		if row['genus.x'] in query_response or row['genus.x'] in genus_with_more_than_threshold_results:
			continue

		search_query = create_genus_union_common_names_query(row)
		api_response = pmc_api_search_article_ids(search_query)
		if type(api_response) != list and api_response.status_code == 414:
			list_of_smaller_search_queries = decompose_genus_union_common_names_query(row)
			api_response = pmc_multiple_api_call(list_of_smaller_search_queries)

		if type(api_response)==list and len(api_response)>500:
			genus_with_more_than_threshold_results.append(row['genus.x'])
		else:
			query_response[row['genus.x']] = [row['genus.x'], row['Genus synonyms'], row['Main common name'], row['Other common names'], \
													row['Excluded names'], search_query, api_response]

	for row in list_of_dicts:
		if row['genus.x'] in genus_with_more_than_threshold_results:
			search_query = create_scientific_name_union_common_names_query(row)
			api_response = pmc_api_search_article_ids(search_query)
			if type(api_response) != list and api_response.status_code == 414:
				list_of_smaller_search_queries = decompose_scientific_name_union_common_names_query(row)
				api_response = pmc_multiple_api_call(list_of_smaller_search_queries)

			if row['genus.x'] in query_response:
				query_response[row['genus.x']][6].extend(api_response)
			else:
				query_response[row['genus.x']] = [row['genus.x'], row['Genus synonyms'], row['Main common name'], row['Other common names'], \
													row['Excluded names'], search_query, api_response]

	return query_response


def create_genus_intersection_common_names_query(row):
	genus = row['genus.x']
	synonyms = row['Genus synonyms'].split('|')
	common_names = row['Main common name'] if row['Other common names']=="" else row['Main common name'] + '|' + row['Other common names']
	common_names = [name for name in common_names.split('|') if row['Excluded names']=='' or name not in (row['Excluded names'].split('|'))]

	search_query = '(Virus OR viruses OR viral) AND ('

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
	synonyms = row['Genus synonyms'].split('|')
	common_names = row['Main common name'] if row['Other common names']=="" else row['Main common name'] + '|' + row['Other common names']
	common_names = [name for name in common_names.split('|') if row['Excluded names']=='' or name not in (row['Excluded names'].split('|'))]

	search_query = '(Virus OR viruses OR viral) AND ('

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
	synonyms = row['Genus synonyms'].split('|')
	common_names = row['Main common name'] if row['Other common names']=="" else row['Main common name'] + '|' + row['Other common names']
	common_names = [name for name in common_names.split('|') if row['Excluded names']=='' or name not in (row['Excluded names'].split('|'))]

	common_search_query = '(Virus OR viruses OR viral) AND ('

	if len(common_names)>0:
		search_query - common_search_query
		for name in common_names:
			search_query += '"' + name + '" OR '
		search_query = search_query[0:-4] + ')'
		list_of_search_queries.append(search_query)

	search_query = common_search_query
	for genus_syn in synonyms:
		search_query += '"' + genus_syn + '" OR '
	search_query = search_query[0:-4] + ')'
	list_of_search_queries.append(search_query)

	return list_of_search_queries


def create_scientific_name_union_common_names_query(row):
	genus = row['genus.x']
	epithet = row['specificEpithet.x']
	genus_synonyms = row['Genus synonyms'].split('|')
	epithet_synonyms = row['Epithet synonyms'].split('|')
	common_names = row['Main common name'] if row['Other common names']=="" else row['Main common name'] + '|' + row['Other common names']
	common_names = [name for name in common_names.split('|') if row['Excluded names']=='' or name not in (row['Excluded names'].split('|'))]

	search_query = '(Virus OR viruses OR viral) AND ('

	if len(common_names)>0:
		for name in common_names:
			search_query += '"' + name + '" OR '

	for genus_syn in genus_synonyms:
		search_query += '("' + genus_syn + '" AND ('
		for epithet_syn in epithet_synonyms:
			search_query +=  '"' + epithet_syn + '" OR '
		search_query = search_query[0:-4] + '))' + ' OR '

	search_query = search_query[0:-4]
	search_query += ')'

	return search_query

def decompose_scientific_name_union_common_names_query(row):

	list_of_search_queries = []
	genus = row['genus.x']
	epithet = row['specificEpithet.x']
	genus_synonyms = row['Genus synonyms'].split('|')
	epithet_synonyms = row['Epithet synonyms'].split('|')
	common_names = row['Main common name'] if row['Other common names']=="" else row['Main common name'] + '|' + row['Other common names']
	common_names = [name for name in common_names.split('|') if row['Excluded names']=='' or name not in (row['Excluded names'].split('|'))]

	common_search_query = '(Virus OR viruses OR viral) AND ('

	if len(common_names)>0:
		search_query = common_search_query
		for name in common_names:
			search_query += '"' + name + '" OR '
		search_query = search_query[0:-4] + ')'
		list_of_search_queries.append(search_query)

	for genus_syn in genus_synonyms:
		search_query = common_search_query
		search_query += '"' + genus_syn + '") AND ('
		for epithet_syn in epithet_synonyms:
			search_query +=  '"' + epithet_syn + '" OR '
		search_query = search_query[0:-4] + ')'
		list_of_search_queries.append(search_query)

	return list_of_search_queries





