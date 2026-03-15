from pathlib import Path


PACKAGE_ROOT = Path(__file__).resolve().parent
SRC_ROOT = PACKAGE_ROOT.parent
REPO_ROOT = SRC_ROOT.parent
DOCS_ROOT = REPO_ROOT / "docs"
ASSETS_ROOT = DOCS_ROOT / "assets"
DATA_ROOT = DOCS_ROOT / "data"
SEEDS_ROOT = PACKAGE_ROOT / "seeds"
DEFAULT_DB_PATH = REPO_ROOT / "chartbook.db"
