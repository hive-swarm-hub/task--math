"""Evaluate agent.py on MATH problems. Compares answers with normalization."""

import json
import re
import subprocess
import sys
from fractions import Fraction


def normalize(s: str) -> str:
    s = s.strip()
    # extract from \boxed{}
    m = re.search(r'\\boxed\{(.+)\}', s)
    if m:
        s = m.group(1)
    # remove dollar signs and whitespace
    s = s.replace('$', '').strip()
    s = ' '.join(s.split())
    return s


def answers_match(expected: str, got: str) -> bool:
    e = normalize(expected)
    g = normalize(got)

    # exact string match
    if e == g:
        return True

    # try numeric comparison
    try:
        ev = float(e)
        gv = float(g)
        return abs(ev - gv) < 1e-6
    except ValueError:
        pass

    # try fraction parsing: \frac{a}{b} -> a/b
    def parse_frac(s):
        m = re.match(r'\\frac\{(-?\d+)\}\{(-?\d+)\}', s)
        if m:
            return Fraction(int(m.group(1)), int(m.group(2)))
        try:
            return Fraction(s)
        except (ValueError, ZeroDivisionError):
            return None

    ef = parse_frac(e)
    gf = parse_frac(g)
    if ef is not None and gf is not None:
        return ef == gf

    return False


def main():
    data_path = sys.argv[1]
    with open(data_path) as f:
        problems = [json.loads(line) for line in f]

    total = len(problems)
    correct = 0

    print(f"Evaluating {total} problems...", file=sys.stderr)

    for i, item in enumerate(problems):
        problem = item["problem"]
        expected = item["answer"]

        # run solver
        try:
            result = subprocess.run(
                ["python3", "agent.py"],
                input=problem, capture_output=True, text=True, timeout=60,
            )
            got = result.stdout.strip()
        except (subprocess.TimeoutExpired, Exception):
            got = "ERROR"

        if answers_match(expected, got):
            correct += 1

    accuracy = correct / total
    print("---")
    print(f"accuracy:         {accuracy:.6f}")
    print(f"correct:          {correct}")
    print(f"total:            {total}")


if __name__ == "__main__":
    main()
