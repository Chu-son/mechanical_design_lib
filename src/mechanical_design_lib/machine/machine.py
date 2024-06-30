import uuid
from graphviz import Digraph


class Machine:
    def __init__(self):
        self.units = []

    def add_unit(self, unit):
        self.units.append(unit)


class MachineUnit:
    def __init__(self, name: str):
        self._name = name
        self.behaviors = []

    def add_behavior(self, behavior):
        self.behaviors.append(behavior)


class Behavior:
    def __init__(self, name: str):
        self._name = name
        self.behavior_summaries = []

    def add_behavior_summary(self, behavior_summary):
        self.behavior_summaries.append(behavior_summary)

    def add_behavior_summary_chain(self, behavior_summary):
        self.behavior_summaries.append(behavior_summary)
        return self


class BehaviorDetail:
    def __init__(self, detail: str):
        self._detail = detail
        self._id = uuid.uuid4()  # ユニークなIDを生成


class IF(BehaviorDetail):
    def __init__(self, condition: str):
        super().__init__(condition)
        self._true_branch = []
        self._false_branch = []

    def add_true_branch(self, detail):
        self._true_branch.append(detail)

    def add_false_branch(self, detail):
        self._false_branch.append(detail)


class LOOP(BehaviorDetail):
    def __init__(self, condition: str):
        super().__init__(condition)
        self._loop_body = []

    def add_to_loop(self, detail):
        self._loop_body.append(detail)


class JUMP(BehaviorDetail):
    def __init__(self, target: BehaviorDetail):
        super().__init__(f"Jump to {target._detail}")
        self._target = target


class PARALLEL(BehaviorDetail):
    def __init__(self):
        super().__init__("Parallel Processes")
        self.parallel_branches = []

    def add_parallel_branch(self, branch):
        self.parallel_branches.append(branch)


class BehaviorSummary:
    def __init__(self, description: str):
        self._description = description
        self.behavior_details = []
        self.detail_relations = []

    def add_behavior_detail(self, behavior_detail):
        if not self.behavior_details:
            self.behavior_details.append(behavior_detail)
        else:
            last_detail = self.behavior_details[-1]
            self.detail_relations.append((last_detail, behavior_detail, ""))
            self.behavior_details.append(behavior_detail)

    def add_detail_relation(self, start_detail, end_detail, label=""):
        self.detail_relations.append((start_detail, end_detail, label))

    def draw_flowchart(self, filename='flowchart'):
        dot = Digraph(comment='Behavior Detail Flowchart')

        for detail in self.behavior_details:
            dot.node(str(detail._id), detail._detail)

        for start, end, label in self.detail_relations:
            dot.edge(str(start._id), str(end._id), label=label)

        dot.render(filename, view=True, format='png')


if __name__ == "__main__":
    behavior_summary = BehaviorSummary("Complex Example Summary")

    # 開始
    start = BehaviorDetail("Start")
    behavior_summary.add_behavior_detail(start)

    # 並列処理
    parallel_process = PARALLEL()
    parallel_1 = BehaviorDetail("Parallel 1")
    parallel_2 = BehaviorDetail("Parallel 2")
    parallel_process.add_parallel_branch(parallel_1)
    parallel_process.add_parallel_branch(parallel_2)
    behavior_summary.add_behavior_detail(parallel_process)
    behavior_summary.add_detail_relation(start, parallel_process)
    behavior_summary.add_detail_relation(parallel_process, parallel_1, "Parallel")
    behavior_summary.add_detail_relation(parallel_process, parallel_2, "Parallel")

    # 並列処理終了後
    after_parallel = BehaviorDetail("After Parallel")
    behavior_summary.add_behavior_detail(after_parallel)
    behavior_summary.add_detail_relation(parallel_1, after_parallel)
    behavior_summary.add_detail_relation(parallel_2, after_parallel)

    # 条件分岐
    condition = IF("Condition: x > 5")
    behavior_summary.add_behavior_detail(condition)
    behavior_summary.add_detail_relation(after_parallel, condition)

    # 真の場合のループ処理
    loop = LOOP("While x < 10")
    loop_detail = BehaviorDetail("Increment x")
    loop.add_to_loop(loop_detail)
    condition.add_true_branch(loop)
    behavior_summary.add_behavior_detail(loop_detail)
    behavior_summary.add_detail_relation(condition, loop, "True")
    behavior_summary.add_detail_relation(loop, loop_detail)

    # 偽の場合のジャンプ処理
    end = BehaviorDetail("End")
    jump_to_end = JUMP(end)
    condition.add_false_branch(jump_to_end)
    behavior_summary.add_behavior_detail(end)
    behavior_summary.add_detail_relation(condition, end, "False")

    # 終了
    behavior_summary.add_detail_relation(loop_detail, end)

    behavior_summary.draw_flowchart('complex_example_flowchart')
