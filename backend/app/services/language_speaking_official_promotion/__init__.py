"""Speaking official CEFR promotion (S0).

RESPONSIBILITY: Sole runtime writer of official_speaking_cefr (S18+).
S0 provides ownership_guard only.
"""

from app.services.language_speaking_official_promotion.ownership_guard import (
    AUTHORIZED_SPEAKING_CEFR_WRITERS,
    find_official_speaking_cefr_writers,
    verify_speaking_cefr_ownership,
)

__all__ = [
    "AUTHORIZED_SPEAKING_CEFR_WRITERS",
    "find_official_speaking_cefr_writers",
    "verify_speaking_cefr_ownership",
]
