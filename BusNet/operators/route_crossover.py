import random

from BusNet.model.route import Route
from BusNet.model.individual import Individual

# Encontrar a parte das rotas que sofrem ovelap
# é importante porque se for 1 pivô é o caso normal
# senão é o caso especial de overlap por segmento q é tratado separado
def find_overlap_segment(route1, route2):
    """
    Retorna o maior segmento comum consecutivo entre duas rotas.
    Se não houver, retorna [].
    """

    r1 = route1.nodes
    r2 = route2.nodes

    best = []

    for i in range(len(r1)):
        for j in range(len(r2)):
            if r1[i] != r2[j]:
                continue

            # tenta expandir
            k = 0
            current = []

            while (i + k < len(r1) and
                   j + k < len(r2) and
                   r1[i + k] == r2[j + k]):
                current.append(r1[i + k])
                k += 1

            if len(current) > len(best):
                best = current

    return best

def split_route_by_overlap(route, overlap):
    """
    Dada uma rota e um overlap consecutivo,
    retorna (prefix, overlap, suffix)
    """
    nodes = route.nodes
    k = len(overlap)

    for i in range(len(nodes) - k + 1):
        if nodes[i:i+k] == overlap:
            prefix = nodes[:i]
            suffix = nodes[i+k:]
            return prefix, overlap, suffix

    raise ValueError("Overlap não encontrado na rota (erro lógico)")

def crossover_partial_overlap(route1, route2, overlap):
    """
    Aplica o crossover de overlap parcial (Fig. 10).
    Retorna duas novas rotas ou None se inválido.
    """

    P1, O, S1 = split_route_by_overlap(route1, overlap)
    P2, _, S2 = split_route_by_overlap(route2, overlap)

    # nova combinação ÚNICA permitida
    new_r1 = P1 + O + S2
    new_r2 = P2 + O + S1

    # validação mínima: precisa ser chain ou loop
    if len(new_r1) < 2 or len(new_r2) < 2:
        return None

    return new_r1, new_r2

def compute_overlap_transfer_gain(route, overlap, demand_matrix):
    """
    Ganho de demanda para crossover com overlap parcial.
    """

    nodes = route.nodes
    k = len(overlap)

    # encontra posição do overlap
    for i in range(len(nodes) - k + 1):
        if nodes[i:i+k] == overlap:
            start = i
            end = i + k - 1
            break
    else:
        return 0.0

    gain = 0.0

    for a in range(len(nodes)):
        for b in range(len(nodes)):
            if a == b:
                continue

            # não pode iniciar ou terminar dentro do overlap
            if start <= a <= end or start <= b <= end:
                continue

            # precisa atravessar o overlap inteiro
            if (a < start and b > end) or (a > end and b < start):
                i = nodes[a]
                j = nodes[b]
                gain += demand_matrix[i - 1][j - 1]

    return gain

def path_passes_through_pivot(route_nodes, i, j, pivot):  # Eu acho q isso aqui n era necessário mas vamos ver => é ss
    idx_i = route_nodes.index(i)
    idx_j = route_nodes.index(j)
    idx_p = route_nodes.index(pivot)

    # pivot precisa estar ENTRE i e j
    return (idx_i < idx_p < idx_j) or (idx_j < idx_p < idx_i)

def compute_route_transfer_gain(route, pivot, demand_matrix):
    """
    Calcula o 'potential transfer demand savings' de uma rota,
    conforme definido no paper (Route-Crossover Operator).
    Para decidir a prob da rota ser escolhida;
    precisamos saber o potencial de tranferencia de demanda dela.
    """

    nodes = route.nodes
    gain = 0.0

    # percorre todos os pares O-D possíveis na rota
    for a in range(len(nodes)):
        for b in range(len(nodes)):
            if a == b:
                continue

            i = nodes[a]
            j = nodes[b]

            # não pode começar ou terminar no pivot
            if i == pivot or j == pivot:
                continue

            # verifica se o caminho passa pelo pivot
            if not path_passes_through_pivot(nodes, i, j, pivot):
                continue

            # soma a demanda O-D
            gain += demand_matrix[i - 1][j - 1]

    return gain

def split_route_at_pivot(route, pivot):
    """
    Divide uma rota em duas partes no pivot.
    Retorna (left, right), ambos incluindo o pivot.

    É necessário já que o crossover consiste em separar
    duas rotas e junta-las, uma com parte de outra.
    """
    nodes = route.nodes

    if pivot not in nodes:
        raise ValueError("Pivot não pertence à rota, erro lógico!")

    idx = nodes.index(pivot)

    left  = nodes[:idx + 1]
    right = nodes[idx:]

    return left, right

def is_terminal(route, node):
    return route.start() == node or route.end() == node

def valid_pivots(route1, route2):
    """
    Retorna lista de nós que podem ser usados como pivot
    entre route1 e route2.
    """
    common = set(route1.nodes).intersection(route2.nodes)
    pivots = []

    for p in common:
        if not (is_terminal(route1, p) and is_terminal(route2, p)):
            pivots.append(p)

    return pivots

def find_crossover_candidates(routes, main_idx):
    """
    Para uma rota principal, encontra todos os pares:
    (idx_da_outra_rota, pivot)
    que são elegíveis para crossover.
    """
    main_route = routes[main_idx]
    candidates = []

    for j, other in enumerate(routes):
        if j == main_idx:
            continue

        pivots = valid_pivots(main_route, other)
        for p in pivots:
            candidates.append((j, p))

    return candidates

def generate_crossover_routes(route1, route2, pivot):
    """
    Gera as rotas candidatas do crossover entre route1 e route2
    usando pivot.
    Retorna lista de listas de nós.
    """

    r1_left, r1_right = split_route_at_pivot(route1, pivot)
    r2_left, r2_right = split_route_at_pivot(route2, pivot)

    candidates = []

    # Combinação 1: r1_left + r2_right
    cand1 = r1_left[:-1] + r2_right
    candidates.append(cand1)

    # Combinação 2: r2_left[:-1] + r1_right
    cand2 = r2_left[:-1] + r1_right
    candidates.append(cand2)

    return candidates

def route_crossover(individuo, demand_matrix):
    """
    Implementa fielmente o Route-Crossover Operator do paper.
    """
    routes = individuo.routes

    if len(routes) <= 1:
        return None  # paper: abort

    # 1) escolhe rota principal
    idx_main = random.randrange(len(routes))
    main_route = routes[idx_main]

    crossover_options = []

    # 2) percorre todas as outras rotas
    for j, other_route in enumerate(routes):
        if j == idx_main:
            continue

        overlap = find_overlap_segment(main_route, other_route)

        if not overlap:
            continue

        # =====================================================
        # CASO 1 — PIVÔ SIMPLES
        # =====================================================
        if len(overlap) == 1:
            pivot = overlap[0]

            # ignora terminal-terminal
            if is_terminal(main_route, pivot) and is_terminal(other_route, pivot):
                continue

            # gera o PAR de rotas novas
            rA_nodes, rB_nodes = generate_crossover_routes(
                main_route, other_route, pivot
            )

            rA = Route(rA_nodes)
            rB = Route(rB_nodes)

            # ganho individual (como no paper)
            gA = compute_route_transfer_gain(rA, pivot, demand_matrix)
            gB = compute_route_transfer_gain(rB, pivot, demand_matrix)

            # rota A como opção (rota B é companheira)
            if gA > 0:
                crossover_options.append({
                    "route": rA,
                    "companion": rB,
                    "idx_main": idx_main,
                    "idx_other": j,
                    "gain": gA
                })


            # rota B como opção (rota A é companheira)
            if gB > 0:
                crossover_options.append({
                    "route": rB,
                    "companion": rA,
                    "idx_main": idx_main,
                    "idx_other": j,
                    "gain": gB
                })

        # =====================================================
        # CASO 2 — OVERLAP PARCIAL
        # =====================================================
        else:
            result = crossover_partial_overlap(
                main_route, other_route, overlap
            )

            if result is None:
                continue

            r1_nodes, r2_nodes = result
            r1 = Route(r1_nodes)
            r2 = Route(r2_nodes)

            g = compute_overlap_transfer_gain(
                r1, overlap, demand_matrix
            )

            # bidirecional
            g *= 2

            if g > 0:
                crossover_options.append({
                    "route": r1,
                    "companion": r2,
                    "idx_main": idx_main,
                    "idx_other": j,
                    "gain": g
                })

    # 3) nenhuma opção viável
    if not crossover_options:
        return None

    # 4) seleção probabilística (Fig. 9)
    weights = [opt["gain"] for opt in crossover_options]
    chosen = random.choices(crossover_options, weights=weights)[0]

    # 5) aplica o crossover (substitui AS DUAS rotas)
    new_routes = routes.copy()
    new_routes[chosen["idx_main"]] = chosen["route"]
    new_routes[chosen["idx_other"]] = chosen["companion"]

    ind = Individual(
        new_routes
    )

    return ind


