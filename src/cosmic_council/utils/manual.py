#!/usr/bin/env python3
"""
Agent Orchestrator Instruction Manual
Implements the six-step problem-solving process with key principles and examples.
"""

from typing import Dict, Any, List
from datetime import datetime, timezone


def get_manual() -> Dict[str, Any]:
    return {
        "title": "Instruction Manual for Solving Personal, Interpersonal, or Global Problems",
        "framework": "Agent Orchestrator",
        "steps": [
            {
                "step": 1,
                "totem": "Red Owl",
                "emoji": "🔴🦉",
                "name": "Define the Problem Clearly",
                "purpose": "Root understanding in facts, context, and knowledge.",
                "process": [
                    "Clarify the core problem",
                    "Break down goals, obstacles, stakeholders",
                    "Research context comprehensively",
                    "Identify underlying causes"
                ],
                "outcome": "Clear definition + list of research questions"
            },
            {
                "step": 2,
                "totem": "Orange Orangutan",
                "emoji": "🟠🦧",
                "name": "Plan and Strategize",
                "purpose": "Structure the path forward with actionable steps.",
                "process": [
                    "Identify objectives",
                    "Create phased plan",
                    "Anticipate challenges and contingencies",
                    "List required resources/tools"
                ],
                "outcome": "Detailed roadmap"
            },
            {
                "step": 3,
                "totem": "Yellow Honeybee",
                "emoji": "🟡🐝",
                "name": "Generate Creative Solutions",
                "purpose": "Explore innovative, diverse approaches.",
                "process": [
                    "Brainstorm multiple solutions",
                    "Use metaphors/visualization/role-play",
                    "Combine ideas into hybrids",
                    "Reflect on creativity's impact/sustainability"
                ],
                "outcome": "Range of solutions/prototypes"
            },
            {
                "step": 4,
                "totem": "Green Turtle",
                "emoji": "🟢🐢",
                "name": "Evaluate Resources and Feasibility",
                "purpose": "Ensure practicality, sustainability, achievability.",
                "process": [
                    "Assess financial/emotional/time resources",
                    "Consider long-term sustainability",
                    "Identify resource gaps and mitigation",
                    "Weigh trade-offs and compromises"
                ],
                "outcome": "Refined, resource-conscious solution"
            },
            {
                "step": 5,
                "totem": "Blue Dolphin",
                "emoji": "🔵🐬",
                "name": "Communicate and Engage Stakeholders",
                "purpose": "Gain support, alignment, and trust.",
                "process": [
                    "Identify who to involve or inform",
                    "Develop persuasive communication strategy",
                    "Use storytelling/data/visuals",
                    "Anticipate perceptions and responses"
                ],
                "outcome": "Communication plan for buy-in and awareness"
            },
            {
                "step": 6,
                "totem": "Purple Elephant",
                "emoji": "🟣🐘",
                "name": "Reflect and Iterate",
                "purpose": "Assess results, integrate feedback, improve continuously.",
                "process": [
                    "Test/implement on small scale",
                    "Gather feedback or self-reflect",
                    "Analyze what worked or not and why",
                    "Capture new questions for next cycle"
                ],
                "outcome": "Continuous learning and iteration"
            }
        ],
        "key_principles": [
            "Holistic Thinking",
            "Cyclical Process",
            "Emotional Intelligence",
            "Quantum Perspective"
        ],
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


def get_examples() -> Dict[str, Any]:
    return {
        "personal": {
            "scenario": "Career change",
            "outline": [
                "Red Owl: Research interests/strengths/market; identify what's missing",
                "Orange Orangutan: Plan exploration, update resume, take courses",
                "Yellow Honeybee: Brainstorm creative paths and side projects",
                "Green Turtle: Assess financial/time resources",
                "Blue Dolphin: Network and communicate goals",
                "Purple Elephant: Reflect on feedback and refine"
            ]
        },
        "global": {
            "scenario": "Climate change initiative",
            "outline": [
                "Red Owl: Research local environmental issues",
                "Orange Orangutan: Plan community initiative",
                "Yellow Honeybee: Creative engagement (events/apps/challenges)",
                "Green Turtle: Evaluate costs/resources; secure funding",
                "Blue Dolphin: Communicate via media and town halls",
                "Purple Elephant: Gather feedback; measure impact; refine"
            ]
        },
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


