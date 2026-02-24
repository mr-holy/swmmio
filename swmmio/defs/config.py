# config.py - cleaned
import os

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FONT_PATH = os.path.join(ROOT_DIR, 'swmmio', 'graphics', 'fonts', 'Verdana.ttf')

# These can be overridden by environment variables
SWMM_EXE_PATH = os.environ.get("SWMM_EXE_PATH", "swmm5")
