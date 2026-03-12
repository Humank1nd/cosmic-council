#!/usr/bin/env python3
"""
MMLU-Pro Benchmark for Cosmic Council
Routes through CRONUS API for proper 108-cycle evaluation
Uses fresh questions to avoid data contamination
"""

import asyncio
import sys
import time
import json
import random
from datetime import datetime
from datasets import load_dataset

sys.path.insert(0, 'src')
import httpx

CRONUS_API = "http://localhost:8010/execute"

# Map MMLU-Pro categories to Cosmic Council totems
CATEGORY_TO_TOTEM = {
    "math": "red",           # Red Owl - analytical/mathematical
    "physics": "red",        # Red Owl - scientific reasoning
    "chemistry": "green",    # Green Tortoise - natural sciences
    "biology": "green",      # Green Tortoise - life sciences
    "computer science": "orange",  # Orange Orangutan - technical systems
    "engineering": "orange", # Orange Orangutan - building/systems
    "economics": "yellow",   # Yellow Honeybee - collective patterns
    "business": "yellow",    # Yellow Honeybee - organizational
    "psychology": "blue",    # Blue Dolphin - understanding minds
    "philosophy": "purple",  # Purple Elephant - wisdom/ethics
    "law": "purple",         # Purple Elephant - ethical frameworks
    "health": "green",       # Green Tortoise - life/wellbeing
    "history": "blue",       # Blue Dolphin - human narrative
    "other": "purple",       # Purple Elephant - general wisdom
}


async def call_cronus(totem: str, question: str, options: list) -> dict:
    """Call CRONUS API with proper totem routing"""
    # Format question with multiple choice options
    formatted_q = f"{question}\n\nOptions:\n"
    for i, opt in enumerate(options):
        formatted_q += f"  {chr(65+i)}) {opt}\n"
    formatted_q += "\nAnswer with just the letter (A, B, C, etc.)"

    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                CRONUS_API,
                json={
                    "totem": totem,
                    "task": formatted_q,
                    "context": "MMLU-Pro benchmark evaluation"
                }
            )
            if response.status_code == 200:
                data = response.json()
                return {"success": True, "result": data.get("result", "")}
            return {"success": False, "error": f"HTTP {response.status_code}"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def extract_answer(response: str) -> str:
    """Extract letter answer from response"""
    resp = response.strip().upper()

    # Direct letter answer
    if resp and resp[0] in "ABCDEFGHIJ":
        return resp[0]

    # Look for patterns like "The answer is A" or "Answer: B"
    for pattern in ["ANSWER IS ", "ANSWER: ", "CORRECT ANSWER IS ", "CORRECT: "]:
        if pattern in resp:
            idx = resp.index(pattern) + len(pattern)
            if idx < len(resp) and resp[idx] in "ABCDEFGHIJ":
                return resp[idx]

    # Look for standalone letter at end
    words = resp.split()
    for word in reversed(words):
        if len(word) == 1 and word in "ABCDEFGHIJ":
            return word
        if len(word) == 2 and word[0] in "ABCDEFGHIJ" and word[1] in ".):":
            return word[0]

    return ""


async def run_mmlu_pro_benchmark(samples_per_category: int = 10):
    """Run MMLU-Pro benchmark through CRONUS"""
    print("=" * 70)
    print("MMLU-PRO BENCHMARK - COSMIC COUNCIL EVALUATION")
    print("=" * 70)
    print("Using fresh questions routed through CRONUS 108-cycle system")
    print(f"Samples per category: {samples_per_category}")
    print("=" * 70)
    print()

    # Load dataset
    print("Loading MMLU-Pro dataset...")
    dataset = load_dataset("TIGER-Lab/MMLU-Pro", split="test")

    # Group by category
    categories = {}
    for item in dataset:
        cat = item["category"]
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(item)

    print(f"Loaded {len(dataset)} questions across {len(categories)} categories")
    print()

    total_correct = 0
    total_questions = 0
    results = {}

    for category in sorted(categories.keys()):
        items = categories[category]
        totem = CATEGORY_TO_TOTEM.get(category, "purple")

        # Random sample to avoid any ordering bias
        sample = random.sample(items, min(samples_per_category, len(items)))

        print(f"[{totem:6}] {category.upper()}")
        print(f"        Testing {len(sample)} questions via CRONUS")

        correct = 0
        for i, item in enumerate(sample):
            question = item["question"]
            options = item["options"]
            answer_idx = item["answer_index"]
            expected = chr(65 + answer_idx)  # Convert 0->A, 1->B, etc.

            start = time.time()
            response = await call_cronus(totem, question, options)
            elapsed = time.time() - start

            if response["success"]:
                model_answer = extract_answer(str(response["result"]))
                is_correct = model_answer == expected
                if is_correct:
                    correct += 1
                status = "PASS" if is_correct else "FAIL"
                print(f"        Q{i+1}: [{status}] exp={expected} got={model_answer or '?'} ({elapsed:.1f}s)")
            else:
                print(f"        Q{i+1}: [ERROR] {response['error'][:40]}")

        accuracy = (correct / len(sample)) * 100 if sample else 0
        results[category] = {
            "correct": correct,
            "total": len(sample),
            "accuracy": accuracy,
            "totem": totem
        }
        total_correct += correct
        total_questions += len(sample)
        print(f"        Score: {correct}/{len(sample)} ({accuracy:.1f}%)")
        print()

    overall = (total_correct / total_questions) * 100 if total_questions else 0

    print("=" * 70)
    print("MMLU-PRO BENCHMARK RESULTS")
    print("=" * 70)
    print(f"{'Category':<20} {'Totem':<8} {'Score':>10} {'Accuracy':>10}")
    print("-" * 50)
    for cat in sorted(results.keys()):
        res = results[cat]
        print(f"{cat:<20} {res['totem']:<8} {res['correct']:>3}/{res['total']:<6} {res['accuracy']:>8.1f}%")
    print("-" * 50)
    print(f"{'OVERALL':<20} {'':<8} {total_correct:>3}/{total_questions:<6} {overall:>8.1f}%")
    print()

    # Compare with known benchmarks
    print("Comparison with SOTA:")
    print(f"  GPT-4o:              ~72%")
    print(f"  Claude 3.5 Sonnet:   ~68%")
    print(f"  Gemini 1.5 Pro:      ~65%")
    print(f"  Cosmic Council:      {overall:.1f}%")
    print()

    # Save results
    output = {
        "timestamp": datetime.now().isoformat(),
        "benchmark": "MMLU-Pro",
        "samples_per_category": samples_per_category,
        "total_questions": total_questions,
        "total_correct": total_correct,
        "overall_accuracy": overall,
        "results_by_category": results
    }
    with open("mmlu_pro_results.json", "w") as f:
        json.dump(output, f, indent=2)
    print(f"Results saved to: mmlu_pro_results.json")

    return output


if __name__ == "__main__":
    # Default to 10 questions per category (140 total) for initial test
    # Can increase for more thorough evaluation
    samples = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    asyncio.run(run_mmlu_pro_benchmark(samples))
