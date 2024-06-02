import sympy
import numpy as np

from mechanical_design_lib.utils.unit import UnitConverter


class GearedMotor:
    def __init__(self,
                 gear_rate: int  # unitless
                 ):
        self._gear_rate = gear_rate

    @property
    def gear_rate(self) -> int:
        return self._gear_rate

    def get_output_rpm(self, input_rpm: float) -> float:
        return input_rpm / self.gear_rate

    def get_input_rpm(self, output_rpm: float) -> float:
        return output_rpm * self.gear_rate
