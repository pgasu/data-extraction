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