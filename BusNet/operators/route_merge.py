import random

from BusNet.operators.utils import weighted_choice
from BusNet.datas.demand_matrix import DEMAND

from BusNet.model.route import Route, routes_with_common_terminal, assign_demand
from BusNet.model.individual import Individual

def transfer_demand(route_i_idx, route_j_idx, assignment):
    td = 0.0

    target_pair = [route_i_idx, route_j_idx]
    reverse_pair = [route_j_idx, route_i_idx]

    for info in assignment.values():
        routes_used = info["routes"]

        # Considera tanto Ri -> Rj quanto Rj -> Ri
        if routes_used == target_pair or routes_used == reverse_pair:
            td += info["demand"]

    return td

def merge_routes(Ri, Rj):
    a = Ri.nodes
    b = Rj.nodes

    if a[-1] == b[0]:
        return Route(a + b[1:])
    if a[-1] == b[-1]:
        return Route(a + b[-2::-1])
    if a[0] == b[-1]:
        return Route(b + a[1:])
    if a[0] == b[0]:
        return Route(b[::-1] + a[1:])

    return None

def route_merge(individual, network, demand=DEMAND):
    routes = individual.routes

    if len(routes) < 2:
        return None

    # 1️⃣ escolhe Ri
    Ri = random.choice(routes)
    Ri_idx = routes.index(Ri)

    # 2️⃣ rotas candidatas
    candidates = routes_with_common_terminal(routes, Ri)
    if not candidates:
        return None

    # 3️⃣ pesos = demanda de transferência
    weights = []
    for Rj in candidates:
        Rj_idx = routes.index(Rj)
        individual.assignment = assign_demand(individual.routes, demand, network=network)
        td = transfer_demand(Ri_idx, Rj_idx, individual.assignment)
        weights.append(td)

    Rj = weighted_choice(candidates, weights)
    if Rj is None:
        return None

    # 4️⃣ merge
    new_route = merge_routes(Ri, Rj)
    if new_route is None:
        return None

    # 5️⃣ cria novo indivíduo
    new_routes = [
        r for r in routes
        if r not in (Ri, Rj)
    ]
    new_routes.append(new_route)

    return Individual(new_routes)


