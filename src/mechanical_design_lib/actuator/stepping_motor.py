import dataclasses
import sympy
from IPython.display import display

from mechanical_design_lib.utils.unit import UnitConverter, UnitSymbol


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
        fs: UnitSymbol
        jo: UnitSymbol
        jl: UnitSymbol

        def display(self):
            display(self.fs.symbol)

    class Formula:
        f: sympy.Symbol

    def __init__(self,
                    fs: float,  # Hz
                    jo: float,  # kg*m^2
                    jl: float,  # kg*m^2
                    ):

        self._fs = fs
        self._jo = jo
        self._jl = jl

        self._symbols = self.Symbols(
            fs=UnitSymbol('fs', 'Hz'),
            jo=UnitSymbol('jo', 'kg*m^2'),
            jl=UnitSymbol('jl', 'kg*m^2'),
        )

    def _formula(self):
        s = self._symbols
        f = s.fs / sympy.sqrt(1 + (s.jl / s.jo))

        self._formula = self.Formula(
            f=f
        )

    def display_symbols(self):
        self._symbols.display()

    def display_formula(self):
        sympy.pprint(self._formula)

    def calculate(self):
        self._formula()
        return self._formula.f.subs({
            self._symbols.fs: self._fs,
            self._symbols.jo: self._jo,
            self._symbols.jl: self._jl,
        })

if __name__ == '__main__':
    motor = SteppingMotor(phase=2, microstep_resolution=1)
    print(motor.get_pps(60))
    print(motor.get_rpm(200))
