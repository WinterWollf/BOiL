import numpy as np
import pandas as pd

def rozwiaz_zzt(supply, demand, purchase_cost, sell_price, unit_transport_costs):
    # Obliczamy zyski jednostkowe
    z = sell_price - purchase_cost[:, np.newaxis] - unit_transport_costs

    # Równoważenie problemu przez dodanie fikcyjnych podmiotów
    if supply.sum() != demand.sum():
        total_supply = supply.sum()
        total_demand = demand.sum()

        new_z = np.zeros((z.shape[0] + 1, z.shape[1] + 1))
        new_z[:-1, :-1] = z
        new_z[-1, :-1] = 0
        new_z[:-1, -1] = 0
        new_z[-1, -1] = 0
        z = new_z

        supply = np.append(supply, total_demand)
        demand = np.append(demand, total_supply)

    # Budujemy plan początkowy metodą największego zysku
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

    # Naprawa ewentualnych ujemnych wartości
    plan[plan < 0] = np.nan

    # Korekta: usuwamy przewozy z ujemnym zyskiem jeśli możliwe
    for i in range(plan.shape[0]):
        for j in range(plan.shape[1]):
            if not np.isnan(plan[i, j]) and z[i, j] < 0:
                # Szukamy trasy z zyskiem >= 0 u tego samego dostawcy
                for k in range(plan.shape[1]):
                    if np.isnan(plan[i, k]) and z[i, k] >= 0:
                        przenies = plan[i, j]
                        plan[i, j] = np.nan
                        plan[i, k] = przenies
                        break

    # Obliczenie końcowego zysku
    total_profit = 0
    for i in range(z.shape[0]):
        for j in range(z.shape[1]):
            if not np.isnan(plan[i, j]):
                total_profit += z[i, j] * plan[i, j]

    # Generowanie indeksów
    row_labels = [f"D{i+1}" for i in range(plan.shape[0]-1)] + ["DF"]
    col_labels = [f"O{j+1}" for j in range(plan.shape[1]-1)] + ["OF"]

    plan_df = pd.DataFrame(plan, index=row_labels, columns=col_labels)
    return plan_df.fillna("-"), total_profit

# Przykład użycia
if __name__ == "__main__":
    supply = np.array([20, 30])
    demand = np.array([10, 28, 27])
    purchase_cost = np.array([10, 12])
    sell_price = np.array([30, 25, 30])
    unit_transport_costs = np.array([[8, 14, 17], [12, 9, 19]])

    plan, profit = rozwiaz_zzt(supply, demand, purchase_cost, sell_price, unit_transport_costs)
    print("\nOstateczny plan przewozów:")
    print(plan.to_string())
    print(f"\nMaksymalny zysk pośrednika: {profit}")
