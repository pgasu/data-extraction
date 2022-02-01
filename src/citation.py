#!/usr/bin/env python3

import argparse

if __name__=='__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('--inputfile1', default='scopus_citations.ris')
	parser.add_argument('--inputfile2', default='pubmed_citations.ris')
	parser.add_argument('--inputfile3', default='pmc_citations.ris')

	args=parser.parse_args()
	input_file1 = args.inputfile1
	input_file2 = args.inputfile2
	input_file3 = args.inputfile3

	with open(input_file1) as file1, open(input_file2) as file2, open(input_file3) as file3:
		lines1 = file1.readlines()
		lines2 = file2.readlines()
		lines3 = file3.readlines()
		file1_articles=[]


		for line in lines1:
			if 'TI  - ' in line:
				file1_articles.append(line[6:])
		file1_articles = list(set(file1_articles))
		print(len(file1_articles))

		count = 0
		common = []
		for line in lines2:
			if 'T1  - ' in line:
				if line[6:] in file1_articles:
					count +=1
					common.append(line[6:])

		file3_articles = []
		for line in lines3:
			if 'T1  - ' in line:
				file3_articles.append(line[6:])
		print(len(file3_articles))

		final_common = 0
		for x in common:
			if x in file3_articles:
				final_common =+1

		print(count)
		print(final_common)