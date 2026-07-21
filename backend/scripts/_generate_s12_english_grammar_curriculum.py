"""One-shot generator: export English grammar curriculum YAML (S12 Wave A).

Usage (from backend/):
    python scripts/_generate_s12_english_grammar_curriculum.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.services.language_grammar.enums import GrammarCEFRBand as C  # noqa: E402
from app.services.language_grammar_catalog.builder import R, ev, topic  # noqa: E402
from app.services.language_grammar_catalog.english_catalog_v1 import (  # noqa: E402
    _raw_topics,
)
from app.services.language_grammar_catalog.types import GrammarTopic  # noqa: E402

OUT = Path(__file__).resolve().parents[1] / "curriculum" / "english" / "grammar"


def _new_topics() -> tuple[GrammarTopic, ...]:
    """Fifteen new topics to hit S12 CEFR quotas (A1=12 … C2=4)."""
    return (
        # A1 (+4)
        topic(
            "gram_object_pronouns",
            display_name="Object pronouns",
            cefr_band=C.A1,
            introduction_order=85,
            prerequisite_ids=("gram_personal_pronouns",),
            learning_objectives=(
                "Use object pronouns after verbs and prepositions",
                "Contrast subject vs object forms in short turns",
            ),
            demonstration_patterns=("me", "you", "him", "her", "it", "us", "them"),
            example_sentences=(
                "Can you help me?",
                "I saw them yesterday.",
            ),
            common_errors=(
                "Can you help I?",
                "I saw they yesterday.",
            ),
            best_reinforcement_skills=(R.speaking, R.listening),
            recommended_contexts=("asking for help", "talking about people"),
            mastery_threshold=75.0,
            review_priority=3,
            focus_note="Keep subject/object contrast concrete and high-frequency.",
        ),
        topic(
            "gram_this_that_these_those",
            display_name="This / that / these / those",
            cefr_band=C.A1,
            introduction_order=90,
            prerequisite_ids=("gram_articles_a_an_the",),
            learning_objectives=(
                "Point to near/far singular and plural nouns with demonstratives",
            ),
            demonstration_patterns=("this", "that", "these", "those"),
            example_sentences=(
                "This book is mine.",
                "Those chairs are new.",
            ),
            common_errors=(
                "This books are mine.",
                "That are my friends.",
            ),
            best_reinforcement_skills=(R.speaking, R.listening),
            recommended_contexts=("classroom objects", "shopping"),
            mastery_threshold=75.0,
            review_priority=2,
        ),
        topic(
            "gram_prepositions_place",
            display_name="Prepositions of place",
            cefr_band=C.A1,
            introduction_order=95,
            prerequisite_ids=("gram_there_is_are",),
            learning_objectives=(
                "Locate objects and people with in / on / under / next to / between",
            ),
            demonstration_patterns=("in", "on", "under", "next to", "between"),
            example_sentences=(
                "The bag is under the table.",
                "She is next to the door.",
            ),
            common_errors=(
                "The bag is in the table. (wrong for surface)",
                "She is next the door.",
            ),
            best_reinforcement_skills=(R.listening, R.speaking),
            recommended_contexts=("describing a room", "map landmarks"),
            mastery_threshold=75.0,
            review_priority=3,
        ),
        topic(
            "gram_imperatives",
            display_name="Imperatives",
            cefr_band=C.A1,
            introduction_order=100,
            prerequisite_ids=("gram_present_simple",),
            learning_objectives=(
                "Give simple instructions and polite requests with imperatives",
            ),
            demonstration_patterns=("open", "don't", "please", "let's"),
            example_sentences=(
                "Open your books.",
                "Don't be late.",
                "Let's start.",
            ),
            common_errors=(
                "You open your books. (as instruction form)",
                "Don't to be late.",
            ),
            best_reinforcement_skills=(R.listening, R.speaking),
            recommended_contexts=("classroom instructions", "directions"),
            mastery_threshold=75.0,
            review_priority=3,
        ),
        # A2 (+2)
        topic(
            "gram_adverbs_frequency",
            display_name="Adverbs of frequency",
            cefr_band=C.A2,
            introduction_order=185,
            prerequisite_ids=("gram_present_simple",),
            learning_objectives=(
                "Place always / usually / often / sometimes / never with present simple",
            ),
            demonstration_patterns=("always", "usually", "often", "sometimes", "never"),
            example_sentences=(
                "I usually walk to school.",
                "She never drinks coffee.",
            ),
            common_errors=(
                "I walk usually to school.",
                "She drinks never coffee.",
            ),
            best_reinforcement_skills=(R.speaking, R.writing),
            recommended_contexts=("daily routines", "habits interview"),
            mastery_threshold=78.0,
            review_priority=3,
        ),
        topic(
            "gram_will_future",
            display_name="Will for future decisions and offers",
            cefr_band=C.A2,
            introduction_order=190,
            prerequisite_ids=("gram_going_to",),
            learning_objectives=(
                "Use will for spontaneous decisions, offers, and predictions",
                "Contrast lightly with going to for plans",
            ),
            demonstration_patterns=("will", "won't", "I'll", "shall"),
            example_sentences=(
                "I'll help you with the bags.",
                "It will be sunny tomorrow.",
            ),
            common_errors=(
                "I will to help you.",
                "I going to help you. (when spontaneous offer is needed)",
            ),
            best_reinforcement_skills=(R.speaking, R.listening),
            recommended_contexts=("offers of help", "weather predictions"),
            mastery_threshold=80.0,
            review_priority=4,
        ),
        # B1 (+4)
        topic(
            "gram_too_enough",
            display_name="Too / enough",
            cefr_band=C.B1,
            introduction_order=265,
            prerequisite_ids=("gram_comparatives_basic",),
            learning_objectives=(
                "Express excess and sufficiency with too + adjective and adjective + enough",
            ),
            demonstration_patterns=("too", "enough", "not enough"),
            example_sentences=(
                "This bag is too heavy.",
                "She is not tall enough.",
            ),
            common_errors=(
                "This bag is enough heavy.",
                "She is not enough tall.",
            ),
            best_reinforcement_skills=(R.speaking, R.writing),
            recommended_contexts=("choosing a product", "fitness goals"),
            mastery_threshold=80.0,
            review_priority=3,
        ),
        topic(
            "gram_gerunds_infinitives",
            display_name="Gerunds and infinitives (basic)",
            cefr_band=C.B1,
            introduction_order=270,
            prerequisite_ids=("gram_present_simple", "gram_can_ability"),
            learning_objectives=(
                "Choose common verb + -ing / to-infinitive patterns correctly",
            ),
            demonstration_patterns=("enjoy -ing", "want to", "decide to", "like -ing"),
            example_sentences=(
                "I enjoy reading at night.",
                "She decided to stay.",
            ),
            common_errors=(
                "I enjoy to read at night.",
                "She decided staying.",
            ),
            best_reinforcement_skills=(R.writing, R.speaking),
            recommended_contexts=("hobbies", "plans and decisions"),
            mastery_threshold=80.0,
            review_priority=3,
        ),
        topic(
            "gram_question_tags",
            display_name="Question tags",
            cefr_band=C.B1,
            introduction_order=275,
            prerequisite_ids=("gram_basic_questions", "gram_present_simple"),
            learning_objectives=(
                "Add basic question tags to confirm information in conversation",
            ),
            demonstration_patterns=("isn't it", "don't you", "aren't they", "didn't he"),
            example_sentences=(
                "You're ready, aren't you?",
                "She lives here, doesn't she?",
            ),
            common_errors=(
                "You're ready, isn't you?",
                "She lives here, isn't she?",
            ),
            best_reinforcement_skills=(R.speaking, R.listening),
            recommended_contexts=("checking understanding", "friendly confirmation"),
            mastery_threshold=80.0,
            review_priority=3,
        ),
        topic(
            "gram_past_perfect_light",
            display_name="Past perfect (light)",
            cefr_band=C.B1,
            introduction_order=280,
            prerequisite_ids=("gram_past_simple", "gram_past_continuous"),
            learning_objectives=(
                "Show an earlier past action with had + past participle before another past event",
            ),
            demonstration_patterns=("had", "hadn't", "already", "before"),
            example_sentences=(
                "I had finished before they arrived.",
                "She hadn't seen the message.",
            ),
            common_errors=(
                "I had finished yesterday. (no second past anchor)",
                "She hadn't saw the message.",
            ),
            best_reinforcement_skills=(R.writing, R.speaking),
            recommended_contexts=("story sequence", "explaining a delay"),
            evidence_requirements=ev(min_observations=4, min_distinct_contexts=2, min_skills_covered=2),
            mastery_threshold=82.0,
            review_priority=4,
        ),
        # B2 (+2)
        topic(
            "gram_third_conditional",
            display_name="Third conditional",
            cefr_band=C.B2,
            introduction_order=365,
            prerequisite_ids=("gram_second_conditional", "gram_past_perfect_light"),
            learning_objectives=(
                "Express unreal past conditions and regrets with if + past perfect, would have",
            ),
            demonstration_patterns=("if had", "would have", "could have", "might have"),
            example_sentences=(
                "If I had left earlier, I would have arrived on time.",
                "She might have passed if she had studied.",
            ),
            common_errors=(
                "If I would have left earlier...",
                "If I had left earlier, I would arrive on time.",
            ),
            best_reinforcement_skills=(R.speaking, R.writing),
            recommended_contexts=("regrets", "missed opportunities"),
            mastery_threshold=84.0,
            review_priority=4,
        ),
        topic(
            "gram_wish_regret",
            display_name="Wish and regret",
            cefr_band=C.B2,
            introduction_order=370,
            prerequisite_ids=("gram_second_conditional", "gram_past_simple"),
            learning_objectives=(
                "Express present/past wishes and regrets with wish / if only",
            ),
            demonstration_patterns=("I wish", "if only", "wish I had", "wish I could"),
            example_sentences=(
                "I wish I had more time.",
                "If only we had listened.",
            ),
            common_errors=(
                "I wish I have more time.",
                "I wish I would have more time. (present wish)",
            ),
            best_reinforcement_skills=(R.speaking, R.writing),
            recommended_contexts=("personal regrets", "unmet goals"),
            mastery_threshold=84.0,
            review_priority=3,
        ),
        # C1 (+2)
        topic(
            "gram_participle_clauses",
            display_name="Participle clauses",
            cefr_band=C.C1,
            introduction_order=445,
            prerequisite_ids=("gram_relative_clauses", "gram_concession"),
            learning_objectives=(
                "Compress background information with participle clauses",
            ),
            demonstration_patterns=("having", "-ing,", "built in", "worried about"),
            example_sentences=(
                "Having finished the report, she left.",
                "Built in 1920, the school still stands.",
            ),
            common_errors=(
                "Dangling participles with unclear subjects",
                "Having finished the report, the door opened.",
            ),
            best_reinforcement_skills=(R.reading, R.writing),
            recommended_contexts=("formal narrative", "academic description"),
            mastery_threshold=88.0,
            review_priority=3,
        ),
        topic(
            "gram_subjunctive_formal",
            display_name="Formal subjunctive / mandative",
            cefr_band=C.C1,
            introduction_order=450,
            prerequisite_ids=("gram_advanced_modals", "gram_second_conditional"),
            learning_objectives=(
                "Use mandative subjunctive and formal were in recommendations and demands",
            ),
            demonstration_patterns=("recommend that", "insist that", "were", "be"),
            example_sentences=(
                "They recommended that she be present.",
                "If he were available, we would start.",
            ),
            common_errors=(
                "They recommended that she is present.",
                "If he was available... (overly informal in formal contexts)",
            ),
            best_reinforcement_skills=(R.writing, R.reading),
            recommended_contexts=("formal recommendations", "policy language"),
            mastery_threshold=88.0,
            review_priority=2,
        ),
        # C2 (+1)
        topic(
            "gram_fronting_advanced",
            display_name="Advanced fronting and information structure",
            cefr_band=C.C2,
            introduction_order=540,
            prerequisite_ids=("gram_inversion_emphasis", "gram_discourse_signalling"),
            learning_objectives=(
                "Control information focus with marked word order and fronting",
            ),
            demonstration_patterns=("only then", "so intense was", "what he did was"),
            example_sentences=(
                "Only then did the team understand the risk.",
                "What they needed was clearer evidence.",
            ),
            common_errors=(
                "Only then the team understood the risk.",
                "Fronting without communicative purpose",
            ),
            best_reinforcement_skills=(R.writing, R.reading),
            recommended_contexts=("editorial argument", "persuasive speech"),
            mastery_threshold=92.0,
            review_priority=2,
            review_half_life_days=28.0,
        ),
    )


def _topic_to_yaml_dict(t: GrammarTopic, display_code: str) -> dict:
    req = t.evidence_requirements
    return {
        "grammar_id": t.grammar_id,
        "display_code": display_code,
        "title": t.display_name,
        "cefr_level": t.cefr_band.value,
        "order": t.introduction_order,
        "prerequisites": list(t.prerequisite_ids),
        "unlock_targets": [],
        "grammar_targets": list(t.demonstration_patterns),
        "teaching_notes": t.focus_note or "",
        "common_mistakes": list(t.common_errors),
        "examples": list(t.example_sentences),
        "learning_objectives": list(t.learning_objectives),
        "estimated_duration_minutes": 25,
        "difficulty": "guided",
        "mastery_threshold": float(t.mastery_threshold),
        "evidence": {
            "min_observations": int(req.min_observations),
            "min_distinct_contexts": int(req.min_distinct_contexts),
            "min_skills_covered": int(req.min_skills_covered),
        },
        "reinforcement_skills": [s.value for s in t.best_reinforcement_skills],
        "recommended_contexts": list(t.recommended_contexts),
        "minimum_context_diversity": int(t.minimum_context_diversity),
        "review_priority": int(t.review_priority),
        "review_half_life_days": float(t.review_half_life_days),
        "focus_note": t.focus_note or "",
    }


def _with_sparse_orders(topics: tuple[GrammarTopic, ...]) -> tuple[GrammarTopic, ...]:
    """Reassign introduction_order = 10,20,... so G1 insert-gap policy holds."""
    ordered = sorted(topics, key=lambda t: (t.introduction_order, t.grammar_id))
    rebuilt: list[GrammarTopic] = []
    for idx, t in enumerate(ordered, start=1):
        rebuilt.append(
            GrammarTopic(
                grammar_id=t.grammar_id,
                display_name=t.display_name,
                cefr_band=t.cefr_band,
                introduction_order=idx * 10,
                prerequisite_ids=t.prerequisite_ids,
                future_topic_ids=(),
                learning_objectives=t.learning_objectives,
                demonstration_patterns=t.demonstration_patterns,
                example_sentences=t.example_sentences,
                common_errors=t.common_errors,
                best_reinforcement_skills=t.best_reinforcement_skills,
                recommended_contexts=t.recommended_contexts,
                minimum_context_diversity=t.minimum_context_diversity,
                evidence_requirements=t.evidence_requirements,
                mastery_threshold=t.mastery_threshold,
                review_priority=t.review_priority,
                review_half_life_days=t.review_half_life_days,
                focus_note=t.focus_note,
            )
        )
    return tuple(rebuilt)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for stale in OUT.glob("*.yaml"):
        stale.unlink()

    combined = tuple(_raw_topics()) + _new_topics()
    ordered = _with_sparse_orders(combined)
    if len(ordered) != 50:
        raise SystemExit(f"Expected 50 topics, got {len(ordered)}")

    from collections import Counter

    counts = Counter(t.cefr_band.value for t in ordered)
    expected = {"A1": 12, "A2": 10, "B1": 10, "B2": 8, "C1": 6, "C2": 4}
    if dict(counts) != expected:
        raise SystemExit(f"CEFR quotas mismatch: {dict(counts)} != {expected}")

    index = {
        "version": "1.0.0",
        "language_code": "en",
        "schema_version": 1,
        "cefr_quotas": expected,
        "ordered_grammar_ids": [t.grammar_id for t in ordered],
    }
    (OUT / "_index.yaml").write_text(
        yaml.safe_dump(index, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )

    for idx, t in enumerate(ordered, start=1):
        code = f"G{idx:03d}"
        path = OUT / f"{t.grammar_id}.yaml"
        path.write_text(
            yaml.safe_dump(_topic_to_yaml_dict(t, code), sort_keys=False, allow_unicode=True),
            encoding="utf-8",
        )
        print(f"wrote {path.name} ({code}) order={t.introduction_order}")

    print(f"OK: wrote {len(ordered)} topics + _index.yaml under {OUT}")


if __name__ == "__main__":
    main()
