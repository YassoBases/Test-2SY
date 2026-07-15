"""Pydantic v2 schemas for the interactive AI English exam.

`FinalAcademicReport` is the strict structured-output contract the AI must satisfy — it is used
both to validate the model's JSON and as the persisted/returned report shape.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field, field_validator, model_validator


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
    """Transcript-based assessment of one server-verified spoken answer.

    ``transcription`` comes only from server STT. Text feedback must not claim that pronunciation
    was measured; ``next_question`` is the adaptive follow-up.
    """

    transcription: str = Field(description="Verbatim text of what the student said.")
    grammar_vocab_feedback: str = Field(description="Short correction of grammar/vocabulary/phrasing.")
    pronunciation_feedback: str = Field(description="Explicit unassessed note; no acoustic scorer is used.")
    fluency_note: str = Field(description="Text-visible coherence/disfluency note only.")
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


class SpeakingPromptEvidence(BaseModel):
    """Which speaking prompts were actually used this session -- MVP bank vs. AI fallback,
    subskill/task-type diversity, and whether curated-bank review metadata was resolvable."""

    prompt_source: str = "unknown"  # mvp_speaking_prompt_bank | fallback_generated | unknown
    prompt_review_status: str = ""
    expected_turns: int = 0
    turns_answered: int = 0
    unique_bank_items_count: int = 0
    unique_subskills_count: int = 0
    repeated_subskills: bool = False
    subskills_seen: list[str] = Field(default_factory=list)
    bank_item_ids_present: bool = False
    fallback_prompt_used: bool = False


class SpeakingSttEvidence(BaseModel):
    """Transcript-availability evidence only -- never a proxy for answer quality/score."""

    provider: str = ""
    transcripts_count: int = 0
    empty_transcripts_count: int = 0
    short_transcripts_count: int = 0
    total_word_count: int = 0
    average_words_per_turn: float = 0.0
    confidence_available: bool = False
    evidence_status: str = "unavailable"  # usable | limited | insufficient | unavailable


class SpeakingLanguageEvaluation(BaseModel):
    """A read-only restatement of the existing grade_speaking() result -- never a second LLM
    call, never a new scoring formula. dimensions.pronunciation is always the literal string
    "unassessed" because no acoustic pronunciation scorer exists for MVP."""

    provider: str = ""
    source: str = "grade_speaking"
    dimensions: dict[str, float | str | None] = Field(default_factory=dict)
    estimated_cefr: str = ""
    score: float | None = None
    scoring_changed: bool = False


class SpeakingProsodyEvidence(BaseModel):
    """MVP delivery evidence derived only from audio_duration_seconds + transcript word count
    (no raw audio, no acoustic/pause/rhythm analysis, no Hume/EVI call of any kind)."""

    provider: str = "derived_duration_transcript"
    runtime_status: str = "not_implemented"  # available | partial | not_implemented | unavailable
    speech_rate_wpm: list[float | None] = Field(default_factory=list)
    average_speech_rate_wpm: float | None = None
    response_duration_status: str = "unknown"  # under | within | over | unknown
    short_response_turns: int = 0
    very_short_response_turns: int = 0
    acoustic_metrics_available: bool = False
    pause_metrics_available: bool = False
    rhythm_metrics_available: bool = False
    evi_runtime_status: str = "not_implemented"


class SpeakingAssessmentCore(BaseModel):
    """Additive, MVP evidence/auditability layer for Speaking. Labels and evidence only -- never
    changes final_level, confidence, or grade_speaking's own scoring (scoring_changed is always
    false and exists only so a future task can grep for when that stops being true)."""

    speaking_assessment_core_version: str = "speaking_assessment_core_mvp_v1"
    speaking_rubric_version: str = "speaking_llm_transcript_rubric_v1"
    scoring_changed: bool = False
    prompt_evidence: SpeakingPromptEvidence = Field(default_factory=SpeakingPromptEvidence)
    stt_evidence: SpeakingSttEvidence = Field(default_factory=SpeakingSttEvidence)
    language_evaluation: SpeakingLanguageEvaluation = Field(default_factory=SpeakingLanguageEvaluation)
    prosody_evidence: SpeakingProsodyEvidence = Field(default_factory=SpeakingProsodyEvidence)
    review_flags: list[str] = Field(default_factory=list)
    needs_human_review: bool = False


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
    # Transcript-based sub-scores: {fluency, lexical, grammar}; pronunciation is unassessed.
    speaking_breakdown: dict[str, float] = Field(default_factory=dict)
    # Per-turn spoken detail (shown in the report, not during the exam).
    speaking_turns: list[SpeakingTurnDetailOut] = Field(default_factory=list)

    # Two-phase triangulation signals (Phase 1: written/turn-based; Phase 2: spoken interview).
    confidence: float = Field(ge=0.0, le=1.0, default=0.0)
    # consistent | speaking_stronger | writing_stronger | live_phase_unavailable
    cross_phase_consistency: str = "consistent"
    # Components that were deliberately not scored because no authoritative signal exists.
    unassessed_components: list[str] = Field(default_factory=list)

    # Additive MVP evidence/auditability layer (see language_speaking_assessment_core_service.py).
    # Labels and evidence only -- never changes any of the scoring fields above.
    assessment_core_version: str = "ai_exam_assessment_core_v1"
    speaking_assessment: SpeakingAssessmentCore = Field(default_factory=SpeakingAssessmentCore)


class ExamNarrativeSchema(BaseModel):
    """The narrative-only slice the AI produces for the final report (structured output, English)."""

    summary: str
    strengths: list[str] = Field(default_factory=list)
    weaknesses: list[str] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)
    detected_errors: list[GrammarErrorDetail] = Field(default_factory=list)
    recommended_starting_lesson_topic: str


class SpeakingGradeSchema(BaseModel):
    """Structured transcript grade; pronunciation is 0/unassessed in this flow."""

    level: CEFRLevel
    fluency: float = Field(ge=0.0, le=10.0, default=0.0)
    lexical: float = Field(ge=0.0, le=10.0, default=0.0)
    grammar: float = Field(ge=0.0, le=10.0, default=0.0)
    pronunciation: float = Field(ge=0.0, le=10.0, default=0.0)
    score: float = Field(ge=0.0, le=10.0)  # equal-weight average of assessed textual criteria
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
    """Shared answer submission for both mcq and gap_fill items. The client never declares which
    type it's answering -- exactly one of choice_index/answer_text is supplied, and the backend
    decides which is required only after resolving the server-side item via question_token."""

    choice_index: int | None = Field(default=None, ge=0)
    answer_text: str | None = Field(default=None, max_length=500)
    request_id: str = Field(min_length=8, max_length=100)
    state_revision: int = Field(ge=1)
    question_token: str = Field(min_length=16, max_length=200)

    @model_validator(mode="after")
    def _check_exactly_one_answer_field(self) -> "McqAnswerIn":
        if self.answer_text is not None and not self.answer_text.strip():
            raise ValueError("answer_text cannot be blank or whitespace-only")
        choice_present = self.choice_index is not None
        text_present = self.answer_text is not None
        if choice_present and text_present:
            raise ValueError("choice_index and answer_text cannot both be provided")
        if not choice_present and not text_present:
            raise ValueError("either choice_index or answer_text is required")
        return self


class WritingAnswerIn(BaseModel):
    text: str = Field(min_length=1, max_length=4000)
    request_id: str = Field(min_length=8, max_length=100)
    state_revision: int = Field(ge=1)
    prompt_token: str = Field(min_length=16, max_length=200)

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
    turn_token: str


class LiveTranscriptionSessionOut(BaseModel):
    """A short-lived OpenAI Realtime ephemeral client secret for Speaking's live transcript
    preview (MVP, display-only). Never used for grading; the official transcript remains the
    backend's own post-submit STT pipeline. `available=False` (fields omitted) is the safe,
    non-error response whenever live transcription is disabled, misconfigured, or the upstream
    call fails -- the frontend must fall back to the normal recording UI without surfacing this
    as an error."""

    available: bool
    client_secret: str | None = None
    expires_at: int | None = None
    model: str | None = None


class McqPromptOut(BaseModel):
    """Shared shape for reading (passage) and listening (audio) comprehension items."""

    instructions: str
    passage: str | None = None
    audio_url: str | None = None
    situation: str | None = None
    question: str
    options: list[str]
    item_index: int
    item_total: int
    question_token: str
    # Additive, backward-compatible: every current item is "mcq". Lets the frontend/tests
    # distinguish task types once a non-MCQ type (e.g. gap_fill) is introduced later.
    question_type: str = "mcq"


class WritingPromptOut(BaseModel):
    prompt: str
    min_words: int = 40
    prompt_token: str


class SpeakingTurnFeedbackOut(BaseModel):
    transcription: str | None = None
    grammar_vocab_feedback: str | None = None
    pronunciation_feedback: str | None = None
    fluency_note: str | None = None


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
    state_revision: int = Field(ge=1)
    phase: str  # speaking | listening | reading | writing | evaluating | completed
    section_index: int  # 0-based index of the current section
    section_total: int
    sections: list[str] = Field(default_factory=list)
    speaking: SpeakingPromptOut | None = None
    mcq: McqPromptOut | None = None
    writing: WritingPromptOut | None = None
    last_feedback: SpeakingTurnFeedbackOut | None = None
    resumed: bool = False
    question_token: str | None = None
    turn_token: str | None = None
    prompt_token: str | None = None
    evidence_status: str = "missing_student_response"
    error_code: str | None = None
    error_message: str | None = None


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
    error_code: str | None = None
    error_message: str | None = None
