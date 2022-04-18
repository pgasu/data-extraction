#!/usr/bin/env python3

import requests, sys
from requests.exceptions import ConnectionError, RequestException
from json import JSONDecodeError
from pybliometrics.scopus import ScopusSearch
from pybliometrics.scopus.exception import ScopusQueryError, Scopus413Error, Scopus414Error, Scopus400Error, ScopusException

ncbi_api_key = ''
scopus_api_key = ''

def search_database(search_query, db):
	if db=='scopus':
		response = search_scopus_articles(search_query)
	else:
		response = search_ncbi_articles(search_query, db)
	return response

def search_ncbi_articles(search_query, db):
	parameters = {
		'tool':'Data_extraction/0.1.0',
		'email':'pgupt109@asu.edu',
		'api_key':ncbi_api_key,
		'db': db,
		'term': search_query,
		'retmax':100000,
		'retmode':'json',
		}
	try:
		response = requests.post('https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi', params=parameters)
		return response
	except JSONDecodeError as e:
		raise SystemExit(e)
	except ConnectionError as e:
		raise SystemExit(e)
	except RequestException as e:
		raise SystemExit(e)

def get_ncbi_citation(id_list, db):
	headers = {
		'tool':'Data_extraction/0.1.0',
		'email':'pgupt109@asu.edu',
		}
	params = {
		'id': id_list,
		'download':'Y',
		'format':'ris',
		}
	try:
		response = requests.get(f'https://api.ncbi.nlm.nih.gov/lit/ctxp/v1/{db}', params=params, headers=headers)
		if response.status_code != 200:
			print(f'{response}')
			sys.exit()
		return response.content
	except ConnectionError as e:
		print(e)
		return False

def search_scopus_articles(search_query):

	param1 = {
		'apiKey':scopus_api_key,
		'view': 'COMPLETE',
		'query': search_query,
		'download': False,
		'subscriber': True,
	}
	param2 = {
		'apiKey':scopus_api_key,
		'view': 'COMPLETE',
		'query': search_query,
		'subscriber': True,
	}
	try:
		api_response = ScopusSearch(**param1)
		if api_response.get_results_size() > 500 or api_response.get_results_size()==0:
			return api_response.get_results_size()
		else:
			api_response = ScopusSearch(**param2)
			return api_response.results
	except ScopusQueryError as e:
		print(f'Scopus query error - {e}')
		return False
	except (Scopus413Error, Scopus414Error, Scopus400Error) as e:
		print(e)
		return False
	except ScopusException as e:
		print("in api call")
		print(search_query)
		print(e)
		return e
