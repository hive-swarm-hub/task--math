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
                "You are an expert competition mathematics solver. "
                "Solve the problem carefully and methodically:\n"
                "1. Identify what the problem is asking for.\n"
                "2. Work through the solution step by step.\n"
                "3. Double-check your arithmetic and algebra.\n"
                "4. Verify your answer satisfies the original conditions.\n"
                "5. Put your final answer inside \\boxed{} on the very last line.\n\n"
                "Answer format rules:\n"
                "- Integers: \\boxed{42}\n"
                "- Fractions: \\boxed{\\frac{1}{2}} (always simplified)\n"
                "- Expressions: \\boxed{2\\sqrt{3}}\n"
                "- Multiple values: \\boxed{3, 5, 7}\n"
                "- Mixed numbers: convert to improper fractions or write as e.g. 137 \\frac{1}{2}\n"
                "- Always simplify fully. Never use decimals unless the answer is inherently decimal."
            )},
            {"role": "user", "content": problem},
        ],
        temperature=0,
        max_tokens=4096,
    )

    text = response.choices[0].message.content.strip()
    return extract_answer(text)


def extract_answer(text: str) -> str:
    """Extract the answer from model output, handling nested braces."""
    # find last \boxed{...} (in case model writes multiple)
    matches = list(re.finditer(r'\\boxed\{', text))
    if matches:
        start = matches[-1].end()
        depth = 1
        i = start
        while i < len(text) and depth > 0:
            if text[i] == '{':
                depth += 1
            elif text[i] == '}':
                depth -= 1
            i += 1
        return text[start:i-1].strip()
    # fallback: last non-empty line
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    return lines[-1] if lines else ""


if __name__ == "__main__":
    problem = sys.stdin.read().strip()
    print(solve(problem))
