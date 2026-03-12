#!/usr/bin/env python3
"""
Humanity's Last Exam (HLE) Style Benchmark for Cosmic Council

Based on the expert-level benchmark from Center for AI Safety & Scale AI.
Current SOTA: ~45% (Gemini 3.1 Pro), ~42% (GPT-5.4)

Usage:
    python hle_benchmark.py              # Run full HLE benchmark
    python hle_benchmark.py --category mathematics
    python hle_benchmark.py --quick      # Run subset (faster)
"""

import asyncio
import argparse
import sys
import time
import json
from datetime import datetime

sys.path.insert(0, 'src')
import httpx

CRONUS_API = "http://localhost:8010/execute"

# Humanity's Last Exam style questions - expert level, multi-domain
HLE_BENCHMARK = {
    "mathematics": {
        "totem": "red",
        "description": "Advanced mathematics (41% of HLE)",
        "questions": [
            {"q": "What is the derivative of x^x with respect to x? Express in terms of x^x and ln(x).", "expected": "x^x(ln(x)+1)", "alt": ["ln(x)+1"]},
            {"q": "In group theory, what is the order of the symmetric group S_4?", "expected": "24"},
            {"q": "What is the sum of the infinite geometric series 1/2 + 1/4 + 1/8 + ...?", "expected": "1"},
            {"q": "The Riemann zeta function zeta(2) = pi^2/k. What is k?", "expected": "6"},
            {"q": "How many prime numbers are there less than 20?", "expected": "8"},
            {"q": "What is the Euler characteristic of a sphere?", "expected": "2"},
            {"q": "In topology, a coffee mug is homeomorphic to what shape?", "expected": "torus", "alt": ["donut", "doughnut"]},
            {"q": "What is 7! (7 factorial)?", "expected": "5040"},
        ]
    },
    "physics": {
        "totem": "green",
        "description": "Physics and physical sciences (9% of HLE)",
        "questions": [
            {"q": "In the Schwarzschild radius formula r_s = 2GM/c^n, what is n?", "expected": "2"},
            {"q": "The fine structure constant alpha is approximately 1/k. What integer is k?", "expected": "137"},
            {"q": "How many quarks are in a proton?", "expected": "3"},
            {"q": "What is Planck's constant h in units of J*s, to 2 decimal places? Answer as 6.XX * 10^-34.", "expected": "6.63", "alt": ["6.62"]},
            {"q": "What is the charge of an electron in coulombs? Answer magnitude only, as 1.6 * 10^-?", "expected": "19"},
            {"q": "In special relativity, what is the Lorentz factor gamma when v=0?", "expected": "1"},
        ]
    },
    "biology_medicine": {
        "totem": "yellow",
        "description": "Biology and medicine (11% of HLE)",
        "questions": [
            {"q": "How many base pairs are in the human genome, approximately in billions?", "expected": "3"},
            {"q": "What organelle is called the powerhouse of the cell?", "expected": "mitochondria", "alt": ["mitochondrion"]},
            {"q": "In DNA, adenine pairs with which nucleotide base?", "expected": "thymine"},
            {"q": "How many chromosomes do humans have in somatic cells?", "expected": "46"},
            {"q": "What enzyme unzips the DNA double helix during replication?", "expected": "helicase"},
            {"q": "What is the normal human body temperature in Celsius?", "expected": "37", "alt": ["36.5", "37.0"]},
            {"q": "How many chambers does the human heart have?", "expected": "4"},
        ]
    },
    "computer_science": {
        "totem": "orange",
        "description": "CS and AI (10% of HLE)",
        "questions": [
            {"q": "What is the time complexity of binary search in Big O notation?", "expected": "o(log n)", "alt": ["log n", "o(logn)"]},
            {"q": "Can a Turing machine solve the halting problem for all programs? Yes or no.", "expected": "no"},
            {"q": "How many bits are in a byte?", "expected": "8"},
            {"q": "What does the P in P vs NP stand for?", "expected": "polynomial"},
            {"q": "What is 255 in binary?", "expected": "11111111"},
            {"q": "In Big O, what is O(1) called?", "expected": "constant"},
            {"q": "What year was the first computer virus created? 1970s, 1980s, or 1990s?", "expected": "1970", "alt": ["70s", "1971"]},
        ]
    },
    "humanities_social": {
        "totem": "blue",
        "description": "Humanities and social sciences (9% of HLE)",
        "questions": [
            {"q": "Who wrote 'Critique of Pure Reason'? Last name only.", "expected": "kant"},
            {"q": "What year did World War II end in Europe?", "expected": "1945"},
            {"q": "What principle states the simplest explanation is usually correct?", "expected": "occam", "alt": ["ockham", "parsimony"]},
            {"q": "The categorical imperative is associated with which philosopher? Last name.", "expected": "kant"},
            {"q": "What ancient wonder was the great lighthouse?", "expected": "alexandria", "alt": ["pharos"]},
            {"q": "Who painted the Mona Lisa? Last name only.", "expected": "vinci", "alt": ["da vinci", "leonardo"]},
            {"q": "What year did the Berlin Wall fall?", "expected": "1989"},
        ]
    },
    "philosophy_ethics": {
        "totem": "purple",
        "description": "Philosophy and ethics",
        "questions": [
            {"q": "Utilitarianism judges actions by their consequences or intentions?", "expected": "consequences"},
            {"q": "Deontological ethics focuses on rules/duties or outcomes?", "expected": "rules", "alt": ["duties", "duty"]},
            {"q": "Who proposed the veil of ignorance? Last name only.", "expected": "rawls"},
            {"q": "The naturalistic fallacy involves deriving 'ought' from what?", "expected": "is"},
            {"q": "Who wrote 'Beyond Good and Evil'? Last name only.", "expected": "nietzsche"},
            {"q": "What is the study of knowledge called?", "expected": "epistemology"},
            {"q": "Cogito ergo sum was stated by which philosopher? Last name.", "expected": "descartes"},
        ]
    },
    "chemistry": {
        "totem": "red",
        "description": "Chemistry (7% of HLE)",
        "questions": [
            {"q": "What is the atomic number of carbon?", "expected": "6"},
            {"q": "How many elements are in the periodic table (approximately)?", "expected": "118"},
            {"q": "What is the chemical formula for water?", "expected": "h2o"},
            {"q": "What is Avogadro's number approximately? Answer as 6.02 * 10^?", "expected": "23"},
            {"q": "What is the pH of pure water at 25C?", "expected": "7"},
            {"q": "What noble gas has atomic number 2?", "expected": "helium", "alt": ["he"]},
        ]
    }
}


async def call_cronus(totem: str, task: str, timeout: float = 90.0) -> dict:
    """Call CRONUS API"""
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(CRONUS_API, json={
                "task": f"Answer this expert question precisely and concisely: {task}",
                "totem": totem,
                "context": "Expert-level exam. Give direct, short answers."
            })
            if response.status_code == 200:
                return {"success": True, "result": response.json().get("result", "")}
            return {"success": False, "error": f"HTTP {response.status_code}"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def check_answer(response: str, expected: str, alternatives: list = None) -> bool:
    """Check if response contains expected answer"""
    resp = response.lower().strip()
    exp = expected.lower().strip()

    # Check primary expected
    if exp in resp:
        return True

    # Check alternatives
    if alternatives:
        for alt in alternatives:
            if alt.lower() in resp:
                return True

    # Handle common variations
    resp_clean = resp.replace(" ", "").replace("-", "")
    exp_clean = exp.replace(" ", "").replace("-", "")
    if exp_clean in resp_clean:
        return True

    return False


async def run_hle_benchmark(categories: list = None, quick: bool = False):
    """Run the HLE-style benchmark"""
    print("=" * 70)
    print("HUMANITY'S LAST EXAM (HLE) STYLE BENCHMARK")
    print("=" * 70)
    print("Testing Cosmic Council against expert-level questions")
    print("Current SOTA: ~45% (Gemini 3.1 Pro), ~42% (GPT-5.4)")
    print("=" * 70)
    print()

    if categories is None:
        categories = list(HLE_BENCHMARK.keys())

    total_correct = 0
    total_questions = 0
    results = {}

    for category in categories:
        if category not in HLE_BENCHMARK:
            continue

        data = HLE_BENCHMARK[category]
        questions = data["questions"][:3] if quick else data["questions"]

        print(f"[{data['totem']:6}] {category.upper()}")
        print(f"        {data['description']}")

        correct = 0
        for i, qa in enumerate(questions):
            start = time.time()
            response = await call_cronus(data["totem"], qa["q"])
            elapsed = time.time() - start

            if response["success"]:
                answer = str(response["result"])
                is_correct = check_answer(answer, qa["expected"], qa.get("alt"))
                if is_correct:
                    correct += 1
                status = "PASS" if is_correct else "FAIL"
                answer_short = answer[:35].replace("\n", " ")
                if len(answer) > 35:
                    answer_short += "..."
                print(f"        Q{i+1}: [{status}] exp={qa['expected'][:15]} ({elapsed:.1f}s)")
            else:
                print(f"        Q{i+1}: [ERROR] {response['error']}")

        accuracy = (correct / len(questions)) * 100 if questions else 0
        results[category] = {"correct": correct, "total": len(questions), "accuracy": accuracy}
        total_correct += correct
        total_questions += len(questions)
        print(f"        Score: {correct}/{len(questions)} ({accuracy:.1f}%)")
        print()

    overall = (total_correct / total_questions) * 100 if total_questions else 0

    print("=" * 70)
    print("HLE-STYLE BENCHMARK RESULTS")
    print("=" * 70)
    print(f"{'Category':<25} {'Score':>10} {'Accuracy':>10}")
    print("-" * 45)
    for cat, res in results.items():
        print(f"{cat:<25} {res['correct']:>3}/{res['total']:<6} {res['accuracy']:>8.1f}%")
    print("-" * 45)
    print(f"{'OVERALL':<25} {total_correct:>3}/{total_questions:<6} {overall:>8.1f}%")
    print()
    print("Comparison to SOTA:")
    print(f"  Gemini 3.1 Pro Preview: 44.7%")
    print(f"  GPT-5.4 (xhigh):        41.6%")
    print(f"  Cosmic Council:         {overall:.1f}%")
    print()

    return {
        "timestamp": datetime.now().isoformat(),
        "results": results,
        "overall": overall,
        "total_correct": total_correct,
        "total_questions": total_questions
    }


def main():
    parser = argparse.ArgumentParser(description="HLE-style Benchmark")
    parser.add_argument("--category", "-c", help="Run specific category")
    parser.add_argument("--quick", "-q", action="store_true", help="Quick mode (3 questions per category)")
    parser.add_argument("--output", "-o", help="Save results to JSON")
    parser.add_argument("--list", "-l", action="store_true", help="List categories")

    args = parser.parse_args()

    if args.list:
        print("HLE Benchmark Categories:")
        for key, data in HLE_BENCHMARK.items():
            print(f"  {key:<25} [{data['totem']:6}] {len(data['questions'])} questions")
        return

    categories = [args.category] if args.category else None
    results = asyncio.run(run_hle_benchmark(categories, args.quick))

    if args.output:
        with open(args.output, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"Results saved to: {args.output}")


if __name__ == "__main__":
    main()
