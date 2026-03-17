#!/usr/bin/env bash
set -euo pipefail
mkdir -p data
echo "Downloading MATH-500..."
python3 -c "
from datasets import load_dataset
import json, pathlib

ds = load_dataset('HuggingFaceH4/MATH-500', split='test')
ds = ds.shuffle(seed=42)

dev_out = pathlib.Path('data/dev.jsonl')
test_out = pathlib.Path('data/test.jsonl')

with dev_out.open('w') as f:
    for row in list(ds)[:400]:
        f.write(json.dumps({'question': row['problem'], 'answer': row['answer']}) + '\n')

with test_out.open('w') as f:
    for row in list(ds)[400:]:
        f.write(json.dumps({'question': row['problem'], 'answer': row['answer']}) + '\n')

print(f'Dev:  400 problems -> {dev_out}')
print(f'Test: 100 problems -> {test_out}')
"
echo "Done."
