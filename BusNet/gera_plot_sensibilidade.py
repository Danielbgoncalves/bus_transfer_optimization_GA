import pandas as pd
import re
import numpy as np
import matplotlib.pyplot as plt

# ===============================
# 1) Abrir CSV
# ===============================
df = pd.read_csv("csvs/sens_metrics_0.6.csv")

# ===============================
# 2) Extrair último best_fitness (robusto)
# ===============================
def extract_final_best(metrics_str):

    # pega tanto:
    # 'best_fitness': 12345.67
    # quanto:
    # 'best_fitness': np.float64(12345.67)

    values = re.findall(
        r"'best_fitness': (?:np\.float64\()?([0-9\.]+)",
        metrics_str
    )

    if len(values) == 0:
        return np.nan  # evita crash

    return float(values[-1])  # último = última iteração

df["final_best"] = df["Metrics"].apply(extract_final_best)

# Remove possíveis linhas problemáticas
df = df.dropna(subset=["final_best"])

# ===============================
# 3) Média das execuções
# ===============================
grouped = (
    df.groupby(["Selected Operator", "Percentage"])
      .agg(mean_best=("final_best", "mean"))
      .reset_index()
)
# ===============================
# 4) Plot
# ===============================

OPERATORS = {
    "route_merge": 0.1,
    "route_break": 0.2,
    "route_sprout": 0.1,
    "add_link": 0.2,
    "remove_link": 0.1,
    "route_crossover": 0.1,
    "transfer_location": 0.2
}

for operator_name in OPERATORS.keys():

    df_op = grouped[grouped["Selected Operator"] == operator_name]

    plt.figure()
    plt.plot(
        df_op["Percentage"],
        df_op["mean_best"],
        marker="o"
    )

    center = df_op["mean_best"].mean()

    y_min = center - 1500
    y_max = center + 1500

    plt.ylim(y_min, y_max)

    plt.xlabel("Probability of choosing the operator")
    plt.ylabel("Total System Cost ($/h)")
    plt.title(f"Sensitivity analysis for {operator_name} genetic operator")
    plt.grid(True)
    plt.show()


check = (
    df.groupby(["Selected Operator", "Percentage"])
      .size()
      .reset_index(name="count")
)

print(check)