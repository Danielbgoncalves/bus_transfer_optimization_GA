from BusNet.operators.utils import weighted_choice
from BusNet.datas.demand_matrix import DEMAND

from BusNet.model.route import Route, compute_route_link_flows, assign_demand
from BusNet.model.individual import Individual

def compute_critical_demand_difference(route_idx, assignment):
    link_flows = compute_route_link_flows(route_idx, assignment)

    if len(link_flows) < 2:
        return 0.0

    flows = sorted(link_flows.values(), reverse=True)
    return flows[0] - flows[1]

def select_route_for_sprout(routes, assignment):
    weights = []

    for idx, _ in enumerate(routes):
        w = compute_critical_demand_difference(idx, assignment)
        weights.append(w)

    return weighted_choice(list(range(len(routes))), weights)

def select_critical_link(route_idx, assignment):
    link_flows = compute_route_link_flows(route_idx, assignment)

    if not link_flows:
        return None

    return max(link_flows.items(), key=lambda x: x[1])[0]

def route_sprout(individual, demand=DEMAND):
    routes = individual.routes

    if individual.assignment is None:
        individual.assignment = assign_demand(routes, demand)

    #  escolhe rota
    r_idx = select_route_for_sprout(routes, individual.assignment)
    if r_idx is None:
        return None

    #  escolhe link crítico
    critical_link = select_critical_link(r_idx, individual.assignment)
    if critical_link is None:
        return None

    u, v = critical_link

    new_route = Route([u, v])

    #  evita duplicata
    for r in routes:
        if r.nodes == new_route.nodes:
            return None

    # novo indivíduo
    return Individual(routes + [new_route])