import pandas as pd
import re
import numpy as np
import glob
import os

# ==========================================
# 1) LER TODOS OS CSVs
# ==========================================

path = "csvs/*.csv"  # ajuste se necessário
files = glob.glob(path)

dfs = []

for file in files:
    df = pd.read_csv(file)
    dfs.append(df)

df_all = pd.concat(dfs, ignore_index=True)

# ==========================================
# 2) EXTRAIR BEST FITNESS FINAL
# ==========================================

def extract_final_best(metrics_str):
    values = re.findall(
        r"'best_fitness': (?:np\.float64\()?([0-9\.]+)",
        metrics_str
    )
    if len(values) == 0:
        return np.nan
    return float(values[-1])

df_all["final_best"] = df_all["Metrics"].apply(extract_final_best)
df_all = df_all.dropna(subset=["final_best"])

# ==========================================
# 3) MELHOR Pe (global)
# ==========================================

pe_stats = (
    df_all.groupby("Terminating Probability")
    .agg(mean_cost=("final_best", "mean"),
         std_cost=("final_best", "std"))
    .reset_index()
)

best_pe_row = pe_stats.loc[pe_stats["mean_cost"].idxmin()]




print("\n==== MELHOR Pe ====")
print(best_pe_row)


# ==========================================
# 4) FILTRAR SÓ O MELHOR Pe
# ==========================================

best_pe = float(best_pe_row["Terminating Probability"])

df_all["Terminating Probability"] = df_all["Terminating Probability"].astype(float)

df_best_pe = df_all.loc[
    np.isclose(df_all["Terminating Probability"].values, best_pe)
]
# ==========================================
# 5) MELHOR Percentage POR OPERADOR
# ==========================================

operator_stats = (
    df_best_pe.groupby(["Selected Operator", "Percentage"])
    .agg(mean_cost=("final_best", "mean"),
         std_cost=("final_best", "std"))
    .reset_index()
)

best_per_operator = (
    operator_stats.loc[
        operator_stats.groupby("Selected Operator")["mean_cost"].idxmin()
    ]
)

print("\n==== MELHOR PERCENTAGE POR OPERADOR ====")
print(best_per_operator.sort_values("Selected Operator"))
