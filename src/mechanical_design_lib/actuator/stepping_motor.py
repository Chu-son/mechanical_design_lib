import sympy

from mechanical_design_lib.utils.unit import UnitConverter


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