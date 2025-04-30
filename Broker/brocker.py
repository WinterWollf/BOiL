import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
from collections import deque
import threading
import traceback
from line_profiler_pycharm import profile

class IntermediaryProblemApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Intermediary Problem Solver")
        self.suppliers = 2
        self.receivers = 3
        self.supply = []
        self.demand = []
        self.purchase_costs = []
        self.sale_prices = []
        self.transport_costs = []
        self.create_widgets()

    def create_widgets(self):
        input_frame = ttk.LabelFrame(self.root, text="Input Parameters")
        input_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        ttk.Label(input_frame, text="Number of Suppliers:").grid(row=0, column=0, padx=5, pady=5)
        self.suppliers_entry = ttk.Entry(input_frame, width=5)
        self.suppliers_entry.insert(0, "2")
        self.suppliers_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(input_frame, text="Number of Receivers:").grid(row=1, column=0, padx=5, pady=5)
        self.receivers_entry = ttk.Entry(input_frame, width=5)
        self.receivers_entry.insert(0, "3")
        self.receivers_entry.grid(row=1, column=1, padx=5, pady=5)

        ttk.Button(input_frame, text="Update Table", command=self.update_input_tables).grid(row=2, column=0, columnspan=2, pady=10)

        self.tables_frame = ttk.LabelFrame(self.root, text="Input Data")
        self.tables_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        self.results_frame = ttk.LabelFrame(self.root, text="Results")
        self.results_frame.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")

        self.results_text = tk.Text(self.results_frame, height=20, width=80)
        self.results_text.grid(row=0, column=0, padx=5, pady=5)
        self.results_text.config(state='disabled')

        ttk.Button(self.root, text="Solve", command=self.solve).grid(row=3, column=0, pady=10)

        self.update_input_tables()

    @profile
    def update_input_tables(self):
        try:
            self.suppliers = int(self.suppliers_entry.get())
            self.receivers = int(self.receivers_entry.get())
            if self.suppliers < 1 or self.receivers < 1:
                raise ValueError("Number of suppliers and receivers must be positive.")
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid input: {e}")
            return

        for widget in self.tables_frame.winfo_children():
            widget.destroy()

        ttk.Label(self.tables_frame, text="Supply:").grid(row=0, column=0, padx=5, pady=5)
        self.supply_entries = []
        for i in range(self.suppliers):
            ttk.Label(self.tables_frame, text=f"D{i+1}").grid(row=0, column=i+1, padx=5, pady=5)
            entry = ttk.Entry(self.tables_frame, width=5)
            entry.grid(row=1, column=i+1, padx=5, pady=5)
            entry.insert(0, "0")
            self.supply_entries.append(entry)

        ttk.Label(self.tables_frame, text="Purchase Costs:").grid(row=2, column=0, padx=5, pady=5)
        self.purchase_entries = []
        for i in range(self.suppliers):
            entry = ttk.Entry(self.tables_frame, width=5)
            entry.grid(row=3, column=i+1, padx=5, pady=5)
            entry.insert(0, "0")
            self.purchase_entries.append(entry)

        ttk.Label(self.tables_frame, text="Demand:").grid(row=4, column=0, padx=5, pady=5)
        self.demand_entries = []
        for j in range(self.receivers):
            ttk.Label(self.tables_frame, text=f"O{j+1}").grid(row=5, column=j+1, padx=5, pady=5)
            entry = ttk.Entry(self.tables_frame, width=5)
            entry.grid(row=6, column=j+1, padx=5, pady=5)
            entry.insert(0, "0")
            self.demand_entries.append(entry)

        ttk.Label(self.tables_frame, text="Sale Prices:").grid(row=7, column=0, padx=5, pady=5)
        self.sale_entries = []
        for j in range(self.receivers):
            entry = ttk.Entry(self.tables_frame, width=5)
            entry.grid(row=8, column=j+1, padx=5, pady=5)
            entry.insert(0, "0")
            self.sale_entries.append(entry)

        ttk.Label(self.tables_frame, text="Transport Costs:").grid(row=9, column=0, padx=5, pady=5)
        self.transport_entries = []
        for i in range(self.suppliers):
            ttk.Label(self.tables_frame, text=f"D{i+1}").grid(row=10+i, column=0, padx=5, pady=5)
            row_entries = []
            for j in range(self.receivers):
                if i == 0:
                    ttk.Label(self.tables_frame, text=f"O{j+1}").grid(row=9, column=j+1, padx=5, pady=5)
                entry = ttk.Entry(self.tables_frame, width=5)
                entry.grid(row=10+i, column=j+1, padx=5, pady=5)
                entry.insert(0, "0")
                row_entries.append(entry)
            self.transport_entries.append(row_entries)

    @profile
    def get_inputs(self):
        try:
            self.supply = [float(entry.get()) for entry in self.supply_entries]
            self.demand = [float(entry.get()) for entry in self.demand_entries]
            self.purchase_costs = [float(entry.get()) for entry in self.purchase_entries]
            self.sale_prices = [float(entry.get()) for entry in self.sale_entries]
            self.transport_costs = [[float(entry.get()) for entry in row] for row in self.transport_entries]
            if any(s <= 0 for s in self.supply) or any(d <= 0 for d in self.demand):
                raise ValueError("Supply and demand must be positive.")
            if any(c < 0 for c in self.purchase_costs) or any(p < 0 for p in self.sale_prices):
                raise ValueError("Costs and prices must be non-negative.")
            if any(c < 0 for row in self.transport_costs for c in row):
                raise ValueError("Transport costs must be non-negative.")
        except ValueError as e:
            print(f"Input Error: {e}")
            messagebox.showerror("Error", f"Invalid input: {e}")
            return False
        return True

    @profile
    def compute_unit_profits(self):
        profits = np.zeros((self.suppliers, self.receivers))
        for i in range(self.suppliers):
            for j in range(self.receivers):
                profits[i, j] = self.sale_prices[j] - (self.purchase_costs[i] + self.transport_costs[i][j])
        return profits

    @profile
    def balance_problem(self, profits):
        total_supply = sum(self.supply)
        total_demand = sum(self.demand)
        supply = self.supply.copy()
        demand = self.demand.copy()
        m, n = profits.shape
        if total_supply < total_demand:
            supply.append(total_demand - total_supply)
            profits = np.vstack([profits, np.zeros((1, n))])
            m += 1
        elif total_supply > total_demand:
            demand.append(total_supply - total_demand)
            profits = np.hstack([profits, np.zeros((m, 1))])
            n += 1
        return profits, supply, demand

    @profile
    def initial_solution(self, profits, supply, demand):
        m, n = profits.shape
        transport = np.zeros((m, n))
        supply_left = supply.copy()
        demand_left = demand.copy()
        while any(s > 0 for s in supply_left) and any(d > 0 for d in demand_left):
            max_profit = np.max(profits * (transport == 0), initial=-np.inf)
            if max_profit == -np.inf:
                break
            i, j = np.where((profits == max_profit) & (transport == 0))
            i, j = i[0], j[0]
            quantity = min(supply_left[i], demand_left[j])
            transport[i, j] = quantity
            supply_left[i] -= quantity
            demand_left[j] -= quantity
        return transport

    @profile
    def compute_potentials(self, profits, transport):
        m, n = transport.shape
        u = np.full(m, np.nan)
        v = np.full(n, np.nan)
        u[-1] = 0
        visited = set()
        stack = [(m-1, None)]
        while stack:
            i, j = stack.pop()
            if i is not None and np.isnan(u[i]):
                for j in range(n):
                    if transport[i, j] > 0 and np.isnan(v[j]):
                        v[j] = profits[i, j] - u[i]
                        stack.append((None, j))
                visited.add(i)
            elif j is not None and np.isnan(v[j]):
                for i in range(m):
                    if transport[i, j] > 0 and np.isnan(u[i]):
                        u[i] = profits[i, j] - v[j]
                        stack.append((i, None))
                visited.add(j)
        if np.isnan(u).any() or np.isnan(v).any():
            for i in range(m):
                for j in range(n):
                    if transport[i, j] == 0 and not np.isnan(u[i]) and not np.isnan(v[j]):
                        transport[i, j] = 1e-6
                        return self.compute_potentials(profits, transport)
        return u, v, transport

    @profile
    def compute_deltas(self, profits, transport, u, v):
        m, n = profits.shape
        deltas = np.zeros((m, n))
        for i in range(m):
            for j in range(n):
                if transport[i, j] == 0:
                    deltas[i, j] = profits[i, j] - u[i] - v[j]
        return deltas

    @profile
    def find_cycle(self, transport, start_i, start_j):
        m, n = transport.shape
        queue = deque([(start_i, start_j, True, [(start_i, start_j, True)])])
        visited = set()
        while queue:
            r, c, add, path = queue.popleft()
            state = (r, c, add)
            if state in visited:
                continue
            visited.add(state)
            if len(path) > 2 and path[0][0] == r and path[0][1] == c and len(path) % 2 == 0:
                return path
            if add:
                for c_next in range(n):
                    if transport[r, c_next] > 0 and c_next != c:
                        queue.append((r, c_next, False, path + [(r, c_next, False)]))
                for r_next in range(m):
                    if transport[r_next, c] > 0 and r_next != r:
                        queue.append((r_next, c, False, path + [(r_next, c, False)]))
            else:
                for c_next in range(n):
                    if (transport[r, c_next] == 0 or (r, c_next) == (start_i, start_j)) and c_next != c:
                        queue.append((r, c_next, True, path + [(r, c_next, True)]))
                for r_next in range(m):
                    if (transport[r_next, c] == 0 or (r_next, c) == (start_i, start_j)) and r_next != r:
                        queue.append((r_next, c, True, path + [(r_next, c, True)]))
        return None

    @profile
    def optimize_transport(self, profits, transport, supply, demand):
        iterations = []
        max_iterations = 100
        iteration = 0
        while iteration < max_iterations:
            u, v, transport = self.compute_potentials(profits, transport)
            deltas = self.compute_deltas(profits, transport, u, v)
            max_delta = np.max(deltas)
            if max_delta <= 1e-6:
                print("Optimization complete: No positive deltas.")
                break
            i, j = np.where(deltas == max_delta)
            i, j = i[0], j[0]
            cycle = self.find_cycle(transport, i, j)
            if not cycle:
                print("No improving cycle found. Terminating.")
                break
            amounts = []
            for idx, (r, c, add) in enumerate(cycle):
                if not add:
                    amounts.append(transport[r, c])
            theta = min(amounts)
            for r, c, add in cycle:
                transport[r, c] += theta if add else -theta
            transport[transport < 1e-6] = 0
            iterations.append(transport.copy())
            iteration += 1
        if iteration >= max_iterations:
            print("Warning: Maximum iterations reached.")
        return transport, iterations

    @profile
    def compute_financials(self, transport, profits):
        m, n = transport.shape
        purchase_cost = 0
        transport_cost = 0
        revenue = 0
        for i in range(min(m, len(self.supply))):
            for j in range(min(n, len(self.demand))):
                qty = transport[i, j]
                if qty > 0:
                    purchase_cost += qty * self.purchase_costs[i]
                    transport_cost += qty * self.transport_costs[i][j]
                    revenue += qty * self.sale_prices[j]
        profit = revenue - (purchase_cost + transport_cost)
        return purchase_cost, transport_cost, revenue, profit

    @profile
    def format_matrix(self, matrix, title, row_labels, col_labels):
        result = f"{title}:\n"
        header = "    " + " ".join(f"{lbl:>6}" for lbl in col_labels)
        result += header + "\n"
        for i, row in enumerate(matrix):
            row_str = f"{row_labels[i]:<4}" + " ".join(f"{x:>6.1f}" for x in row)
            result += row_str + "\n"
        return result

    @profile
    def update_results(self, output):
        print("Updating GUI with results:")
        print(output)
        self.results_text.config(state='normal')
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(tk.END, output)
        self.results_text.config(state='disabled')

    @profile
    def run_solver(self):
        try:
            if not self.get_inputs():
                output = "Error: Invalid inputs."
                print(output)
                self.root.after(0, lambda: self.update_results(output))
                return
            print("Starting solver...")
            profits = self.compute_unit_profits()
            profits, supply, demand = self.balance_problem(profits)
            transport = self.initial_solution(profits, supply, demand)
            transport, iterations = self.optimize_transport(profits, transport, supply, demand)
            purchase_cost, transport_cost, revenue, profit = self.compute_financials(transport, profits)
            output = ""
            row_labels = [f"D{i+1}" for i in range(len(self.supply))] + (["DF"] if sum(self.supply) < sum(self.demand) else [])
            col_labels = [f"O{j+1}" for j in range(len(self.demand))] + (["OF"] if sum(self.supply) > sum(self.demand) else [])
            output += self.format_matrix(profits, "Unit Profit Table", row_labels, col_labels)
            output += "\n"
            for idx, iter_transport in enumerate(iterations):
                output += self.format_matrix(iter_transport, f"Iteration {idx+1} Transport Plan", row_labels, col_labels)
                output += "\n"
            output += self.format_matrix(transport, "Optimal Transport Plan", row_labels, col_labels)
            output += f"\nTotal Purchase Cost: {purchase_cost:.2f}\n"
            output += f"Total Transport Cost: {transport_cost:.2f}\n"
            output += f"Total Revenue: {revenue:.2f}\n"
            output += f"Total Profit: {profit:.2f}\n"
            print("Solver completed. Results:")
            print(output)
            self.root.after(0, lambda: self.update_results(output))
        except Exception as e:
            error_msg = f"Solver Error: {str(e)}\n{traceback.format_exc()}"
            print(error_msg)
            self.root.after(0, lambda: self.update_results(error_msg))

    def solve(self):
        threading.Thread(target=self.run_solver, daemon=True).start()

if __name__ == "__main__":
    root = tk.Tk()
    app = IntermediaryProblemApp(root)
    root.mainloop()