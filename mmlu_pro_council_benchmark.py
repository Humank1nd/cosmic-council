#!/usr/bin/env python3
"""
MMLU-Pro Benchmark - FULL COSMIC COUNCIL EVALUATION
Routes through ALL 6 totems in ROYGBV order for each question.
Each totem gets fresh context with summary of previous deliberations.

The Cosmic Canon:
- Red Owl: Research & foundational analysis
- Orange Orangutan: Strategic planning & orchestration
- Yellow Honeybee: Creative solutions & prototyping
- Green Tortoise: Resource/cost-benefit analysis
- Blue Dolphin: Communication & clarity
- Purple Elephant: Synthesis & final decision
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

CRONUS_API = "http://localhost:8010"

# ROYGBV order - all 6 totems work together
ROYGBV_SEQUENCE = ["red", "orange", "yellow", "green", "blue", "purple"]

TOTEM_ROLES = {
    "red": {
        "name": "Red Owl",
        "role": "Research & Analysis",
        "instruction": "Analyze this problem deeply. Identify key facts, eliminate obviously wrong options, and determine which answer is most likely correct based on evidence and logic."
    },
    "orange": {
        "name": "Orange Orangutan",
        "role": "Strategic Planning",
        "instruction": "Review the research analysis. Develop a strategic approach to verify the answer. Consider what additional perspectives might help confirm or refute the proposed answer."
    },
    "yellow": {
        "name": "Yellow Honeybee",
        "role": "Creative Problem-Solving",
        "instruction": "Apply creative thinking to this problem. Are there alternative interpretations? Consider edge cases or unconventional approaches that might reveal the correct answer."
    },
    "green": {
        "name": "Green Tortoise",
        "role": "Careful Evaluation",
        "instruction": "Carefully evaluate all the analysis so far. Weigh the evidence for each proposed answer. Consider the reliability and completeness of the reasoning."
    },
    "blue": {
        "name": "Blue Dolphin",
        "role": "Clear Communication",
        "instruction": "Synthesize the council's deliberations into a clear assessment. Which answer has the strongest support? Articulate the reasoning concisely."
    },
    "purple": {
        "name": "Purple Elephant",
        "role": "Final Synthesis",
        "instruction": "As the council synthesizer, review all perspectives and make the FINAL decision. State ONLY the letter of the correct answer (A, B, C, etc.) with brief justification."
    }
}


def extract_answer(response: str) -> str:
    """Extract letter answer from response"""
    resp = response.strip().upper()

    # Direct letter answer
    if resp and resp[0] in "ABCDEFGHIJ":
        return resp[0]

    # Look for patterns like "The answer is A" or "Answer: B"
    for pattern in ["ANSWER IS ", "ANSWER: ", "CORRECT ANSWER IS ", "CORRECT: ", "FINAL ANSWER: ", "THE ANSWER IS "]:
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


async def call_full_council(question: str, options: list) -> dict:
    """
    Call CRONUS with FULL COUNCIL deliberation.
    All 6 totems process the question in ROYGBV order.
    Each totem gets fresh context with summary of previous deliberations.
    """
    # Format question with multiple choice options
    formatted_q = f"{question}\n\nOptions:\n"
    for i, opt in enumerate(options):
        formatted_q += f"  {chr(65+i)}) {opt}\n"

    all_responses = []
    agents_used = []
    all_answers = []

    try:
        # Per-totem timeout of 180s (3 min), total council ~18 min max
        async with httpx.AsyncClient(timeout=180.0) as client:
            for i, totem in enumerate(ROYGBV_SEQUENCE):
                totem_info = TOTEM_ROLES[totem]

                # Build the task with totem-specific instruction
                if i == 0:
                    # Red Owl - First analysis (no prior context)
                    task = f"""{totem_info['instruction']}

QUESTION:
{formatted_q}

Analyze and propose your answer."""
                elif i < 5:
                    # Middle totems - Include summary of prior deliberation
                    prior_summary = []
                    for j, (prev_totem, prev_resp) in enumerate(zip(ROYGBV_SEQUENCE[:i], all_responses)):
                        prev_answer = extract_answer(prev_resp)
                        short_resp = prev_resp[:200] + "..." if len(prev_resp) > 200 else prev_resp
                        prior_summary.append(f"- {TOTEM_ROLES[prev_totem]['name']}: {prev_answer or '?'}")

                    task = f"""{totem_info['instruction']}

QUESTION:
{formatted_q}

COUNCIL DELIBERATION SO FAR:
{chr(10).join(prior_summary)}

Add your analysis and state which answer you support."""
                else:
                    # Purple Elephant - Final synthesis
                    vote_count = {}
                    for ans in all_answers:
                        if ans:
                            vote_count[ans] = vote_count.get(ans, 0) + 1

                    vote_summary = ", ".join([f"{k}={v}" for k, v in sorted(vote_count.items(), key=lambda x: -x[1])])

                    task = f"""{totem_info['instruction']}

QUESTION:
{formatted_q}

COUNCIL VOTES: {vote_summary or 'No clear votes'}

Make the FINAL decision. Respond with ONLY the letter (A, B, C, etc.)."""

                response = await client.post(
                    f"{CRONUS_API}/execute",
                    json={"task": task, "totem": totem}
                )

                if response.status_code == 200:
                    data = response.json()
                    result = str(data.get("result", ""))
                    all_responses.append(result)
                    agents_used.append(data.get("agent_used", totem))

                    # Extract this totem's answer
                    answer = extract_answer(result)
                    all_answers.append(answer)
                    # Progress indicator
                    print(f"            [{totem_info['name']}] -> {answer or '?'}", flush=True)
                else:
                    all_responses.append(f"ERROR:{response.status_code}")
                    all_answers.append("")
                    print(f"            [{totem_info['name']}] -> HTTP {response.status_code}", flush=True)

            # Return the final synthesis
            return {
                "success": True,
                "result": all_responses[-1] if all_responses else "",
                "all_responses": all_responses,
                "all_answers": all_answers,
                "agents_used": agents_used
            }
    except httpx.TimeoutException as e:
        return {"success": False, "error": f"Timeout after {len(all_responses)} totems"}
    except Exception as e:
        return {"success": False, "error": f"{type(e).__name__}: {str(e)[:100]}"}


async def run_council_benchmark(samples_per_category: int = 5):
    """Run MMLU-Pro benchmark with FULL COSMIC COUNCIL"""
    print("=" * 70)
    print("MMLU-PRO - FULL COSMIC COUNCIL BENCHMARK")
    print("=" * 70)
    print("All 6 totems deliberate on each question in ROYGBV order:")
    print("  Red Owl -> Orange Orangutan -> Yellow Honeybee ->")
    print("  Green Tortoise -> Blue Dolphin -> Purple Elephant (synthesis)")
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

        # Random sample
        sample = random.sample(items, min(samples_per_category, len(items)))

        print(f"[COUNCIL] {category.upper()}")
        print(f"          Testing {len(sample)} questions with full 6-totem deliberation")

        correct = 0
        for i, item in enumerate(sample):
            question = item["question"]
            options = item["options"]
            answer_idx = item["answer_index"]
            expected = chr(65 + answer_idx)

            start = time.time()
            response = await call_full_council(question, options)
            elapsed = time.time() - start

            if response["success"]:
                model_answer = extract_answer(str(response["result"]))
                is_correct = model_answer == expected
                if is_correct:
                    correct += 1
                status = "PASS" if is_correct else "FAIL"

                # Show vote distribution
                votes = response.get("all_answers", [])
                vote_str = "".join([v or "?" for v in votes])

                print(f"          Q{i+1}: [{status}] exp={expected} got={model_answer or '?'} votes=[{vote_str}] ({elapsed:.1f}s)")
            else:
                err = response.get('error', 'Unknown')[:40]
                print(f"          Q{i+1}: [ERROR] {err}")

        accuracy = (correct / len(sample)) * 100 if sample else 0
        results[category] = {
            "correct": correct,
            "total": len(sample),
            "accuracy": accuracy
        }
        total_correct += correct
        total_questions += len(sample)
        print(f"          Score: {correct}/{len(sample)} ({accuracy:.1f}%)")
        print()

    overall = (total_correct / total_questions) * 100 if total_questions else 0

    print("=" * 70)
    print("FULL COSMIC COUNCIL BENCHMARK RESULTS")
    print("=" * 70)
    print(f"{'Category':<20} {'Score':>10} {'Accuracy':>10}")
    print("-" * 42)
    for cat in sorted(results.keys()):
        res = results[cat]
        print(f"{cat:<20} {res['correct']:>3}/{res['total']:<6} {res['accuracy']:>8.1f}%")
    print("-" * 42)
    print(f"{'OVERALL':<20} {total_correct:>3}/{total_questions:<6} {overall:>8.1f}%")
    print()

    # Comparison
    print("Comparison:")
    print(f"  Individual totem routing:  39.3%")
    print(f"  Full Council (6 totems):   {overall:.1f}%")
    print()

    # Save results
    output = {
        "timestamp": datetime.now().isoformat(),
        "benchmark": "MMLU-Pro",
        "method": "full_cosmic_council",
        "totems_used": ROYGBV_SEQUENCE,
        "samples_per_category": samples_per_category,
        "total_questions": total_questions,
        "total_correct": total_correct,
        "overall_accuracy": overall,
        "results_by_category": results
    }
    with open("mmlu_pro_council_results.json", "w") as f:
        json.dump(output, f, indent=2)
    print(f"Results saved to: mmlu_pro_council_results.json")

    return output


if __name__ == "__main__":
    samples = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    asyncio.run(run_council_benchmark(samples))
