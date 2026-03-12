"""
RAG Knowledge Base for Cosmic Council Totems
Retrieval-Augmented Generation to improve expert-level accuracy
"""

import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from pathlib import Path

@dataclass
class KnowledgeFact:
    """A single fact in the knowledge base"""
    domain: str
    topic: str
    fact: str
    keywords: List[str]
    source: str = "curated"


# Physics Constants and Formulas
PHYSICS_KNOWLEDGE = [
    KnowledgeFact("physics", "particles", "A proton contains exactly 3 quarks: 2 up quarks and 1 down quark", ["proton", "quark", "particle"]),
    KnowledgeFact("physics", "particles", "A neutron contains exactly 3 quarks: 1 up quark and 2 down quarks", ["neutron", "quark", "particle"]),
    KnowledgeFact("physics", "constants", "The fine structure constant alpha is approximately 1/137 or 0.007297", ["fine structure", "alpha", "constant"]),
    KnowledgeFact("physics", "constants", "Speed of light c = 299,792,458 m/s or approximately 3.00 x 10^8 m/s", ["speed", "light", "constant"]),
    KnowledgeFact("physics", "constants", "Planck's constant h = 6.626 x 10^-34 J*s", ["planck", "constant"]),
    KnowledgeFact("physics", "constants", "Elementary charge e = 1.602 x 10^-19 coulombs", ["charge", "electron", "coulomb"]),
    KnowledgeFact("physics", "relativity", "Schwarzschild radius r_s = 2GM/c^2 where the exponent of c is 2", ["schwarzschild", "radius", "black hole"]),
    KnowledgeFact("physics", "relativity", "Lorentz factor gamma = 1/sqrt(1-v^2/c^2), equals 1 when v=0", ["lorentz", "factor", "gamma", "relativity"]),
    KnowledgeFact("physics", "quantum", "Momentum operator in quantum mechanics is -i*hbar*d/dx", ["momentum", "operator", "quantum"]),
]

# Biology and Medicine Facts
BIOLOGY_KNOWLEDGE = [
    KnowledgeFact("biology", "genetics", "Human genome contains approximately 3 billion base pairs", ["genome", "base pair", "dna"]),
    KnowledgeFact("biology", "cell", "Mitochondria is the powerhouse of the cell, producing ATP", ["mitochondria", "powerhouse", "cell", "atp"]),
    KnowledgeFact("biology", "genetics", "In DNA, Adenine pairs with Thymine (A-T), Guanine pairs with Cytosine (G-C)", ["adenine", "thymine", "base pair", "dna"]),
    KnowledgeFact("biology", "genetics", "Humans have 46 chromosomes (23 pairs) in somatic cells", ["chromosome", "human", "cell"]),
    KnowledgeFact("biology", "genetics", "Helicase is the enzyme that unzips DNA during replication", ["helicase", "enzyme", "dna", "replication"]),
    KnowledgeFact("biology", "anatomy", "Human body temperature is normally 37 degrees Celsius or 98.6 Fahrenheit", ["temperature", "body", "celsius"]),
    KnowledgeFact("biology", "anatomy", "The human heart has exactly 4 chambers: 2 atria and 2 ventricles", ["heart", "chamber", "atria", "ventricle"]),
    KnowledgeFact("biology", "anatomy", "Humans have 206 bones in the adult skeleton", ["bones", "skeleton", "anatomy"]),
]

# Chemistry Facts
CHEMISTRY_KNOWLEDGE = [
    KnowledgeFact("chemistry", "elements", "Carbon has atomic number 6", ["carbon", "atomic number", "element"]),
    KnowledgeFact("chemistry", "elements", "The periodic table has 118 confirmed elements", ["periodic table", "elements", "number"]),
    KnowledgeFact("chemistry", "compounds", "Water has chemical formula H2O (two hydrogen, one oxygen)", ["water", "h2o", "formula", "chemical"]),
    KnowledgeFact("chemistry", "constants", "Avogadro's number is approximately 6.022 x 10^23 particles per mole", ["avogadro", "number", "mole"]),
    KnowledgeFact("chemistry", "properties", "Pure water at 25°C has pH of exactly 7 (neutral)", ["ph", "water", "neutral"]),
    KnowledgeFact("chemistry", "elements", "Helium has atomic number 2, is a noble gas", ["helium", "noble gas", "atomic number"]),
    KnowledgeFact("chemistry", "elements", "Oxygen has atomic number 8", ["oxygen", "atomic number"]),
    KnowledgeFact("chemistry", "elements", "Gold has atomic number 79, symbol Au", ["gold", "au", "atomic number"]),
]

# Mathematics Facts
MATH_KNOWLEDGE = [
    KnowledgeFact("math", "calculus", "Derivative of x^x is x^x * (ln(x) + 1)", ["derivative", "x^x", "calculus"]),
    KnowledgeFact("math", "group_theory", "Order of symmetric group S_n is n! (n factorial). S_4 = 4! = 24", ["symmetric group", "order", "factorial"]),
    KnowledgeFact("math", "series", "Geometric series 1/2 + 1/4 + 1/8 + ... = 1 (sum to infinity)", ["geometric", "series", "sum"]),
    KnowledgeFact("math", "analysis", "Riemann zeta function zeta(2) = pi^2/6", ["riemann", "zeta", "pi"]),
    KnowledgeFact("math", "number_theory", "Primes less than 20: 2,3,5,7,11,13,17,19 (8 total)", ["prime", "number", "less than 20"]),
    KnowledgeFact("math", "topology", "Euler characteristic of sphere is 2", ["euler", "characteristic", "sphere"]),
    KnowledgeFact("math", "topology", "Coffee mug is homeomorphic to a torus (donut shape)", ["homeomorphic", "torus", "coffee mug", "topology"]),
    KnowledgeFact("math", "arithmetic", "7! = 7 factorial = 5040", ["factorial", "7!"]),
]


class RAGKnowledgeBase:
    """Simple RAG knowledge base for Cosmic Council"""

    def __init__(self):
        self.knowledge: Dict[str, List[KnowledgeFact]] = {
            "physics": PHYSICS_KNOWLEDGE,
            "biology": BIOLOGY_KNOWLEDGE,
            "chemistry": CHEMISTRY_KNOWLEDGE,
            "math": MATH_KNOWLEDGE,
        }

    def retrieve(self, query: str, domain: Optional[str] = None, top_k: int = 3) -> List[KnowledgeFact]:
        """Retrieve relevant facts for a query"""
        query_lower = query.lower()
        results = []

        # Determine which knowledge bases to search
        if domain:
            domains = [domain]
        else:
            domains = list(self.knowledge.keys())

        for d in domains:
            if d not in self.knowledge:
                continue

            for fact in self.knowledge[d]:
                # Score based on keyword matches
                score = 0
                for keyword in fact.keywords:
                    if keyword.lower() in query_lower:
                        score += 1

                # Also check if topic matches
                if fact.topic.lower() in query_lower:
                    score += 0.5

                if score > 0:
                    results.append((score, fact))

        # Sort by score and return top_k
        results.sort(key=lambda x: x[0], reverse=True)
        return [fact for _, fact in results[:top_k]]

    def format_context(self, facts: List[KnowledgeFact]) -> str:
        """Format retrieved facts as context for the LLM"""
        if not facts:
            return ""

        lines = ["Relevant knowledge:"]
        for fact in facts:
            lines.append(f"- {fact.fact}")

        return "\n".join(lines)


def get_enhanced_prompt(question: str, domain: str) -> str:
    """Generate RAG-enhanced prompt for a question

    Args:
        question: The question to answer
        domain: Domain name (physics, chemistry, biology, math) or totem name
    """
    kb = RAGKnowledgeBase()

    # Map totems to domains (for backward compatibility)
    totem_domains = {
        "red": ["math", "physics"],
        "green": ["physics", "chemistry"],
        "yellow": ["biology"],
        "orange": None,  # General
        "blue": None,    # General
        "purple": None,  # General
    }

    # Direct domain names also supported
    direct_domains = ["physics", "chemistry", "biology", "math"]

    if domain in direct_domains:
        # Direct domain lookup
        facts = kb.retrieve(question, domain, top_k=3)
    elif domain in totem_domains:
        # Totem-based lookup
        mapped = totem_domains.get(domain)
        if isinstance(mapped, list):
            facts = []
            for d in mapped:
                facts.extend(kb.retrieve(question, d, top_k=2))
        else:
            facts = kb.retrieve(question, mapped, top_k=3)
    else:
        # General search across all domains
        facts = kb.retrieve(question, None, top_k=3)

    context = kb.format_context(facts)

    if context:
        return f"""{context}

Question: {question}

Answer precisely and concisely."""
    else:
        return f"Question: {question}\n\nAnswer precisely and concisely."


# Domain-specific prompt templates
DOMAIN_PROMPTS = {
    "physics": """You are an expert physicist. When answering:
- State relevant formulas or constants
- Show your reasoning
- Give precise numerical answers
- Include units when appropriate""",

    "chemistry": """You are an expert chemist. When answering:
- Use proper chemical notation (H2O, not "water")
- State molecular formulas precisely
- Include atomic numbers when relevant""",

    "biology": """You are an expert biologist. When answering:
- Use proper scientific terminology
- Be precise with numbers (exact counts, not approximations)
- State anatomical facts accurately""",

    "math": """You are an expert mathematician. When answering:
- Show the key steps in your reasoning
- State formulas used
- Give exact numerical answers""",
}


def get_system_prompt(domain: str) -> str:
    """Get domain-specific system prompt"""
    return DOMAIN_PROMPTS.get(domain, "You are a knowledgeable expert. Answer precisely and concisely.")
