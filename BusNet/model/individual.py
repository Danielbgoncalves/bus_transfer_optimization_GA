
from BusNet.model.route_generation import generate_first_route, generate_next_route
from BusNet.model.route import Route, assign_demand, compute_route_total_demand, compute_q_cr, compute_a_ijk, compute_all_headways, compute_transfer_ranking_auxi, find_coordinated_sets
from BusNet.model.cost_function import compute_total_cost

class Individual:
    def __init__(self, routes):
        self.routes = routes

        self.assignment = None
        self.routes_data = None
        self.costs = None
        self.fitness = None

    def evaluate_with_coordination(self, network, demand_matrix, params):
        # 1. Cálculos Globais (Feitos apenas uma vez)
        self.assignment = assign_demand(self.routes, demand_matrix, network)
        transfer_ranking = compute_transfer_ranking_auxi(self.assignment)

        # G_k mapeia cada rota ao seu grupo de coordenação {rota_id: {conjunto_de_rotas}}
        G_k = find_coordinated_sets(transfer_ranking, self.routes)

        a_ijk = compute_a_ijk(self.assignment, G_k)


        # args: compute_all_headways(routes, assignment, G_k, transfer_ranking, Q, params, network, a_ijk):
        h_k = compute_all_headways(
            self.routes,
            self.assignment,
            G_k,
            demand_matrix,  # Representa o 'Q' na sua função
            params,
            network,
            a_ijk
        )

        # Dados por rota
        self.routes_data = []
        for k, route in enumerate(self.routes):
            route_info = {}
            route_info["length"] = route.length(network)
            route_info["total_demand"] = compute_route_total_demand(k, self.assignment)
            route_info["q_cr"] = compute_q_cr(k, self.assignment)
            route_info["h"] = h_k[k]  # <<< vem de fora agora
            self.routes_data.append(route_info)

        # Custos
        self.costs = compute_total_cost(
            self.routes_data,
            self.assignment,
            params,
            a_ijk,
            h_k,
            demand_matrix,
            network,
            True
        )

        # def compute_total_cost(routes_data, assignment, params, a_ijk, h_k, demand_matrix):

        # Fitness
        self.fitness = self.costs["TC"]
        return self.fitness

"""
    # É a sem coordenação
    def evaluate_with_no_coordination(self, network, demand_matrix, params):
        # 1. Assignment (Passando network para calcular distancias reais)
        self.assignment = assign_demand(self.routes, demand_matrix, network)

        # 2. Dados por rota
        self.routes_data = []
        for k, route in enumerate(self.routes):
            route_info = {}
            route_info["length"] = route.length(network)
            route_info["total_demand"] = compute_route_total_demand(k, self.assignment)
            route_info["q_cr"] = compute_q_cr(k, self.assignment)

            # Recalcula Headway
            route_info["h"] = compute_headway(route_info, params)
            self.routes_data.append(route_info)

        # 3. Custos (Ajustado argumentos)
        self.costs = compute_total_cost(
            self.routes_data,
            self.assignment, # removemos network daqui pois não usa mais no UVC
            params, 0, 0, 0, network
        )

        # 4. Fitness
        self.fitness = self.costs["TC"]
        return self.fitness

    def evaluate_with_coordination(self, network, demand_matrix, params):

        # 1. Assignment
        self.assignment = assign_demand(
            self.routes, demand_matrix, network
        )

        # 2. Transfer demand → G_k
        transfer_demand = compute_transfer_demand_by_node(self.assignment)
        critical_node = select_critical_transfer_node(transfer_demand)
        G_k = build_G_k(self.routes, critical_node)

        # 3. a_ijk
        a_ijk = compute_a_ijk(self.assignment, G_k)

        # 4. Headways (GLOBAL)
        h_k = compute_all_headways(
            self.routes,
            G_k,
            a_ijk,
            demand_matrix,
            params,
            self.assignment,
            network
        )

        # 5. Dados por rota
        self.routes_data = []
        for k, route in enumerate(self.routes):
            route_info = {}
            route_info["length"] = route.length(network)
            route_info["total_demand"] = compute_route_total_demand(k, self.assignment)
            route_info["q_cr"] = compute_q_cr(k, self.assignment)
            route_info["h"] = h_k[k]   # <<< vem de fora agora
            self.routes_data.append(route_info)

        # 6. Custos
        self.costs = compute_total_cost(
            self.routes_data,
            self.assignment,
            params,
            a_ijk,
            h_k,
            demand_matrix,
            network,
            True
        )

        # def compute_total_cost(routes_data, assignment, params, a_ijk, h_k, demand_matrix):

        # 7. Fitness
        self.fitness = self.costs["TC"]
        return self.fitness


"""

def generate_individual(graph, Pe):
    routes = []
    free_nodes = set(graph.keys())

    r0 = generate_first_route(graph, Pe)
    routes.append(r0)
    free_nodes -= set(r0)

    while free_nodes:
        #rk = generate_next_route(graph, routes, free_nodes, Pe)
        rk = generate_next_route(graph, routes, Pe)
        routes.append(rk)
        free_nodes -= set(rk)

    return Individual([Route(v) for v in routes])

def generate_population(pop_size, graph, Pe):
    population = []

    for _ in range(pop_size):
        ind = generate_individual(graph, Pe)
        population.append(ind)

    return population

# def generate_population(pop_size, graph, Pe=0.6):
#     """
#     Gera uma população de soluções (listas de rotas) para o grafo.
#
#     Args:
#         pop_size (int): Número de indivíduos na população.
#         graph (dict): Grafo representado como dicionário {nó: [vizinhos]}.
#         Pe (float): Probabilidade de terminar a rota durante expansão.
#
#     Returns:
#         population (list): Lista de indivíduos, cada um sendo uma lista de rotas.
#     """
#     population = []
#     for _ in range(pop_size):
#         individual = generate_all_routes(graph, Pe)
#         population.append(individual)
#     return population

