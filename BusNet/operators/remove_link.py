from collections import defaultdict

from BusNet.operators.utils import weighted_choice
from BusNet.datas.demand_matrix import DEMAND

from BusNet.model.route import Route, assign_demand
from BusNet.model.individual import Individual

def compute_global_link_flows(assignment):
    link_flows = {}

    for info in assignment.values():
        demand = info["demand"]
        paths = info["paths"]

        for path in paths.values():
            for (u, v) in path:
                key = tuple(sorted((u, v)))  # bidirecional
                link_flows[key] = link_flows.get(key, 0.0) + demand

    return link_flows

# Aparentemente permitia gerar grafos desconexos
# def can_remove_link(routes, u, v):
#     # todos os nós antes
#     nodes_before = set(n for r in routes for n in r.nodes)
#
#     nodes_after = set()
#     for r in routes:
#         for i in range(len(r.nodes) - 1):
#             a, b = r.nodes[i], r.nodes[i+1]
#
#             if (a == u and b == v) or (a == v and b == u):
#                 continue  # simula remoção do link
#
#             nodes_after.add(a)
#             nodes_after.add(b)
#
#     return nodes_before.issubset(nodes_after)

# Agora aparentemente não gera mais grafos desconexos
def can_remove_link(routes, u, v):
    # nós antes (como você já fazia)
    nodes_before = set(n for r in routes for n in r.nodes)

    # constrói o grafo após a remoção do link
    graph = defaultdict(set)

    for r in routes:
        nodes = r.nodes
        for i in range(len(nodes) - 1):
            a, b = nodes[i], nodes[i+1]

            if (a == u and b == v) or (a == v and b == u):
                continue

            graph[a].add(b)
            graph[b].add(a)

    # 1️⃣ todos os nós continuam existindo
    if set(graph.keys()) != nodes_before:
        return False

    # 2️⃣ teste de conectividade (DFS)
    visited = set()
    stack = [next(iter(graph))]
    visited.add(stack[0])

    while stack:
        curr = stack.pop()
        for nxt in graph[curr]:
            if nxt not in visited:
                visited.add(nxt)
                stack.append(nxt)

    return visited == set(graph.keys())

def remove_link_from_route(route, u, v, min_nodes=2):
    nodes = route.nodes
    segments = []
    start = 0

    for i in range(len(nodes) - 1):
        a, b = nodes[i], nodes[i+1]

        if (a == u and b == v) or (a == v and b == u):
            if i + 1 - start >= min_nodes:
                segments.append(Route(nodes[start:i+1]))
            start = i + 1

    if len(nodes) - start >= min_nodes:
        segments.append(Route(nodes[start:]))

    return segments

def remove_link(individual, demand=DEMAND):
    routes = individual.routes

    if individual.assignment is None:
        individual.assignment = assign_demand(routes, demand)

    assignment = individual.assignment

    #  dentificar links usados
    link_flows = compute_global_link_flows(assignment)
    if not link_flows:
        return None

    links = list(link_flows.keys())

    #  robabilidade inversa ao fluxo (paper)
    weights = [1.0 / link_flows[l] for l in links]

    link = weighted_choice(links, weights)
    if link is None:
        return None

    u, v = link

    #  teste de segurança
    if not can_remove_link(routes, u, v):
        return None  # aborta como no paper

    #  emoção efetiva
    new_routes = []
    for r in routes:
        new_routes.extend(remove_link_from_route(r, u, v))

    if not new_routes:
        return None

    return Individual(new_routes)
