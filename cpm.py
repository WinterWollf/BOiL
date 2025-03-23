from matplotlib.patches import FancyArrowPatch
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
        Draws an Activity on Node (AON) network diagram with improved layout, arrow spacing, and legend.
        """
        G = nx.DiGraph()

        max_ef = max(a.EF for a in self.activities.values())
        # Use fixed-width formatting for alignment instead of tabs
        G.add_node("START", label_inside=f"{0:>2}       {0:>2}\n{0:>2}  {0:>2}  {0:>2}", label_above="START")
        G.add_node("END", label_inside=f"{max_ef:>2}       {max_ef:>2}\n{max_ef:>2}  {0:>2}  {max_ef:>2}",
                   label_above="END")

        for name, act in self.activities.items():
            # Use fixed-width formatting for consistent alignment
            label_inside = f"{act.ES:>2}  {act.duration:>2}  {act.EF:>2}\n{act.LS:>2}  {act.reserve:>2}  {act.LF:>2}"
            G.add_node(name, label_inside=label_inside, label_above=name)

        for name, act in self.activities.items():
            if not act.predecessors:
                G.add_edge("START", name)
            for pred in act.predecessors:
                G.add_edge(pred, name)
            successors = [s for s in self.activities.values() if name in s.predecessors]
            if not successors:
                G.add_edge(name, "END")

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

        horizontal_spacing = 12.0
        vertical_spacing = max(6.0, 40.0 / max_nodes_in_level)

        for level in range(max_level + 1):
            nodes_in_level = level_groups.get(level, [])
            level_height = len(nodes_in_level) * vertical_spacing
            start_y = level_height / 2
            for i, node in enumerate(nodes_in_level):
                pos[node] = (level * horizontal_spacing, start_y - i * vertical_spacing)

        pos["START"] = (-horizontal_spacing, 0)
        pos["END"] = ((max_level + 1) * horizontal_spacing, 0)

        num_nodes = len(self.activities) + 2
        base_width = 6.0
        base_height = 1.6
        scale_factor = min(1.0, 20.0 / num_nodes)
        node_width = base_width * scale_factor
        node_height = base_height * scale_factor
        base_font_size = 9

        # Increased figure size
        fig, ax = plt.subplots(figsize=(max_level * 4 + 4, max_nodes_in_level * vertical_spacing / 2 + 4))

        critical_nodes = set(self.critical_path)
        regular_nodes = set(self.activities.keys()) - critical_nodes
        start_end_nodes = {"START", "END"}

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

        critical_edges = [(self.critical_path[i], self.critical_path[i + 1])
                          for i in range(len(self.critical_path) - 1)]
        critical_edges.extend([("START", name) for name in self.critical_path
                               if not self.activities[name].predecessors])
        critical_edges.extend([(name, "END") for name in self.critical_path
                               if not [s for s in self.activities.values() if name in s.predecessors]])

        regular_edges = [edge for edge in G.edges() if edge not in critical_edges]

        def is_horizontal_edge(edge):
            (x1, y1), (x2, y2) = pos[edge[0]], pos[edge[1]]
            return abs(y1 - y2) < 1e-5

        regular_horizontal = [edge for edge in regular_edges if is_horizontal_edge(edge)]
        regular_non_horizontal = [edge for edge in regular_edges if not is_horizontal_edge(edge)]

        critical_horizontal = [edge for edge in critical_edges if is_horizontal_edge(edge)]
        critical_non_horizontal = [edge for edge in critical_edges if not is_horizontal_edge(edge)]

        nx.draw_networkx_edges(G, pos, edgelist=regular_non_horizontal, edge_color='gray',
                               arrows=True, arrowstyle='->', arrowsize=20, width=2,
                               connectionstyle="arc3,rad=0.2", min_target_margin=30)

        nx.draw_networkx_edges(G, pos, edgelist=critical_non_horizontal, edge_color='red',
                               arrows=True, arrowstyle='->', arrowsize=20, width=2,
                               connectionstyle="arc3,rad=0.2", min_target_margin=30)

        nx.draw_networkx_edges(G, pos, edgelist=regular_horizontal, edge_color='gray',
                               arrows=True, arrowstyle='->', arrowsize=20, width=2,
                               connectionstyle="arc3,rad=0.0", min_target_margin=30)

        nx.draw_networkx_edges(G, pos, edgelist=critical_horizontal, edge_color='red',
                               arrows=True, arrowstyle='->', arrowsize=20, width=2,
                               connectionstyle="arc3,rad=0.0", min_target_margin=30)

        labels_above = nx.get_node_attributes(G, 'label_above')
        labels_inside = nx.get_node_attributes(G, 'label_inside')

        label_pos_above = {node: (x, y + node_height / 2 + 0.4) for node, (x, y) in pos.items()}

        for node, (x, y) in pos.items():
            ax.text(x, y + node_height / 2 + 0.4, labels_above[node],
                    ha='center', va='bottom', fontweight='bold', fontsize=base_font_size + 2)

            text_obj = ax.text(x, y, labels_inside[node],
                               ha='center', va='center', fontsize=base_font_size,
                               wrap=True, bbox=dict(facecolor='none', edgecolor='none', pad=0))

            renderer = fig.canvas.get_renderer()
            bbox = text_obj.get_window_extent(renderer=renderer)
            bbox_width = bbox.width / fig.dpi
            bbox_height = bbox.height / fig.dpi

            font_size = base_font_size
            while (bbox_width > node_width * 0.85 or bbox_height > node_height * 0.85) and font_size > 4:
                font_size -= 0.5
                text_obj.set_fontsize(font_size)
                bbox = text_obj.get_window_extent(renderer=renderer)
                bbox_width = bbox.width / fig.dpi
                bbox_height = bbox.height / fig.dpi

        # Pin the legend to the bottom-right corner of the screen
        legend_x = 0.03
        legend_y = 0.98

        legend_string = "Legenda"
        legend_text = "ES  T  EF\nLS  R  LF"
        ax.text(legend_x, legend_y, "Legenda",
                ha='left', va='top', fontsize=15, fontstyle="italic", fontweight='600',
                transform=ax.transAxes)  # Użycie układu osi

        ax.text(legend_x, legend_y - 0.05, "ES  T  EF\nLS  R  LF",
                ha='left', va='top', fontsize=12, fontweight='bold',
                bbox=dict(facecolor='white', edgecolor='black', boxstyle='round,pad=0.3'),
                transform=ax.transAxes)  # Użycie układu osi

        plt.title("CPM (Activity on Node)\nRed: Critical Path")
        plt.subplots_adjust(left=0.0, bottom=0.0, right=1.0, top=0.93, wspace=0.2, hspace=0.2)
        plt.axis('off')

        # Automatic view adjustment
        ax.set_xlim(min(x - node_width for x, y in pos.values()) - 3,
                    max(x + node_width for x, y in pos.values()) + 3)
        ax.set_ylim(min(y - node_height for x, y in pos.values()) - 3,
                    max(y + node_height for x, y in pos.values()) + 3)

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
        manager.window.resizable(False, False)

        plt.show()
