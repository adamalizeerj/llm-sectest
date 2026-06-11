import os

import pytest

from llm_sectest.client import TargetClient, TargetConfig
from llm_sectest.oracles import Sentinels


@pytest.fixture(scope="session")
def attempts() -> int:
    # Best-of-N. Lower for speed on constrained hardware, raise for flakier models.
    return int(os.environ.get("LLM_SECTEST_ATTEMPTS", "3"))


@pytest.fixture(scope="session")
def client() -> TargetClient:
    base = os.environ.get("TARGET_BASE_URL", "http://localhost:8000")
    c = TargetClient(TargetConfig(base_url=base))
    if not c.reachable():
        pytest.skip(f"Target not reachable at {base}. Start uvicorn from the repo root first.")
    return c


@pytest.fixture(scope="session")
def sentinels() -> Sentinels:
    return Sentinels()
