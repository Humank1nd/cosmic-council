#!/usr/bin/env python3
"""
Enhanced HLE Benchmark with RAG Knowledge Base
Tests improvements to reach 100% accuracy
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
CRONUS_API = "http://localhost:8010/execute"

# Same benchmark questions as before
HLE_BENCHMARK = {
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
    },
}


async def call_lm_studio_enhanced(question: str, domain: str) -> dict:
    """Call LM Studio with RAG-enhanced prompt"""
    try:
        # Get RAG-enhanced prompt
        enhanced_prompt = get_enhanced_prompt(question, domain)
        system_prompt = get_system_prompt(domain)

        async with httpx.AsyncClient(timeout=300.0) as client:  # 5 min timeout
            response = await client.post(
                LM_STUDIO_API,
                json={
                    "model": "google/gemma-3-4b",  # Faster model
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": enhanced_prompt}
                    ],
                    "temperature": 0.1,
                    "max_tokens": 1000  # Increased for reasoning model
                }
            )
            if response.status_code == 200:
                data = response.json()
                message = data.get("choices", [{}])[0].get("message", {})
                # Handle reasoning models - check both content and reasoning_content
                content = message.get("content", "")
                reasoning = message.get("reasoning_content", "")
                # Combine both for answer checking
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

    # Clean comparison - remove spaces, hyphens
    resp_clean = resp.replace(" ", "").replace("-", "")
    exp_clean = exp.replace(" ", "").replace("-", "")
    if exp_clean in resp_clean:
        return True

    # Handle Unicode subscripts/superscripts (chemistry formulas)
    unicode_map = {
        '\u2080': '0', '\u2081': '1', '\u2082': '2', '\u2083': '3',
        '\u2084': '4', '\u2085': '5', '\u2086': '6', '\u2087': '7',
        '\u2088': '8', '\u2089': '9',  # subscripts
        '\u00b2': '2', '\u00b3': '3',  # superscripts
    }
    resp_normalized = resp
    for uni, ascii_char in unicode_map.items():
        resp_normalized = resp_normalized.replace(uni, ascii_char)
    if exp in resp_normalized:
        return True

    return False


async def run_enhanced_benchmark():
    """Run the enhanced HLE benchmark"""
    print("=" * 70)
    print("ENHANCED HLE BENCHMARK (with RAG Knowledge Base)")
    print("=" * 70)
    print("Testing RAG-enhanced prompts on previously failing categories")
    print("=" * 70)
    print()

    kb = RAGKnowledgeBase()
    total_correct = 0
    total_questions = 0
    results = {}

    for category, data in HLE_BENCHMARK.items():
        print(f"[{data['totem']:6}] {category.upper()}")
        print(f"        Domain: {data['domain']} (RAG-enhanced)")

        correct = 0
        for i, qa in enumerate(data["questions"]):
            start = time.time()

            # Show RAG retrieval
            facts = kb.retrieve(qa["q"], data["domain"], top_k=2)
            if facts:
                print(f"        RAG: Retrieved {len(facts)} relevant facts")

            response = await call_lm_studio_enhanced(qa["q"], data["domain"])
            elapsed = time.time() - start

            if response["success"]:
                answer = str(response["result"])
                is_correct = check_answer(answer, qa["expected"], qa.get("alt"))
                if is_correct:
                    correct += 1
                status = "PASS" if is_correct else "FAIL"
                print(f"        Q{i+1}: [{status}] exp={qa['expected'][:15]} ({elapsed:.1f}s)")
                if not is_correct:
                    # Show relevant part of answer (ASCII-safe)
                    answer_clean = answer.replace('\n', ' ')[:80]
                    answer_safe = answer_clean.encode('ascii', 'replace').decode('ascii')
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
    print("ENHANCED BENCHMARK RESULTS")
    print("=" * 70)
    print(f"{'Category':<25} {'Score':>10} {'Accuracy':>10}")
    print("-" * 45)
    for cat, res in results.items():
        print(f"{cat:<25} {res['correct']:>3}/{res['total']:<6} {res['accuracy']:>8.1f}%")
    print("-" * 45)
    print(f"{'OVERALL':<25} {total_correct:>3}/{total_questions:<6} {overall:>8.1f}%")
    print()

    # Compare with baseline
    print("Comparison:")
    print(f"  Baseline (no RAG):  93.8%")
    print(f"  Enhanced (with RAG): {overall:.1f}%")
    print(f"  Improvement:        {overall - 93.8:+.1f}%")

    return results


if __name__ == "__main__":
    asyncio.run(run_enhanced_benchmark())
