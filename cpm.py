import matplotlib.pyplot as plt
import networkx as nx


class CPM:
    def __init__(self, activities):
        self.activities = activities if activities else {}
        self.critical_path = []

    def topologicalSort(self) -> list:
        """
        Returns a list of activities in topological order based on predecessor relationships.
        'activities' is a dictionary {name: Activity}.
        """

        in_degree = {name: 0 for name in self.activities}
        for act in self.activities.values():
            for _ in act.predecessors:
                in_degree[act.name] += 1

        queue = [n for n in in_degree if in_degree[n] == 0]
        topo_order = []

        while queue:
            current = queue.pop(0)
            topo_order.append(current)

            for name, act in self.activities.items():
                if current in act.predecessors:
                    in_degree[name] -= 1
                    if in_degree[name] == 0:
                        queue.append(name)
        return topo_order

    def calculate(self) -> dict:
        """
        Calculates ES, EF, LS, LF times and time reserve for each activity.
        Returns the same 'activities' dictionary with updated values.
        """

        order = self.topologicalSort()

        for name in order:
            act = self.activities[name]

            if not act.predecessors:
                act.ES = 0
            else:
                act.ES = max(self.activities[p].EF for p in act.predecessors)
            act.EF = act.ES + act.duration

        max_EF = max(a.EF for a in self.activities.values())

        for name in reversed(order):
            act = self.activities[name]
            successors = [s for s in self.activities.values() if name in s.predecessors]

            if not successors:
                act.LF = max_EF
            else:
                act.LF = min(s.LS for s in successors)

            act.LS = act.LF - act.duration
            act.reserve = act.LS - act.ES

        self.critical_path = self.criticalPath()
        return self.activities

    def criticalPath(self):
        return [n for n, a in self.activities.items() if a.reserve == 0]

    def print(self) -> None:
        print("CPM Results:")
        for name, act in self.activities.items():
            print(f"  Activity {name}: "
                  f"ES={act.ES}, EF={act.EF}, "
                  f"LS={act.LS}, LF={act.LF}, "
                  f"Reserve={act.reserve}"
                  )

    def printCriticalPath(self) -> None:
        print("Critical Path:", " -> ".join(self.critical_path))

    def drawAON(self) -> None:
        """
        Draws an Activity on Node (AON) network diagram.
        Activities are positioned based on their topological levels and Early Start (ES) times.
        """
        G = nx.DiGraph()

        G.add_node("START", label="START\nES: 0\nEF: 0")
        G.add_node("END",
                   label=f"END\nES: {max(a.EF for a in self.activities.values())}\nEF: {max(a.EF for a in self.activities.values())}")

        # Activity nodes
        for name, act in self.activities.items():
            # label = f"{name}\nDur: {act.duration}\nES: {act.ES}\nEF: {act.EF}"
            label = f"{name}\nES: {act.ES}   T: {act.duration}   EF: {act.EF}\n\nLS: {act.LS}   R: {act.reserve}   LF: {act.LF}"
            G.add_node(name, label=label)

        for name, act in self.activities.items():
            if not act.predecessors:
                G.add_edge("START", name)

        for name, act in self.activities.items():
            for pred in act.predecessors:
                G.add_edge(pred, name)

        # max_EF = max(a.EF for a in self.activities.values())
        for name, act in self.activities.items():
            successors = [s for s in self.activities.values() if name in s.predecessors]
            if not successors:
                G.add_edge(name, "END")

        topo_order = list(nx.topological_sort(G))
        levels = {}
        for node in topo_order:
            predecessors = list(G.predecessors(node))
            if not predecessors:
                levels[node] = 0
            else:
                levels[node] = max(levels[pred] for pred in predecessors) + 1

        level_groups = {}
        for node, level in levels.items():
            if level not in level_groups:
                level_groups[level] = []
            level_groups[level].append(node)

        pos = {}
        max_level = max(levels.values())
        for level in range(max_level + 1):
            nodes_in_level = level_groups.get(level, [])
            for i, node in enumerate(nodes_in_level):
                pos[node] = (level * 3, -i)

        pos["START"] = (-1, 0)
        pos["END"] = ((max_level + 1) * 3, 0)

        critical_nodes = set(self.critical_path)
        regular_nodes = set(self.activities.keys()) - critical_nodes
        start_end_nodes = {"START", "END"}


        # Stare podejscie #
        ####################

        # nx.draw_networkx_nodes(G, pos, nodelist=list(start_end_nodes),
        #                        node_color='lightgreen', node_size=6000,
        #                        node_shape='s')
        #
        # nx.draw_networkx_nodes(G, pos, nodelist=list(regular_nodes),
        #                        node_color='lightblue', node_size=6000,
        #                        node_shape='s')
        #
        # nx.draw_networkx_nodes(G, pos, nodelist=list(critical_nodes),
        #                        node_color='salmon', node_size=6000,
        #                        node_shape='s')

        ####################

        # Nowe podejscie #

        for node in start_end_nodes:
            x, y = pos[node]
            plt.gca().add_patch(plt.Rectangle((x - 1.5, y - 0.1), 3, 0.2, color='lightgreen', ec='black', zorder=2))

        for node in regular_nodes:
            x, y = pos[node]
            plt.gca().add_patch(plt.Rectangle((x - 1.5, y - 0.1), 3, 0.2, color='lightblue', ec='black', zorder=2))

        for node in critical_nodes:
            x, y = pos[node]
            plt.gca().add_patch(plt.Rectangle((x - 1.5, y - 0.1), 3, 0.2, color='salmon', ec='black', zorder=2))


        critical_edges = []
        for i in range(len(self.critical_path) - 1):
            critical_edges.append((self.critical_path[i], self.critical_path[i + 1]))

        for name in self.critical_path:
            if not self.activities[name].predecessors:
                critical_edges.append(("START", name))

        for name in self.critical_path:
            successors = [s for s in self.activities.values() if name in s.predecessors]
            if not successors:
                critical_edges.append((name, "END"))

        regular_edges = [edge for edge in G.edges() if edge not in critical_edges]
        nx.draw_networkx_edges(G, pos, edgelist=regular_edges, edge_color='gray',
                               arrows=True, arrowstyle='->', arrowsize=20, width=2,
                               connectionstyle="arc3,rad=0.1", min_target_margin=20)

        nx.draw_networkx_edges(G, pos, edgelist=critical_edges, edge_color='red',
                               arrows=True, arrowstyle='->', arrowsize=20, width=2,
                               connectionstyle="arc3,rad=0.1", min_target_margin=20)

        labels = nx.get_node_attributes(G, 'label')
        nx.draw_networkx_labels(G, pos, labels, font_size=8)

        plt.title("CPM (Activity on Node)\nRed: Critical Path")

        manager = plt.get_current_fig_manager()
        try:
            manager.window.showMaximized()
        except AttributeError:
            try:
                manager.window.state('zoomed')
            except AttributeError:
                try:
                    manager.frame.Maximize(True)
                except AttributeError:
                    print("Could not maximize window: backend not supported.")

        plt.axis('off')
        plt.show()
