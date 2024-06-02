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

    def get_pps(self, rpm: float) -> float:
        return (rpm / 60) * (360 / self.step_angle)

    def get_rpm(self, pps: float) -> float:
        return (pps / (360 / self.step_angle)) * 60
    
    def get_pulse(self, revolute_angle: float) -> float:
        return revolute_angle / self.step_angle



if __name__ == '__main__':
    motor = SteppingMotor(phase=2, microstep_resolution=1)
    print(motor.get_pps(60))
    print(motor.get_rpm(200))
