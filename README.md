# Dataset
Using the KDD Cup 2003 dataset, it contains roughly 30,000 research papers from the arXiv. I will be using abstract and citation graph, the abstract dataset contains metadata related to an research paper. The abstract metadata we will utilize will be title, author names, and date.
```python
from data import Data
from model import Model
import random

X_train, X_test, y_train, y_test, AUTHOR_MAP = Data().getXY(useSaved=True)

model = Model().getFitModel(X_train, y_train)

accuracy, true_idx = Model().testModel(X_test, y_test, model, subset_acc=False)
print(f'Accuracy of the model: {accuracy}')

index = random.randint(0, len(X_test))

AUTHOR_MAP_DASH = {y:x for x,y in AUTHOR_MAP.items()}
s = ', '.join([AUTHOR_MAP_DASH[i] if i in AUTHOR_MAP_DASH.keys() else "UNK" for i in X_test[index]])

print(f'Cited research authors {s} and the paper is {Model().getAuthor([X_test[index]], AUTHOR_MAP, model)}')
```
