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
        """
        G = nx.DiGraph()

        max_ef = max(a.EF for a in self.activities.values())
        G.add_node("START", label_inside=f"{0:>2}       {0:>2}\n{0:>2}  {0:>2}  {0:>2}", label_above="START")
        G.add_node("END", label_inside=f"{max_ef:>2}       {max_ef:>2}\n{max_ef:>2}  {0:>2}  {max_ef:>2}",
                   label_above="END")

        for name, act in self.activities.items():
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

        base_offset = 0.2
        scaling_factor = 10.0
        curvature_offset = base_offset * (num_nodes / scaling_factor)
        curvature_offset = min(max(curvature_offset, 0.1), 0.5)

        def get_dynamic_rad(edge):
            (x1, y1), (x2, y2) = pos[edge[0]], pos[edge[1]]
            vertical_dist = abs(y1 - y2)
            horizontal_dist = abs(x1 - x2)
            rad = curvature_offset * (vertical_dist / (horizontal_dist + 1e-5))
            return min(max(rad, 0.1), 0.5)

        base_margin = 40.0
        dynamic_margin = base_margin * scale_factor
        dynamic_margin = max(dynamic_margin, 20.0)

        for edge in regular_non_horizontal:
            rad = get_dynamic_rad(edge)
            adjusted_margin = dynamic_margin * (1 + rad)
            nx.draw_networkx_edges(G, pos, edgelist=[edge], edge_color='gray',
                                   arrows=True, arrowstyle='->', arrowsize=25, width=2,
                                   connectionstyle=f"arc3,rad={rad}", min_target_margin=adjusted_margin)

        for edge in critical_non_horizontal:
            rad = get_dynamic_rad(edge)
            adjusted_margin = dynamic_margin * (1 + rad)
            nx.draw_networkx_edges(G, pos, edgelist=[edge], edge_color='red',
                                   arrows=True, arrowstyle='->', arrowsize=25, width=2.5,
                                   connectionstyle=f"arc3,rad={rad}", min_target_margin=adjusted_margin)

        nx.draw_networkx_edges(G, pos, edgelist=regular_horizontal, edge_color='gray',
                               arrows=True, arrowstyle='->', arrowsize=25, width=2,
                               connectionstyle="arc3,rad=0.0", min_target_margin=dynamic_margin)

        nx.draw_networkx_edges(G, pos, edgelist=critical_horizontal, edge_color='red',
                               arrows=True, arrowstyle='->', arrowsize=25, width=2.5,
                               connectionstyle="arc3,rad=0.0", min_target_margin=dynamic_margin)

        labels_above = nx.get_node_attributes(G, 'label_above')
        labels_inside = nx.get_node_attributes(G, 'label_inside')

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

        legend_x = 0.03
        legend_y = 0.98

        ax.text(legend_x, legend_y, "Legenda",
                ha='left', va='top', fontsize=15, fontstyle="italic", fontweight='600',
                transform=ax.transAxes)

        ax.text(legend_x, legend_y - 0.05, "ES  T  EF\nLS  R  LF",
                ha='left', va='top', fontsize=12, fontweight='bold',
                bbox=dict(facecolor='white', edgecolor='black', boxstyle='round,pad=0.3'),
                transform=ax.transAxes)

        plt.title("CPM (Activity on Node)\nRed: Critical Path")
        plt.subplots_adjust(left=0.0, bottom=0.0, right=1.0, top=0.93, wspace=0.2, hspace=0.2)
        plt.axis('off')

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

    def drawAOA(self) -> None:
        """
        Draws an Activity on Arrow (AOA) network.
        """
        G = nx.DiGraph()

        event_counter = 0
        event_times = {}
        activity_to_edges = {}

        G.add_node(event_counter)
        event_times[event_counter] = 0
        start_event = event_counter
        event_counter += 1

        events = {frozenset(): start_event}
        activity_to_start_event = {}
        activity_to_end_event = {}

        topo_order = self.topologicalSort()

        successor_to_activities = {}
        for name in topo_order:
            successors = frozenset([s for s in self.activities.keys() if name in self.activities[s].predecessors])
            if successors not in successor_to_activities:
                successor_to_activities[successors] = []
            successor_to_activities[successors].append(name)

        activity_to_end_node = {}

        for name in topo_order:
            act = self.activities[name]
            predecessors = frozenset(act.predecessors)

            if not predecessors:
                start_event = 0
            else:
                predecessor_ends = frozenset([p for p in predecessors])
                if predecessor_ends not in events:
                    start_time = max(self.activities[pred].EF for pred in predecessors)
                    events[predecessor_ends] = event_counter
                    event_times[event_counter] = start_time
                    G.add_node(event_counter)
                    for pred in predecessors:
                        pred_end = activity_to_end_node[pred]
                        if not G.has_edge(pred_end, event_counter):
                            G.add_edge(pred_end, event_counter, label="", duration=0, reserve=0)
                    event_counter += 1
                start_event = events[predecessor_ends]
            activity_to_start_event[name] = start_event

            successors = frozenset([s for s in self.activities.keys() if name in self.activities[s].predecessors])

            ending_activities = frozenset(successor_to_activities.get(successors, [name]))
            if ending_activities not in events:
                end_time = max(self.activities[n].EF for n in ending_activities)
                events[ending_activities] = event_counter
                event_times[event_counter] = end_time
                G.add_node(event_counter)
                event_counter += 1
            end_event = events[ending_activities]
            activity_to_end_event[name] = end_event
            activity_to_end_node[name] = end_event

            G.add_edge(start_event, end_event, label=name, duration=act.duration, reserve=act.reserve)
            activity_to_edges[name] = (start_event, end_event)

        end_activities = frozenset([name for name, act in self.activities.items() if
                                    not any(name in s.predecessors for s in self.activities.values())])
        if end_activities not in events:
            end_time = max(self.activities[name].EF for name in end_activities)
            events[end_activities] = event_counter
            event_times[event_counter] = end_time
            G.add_node(event_counter)
            end_event = event_counter
            event_counter += 1
        else:
            end_event = events[end_activities]

        for name in end_activities:
            last_event = activity_to_end_event[name]
            if last_event != end_event and not G.has_edge(last_event, end_event):
                G.add_edge(last_event, end_event, label="", duration=0, reserve=0)

        event_earliest = {}
        event_latest = {}
        event_slack = {}

        for event, time in event_times.items():
            event_earliest[event] = time
            event_latest[event] = float('inf')
            event_slack[event] = 0

        event_earliest[0] = 0
        max_time = max(event_times.values())
        event_latest[end_event] = max_time

        topo_order = list(nx.topological_sort(G))
        for event in reversed(topo_order):
            successors = list(G.successors(event))
            if not successors:
                event_latest[event] = max_time
            else:
                min_successor_time = float('inf')
                for succ in successors:
                    for edge in G.edges(data=True):
                        if edge[0] == event and edge[1] == succ:
                            duration = edge[2]['duration']
                            successor_earliest = event_earliest[succ]
                            min_successor_time = min(min_successor_time, successor_earliest - duration)
                event_latest[event] = min_successor_time if min_successor_time != float('inf') else max_time

            event_slack[event] = event_latest[event] - event_earliest[event]

        for event in G.nodes():
            j = event
            t0_j = event_earliest[event]
            t1_j = event_latest[event]
            L_j = event_slack[event]
            label = f"{j}\n{t0_j:>2}       {t1_j:>2}\n{L_j:>2}"
            G.nodes[event]['label'] = label

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

        fig, ax = plt.subplots(figsize=(max_level * 3 + 4, max_nodes_in_level * vertical_spacing / 2 + 4))

        node_size = 2500
        critical_activities = set(self.critical_path)

        critical_nodes = set()
        for activity in critical_activities:
            start_event, end_event = activity_to_edges[activity]
            critical_nodes.add(start_event)
            critical_nodes.add(end_event)

        start_node = 0
        end_node = end_event

        node_colors = []
        for node in G.nodes():
            if node == start_node:
                node_colors.append('lightgreen')
            elif node == end_node:
                node_colors.append('lightcoral')
            elif node in critical_nodes:
                node_colors.append('salmon')
            else:
                node_colors.append('lightblue')

        nx.draw_networkx_nodes(G, pos, node_size=node_size, node_color=node_colors, node_shape='o', ax=ax)

        edges_by_target = {}
        for edge in G.edges(data=True):
            start, end, data = edge
            if end not in edges_by_target:
                edges_by_target[end] = []
            edges_by_target[end].append((start, end, data))

        for target, edges in edges_by_target.items():
            num_edges = len(edges)
            for idx, (start, end, data) in enumerate(edges):
                activity_name = data['label']
                if not activity_name:
                    edge_color = 'black'
                    edge_width = 1.0
                    style = 'dashed'
                    rad = 0.0 if abs(pos[start][1] - pos[end][1]) < 1e-5 else 0.3
                    nx.draw_networkx_edges(
                        G, pos, edgelist=[(start, end)], edge_color=edge_color,
                        width=edge_width, style=style, arrows=False,
                        connectionstyle=f"arc3,rad={rad}", ax=ax
                    )
                    continue
                is_critical = activity_name in critical_activities
                edge_color = 'red' if is_critical else 'black'
                edge_width = 2.5 if is_critical else 1.5

                (x1, y1), (x2, y2) = pos[start], pos[end]
                if num_edges > 1:
                    rad = 0.3 + 0.2 * (idx - (num_edges - 1) / 2)
                else:
                    rad = 0.0 if abs(y1 - y2) < 1e-5 else 0.3

                nx.draw_networkx_edges(
                    G, pos, edgelist=[(start, end)], edge_color=edge_color,
                    width=edge_width, arrows=True, arrowstyle='->', arrowsize=20,
                    connectionstyle=f"arc3,rad={rad}", ax=ax,
                    min_target_margin=40
                )

                t = 0.3
                mid_x = x1 + t * (x2 - x1)
                mid_y = y1 + t * (y2 - y1)
                offset_y = 0.5 * (idx - (num_edges - 1) / 2)
                mid_y += offset_y
                label = f"{activity_name}\nDur: {data['duration']}"
                ax.text(
                    mid_x, mid_y, label, fontsize=9, ha='center', va='center', fontweight='bold',
                    bbox=dict(facecolor='white', edgecolor='none', alpha=0.7)
                )

        labels = nx.get_node_attributes(G, 'label')
        for node, label in labels.items():
            x, y = pos[node]
            ax.text(x, y, label, ha='center', va='center', fontsize=9,
                    bbox=dict(facecolor='none', edgecolor='none', pad=0))

        legend_x = 0.03
        legend_y = 0.98
        ax.text(legend_x, legend_y, "Legenda",
                ha='left', va='top', fontsize=12, fontstyle="italic", fontweight='600',
                transform=ax.transAxes)
        ax.text(legend_x, legend_y - 0.05, "     No.\nES      LS\n      R",
                ha='left', va='top', fontsize=10, fontweight='bold',
                bbox=dict(facecolor='white', edgecolor='black', boxstyle='round,pad=0.3'),
                transform=ax.transAxes)

        plt.title("CPM (Activity on Arrow)\nRed Edges: Critical Path")
        plt.axis('off')

        plt.subplots_adjust(left=0.015, bottom=0.015, right=0.985, top=0.93, wspace=0.2, hspace=0.2)

        ax.set_xlim(min(x for x, y in pos.values()) - 2, max(x for x, y in pos.values()) + 2)
        ax.set_ylim(min(y for x, y in pos.values()) - 2, max(y for x, y in pos.values()) + 2)

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
