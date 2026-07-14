"""Catalog: subjects, teacher profiles, courses."""

import enum
from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class TeacherProfile(Base):
    __tablename__ = "teacher_profiles"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True, index=True)
    full_name: Mapped[str] = mapped_column(String(255))
    image_url: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    bio: Mapped[str | None] = mapped_column(Text, nullable=True)
    rating: Mapped[float] = mapped_column(Float, default=4.8)
    student_count: Mapped[int] = mapped_column(Integer, default=0)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    setup_completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    # Teaching impact metrics (teacher-edited, separate from bio)
    impact_total_students: Mapped[int | None] = mapped_column(Integer, nullable=True)
    impact_grade12_students: Mapped[int | None] = mapped_column(Integer, nullable=True)
    impact_completed_subject: Mapped[int | None] = mapped_column(Integer, nullable=True)
    impact_excellent_grades: Mapped[int | None] = mapped_column(Integer, nullable=True)
    impact_years_teaching: Mapped[int | None] = mapped_column(Integer, nullable=True)
    # Teaching philosophy
    philosophy_teaching_style: Mapped[str | None] = mapped_column(Text, nullable=True)
    philosophy_lesson_approach: Mapped[str | None] = mapped_column(Text, nullable=True)
    philosophy_exam_preparation: Mapped[str | None] = mapped_column(Text, nullable=True)
    # AI lesson-chat identity (teacher-editable)
    teacher_teaching_style: Mapped[str] = mapped_column(String(32), default="step_by_step")
    teacher_tone: Mapped[str] = mapped_column(String(32), default="balanced")
    teacher_question_style: Mapped[str] = mapped_column(String(32), default="mixed")
    teacher_motivation_level: Mapped[str] = mapped_column(String(32), default="medium")
    teacher_display_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    teacher_signature_phrase: Mapped[str | None] = mapped_column(String(500), nullable=True)

    user: Mapped["User"] = relationship(back_populates="teacher_profile")
    courses: Mapped[list["Course"]] = relationship(back_populates="teacher_profile")
    subject_links: Mapped[list["TeacherProfileSubject"]] = relationship(
        back_populates="teacher_profile", cascade="all, delete-orphan"
    )
    grade_links: Mapped[list["TeacherProfileGrade"]] = relationship(
        back_populates="teacher_profile", cascade="all, delete-orphan"
    )
    voice_samples: Mapped[list["TeacherVoiceSample"]] = relationship(
        back_populates="teacher_profile",
        cascade="all, delete-orphan",
        order_by="TeacherVoiceSample.uploaded_at.desc()",
    )
    qualifications: Mapped[list["TeacherQualification"]] = relationship(
        back_populates="teacher_profile",
        cascade="all, delete-orphan",
        order_by="TeacherQualification.sort_order, TeacherQualification.id",
    )
    teaching_experiences: Mapped[list["TeacherTeachingExperience"]] = relationship(
        back_populates="teacher_profile",
        cascade="all, delete-orphan",
        order_by="TeacherTeachingExperience.sort_order, TeacherTeachingExperience.id",
    )
    achievements: Mapped[list["TeacherAchievement"]] = relationship(
        back_populates="teacher_profile",
        cascade="all, delete-orphan",
        order_by="TeacherAchievement.is_pinned.desc(), TeacherAchievement.sort_order, TeacherAchievement.id",
    )
    why_study_points: Mapped[list["TeacherWhyStudyPoint"]] = relationship(
        back_populates="teacher_profile",
        cascade="all, delete-orphan",
        order_by="TeacherWhyStudyPoint.sort_order, TeacherWhyStudyPoint.id",
    )
    professional_documents: Mapped[list["TeacherProfessionalDocument"]] = relationship(
        back_populates="teacher_profile",
        cascade="all, delete-orphan",
        order_by="TeacherProfessionalDocument.sort_order, TeacherProfessionalDocument.id",
    )


class Subject(Base):
    __tablename__ = "subjects"
    __table_args__ = (UniqueConstraint("grade", "slug", name="uq_subject_grade_slug"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name_ar: Mapped[str] = mapped_column(String(120))
    slug: Mapped[str] = mapped_column(String(80), index=True)
    grade: Mapped[int] = mapped_column(Integer, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    courses: Mapped[list["Course"]] = relationship(back_populates="subject")


class Course(Base):
    __tablename__ = "courses"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(500))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_published: Mapped[bool] = mapped_column(Boolean, default=True)
    subject_id: Mapped[int] = mapped_column(ForeignKey("subjects.id"), index=True)
    teacher_profile_id: Mapped[int] = mapped_column(ForeignKey("teacher_profiles.id"), index=True)
    grade: Mapped[int] = mapped_column(Integer, index=True)
    price: Mapped[float] = mapped_column(Float, default=0.0)
    currency: Mapped[str] = mapped_column(String(10), default="SYP")
    thumbnail_url: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    banner_url: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    subject: Mapped["Subject"] = relationship(back_populates="courses")
    teacher_profile: Mapped["TeacherProfile"] = relationship(back_populates="courses")
    access_records: Mapped[list["StudentCourseAccess"]] = relationship(back_populates="course")
    lessons: Mapped[list["Lesson"]] = relationship(
        back_populates="course",
        foreign_keys="Lesson.course_id",
    )
    manual_quizzes: Mapped[list["CourseQuiz"]] = relationship(
        back_populates="course",
        cascade="all, delete-orphan",
    )


class TeacherProfileSubject(Base):
    __tablename__ = "teacher_profile_subjects"
    __table_args__ = (UniqueConstraint("teacher_profile_id", "subject_id", name="uq_teacher_subject"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    teacher_profile_id: Mapped[int] = mapped_column(ForeignKey("teacher_profiles.id", ondelete="CASCADE"))
    subject_id: Mapped[int] = mapped_column(ForeignKey("subjects.id", ondelete="CASCADE"))

    teacher_profile: Mapped["TeacherProfile"] = relationship(back_populates="subject_links")
    subject: Mapped["Subject"] = relationship()


class TeacherProfileGrade(Base):
    __tablename__ = "teacher_profile_grades"
    __table_args__ = (UniqueConstraint("teacher_profile_id", "grade", name="uq_teacher_grade"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    teacher_profile_id: Mapped[int] = mapped_column(ForeignKey("teacher_profiles.id", ondelete="CASCADE"))
    grade: Mapped[int] = mapped_column(Integer)

    teacher_profile: Mapped["TeacherProfile"] = relationship(back_populates="grade_links")
