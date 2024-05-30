import enum
import sympy

G = 9.81  # m/s^2


class UnitConverter:
    @staticmethod
    def g_to_mm_s2(acceleration_g: float) -> float:
        return acceleration_g * G * 1000
