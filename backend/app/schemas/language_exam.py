"""Pydantic v2 schemas for the interactive AI English exam.

`FinalAcademicReport` is the strict structured-output contract the AI must satisfy — it is used
both to validate the model's JSON and as the persisted/returned report shape.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field, field_validator


class CEFRLevel(str, Enum):
    A1 = "A1"
    A2 = "A2"
    B1 = "B1"
    B2 = "B2"
    C1 = "C1"
    C2 = "C2"


# ---------- input ----------

class ExamInitiateIn(BaseModel):
    """Optional theme selector for a new exam (None / 'surprise' = random)."""

    theme: str | None = None


class ChatInputSchema(BaseModel):
    """A sanitised student message."""

    message: str = Field(min_length=1, max_length=2000)

    @field_validator("message")
    @classmethod
    def _strip(cls, v: str) -> str:
        v = " ".join((v or "").split())
        if not v:
            raise ValueError("message cannot be empty")
        return v


# ---------- AI structured output ----------

class SpeakingTurnAssessment(BaseModel):
    """Audio-native assessment of ONE spoken answer (google-genai structured output).

    Gemini judges the actual audio: ``transcription`` is what it heard; the feedback fields cover
    both content and delivery; ``next_question`` is its adaptive follow-up (the backend still owns
    when the speaking section ends).
    """

    transcription: str = Field(description="Verbatim text of what the student said.")
    grammar_vocab_feedback: str = Field(description="Short correction of grammar/vocabulary/phrasing.")
    pronunciation_feedback: str = Field(description="Note on pronunciation/clarity from the audio.")
    fluency_note: str = Field(description="Note on fluency: pace, hesitation, coherence.")
    estimated_level: "CEFRLevel" = Field(description="CEFR level estimated from this answer.")
    next_question: str = Field(description="The next adaptive in-character question to ask.")


class GrammarErrorDetail(BaseModel):
    original_text: str
    corrected_text: str
    rule_explanation: str  # English (the platform is English-only).


class FinalAcademicReportSchema(BaseModel):
    """Strict academic report — enforces the examiner AI's structured output."""

    cefr_level: CEFRLevel
    grammatical_accuracy_score: float = Field(ge=0.0, le=10.0)
    vocabulary_richness_score: float = Field(ge=0.0, le=10.0)
    fluency_coherence_score: float = Field(ge=0.0, le=10.0)
    overall_academic_summary: str
    detected_errors: list[GrammarErrorDetail] = Field(default_factory=list)
    recommended_starting_lesson_topic: str

    @field_validator(
        "grammatical_accuracy_score", "vocabulary_richness_score", "fluency_coherence_score"
    )
    @classmethod
    def _round_scores(cls, v: float) -> float:
        return round(max(0.0, min(10.0, float(v))), 1)


class MultiSkillReportSchema(BaseModel):
    """Final placement report. Per-skill CEFR levels + an AI-written narrative.

    Skill levels/scores are computed by the backend (reading/listening from % correct, speaking
    from the audio engine, writing from the grader). Grammar/vocab is a diagnostic anchor, not a
    persisted learner skill. The AI fills only the narrative fields.
    """

    overall_level: CEFRLevel
    reading_level: CEFRLevel
    listening_level: CEFRLevel
    writing_level: CEFRLevel
    speaking_level: CEFRLevel

    reading_score_percent: float = Field(ge=0.0, le=100.0, default=0.0)
    listening_score_percent: float = Field(ge=0.0, le=100.0, default=0.0)
    writing_score: float = Field(ge=0.0, le=10.0, default=0.0)
    speaking_score: float = Field(ge=0.0, le=10.0, default=0.0)
    grammar_vocab_level: CEFRLevel | None = None
    grammar_vocab_score_percent: float = Field(ge=0.0, le=100.0, default=0.0)

    summary: str = ""
    strengths: list[str] = Field(default_factory=list)
    weaknesses: list[str] = Field(default_factory=list)
    detected_errors: list[GrammarErrorDetail] = Field(default_factory=list)
    recommended_starting_lesson_topic: str = ""

    # Backend-computed guidance.
    strongest_skill: str = ""
    weakest_skill: str = ""
    recommendations: list[str] = Field(default_factory=list)
    weeks_to_next_level: int = 0
    # Writing IELTS sub-scores: {task_achievement, coherence, lexical, grammar} (0-10).
    writing_breakdown: dict[str, float] = Field(default_factory=dict)
    # Speaking IELTS sub-scores: {fluency, lexical, grammar, pronunciation} (0-10).
    speaking_breakdown: dict[str, float] = Field(default_factory=dict)
    # Per-turn spoken detail (shown in the report, not during the exam).
    speaking_turns: list[SpeakingTurnDetailOut] = Field(default_factory=list)

    # Two-phase triangulation signals (Phase 1: written/turn-based; Phase 2: spoken interview).
    confidence: float = Field(ge=0.0, le=1.0, default=0.0)
    # consistent | speaking_stronger | writing_stronger | live_phase_unavailable
    cross_phase_consistency: str = "consistent"


class ExamNarrativeSchema(BaseModel):
    """The narrative-only slice the AI produces for the final report (structured output, English)."""

    summary: str
    strengths: list[str] = Field(default_factory=list)
    weaknesses: list[str] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)
    detected_errors: list[GrammarErrorDetail] = Field(default_factory=list)
    recommended_starting_lesson_topic: str


class SpeakingGradeSchema(BaseModel):
    """Structured IELTS-style grade of the spoken answers (4 criteria, each 0-10)."""

    level: CEFRLevel
    fluency: float = Field(ge=0.0, le=10.0, default=0.0)
    lexical: float = Field(ge=0.0, le=10.0, default=0.0)
    grammar: float = Field(ge=0.0, le=10.0, default=0.0)
    pronunciation: float = Field(ge=0.0, le=10.0, default=0.0)
    score: float = Field(ge=0.0, le=10.0)  # equal-weight average of the four
    feedback: str = ""
    detected_errors: list[GrammarErrorDetail] = Field(default_factory=list)

    @field_validator("fluency", "lexical", "grammar", "pronunciation", "score")
    @classmethod
    def _round_score(cls, v: float) -> float:
        return round(max(0.0, min(10.0, float(v))), 1)


class WritingGradeSchema(BaseModel):
    """Structured IELTS-style grade of the writing answer (4 criteria, each 0-10)."""

    level: CEFRLevel
    task_achievement: float = Field(ge=0.0, le=10.0, default=0.0)
    coherence: float = Field(ge=0.0, le=10.0, default=0.0)
    lexical: float = Field(ge=0.0, le=10.0, default=0.0)
    grammar: float = Field(ge=0.0, le=10.0, default=0.0)
    score: float = Field(ge=0.0, le=10.0)  # weighted overall (the 4 criteria, equal weight)
    feedback: str = ""
    detected_errors: list[GrammarErrorDetail] = Field(default_factory=list)

    @field_validator("task_achievement", "coherence", "lexical", "grammar", "score")
    @classmethod
    def _round_score(cls, v: float) -> float:
        return round(max(0.0, min(10.0, float(v))), 1)


# ---------- API: inputs ----------

class McqAnswerIn(BaseModel):
    choice_index: int = Field(ge=0)


class WritingAnswerIn(BaseModel):
    text: str = Field(min_length=1, max_length=4000)

    @field_validator("text")
    @classmethod
    def _strip(cls, v: str) -> str:
        v = (v or "").strip()
        if not v:
            raise ValueError("text cannot be empty")
        return v


# ---------- API: section prompt payloads ----------

class SpeakingPromptOut(BaseModel):
    scenario_title: str
    setting: str = ""
    examiner_message: str
    turn: int
    total_turns: int


class McqPromptOut(BaseModel):
    """Shared shape for reading (passage) and listening (audio) comprehension items."""

    instructions: str
    passage: str | None = None
    audio_url: str | None = None
    audio_text: str | None = None
    situation: str | None = None
    question: str
    options: list[str]
    item_index: int
    item_total: int


class WritingPromptOut(BaseModel):
    prompt: str
    min_words: int = 40


class SpeakingTurnFeedbackOut(BaseModel):
    transcription: str | None = None
    grammar_vocab_feedback: str | None = None
    pronunciation_feedback: str | None = None
    fluency_note: str | None = None


class SpeakingTranscriptionOut(BaseModel):
    """Speech-to-text preview returned before a spoken answer is submitted."""

    transcription: str
    engine: str
    model: str


class SpeakingTurnDetailOut(BaseModel):
    """One spoken turn in the final report: the question, what was said, and per-turn notes."""

    question: str = ""
    transcription: str = ""
    grammar_vocab_feedback: str = ""
    pronunciation_feedback: str = ""
    fluency_note: str = ""


# ---------- API: unified state machine ----------

class ExamStateOut(BaseModel):
    """One contract telling the frontend exactly what to render next."""

    session_id: str
    phase: str  # speaking | listening | reading | writing | evaluating | completed
    section_index: int  # 0-based index of the current section
    section_total: int
    sections: list[str] = Field(default_factory=list)
    speaking: SpeakingPromptOut | None = None
    mcq: McqPromptOut | None = None
    writing: WritingPromptOut | None = None
    last_feedback: SpeakingTurnFeedbackOut | None = None
    resumed: bool = False


class ExamProcessingOut(BaseModel):
    status: str = "processing"
    session_id: str
    message: str


class ExamReportOut(BaseModel):
    session_id: str
    status: str  # in_progress | evaluating | completed | failed
    is_completed: bool
    report: MultiSkillReportSchema | None = None
    completed_at: datetime | None = None
