import mechanical_design_lib.utils.flowchart as flowchart
from mechanical_design_lib.actuator.actuator import BaseActuator

from mechanical_design_lib.utils.util import DirectoryFactory
from mechanical_design_lib.utils.logger import LoggerFactory

logger = LoggerFactory.get_logger(__name__)


class BehaviorSummary(flowchart.Subroutine):
    def __init__(self, description: str,
                 root_element: flowchart.FlowchartElement = None,
                 is_parse_subroutine: bool = False,
                 takt_time: float = None,
                 ):
        super().__init__(description,
                         subroutine_root_element=root_element,
                         is_parse_subroutine=is_parse_subroutine
                         )
        self._description = description
        self._takt_time = takt_time

    def get_takt_time(self,
                      parse_subroutine: bool = True,
                      ) -> float:
        if parse_subroutine and self.subroutine_root_element is not None:
            return self._calc_takt_time()

        elif self._takt_time is not None:
            return self._takt_time
        else:
            raise ValueError("Takt time is not set.")

    def _calc_takt_time(self) -> float:
        takt_time = 0
        for element in flowchart.ElementIterator(self.subroutine_root_element):
            if hasattr(element, "get_takt_time"):
                tt = element.get_takt_time()
                if tt is None:
                    continue
                takt_time += tt

        return takt_time


class BehaviorDetailAction(flowchart.Action):
    # def __init__(self, action: str, actuator: BaseActuator = None):
    #     super().__init__(action)
    #     self._actuator = actuator

    def __init__(self,
                 action: str,
                 takt_time: float = None,
                 ):
        super().__init__(action)
        self._takt_time = takt_time

    @property
    def label(self):
        return f"{self._label}\n (takt time: {self._takt_time})"

    def get_takt_time(self) -> float:
        if self._takt_time is None:
            logger.warn(f"Warning: Takt time is not set for {self.label}")

        logger.info(f"Action: {self._label}, takt time: {self._takt_time}")
        return self._takt_time


class BehaviorParallel(flowchart.Parallel):
    def __init__(self, description: str):
        super().__init__(description)

    def add_parallel_element(self, root_element: BehaviorDetailAction):
        return super().add_parallel_element(root_element)

    def get_takt_time(self) -> float:
        takt_time = 0
        for element in self._parallel_elements:
            element_takt_time = 0
            for e in flowchart.ElementIterator(element):
                if hasattr(e, "get_takt_time"):
                    tt = e.get_takt_time()
                    if tt is None:
                        continue
                    element_takt_time += tt

            takt_time = max(takt_time, element_takt_time)

        logger.info(f"Parallel: {self.label}, max takt time: {takt_time}")
        return takt_time


class BehaviorLoop(flowchart.Loop):
    def __init__(self, description: str, loop_count: int):
        super().__init__(description, loop_count)

    def set_loop_content(self, root_element: BehaviorDetailAction):
        return super().set_loop_content(root_element)

    def get_takt_time(self) -> float:
        takt_time = 0
        for element in flowchart.ElementIterator(self._loop_content):
            if hasattr(element, "get_takt_time"):
                tt = element.get_takt_time()
                if tt is None:
                    continue
                takt_time += tt

        takt = takt_time * self._loop_count
        logger.info(f"Loop: {self.label}, takt time: {
            takt_time} x {self._loop_count} = {takt}")
        return takt


class BehaviorDecision(flowchart.Decision):
    def __init__(self, description: str, default_yes: bool = True):
        super().__init__(description)

        self._default_yes = default_yes

    def get_takt_time(self) -> float:
        takt_time = 0

        if self._default_yes:
            for element in flowchart.ElementIterator(self._yes_root_element):
                if hasattr(element, "get_takt_time"):
                    tt = element.get_takt_time()
                    if tt is None:
                        continue
                    takt_time += tt

        else:
            for element in flowchart.ElementIterator(self._no_root_element):
                if hasattr(element, "get_takt_time"):
                    tt = element.get_takt_time()
                    if tt is None:
                        continue
                    takt_time += tt

        logger.info(f"Decision: {self.label}, Value: {
            "Yes" if self._default_yes else "No"}, takt time: {takt_time}")
        return takt_time


class MachineUnit:
    def __init__(self, name: str):
        self._name = name
        self._behaviors = {}

    def add_behavior(self, behavior_name: str, behavior: BehaviorSummary):
        if behavior_name in self._behaviors:
            raise ValueError(f"Behavior {behavior_name} already exists.")

        self._behaviors[behavior_name] = behavior
        return self

    def get_behavior(self, behavior_name: str):
        if behavior_name not in self._behaviors:
            raise ValueError(f"Behavior {behavior_name} does not exist.")
        return self._behaviors[behavior_name]


class Machine:
    def __init__(self):
        self.units = {}

    def add_unit(self, unit: MachineUnit):
        if unit._name in self.units:
            raise ValueError(f"Unit {unit._name} already exists.")

        self.units[unit._name] = unit
        return self


if __name__ == "__main__":
    # フローチャートの作成
    root = flowchart.Root("Start")

    after_root_connector = flowchart.Connector("").add_from(root)
    input1 = flowchart.Input("User Input").add_next(after_root_connector)

    action1 = BehaviorDetailAction("Action 1",
                                   takt_time=1.0,
                                   ).add_from(after_root_connector)
    action2 = BehaviorDetailAction("Action 2",
                                   takt_time=1.0,
                                   ).add_from(action1)

    # parallel
    parallel1 = BehaviorParallel("Parallel 1").add_from(action2)

    action3 = BehaviorDetailAction("Action 3",
                                   takt_time=1.0,
                                   )
    parallel1.add_parallel_element(action3)

    action4 = BehaviorDetailAction("Action 4",
                                   takt_time=1.0,
                                   )
    parallel1.add_parallel_element(action4)

    action5 = BehaviorDetailAction("Action 5",
                                   takt_time=1.0,
                                   )
    action6 = BehaviorDetailAction("Action 6",
                                   takt_time=1.0,
                                   ).add_from(action5)
    parallel1.add_parallel_element(action5)
    # parallel end

    action7 = BehaviorDetailAction("Action 7",
                                   takt_time=1.0,
                                   ).add_from(parallel1)

    # loop
    loop1 = BehaviorLoop("Loop 1",
                         loop_count=3,
                         ).add_from(action7)

    action8 = BehaviorDetailAction("Action 8",
                                   takt_time=1.0,
                                   )
    action9 = BehaviorDetailAction("Action 9",
                                   takt_time=1.0,
                                   ).add_from(action8)

    loop1.set_loop_content(root_element=action8)
    # loop end

    action10 = BehaviorDetailAction("Action 10",
                                    takt_time=1.0,
                                    ).add_from(loop1)

    decision = BehaviorDecision("Is Condition True?").add_from(action10)
    action11 = BehaviorDetailAction("Action 11",
                                    takt_time=1.0,
                                    )
    action12 = BehaviorDetailAction("Action 12",
                                    takt_time=1.0,
                                    )

    decision.add_yes(action11)
    decision.add_no(action12)

    end = flowchart.Root("End")

    decision.add_next(end)

    # BehaviorSummaryとしてまとめる
    behavior_start = flowchart.Root("Behavior Root")
    behavior_summary = BehaviorSummary(
        "Complex Example Summary",
        root_element=root,
        is_parse_subroutine=True
    ).add_from(behavior_start)

    behavior_end = flowchart.Root("Behavior End").add_from(behavior_summary)

    # フローチャート描画
    fc = flowchart.Flowchart(behavior_start)
    fc.draw(filename="machine_behavior_example",
            # view=True,
            view=False,
            )

    logger.info(f"takt time: {behavior_summary.get_takt_time()}")
