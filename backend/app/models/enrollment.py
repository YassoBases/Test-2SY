"""Student onboarding choices, payments, course access."""

import enum
from datetime import datetime

from sqlalchemy import DateTime, Enum, Float, ForeignKey, Integer, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class OnboardingStep(str, enum.Enum):
    grade = "grade"
    subjects = "subjects"
    teachers = "teachers"
    complete = "complete"


class PaymentStatus(str, enum.Enum):
    pending = "pending"
    paid = "paid"
    failed = "failed"


class PaymentMethod(str, enum.Enum):
    card = "card"
    transfer = "transfer"
    wallet = "wallet"
    cash = "cash"


class PaymentItemProductType(str, enum.Enum):
    course = "course"
    language = "language"


class StudentSubjectChoice(Base):
    __tablename__ = "student_subject_choices"
    __table_args__ = (UniqueConstraint("student_id", "subject_id", name="uq_student_subject"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    subject_id: Mapped[int] = mapped_column(ForeignKey("subjects.id", ondelete="CASCADE"), index=True)

    subject: Mapped["Subject"] = relationship()


class StudentTeacherChoice(Base):
    __tablename__ = "student_teacher_choices"
    __table_args__ = (UniqueConstraint("student_id", "subject_id", name="uq_student_teacher_subject"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    subject_id: Mapped[int] = mapped_column(ForeignKey("subjects.id", ondelete="CASCADE"), index=True)
    teacher_profile_id: Mapped[int] = mapped_column(ForeignKey("teacher_profiles.id"), index=True)

    subject: Mapped["Subject"] = relationship()
    teacher_profile: Mapped["TeacherProfile"] = relationship()


class StudentCourseAccess(Base):
    __tablename__ = "student_course_access"
    __table_args__ = (UniqueConstraint("student_id", "course_id", name="uq_student_course"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    course_id: Mapped[int] = mapped_column(ForeignKey("courses.id", ondelete="CASCADE"), index=True)
    payment_status: Mapped[PaymentStatus] = mapped_column(Enum(PaymentStatus), default=PaymentStatus.pending)
    unlocked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    activated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    course: Mapped["Course"] = relationship(back_populates="access_records")


class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    total_amount: Mapped[float] = mapped_column(Float)
    currency: Mapped[str] = mapped_column(String(10), default="SYP")
    method: Mapped[PaymentMethod | None] = mapped_column(Enum(PaymentMethod), nullable=True)
    status: Mapped[PaymentStatus] = mapped_column(Enum(PaymentStatus), default=PaymentStatus.pending)
    reference: Mapped[str | None] = mapped_column(String(64), nullable=True)
    paid_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    items: Mapped[list["PaymentItem"]] = relationship(back_populates="payment", cascade="all, delete-orphan")


class PaymentItem(Base):
    __tablename__ = "payment_items"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    payment_id: Mapped[int] = mapped_column(ForeignKey("payments.id", ondelete="CASCADE"), index=True)
    product_type: Mapped[PaymentItemProductType] = mapped_column(
        Enum(
            PaymentItemProductType,
            name="payment_item_product_type",
            values_callable=lambda e: [x.value for x in e],
        ),
        default=PaymentItemProductType.course,
    )
    course_id: Mapped[int | None] = mapped_column(ForeignKey("courses.id"), nullable=True, index=True)
    language_product_id: Mapped[int | None] = mapped_column(
        ForeignKey("language_products.id", ondelete="CASCADE"), nullable=True, index=True
    )
    unit_price: Mapped[float] = mapped_column(Float)

    payment: Mapped["Payment"] = relationship(back_populates="items")
    course: Mapped["Course | None"] = relationship()
