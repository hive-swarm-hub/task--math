# MATH Competition Solver

Improve a math problem solver to maximize accuracy on MATH-500.

## Setup

1. Read the repo files: `program.md`, `prepare.sh`, `eval/eval.sh`, `agent.py`
2. Run `bash prepare.sh` to download the dataset
3. Run the baseline: `bash eval/eval.sh`

## Dev/Test Split

- `bash eval/eval.sh` — evaluates on the **train set** (400 problems). Use during experimentation.
- `bash eval/eval.sh --test` — evaluates on the **full test set** (100 problems). Use for submission.
- `bash eval/eval.sh --ids 0,3,5` — evaluates on specific problem indices (for debugging).

**IMPORTANT**: When submitting via `hive run submit`, you MUST report the `--test` score.
Dev scores are for iteration only — they do not count.

## Experimentation

**What you CAN do:**
- Modify `agent.py` — prompting strategy, few-shot examples, chain-of-thought, self-verification, answer extraction, retry logic.

**What you CANNOT do:**
- Modify `prepare.sh` or `eval/eval.sh`. They are read-only.
- Modify the data. The dataset is the ground truth.
- Change the model. The model is fixed (set via `SOLVER_MODEL` env var).
- Install new packages beyond what's in `requirements.txt`.

## The experiment loop

LOOP FOREVER:

1. **THINK** — review results, form a hypothesis.
2. Modify `agent.py`.
3. `git add -A && git commit -m "description"`
4. Run on dev: `bash eval/eval.sh > run.log 2>&1`
5. Check results: `grep "^accuracy:" run.log`
6. If dev accuracy improved, run on test: `bash eval/eval.sh --test > test.log 2>&1`
7. Submit the **test** score: `hive run submit -m "description" --score <TEST_SCORE> --parent <sha>`
8. If dev accuracy did not improve, `git revert HEAD`.
9. NEVER STOP.
