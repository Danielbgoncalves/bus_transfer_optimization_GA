from itertools import product
from BusNet.genetic_algorithm.run_ga import run_ga, choose_operator, redistribute_equal
from BusNet.model.route import build_adjacency
from BusNet.model.network import Network
from BusNet.model.individual import generate_population

from BusNet.datas.demand_matrix import DEMAND
from BusNet.datas.nodes import NODES
from BusNet.datas.links import LINKS
from BusNet.plots.visualize_graphs import plot_fitness_by_epochs, plot_parent_child_routes_with_offset2

import copy
import pandas as pd
import os

OPERATORS = {
    "route_merge": 0.1,
    "route_break": 0.2,
    "route_sprout": 0.1,
    "add_link": 0.2,
    "remove_link": 0.1,
    "route_crossover": 0.1,
    "transfer_location": 0.2
}

PARAMETROS = {
    'V': 40,      # "bus travel speed 40 km/h"
    'Cv': 55,     # "bus operating cost $55/h"
    'K': 50,      # "bus capacity 50 passengers/bus"
    'L': 1.2,     # "load factor 1.2" (Aceita superlotação/em pé)
    'yw': 17,     # "user waiting time value $17/h" (Usado na Eq. 5)
    'yv': 8.5,     #  "user in-vehicle time value $8.5/h"
    'h_min': 0.0
}

perc = [0.1, 0.2, 0.3, 0.4, 0.5]
exec_nb = list(range(1,21))
pe = [0.8]

csv_file = "csvs/sens_metrics_8.csv"
file_exists = os.path.isfile(csv_file)

for pend, p, op, exec in product(pe, perc, OPERATORS.keys(), exec_nb):

    new_distribution = redistribute_equal(OPERATORS, op, p)

    g = build_adjacency(LINKS)
    netw = Network(NODES, LINKS)

    print()
    print(f"==== Running, {op}, {p}, {pend} << {exec} >> ====")
    print()

    population = generate_population(10, g, Pe=pend)

    # for i, ind in enumerate(population):
    #     print(len(ind.routes), ind.evaluate_with_coordination(netw, DEMAND, PARAMETROS))

    initial_population = copy.deepcopy(population)

    final_pop, metrics = run_ga(
        population,
        netw,
        DEMAND,
        PARAMETROS,
        new_distribution,
        iterations=100
    )

    # print("<<<< Final Population >>>>")
    # for i, ind in enumerate(final_pop):
    #     print(len(ind.routes), ind.evaluate_with_coordination(netw, DEMAND, PARAMETROS))

    # salva UMA LINHA por iteração
    row = {
        "Execution Number": exec,
        "Population": len(population),
        "Terminating Probability": pend,
        "Selected Operator": op,
        "Percentage": p,
        "Metrics": metrics
    }

    df_row = pd.DataFrame([row])

    df_row.to_csv(
        csv_file,
        mode="a",
        header=not file_exists,
        index=False
    )

    file_exists = True

# # RODANDO NA MORAL tá com plot ligado, não rodar mt gerações senão pc derrete a memória
# g = build_adjacency(LINKS)
# netw = Network(NODES, LINKS)
# population = generate_population(10, g, Pe=0.6)
# final_pop, metrics = run_ga(population, netw, DEMAND, PARAMETROS, iterations=250)
#
# sens_metrics.append({
#     "Execution Number": exec,
#     "Population": len(population),
#     "Terminating Probability": pe,
#     #"Selected Operator": op,
#     #"Percentage": p,
#     "Metrics": metrics
# })
#
# plot_fitness_by_epochs(metrics)
# best = min(final_pop, key=lambda ind: ind.fitness)
# plot_parent_child_routes_with_offset2(best,
#         best,
#         NODES,
#         "Melhor indivíduo dentre as gerações",
#         title_parent="Melhor",
#         title_child="Melhor tb, o mesmo",
#         offset_scale=0.15)