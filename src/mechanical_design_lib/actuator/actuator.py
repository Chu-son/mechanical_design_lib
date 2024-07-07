import sympy
import numpy as np

from mechanical_design_lib.utils.unit import UnitConverter


class BaseActuator:
    def __init__(self,
                 stroke: int,  # unit depends on subclass
                 max_velocity: int,  # unit depends on subclass
                 max_acceleration: float,  # unit depends on subclass
                 max_deceleration: float,  # unit depends on subclass
                 ):
        self._stroke = stroke
        self._max_velocity = max_velocity
        self._max_acceleration = max_acceleration
        self._max_deceleration = max_deceleration

        self._position: int = 0  # unit depends on subclass

    def move_absolute(self,
                      target_position: int,  # unit depends on subclass
                      time: float | None = None,  # s
                      velocity: int | None = None,  # unit depends on subclass
                      acceleration: float | None = None,  # unit depends on subclass
                      deceleration: float | None = None,  # unit depends on subclass
                      ) -> float:
        # validate
        self._validate_move(target_position, time, velocity,
                            acceleration, deceleration)

        self._position = target_position

        if time is not None:
            return time
        else:
            distance = target_position - self._position
            return self._calculate_move_time(distance, velocity, acceleration, deceleration)

    def move_relative(self,
                      distance: int,  # unit depends on subclass
                      time: float | None = None,  # s
                      velocity: int | None = None,  # unit depends on subclass
                      acceleration: float | None = None,  # unit depends on subclass
                      deceleration: float | None = None,  # unit depends on subclass
                      ) -> float:
        # validate
        self._validate_move(self._position + distance, time, velocity,
                            acceleration, deceleration)

        self._position += distance

        if time is not None:
            return time
        else:
            return self._calculate_move_time(distance, velocity, acceleration, deceleration)

    def _calculate_move_time(self,
                             distance: int,  # unit depends on subclass
                             velocity: int | None = None,  # unit depends on subclass
                             acceleration: float | None = None,  # unit depends on subclass
                             deceleration: float | None = None,  # unit depends on subclass
                             ) -> float:
        velocity = velocity or self._max_velocity
        acceleration = acceleration or self._max_acceleration
        deceleration = deceleration or self._max_deceleration

        return distance / velocity

    def _validate_move(self,
                       target_position: int,  # unit depends on subclass
                       time: float | None = None,  # s
                       velocity: int | None = None,  # unit depends on subclass
                       acceleration: float | None = None,  # unit depends on subclass
                       deceleration: float | None = None,  # unit depends on subclass
                       ) -> None:
        if target_position > self._stroke:
            raise ValueError("Target position is out of stroke range.")
        if target_position < 0:
            raise ValueError("Target position is out of stroke range.")

    def move_detail(self,
                    target_position: int,  # unit depends on subclass
                    velocity: int | None = None,  # unit depends on subclass
                    acceleration: float | None = None,  # unit depends on subclass
                    deceleration: float | None = None,  # unit depends on subclass
                    simulation_only: bool = False,
                    ) -> np.ndarray:

        if target_position > self._stroke:
            raise ValueError("Target position is out of stroke range.")
        if target_position < 0:
            raise ValueError("Target position is out of stroke range.")

        if simulation_only:
            self._position = target_position

        velocity = velocity or self._max_velocity
        acceleration = acceleration or self._max_acceleration
        deceleration = deceleration or self._max_deceleration

        # Define symbols
        t_accel = sympy.Symbol('t_accel')
        t_decel = sympy.Symbol('t_decel')
        t_const = sympy.Symbol('t_const')

        # Define equations
        eq1 = sympy.Eq(velocity, acceleration * t_accel)
        eq2 = sympy.Eq(velocity, deceleration * t_decel)
        eq3 = sympy.Eq(target_position, (velocity * t_accel / 2) +
                       velocity * t_const + (velocity * t_decel / 2))

        # Solve equations
        solution = sympy.solve((eq1, eq2, eq3), (t_accel, t_decel, t_const))
        print(f"Solutions: {solution}")

        t_accel = solution[t_accel]
        t_decel = solution[t_decel]
        t_const = solution[t_const]

        t_total = t_accel + t_const + t_decel  # s

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


class LinearActuator(BaseActuator):
    def __init__(self,
                 stroke: int,  # mm
                 max_velocity: int,  # mm/s
                 max_acceleration: float,  # mm/s^2
                 max_deceleration: float,  # mm/s^2
                 ):
        super().__init__(stroke, max_velocity, max_acceleration, max_deceleration)


class RotaryActuator(BaseActuator):
    def __init__(self,
                 stroke: float,  # degree
                 max_velocity: float,  # degree/s
                 max_acceleration: float,  # degree/s^2
                 max_deceleration: float,  # degree/s^2
                 ):
        super().__init__(stroke, max_velocity, max_acceleration, max_deceleration)


class LinearActuatorFactory:
    @staticmethod
    def create_linear_actuator(stroke: int,  # mm
                               time: float,  # s
                               max_velocity: int | None = None,  # mm/s
                               max_acceleration: float | None = None,  # mm/s^2
                               max_deceleration: float | None = None,  # mm/s^2
                               ) -> LinearActuator:

        t_accel = sympy.Symbol('t_accel')
        t_decel = sympy.Symbol('t_decel')

        if max_velocity is not None:
            max_acceleration = UnitConverter.g_to_mm_s2(0.3)
            max_deceleration = UnitConverter.g_to_mm_s2(0.3)

            # TODO
            # # Calculate max_acceleration
            # if max_acceleration is None and max_deceleration is None:
            #     max_acceleration = sympy.Symbol('max_acceleration')
            #     max_deceleration = max_acceleration
            # else:
            #     max_acceleration = max_acceleration or sympy.Symbol(
            #         'max_acceleration')
            #     max_deceleration = max_deceleration or sympy.Symbol(
            #         'max_deceleration')

            # eq1 = sympy.Eq(max_velocity, t_accel * max_acceleration)
            # eq2 = sympy.Eq(max_velocity, t_decel * max_deceleration)
            # eq3 = sympy.Eq(stroke, (max_velocity * t_accel / 2) + max_velocity *
            #                (time - t_accel - t_decel) + (max_velocity * t_decel / 2))

            # solution = sympy.solve(
            #     (eq1, eq2, eq3), (max_acceleration), dict=True)

            # print(f"Solutions: {solution}")

            # if type(solution) is list:
            #     max_acceleration = solution[0][max_acceleration]
            #     max_deceleration = solution[0][max_deceleration]
            #     print(f"max_accel[G]: {max_acceleration * 1000 / G}")
            # else:
            #     max_acceleration = solution[max_acceleration]
            #     max_deceleration = solution[max_deceleration]

        elif max_acceleration is None or max_deceleration is None:
            # Calculate max_velocity with max_acceleration and max_deceleration as 0.3G
            max_acceleration = max_acceleration or UnitConverter.g_to_mm_s2(
                0.3)
            max_deceleration = max_deceleration or UnitConverter.g_to_mm_s2(
                0.3)

            max_velocity = sympy.Symbol('max_velocity')
            eq1 = sympy.Eq(max_velocity, t_accel * max_acceleration)
            eq2 = sympy.Eq(max_velocity, t_decel * max_deceleration)
            eq3 = sympy.Eq(stroke, (max_velocity * t_accel / 2) + max_velocity *
                           (time - t_accel - t_decel) + (max_velocity * t_decel / 2))

            solution = sympy.solve(
                (eq1, eq2, eq3), (t_accel, t_decel, max_velocity), dict=True)

            print(f"Solutions: {solution}")
            if type(solution) is list:
                max_velocity = solution[0][max_velocity]
            else:
                max_velocity = solution[max_velocity]

        else:
            raise ValueError(
                "Either max_velocity or max_acceleration/max_deceleration must be provided.")

        return LinearActuator(stroke, max_velocity, max_acceleration, max_deceleration)


class ScrewActuator(LinearActuator):
    def __init__(self,
                 stroke: int,  # mm
                 max_velocity: int,  # mm/s
                 max_acceleration: float,  # mm/s^2
                 max_deceleration: float,  # mm/s^2
                 pitch: float,  # mm/rev
                 ):
        super().__init__(stroke, max_velocity, max_acceleration, max_deceleration)
        self._pitch = pitch

    def move(self,
             target_position: int,  # mm
             velocity: int | None = None,  # mm/s
             acceleration: float | None = None,  # mm/s^2
             deceleration: float | None = None,  # mm/s^2
             simulation_only: bool = False,
             ) -> np.ndarray:
        return super().move(target_position, velocity, acceleration, deceleration, simulation_only)

    def get_revolution(self, distance: int) -> float:
        return distance / self._pitch


if __name__ == "__main__":
    # actuator = LinearActuator(stroke=600, max_velocity=120,
    #                           max_acceleration=UnitConverter.g_to_mm_s2(0.3),
    #                           max_deceleration=UnitConverter.g_to_mm_s2(0.3)
    #                           )
    # actuator = LinearActuatorFactory.create_linear_actuator(stroke=600, time=3)
    actuator = LinearActuatorFactory.create_linear_actuator(
        stroke=600, time=4, max_velocity=120)
    move_log = actuator.move(target_position=600, simulation_only=True,
                             #  acceleration=UnitConverter.g_to_mm_s2(0.1),
                             #  deceleration=UnitConverter.g_to_mm_s2(0.2)
                             )

    import matplotlib.pyplot as plt

    print(f"Move time: {move_log[0][-1]} s")
    print(f"Max velocity: {np.max(move_log[1])} mm/s")
    plt.plot(move_log[0], move_log[1])
    plt.show()
