"""MATH solver — the artifact agents evolve.

Takes a competition math problem on stdin, prints the answer on stdout.
Answers may be numeric, fractions, expressions, or LaTeX.
"""

import sys
import os

from openai import OpenAI


def solve(problem: str) -> str:
    """Solve a competition math problem. Return the answer as a string."""
    client = OpenAI()

    response = client.chat.completions.create(
        model=os.environ.get("SOLVER_MODEL", "gpt-4.1-nano"),
        messages=[
            {"role": "system", "content": (
                "Solve the math problem. Show your work step by step. "
                "On the LAST line, write ONLY the final answer with no explanation. "
                "For fractions use LaTeX like \\frac{1}{2}. For expressions use LaTeX notation."
            )},
            {"role": "user", "content": problem},
        ],
        temperature=0,
        max_tokens=1024,
    )

    lines = response.choices[0].message.content.strip().split("\n")
    return lines[-1].strip()


if __name__ == "__main__":
    problem = sys.stdin.read().strip()
    print(solve(problem))
