from graphviz import Digraph
import uuid

import copy


class FlowchartElement:
    def __init__(self, label):
        self._label = label
        self._id = str(uuid.uuid4())
        self._next_elements = []
        self._elements_backlinks = []

    def add_next(self, element, label=''):
        self._next_elements.append((element, label))
        element.add_backlink(self)
        return self

    def add_from(self, element, label=''):
        element.add_next(self, label)
        return self

    def add_to_graph(self, graph):
        raise NotImplementedError

    def add_backlink(self, element):
        self._elements_backlinks.append(element)

    @property
    def label(self):
        return self._label

    @property
    def id(self):
        return self._id

    @property
    def next_elements(self):
        return self._next_elements

    @property
    def elements_backlinks(self):
        return self._elements_backlinks


class Action(FlowchartElement):
    def add_to_graph(self, graph):
        graph.graph.node(self.id, self.label, shape='box', style='rounded')


class Decision(FlowchartElement):
    def add_yes(self, element):
        self.add_next(element, 'Yes')

    def add_no(self, element):
        self.add_next(element, 'No')

    def add_to_graph(self, graph):
        graph.graph.node(self.id, self.label, shape='diamond')


class Subroutine(FlowchartElement):
    def __init__(self, label, subroutine_root_element=None, is_parse_subroutine=False):
        super().__init__(label)
        self._subroutine_root_element = subroutine_root_element
        self._is_parse_subroutine = is_parse_subroutine

    def add_to_graph(self, graph):
        if self.is_parse_subroutine and self.subroutine_root_element:
            self.subroutine_root_element.add_to_graph(graph)
        else:
            graph.graph.node(self.id, f" | {self.label} | ", shape='record')

    @property
    def next_elements(self):
        if self.is_parse_subroutine and self.subroutine_root_element:
            return self.subroutine_root_element.next_elements
        else:
            return self._next_elements

    @property
    def elements_backlinks(self):
        if self.is_parse_subroutine and self.subroutine_root_element:
            return self.subroutine_root_element.elements_backlinks
        else:
            return self._elements_backlinks

    def add_next(self, element, label=''):
        if self.is_parse_subroutine and self.subroutine_root_element:
            get_last_element(
                self.subroutine_root_element).add_next(element, label)
            print(get_last_element(self._subroutine_root_element).label)
            print(element.label)
            return self
        else:
            super().add_next(element, label)

    def add_from(self, element, label=''):
        if self.is_parse_subroutine and self.subroutine_root_element:
            self.subroutine_root_element.add_from(element, label)
            return self
        else:
            super().add_from(element, label)

    def add_backlink(self, element):
        if self.is_parse_subroutine and self.subroutine_root_element:
            get_last_element(
                self.subroutine_root_element).add_backlink(element)
        else:
            super().add_backlink(element)

    @property
    def subroutine_root_element(self):
        return self._subroutine_root_element

    @property
    def is_parse_subroutine(self):
        return self._is_parse_subroutine


class Input(FlowchartElement):
    def add_to_graph(self, graph):
        graph.graph.node(self.id, self.label, shape='parallelogram')


class Root(FlowchartElement):
    def add_to_graph(self, graph):
        graph.graph.node(self.id, self.label, shape='ellipse')


class LoopStart(FlowchartElement):
    def add_to_graph(self, graph):
        graph.graph.node(self.id, self.label, shape='trapezium')


class LoopEnd(FlowchartElement):
    def add_to_graph(self, graph):
        graph.graph.node(self.id, self.label, shape='invtrapezium')


class Connector(FlowchartElement):
    def add_to_graph(self, graph):
        graph.graph.node(self.id, self.label, shape='point')


# 幅優先探索で最後の要素を取得
def get_last_element(element):
    queue = [element]
    visited = set()

    while queue:
        current_element = queue.pop(0)
        visited.add(current_element)

        next_elements = current_element.next_elements
        if not next_elements:
            return current_element

        for next_element, _ in next_elements:
            if next_element not in visited:
                queue.append(next_element)

    return None


class Flowchart:
    def __init__(self, root_element):
        self.root_element = root_element

        self.graph = Digraph(format='png')
        self.visited_nodes = set()
        self.visited_edges = set()

    def draw(self, filename='flowchart'):
        if not self.root_element:
            raise ValueError('Root element is not set.')

        self._add_elements_to_graph(self.root_element)
        self.graph.render(filename, view=True)

    def _add_elements_to_graph(self, element):
        if element.id in self.visited_nodes:
            return

        element.add_to_graph(self)
        self.visited_nodes.add(element.id)

        for next_element, label in element.next_elements:
            self._add_edges_to_graph(element, next_element, label)

        for backlink in element.elements_backlinks:
            self._add_elements_to_graph(backlink)

    def _add_edges_to_graph(self, element, next_element, label):
        edge = (element.id, next_element.id)

        if edge not in self.visited_edges:
            next_element.add_to_graph(self)
            self.graph.edge(element.id, next_element.id, label)
            self.visited_edges.add(edge)

            self._add_elements_to_graph(next_element)


if __name__ == '__main__':
    # フローチャートの作成例

    # 要素の追加
    sub_root = Action('Subroutine Action 1')
    sub_action2 = Action('Subroutine Action 2').add_from(sub_root)

    # 要素の追加
    root = Root('Start')

    after_root_connector = Connector('').add_from(root)
    input1 = Input('User Input').add_next(after_root_connector)

    action1 = Action('Action 1').add_from(after_root_connector)
    decision = Decision('Is Condition True?').add_from(action1)

    action2 = Action('Action 2')
    action3 = Action('Action 3')
    decision.add_yes(action2)
    decision.add_no(action3)

    subroutine = Subroutine('Subroutine', sub_root, is_parse_subroutine=True,
                            ).add_from(action2)

    loop_start = LoopStart('Loop Start').add_from(action3)
    action4 = Action('Action 4').add_from(loop_start)
    loop_end = LoopEnd('Loop End').add_from(action4)

    end = Root('End')
    end.add_from(subroutine)
    end.add_from(loop_end)

    # フローチャートの描画
    flowchart = Flowchart(root)
    flowchart.draw('example_flowchart_with_subroutine_and_input')
