"""small utilities for more complex calculations"""
from pathlib import Path
import os



def is_env_path_valid(env_path: Path) -> bool:

    res = False

    if env_path.exists() and env_path.is_file() and os.path.basename(env_path) == '.env':
        res = True

    return res
