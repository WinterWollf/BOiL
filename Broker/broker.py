import numpy as np
import pandas as pd

def find_cycle(basis, start):
    """
    Znajduje cykl w bazie z punktu startowego
    """
    from collections import defaultdict

    basis_plus = basis + [start]
    rows = defaultdict(list)
    columns = defaultdict(list)

    # Build row and column maps from basis cells
    for (i, j) in basis_plus:
        rows[i].append((i, j))
        columns[j].append((i, j))

    def dfs(path, visited, level=0):
        last = path[-1]
        row_idx, col_idx = last

        # Completed cycle
        if len(path) >= 4 and last == start and level % 2 == 0:
            return path

        # Choose neighbors in the row or column, alternating
        neighbors = rows[row_idx] if level % 2 == 0 else columns[col_idx]

        for (i, j) in neighbors:
            if (i, j) == start and len(path) >= 4:
                return path
            if (i, j) not in visited:
                new_path = dfs(path + [(i, j)], visited | {(i, j)}, level + 1)
                if new_path:
                    return new_path
        return None

    return dfs([start], {start})



def ZZT(supply, demand, purchase_cost, sell_price, unit_transport_costs, supplier_contracts, seller_contracts):
    # --- Obliczanie zysku jednostkowego ---
    detailed_revenue = sell_price - purchase_cost[:, np.newaxis] - unit_transport_costs
    original_rows, original_cols = detailed_revenue.shape

    if supply.sum() != demand.sum():
        seller_contracts = np.append(seller_contracts, 0)
        supplier_contracts = np.append(supplier_contracts, 0)
        
        total_supply = supply.sum()
        total_demand = demand.sum()
        new_z = np.zeros((detailed_revenue.shape[0] + 1, detailed_revenue.shape[1] + 1))
        new_z[:-1, :-1] = detailed_revenue
        detailed_revenue = new_z
        supply = np.append(supply, total_demand)
        demand = np.append(demand, total_supply)

        purchase_cost = np.append(purchase_cost, 0)
        sell_price = np.append(sell_price, 0)
        unit_transport_costs = np.pad(unit_transport_costs, ((0,1), (0,1)), constant_values=0)

        block_val = np.max(unit_transport_costs) * 100000

        detailed_revenue[-1, :] += -block_val * seller_contracts
        unit_transport_costs[-1, :] += block_val * seller_contracts

        detailed_revenue[:, -1] += -block_val * supplier_contracts
        unit_transport_costs[:, -1] += block_val * supplier_contracts


    # --- Pierwsza propozycja planu dostaw ---
    # Kopia zysków, w celu poprawnego sortowania
    dt_rev_copy = detailed_revenue.copy()
    max_value = np.max(dt_rev_copy) + 1
    dt_rev_copy[-1, :] = -max_value
    dt_rev_copy[:-1, -1] = -max_value

    optimal_plan = np.full_like(detailed_revenue, fill_value=np.nan)
    supply_left = supply.copy()
    demand_left = demand.copy()
    flat_indices = np.argsort(dt_rev_copy.ravel())[::-1]
    sorted_indices = np.array(np.unravel_index(flat_indices, dt_rev_copy.shape)).T

    for i, j in sorted_indices:
        if supply_left[i] > 0 and demand_left[j] > 0:
            qty = min(supply_left[i], demand_left[j])
            optimal_plan[i, j] = qty
            supply_left[i] -= qty
            demand_left[j] -= qty

    optimal_plan[optimal_plan < 0] = np.nan

    # --- Sprawdzenie poprawności wyniku i optymalizacja ---
    delta_results = []
    max_delta = 0
    while True:
        alpha = [None] * detailed_revenue.shape[0]
        beta = [None] * detailed_revenue.shape[1]
        alpha[-1] = 0

        while True:
            changed = False
            for i in range(detailed_revenue.shape[0]):
                for j in range(detailed_revenue.shape[1]):
                    if not np.isnan(optimal_plan[i, j]):
                        if alpha[i] is not None and beta[j] is None:
                            beta[j] = detailed_revenue[i, j] - alpha[i]
                            changed = True
                        elif alpha[i] is None and beta[j] is not None:
                            alpha[i] = detailed_revenue[i, j] - beta[j]
                            changed = True
            if not changed:
                break

        delta_results = []
        for i in range(detailed_revenue.shape[0]):
            for j in range(detailed_revenue.shape[1]):
                if np.isnan(optimal_plan[i, j]) and alpha[i] is not None and beta[j] is not None:
                    delta = detailed_revenue[i, j] - alpha[i] - beta[j]
                    delta_results.append((i, j, delta))

        max_delta = max(delta_results, key=lambda x: x[2])
        
        # --- Optymalizacja wyniku ---
        if max_delta[2] > 0:
            cycle = find_cycle(list(zip(*np.where(~np.isnan(optimal_plan)))), max_delta[:2])
            if cycle is None:
                raise ValueError("Nie można znaleźć cyklu.")

            min_qty = min(optimal_plan[i, j] for i, j in cycle[1::2])
            for i, j in cycle[1::2]:
                if np.isnan(optimal_plan[i, j]):
                    optimal_plan[i, j] = 0
                optimal_plan[i, j] -= min_qty
                if optimal_plan[i, j] == 0:
                    optimal_plan[i, j] = np.nan
            for i, j in cycle[::2]:
                if np.isnan(optimal_plan[i, j]):
                    optimal_plan[i, j] = 0
                optimal_plan[i, j] += min_qty
                if optimal_plan[i, j] == 0:
                    optimal_plan[i, j] = np.nan
        else:
            break


    # --- Obliczanie całkowitego zysku i kosztów ---
    total_profit = 0
    transport_cost_total = 0
    purchase_cost_total = 0
    revenue_total = 0

    for i in range(detailed_revenue.shape[0]):
        for j in range(detailed_revenue.shape[1]):
            if not np.isnan(optimal_plan[i, j]):
                qty = optimal_plan[i, j]
                total_profit += detailed_revenue[i, j] * qty
                if i < original_rows and j < original_cols:
                    purchase_cost_total += purchase_cost[i] * qty
                if i < original_rows and j < original_cols:
                    revenue_total += sell_price[j] * qty
                if i < original_rows and j < original_cols:
                    transport_cost_total += unit_transport_costs[i][j] * qty


    # --- Przygotowanie wyników do wyświetlenia ---
    row_labels = [f"D{i+1}" if i < original_rows else "DF" for i in range(detailed_revenue.shape[0])]
    col_labels = [f"O{j+1}" if j < original_cols else "OF" for j in range(detailed_revenue.shape[1])]
    plan_df = pd.DataFrame(optimal_plan, index=row_labels, columns=col_labels).fillna("-").replace(0, "-")
    z_df = pd.DataFrame(detailed_revenue, index=row_labels, columns=col_labels).astype(object)
    z_df.loc[row_labels[-1], seller_contracts == 1] = "-M"
    z_df.loc[supplier_contracts == 1, col_labels[-1]] = "-M"

    delta_readable = [f"{row_labels[i]} -> {col_labels[j]} Δ = {delta:.2f}" for i, j, delta in delta_results]

    has_similar_alt_solution=max_delta[2] == 0

    return (
        plan_df,
        total_profit,
        z_df,
        delta_readable,
        revenue_total,
        purchase_cost_total,
        transport_cost_total,
        has_similar_alt_solution
    )
