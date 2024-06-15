import dataclasses
import sympy
from IPython.display import display, Latex

from mechanical_design_lib.utils.unit import UnitConverter, UnitSymbol
from mechanical_design_lib.utils.util import get_latex_symbol_and_unit


class SteppingMotor:

    def __init__(self,
                 phase: int,
                 microstep_resolution: int,  # 1: full step, 2: half step, 4: quarter step,,,
                 ):
        self._phase = phase
        self._microstep_resolution = microstep_resolution

        self._microstep_rate = 1 / microstep_resolution
        self._step_angle = 360 / (self.phase * 100) * \
            self._microstep_rate  # degree

    @property
    def phase(self) -> int:
        return self._phase

    @property
    def step_angle(self) -> float:
        return self._step_angle

    def get_pps(self, rpm: float) -> float:
        return (rpm / 60) * (360 / self.step_angle)

    def get_rpm(self, pps: float) -> float:
        return (pps / (360 / self.step_angle)) * 60

    def get_pulse(self, revolute_angle: float) -> float:
        return revolute_angle / self.step_angle


class StartingPulseRate:
    @dataclasses.dataclass
    class Symbols:
        fs: UnitSymbol = UnitSymbol('f_s', 'Hz')
        jo: UnitSymbol = UnitSymbol('J_o', 'kg*m^2')
        jl: UnitSymbol = UnitSymbol('J_l', 'kg*m^2')

        def display(self):
            display(Latex("----- Symbols -----"))
            display(get_latex_symbol_and_unit(
                "Starting pulse rate of the stepping motor", self.fs.symbol, self.fs.unit))
            display(get_latex_symbol_and_unit(
                "Inertia of the rotor", self.jo.symbol, self.jo.unit))
            display(get_latex_symbol_and_unit(
                "Inertia of the load", self.jl.symbol, self.jl.unit))

    @dataclasses.dataclass
    class Formula:
        f: UnitSymbol = UnitSymbol('f', 'Hz')

    def __init__(self):

        self._symbols = self.Symbols()
        self._formula = self.Formula()

        self._init_formula()

    def _init_formula(self):
        s = self._symbols

        f = s.fs.symbol / sympy.sqrt(1 + (s.jl.symbol / s.jo.symbol))

        self._formula.f = UnitSymbol(f, 'Hz')

    @property
    def symbols(self):
        return self._symbols

    @property
    def formula(self):
        return self._formula

    def display_symbols(self):
        self._symbols.display()

    def display_formula(self):
        sympy.pprint(self._formula)

    def calculate(self, symbols: Symbols):
        return self._formula.f.symbol.subs({
            self._symbols.fs.symbol: symbols.fs.value,
            self._symbols.jo.symbol: symbols.jo.value,
            self._symbols.jl.symbol: symbols.jl.value,
        })


if __name__ == '__main__':
    motor = SteppingMotor(phase=2, microstep_resolution=1)
    print(motor.get_pps(60))
    print(motor.get_rpm(200))
