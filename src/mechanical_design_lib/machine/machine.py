import mechanical_design_lib.utils.flowchart as flowchart
from mechanical_design_lib.actuator.actuator import BaseActuator


class Machine:
    def __init__(self):
        self.units = []

    def add_unit(self, unit):
        self.units.append(unit)


class MachineUnit:
    def __init__(self, name: str):
        self._name = name
        self.behaviors = {}

    def add_behavior(self, behavior):
        self.behaviors[behavior.name] = behavior


class MachineUnitBehavior:
    def __init__(self, name: str):
        self._name = name
        self.behavior_summaries = []

    def add_behavior_summary(self, behavior_summary):
        self.behavior_summaries.append(behavior_summary)

    @property
    def name(self):
        return self._name


class BehaviorSummary(flowchart.Subroutine):
    def __init__(self, description: str,
                 root_element: flowchart.FlowchartElement = None,
                 is_parse_subroutine: bool = False
                 ):
        super().__init__(description,
                         subroutine_root_element=root_element,
                         is_parse_subroutine=is_parse_subroutine
                         )
        self._description = description


class BehaviorDetailAction(flowchart.Action):
    # def __init__(self, action: str, actuator: BaseActuator = None):
    #     super().__init__(action)
    #     self._actuator = actuator

    def __init__(self, action: str, action_time: float = None):
        super().__init__(action)
        self._action_time = action_time


if __name__ == "__main__":

    # フローチャートの作成例
    root = flowchart.Root("Start")

    after_root_connector = flowchart.Connector("").add_from(root)
    input1 = flowchart.Input("User Input").add_next(after_root_connector)

    action1 = BehaviorDetailAction("Action 1").add_from(after_root_connector)
    action2 = BehaviorDetailAction("Action 2").add_from(action1)
    action3 = BehaviorDetailAction("Action 3").add_from(action2)
    action4 = BehaviorDetailAction("Action 4").add_from(action3)

    action5 = BehaviorDetailAction("Action 5").add_from(action4)
    action6 = BehaviorDetailAction("Action 6").add_from(action4)

    action7 = BehaviorDetailAction("Action 7").add_from(action4)
    action8 = BehaviorDetailAction("Action 8").add_from(action7)

    action9 = BehaviorDetailAction("Action 8")\
        .add_from(action5)\
        .add_from(action6)\
        .add_from(action8)\

    action10 = BehaviorDetailAction("Action 10").add_from(action9)

    loop_start = flowchart.LoopStart("Loop Start").add_from(action10)

    action11 = BehaviorDetailAction("Action 11").add_from(loop_start)
    action12 = BehaviorDetailAction("Action 12").add_from(action11)
    action13 = BehaviorDetailAction("Action 13").add_from(action12)

    loop_end = flowchart.LoopEnd("Loop End").add_from(action13)

    action14 = BehaviorDetailAction("Action 14").add_from(loop_end)

    decision = flowchart.Decision("Is Condition True?").add_from(action14)
    action15 = BehaviorDetailAction("Action 15")
    action16 = BehaviorDetailAction("Action 16")

    decision.add_yes(action15)
    decision.add_no(action16)

    end = flowchart.Root("End").add_from(action15).add_from(action16)
    
    behavior_start = flowchart.Root("Behavior Root")
    behavior_summary = BehaviorSummary(
        "Complex Example Summary",
        root_element=root,
        is_parse_subroutine=True
    ).add_from(behavior_start)

    behavior_end = flowchart.Root("Behavior End").add_from(behavior_summary)

    fc = flowchart.Flowchart(behavior_start)
    fc.post_process()
    fc.draw(filename="complex_example_summary")
