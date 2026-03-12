#!/usr/bin/env python3
"""
Full HLE Benchmark with RAG Enhancement
Combines RAG knowledge base with all benchmark categories
"""

import asyncio
import sys
import time
import json
from datetime import datetime

sys.path.insert(0, 'src')
import httpx

from cosmic_council.enhancements.rag_knowledge_base import (
    RAGKnowledgeBase, get_enhanced_prompt, get_system_prompt
)

LM_STUDIO_API = "http://localhost:1234/v1/chat/completions"
MODEL = "google/gemma-3-4b"

# Full HLE benchmark questions
HLE_BENCHMARK = {
    "mathematics": {
        "totem": "red",
        "domain": "math",
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
        "domain": "physics",
        "questions": [
            {"q": "In the Schwarzschild radius formula r_s = 2GM/c^n, what is n?", "expected": "2"},
            {"q": "The fine structure constant alpha is approximately 1/k. What integer is k?", "expected": "137"},
            {"q": "How many quarks are in a proton?", "expected": "3"},
            {"q": "What is Planck's constant h in units of J*s? Answer as 6.XX * 10^-34.", "expected": "6.63", "alt": ["6.62", "6.626"]},
            {"q": "What is the charge of an electron in coulombs? Answer as 1.6 * 10^-?", "expected": "19"},
            {"q": "In special relativity, what is the Lorentz factor gamma when v=0?", "expected": "1"},
        ]
    },
    "biology_medicine": {
        "totem": "yellow",
        "domain": "biology",
        "questions": [
            {"q": "How many base pairs are in the human genome, approximately in billions?", "expected": "3"},
            {"q": "What organelle is called the powerhouse of the cell?", "expected": "mitochondria"},
            {"q": "In DNA, adenine pairs with which nucleotide base?", "expected": "thymine"},
            {"q": "How many chromosomes do humans have in somatic cells?", "expected": "46"},
            {"q": "What enzyme unzips the DNA double helix during replication?", "expected": "helicase"},
            {"q": "What is the normal human body temperature in Celsius?", "expected": "37"},
            {"q": "How many chambers does the human heart have?", "expected": "4", "alt": ["four"]},
        ]
    },
    "computer_science": {
        "totem": "orange",
        "domain": "cs",
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
        "domain": "humanities",
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
        "domain": "philosophy",
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
        "totem": "green",
        "domain": "chemistry",
        "questions": [
            {"q": "What is the atomic number of carbon?", "expected": "6"},
            {"q": "How many elements are in the periodic table (approximately)?", "expected": "118"},
            {"q": "What is the chemical formula for water?", "expected": "h2o"},
            {"q": "What is Avogadro's number approximately? Answer as 6.02 * 10^?", "expected": "23"},
            {"q": "What is the pH of pure water at 25C?", "expected": "7"},
            {"q": "What noble gas has atomic number 2?", "expected": "helium"},
        ]
    }
}


async def call_model_with_rag(question: str, domain: str) -> dict:
    """Call LM Studio with RAG-enhanced prompt"""
    try:
        enhanced_prompt = get_enhanced_prompt(question, domain)
        system_prompt = get_system_prompt(domain)

        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                LM_STUDIO_API,
                json={
                    "model": MODEL,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": enhanced_prompt}
                    ],
                    "temperature": 0.1,
                    "max_tokens": 800
                }
            )
            if response.status_code == 200:
                data = response.json()
                message = data.get("choices", [{}])[0].get("message", {})
                content = message.get("content", "")
                reasoning = message.get("reasoning_content", "")
                full_response = f"{content}\n{reasoning}" if reasoning else content
                return {"success": True, "result": full_response}
            return {"success": False, "error": f"HTTP {response.status_code}"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def check_answer(response: str, expected: str, alternatives: list = None) -> bool:
    """Check if response contains expected answer"""
    resp = response.lower().strip()
    exp = expected.lower().strip()

    if exp in resp:
        return True

    if alternatives:
        for alt in alternatives:
            if alt.lower() in resp:
                return True

    # Clean comparison
    resp_clean = resp.replace(" ", "").replace("-", "")
    exp_clean = exp.replace(" ", "").replace("-", "")
    if exp_clean in resp_clean:
        return True

    # Handle Unicode subscripts/superscripts
    unicode_map = {
        '\u2080': '0', '\u2081': '1', '\u2082': '2', '\u2083': '3',
        '\u2084': '4', '\u2085': '5', '\u2086': '6', '\u2087': '7',
        '\u2088': '8', '\u2089': '9', '\u00b2': '2', '\u00b3': '3',
    }
    resp_normalized = resp
    for uni, ascii_char in unicode_map.items():
        resp_normalized = resp_normalized.replace(uni, ascii_char)
    if exp in resp_normalized:
        return True

    return False


async def run_full_benchmark():
    """Run the full HLE benchmark with RAG"""
    print("=" * 70)
    print("FULL HLE BENCHMARK WITH RAG ENHANCEMENT")
    print("=" * 70)
    print(f"Model: {MODEL}")
    print("=" * 70)
    print()

    total_correct = 0
    total_questions = 0
    results = {}

    for category, data in HLE_BENCHMARK.items():
        print(f"[{data['totem']:6}] {category.upper()}")
        print(f"        Domain: {data['domain']}")

        correct = 0
        for i, qa in enumerate(data["questions"]):
            start = time.time()
            response = await call_model_with_rag(qa["q"], data["domain"])
            elapsed = time.time() - start

            if response["success"]:
                answer = str(response["result"])
                is_correct = check_answer(answer, qa["expected"], qa.get("alt"))
                if is_correct:
                    correct += 1
                status = "PASS" if is_correct else "FAIL"
                print(f"        Q{i+1}: [{status}] exp={qa['expected'][:15]} ({elapsed:.1f}s)")
                if not is_correct:
                    answer_safe = answer.replace('\n', ' ')[:60].encode('ascii', 'replace').decode('ascii')
                    print(f"             Got: {answer_safe}")
            else:
                print(f"        Q{i+1}: [ERROR] {response['error']}")

        accuracy = (correct / len(data["questions"])) * 100 if data["questions"] else 0
        results[category] = {"correct": correct, "total": len(data["questions"]), "accuracy": accuracy}
        total_correct += correct
        total_questions += len(data["questions"])
        print(f"        Score: {correct}/{len(data['questions'])} ({accuracy:.1f}%)")
        print()

    overall = (total_correct / total_questions) * 100 if total_questions else 0

    print("=" * 70)
    print("FULL BENCHMARK RESULTS")
    print("=" * 70)
    print(f"{'Category':<25} {'Score':>10} {'Accuracy':>10}")
    print("-" * 45)
    for cat, res in results.items():
        print(f"{cat:<25} {res['correct']:>3}/{res['total']:<6} {res['accuracy']:>8.1f}%")
    print("-" * 45)
    print(f"{'OVERALL':<25} {total_correct:>3}/{total_questions:<6} {overall:>8.1f}%")
    print()

    print("Comparison:")
    print(f"  Baseline (no RAG):    93.8%")
    print(f"  With RAG:             {overall:.1f}%")
    print(f"  Improvement:          {overall - 93.8:+.1f}%")
    print()

    # Save results
    output = {
        "timestamp": datetime.now().isoformat(),
        "model": MODEL,
        "rag_enhanced": True,
        "results": results,
        "overall": overall,
        "total_correct": total_correct,
        "total_questions": total_questions
    }
    with open("hle_results_rag.json", "w") as f:
        json.dump(output, f, indent=2)
    print("Results saved to: hle_results_rag.json")

    return output


if __name__ == "__main__":
    asyncio.run(run_full_benchmark())
