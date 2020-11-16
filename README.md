# Dataset
Using the KDD Cup 2003 dataset, it contains roughly 30,000 research papers from the arXiv. I will be using abstract and citation graph, the abstract dataset contains metadata related to an research paper. The abstract metadata we will utilize will be title, author names, and date.
## Data.py
It contains Data class that will download, extract and create csv file. The csv file will contain research paper title, date and authors mapping to citiation paper title, date and authors.
```python
    from data import Data

    # Download the dataset
    Data().getDataset()
    # Converting the dataset into CSV file
    Data().getDataInCsv()
```