import random

from BusNet.operators import *

from BusNet.datas.demand_matrix import DEMAND
from BusNet.datas.nodes import NODES
from BusNet.plots.visualize_graphs import plot_parent_child_routes_with_offset2
import copy

OPERATORS = {
    "route_merge": 0.1,
    "route_break": 0.2,
    "route_sprout": 0.1,
    "add_link": 0.2,
    "remove_link": 0.1,
    "route_crossover": 0.1,
    "transfer_location": 0.2
}

# Escolhe o operador com base na sua probabilidade
def choose_operator(operator_dict=OPERATORS):
    probs = list(operator_dict.values())
    ops = list(operator_dict.keys())

    return random.choices(ops, probs)[0]

# Aplica o operador
def apply_operator(parent, op_name, network, demand_matrix):
    if op_name == "route_merge":
        child = route_merge(parent, network, demand_matrix)
    elif op_name == "route_break":
        child = route_break(parent, demand_matrix)
    elif op_name == "route_sprout":
        child = route_sprout(parent, demand_matrix)
    elif op_name == "add_link":
        child = add_link(parent, network, demand_matrix)
    elif op_name == "remove_link":
        child = remove_link(parent)
    elif op_name == "route_crossover":
        child = route_crossover(parent, demand_matrix)
    elif op_name == "transfer_location":
        child = transfer_location(parent, network, DEMAND)

    return child

# Redistribui igualmente a probabilidade entre operadores dado que um tem probabilidade fixa (para testes)
def redistribute_equal(operators, chosen_op, p):
    new_ops = operators.copy()
    new_ops[chosen_op] = p

    others = [op for op in operators if op != chosen_op]
    share = (1 - p) / len(others)

    for op in others:
        new_ops[op] = share

    return new_ops

# Ciclo principal de evolução
def run_ga(population, network, demand_matrix, params, operators, iterations=250):
    for ind in population:
        if ind.fitness is None:
            ind.evaluate_with_coordination(network, demand_matrix, params)

    best = min(population, key=lambda ind: ind.fitness)

    a=0
    metrics = []
    for it in range(iterations):

        target = random.choice(population)

        # ≥ Usar 'operator_name' significa rodar apenas com esse operador
        # não é o que queremos em uma rodagem de vdd, é apenas TESTE

        operator_name = choose_operator(operators)

        new_ind = apply_operator(target, operator_name, network, demand_matrix)

        chances = 0
        while new_ind is None and chances < 10:
            operator_name = choose_operator(operators)
            new_ind = apply_operator(target, operator_name, network, demand_matrix)
            chances += 1

        if new_ind is None:
            continue
        a +=1
        # plot_parent_child_routes_with_offset2(
        #     target,
        #     new_ind,
        #     NODES,
        #     operator_name,
        #     title_parent="Pai",
        #     title_child="Filho",
        #     offset_scale=0.1
        # )

        new_ind.evaluate_with_coordination(network, demand_matrix, params)

        # Elitismo implicito
        worst = max(population, key=lambda ind: ind.fitness)

        if new_ind.fitness < worst.fitness:
            population.remove(worst)
            population.append(new_ind)

        # (opcional) log
        best = min(population, key=lambda ind: ind.fitness)
        # if it % 10 == 0:
        # print(f"Iter {it}: best fitness = {best.fitness}")

        metrics.append({
            "iteration": it,
            "operator": operator_name,
            "best_ind": copy.deepcopy(best),
            "best_fitness": best.fitness
        })
    print("Operador aplicado:", a)
    return population, metrics