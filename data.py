import tarfile
import os
import requests
import re
import json
import pandas as pd
import numpy as np
from tqdm import tqdm

class Data():
    def download(self):
        """
            Download the data into Dataset folder. 
            Dataset folder will be created in the current dir.
            I will be using KDD Cup 2003's Arxiv dataset.
        """
        # Citation Graph
        fname = 'hep-th-citations.tar.gz'
        r = requests.get('http://www.cs.cornell.edu/projects/kddcup/download/' + fname)
        open(fname , 'wb').write(r.content)
        # Abstract which contains metadata like Title, Author, Date, and Journal
        fname = 'hep-th-abs.tar.gz'
        r = requests.get('http://www.cs.cornell.edu/projects/kddcup/download/' + fname)
        open(fname , 'wb').write(r.content)

    def extract(self):
        """
            Extract citation.tar.gz into Dataset folder.
            Extract abs.tar.gz into Dataset folder.
        """
        tar = tarfile.open("./hep-th-citations.tar.gz")
        tar.extractall("./Dataset")
        tar.close()
        tar = tarfile.open("./hep-th-abs.tar.gz")
        tar.extractall("./Dataset/abs")
        tar.close()
    
    def getDataset(self):
        """
            Utilize the above two functions to download and extract the dataset.
            Delete the .tar.gz files.
        """
        print('Downloading...')
        self.download()
        print('Extracting...')
        self.extract()
        os.remove("./hep-th-citations.tar.gz")
        os.remove("./hep-th-abs.tar.gz")

    def getDataInCsv(self):
        """
            The extracted dataset is then used to create a csv file which maps x to y.
            X is a research paper, y is the citations of that research paper.
            In x we have included the Title of the research paper, date and author of the research paper.
            In y we have included the Title of the cited paper, date and authors of the cited paper.
        """
        CITATIONS = "./Dataset/hep-th-citations"
        ADDRESS = "./Dataset/abs"
        ADDRESS = [ADDRESS + '/' + date for date in os.listdir(ADDRESS)]
        MAIN = {}

        # Check if data.txt exists or not
        if(os.path.isfile('./Dataset/data.txt') == False):
            for date in ADDRESS:
                progressBar = tqdm(os.listdir(date))
                for f in progressBar:
                    progressBar.set_description(f"Currently processing: {date.split('/')[-1]}")
                    filename = f.split('.')[0] # 100100.abs = ['100100', 'abs']
                    f = open(date + '/' + f) # Open the file
                    LOCAL_MAIN = {}
                    for line in f.readlines(): # Read lines from the file
                        firstWord = line.split(' ')[0]
                        if(firstWord == "Title:"):
                            # The line = 'Title: some title\n' and we remove substring 'Title: ' and '\n' from it
                            title = line[len("Title: "): len(line) - 1]
                            LOCAL_MAIN['TITLE'] = title
                        elif(firstWord == "Authors:" or firstWord == "Author:"):
                            # We do not want Organization details for now, the main reason behind this is because the organization detail
                            # is absent from a lot of papers in the dataset

                            # Observed: 1) The organization details are provided between '(' and ')'
                            # 2) Authors names separators used are: "," or "and" or combination of both.

                            # Removing organization details using Regular Expression
                            line = re.sub('\([A-z0-9]*\)', "", line).strip()
                            # Get list of authors
                            li = []
                            if(firstWord == "Authors:"):
                                line = line[len("Authors: "):]
                            else:
                                line = line[len("Author: "):]
                            authors = line.split("and") # Split with "and", it will split in two parts
                            # If only 1 author then split on and will give us array with only 1 element
                            if(len(authors) != 1):
                                # More than 1 author
                                li.append(authors[1])
                                # Split with ","
                                authors = authors[0].split(",")
                            # Merge the lists
                            li.extend(authors)
                            # Found that author strings might have trailing whitespaces 
                            li = [i.strip() for i in li]
                            LOCAL_MAIN['AUTHORS'] = li
                        elif(firstWord == "Date:"):
                            line = line[len("Date: "):]
                            line = line.split('(')[0].strip()
                            LOCAL_MAIN['DATE'] = line
                    MAIN[filename] = LOCAL_MAIN
            # Save in file for future use
            with open("./Dataset/data.txt", 'w') as outfile:
                json.dump(MAIN, outfile)
        else:
            # Assign MAIN to the data.txt JSON
            with open("./Dataset/data.txt", 'r') as readfile:
                MAIN = json.load(readfile)

        ###===============================================================================================###
        
        citationGraph = pd.read_table(CITATIONS)
        citationGraph.columns = [' ']
        citationGraph = citationGraph.to_numpy()
        # citationGraph[0][0] = '0001001 9308122'
        # Split with space, first string is the paper and second string is the citation
        # Take two list and append into it the two strings in order
        paper = []
        cited = []
        progressBar = tqdm(citationGraph) 
        for row in progressBar:
            progressBar.set_description('Parsing citation graph...')
            row = row[0].split(' ')
            p = row[0]
            c = row[1]
            paper.append(p)
            cited.append(c)

        paper_title = []
        paper_authors = []
        paper_date = []
        cited_title = []
        cited_authors = []
        cited_date = []
        progressBar = tqdm(paper)
        for i, _ in enumerate(progressBar):
            progressBar.set_description('Creating data.csv...')
            # Get the Research Paper using the key
            paper_title.append(MAIN[paper[i]]['TITLE'])
            paper_authors.append(','.join(MAIN[paper[i]]['AUTHORS']))
            paper_date.append(MAIN[paper[i]]['DATE'])
            # Get the cited Paper using key
            cited_title.append(MAIN[cited[i]]['TITLE'])
            cited_authors.append(','.join(MAIN[cited[i]]['AUTHORS']))
            cited_date.append(MAIN[cited[i]]['DATE'])
        # Convert into PD and save it as csv
        FINAL = {'Paper-title': paper_title, 'Paper-authors': paper_authors, 'Paper-date': paper_date, 'Cited-title': cited_title, 'Cited-authors' : cited_authors, 'Cited-date': cited_date}
        pd.DataFrame(FINAL).to_csv('data.csv')