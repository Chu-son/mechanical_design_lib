import sympy
import numpy as np


G = 9.81  # m/s^2


class UnitConverter:
    @staticmethod
    def g_to_mm_s2(acceleration_g: float) -> float:
        return acceleration_g * G * 1000


class LinearActuator:
    def __init__(self,
                 stroke: int,  # mm
                 max_velocity: int,  # mm/s
                 max_acceleration: float,  # mm/s^2
                 max_deceleration: float,  # mm/s^2
                 ):
        self._stroke = stroke
        self._max_velocity = max_velocity
        self._max_acceleration = max_acceleration
        self._max_deceleration = max_deceleration

        self._position: int = 0  # mm

    def move(self,
             target_position: int,  # mm
             velocity: int | None = None,  # mm/s
             acceleration: float | None = None,  # mm/s^2
             deceleration: float | None = None,  # mm/s^2
             only_simulation: bool = False,
             ) -> np.ndarray:

        if target_position > self._stroke:
            raise ValueError("Target position is out of stroke range.")
        if target_position < 0:
            raise ValueError("Target position is out of stroke range.")

        if only_simulation:
            self._position = target_position

        velocity = velocity or self._max_velocity
        acceleration = acceleration or self._max_acceleration
        deceleration = deceleration or self._max_deceleration

        t_accel = velocity / acceleration  # s
        dx_accel = velocity * t_accel / 2  # mm

        t_decel = velocity / deceleration  # s
        dx_decel = velocity * t_decel / 2  # mm

        dx_const = target_position - dx_accel - dx_decel  # mm
        t_const = dx_const / velocity  # s

        t_total = t_accel + t_const + t_decel  # s
        x_total = dx_accel + dx_const + dx_decel  # mm

        delta_t = 0.01  # s
        t_array = np.arange(0, t_total, delta_t)
        v_array = np.zeros_like(t_array)

        for i, t in enumerate(t_array):
            if t < t_accel:
                v_array[i] = acceleration * t
            elif t < t_accel + t_const:
                v_array[i] = velocity
            else:
                v_array[i] = velocity - deceleration * (t - t_accel - t_const)

        return np.array([t_array, v_array])


if __name__ == "__main__":
    actuator = LinearActuator(stroke=600, max_velocity=120,
                              max_acceleration=UnitConverter.g_to_mm_s2(0.3),
                              max_deceleration=UnitConverter.g_to_mm_s2(0.3)
                              )
    move_log = actuator.move(target_position=600, only_simulation=True,
                             acceleration=UnitConverter.g_to_mm_s2(0.1),
                             deceleration=UnitConverter.g_to_mm_s2(0.2)
                             )

    import matplotlib.pyplot as plt

    print(f"Move time: {move_log[0][-1]} s")
    print(f"Max velocity: {np.max(move_log[1])} mm/s")
    plt.plot(move_log[0], move_log[1])
    plt.show()
