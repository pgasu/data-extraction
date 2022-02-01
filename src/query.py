#!/usr/bin/env python3
import math, copy, ssl, sys
from api_call import search_database, get_ncbi_citation
from scholarly import scholarly, ProxyGenerator
from fp.fp import FreeProxy
from itertools import product
from collections import namedtuple
from requests.exceptions import ConnectionError

# q1 - genus union common names query
# q2 - scientific name union common names query

def query_database(species_records, database):
	GenusRecord = namedtuple('GenusRecord', 'genus, genusSynonym, mainCommonName, otherCommonName, excludedName')
	genus_records = []

# By default, we aim to query a database for each genus without species details (specificEpithet or epithetSynonym), 
# so we lump the input species_records and create genus-level records
	for record in species_records:
		idx = record_exists(genus_records, record.genus)
		if not idx:
			_dict = record._asdict()
			genus_records.append(GenusRecord(**{key: _dict[key] for key in _dict if key not in ['specificEpithet', 'epithetSynonym']}))
		else:
			mcn = genus_records[idx].mainCommonName if record.mainCommonName == '' else f'{genus_records[idx].mainCommonName}|{record.mainCommonName}'
			ocn = genus_records[idx].otherCommonName if record.otherCommonName == '' else f'{genus_records[idx].otherCommonName}|{record.otherCommonName}'
			exn = genus_records[idx].excludedName if record.excludedName == '' else f'{genus_records[idx].excludedName}|{record.excludedName}'
			new_record = genus_records[idx]._replace(mainCommonName=mcn, otherCommonName=ocn, excludedName=exn)
			genus_records.append(new_record)
			genus_records.pop(idx)

	genus_gt_threshold = [] # list of genera whose queries result in number of articles greater than the threshold limit (500)
	QueryResponse = namedtuple('QueryResponse', 'genus, genusSynonym, specificEpithet, epithetSynonym, mainCommonName, \
						otherCommonName, excludedName, searchQuery, apiResponse')
	response_report = []	# list of QueryResponse - search report for genus-level queries, followed by species-level queries if the initial search is too broad

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
				success = pg.ScraperAPI('86ec6c6fd7438f17779375e71b20810b')
				# proxy = FreeProxy(rand=True, timeout=1, country_id=['US']).get()
				# print(proxy)
				# pg.SingleProxy(http =proxy, https =proxy)

				# success = pg.Luminati(usr = "lum-customer-hl_1f0a2d53-zone-unblocker", passwd="akv76bfl6rbd", proxy_port=22225) #ScraperAPI(API_KEY ='86ec6c6fd7438f17779375e71b20810b')
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

		for row in species_records:
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

	elif database == 'scopus':
		scopus_documents = []
		for record in genus_records:
			search_queries = create_scopus_q1(record)
			response_length = 0
			response_list = []
			for query in search_queries:
				api_response = search_database(query, database)
				if type(api_response) == list:
					response_list.extend(api_response)
					response_length += len(api_response)
				elif type(api_response) == int:
					response_length += api_response
				elif api_response == False:
					sys.exit('one of the other errors')
				else:
					sys.exit('Unexpected response from scopus API call')
						
			if response_length > 500:
				genus_gt_threshold.append(record.genus)
			else:
				scopus_documents.extend(response_list)
				response_report.append(QueryResponse(specificEpithet='',epithetSynonym='',searchQuery="|".join(search_queries),\
														apiResponse=response_length, **record._asdict()))

		print(genus_gt_threshold)

		species_response_report = {}
		for record in species_records:
			if record.genus in genus_gt_threshold:
				search_queries = create_scopus_q2(record)
				response_length = 0
				response_list = []
				for query in search_queries:
					api_response = search_database(query, database)
					if type(api_response) == list:
						response_list.extend(api_response)
						response_length += len(api_response)
					elif type(api_response) == int:
						response_length += api_response
					elif api_response == False:
						sys.exit('one of the other errors')
					else:
						sys.exit('Unexpected response from scopus API call')

				if record.genus not in species_response_report:
					species_response_report[record.genus] = [response_list, QueryResponse(searchQuery="|".join(search_queries), \
																apiResponse=response_length, **record._asdict())]
				else:
					if response_list:
						species_response_report[record.genus][0] = list(set(species_response_report[record.genus][0] + response_list))
					updated_length = len(species_response_report[record.genus][0])
					sq = f'{species_response_report[record.genus][1].searchQuery}|{"|".join(search_queries)}'
					se = f'{species_response_report[record.genus][1].specificEpithet}|{record.specificEpithet}'
					es = f'{species_response_report[record.genus][1].epithetSynonym}|{record.epithetSynonym}'
					new_record = species_response_report[record.genus][1]._replace(specificEpithet=se, epithetSynonym=es, apiResponse=updated_length, searchQuery=sq)
					species_response_report[record.genus].pop(1)
					species_response_report[record.genus].append(new_record)

		print(len(species_response_report))
		for item in species_response_report.items():
			if item[1][1].apiResponse < 500:
				print('many docs')
				scopus_documents.extend(item[1][0])
			response_report.append(item[1][1])

		generate_scopus_citations(list(set(scopus_documents)))

	elif database in ['pmc', 'pubmed']:
		troublesome_terms = []
		print("round 1")
		for record in genus_records:
			output_articles_ids = []	# list of resulting articles' ids for a genus record
			search_queries = create_q1(record, database)
			for query in search_queries:
				api_response = search_database(query, database)
				if api_response.status_code == 200:
					output = [int(idx) for idx in api_response.json()['esearchresult']['idlist']]
					if database=='pmc' and len(output) > 200:
						new_terms = find_troublesome_terms(query, database)
						if new_terms and not all(term in troublesome_terms for term in new_terms):
							troublesome_terms.extend(new_terms)
							troublesome_terms = list(set(troublesome_terms))
							for term in troublesome_terms:
								query = query.replace(f'"{term}"[Body - Key Terms]', f'"{term}"[Title]')
							api_response = search_database(query, database)
							if api_response.status_code == 200:
								output_articles_ids.extend([int(idx) for idx in api_response.json()['esearchresult']['idlist']])
							else:
								print(f'{record.genus} - {api_response.status_code}')
								sys.exit()
						else:
							output_articles_ids.extend(output)
					elif database=='pubmed' and len(output) > 500:
						new_terms = find_troublesome_terms(query, database)
						troublesome_terms.extend(new_terms)
						troublesome_terms = list(set(troublesome_terms))
						output_articles_ids.extend(output)
					else:
						output_articles_ids.extend(output)
				else:
					print(f'{record.genus} - {api_response.status_code}')
					print(f'{query}')
					sys.exit()
			output_articles_ids = list(set(output_articles_ids))
			if len(output_articles_ids) > 500:
				genus_gt_threshold.append(record.genus)
			else:
				response_report.append(QueryResponse(specificEpithet='',epithetSynonym='',searchQuery="|".join(search_queries),\
									apiResponse=output_articles_ids, **record._asdict()))

		print(f'Genus resulting articles more than threshold values: {genus_gt_threshold}')
		print(f'Troublesome terms causing high volume of articles: {troublesome_terms}')
		print("round 2")
		for record in genus_records:
			if record.genus in genus_gt_threshold:
				output_articles_ids = []
				search_queries = create_q1(record, database, troublesome_terms)
				for query in search_queries:
					api_response = search_database(query, database)
					if api_response.status_code == 200:
						output = [int(idx) for idx in api_response.json()['esearchresult']['idlist']]
						output_articles_ids.extend(output)
					else:
						print(f'{record.genus} - {api_response.status_code}')
						print(f'{query}')
						sys.exit()
				output_articles_ids = list(set(output_articles_ids))
				if len(output_articles_ids) <= 500:
					genus_gt_threshold.remove(record.genus)
					response_report.append(QueryResponse(specificEpithet='',epithetSynonym='',searchQuery="|".join(search_queries),\
										apiResponse=output_articles_ids, **record._asdict()))
		
		print(f'Genus resulting articles more than threshold values after round 2: {genus_gt_threshold}')
		for record in species_records:
			if record.genus in genus_gt_threshold:
				output_articles_ids = []
				search_queries = create_q2(record, database, troublesome_terms)
				for query in search_queries:
					api_response = search_database(query, database)
					if api_response.status_code == 200:
						output = [int(idx) for idx in api_response.json()['esearchresult']['idlist']]
						if database=='pmc' and len(output) > 200:
							print("I am in")
							print(record.genus)
							print(troublesome_terms)
							print()
							new_terms = find_troublesome_terms(query, database)
							if new_terms and not all(term in troublesome_terms for term in new_terms):
								troublesome_terms.extend(new_terms)
								troublesome_terms = list(set(troublesome_terms))
								for term in troublesome_terms:
									query = query.replace(f'"{term}"[Body - Key Terms]', f'"{term}"[Title]')
								api_response = search_database(query, database)
								if api_response.status_code == 200:
									output_articles_ids.extend([int(idx) for idx in api_response.json()['esearchresult']['idlist']])
								else:
									print(f'{record.genus} - {api_response.status_code}')
									sys.exit()
							else:
								output_articles_ids.extend(output)
						elif database=='pubmed' and len(output) > 500:
							new_terms = find_troublesome_terms(query, database)
							troublesome_terms.extend(new_terms)
							troublesome_terms = list(set(troublesome_terms))
							for term in troublesome_terms:
								query = query.replace(f'"{term}"[Title/Abstract] OR ', '')
								if query.endswith(f'"{term}"[Title/Abstract]'):
									query = query.replace(f'"{term}"[Title/Abstract]', '')
							api_response = search_database(query, database)
							if api_response.status_code == 200:
								output_articles_ids.extend([int(idx) for idx in api_response.json()['esearchresult']['idlist']])
							else:
								print(f'{record.genus} - {api_response.status_code}')
								sys.exit()
						else:
							output_articles_ids.extend(output)
					else:
						print(f'{record.genus} - {api_response.status_code}')
						sys.exit()

				idx = record_exists(response_report, record.genus)
				if not idx:
					response_report.append(QueryResponse(searchQuery="|".join(search_queries), apiResponse=output_articles_ids, **record._asdict()))
				else:
					unique_ids = list(set(response_report[idx].apiResponse + output_articles_ids))
					sq = f'{response_report[idx].searchQuery}|{"|".join(search_queries)}'
					se = f'{response_report[idx].specificEpithet}|{record.specificEpithet}'
					es = f'{response_report[idx].epithetSynonym}|{record.epithetSynonym}'
					new_record = response_report[idx]._replace(specificEpithet=se, epithetSynonym=es, apiResponse=unique_ids, searchQuery=sq)
					response_report.append(new_record)
					response_report.pop(idx)

		print(f'Troublesome terms causing high volume of articles after round 3: {troublesome_terms}')
		generate_citation_file(response_report, database)

	else:
		sys.exit(f'Database {database} search not yet supported')

	return response_report

def create_q1(record, database, troublesome_terms=[]):
	search_queries = []
	synonyms = list(set(record.genusSynonym.split('|') + [record.genus]))
	common_names = f'{record.mainCommonName}|{record.otherCommonName}' if record.otherCommonName else record.mainCommonName
	common_names = list(set(common_names.split('|')))
	search_terms = synonyms + common_names
	search_query = '(Virus OR viruses OR viral) AND ('

	if database == 'pubmed':
		for name in search_terms:
			if name not in troublesome_terms:
				if len(search_query + f'"{name}"[Title/Abstract] OR ') > 3000:
					search_queries.append(f'{search_query[:-4]})')
					search_query = f'(Virus OR viruses OR viral) AND ("{name}"[Title/Abstract] OR '
				else:
					search_query += f'"{name}"[Title/Abstract] OR '
	elif database=='pmc':
		for name in search_terms:
			if name in troublesome_terms:
				if len(search_query + f'"{name}"[Abstract] OR "{name}"[Title] OR ') > 3000:
					search_queries.append(f'{search_query[:-4]})')
					search_query = f'(Virus OR viruses OR viral) AND ("{name}"[Abstract] OR "{name}"[Title] OR '
				else:
					search_query += f'"{name}"[Abstract] OR "{name}"[Title] OR '
			else:
				if len(search_query + f'"{name}"[Abstract] OR "{name}"[Body - Key Terms] OR ') > 3000:
					search_queries.append(f'{search_query[:-4]})')
					search_query = f'(Virus OR viruses OR viral) AND ("{name}"[Abstract] OR "{name}"[Body - Key Terms] OR '
				else:
					search_query += f'"{name}"[Abstract] OR "{name}"[Body - Key Terms] OR '

	search_queries.append(f'{search_query[:-4]})')
	return search_queries

def create_scopus_q1(record, troublesome_terms=[]):
	search_queries = []
	synonyms = list(set(record.genusSynonym.split('|') + [record.genus]))
	common_names = f'{record.mainCommonName}|{record.otherCommonName}' if record.otherCommonName else record.mainCommonName
	common_names = list(set(common_names.split('|')))
	search_terms = synonyms + common_names
	search_terms = [i for i in search_terms if i]
	search_query = 'TITLE-ABS-KEY(virus OR viruses OR viral AND '

	for name in search_terms:
		if len(search_query + f'{{{name}}} OR ') > 1000:
			search_queries.append(f'{search_query[:-4]})')
			search_query = f'TITLE-ABS-KEY(virus OR viruses OR viral AND {{{name}}} OR '
		else:
			search_query += f'{{{name}}} OR '

	search_queries.append(f'{search_query[:-4]})')
	return search_queries

def create_scopus_q2(record, troublesome_terms=[]):
	search_queries = []
	genus_synonyms = list(set(record.genusSynonym.split('|') + [record.genus]))
	epithet_synonyms = list(set(record.epithetSynonym.split('|') + [record.specificEpithet]))
	scientific_names = [f'{genus} {epithet}' for genus, epithet in product(genus_synonyms, epithet_synonyms)]
	common_names = f'{record.mainCommonName}|{record.otherCommonName}' if record.otherCommonName else record.mainCommonName
	common_names = list(set(common_names.split('|')))
	search_terms = scientific_names + common_names
	search_terms = [i for i in search_terms if i]
	search_query = 'TITLE-ABS-KEY(virus OR viruses OR viral AND '

	for name in search_terms:
		if len(search_query + f'{{{name}}} OR ') > 1000:
			search_queries.append(f'{search_query[:-4]})')
			search_query = f'TITLE-ABS-KEY(virus OR viruses OR viral AND {{{name}}} OR '
		else:
			search_query += f'{{{name}}} OR '

	search_queries.append(f'{search_query[:-4]})')
	return search_queries

def create_q2(record, database, troublesome_terms=[]):
	search_queries = []
	genus_synonyms = list(set(record.genusSynonym.split('|') + [record.genus]))
	epithet_synonyms = list(set(record.epithetSynonym.split('|') + [record.specificEpithet]))
	scientific_names = [f'{genus} {epithet}' for genus, epithet in product(genus_synonyms, epithet_synonyms)]
	common_names = f'{record.mainCommonName}|{record.otherCommonName}' if record.otherCommonName else record.mainCommonName
	common_names = list(set(common_names.split('|')))
	search_terms = scientific_names + common_names
	search_query = '(Virus OR viruses OR viral) AND ('

	if database == 'pubmed':
		for name in search_terms:
			if len(search_query + f'"{name}"[Title/Abstract] OR ') > 3000:
				search_queries.append(f'{search_query[:-4]})')
				search_query = f'(Virus OR viruses OR viral) AND ("{name}"[Title/Abstract] OR '
			else:
				search_query += f'"{name}"[Title/Abstract] OR '
	elif database=='pmc':
		for name in search_terms:
			if name in troublesome_terms:
				if len(search_query + f'"{name}"[Abstract] OR "{name}"[Title] OR ') > 3000:
					search_queries.append(f'{search_query[:-4]})')
					search_query = f'(Virus OR viruses OR viral) AND ("{name}"[Abstract] OR "{name}"[Title] OR '
				else:
					search_query += f'"{name}"[Abstract] OR "{name}"[Title] OR '
			else:
				if len(search_query + f'"{name}"[Abstract] OR "{name}"[Body - Key Terms] OR ') > 3000:
					search_queries.append(f'{search_query[:-4]})')
					search_query = f'(Virus OR viruses OR viral) AND ("{name}"[Abstract] OR "{name}"[Body - Key Terms] OR '
				else:
					search_query += f'"{name}"[Abstract] OR "{name}"[Body - Key Terms] OR '

	search_queries.append(f'{search_query[:-4]})')

	return search_queries

# def create_q2(record, database, troublesome_terms=[]):
# 	search_queries = []
# 	excluded_names = record.excludedName.split('|')
# 	genus_synonyms = list(set([syn for syn in record.genusSynonym.split('|') if syn not in excluded_names] + [record.genus]))
# 	epithet_synonyms = list(set([syn for syn in record.epithetSynonym.split('|') if syn not in excluded_names] + [record.specificEpithet]))
# 	scientific_names = [f'{genus} {epithet}' for genus, epithet in product(genus_synonyms, epithet_synonyms) if f'{genus} {epithet}' not in excluded_names]
# 	common_names = f'{record.mainCommonName}|{record.otherCommonName}' if record.otherCommonName else record.mainCommonName
# 	common_names = [name for name in common_names.split('|') if name not in excluded_names]
# 	options = scientific_names + common_names
# 	search_query = '(Virus OR viruses OR viral) AND ('

# 	if database == 'pubmed':
# 		for name in options:
# 			if len(search_query + f'"{name}"[Title/Abstract] OR ') > 3000:
# 				search_queries.append(f'{search_query[:-4]})')
# 				search_query = f'(Virus OR viruses OR viral) AND ("{name}"[Title/Abstract] OR '
# 			else:
# 				search_query += f'"{name}"[Title/Abstract] OR '
# 	else:
# 		for name in options:
# 			if name in troublesome_terms:
# 				if len(search_query + f'"{name}"[Abstract] OR "{name}"[Title] OR ') > 3000:
# 					search_queries.append(f'{search_query[:-4]})')
# 					search_query = f'(Virus OR viruses OR viral) AND ("{name}"[Abstract] OR "{name}"[Title] OR '
# 				else:
# 					search_query += f'"{name}"[Abstract] OR "{name}"[Title] OR '
# 			else:
# 				if len(search_query + f'"{name}"[Abstract] OR "{name}"[Body - Key Terms] OR ') > 3000:
# 					search_queries.append(f'{search_query[:-4]})')
# 					search_query = f'(Virus OR viruses OR viral) AND ("{name}"[Abstract] OR "{name}"[Body - Key Terms] OR '
# 				else:
# 					search_query += f'"{name}"[Abstract] OR "{name}"[Body - Key Terms] OR '

# 	search_queries.append(f'{search_query[:-4]})')

# 	return search_queries

def create_google_scholar_q1(row):
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

	return list_of_search_queries

def find_troublesome_terms(query, database):
	troublesome_tms = []
	query_terms = list(set(query.split('"')[1::2]))
	if '' in query_terms: query_terms.remove('')

	for each_term in query_terms:
		if database == 'pmc':
			search_query = f'(Virus OR viruses OR viral) AND ("{each_term}"[Abstract] OR "{each_term}"[Body - Key Terms]'
		else:
			search_query = f'(Virus OR viruses OR viral) AND ("{each_term}"[Title/Abstract]'
		api_response = search_database(search_query, database)
		if api_response.status_code == 200:
			output = [int(idx) for idx in api_response.json()['esearchresult']['idlist']]
			if len(output) > 200: troublesome_tms.append(each_term)
	return troublesome_tms

def record_exists(list_of_named_tuples, value):
	for index, named_tuple in enumerate(list_of_named_tuples):
		if value in named_tuple:
			return index
	return False

def generate_citation_file(response_report, db):
	unique_ids = set()
	for item in response_report:
		if len(item.apiResponse) < 500: unique_ids.update(item.apiResponse)
	unique_ids = list(unique_ids)
	print(len(unique_ids))

	with open(f'{db}_citations.ris', 'ab+') as citations_file:
		count = 0
		while True:
			missed_keys = False
			# print(len(unique_ids))
			for i in range(count, len(unique_ids), 25):
				# print(i, i+25)
				id_list = unique_ids[i:i+25]
				response = get_ncbi_citation(id_list, db)
				if not response:
					missed_keys = True
					count=i
					break
				else:
					citations_file.write(response)

			if missed_keys == False: break

def generate_scopus_citations(documents):

	with open('scopus_citations.ris', 'a+') as citations_file:
		print(len(documents))
		for item in documents:
			title = item.title
			doi = item.doi
			issn = item.issn
			aggregationType = item.aggregationType
			issueIdentifier = item.issueIdentifier
			description = item.description
			authkeywords = item.authkeywords
			publicationName = item.publicationName
			volume = item.volume
			pageRange = item.pageRange
			coverDate = item.coverDate

			ris = f"TY  - {aggregationType}\nTI  - {title}\nJF  - {publicationName}\n"\
	              f"VL  - {volume}\nIS  - {issueIdentifier}\nDA  - {coverDate}\n"\
	              f"PY  - {coverDate[0:4]}\nAB  - {description}\n"
			
			if pageRange:
				if '-' in pageRange:
					ris += f"SP  - {pageRange.split('-')[0]}\nEP  - {pageRange.split('-')[1]}\n"
				else:
					ris += f'SP  - {pageRange}\n'

			if item.author_names:
				for au in item.author_names.split(';'):
					ris += f'AU  - {au}\n'
	        # DOI
			if doi:
				ris += f'DO  - {doi}\n'
	        # Issue
			if issn:
				ris += f'SN  - {issn}\n'
	        # Keywords
			if authkeywords:
				for keyword in authkeywords.split(' | '):
					ris += f'KW  - {keyword}\n'
			ris += 'ER  - \n\n'

			if not title or not doi:
				print(ris)
				print()

			citations_file.write(ris)