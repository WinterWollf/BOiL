from tkinter import ttk, messagebox
import numpy as np
import tkinter as tk
from Broker.broker import ZZT


class IntermediaryProblemApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Broker Problem Solver")
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

        ttk.Label(self.tables_frame, text="Contract Options:").grid(row=10+self.suppliers, column=0, padx=5, pady=5)
        self.contract_var = tk.StringVar(value="None")
        contract_options = ["None"] + [f"D{i+1}" for i in range(self.suppliers)] + [f"O{j+1}" for j in range(self.receivers)]
        self.contract_menu = ttk.OptionMenu(self.tables_frame, self.contract_var, *contract_options)
        self.contract_menu.grid(row=10+self.suppliers, column=1, columnspan=self.receivers, padx=5, pady=5)

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

            selected_contract = self.contract_var.get()
            supplier_contracts = np.zeros(len(supply), dtype=int)
            receiver_contracts = np.zeros(len(demand), dtype=int)

            if selected_contract.startswith("D"):
                supplier_index = int(selected_contract.split("D")[1]) - 1
                supplier_contracts[supplier_index] = 1
            elif selected_contract.startswith("O"):
                receiver_index = int(selected_contract.split("O")[1]) - 1
                receiver_contracts[receiver_index] = 1

            return supply, demand, purchase_cost, sale_price, transport_costs, supplier_contracts, receiver_contracts
        except ValueError as e:
            messagebox.showerror("Input Error", str(e))
            return None

    def solve_problem(self):
        inputs = self.get_inputs()
        if inputs is None:
            return
        supply, demand, purchase_cost, sale_price, transport_costs, supplier_contracts, receiver_contracts = inputs
        plan_df, total_profit, z_df, delta_list, revenue, purchase_cost_sum, transport_cost_sum, has_alt_plans = ZZT(
            supply, demand, purchase_cost, sale_price, transport_costs, supplier_contracts, receiver_contracts)

        z_text = z_df.to_string()
        delta_text = "\n".join(delta_list)

        output = (
            f"Ostateczny plan przewozów:\n{plan_df.to_string(index=True)}\n\n"
            f"Tablica zysków jednostkowych (z):\n{z_text}\n\n"
            f"Wskaźniki optymalności Δij dla tras niebazowych:\n{delta_text}\n\n"
            f"PC: {revenue:.2f}\n"
            f"KZ: {purchase_cost_sum:.2f}\n"
            f"KT: {transport_cost_sum:.2f}\n"
            f"ZC: {total_profit:.2f}\n\n",
            f"Czy istnieją alternatywne plany dostaw: {'Tak' if has_alt_plans else 'Nie'}"
        )
        self.update_results(output)

    def update_results(self, output):
        self.results_text.config(state='normal')
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(tk.END, output)
        self.results_text.config(state='disabled')
