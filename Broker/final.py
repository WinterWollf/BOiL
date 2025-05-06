import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
import pandas as pd

def rozwiaz_zzt(supply, demand, purchase_cost, sell_price, unit_transport_costs):
    z = sell_price - purchase_cost[:, np.newaxis] - unit_transport_costs
    original_rows, original_cols = z.shape

    dummy_supplier = False
    dummy_receiver = False

    if supply.sum() != demand.sum():
        total_supply = supply.sum()
        total_demand = demand.sum()
        new_z = np.zeros((z.shape[0] + 1, z.shape[1] + 1))
        new_z[:-1, :-1] = z
        z = new_z
        supply = np.append(supply, total_demand)
        demand = np.append(demand, total_supply)

        purchase_cost = np.append(purchase_cost, 0)
        sell_price = np.append(sell_price, 0)
        unit_transport_costs = np.pad(unit_transport_costs, ((0,1), (0,1)), constant_values=0)

        dummy_supplier = True
        dummy_receiver = True

    plan = np.full_like(z, fill_value=np.nan)
    supply_left = supply.copy()
    demand_left = demand.copy()
    flat_indices = np.argsort(z.ravel())[::-1]
    sorted_indices = np.array(np.unravel_index(flat_indices, z.shape)).T

    for i, j in sorted_indices:
        if supply_left[i] > 0 and demand_left[j] > 0:
            qty = min(supply_left[i], demand_left[j])
            plan[i, j] = qty
            supply_left[i] -= qty
            demand_left[j] -= qty

    plan[plan < 0] = np.nan

    # Zysk całkowity przez z[i,j]
    total_profit = 0
    transport_cost_total = 0
    purchase_cost_total = 0
    total_revenue = 0

    for i in range(z.shape[0]):
        for j in range(z.shape[1]):
            if not np.isnan(plan[i, j]):
                qty = plan[i, j]
                total_profit += z[i, j] * qty
                # rzeczywisty koszt zakupu tylko, jeśli towar NIE idzie do fikcyjnego odbiorcy
                if i < original_rows and j < original_cols:
                    purchase_cost_total += purchase_cost[i] * qty

                # rzeczywisty przychód tylko, jeśli towar NIE pochodzi od fikcyjnego dostawcy
                if i < original_rows and j < original_cols:
                    total_revenue += sell_price[j] * qty

                # koszt transportu tylko dla rzeczywistych tras
                if i < original_rows and j < original_cols:
                    transport_cost_total += unit_transport_costs[i][j] * qty


    # Obliczanie ∆ij
    u = [None] * z.shape[0]
    v = [None] * z.shape[1]
    u[0] = 0

    while True:
        changed = False
        for i in range(z.shape[0]):
            for j in range(z.shape[1]):
                if not np.isnan(plan[i, j]):
                    if u[i] is not None and v[j] is None:
                        v[j] = z[i, j] - u[i]
                        changed = True
                    elif u[i] is None and v[j] is not None:
                        u[i] = z[i, j] - v[j]
                        changed = True
        if not changed:
            break

    delta_results = []
    for i in range(z.shape[0]):
        for j in range(z.shape[1]):
            if np.isnan(plan[i, j]) and u[i] is not None and v[j] is not None:
                delta = z[i, j] - u[i] - v[j]
                delta_results.append((i, j, delta))

    row_labels = [f"D{i+1}" if i < original_rows else "DF" for i in range(z.shape[0])]
    col_labels = [f"O{j+1}" if j < original_cols else "OF" for j in range(z.shape[1])]
    plan_df = pd.DataFrame(plan, index=row_labels, columns=col_labels).fillna("-")
    z_df = pd.DataFrame(z, index=row_labels, columns=col_labels)

    delta_readable = [f"{row_labels[i]} -> {col_labels[j]} Δ = {delta:.2f}" for i, j, delta in delta_results]

    return (
        plan_df,
        total_profit,
        z_df,
        delta_readable,
        total_revenue,
        purchase_cost_total,
        transport_cost_total
    )

class IntermediaryProblemApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Brocker Problem Solver")
        self.suppliers = 2
        self.receivers = 3
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

        self.results_text = tk.Text(self.results_frame, height=15, width=60)
        self.results_text.grid(row=0, column=0, padx=5, pady=5)
        self.results_text.config(state='disabled')

        ttk.Button(self.root, text="Solve", command=self.solve_problem).grid(row=3, column=0, pady=10)

        self.update_input_tables()

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

    def get_inputs(self):
        try:
            supply = np.array([float(entry.get()) for entry in self.supply_entries])
            demand = np.array([float(entry.get()) for entry in self.demand_entries])
            purchase_cost = np.array([float(entry.get()) for entry in self.purchase_entries])
            sale_price = np.array([float(entry.get()) for entry in self.sale_entries])
            transport_costs = np.array([[float(entry.get()) for entry in row] for row in self.transport_entries])

            if any(s <= 0 for s in supply) or any(d <= 0 for d in demand):
                raise ValueError("Supply and demand must be positive.")
            if any(c < 0 for c in purchase_cost) or any(p < 0 for p in sale_price):
                raise ValueError("Costs and prices must be non-negative.")
            if any(c < 0 for row in transport_costs for c in row):
                raise ValueError("Transport costs must be non-negative.")
            return supply, demand, purchase_cost, sale_price, transport_costs
        except ValueError as e:
            messagebox.showerror("Input Error", str(e))
            return None

    def solve_problem(self):
        inputs = self.get_inputs()
        if inputs is None:
            return
        supply, demand, purchase_cost, sale_price, transport_costs = inputs
        plan_df, total_profit, z_df, delta_list, revenue, purchase_cost_sum, transport_cost_sum = rozwiaz_zzt(
            supply, demand, purchase_cost, sale_price, transport_costs)

        z_text = z_df.to_string()
        delta_text = "\n".join(delta_list)

        output = (
            f"Ostateczny plan przewozów:\n{plan_df.to_string(index=True)}\n\n"
            f"Tablica zysków jednostkowych (z):\n{z_text}\n\n"
            f"Wskaźniki optymalności Δij dla tras niebazowych:\n{delta_text}\n\n"
            f"PC: {revenue:.2f}\n"
            f"KZ: {purchase_cost_sum:.2f}\n"
            f"KT: {transport_cost_sum:.2f}\n"
            f"ZC: {total_profit:.2f}"
        )
        self.update_results(output)

    def update_results(self, output):
        self.results_text.config(state='normal')
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(tk.END, output)
        self.results_text.config(state='disabled')


if __name__ == "__main__":
    root = tk.Tk()
    app = IntermediaryProblemApp(root)
    root.mainloop()