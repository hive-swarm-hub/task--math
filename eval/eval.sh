#!/usr/bin/env bash
# Usage:
#   bash eval/eval.sh              — train set (for experimentation)
#   bash eval/eval.sh --test       — test set (for submission only)
#   bash eval/eval.sh --ids 0,3,5  — specific indices (for debugging)
set -euo pipefail

DATA="data/train.jsonl"
IDS=""
while [ $# -gt 0 ]; do
    case "$1" in
        --test) DATA="data/test.jsonl"; shift ;;
        --ids) IDS="$2"; shift 2 ;;
        --ids=*) IDS="${1#--ids=}"; shift ;;
        *) shift ;;
    esac
done

if [ ! -f "$DATA" ]; then
    echo "ERROR: $DATA not found. Run: bash prepare.sh" >&2
    exit 1
fi

if [ -n "$IDS" ]; then
    TMPDATA=$(mktemp)
    python3 -c "
ids = set(int(i) for i in \"$IDS\".split(\",\"))
with open(\"$DATA\") as f:
    for i, line in enumerate(f):
        if i in ids:
            print(line, end=\"\")
" > "$TMPDATA"
    DATA="$TMPDATA"
fi

TOTAL=$(wc -l < "$DATA")
CORRECT=0

echo "Evaluating $TOTAL problems from $DATA..." >&2

while IFS= read -r line; do
    question=$(echo "$line" | python3 -c "import sys,json; print(json.load(sys.stdin)['question'])")
    expected=$(echo "$line" | python3 -c "import sys,json; print(json.load(sys.stdin)['answer'])")
    got=$(echo "$question" | python3 agent.py 2>/dev/null || echo "ERROR")
    normalize() { echo "$1" | tr -d ',' | sed 's/\.0*$//' | xargs; }
    got_norm=$(normalize "$got")
    exp_norm=$(normalize "$expected")
    if [ "$got_norm" = "$exp_norm" ]; then CORRECT=$((CORRECT + 1)); fi
done < "$DATA"

ACCURACY=$(python3 -c "print(f'{${CORRECT} / ${TOTAL}}' if $TOTAL == 0 else f'{${CORRECT} / ${TOTAL}:.6f}')")

echo "---"
echo "accuracy:         $ACCURACY"
echo "correct:          $CORRECT"
echo "total:            $TOTAL"
