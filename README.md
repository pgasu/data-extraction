# data-extraction

## Overview
This Python script search research articles with coocurrence of a virus and any of the 70 genera of North American rodents. The script incorporates searching the following databases: Pubmed Central (pmc), Pubmed, Scopus and Google Scholar. The search algorithm employs various names (genus name, scientific name - genus + epithet, common name, genus synonyms, epithet synonyms) to build different variations of search queries for different databases. To restrict the number of resulting articles, I have used a threshold limit (=500). If a query results in articles more than the threshold limit, the query is restricted using various approaches to bring the numbers below the threshold limit. The script results in a RIS-format citation file for the resulting articles and a report detailing the search results for each individual genus. 

## Query-building


