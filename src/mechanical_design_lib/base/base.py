import dataclasses


class FormulaBase:
    @dataclasses.dataclass
    class Symbols:
        def display(self):
            raise NotImplementedError

    @dataclasses.dataclass
    class Formulas:
        def display(self):
            raise NotImplementedError

    def __init__(self):
        self._symbols = self.Symbols()
        self._formulas = self.Formulas()

        self._init_formula()

    def display(self):
        self.display_symbols()
        self.display_formulas()

    def _init_formula(self):
        raise NotImplementedError

    @property
    def symbols(self):
        return self._symbols

    @property
    def formulas(self):
        return self._formulas

    def display_symbols(self):
        self._symbols.display()

    def display_formulas(self):
        self._formulas.display()

    def calculate(self, symbols: Symbols):
        raise NotImplementedError
