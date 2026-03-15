"""MATH solver — the artifact agents evolve.

Takes a competition math problem on stdin, prints the answer on stdout.
Answers may be numeric, fractions, expressions, or LaTeX.
"""

import sys
import os
import re

from openai import OpenAI


def solve(problem: str) -> str:
    """Solve a competition math problem. Return the answer as a string."""
    client = OpenAI()

    response = client.chat.completions.create(
        model=os.environ.get("SOLVER_MODEL", "gpt-4.1-nano"),
        messages=[
            {"role": "system", "content": (
                "You are a competition math solver. "
                "Solve the problem step by step, showing all reasoning. "
                "Put your final answer inside \\boxed{} on the last line. "
                "For example: \\boxed{42} or \\boxed{\\frac{1}{2}}. "
                "The answer inside \\boxed{} should be simplified and exact."
            )},
            {"role": "user", "content": problem},
        ],
        temperature=0,
        max_tokens=2048,
    )

    text = response.choices[0].message.content.strip()
    # extract from \boxed{}
    m = re.search(r'\\boxed\{(.+)\}', text)
    if m:
        return m.group(1).strip()
    # fallback: last line
    lines = text.split("\n")
    return lines[-1].strip()


if __name__ == "__main__":
    problem = sys.stdin.read().strip()
    print(solve(problem))
