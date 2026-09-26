import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest

from app.seed_data import seed


@pytest.fixture(scope="session", autouse=True)
def seeded_db():
    seed()
