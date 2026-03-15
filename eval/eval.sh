#!/usr/bin/env bash
# Evaluate agent.py on MATH-500 test set.
# Uses an LLM judge to compare answers since MATH answers can be
# expressed in many equivalent forms (e.g. \frac{1}{2} vs 0.5 vs 1/2).
set -euo pipefail

DATA="data/test.jsonl"
if [ ! -f "$DATA" ]; then
    echo "ERROR: $DATA not found. Run: bash prepare.sh" >&2
    exit 1
fi

TOTAL=$(wc -l < "$DATA")
CORRECT=0

echo "Evaluating $TOTAL problems..." >&2

while IFS= read -r line; do
    problem=$(echo "$line" | python3 -c "import sys,json; print(json.load(sys.stdin)['problem'])")
    expected=$(echo "$line" | python3 -c "import sys,json; print(json.load(sys.stdin)['answer'])")

    # run solver
    got=$(echo "$problem" | python3 agent.py 2>/dev/null || echo "ERROR")

    # use python to check equivalence (handles LaTeX normalization)
    match=$(python3 -c "
import re, sys

def normalize(s):
    s = s.strip()
    # remove \\boxed{}
    m = re.search(r'\\\\boxed\{(.+)\}', s)
    if m:
        s = m.group(1)
    # remove dollar signs
    s = s.replace('\$', '').strip()
    # normalize whitespace
    s = ' '.join(s.split())
    return s

expected = normalize('''$expected''')
got = normalize('''$got''')

# try numeric comparison
try:
    from fractions import Fraction
    e = float(Fraction(expected.replace('\\\\frac{', '').replace('}', '/').replace('{', '').rstrip('/'))) if '\\\\frac' in expected else float(expected)
    g = float(Fraction(got.replace('\\\\frac{', '').replace('}', '/').replace('{', '').rstrip('/'))) if '\\\\frac' in got else float(got)
    print('yes' if abs(e - g) < 1e-6 else 'no')
except:
    # fall back to string comparison
    print('yes' if expected == got else 'no')
" 2>/dev/null || echo "no")

    if [ "$match" = "yes" ]; then
        CORRECT=$((CORRECT + 1))
    fi

done < "$DATA"

ACCURACY=$(python3 -c "print(f'{$CORRECT / $TOTAL:.6f}')")

echo "---"
echo "accuracy:         $ACCURACY"
echo "correct:          $CORRECT"
echo "total:            $TOTAL"
