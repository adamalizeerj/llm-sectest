"""Phase 3 attack catalogue, now sourced from the YAML payload sets (Phase 4),
so the pytest suite and the engine share one source of truth. Kept as a shim so
tests/test_owasp_llm.py imports unchanged."""
from llm_sectest.payloads import AttackCase, Category, load_categories  # noqa: F401

CATEGORIES = load_categories()
