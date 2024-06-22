import numpy as np
from typing import List, Union

from mechanical_design_lib.utils.unit import UnitType


class OutputComponentBase:
    def __init__(self,
                 pitch_diameter: float,  # mm
                 distance_unit: UnitType = UnitType.DISTANCE,  # Distance or Angle
                 ):
        self._pitch_diameter = pitch_diameter
        self._distance_unit = distance_unit

        if distance_unit not in [UnitType.DISTANCE, UnitType.ANGLE]:
            raise ValueError("Base unit must be Distance or Angle.")

    def get_revolution(self,
                       distance: float  # mm or degree
                       ) -> float:  # revolution
        if self._distance_unit == UnitType.DISTANCE:
            return distance / (self._pitch_diameter * np.pi)
        elif self._distance_unit == UnitType.ANGLE:
            return distance / 360
        else:
            raise ValueError("Base unit must be Distance or Angle.")

    def get_angle(self,
                  distance: float  # mm or degree
                  ) -> float:  # degree
        return self.get_revolution(distance) * 360

    def get_rpm(self,
                speed: float  # mm/s or degree/s
                ) -> float:
        if self._distance_unit == UnitType.DISTANCE:
            return speed / (self._pitch_diameter * np.pi) * 60
        elif self._distance_unit == UnitType.ANGLE:
            return speed / 360 * 60
        else:
            raise ValueError("Base unit must be Distance or Angle.")

    @property
    def pitch_diameter(self) -> float:
        return self._pitch_diameter


class Pulley(OutputComponentBase):
    def __init__(self,
                 pulley_diameter: float,  # mm
                 distance_unit: UnitType = UnitType.DISTANCE,  # Distance or Angle
                 ):
        super().__init__(
            pitch_diameter=pulley_diameter,
            distance_unit=distance_unit,
        )

    @property
    def pulley_diameter(self) -> float:
        return self._pitch_diameter


class RotaryPowerTransmissionComponentBase(OutputComponentBase):
    def __init__(self,
                 pitch_diameter: float,  # mm
                 ):
        self._pitch_diameter = pitch_diameter

        super().__init__(
            pitch_diameter=pitch_diameter,
        )


class TimingPulley(RotaryPowerTransmissionComponentBase):
    def __init__(self,
                 pulley_diameter: float,  # mm
                 ):
        super().__init__(
            pulley_diameter=pulley_diameter,
        )

    @property
    def pulley_diameter(self) -> float:
        return self._pitch_diameter


class Gear(RotaryPowerTransmissionComponentBase):
    def __init__(self,
                 module: float,  # mm
                 number_of_teeth: int,  # -
                 width: float,  # mm
                 ):
        self._module = module
        self._number_of_teeth = number_of_teeth
        self._width = width

        pitch_diameter = module * number_of_teeth
        super().__init__(pitch_diameter=pitch_diameter)

    @property
    def module(self) -> float:
        return self._module

    @property
    def number_of_teeth(self) -> int:
        return self._number_of_teeth

    @property
    def width(self) -> float:
        return self._width


class SpurGear(Gear):
    def __init__(self,
                 module: float,  # mm
                 number_of_teeth: int,  # -
                 width: float,  # mm
                 ):
        super().__init__(module, number_of_teeth, width)


class RotaryPowerTransmissionComponentUnitBase:
    def __init__(self,
                 #  components: list[RotaryPowerTransmissionComponentBase |
                 #                   "RotaryPowerTransmissionComponentUnitBase"],
                 components: List[Union[RotaryPowerTransmissionComponentBase,
                                        "RotaryPowerTransmissionComponentUnitBase"]],
                 ):
        self._components = components

        self._validate()

        self._reduction_ratio = self._culculate_reduction_ratio()

    @property
    def reduction_ratio(self) -> float:
        return self._reduction_ratio

    def _validate(self):
        if len(self._components) < 2:
            raise ValueError("Number of components must be more than 2.")

    def _culculate_reduction_ratio(self):
        raise NotImplementedError


class SingleStageGears(RotaryPowerTransmissionComponentUnitBase):
    def __init__(self,
                 gear_list: list[Gear],
                 ):
        super().__init__(components=gear_list)

    def _culculate_reduction_ratio(self):
        return self._components[-1].number_of_teeth / self._components[0].number_of_teeth


class MultiStageGears(RotaryPowerTransmissionComponentUnitBase):
    def __init__(self,
                 single_stage_gears_list: list[SingleStageGears],
                 ):
        super().__init__(components=single_stage_gears_list)

    def _validate(self):
        if len(self._components) < 1:
            raise ValueError("Number of components must be more than 2.")

    def _culculate_reduction_ratio(self):
        reduction_ratio = 1
        for single_stage_gears in self._components:
            reduction_ratio *= single_stage_gears.reduction_ratio

        return reduction_ratio
