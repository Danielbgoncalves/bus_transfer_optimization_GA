from BusNet.operators.utils import weighted_choice
from BusNet.datas.demand_matrix import DEMAND

from BusNet.model.route import Route, compute_route_link_flows, assign_demand
from BusNet.model.individual import Individual

def compute_route_discrepancy(route_idx, route, assignment):
    link_flows = compute_route_link_flows(route_idx, assignment)

    if len(link_flows) < 2:
        return 0.0

    flows = sorted(link_flows.values())
    return flows[1] - flows[0]

def select_route_to_break(routes, assignment):
    weights = []

    for idx, route in enumerate(routes):
        w = compute_route_discrepancy(idx, route, assignment)
        weights.append(w)

    return weighted_choice(list(range(len(routes))), weights)

def select_break_links(route_idx, route, assignment, max_splits=2, min_gap=2):
    link_flows = compute_route_link_flows(route_idx, assignment)

    if len(link_flows) < 3:
        return []

    nodes = route.nodes

    # links internos
    internal_links = []
    for (u, v), flow in link_flows.items():
        if u != nodes[0] and v != nodes[-1]:
            internal_links.append(((u, v), flow, nodes.index(v)))

    if not internal_links:
        return []

    # ordena por fluxo
    internal_links.sort(key=lambda x: x[1])

    selected = []
    used_indices = []

    for (u, v), flow, idx in internal_links:
        if all(abs(idx - j) >= min_gap for j in used_indices):
            selected.append((u, v))
            used_indices.append(idx)

        if len(selected) == max_splits:
            break

    return selected



def break_route_by_links(route, break_links, min_nodes=3):
    nodes = route.nodes
    cut_indices = sorted(
        nodes.index(v) for (u, v) in break_links if v in nodes
    )

    segments = []
    start = 0

    for idx in cut_indices:
        if idx + 1 - start >= min_nodes:
            segments.append(Route(nodes[start:idx+1]))
        start = idx

    if len(nodes) - start >= min_nodes:
        segments.append(Route(nodes[start:]))

    return segments

def route_break(individual, demand):
    routes = individual.routes

    if individual.assignment is None:
        individual.assignment = assign_demand(routes, demand)

    # 1️⃣ escolhe rota
    r_idx = select_route_to_break(routes, individual.assignment)
    if r_idx is None:
        return None

    route = routes[r_idx]
    nodes = route.nodes

    # 2️⃣ fluxos por link
    link_flows = compute_route_link_flows(r_idx, individual.assignment)
    if not link_flows:
        return None

    # 3️⃣ link de menor fluxo
    (u, v), _ = min(link_flows.items(), key=lambda x: x[1])

    cut_u = nodes.index(u)
    cut_v = nodes.index(v)

    # 4️⃣ construir novas rotas
    new_routes = []

    # esquerda
    if cut_u + 1 >= 2:
        new_routes.append(Route(nodes[:cut_u + 1]))

    # rota central (link mínimo)
    new_routes.append(Route([u, v]))

    # direita
    if len(nodes) - cut_v >= 2:
        new_routes.append(Route(nodes[cut_v:]))

    # se não houve quebra real
    if len(new_routes) < 2:
        return None

    # 5️⃣ monta novo indivíduo
    final_routes = [
        r for i, r in enumerate(routes) if i != r_idx
    ] + new_routes

    return Individual(final_routes)
