#!/usr/bin/env python3

import requests
from requests.exceptions import ConnectionError
from json import JSONDecodeError

api_key = '310a232c07175b642551785374fdecd7e508'

def pmc_api_search_article_ids(search_query):
	parameters = {
		'tool':'Data_extraction/0.1.0',
		'email':'pgupt109@asu.edu',
		'api_key':api_key,
		'db': 'pubmed',
		'term': search_query,
		'retmax':100000,
		'retmode':'json'	
		}

	try:
		response = requests.post('https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi', params=parameters)
		if response.status_code == 414:
			return response
		response_id_list = [int(idx) for idx in response.json()['esearchresult']['idlist']]
		return list(set(response_id_list))
	except JSONDecodeError as e:
		print(e)
		return ("Error: JSONDecodeError")


def pmc_multiple_api_call(search_query_list):

	response_id_list = []

	for search_query in search_query_list:

		parameters = {
			'tool':'Data_extraction/0.1.0',
			'email':'pgupt109@asu.edu',
			'api_key':api_key,
			'db': 'pubmed',
			'term': search_query,
			'retmax':100000,
			'retmode':'json'	
			}

		try:
			response = requests.post('https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi', params=parameters)
			response_id_list.extend([int(idx) for idx in response.json()['esearchresult']['idlist']])
		except JSONDecodeError as e:
			print(e)
		except requests.exceptions.RequestException as e:
			raise SystemExit(e)

	return list(set(response_id_list))

def scopus_api_search_article_ids(search_query):
	print(search_query)
	parameters = {
		'apiKey':'a4a02608fd7272ed2b8312efad849197',
		'httpAccept':'application/json',
		'query': search_query,
		}

	try:
		response = requests.get('https://api.elsevier.com/content/search/scopus', params=parameters)
		if response.status_code == 414:
			return response
		print(response.content)
		# response_id_list = [int(idx) for idx in response.json()['esearchresult']['idlist']]
		# return list(set(response_id_list))
	except JSONDecodeError as e:
		print(e)
		return ("Error: JSONDecodeError")

