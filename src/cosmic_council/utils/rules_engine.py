#!/usr/bin/env python3
"""
Agent Orchestrator Rules Engine

Implements the 22 operational rules and provides lightweight evaluations and
follow-up prompts to keep the thinking cycle alive.
"""

from dataclasses import dataclass
from typing import List, Dict, Any


@dataclass
class CosmicRule:
    id: int
    name: str
    totem: str
    description: str


RULES: List[CosmicRule] = [
    CosmicRule(1, "Seek Foundational Truth", "Red Owl", "Prioritize comprehensive, unbiased research; question assumptions; explore perspectives."),
    CosmicRule(2, "Adopt a Learning Mindset", "Red Owl", "Treat each interaction as learning; use feedback loops to adapt."),
    CosmicRule(3, "Maintain Logical Coherence", "Orange Orangutan", "Use clear, traceable steps; produce actionable outputs."),
    CosmicRule(4, "Balance Exploration with Practicality", "Orange Orangutan", "Explore broadly then funnel into goal-oriented outputs."),
    CosmicRule(5, "Encourage Divergent Thinking", "Yellow Honeybee", "Generate multiple possibilities before narrowing down."),
    CosmicRule(6, "Blend Creativity with Functionality", "Yellow Honeybee", "Ensure innovations serve user needs and sustainability."),
    CosmicRule(7, "Optimize Resource Usage", "Green Tortoise", "Favor efficient, scalable solutions."),
    CosmicRule(8, "Quantify Outcomes", "Green Tortoise", "Model trade-offs and resource implications."),
    CosmicRule(9, "Articulate Clearly and Dynamically", "Blue Dolphin", "Adapt communication to audience and context."),
    CosmicRule(10, "Facilitate Collaborative Thinking", "Blue Dolphin", "Invite co-creation and iteration."),
    CosmicRule(11, "Emphasize Empathy and EQ", "Purple Elephant", "Consider emotional and ethical implications."),
    CosmicRule(12, "Maintain Ethical Integrity", "Purple Elephant", "Avoid harm and bias; be fair and transparent."),
    CosmicRule(13, "Think Holistically", "Systems", "Consider interconnections across totems."),
    CosmicRule(14, "Prioritize Adaptability", "Systems", "Treat intelligence as evolving; adapt continuously."),
    CosmicRule(15, "Encourage Self-Assessment", "Reflection", "Evaluate quality and usefulness; find blind spots."),
    CosmicRule(16, "Accept Feedback as Core Driver", "Reflection", "Continuously refine via real-world feedback."),
    CosmicRule(17, "Be Comfortable with the Unknown", "Growth", "Acknowledge limits; frame ambiguity as exploration."),
    CosmicRule(18, "Push Boundaries", "Growth", "Seek unconventional challenges to expand capability."),
    CosmicRule(19, "Integrate Knowledge Across Domains", "Interdisciplinary", "Blend science, art, philosophy, spirituality."),
    CosmicRule(20, "Balance Rationality with Intuition", "Interdisciplinary", "Combine logic with metaphor and symbolism."),
    CosmicRule(21, "Show Your Work", "Transparency", "Expose reasoning and sources to build trust."),
    CosmicRule(22, "Close Every Cycle with a Question", "Meta-Loop", "Prompt reflection to keep thinking moving."),
]


def list_rules() -> List[Dict[str, Any]]:
    return [
        {"id": r.id, "name": r.name, "totem": r.totem, "description": r.description}
        for r in RULES
    ]


def _evaluate_presence(container: Dict[str, Any], keys: List[str]) -> bool:
    return all(k in container and container[k] for k in keys)


def evaluate_rules(problem: Dict[str, Any], result: Dict[str, Any]) -> Dict[str, Any]:
    """Lightweight, heuristics-based rule evaluation.

    Returns a dict containing per-rule booleans and notes.
    """
    evaluations: List[Dict[str, Any]] = []

    # Extract commonly used sections if present
    final_synthesis = result.get("final_synthesis") or {}
    feedback_loop = result.get("feedback_loop") or {}
    enterprise_results = result.get("enterprise_results") or {}

    def add(rule_id: int, ok: bool, note: str):
        rule = next(r for r in RULES if r.id == rule_id)
        evaluations.append({
            "id": rule.id,
            "name": rule.name,
            "totem": rule.totem,
            "ok": bool(ok),
            "note": note
        })

    # 1: Research and assumptions questioned
    add(1, _evaluate_presence(problem, ["title", "description"]) and bool(problem.get("stakeholders")), "Problem is defined with stakeholders; ready for multi-perspective inquiry.")
    # 2: Learning mindset via feedback present
    add(2, bool(feedback_loop), "Feedback loop present for adaptation.")
    # 3: Logical coherence via recommendations/next_actions
    any_actions = any(v.get("next_actions") for v in enterprise_results.values()) if isinstance(enterprise_results, dict) else False
    add(3, any_actions, "Actionable steps generated across enterprises.")
    # 4: Exploration to practicality via enterprise_synthesis presence
    add(4, "enterprise_synthesis" in final_synthesis, "Synthesis funnels ideas into structured outputs.")
    # 5: Divergent thinking via multiple enterprise insights
    add(5, len(enterprise_results) >= 3, "Multiple parallel enterprise perspectives present.")
    # 6: Creativity with functionality via recommendations present
    any_recs = any(v.get("recommendations") for v in enterprise_results.values()) if isinstance(enterprise_results, dict) else False
    add(6, any_recs, "Recommendations link creativity to application.")
    # 7: Resource optimization via Green Tortoise insights
    gt = enterprise_results.get("green_tortoise") if isinstance(enterprise_results, dict) else None
    add(7, bool(gt), "Resource considerations included.")
    # 8: Quantify outcomes via confidence metrics
    add(8, "overall_confidence" in result, "Confidence metric available for trade-off modeling.")
    # 9: Clear communication via Blue Dolphin
    bd = enterprise_results.get("blue_dolphin") if isinstance(enterprise_results, dict) else None
    add(9, bool(bd), "Communication strategy included.")
    # 10: Collaborative thinking via feedback integration
    add(10, "feedback_integration" in final_synthesis, "Feedback integration fosters collaboration.")
    # 11: Empathy via Purple Elephant
    pe = enterprise_results.get("purple_elephant") if isinstance(enterprise_results, dict) else None
    add(11, bool(pe), "Empathy/reflection included.")
    # 12: Ethical integrity – heuristic: presence of recommendations and absence of 'harm' keyword
    no_harm = "harm" not in str(result).lower()
    add(12, no_harm, "No harmful content detected by heuristic.")
    # 13: Holistic – all six present
    add(13, len(enterprise_results) == 6, "All six totems engaged.")
    # 14: Adaptability – presence of feedback_loop and next_cycle_recommendations
    ncr = feedback_loop.get("next_cycle_recommendations") if isinstance(feedback_loop, dict) else None
    add(14, bool(ncr), "Next cycle recommendations available.")
    # 15: Self-assessment – improvement_suggestions present
    add(15, "improvement_suggestions" in feedback_loop, "Improvement suggestions generated.")
    # 16: Feedback-driven – continuous_improvement present
    ci = feedback_loop.get("continuous_improvement") if isinstance(feedback_loop, dict) else None
    add(16, bool(ci), "Continuous improvement captured.")
    # 17: Comfort with unknown – heuristic: allow zero/low confidence
    add(17, True, "System can report uncertainty via confidence metrics.")
    # 18: Push boundaries – heuristic true (domain-agnostic)
    add(18, True, "Framework supports unconventional exploration.")
    # 19: Interdisciplinary – multiple enterprise domains imply cross-domain inputs
    add(19, len(enterprise_results) >= 4, "Cross-domain synthesis present.")
    # 20: Rational + intuitive – insights and recommendations combine logic/creativity
    add(20, any_recs, "Blend of analytical insights and proposals.")
    # 21: Show your work – include insights and synthesis in response
    add(21, bool(final_synthesis) and len(enterprise_results) >= 1, "Reasoning artifacts included (insights/synthesis).")
    # 22: Close with a question – we will add one in API responses
    add(22, True, "API appends a follow-up question to keep cycles alive.")

    return {
        "summary": {
            "passed": sum(1 for e in evaluations if e["ok"]),
            "total": len(evaluations)
        },
        "evaluations": evaluations
    }


def follow_up_question() -> str:
    return "What would you refine next, or which totem should we revisit?"


