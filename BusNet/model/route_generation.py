# import random
#
# def generate_first_route(graph, Pe):
#     nodes = list(graph.keys())
#
#     # 1. Primeiro nó: qualquer nó
#     first = random.choice(nodes)
#     route = [first]
#
#     # 2. Segundo nó: vizinho do primeiro
#     neighbors = list(graph[first])
#     second = random.choice(neighbors)
#     route.append(second)
#
#     # 3. Crescimento da rota
#     while True:
#         # Decide se termina
#         if random.random() < Pe:
#             break
#
#         # Decide se expande no início ou no fim
#         expand_front = random.choice([True, False])
#
#         if expand_front:
#             current = route[0]
#             opposite = route[-1]
#         else:
#             current = route[-1]
#             opposite = route[0]
#
#         # Conjunto de candidatos
#         candidates = set(graph[current])
#
#         # Remove nós já na rota (exceto possível fechamento)
#         free_candidates = [n for n in candidates if n not in route]
#
#         # Se rota ≥ 3, pode fechar circuito
#         if len(route) >= 3 and opposite in candidates:
#             free_candidates.append(opposite)
#
#         # Se não houver candidatos, termina
#         if not free_candidates:
#             break
#
#         next_node = random.choice(free_candidates)
#
#         # Fecha circuito
#         if next_node == opposite:
#             if expand_front:
#                 route.insert(0, next_node)
#             else:
#                 route.append(next_node)
#             break
#
#         # Expansão normal
#         if expand_front:
#             route.insert(0, next_node)
#         else:
#             route.append(next_node)
#
#     return route
#
# def generate_next_route(graph, routes, free_nodes, Pe=0.6):
#
#     rng = random.Random()
#
#     # =========================
#     # 1) Nós já usados em rotas existentes
#     # =========================
#     used_nodes = set()
#     for r in routes:
#         used_nodes.update(r)
#
#     # =========================
#     # 2) Escolher o primeiro nó
#     # free node conectado a alguma rota existente
#     # =========================
#     start_candidates = [
#         n for n in free_nodes
#         if any(v in used_nodes for v in graph[n])
#     ]
#
#     if not start_candidates:
#         raise ValueError("Não há free nodes conectados às rotas existentes.")
#
#     start = rng.choice(start_candidates)
#
#     # =========================
#     # 3) Escolher o segundo nó
#     # nó já usado que seja vizinho do primeiro
#     # =========================
#     second_candidates = [
#         v for v in graph[start]
#         if v in used_nodes
#     ]
#
#     if not second_candidates:
#         raise ValueError("Free node escolhido não conecta a nenhuma rota existente.")
#
#     second = rng.choice(second_candidates)
#
#     route = [start, second]
#
#     # =========================
#     # 4) Expansão da rota
#     # =========================
#     while True:
#
#         # decisão de terminar
#         if rng.random() < Pe:
#             break
#
#         # escolher ponta
#         grow_front = rng.random() < 0.5
#         current = route[0] if grow_front else route[-1]
#         opposite = route[-1] if grow_front else route[0]
#
#         neighbors = graph[current]
#
#         # candidatos = vizinhos que ainda não estão na rota
#         candidates = [
#             n for n in neighbors
#             if n not in route
#         ]
#
#         # possibilidade de fechar circuito
#         if len(route) >= 3 and opposite in neighbors:
#             # fechar circuito termina a rota imediatamente
#             if rng.random() < 0.5:
#                 if grow_front:
#                     route.insert(0, opposite)
#                 else:
#                     route.append(opposite)
#                 break
#
#         # se não há candidatos, não dá pra crescer
#         if not candidates:
#             break
#
#         chosen = rng.choice(candidates)
#
#         if grow_front:
#             route.insert(0, chosen)
#         else:
#             route.append(chosen)
#
#     return route

import random

def generate_first_route(graph, Pe):
    nodes = list(graph.keys())

    # 1) Primeiro nó
    first = random.choice(nodes)
    route = [first]

    # 2) Segundo nó (vizinho)
    second = random.choice(list(graph[first]))
    route.append(second)

    # 3) Crescimento
    while True:

        # decisão de terminar
        if random.random() < Pe:
            break

        grow_front = random.random() < 0.5
        current = route[0] if grow_front else route[-1]
        opposite = route[-1] if grow_front else route[0]

        candidates = [
            n for n in graph[current]
            if n not in route
        ]

        # possibilidade de fechar circuito
        if len(route) >= 3 and opposite in graph[current]:
            candidates.append(opposite)

        if not candidates:
            break

        chosen = random.choice(candidates)

        # fechamento de circuito
        if chosen == opposite:
            if grow_front:
                route.insert(0, chosen)
            else:
                route.append(chosen)
            break

        # expansão normal
        if grow_front:
            route.insert(0, chosen)
        else:
            route.append(chosen)

    return route

def generate_next_route(graph, routes, Pe):
    rng = random.Random()

    # nós usados
    used_nodes = set()
    for r in routes:
        used_nodes.update(r)

    # free nodes
    free_nodes = [n for n in graph if n not in used_nodes]

    # 1) primeiro nó: free node conectado a alguma rota
    start_candidates = [
        n for n in free_nodes
        if any(v in used_nodes for v in graph[n])
    ]

    if not start_candidates:
        raise ValueError("Não há free nodes conectados às rotas existentes.")

    start = rng.choice(start_candidates)

    # 2) segundo nó: nó de rota existente
    second_candidates = [
        v for v in graph[start]
        if v in used_nodes
    ]

    second = rng.choice(second_candidates)

    route = [start, second]

    # 3) crescimento
    while True:

        if rng.random() < Pe:
            break

        grow_front = rng.random() < 0.5
        current = route[0] if grow_front else route[-1]
        opposite = route[-1] if grow_front else route[0]

        candidates = [
            n for n in graph[current]
            if n not in route
        ]

        # opposite end sempre entra no choice set
        if opposite in graph[current]:
            candidates.append(opposite)

        if not candidates:
            break

        chosen = rng.choice(candidates)

        if chosen == opposite:
            if grow_front:
                route.insert(0, chosen)
            else:
                route.append(chosen)
            break

        if grow_front:
            route.insert(0, chosen)
        else:
            route.append(chosen)

    return route
