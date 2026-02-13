from .utils import weighted_choice

from BusNet.model.route import Route
from BusNet.model.individual import Individual

def get_used_links(routes):
    used = set()
    for route in routes:
        nodes = route.nodes
        for i in range(len(nodes) - 1):
            u, v = nodes[i], nodes[i+1]
            used.add(tuple(sorted((u, v))))
    return used

def link_od_demand(u, v, demand_matrix):
    # bidirecional
    return demand_matrix[u-1][v-1] + demand_matrix[v-1][u-1]

def add_link(individual, network, demand_matrix):
    routes = individual.routes

    #  links já utilizados nas rotas atuais
    used_links = get_used_links(routes)

    #  links disponíveis na rede que ainda não estão em nenhuma rota
    candidate_links = []
    weights = []

    for (u, v) in network.links:
        link = tuple(sorted((u, v)))
        if link in used_links:
            continue

        w = link_od_demand(u, v, demand_matrix)
        if w > 0:
            candidate_links.append((u, v))
            weights.append(w)

    # nenhum link relevante encontrado
    if not candidate_links:
        return None

    #  escolha probabilística proporcional à demanda O-D
    chosen = weighted_choice(candidate_links, weights)
    if chosen is None:
        return None

    u, v = chosen

    # cria nova rota mínima (atalho)
    new_route = Route([u, v])

    # monta novo indivíduo
    new_routes = routes + [new_route]
    return Individual(new_routes)
