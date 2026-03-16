"""MATH solver — the artifact agents evolve.

Takes a competition math problem on stdin, prints the answer on stdout.
Answers may be numeric, fractions, expressions, or LaTeX.
"""

import sys
import os
import re

from openai import OpenAI


def preprocess(problem: str) -> str:
    """Clean up problem text for better model understanding."""
    # Strip [asy]...[/asy] blocks — they're Asymptote diagram code
    # that the model can't render. The labels in them are still
    # referenced in the problem text.
    cleaned = re.sub(r'\[asy\].*?\[/asy\]', '[Diagram]', problem, flags=re.DOTALL)
    return cleaned.strip()


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
                "- Always simplify fully. Never use decimals unless the answer is inherently decimal.\n\n"
                "IMPORTANT: Give ONLY the value asked for inside \\boxed{}. "
                "Do not include variable names, units, or labels. "
                "For example, if asked 'What is tan A?', answer \\boxed{2}, not \\boxed{\\tan A = 2}."
            )},
            {"role": "user", "content": preprocess(problem)},
        ],
        temperature=0,
        max_tokens=8192,
    )

    text = response.choices[0].message.content.strip()
    return clean_answer(extract_answer(text))


def clean_answer(answer: str) -> str:
    """Post-process extracted answer to match judge's expected format."""
    s = answer.strip()
    # remove wrapping dollar signs
    s = s.strip('$')
    # remove prefixes like "(a, b, c, d) = " or "\tan A = "
    s = re.sub(r'^\\?[a-zA-Z]+\s*[A-Za-z]?\s*=\s*', '', s)
    s = re.sub(r'^[\(\[]?[a-zA-Z](?:\s*,\s*[a-zA-Z])*[\)\]]?\s*=\s*', '', s)
    # remove \! (thin space) from numbers
    s = s.replace('\\!', '')
    # remove \text{} wrapper but keep content
    s = re.sub(r'\\text\{([^}]*)\}', r'\1', s)
    # remove \left and \right
    s = s.replace('\\left', '').replace('\\right', '')
    # remove spaces around commas in tuples
    s = re.sub(r'\s*,\s*', ',', s)
    # collapse spaces around +/- in expressions (6 + 9i -> 6+9i)
    # but NOT before \frac, \sqrt, \pi etc (keep "137 \frac{1}{2}")
    s = re.sub(r'\s*\+\s*', '+', s)
    s = re.sub(r'\s*-\s*', '-', s)
    # restore space before backslash commands (e.g. "137\frac" -> "137 \frac")
    s = re.sub(r'(\d)\\', r'\1 \\', s)
    # also handle "-\frac" -> "-\\frac" (no space needed, just minus)
    # normalize spaces
    s = s.strip()
    return s


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
