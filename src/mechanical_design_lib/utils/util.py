import sympy
from IPython.display import display, Latex
import os
import pathlib
import enum
import time


PROJECT_ROOT_PATH = pathlib.Path(__file__).parent.parent.parent.parent
EXEC_DATE_STR = time.strftime("%Y%m%d_%H%M%S")


def get_latex_symbol_and_unit(
        label: str,
        symbol: sympy.Symbol,
        unit: sympy.Symbol,
):
    if unit == "":
        return Latex(rf"{label}: $ \ {sympy.latex(symbol)}$")
    return Latex(rf"{label}: $ \ {sympy.latex(symbol)} \ [{sympy.latex(unit)}]$")


def display_latex_symbol_and_unit(
        label: str,
        symbol: sympy.Symbol,
        unit: sympy.Symbol,
):
    display(get_latex_symbol_and_unit(label, symbol, unit))


class DirectoryFactory:
    __DIRECTORIES = {}
    __OUTPUT_DIRECTORY = PROJECT_ROOT_PATH / "output"
    __ENV_PREFIX = "MDL_DIR"
    __ENV_OUTPUT_DIRECTORY = f"{__ENV_PREFIX}_OUTPUT"

    class DirectoryName(enum.Enum):
        LOG = "log"
        DATA = "data"

    @classmethod
    def get_directory(cls, name: DirectoryName):
        if cls.__DIRECTORIES.get(name) is None:
            env_name = cls.get_env_from_directory_name(name)
            if env_name in os.environ:
                directory_path = pathlib.Path(
                    os.environ[env_name]) / EXEC_DATE_STR
            elif cls.__ENV_OUTPUT_DIRECTORY in os.environ:
                directory_path = pathlib.Path(
                    os.environ[cls.__ENV_OUTPUT_DIRECTORY]) / EXEC_DATE_STR / name.value
            else:
                directory_path = cls.__OUTPUT_DIRECTORY / EXEC_DATE_STR / name.value

            if not os.path.exists(directory_path):
                os.makedirs(directory_path)
            cls.__DIRECTORIES[name] = directory_path
        return cls.__DIRECTORIES[name]

    @staticmethod
    def get_env_from_directory_name(directory_name: DirectoryName) -> str:
        return f"{DirectoryFactory.__ENV_PREFIX}_{directory_name.value.upper()}"
