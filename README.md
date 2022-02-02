# data-extraction

## Overview
This Python script search research articles with coocurrence of a virus and any of the 70 genera of North American rodents. The script incorporates searching the following databases: Pubmed Central (pmc), Pubmed, Scopus and Google Scholar. The search algorithm employs various names (genus name, scientific name - genus + epithet, common name, genus synonyms, epithet synonyms) to build different variations of search queries for different databases. To restrict the number of resulting articles, I have used a threshold limit (=500). If a query results in articles more than the threshold limit, the query is restricted using various approaches to bring the numbers below the threshold limit. The script results in a RIS-format citation file for the resulting articles and a report detailing the search results for each individual genus. 

## Input data files
The following input files are used to extract information about North American rodents to build search queries, which are stored in the 'data' folder:
- **MDD_v1.6_allSynonyms_NAm_Rodentia.csv** The file contains the details of the 70 genera of North American rodents, including species names for each genera, their synonyms, and common names. 
- **MDD_genus_syn_8Oct2021_NAmRodentia.csv** The file contains the synonyms for the 70 genera of North American rodents.

## Query-building
Each database use their own custom unique formats and techniques to build search queries. Here, I will explain the general approach we have taken to build search queries for each database. The general format of the query is: **(virus or viruses or viral) AND (X1 OR X2 OR X3 OR ...)** where X1, X2, X3... represent genus names, scientific names, genus synonyms, scientific names with epithet synonyms, and common names.

### Pubmed Central (pmc) and Pubmed
For pmc and Pubmed, the initial scope of search queries is '_All Fields_', and the search terms (X1, X2, X3...) use genus names, genus synonyms and common names. If the search query results in more than 500 articles (i.e. threshold limit), we restrain search queries by (i) restricting the scope to '_Title/Abstract_', or (ii) restricting search terms by replacing genus name with scientific name (using a combination of genus and epithet synonyms). 

### Scopus
For Scopus database, the scope of search queries is set to '_Title/Abstract/Keywords_'. We use the same approach as in pmc/pubmed for search terms - initially, genus names, genus synonyms and common names are used, but if the search results exceed threshold limit, genus names are replaced by scientific names.




