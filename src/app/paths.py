import pathlib
from typing import Final


APP_PATH: Final = pathlib.Path(__file__).parent
SRC_PATH: Final = APP_PATH.parent
ROOT_PATH: Final = SRC_PATH.parent

USER_DIR_PATH: Final = ROOT_PATH / "user_dir"
