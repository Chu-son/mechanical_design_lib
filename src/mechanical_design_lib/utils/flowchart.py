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

    def get_nextlinks(self):
        return self._next_elements
        # return copy.deepcopy(self._next_elements)

    def get_backlinks(self):
        return self._elements_backlinks
        # return copy.deepcopy(self._elements_backlinks)

    def drop_nextlink(self, element):
        self._next_elements = [(next_element, label) for next_element,
                               label in self._next_elements if next_element != element]

    def replace_nextlink(self, element, new_element):
        for i, (next_element, label) in enumerate(self._next_elements):
            if next_element == element:
                self._next_elements[i] = (new_element, label)
                new_element.add_backlink(self)
                element.drop_backlink(self)
                return

    def drop_backlink(self, element):
        self._elements_backlinks = [
            backlink for backlink in self._elements_backlinks if backlink != element]

    def replace_backlink(self, element, new_element):
        for i, backlink in enumerate(self._elements_backlinks):
            if backlink == element:
                self._elements_backlinks[i] = new_element
                new_element.add_next(self)
                element.drop_nextlink(self)
                return

    def post_process(self):
        pass

    def copy_to(self, element):
        element._next_elements = self._next_elements
        element._elements_backlinks = self._elements_backlinks

        return element


class Action(FlowchartElement):
    def add_to_graph(self, graph):
        graph.graph.node(self.id, self.label, shape='box', style='rounded')


class Decision(FlowchartElement):
    def __init__(self, label):
        super().__init__(label)

        self._yes_root_element = None
        self._no_root_element = None

        self._yes_next_element = None
        self._no_next_element = None

    def add_yes(self, element):
        self._yes_root_element = element
        return self

    def add_no(self, element):
        self._no_root_element = element
        return self

    def add_yes_next(self, element):
        self._yes_next_element = element
        return self

    def add_no_next(self, element):
        self._no_next_element = element
        return self

    def post_process(self):
        if self._yes_root_element is None \
                or self._no_root_element is None:
            raise ValueError('Decision element is not properly set.')

        if self._yes_next_element is None or self._no_next_element is None:
            next_links = self.get_nextlinks()
            if len(next_links) > 1:
                raise ValueError(
                    'Decision element has multiple next elements.')

            if self._yes_next_element is None:
                self._yes_next_element = next_links[0][0]

            if self._no_next_element is None:
                self._no_next_element = next_links[0][0]

        self._next_elements = []

        self.add_next(self._yes_root_element, 'Yes')
        get_last_element(self._yes_root_element).add_next(
            self._yes_next_element)

        self.add_next(self._no_root_element, 'No')
        get_last_element(self._no_root_element).add_next(self._no_next_element)


    def add_to_graph(self, graph):
        graph.graph.node(self.id, self.label, shape='diamond')


class Subroutine(FlowchartElement):
    def __init__(self, label, subroutine_root_element=None, is_parse_subroutine=False):
        super().__init__(label)
        self._subroutine_root_element = subroutine_root_element
        self._is_parse_subroutine = is_parse_subroutine

    def add_to_graph(self, graph):
        graph.graph.node(self.id, f" | {self.label} | ", shape='record')

    @property
    def subroutine_root_element(self):
        return self._subroutine_root_element

    @property
    def is_parse_subroutine(self):
        return self._is_parse_subroutine

    def post_process(self):
        if self.is_parse_subroutine:
            first_element = self._subroutine_root_element
            new_first_element = self._subroutine_root_element.copy_to(
                Connector('Subroutine Start Connector'))
            for next_element, label in first_element.get_nextlinks():
                next_element.replace_backlink(first_element, new_first_element)

            last_element = get_last_element(new_first_element)
            new_last_element = last_element.copy_to(
                Connector('Subroutine End Connector'))
            for backlink in last_element.get_backlinks():
                backlink.replace_nextlink(last_element, new_last_element)

            for next_element, label in self.get_nextlinks():
                new_last_element.add_next(next_element, label)
                next_element.drop_backlink(self)

            for backlink in self.get_backlinks():
                backlink.add_next(new_first_element)
                backlink.drop_nextlink(self)

            self._subroutine_root_element = new_first_element


class Loop(FlowchartElement):
    def __init__(self, label: str, loop_count: int):
        super().__init__(label)
        self._loop_start = LoopStart(f'{label} Start\n (n= {loop_count})')
        self._loop_end = LoopEnd(f'{label} End')

        self._loop_content = None
        self._loop_count = loop_count

    def set_loop_content(self, root_element):
        self._loop_content = root_element

    @property
    def label(self):
        return f"{self._label}\n (n= {self._loop_count})"

    def post_process(self):
        self._loop_start.add_next(self._loop_content)
        last_elem = get_last_element(self._loop_content)
        last_elem.add_next(self._loop_end)

        tmp_backlinks = self.get_backlinks()
        for backlink in self.get_backlinks():
            backlink.replace_nextlink(self, self._loop_start)
        self._elements_backlinks = tmp_backlinks

        tmp_nextlinks = self.get_nextlinks()
        for next_element, label in self.get_nextlinks():
            next_element.replace_backlink(self, self._loop_end)
        self._next_elements = tmp_nextlinks


class Parallel(FlowchartElement):
    def __init__(self, label):
        super().__init__(label)
        self._parallel_elements = []

        self._parallel_start_connector = Connector(f'{label} Start Connector')
        self._parallel_end_connector = Connector(f'{label} End Connector')

    def add_parallel_element(self, root_element):
        self._parallel_elements.append(root_element)
        return self

    def post_process(self):
        for element in self._parallel_elements:
            self._parallel_start_connector.add_next(element)
            last_elem = get_last_element(element)
            last_elem.add_next(self._parallel_end_connector)

        tmp_backlinks = self.get_backlinks()
        for backlink in self.get_backlinks():
            backlink.replace_nextlink(self, self._parallel_start_connector)
        self._elements_backlinks = tmp_backlinks

        tmp_nextlinks = self.get_nextlinks()
        for next_element, label in self.get_nextlinks():
            next_element.replace_backlink(self, self._parallel_end_connector)
        self._next_elements = tmp_nextlinks


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
        if current_element in visited:
            continue
        visited.add(current_element)

        next_elements = current_element.get_nextlinks()
        if not next_elements:
            return current_element

        for next_element, _ in next_elements:
            if next_element not in visited:
                queue.append(next_element)

    return None


class ElementIterator:
    def __init__(self,
                 root_element: FlowchartElement,
                 ) -> None:
        self._root_element = root_element

    def __iter__(self):
        queue = [self._root_element]
        visited = set()

        while queue:
            current_element = queue.pop(0)
            if current_element in visited:
                continue
            visited.add(current_element)

            print(f"Current element: {current_element.label}")
            yield current_element

            next_elements = current_element.get_nextlinks()
            for next_element, _ in next_elements:
                if next_element not in visited:
                    queue.append(next_element)

            backlinks = current_element.get_backlinks()
            for backlink in backlinks:
                if backlink not in visited:
                    queue.append(backlink)


class ElementsCompiler:
    @staticmethod
    def compile(root_element) -> FlowchartElement:
        # root_element から走査して、新しい FlowchartElement を作成する
        new_root_element = copy.deepcopy(root_element)
        for element in ElementIterator(new_root_element):
            element.post_process()

        return new_root_element


class Flowchart:
    def __init__(self, root_element):
        self.root_element = root_element

        self.graph = Digraph(format='png')
        self.visited_nodes = set()
        self.visited_edges = set()

    def _post_process(self):
        # for element in self._get_elements():
        print("Post processing")
        # for element in ElementIterator(self.root_element):
        #     element.post_process()
        self.root_element = ElementsCompiler.compile(self.root_element)
        print("Post processing done")

    def draw(self, filename='flowchart', view=True):
        if not self.root_element:
            raise ValueError('Root element is not set.')
        self._post_process()

        self._add_elements_to_graph(self.root_element)
        self.graph.render(filename,
                          view=view,
                          )

    def _add_elements_to_graph(self, element):
        if element.id in self.visited_nodes:
            return

        print(f"Adding element: {element.label}")
        element.add_to_graph(self)
        self.visited_nodes.add(element.id)

        for next_element, label in element.get_nextlinks():
            self._add_edges_to_graph(element, next_element, label)

        for backlink in element.get_backlinks():
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

    # サブルーチン
    sub_root = Root('Subroutine Start')
    sub_action = Action('Subroutine Action 1').add_from(sub_root)
    sub_action2 = Action('Subroutine Action 2').add_from(sub_action)
    sub_end = Root('Subroutine End').add_from(sub_action2)

    # メインのフローチャート
    root = Root('Start')

    after_root_connector = Connector('').add_from(root)
    input1 = Input('User Input').add_next(after_root_connector)

    action1 = Action('Action 1').add_from(after_root_connector)
    decision = Decision('Is Condition True?').add_from(action1)

    action2 = Action('Action 2')
    subroutine = Subroutine('Subroutine', sub_root, is_parse_subroutine=True,
                            ).add_from(action2)

    decision.add_yes(action2)

    action3 = Action('Action 3')
    loop_start = LoopStart('Loop Start').add_from(action3)
    action4 = Action('Action 4').add_from(loop_start)
    loop_end = LoopEnd('Loop End').add_from(action4)

    decision.add_no(action3)

    end = Root('End').add_from(decision)

    # フローチャート描画
    flowchart = Flowchart(root)
    flowchart.draw('example_flowchart')
