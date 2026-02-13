import random
from BusNet.model.route import Route
from BusNet.model.individual import Individual

def transfer_location(individual, network, demand_matrix):
    routes = individual.routes
    if len(routes) < 2: return None

    idx_main = random.randrange(len(routes))
    main_route = routes[idx_main]

    candidatos_intersecao = []
    for idx_r, r in enumerate(routes):
        if idx_r == idx_main: continue

        comuns = set(main_route.nodes) & set(r.nodes)
        for t_old in comuns:
            candidatos_intersecao.append({'idx_r': idx_r, 't_old': t_old})

    if not candidatos_intersecao:
      return None

    escolha = random.choice(candidatos_intersecao)

    r2 = routes[escolha['idx_r']]
    t_old = escolha['t_old']
    nos_r2 = r2.nodes
    idx_t_old = nos_r2.index(t_old)

    # CONECTIVIDADE
    vizinhos = []
    if idx_t_old > 0: vizinhos.append(nos_r2[idx_t_old - 1])
    if idx_t_old < len(nos_r2) - 1: vizinhos.append(nos_r2[idx_t_old + 1])

    validos = []
    for t_new in main_route.nodes:
        if t_new == t_old or t_new in nos_r2: continue

        # Checa se t_new se liga fisicamente aos vizinhos de t_old na R2
        if all((v, t_new) in network.length or (t_new, v) in network.length for v in vizinhos):
            validos.append(t_new)

    opcoes_peso = []
    for t_new in validos:
        ganho = 0
        for no_r2 in nos_r2:
            if no_r2 == t_old:
              continue

            ganho += demand_matrix[t_new-1][no_r2-1] + demand_matrix[no_r2-1][t_new-1]

        if ganho > 0:
            opcoes_peso.append({'t_new': t_new, 'ganho': ganho})

    if not opcoes_peso: return None

    t_new_final = random.choices(opcoes_peso, weights=[o['ganho'] for o in opcoes_peso])[0]['t_new']

    novos_nos = list(nos_r2)
    novos_nos[idx_t_old] = t_new_final

    novas_rotas = list(routes)
    novas_rotas[escolha['idx_r']] = Route(novos_nos)

    individual = Individual(novas_rotas)

    return individual
