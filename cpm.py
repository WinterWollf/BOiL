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
        Draws an Activity on Node (AON) network diagram with proper node sizing and positioning.
        """
        G = nx.DiGraph()

        max_ef = max(a.EF for a in self.activities.values())
        G.add_node("START", label_inside=f"ES: {0}   T: {0}   EF: {0}\nLS: {0}   R: {0}   LF: {0}",
                   label_above="START")
        G.add_node("END",
                   label_inside=f"ES: {max_ef}   T: {max_ef}   EF: {max_ef}\nLS: {max_ef}   R: {max_ef}   LF: {max_ef}",
                   label_above="END")

        for name, act in self.activities.items():
            label_inside = f"ES: {act.ES}   T: {act.duration}   EF: {act.EF}\nLS: {act.LS}   R: {act.reserve}   LF: {act.LF}"
            G.add_node(name, label_inside=label_inside, label_above=name)

        # Adding edges
        for name, act in self.activities.items():
            if not act.predecessors:
                G.add_edge("START", name)
            for pred in act.predecessors:
                G.add_edge(pred, name)
            successors = [s for s in self.activities.values() if name in s.predecessors]
            if not successors:
                G.add_edge(name, "END")

        # Calculate positions
        topo_order = list(nx.topological_sort(G))
        levels = {}
        for node in topo_order:
            predecessors = list(G.predecessors(node))
            levels[node] = 0 if not predecessors else max(levels[pred] for pred in predecessors) + 1

        level_groups = {}
        for node, level in levels.items():
            if level not in level_groups:
                level_groups[level] = []
            level_groups[level].append(node)

        pos = {}
        max_level = max(levels.values())
        max_nodes_in_level = max(len(nodes) for nodes in level_groups.values())

        # Dynamic spacing based on number of nodes
        horizontal_spacing = 6.0
        vertical_spacing = max(2.0, 20.0 / max_nodes_in_level)

        for level in range(max_level + 1):
            nodes_in_level = level_groups.get(level, [])
            level_height = len(nodes_in_level) * vertical_spacing
            start_y = level_height / 2
            for i, node in enumerate(nodes_in_level):
                pos[node] = (level * horizontal_spacing, start_y - i * vertical_spacing)

        pos["START"] = (-horizontal_spacing, 0)
        pos["END"] = ((max_level + 1) * horizontal_spacing, 0)

        fig, ax = plt.subplots(figsize=(max_level * 2 + 4, max_nodes_in_level + 2))

        # Node parameters
        node_width = 3.2
        node_height = 0.6
        critical_nodes = set(self.critical_path)
        regular_nodes = set(self.activities.keys()) - critical_nodes
        start_end_nodes = {"START", "END"}

        # Draw nodes
        for node in start_end_nodes:
            x, y = pos[node]
            ax.add_patch(plt.Rectangle((x - node_width / 2, y - node_height / 2), node_width, node_height,
                                       color='lightgreen', ec='black', zorder=2))

        for node in regular_nodes:
            x, y = pos[node]
            ax.add_patch(plt.Rectangle((x - node_width / 2, y - node_height / 2), node_width, node_height,
                                       color='lightblue', ec='black', zorder=2))

        for node in critical_nodes:
            x, y = pos[node]
            ax.add_patch(plt.Rectangle((x - node_width / 2, y - node_height / 2), node_width, node_height,
                                       color='salmon', ec='black', zorder=2))

        # Draw edges
        critical_edges = [(self.critical_path[i], self.critical_path[i + 1])
                          for i in range(len(self.critical_path) - 1)]
        critical_edges.extend([("START", name) for name in self.critical_path
                               if not self.activities[name].predecessors])
        critical_edges.extend([(name, "END") for name in self.critical_path
                               if not [s for s in self.activities.values() if name in s.predecessors]])

        regular_edges = [edge for edge in G.edges() if edge not in critical_edges]

        nx.draw_networkx_edges(G, pos, edgelist=regular_edges, edge_color='gray',
                               arrows=True, arrowstyle='->', arrowsize=20, width=2,
                               connectionstyle="arc3,rad=0.1", min_target_margin=20)

        nx.draw_networkx_edges(G, pos, edgelist=critical_edges, edge_color='red',
                               arrows=True, arrowstyle='->', arrowsize=20, width=2,
                               connectionstyle="arc3,rad=0.1", min_target_margin=20)

        # Draw labels
        labels_above = nx.get_node_attributes(G, 'label_above')
        labels_inside = nx.get_node_attributes(G, 'label_inside')

        label_pos_above = {node: (x, y + node_height / 2 + 0.2) for node, (x, y) in pos.items()}

        nx.draw_networkx_labels(G, label_pos_above, labels_above, font_size=10, font_weight='bold')
        nx.draw_networkx_labels(G, pos, labels_inside, font_size=7, verticalalignment='center')

        plt.title("CPM (Activity on Node)\nRed: Critical Path")
        plt.axis('off')
        plt.tight_layout()

        # Automatic view adjustment
        ax.set_xlim(min(x - node_width for x, y in pos.values()) - 1,
                    max(x + node_width for x, y in pos.values()) + 1)
        ax.set_ylim(min(y - node_height for x, y in pos.values()) - 1,
                    max(y + node_height for x, y in pos.values()) + 1)

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

        plt.show()
