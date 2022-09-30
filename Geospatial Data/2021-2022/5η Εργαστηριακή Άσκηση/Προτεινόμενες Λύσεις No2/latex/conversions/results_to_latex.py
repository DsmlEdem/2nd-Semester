import re
import pandas as pd


pattern = re.compile('.*?(\w+).*?(-?\d+.\d+)')
results = []

for model in 'retinanet', 'fasterrcnn':
    with open(f'./{model}_mean_ap.txt') as f:
        for line in f:
            match = pattern.match(line)
            if match:
                metric, value = match.groups()
                if not metric.endswith(('highlighter', 'spoon', 'candle')):
                    results.append((model, metric, float(value)))

df = (
    pd.DataFrame(results, columns=['Model', 'Metric', 'Value'])
     .set_index(['Model', 'Metric'])
     .unstack('Model')
     .rename(columns={'retinanet': 'RetinaNet', 'fasterrcnn': 'Faster R-CNN'})  # type: ignore
)


df.index = (
    df.index
     .str.replace('test_', '')
     .str.replace('map', 'mAP')
     .str.replace('mar', 'mAR')
     .str.replace('class_', '')
     .str.replace('_(?=\d)', '@')
     .str.replace('_', ' ')
)

df = df.droplevel(0, axis='columns')  # type: ignore
df.columns.name = None


latex = df.style.format(precision=3).to_latex(hrules=True)  # type: ignore
print(latex)
