#!/usr/bin/env bash
set -euo pipefail
mkdir -p data
echo "Downloading MATH-500..."
python3 << 'PY'
from datasets import load_dataset
import json, pathlib, random
random.seed(42)
items = list(load_dataset('HuggingFaceH4/MATH-500', split='test'))
random.shuffle(items)
with pathlib.Path('data/train.jsonl').open('w') as f:
    for row in items[:100]:
        f.write(json.dumps({"question": row["problem"], "answer": row["answer"]}) + '\n')
with pathlib.Path('data/test.jsonl').open('w') as f:
    for row in items[100:250]:
        f.write(json.dumps({"question": row["problem"], "answer": row["answer"]}) + '\n')
print('Train: 100, Test: 150')
PY
echo "Done."
