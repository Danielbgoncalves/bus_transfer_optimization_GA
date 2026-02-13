import numpy as np
import heapq
import math



class Route:
    def __init__(self, nodes):
        self.nodes = nodes

    def start(self):
      return self.nodes[0]

    def end(self):
      return self.nodes[-1]

    def length(self, network):
        d = 0.0
        for i in range(len(self.nodes) - 1):
            u = self.nodes[i]
            v = self.nodes[i + 1]
            d += network.length[(u, v)]
        return d

# === Funções de cálculo de rota ===

# retorna True se 2 rotas compartilham terminal
def share_terminal(r1, r2):
    return (
        r1.start() == r2.start() or
        r1.start() == r2.end() or
        r1.end() == r2.start() or
        r1.end() == r2.end()
    )

# Retorna uma lista de rotas que compartilham da rota Ri
def routes_with_common_terminal(routes, Ri):
    return [
        Rj for Rj in routes
        if Rj is not Ri and share_terminal(Ri, Rj)
    ]

# Auxiliar para tornar assig_demand operante para caminhos de ida E DE VOLTA
def extract_path(nodes, u, v):
    """
    Extrai o caminho entre u e v em uma rota bidirecional.
    Retorna lista de links (u,v). Se u == v, retorna [].
    """
    i = nodes.index(u)
    j = nodes.index(v)

    path = []

    if i < j:
        for p in range(i, j):
            path.append((nodes[p], nodes[p+1]))
    elif i > j:
        for p in range(i, j, -1):
            path.append((nodes[p], nodes[p-1]))

    return path

# ========= Calculo do assigment # =========

def build_route_network_graph(routes, network):
    """Constrói um grafo onde as arestas são os links cobertos pelas rotas."""
    adj = defaultdict(list)
    link_to_routes = defaultdict(list)

    for r_idx, route in enumerate(routes):
        nodes = route.nodes
        for i in range(len(nodes) - 1):
            u, v = nodes[i], nodes[i + 1]
            # Distância física do link
            dist = network.length.get((u, v), float('inf'))

            # Adiciona ao grafo (bidirecional)
            adj[u].append((v, dist))
            adj[v].append((u, dist))

            # Mapeia qual rota cobre este link
            link_to_routes[(u, v)].append(r_idx)
            link_to_routes[(v, u)].append(r_idx)

    return adj, link_to_routes


def dijkstra_shortest_path(start, end, adj):
    """Retorna (distancia, lista_de_nos) do caminho mais curto."""
    pq = [(0.0, start, [start])]
    visited = set()

    while pq:
        cost, u, path = heapq.heappop(pq)
        if u == end:
            return cost, path
        if u in visited:
            continue
        visited.add(u)

        for v, weight in adj[u]:
            if v not in visited:
                heapq.heappush(pq, (cost + weight, v, path + [v]))

    return float('inf'), []


def reconstruct_path_structure(path_nodes, link_to_routes):
    """
    Converte a lista de nós no formato de dicionário de rotas.
    Prioriza a continuidade da rota para evitar transferências desnecessárias.
    """
    if not path_nodes or len(path_nodes) < 2:
        return [], {}

    used_routes_list = []
    paths_dict = defaultdict(list)

    # 1. Olhar para o primeiro link
    u, v = path_nodes[0], path_nodes[1]
    candidates_start = link_to_routes.get((u, v), [])
    if not candidates_start: return [], {}

    # Lógica de seleção inicial: Tenta olhar para o segundo link para decidir melhor a rota de partida
    current_route = candidates_start[0]

    if len(path_nodes) > 2:
        v_next, w_next = path_nodes[1], path_nodes[2]
        candidates_next = link_to_routes.get((v_next, w_next), [])
        # Se houver uma rota que serve tanto o link 1 quanto o 2, escolha ela!
        common = set(candidates_start) & set(candidates_next)
        if common:
            current_route = list(common)[0]

    used_routes_list.append(current_route)
    paths_dict[current_route].append((u, v))

    # 2. Iterar pelos links restantes
    for i in range(1, len(path_nodes) - 1):
        u, v = path_nodes[i], path_nodes[i + 1]
        candidates = link_to_routes.get((u, v), [])

        if not candidates: return [], {}

        if current_route in candidates:
            paths_dict[current_route].append((u, v))
        else:
            # Precisa trocar de rota (Transferência Real)

            # Estratégia simples: Pega a primeira.
            # (Melhoria futura: olhar para frente de novo para ver qual vai mais longe)
            new_route = candidates[0]

            # Verifica sobreposição para evitar duplicar na lista sequencial
            if new_route != current_route:
                used_routes_list.append(new_route)
                current_route = new_route

            paths_dict[current_route].append((u, v))

    return used_routes_list, dict(paths_dict)


def reconstruct_path_structure_v1(path_nodes, link_to_routes):
    """
    Reconstrói as rotas minimizando o número de transferências (Look-Ahead).
    Escolhe a rota que cobre o maior segmento contínuo do caminho restante.
    """
    if not path_nodes or len(path_nodes) < 2:
        return [], {}

    used_routes_list = []
    paths_dict = defaultdict(list)

    # Índice atual no caminho de nós
    current_idx = 0
    total_nodes = len(path_nodes)

    while current_idx < total_nodes - 1:
        u, v = path_nodes[current_idx], path_nodes[current_idx + 1]

        # 1. Identificar todas as rotas que cobrem o link atual
        candidates = link_to_routes.get((u, v), [])

        if not candidates:
            # Se não há rota para este link, o caminho é inviável na rede de rotas atual
            return [], {}

        # 2. SELEÇÃO "LOOK-AHEAD": Qual candidato vai mais longe?
        best_route = None
        max_length = -1

        # Se já estamos numa rota e ela serve o próximo link, tendemos a mantê-la
        # (histerese para evitar trocas desnecessárias se o empate for perfeito)
        current_route_in_use = used_routes_list[-1] if used_routes_list else None

        for route_id in candidates:
            # Verifica quantos links consecutivos essa rota consegue cobrir
            length = 0
            temp_idx = current_idx

            while temp_idx < total_nodes - 1:
                curr_u, curr_v = path_nodes[temp_idx], path_nodes[temp_idx + 1]
                # Verifica se a rota 'route_id' cobre o link (curr_u, curr_v)
                if route_id in link_to_routes.get((curr_u, curr_v), []):
                    length += 1
                    temp_idx += 1
                else:
                    break

            # Critério de desempate: se o comprimento for igual, prefira a rota já em uso
            if length > max_length:
                max_length = length
                best_route = route_id
            elif length == max_length and route_id == current_route_in_use:
                best_route = route_id

        # 3. Registrar a melhor rota encontrada
        # Se mudamos de rota em relação ao passo anterior, adicionamos à lista sequencial
        if not used_routes_list or used_routes_list[-1] != best_route:
            used_routes_list.append(best_route)

        # 4. "Consumir" os links que essa rota cobriu
        # Adiciona os links ao dicionário da rota e avança o índice principal
        for _ in range(max_length):
            u_next = path_nodes[current_idx]
            v_next = path_nodes[current_idx + 1]
            paths_dict[best_route].append((u_next, v_next))
            current_idx += 1

    return used_routes_list, dict(paths_dict)


def assign_demand(routes, demand_matrix, network):
    """
    Versão baseada em GRAFOS.
    Encontra o menor caminho real usando a malha de rotas disponível.
    Suporta N-transferências.
    """
    assignment = {}
    num_nodes = demand_matrix.shape[0]

    # 1. Cria o grafo da rede de rotas
    adj, link_to_routes = build_route_network_graph(routes, network)

    for i in range(num_nodes):
        for j in range(num_nodes):
            q = demand_matrix[i][j]
            if q <= 0 or i == j:
                continue

            origin = i + 1
            dest = j + 1
            dist_marshall = network.shortest_paths.get((origin, dest), float('inf'))

            # 2. Dijkstra na rede de rotas
            travel_dist, path_nodes = dijkstra_shortest_path(origin, dest, adj)

            # Se encontrou caminho finito
            if path_nodes and math.isfinite(travel_dist):
                routes_used, paths_breakdown = reconstruct_path_structure(path_nodes, link_to_routes)

                assignment[(origin, dest)] = {
                    "demand": q,
                    "routes": routes_used,
                    "dist_marshall": dist_marshall,
                    "travel_distance": travel_dist,  # <--- CRUCIAL PARA O UVC
                    "paths": paths_breakdown
                }
            # Se não encontrou, não adiciona ao assignment (será penalizado na func de custo)

    return assignment


def get_path_length(network, path_links):
    """Calcula a distância total de uma lista de links."""
    dist = 0.0
    for u, v in path_links:
        dist += network.length.get((u, v), float('inf'))
    return dist

# === Funções que implementam o Headway Coordenado ===

def get_transfer_node(info):
    """
    Retorna o nó de transferência de um OD com 1 transferência.
    Se não houver transferência, retorna None.
    """
    routes = info["routes"]

    # Sem transferência
    if len(routes) != 2:
        return None

    k1, k2 = routes
    path1 = info["paths"][k1]
    path2 = info["paths"][k2]

    # último nó da rota k1
    u, v = path1[-1]
    last_node_k1 = v

    # primeiro nó da rota k2
    u2, v2 = path2[0]
    first_node_k2 = u2

    if last_node_k1 != first_node_k2:
        raise ValueError("Inconsistência: nó de transferência não coincide")

    return last_node_k1

def compute_transfer_demand_by_node(assignment):
    """
    Retorna:
    {node: demanda_total_de_transferencia}
    """
    td = defaultdict(float)

    for info in assignment.values():
        if len(info["routes"]) != 2:
            continue

        v = get_transfer_node(info)
        td[v] += info["demand"]

    return dict(td)

def select_critical_transfer_node(transfer_demand):
    """
    Retorna o nó com maior demanda de transferência.
    Se não houver transferências, retorna None.
    """
    if not transfer_demand:
        return None

    return max(transfer_demand, key=transfer_demand.get)

def build_G_k(routes, critical_node):
    """
    Retorna:
    G_k = {k: set(rotas coordenadas)}
    """
    R = len(routes)
    G = {k: set() for k in range(R)}

    if critical_node is None:
        return G  # ninguém coordena

    # rotas que passam pelo nó crítico
    coordinated_routes = {
        k for k, route in enumerate(routes)
        if critical_node in route.nodes
    }

    # atribui o mesmo conjunto a todas
    for k in coordinated_routes:
        G[k] = set(coordinated_routes)

    return G

def compute_a_ijk(assignment, G_k):
    """
    Retorna:
    a_ijk[(i, j, k)] = 0 ou 1
    """
    a_ijk = {}

    for (i, j), info in assignment.items():
        routes = info["routes"]

        for idx, k in enumerate(routes):

            # Caso 1: rota de origem
            if idx == 0:
                a_ijk[(i, j, k)] = 1
                continue

            prev_k = routes[idx - 1]

            # Caso 2: transferência
            if k in G_k.get(prev_k, set()):
                a_ijk[(i, j, k)] = 0  # coordenada
            else:
                a_ijk[(i, j, k)] = 1  # não coordenada

    return a_ijk

def compute_headway_coordinated(k, G_k, routes, a_ijk, Q, params, hk_max, network):
    G = G_k[k]
    m = Q.shape[0]

    total_length = sum(routes[n].length(network) for n in G)

    effective_demand = 0.0
    for n in G:
        for i in range(m):
            for j in range(m):
                q = Q[i, j]
                if q > 0:
                    effective_demand += q * a_ijk.get((i+1, j+1, n), 0)

    if effective_demand == 0:
        return max(hk_max[n] for n in G)

    hk = (
        4 * total_length * params["Cv"] /
        (params["V"] * params["yw"] * effective_demand)
    ) ** 0.5

    hk_max = max(hk_max[n] for n in G)

    return min(hk, hk_max)


def compute_transfer_ranking_auxi(assignment):
    """
    Calcula a demanda de transferência para cada par de rotas em cada nó.
    Retorna uma lista ordenada: [((no, r1, r2), demanda), ...]
    """
    # Chave: (nó_de_transferência, rota_A, rota_B)
    # Rota_A e Rota_B são ordenadas para evitar duplicatas como (1,2) e (2,1)
    transfer_data = defaultdict(float)

    for info in assignment.values():
        routes_used = info["routes"]
        # O artigo foca em reduzir custos de transferência entre rotas
        # Se houve transferência (mais de uma rota usada)
        if len(routes_used) > 1:
            q_ij = info["demand"]
            paths = info["paths"]

            for i in range(len(routes_used) - 1):

                r1 = routes_used[i]
                r2 = routes_used[i + 1]

                try:
                    transfer_node = paths[r1][-1][1]
                    pair = tuple(sorted((r1, r2)))
                    key = (transfer_node, pair[0], pair[1])

                    transfer_data[key] += q_ij

                except (IndexError, KeyError):
                    continue


    # Transforma em lista e ordena pela demanda decrescente (Ranking do artigo)
    ranking = sorted(transfer_data.items(), key=lambda item: item[1], reverse=True)

    return ranking

def find_coordinated_sets(transfer_ranking, routes):
    # Gamma_map: {rota_id: set_de_coordenacao}
    # No início, cada rota é seu próprio conjunto (vazio ou apenas ela mesma)
    gamma_k = {i: {i} for i, _ in enumerate(routes)}
    rotas_comprometidas = set()

    # Percorre o ranking por prioridade
    for (node, r1, r2), demand in transfer_ranking:
        # Se nenhuma das duas rotas já estiver coordenada em outro ponto [cite: 481, 482]
        if r1 not in rotas_comprometidas and r2 not in rotas_comprometidas:
            # Formar o conjunto Gamma_k para essas rotas [cite: 141]
            grupo = {r1, r2}
            gamma_k[r1] = grupo
            gamma_k[r2] = grupo

            # Marcar como ocupadas para respeitar a regra de "apenas um ponto" [cite: 480]
            rotas_comprometidas.add(r1)
            rotas_comprometidas.add(r2)

    return gamma_k


def compute_coordinated_headway_value(gamma_k, routes, a_ijk, Q, params, hk_max_dict, network):
    """
    Calcula o headway otimizado para um grupo de rotas que se coordenam.
    """
    m = Q.shape[0]
    total_length = sum(routes[n].length(network) for n in gamma_k)

    effective_demand = 0.0
    for n in gamma_k:
        for i in range(m):
            for j in range(m):
                q = Q[i, j]
                if q > 0:
                    # i+1, j+1 se seus IDs de nós começarem em 1
                    effective_demand += q * a_ijk.get((i + 1, j + 1, n), 0)

    # Evitar divisão por zero
    if effective_demand == 0:
        return min([hk_max_dict[n] for n in gamma_k])

    # Sua fórmula original
    hk = math.sqrt(
        (4 * total_length * params["Cv"]) /
            (params["V"] * params["yw"] * effective_demand)
    )

    # O headway do grupo não pode exceder o menor hk_max entre as rotas do grupo
    # (Para não estourar a capacidade de nenhuma delas)
    limit_max = max(hk_max_dict[n] for n in gamma_k)
    h_min = params['h_min']

    return max(min(hk, limit_max), h_min)

def compute_headway_uncoordinated(k, routes, a_ijk, Q, params, hk_max, network):
    """
    Calcula o headway ótimo para uma rota não coordenada.
    Baseado no equilíbrio entre custo operacional e tempo de espera (h/2).
    """
    m = Q.shape[0]
    effective_demand = 0.0

    # 1. Calcula a demanda efetiva que passa por esta rota (usando a_ijk)
    for i in range(m):
        for j in range(m):
            q = Q[i, j]
            if i == j or q == 0:
                continue

            if q > 0:
                # a_ijk.get((i+1, j+1, k), 0) verifica se o par i-j usa a rota k
                effective_demand += q * a_ijk.get((i + 1, j + 1, k), 0)

    # 2. Se não houver demanda, a rota opera no limite máximo de tempo (intervalo maior)
    if effective_demand <= 0:
        return hk_max

    # 3. Cálculo do headway ótimo (Fórmula da Raiz Quadrada)
    # Esta fórmula minimiza: Custo_Op(h) + Custo_Espera(h)
    # h = sqrt( (4 * L * Cv) / (V * yw * D_eff) )

    route_length = routes[k].length(network)

    numerator = 4 * route_length * params["Cv"]
    denominator = params["V"] * params["yw"] * effective_demand

    hk_optimal = math.sqrt(numerator / denominator)

    # 4. Restrição: O headway não pode ser maior que o hk_max (capacidade)
    # nem menor que o h_min (limite operacional, ex: 5 min)
    h_min = params['h_min']

    return max(min(hk_optimal, hk_max), h_min)

# === Mais auxiliares ===
def compute_hk_max(q_cr, params):
    K = params["K"]
    L = params["L"]

    if q_cr > 0:
        return (K * L) / q_cr

    return float('inf')

def compute_route_total_demand(route_index, assignment):
    """
    Calcula a demanda total servida pela rota k
    ∑ q_ij * a_ijk
    """
    total = 0.0

    for info in assignment.values():
        if route_index in info["routes"]:
            total += info["demand"]

    return total

def compute_route_link_flows(route_index, assignment):
    """
    Retorna um dicionário:
    {(u,v): fluxo_passageiros}
    """
    link_flows = defaultdict(float)

    for info in assignment.values():
        if route_index not in info["routes"]:
            continue

        q = info["demand"]
        path = info["paths"][route_index]

        for link in path:
            link_flows[link] += q

    return dict(link_flows)

def compute_q_cr(route_index, assignment):
    link_flows = compute_route_link_flows(route_index, assignment)
    if not link_flows:
        return 0.0
    return max(link_flows.values())


def compute_all_headways(routes, assignment, G_k, Q, params, network, a_ijk):
    """
    Calcula os headways (h_k) para todas as rotas.

    Args:
        routes: Lista de objetos Route.
        assignment: Dicionário com a alocação de demanda.
        G_k: Dicionário {rota_id: {conjunto_de_rotas_coordenadas}}.
             Já deve vir processado com base no transfer_ranking.
        Q: Matriz de demanda (O-D).
        params: Parâmetros do sistema (Cv, V, etc).
        network: Objeto da rede (para distâncias).
        a_ijk: Matriz auxiliar de uso da rota.

    Returns:
        hk: Dicionário {rota_id: headway_otimo}
    """
    hk = {}
    hk_max_dict = {}

    # 1. Passo Crítico: Calcular a Capacidade Máxima (h_max) para TODAS as rotas primeiro.
    for k in range(len(routes)):
        q_cr = compute_q_cr(k, assignment)
        hk_max_dict[k] = compute_hk_max(q_cr, params)

    # 2. Calcular o Headway Operacional (Otimizado)
    processed_routes = set()

    for k in range(len(routes)):
        if k in processed_routes:
            continue

        # Obtém o grupo de coordenação. Se não houver, retorna conjunto contendo apenas k.
        gamma_k = G_k.get(k, {k})

        # Verifica se é um grupo de coordenação real (mais de uma rota)
        if len(gamma_k) > 1:
            # === Rota Coordenada (Eq. 8 do Artigo) ===
            # Calcula um único headway para todo o grupo
            h_shared = compute_coordinated_headway_value(
                gamma_k, routes, a_ijk, Q, params, hk_max_dict, network
            )

            # Aplica o valor compartilhado a todas as rotas do grupo
            for r_id in gamma_k:
                hk[r_id] = h_shared
                processed_routes.add(r_id)
        else:
            # === Rota Não Coordenada (Eq. 5 do Artigo) ===
            hk[k] = compute_headway_uncoordinated(
                k, routes, a_ijk, Q, params, hk_max_dict[k], network
            )
            processed_routes.add(k)

    return hk

def compute_number_of_buses(route_data, h_k, params):
    d_k = route_data["length"]
    V = params["V"]

    if h_k == float('inf'):
        return 0

    # tempo de ciclo (ida + volta)
    T_k = (2 * d_k) / V

    # número de ônibus
    N_k = T_k / h_k

    return math.ceil(N_k)

# === Grafo ===
from collections import defaultdict

def build_adjacency(links):
    graph = defaultdict(set)
    for i, j in links:
        graph[i].add(j)
        graph[j].add(i)
    return graph



