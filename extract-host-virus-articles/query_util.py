#!/usr/bin/env python3

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





