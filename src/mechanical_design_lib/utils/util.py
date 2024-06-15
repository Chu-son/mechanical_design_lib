import sympy
from IPython.display import display, Latex


def get_latex_symbol_and_unit(
        label: str,
        symbol: sympy.Symbol,
        unit: sympy.Symbol,
):
    return Latex(f"{label}: $ \ {sympy.latex(symbol)} \ [{sympy.latex(unit)}]$")


def display_latex_symbol_and_unit(
        label: str,
        symbol: sympy.Symbol,
        unit: sympy.Symbol,
):
    display(get_latex_symbol_and_unit(label, symbol, unit))
