#!/usr/bin/env bash
set -euo pipefail
mkdir -p data
echo "Downloading MATH-500..."
python3 << 'PY'
from datasets import load_dataset
import json, pathlib
ds = load_dataset('HuggingFaceH4/MATH-500', split='test')
out = pathlib.Path('data/test.jsonl')
with out.open('w') as f:
    for row in ds:
        f.write(json.dumps({"question": row["problem"], "answer": row["answer"]}) + '\n')
print(f'Wrote {len(ds)} problems to {out}')
PY
echo "Done."
