from tkinter import ttk, messagebox
import numpy as np
import tkinter as tk
from Broker.broker import ZZT
import pandas as pd
from tkinter.filedialog import asksaveasfilename, askopenfilename


class IntermediaryProblemApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Broker Problem Solver")
        self.root.geometry("1000x700")
        self.root.minsize(1024, 768)

        window_width = 1024
        window_height = 768

        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()

        x_coordinate = (screen_width / 2) - (window_width / 2)
        y_coordinate = (screen_height / 2) - (window_height / 2)

        root.geometry(f"{window_width}x{window_height}+{int(x_coordinate)}+{int(y_coordinate)}")


        self.main_color = "#4076FF"
        self.text_color = "#000000"
        self.white = "#ffffff"

        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.root.configure(bg=self.main_color)

        self.style.configure("TFrame", background=self.main_color)
        self.style.configure("TLabel", background=self.main_color, foreground=self.text_color)
        self.style.configure("TLabelframe", background=self.main_color)
        self.style.configure("TLabelframe.Label", background=self.main_color, foreground="white", font=("Arial", 10, "bold"))

        self.style.configure("TEntry", fieldbackground=self.white, background=self.white)
        self.style.configure("Treeview", background=self.white, fieldbackground=self.white, foreground="black")

        self.style.configure("Accent.TButton",
                             background=self.main_color,
                             foreground="white",
                             font=("Arial", 10, "bold"))
        self.style.map("Accent.TButton",
                       background=[("active", "#3057c7")],
                       foreground=[("disabled", "#cccccc")])

        self.suppliers = 2
        self.receivers = 3

        self.create_widgets()

    def create_widgets(self):
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(0, weight=1)

        # Left
        left_frame = ttk.Frame(main_frame)
        left_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        left_frame.columnconfigure(0, weight=1)

        input_frame = ttk.LabelFrame(left_frame, text="Input Parameters")
        input_frame.pack(fill="x", pady=(0, 10))

        input_inner = tk.Frame(input_frame, bg=self.main_color)
        input_inner.pack(fill="both", expand=True)

        ttk.Label(input_inner, text="Number of Suppliers:", font=("Arial", 10, "bold")).grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.suppliers_entry = ttk.Entry(input_inner, width=5)
        self.suppliers_entry.insert(0, "2")
        self.suppliers_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(input_inner, text="Number of Receivers:", font=("Arial", 10, "bold")).grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.receivers_entry = ttk.Entry(input_inner, width=5)
        self.receivers_entry.insert(0, "3")
        self.receivers_entry.grid(row=1, column=1, padx=5, pady=5)

        ttk.Button(input_inner, text="Update Table", style="Accent.TButton", command=self.update_input_tables).grid(row=2, column=0, columnspan=2, pady=10)
        ttk.Button(input_inner, text="Load from Excel", style="Accent.TButton", command=self.load_from_excel).grid(row=3, column=0, columnspan=2, pady=10)

        self.tables_frame = ttk.LabelFrame(left_frame, text="Input Data")
        self.tables_frame.pack(fill="both", expand=True)

        self.tables_inner = tk.Frame(self.tables_frame, bg=self.white)
        self.tables_inner.pack(fill="both", expand=True)

        # Right
        right_frame = ttk.Frame(main_frame)
        right_frame.grid(row=0, column=1, sticky="nsew")
        right_frame.columnconfigure(0, weight=1)
        right_frame.rowconfigure(0, weight=1)

        self.results_frame = ttk.LabelFrame(right_frame, text="Results")
        self.results_frame.grid(row=0, column=0, sticky="nsew")
        self.results_frame.rowconfigure(0, weight=1)
        self.results_frame.columnconfigure(0, weight=1)

        self.results_text = tk.Text(self.results_frame, height=15, width=80, font=("Courier", 10),
                                    bg=self.white, fg=self.text_color)
        self.results_text.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")

        scrollbar = ttk.Scrollbar(self.results_frame, command=self.results_text.yview)
        scrollbar.grid(row=0, column=1, sticky='ns')
        self.results_text.config(yscrollcommand=scrollbar.set, state='disabled')

        button_frame = ttk.Frame(right_frame)
        button_frame.grid(row=1, column=0, pady=10)

        ttk.Button(button_frame, text="Solve", style="Accent.TButton", command=self.solve_problem).grid(row=0, column=0, padx=5)
        ttk.Button(button_frame, text="Save to Excel", style="Accent.TButton", command=self.save_to_excel).grid(row=0, column=1, padx=5)

        self.update_input_tables()

    def update_input_tables(self, supply=None, demand=None, purchase_cost=None, sale_price=None, transport_costs=None, contract=None):
        try:
            self.suppliers = len(supply) if supply else int(self.suppliers_entry.get())
            self.receivers = len(demand) if demand else int(self.receivers_entry.get())
            if self.suppliers < 1 or self.receivers < 1:
                raise ValueError("Number of suppliers and receivers must be positive.")
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid input: {e}")
            return

        for widget in self.tables_frame.winfo_children():
            widget.destroy()

        row_offset = 0

        # Supply
        ttk.Label(self.tables_frame, text="Supply:", style="Header.TLabel", font=("Arial", 10, "bold")).grid(row=row_offset, column=0, padx=5, pady=5)
        self.supply_entries = []
        for i in range(self.suppliers):
            ttk.Label(self.tables_frame, text=f"O{i+1}").grid(row=row_offset, column=i+1, padx=5, pady=5)
            entry = ttk.Entry(self.tables_frame, width=5)
            entry.grid(row=row_offset + 1, column=i+1, padx=5, pady=5)
            entry.insert(0, str(supply[i]) if supply else "0")
            self.supply_entries.append(entry)
        row_offset += 2

        ttk.Separator(self.tables_frame, orient='horizontal').grid(row=row_offset, column=0, columnspan=self.suppliers + 2, sticky="ew", pady=10)
        row_offset += 1

        # Purchase Costs
        ttk.Label(self.tables_frame, text="Purchase Costs:", style="Header.TLabel", font=("Arial", 10, "bold")).grid(row=row_offset, column=0, padx=5, pady=5)
        self.purchase_entries = []
        for i in range(self.suppliers):
            entry = ttk.Entry(self.tables_frame, width=5)
            entry.grid(row=row_offset + 1, column=i+1, padx=5, pady=5)
            entry.insert(0, str(purchase_cost[i]) if purchase_cost else "0")
            self.purchase_entries.append(entry)
        row_offset += 2

        ttk.Separator(self.tables_frame, orient='horizontal').grid(row=row_offset, column=0, columnspan=self.suppliers + 2, sticky="ew", pady=10)
        row_offset += 1

        # Demand
        ttk.Label(self.tables_frame, text="Demand:", style="Header.TLabel", font=("Arial", 10, "bold")).grid(row=row_offset, column=0, padx=5, pady=5)
        self.demand_entries = []
        for j in range(self.receivers):
            ttk.Label(self.tables_frame, text=f"D{j+1}").grid(row=row_offset, column=j+1, padx=5, pady=5)
            entry = ttk.Entry(self.tables_frame, width=5)
            entry.grid(row=row_offset + 1, column=j+1, padx=5, pady=5)
            entry.insert(0, str(demand[j]) if demand else "0")
            self.demand_entries.append(entry)
        row_offset += 2

        ttk.Separator(self.tables_frame, orient='horizontal').grid(row=row_offset, column=0, columnspan=self.receivers + 2, sticky="ew", pady=10)
        row_offset += 1

        # Sale Prices
        ttk.Label(self.tables_frame, text="Sale Prices:", style="Header.TLabel", font=("Arial", 10, "bold")).grid(row=row_offset, column=0, padx=5, pady=5)
        self.sale_entries = []
        for j in range(self.receivers):
            entry = ttk.Entry(self.tables_frame, width=5)
            entry.grid(row=row_offset + 1, column=j+1, padx=5, pady=5)
            entry.insert(0, str(sale_price[j]) if sale_price else "0")
            self.sale_entries.append(entry)
        row_offset += 2

        ttk.Separator(self.tables_frame, orient='horizontal').grid(row=row_offset, column=0, columnspan=self.receivers + 2, sticky="ew", pady=10)
        row_offset += 1

        # Transport Costs
        ttk.Label(self.tables_frame, text="Transport Costs:", style="Header.TLabel", font=("Arial", 10, "bold")).grid(row=row_offset, column=0, padx=5, pady=5)
        self.transport_entries = []
        for i in range(self.suppliers):
            ttk.Label(self.tables_frame, text=f"O{i+1}").grid(row=row_offset + i + 1, column=0, padx=5, pady=5)
            row_entries = []
            for j in range(self.receivers):
                if i == 0:
                    ttk.Label(self.tables_frame, text=f"D{j+1}").grid(row=row_offset, column=j+1, padx=5, pady=5)
                entry = ttk.Entry(self.tables_frame, width=5)
                entry.grid(row=row_offset + i + 1, column=j+1, padx=5, pady=5)
                value = str(transport_costs[i][j]) if transport_costs else "0"
                entry.insert(0, value)
                row_entries.append(entry)
            self.transport_entries.append(row_entries)
        row_offset += self.suppliers + 2

        ttk.Separator(self.tables_frame, orient='horizontal').grid(row=row_offset, column=0, columnspan=max(self.suppliers, self.receivers) + 2, sticky="ew", pady=10)
        row_offset += 1

        # Contract
        ttk.Label(self.tables_frame, text="Contract Options:", style="Header.TLabel", font=("Arial", 10, "bold")).grid(row=row_offset, column=0, padx=5, pady=5)
        self.contract_var = tk.StringVar(value=contract or "None")
        contract_options = ["None"] + [f"O{i+1}" for i in range(self.suppliers)] + [f"D{j+1}" for j in range(self.receivers)]
        self.contract_menu = ttk.OptionMenu(self.tables_frame, self.contract_var, self.contract_var.get(), *contract_options)
        self.contract_menu.grid(row=row_offset, column=1, columnspan=max(self.receivers, 1), padx=5, pady=5)

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

    def save_to_excel(self):
        inputs = self.get_inputs()
        if inputs is None:
            return
        supply, demand, purchase_cost, sale_price, transport_costs, supplier_contracts, receiver_contracts = inputs
        plan_df, total_profit, z_df, delta_list, revenue, purchase_cost_sum, transport_cost_sum, has_alt_plans = ZZT(
            supply, demand, purchase_cost, sale_price, transport_costs, supplier_contracts, receiver_contracts)


        file_path = asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")])
        if not file_path:
            return

        with pd.ExcelWriter(file_path) as writer:
            supply_df = pd.DataFrame({
                "Supplier": [f"O{i+1}" for i in range(len(supply))],
                "Supply": supply
            })
            supply_df.to_excel(writer, sheet_name="Supply", index=False)

            demand_df = pd.DataFrame({
                "Receiver": [f"D{j+1}" for j in range(len(demand))],
                "Demand": demand
            })
            demand_df.to_excel(writer, sheet_name="Demand", index=False)

            purchase_cost_df = pd.DataFrame({
                "Supplier": [f"O{i+1}" for i in range(len(purchase_cost))],
                "Purchase Cost": purchase_cost
            })
            purchase_cost_df.to_excel(writer, sheet_name="Purchase Costs", index=False)

            sale_price_df = pd.DataFrame({
                "Receiver": [f"D{j+1}" for j in range(len(sale_price))],
                "Sale Price": sale_price
            })
            sale_price_df.to_excel(writer, sheet_name="Sale Prices", index=False)

            transport_df = pd.DataFrame(transport_costs, columns=[f"O{j+1}" for j in range(len(demand))],
                                        index=[f"D{i+1}" for i in range(len(supply))])
            transport_df.to_excel(writer, sheet_name="Transport Costs")

            contract_df = pd.DataFrame({"Contract": [self.contract_var.get()]})
            contract_df.to_excel(writer, sheet_name="Contract", index=False)

            plan_df.to_excel(writer, sheet_name="Plan")
            z_df.to_excel(writer, sheet_name="Unit Profits (z)")
            split_delta = [d.replace(" ", "").split("=") for d in delta_list]
            delta_df = pd.DataFrame(split_delta, columns=["Δij", "Value"])
            delta_df["Value"] = pd.to_numeric(delta_df["Value"], errors="coerce")

            summary_data = {
                "Revenue (PC)": [revenue],
                "Purchase Cost (KZ)": [purchase_cost_sum],
                "Transport Cost (KT)": [transport_cost_sum],
                "Total Profit (ZC)": [total_profit],
                "Alternative Plans": ["Yes" if has_alt_plans else "No"]
            }
            summary_df = pd.DataFrame(summary_data)
            summary_df.to_excel(writer, sheet_name="Summary", index=False)

        messagebox.showinfo("Success", f"Data saved successfully to {file_path}")

    def load_from_excel(self):
        from tkinter.filedialog import askopenfilename
        from tkinter import messagebox

        file_path = askopenfilename(filetypes=[("Excel files", "*.xlsx")])
        if not file_path:
            return None

        try:
            # Load each sheet
            supply_df = pd.read_excel(file_path, sheet_name="Supply")
            demand_df = pd.read_excel(file_path, sheet_name="Demand")
            purchase_df = pd.read_excel(file_path, sheet_name="Purchase Costs")
            sale_df = pd.read_excel(file_path, sheet_name="Sale Prices")
            transport_df = pd.read_excel(file_path, sheet_name="Transport Costs", index_col=0)

            contract = None
            try:
                contract_df = pd.read_excel(file_path, sheet_name="Contract")
                if not contract_df.empty and "Contract" in contract_df.columns:
                    contract = str(contract_df["Contract"].iloc[0])
            except Exception as e:
                print(f"Error loading contract sheet: {e}")

            # Extract values
            supply = supply_df["Supply"].tolist()
            demand = demand_df["Demand"].tolist()
            purchase_cost = purchase_df["Purchase Cost"].tolist()
            sale_price = sale_df["Sale Price"].tolist()
            transport_costs = transport_df.values.tolist()

            # Currently not loaded from Excel; placeholder for consistency
            supplier_contracts = None
            receiver_contracts = None

            supply, demand, purchase_cost, sale_price, transport_costs, supplier_contracts, receiver_contracts
            self.update_input_tables(supply, demand, purchase_cost, sale_price, transport_costs, contract)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load Excel file:\n{e}")
            return None


    def update_results(self, output):
        self.results_text.config(state='normal')
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(tk.END, output)
        self.results_text.config(state='disabled')
