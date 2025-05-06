import numpy as np
import pandas as pd


def ZZT(supply, demand, purchase_cost, sell_price, unit_transport_costs):
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

    total_profit = 0
    transport_cost_total = 0
    purchase_cost_total = 0
    total_revenue = 0

    for i in range(z.shape[0]):
        for j in range(z.shape[1]):
            if not np.isnan(plan[i, j]):
                qty = plan[i, j]
                total_profit += z[i, j] * qty
                if i < original_rows and j < original_cols:
                    purchase_cost_total += purchase_cost[i] * qty
                if i < original_rows and j < original_cols:
                    total_revenue += sell_price[j] * qty
                if i < original_rows and j < original_cols:
                    transport_cost_total += unit_transport_costs[i][j] * qty

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
