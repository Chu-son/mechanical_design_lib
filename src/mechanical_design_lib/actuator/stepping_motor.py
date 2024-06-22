import dataclasses
import sympy
from IPython.display import display, Latex

from mechanical_design_lib.utils.unit import UnitConverter, UnitSymbol
from mechanical_design_lib.utils.unit import Angle, Distance

from mechanical_design_lib.utils.util import display_latex_symbol_and_unit
from mechanical_design_lib.base.base import FormulaBase
from mechanical_design_lib.power_transmission_component import rotary_power_transmission_component as rptc


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

    def get_angle(self, pulse: float) -> float:
        return pulse * self.step_angle


class SteppingMotorActuatorUnit:
    def __init__(self,
                 transmission_component_unit_list: list[rptc.RotaryPowerTransmissionComponentUnitBase],
                 output_component: rptc.OutputComponentBase,
                 stepping_motor: SteppingMotor,
                 ):

        self._transmission_component_unit_list = transmission_component_unit_list
        self._output_component = output_component
        self._stepping_motor = stepping_motor

        self._reduction_ratio = self._culculate_reduction_ratio()

    @property
    def reduction_ratio(self) -> float:
        return self._reduction_ratio

    def _culculate_reduction_ratio(self) -> float:
        reduction_ratio = 1
        for component in self._transmission_component_unit_list:
            reduction_ratio *= component.reduction_ratio
        return reduction_ratio

    def get_pulse(self,
                  distance: Distance | Angle  # mm or degree
                  ) -> float:
        return self._stepping_motor.get_pulse(
            self._output_component.get_angle(distance) * self.reduction_ratio
        )

    def get_pps(self,
                speed: float  # mm/s or degree/s
                ) -> float:
        return self._stepping_motor.get_pps(
            self._output_component.get_rpm(speed) * self.reduction_ratio
        )

    def get_distance(self,
                     pulse: float  # -
                     ) -> Distance | Angle:
        return self._output_component.get_distance(
            self._stepping_motor.get_angle(pulse) / self.reduction_ratio
        )


class StartingPulseRate(FormulaBase):
    @dataclasses.dataclass
    class Symbols(FormulaBase.Symbols):
        fs: UnitSymbol = UnitSymbol('f_s', 'Hz')
        jo: UnitSymbol = UnitSymbol('J_o', 'kg*m^2')
        jl: UnitSymbol = UnitSymbol('J_l', 'kg*m^2')

        def display(self):
            display(Latex("----- Symbols -----"))
            display_latex_symbol_and_unit(
                "Starting pulse rate of the stepping motor", self.fs.symbol, self.fs.unit)
            display_latex_symbol_and_unit(
                "Inertia of the rotor", self.jo.symbol, self.jo.unit)
            display_latex_symbol_and_unit(
                "Inertia of the load", self.jl.symbol, self.jl.unit)

    @dataclasses.dataclass
    class Formulas(FormulaBase.Formulas):
        f: UnitSymbol = UnitSymbol('f', 'Hz')

        def display(self):
            display(Latex("----- Formula -----"))
            display_latex_symbol_and_unit(
                "Starting pulse rate of the stepping motor", self.f.symbol, self.f.unit)

    def __init__(self):
        super().__init__()

    def _init_formula(self):
        s = self._symbols

        f = s.fs.symbol / sympy.sqrt(1 + (s.jl.symbol / s.jo.symbol))

        self._formulas.f = UnitSymbol(f, 'Hz')

    def calculate(self, symbols: Symbols):
        return self._formulas.f.symbol.subs({
            self._symbols.fs.symbol: symbols.fs.value,
            self._symbols.jo.symbol: symbols.jo.value,
            self._symbols.jl.symbol: symbols.jl.value,
        })


if __name__ == '__main__':
    motor = SteppingMotor(phase=2, microstep_resolution=1)
    print(motor.get_pps(60))
    print(motor.get_rpm(200))
