from sqlalchemy.dialects import postgresql

from app.services.language_speaking_educational_package.persistence import _student_owner_clause


def _compiled_sql(expr) -> str:
    return str(
        expr.compile(
            dialect=postgresql.dialect(),
            compile_kwargs={"literal_binds": True},
        )
    )


def test_speaking_package_owner_clause_supports_legacy_json_owner_rows() -> None:
    sql = _compiled_sql(_student_owner_clause(123))

    assert "language_content_items.student_id = 123" in sql
    assert "language_content_items.student_id IS NULL" in sql
    assert "owner_student_id" in sql
    assert "'123'" in sql
