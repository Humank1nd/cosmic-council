"""
WHITE RABBIT - Intent Classifier.

Classifies the intent of input prompts.
This implements Criterion 2: Intent classification.

The intent/type of inquiry must be correctly identified.
"""

import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime

import structlog

from .models import (
    InputPrompt,
    InputType,
    Intent,
    IntentCategory,
    UrgencyLevel,
    WhiteRabbitConfig,
)

logger = structlog.get_logger(__name__)


@dataclass
class ClassificationResult:
    """Result of intent classification."""
    intent: Intent
    alternative_intents: List[Intent] = field(default_factory=list)
    classification_confidence: float = 0.0
    processing_time_ms: int = 0


@dataclass
class BatchClassificationResult:
    """Result of classifying multiple prompts."""
    results: List[ClassificationResult] = field(default_factory=list)
    total_classified: int = 0
    average_confidence: float = 0.0
    duration_ms: int = 0


class IntentClassifier:
    """
    Classifies the intent of input prompts.

    Criterion 2: The intent/type of inquiry is correctly identified.
    """

    # Intent keyword patterns
    INTENT_PATTERNS: Dict[IntentCategory, List[str]] = {
        IntentCategory.INQUIRY: [
            r"\bwhy\b", r"\bhow\b", r"\bwhat\b", r"\bwhen\b", r"\bwhere\b", r"\bwho\b",
            r"\bexplain\b", r"\bdescribe\b", r"\bunderstand\b", r"\bclarify\b",
            r"\?$", r"\bquestion\b", r"\bcurious\b", r"\bwonder\b",
        ],
        IntentCategory.ACTION: [
            r"\bdo\b", r"\bexecute\b", r"\bperform\b", r"\brun\b", r"\bstart\b",
            r"\bstop\b", r"\brestart\b", r"\bdeploy\b", r"\binstall\b",
            r"\bplease\b", r"\bneed to\b", r"\bwant to\b", r"\bshould\b",
        ],
        IntentCategory.ANALYSIS: [
            r"\banalyze\b", r"\binvestigate\b", r"\bexamine\b", r"\breview\b",
            r"\bcompare\b", r"\bassess\b", r"\bevaluate\b", r"\baudit\b",
            r"\bcheck\b", r"\bdiagnose\b", r"\btroubleshoot\b",
        ],
        IntentCategory.CREATION: [
            r"\bcreate\b", r"\bbuild\b", r"\bgenerate\b", r"\bmake\b",
            r"\bdesign\b", r"\bdevelop\b", r"\bimplement\b", r"\bwrite\b",
            r"\bnew\b", r"\badd\b", r"\bset up\b",
        ],
        IntentCategory.OPTIMIZATION: [
            r"\boptimize\b", r"\bimprove\b", r"\benhance\b", r"\bspeed up\b",
            r"\breduce\b", r"\bminimize\b", r"\bmaximize\b", r"\befficient\b",
            r"\bperformance\b", r"\bscale\b", r"\btuning\b",
        ],
        IntentCategory.RESOLUTION: [
            r"\bfix\b", r"\bresolve\b", r"\bsolve\b", r"\brepair\b",
            r"\berror\b", r"\bbug\b", r"\bissue\b", r"\bproblem\b",
            r"\bfailing\b", r"\bbroken\b", r"\bcrash\b",
        ],
        IntentCategory.MONITORING: [
            r"\bmonitor\b", r"\bwatch\b", r"\btrack\b", r"\bobserve\b",
            r"\balert\b", r"\bnotify\b", r"\breport\b", r"\bstatus\b",
            r"\bmetric\b", r"\blog\b", r"\bdashboard\b",
        ],
        IntentCategory.FEEDBACK: [
            r"\bfeedback\b", r"\bresult\b", r"\boutcome\b", r"\bcompleted\b",
            r"\bfinished\b", r"\binsight\b", r"\blearning\b", r"\bcontinue\b",
        ],
    }

    # Urgency patterns
    URGENCY_PATTERNS: Dict[UrgencyLevel, List[str]] = {
        UrgencyLevel.CRITICAL: [
            r"\bcritical\b", r"\bemergency\b", r"\burgent\b", r"\basap\b",
            r"\bimmediately\b", r"\bdown\b", r"\boutage\b", r"\bsev[- ]?1\b",
        ],
        UrgencyLevel.HIGH: [
            r"\bhigh priority\b", r"\bimportant\b", r"\bsoon\b",
            r"\bsev[- ]?2\b", r"\bescalate\b",
        ],
        UrgencyLevel.LOW: [
            r"\blow priority\b", r"\bwhen you can\b", r"\bno rush\b",
            r"\beventually\b", r"\bbacklog\b",
        ],
    }

    def __init__(
        self,
        config: Optional[WhiteRabbitConfig] = None,
    ):
        """
        Initialize the intent classifier.

        Args:
            config: Configuration
        """
        self.config = config or WhiteRabbitConfig()

        # Compile patterns
        self._intent_patterns = {
            category: [re.compile(p, re.IGNORECASE) for p in patterns]
            for category, patterns in self.INTENT_PATTERNS.items()
        }
        self._urgency_patterns = {
            level: [re.compile(p, re.IGNORECASE) for p in patterns]
            for level, patterns in self.URGENCY_PATTERNS.items()
        }

        # Track classifications
        self._classified_count: int = 0
        self._confidence_sum: float = 0.0

        logger.info("intent_classifier_initialized")

    def classify(
        self,
        prompt: InputPrompt,
        context: Optional[Dict[str, Any]] = None,
    ) -> ClassificationResult:
        """
        Classify the intent of a prompt.

        Args:
            prompt: Input prompt to classify
            context: Additional context

        Returns:
            ClassificationResult
        """
        import time
        start_time = time.time()
        context = context or {}

        content = prompt.content.lower()

        # Handle feedback type specially
        if prompt.input_type == InputType.FEEDBACK:
            intent = self._classify_feedback(prompt, context)
        else:
            # Classify intent category
            category, confidence = self._classify_category(content)

            # Classify urgency
            urgency = self._classify_urgency(content)

            # Extract entities and keywords
            entities = self._extract_entities(content)
            keywords = self._extract_keywords(content)

            # Determine subject and action
            subject = self._extract_subject(content)
            action_requested = self._extract_action(content, category)

            # Assess complexity
            complexity = self._assess_complexity(content, entities)

            # Generate initial questions for Red Owl
            initial_questions = self._generate_initial_questions(
                content, category, subject
            )

            # Generate suggested hypotheses
            suggested_hypotheses = self._generate_hypotheses(
                content, category, subject
            )

            intent = Intent(
                prompt_id=prompt.id,
                category=category,
                confidence=confidence,
                subject=subject,
                action_requested=action_requested,
                entities=entities,
                keywords=keywords,
                urgency=urgency,
                complexity=complexity,
                initial_questions=initial_questions,
                suggested_hypotheses=suggested_hypotheses,
            )

        # Find alternative interpretations
        alternatives = self._find_alternatives(prompt, intent)

        # Update tracking
        self._classified_count += 1
        self._confidence_sum += intent.confidence

        processing_time = int((time.time() - start_time) * 1000)

        logger.debug(
            "intent_classified",
            prompt_id=prompt.id,
            category=intent.category.value,
            confidence=intent.confidence,
            urgency=intent.urgency.value,
        )

        return ClassificationResult(
            intent=intent,
            alternative_intents=alternatives,
            classification_confidence=intent.confidence,
            processing_time_ms=processing_time,
        )

    def classify_batch(
        self,
        prompts: List[InputPrompt],
        context: Optional[Dict[str, Any]] = None,
    ) -> BatchClassificationResult:
        """
        Classify multiple prompts.

        Args:
            prompts: List of prompts
            context: Shared context

        Returns:
            BatchClassificationResult
        """
        import time
        start_time = time.time()

        results: List[ClassificationResult] = []
        total_confidence = 0.0

        for prompt in prompts:
            result = self.classify(prompt, context)
            results.append(result)
            total_confidence += result.classification_confidence

        duration_ms = int((time.time() - start_time) * 1000)
        avg_confidence = total_confidence / len(prompts) if prompts else 0.0

        logger.info(
            "batch_classification_complete",
            total=len(prompts),
            avg_confidence=avg_confidence,
            duration_ms=duration_ms,
        )

        return BatchClassificationResult(
            results=results,
            total_classified=len(results),
            average_confidence=avg_confidence,
            duration_ms=duration_ms,
        )

    def _classify_category(self, content: str) -> Tuple[IntentCategory, float]:
        """Classify the intent category."""
        scores: Dict[IntentCategory, int] = {cat: 0 for cat in IntentCategory}

        for category, patterns in self._intent_patterns.items():
            for pattern in patterns:
                if pattern.search(content):
                    scores[category] += 1

        # Find highest scoring category
        max_score = max(scores.values())
        if max_score == 0:
            return self.config.default_intent_category, 0.5

        # Calculate confidence based on score difference
        best_category = max(scores, key=scores.get)
        total_matches = sum(scores.values())
        confidence = min(0.5 + (max_score / max(total_matches, 1)) * 0.5, 1.0)

        return best_category, confidence

    def _classify_urgency(self, content: str) -> UrgencyLevel:
        """Classify urgency level."""
        for level, patterns in self._urgency_patterns.items():
            for pattern in patterns:
                if pattern.search(content):
                    return level
        return UrgencyLevel.NORMAL

    def _extract_entities(self, content: str) -> List[str]:
        """Extract named entities from content."""
        entities = []

        # Extract quoted strings
        quoted = re.findall(r'"([^"]+)"', content)
        entities.extend(quoted)
        quoted = re.findall(r"'([^']+)'", content)
        entities.extend(quoted)

        # Extract service-like names (word-word pattern)
        services = re.findall(r"\b([a-z]+-[a-z]+(?:-[a-z]+)*)\b", content)
        entities.extend(services)

        # Extract paths
        paths = re.findall(r"(/[a-zA-Z0-9_/-]+)", content)
        entities.extend(paths)

        return list(set(entities))[:10]  # Limit

    def _extract_keywords(self, content: str) -> List[str]:
        """Extract key terms from content."""
        # Remove common stop words
        stop_words = {
            "the", "a", "an", "is", "are", "was", "were", "be", "been",
            "being", "have", "has", "had", "do", "does", "did", "will",
            "would", "could", "should", "may", "might", "must", "shall",
            "can", "to", "of", "in", "for", "on", "with", "at", "by",
            "from", "as", "into", "through", "during", "before", "after",
            "above", "below", "between", "under", "again", "further",
            "then", "once", "here", "there", "when", "where", "why",
            "how", "all", "each", "every", "both", "few", "more", "most",
            "other", "some", "such", "no", "nor", "not", "only", "own",
            "same", "so", "than", "too", "very", "just", "and", "but",
            "if", "or", "because", "until", "while", "this", "that",
            "these", "those", "it", "its", "i", "me", "my", "we", "our",
            "you", "your", "he", "she", "they", "them", "what", "which",
        }

        words = re.findall(r"\b[a-z]{3,}\b", content)
        keywords = [w for w in words if w not in stop_words]

        # Return unique keywords, most common first
        from collections import Counter
        counts = Counter(keywords)
        return [w for w, _ in counts.most_common(10)]

    def _extract_subject(self, content: str) -> str:
        """Extract the main subject of the input."""
        # Simple heuristic: look for noun phrases after key verbs
        patterns = [
            r"(?:about|regarding|concerning)\s+(.+?)(?:\.|$)",
            r"(?:the|a|an)\s+(\w+(?:\s+\w+)?)\s+(?:is|are|has|have)",
            r"(?:check|analyze|investigate|review)\s+(?:the\s+)?(.+?)(?:\.|$)",
        ]

        for pattern in patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                return match.group(1).strip()[:100]

        # Fallback: first significant noun phrase
        words = content.split()[:10]
        return " ".join(words[:3]) if words else ""

    def _extract_action(self, content: str, category: IntentCategory) -> str:
        """Extract the requested action."""
        action_verbs = {
            IntentCategory.ACTION: ["do", "execute", "perform", "run", "start", "stop"],
            IntentCategory.ANALYSIS: ["analyze", "investigate", "examine", "review"],
            IntentCategory.CREATION: ["create", "build", "generate", "make", "develop"],
            IntentCategory.OPTIMIZATION: ["optimize", "improve", "enhance", "speed up"],
            IntentCategory.RESOLUTION: ["fix", "resolve", "solve", "repair"],
            IntentCategory.MONITORING: ["monitor", "watch", "track", "observe"],
        }

        verbs = action_verbs.get(category, [])
        for verb in verbs:
            pattern = rf"\b{verb}\b\s+(.+?)(?:\.|,|$)"
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                return f"{verb} {match.group(1).strip()[:50]}"

        return category.value

    def _assess_complexity(self, content: str, entities: List[str]) -> str:
        """Assess the complexity of the input."""
        # Heuristics for complexity
        word_count = len(content.split())
        entity_count = len(entities)
        question_count = content.count("?")
        conjunction_count = len(re.findall(r"\b(and|or|but|however|therefore)\b", content))

        complexity_score = (
            word_count / 20 +
            entity_count / 3 +
            question_count +
            conjunction_count / 2
        )

        if complexity_score < 2:
            return "simple"
        elif complexity_score < 5:
            return "medium"
        else:
            return "complex"

    def _generate_initial_questions(
        self,
        content: str,
        category: IntentCategory,
        subject: str,
    ) -> List[str]:
        """Generate initial questions for Red Owl."""
        questions = []

        if category == IntentCategory.RESOLUTION:
            questions.extend([
                f"What is the root cause of the issue with {subject}?",
                f"When did the problem with {subject} first occur?",
                f"What has changed recently that might affect {subject}?",
            ])
        elif category == IntentCategory.ANALYSIS:
            questions.extend([
                f"What patterns can we identify in {subject}?",
                f"What are the key metrics for {subject}?",
                f"How does {subject} compare to baseline?",
            ])
        elif category == IntentCategory.OPTIMIZATION:
            questions.extend([
                f"What are the current bottlenecks in {subject}?",
                f"What is the target state for {subject}?",
                f"What constraints apply to optimizing {subject}?",
            ])
        else:
            questions.extend([
                f"What is the current state of {subject}?",
                f"What are the requirements for {subject}?",
                f"Who are the stakeholders for {subject}?",
            ])

        return questions[:5]

    def _generate_hypotheses(
        self,
        content: str,
        category: IntentCategory,
        subject: str,
    ) -> List[str]:
        """Generate suggested hypotheses."""
        hypotheses = []

        if category == IntentCategory.RESOLUTION:
            hypotheses.extend([
                f"The issue with {subject} may be caused by recent changes",
                f"The problem could be related to resource constraints",
                f"External dependencies may be affecting {subject}",
            ])
        elif category == IntentCategory.OPTIMIZATION:
            hypotheses.extend([
                f"Caching could improve {subject} performance",
                f"Scaling resources may resolve bottlenecks",
                f"Configuration tuning could optimize {subject}",
            ])

        return hypotheses[:3]

    def _classify_feedback(
        self,
        prompt: InputPrompt,
        context: Dict[str, Any],
    ) -> Intent:
        """Classify feedback from Black Snake."""
        content = prompt.content.lower()
        metadata = prompt.metadata

        # Extract from metadata if available
        priority = metadata.get("priority", "medium")
        urgency_str = metadata.get("urgency", "normal")

        urgency_map = {
            "normal": UrgencyLevel.NORMAL,
            "soon": UrgencyLevel.HIGH,
            "immediate": UrgencyLevel.CRITICAL,
        }
        urgency = urgency_map.get(urgency_str, UrgencyLevel.NORMAL)

        # Get questions and hypotheses from feedback
        feedback = metadata.get("feedback", {})
        initial_questions = feedback.get("new_questions", [])
        suggested_hypotheses = feedback.get("hypotheses_to_test", [])

        return Intent(
            prompt_id=prompt.id,
            category=IntentCategory.FEEDBACK,
            confidence=0.9,  # High confidence for structured feedback
            subject="Previous cycle feedback",
            action_requested="Continue inquiry cycle",
            urgency=urgency,
            complexity="medium",
            initial_questions=initial_questions,
            suggested_hypotheses=suggested_hypotheses,
            metadata={"feedback_source": "black_snake"},
        )

    def _find_alternatives(
        self,
        prompt: InputPrompt,
        primary: Intent,
    ) -> List[Intent]:
        """Find alternative intent interpretations."""
        alternatives = []
        content = prompt.content.lower()

        # Score all categories
        scores: Dict[IntentCategory, int] = {cat: 0 for cat in IntentCategory}
        for category, patterns in self._intent_patterns.items():
            for pattern in patterns:
                if pattern.search(content):
                    scores[category] += 1

        # Get top alternatives (excluding primary)
        sorted_cats = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        for category, score in sorted_cats:
            if category != primary.category and score > 0:
                alt_intent = Intent(
                    prompt_id=prompt.id,
                    category=category,
                    confidence=min(score / 5, 0.8),
                    subject=primary.subject,
                )
                alternatives.append(alt_intent)
                if len(alternatives) >= 2:
                    break

        return alternatives

    def get_metrics(self) -> Dict[str, Any]:
        """Get classifier metrics."""
        return {
            "total_classified": self._classified_count,
            "average_confidence": (
                self._confidence_sum / self._classified_count
                if self._classified_count > 0 else 0.0
            ),
        }


def create_intent_classifier(
    config: Optional[WhiteRabbitConfig] = None,
) -> IntentClassifier:
    """Factory function to create an IntentClassifier."""
    return IntentClassifier(config=config)
