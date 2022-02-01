#!/usr/bin/env python3

import requests, os, csv, time, argparse
from query import query_database
from collections import namedtuple
from csv_util import process_csv

if __name__=='__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('--input', default='MDD_v1.6_allSynonyms_NAm_Rodentia.csv', \
						help='name of the input file. The file must be in CSV format and contains the fields to be queried')
	parser.add_argument('--genus_synonyms', default='MDD_genus_syn_8Oct2021_NAmRodentia.csv', \
						help='name of the file containing genus synonyms (CSV format)')
	parser.add_argument('--excluded', default = 'NAm_Rodent_Excluded_Names.csv', help='name of file containing genus/species/common names to be excluded')
	# parser.add_argument('--query-type', choices=['q1', 'q2', 'q3', 'q4', 'q5'], default='q3', help="""Type of search queries to use: 
	# 					q1: genus name, 
	# 					q2: genus name OR genus synonyms, 
	# 					q3: genus name OR genus synonyms or common names, 
	# 					q4: scientific name OR synonyms(combinations of genus and epithet synonyms), 
	# 					q5: scientific name or synonyms or common names""")
	parser.add_argument('--database', default='scopus', help='database to be queried, e.g. "pmc", "pubmed", "scopus", "Google Scholar"')

	args=parser.parse_args()
	input_file = args.input
	genus_syns = args.genus_synonyms
	excluded = args.excluded
	database = args.database
	process_csv(input_file, genus_syns, excluded)

	with open('NAm_Rodent_Lit_Search.csv') as f:
		reader = csv.reader(f)
		SpeciesRecord = namedtuple('SpeciesRecord', next(reader))
		species_records = [SpeciesRecord(*row) for row in reader]
		search_report = query_database(species_records, database)

	with open('NAm_Rodent_Lit_Search_Report.csv', 'w', newline='') as f:
		writer = csv.DictWriter(f, fieldnames=search_report[0]._fields)
		writer.writeheader()

		for item in search_report:
			if database == 'scopus':
				writer.writerow(item._asdict())
			else:
				_out_dict = {key: item._asdict()[key] for key in item._asdict() if key not in ['apiResponse']}
				_out_dict['apiResponse'] = len(item.apiResponse)
				writer.writerow(_out_dict)


