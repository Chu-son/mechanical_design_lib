import enum
import sympy
from typing import NewType

from mechanical_design_lib.utils.constant import GRAVITY as G


Angle = NewType("Angle", float)
Distance = NewType("Distance", float)
Pulse = NewType("Pulse", float)
PPS = NewType("PPS", float)


class UnitType(enum.IntEnum):
    ANGLE = enum.auto()
    DISTANCE = enum.auto()
    PULSE = enum.auto()


class UnitConverter:
    @staticmethod
    def g_to_mm_s2(acceleration_g: float) -> float:
        return acceleration_g * G * 1000


class SIPrefix(enum.Enum):
    YOTTA = 24
    ZETTA = 21
    EXA = 18
    PETA = 15
    TERA = 12
    GIGA = 9
    MEGA = 6
    KILO = 3
    HECTO = 2
    DECA = 1
    NONE = 0
    DECI = -1
    CENTI = -2
    MILLI = -3
    MICRO = -6
    NANO = -9
    PICO = -12
    FEMTO = -15
    ATTO = -18
    ZEPTO = -21
    YOCTO = -24


class SIPrefixedValue:
    def __init__(self, value: float, prefix: SIPrefix):
        self._value = value
        self._prefix = prefix

    @property
    def value(self) -> float:
        return self._value

    def convert_to(self, prefix: SIPrefix) -> float:
        return self.value * 10 ** (self.prefix.value - prefix.value)

    @property
    def prefix(self) -> SIPrefix:
        return self._prefix

    def __str__(self) -> str:
        return f"{self.value} [{self.prefix.name}]"


class UnitSymbol:
    def __init__(self, name: str | sympy.Symbol, unit: str | sympy.Symbol, value: float | None = None):
        self._symbol = sympy.Symbol(name) if isinstance(name, str) else name
        self._unit = sympy.Symbol(unit) if isinstance(unit, str) else unit
        self._value = value

    @property
    def unit(self) -> sympy.Symbol:
        return self._unit

    @property
    def symbol(self) -> sympy.Symbol:
        return self._symbol

    @property
    def value(self) -> float:
        return self._value

    @value.setter
    def value(self, value: float):
        if self._value is not None:
            print(f"Warning: {self._symbol} is already set to {
                  self._value}. Overwriting with {value}.")
        self._value = value
