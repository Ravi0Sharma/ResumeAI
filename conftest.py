import sys
from pathlib import Path

# Ensure repository root is importable when running pytest from any subdir.
_REPO_ROOT = Path(__file__).resolve().parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))


