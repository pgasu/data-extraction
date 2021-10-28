#!/usr/bin/env python3

api_key = '310a232c07175b642551785374fdecd7e508'

def pmc_api_search_article_ids(search_query):

	parameters = {
		'tool':'Data_extraction/0.1.0',
		'email':'pgupt109@asu.edu',
		'api_key':api_key,
		'db': 'pmc',
		'term': search_query,
		'retmax':100000,
		'retmode':'json'	
		}

	try:
		response = requests.post('https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi', params=parameters)
		response_id_list = [int(idx) for idx in response.json()['esearchresult']['idlist']]
		return response_id_list
	except JSONDecodeError as e:
		return ("Error: " + e)