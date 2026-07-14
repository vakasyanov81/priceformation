"""fixtures for integration tests"""

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str((_ROOT / "../src").resolve()))
