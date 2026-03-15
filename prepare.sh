#!/usr/bin/env bash
# Download MATH-500 test set. Run once.
set -euo pipefail

mkdir -p data

echo "Downloading MATH-500 test set..."
python3 -c "
from datasets import load_dataset
import json, pathlib, random

random.seed(42)
ds = load_dataset('HuggingFaceH4/MATH-500', split='test')
ds = ds.shuffle(seed=42).select(range(50))
out = pathlib.Path('data/test.jsonl')
with out.open('w') as f:
    for row in ds:
        f.write(json.dumps({
            'problem': row['problem'],
            'answer': row['answer'],
            'subject': row['subject'],
            'level': row['level'],
        }) + '\n')

print(f'Wrote {len(ds)} problems to {out}')
"

echo "Done. $(wc -l < data/test.jsonl) problems in data/test.jsonl"
