import numpy as np
import math

def compute_fleet_cost(routes_data, params):
    Cv = params["Cv"]
    V  = params["V"]

    total_buses = 0
    for route in routes_data:
        d_k = route["length"]
        h_k = route["h"]

        n_k = d_k / h_k

        total_buses += n_k

        # 3. O custo total da frota é o número de ônibus * custo por veículo
    FC = (2 * total_buses * Cv) / V
    return FC

def compute_user_in_vehicle_cost(assignment, params):
    """
    Calcula o UVC usando apenas a matriz de demanda e a distância mínima
    calculado no assigment.
    """
    V = params["V"]  # Velocidade
    yv = params["yv"]  # Valor do tempo de viagem (in-vehicle)

    cost = 0.0
    # Iteramos diretamente sobre os passageiros que conseguiram uma rota
    for (_, _), info in assignment.items():
        qij = info["demand"]
        Dij = info["travel_distance"]  # Pega o Dij que calculamos no assign_demand

        # Custo = Demanda * Peso * (Distância nas rotas / Velocidade)
        if math.isfinite(Dij):
            cost += qij * Dij


    UVC = (yv * cost) / V

    return UVC

def compute_user_waiting_cost(a_ijk, h_k, demand_matrix, params):

    total = 0.0
    m = demand_matrix.shape[0]
    yw = params['yw']

    for k, hk in h_k.items():

        for i in range(m):
            for j in range(m):
                q = demand_matrix[i, j]
                if q <= 0 or i == j:
                    continue

                usage = a_ijk.get((i + 1, j + 1, k), 0)
                if usage > 0:
                    total += q * usage * hk

    UWC = yw * total / 2

    return UWC

def compute_total_cost(
        routes_data, assignment, params, a_ijk, h_k, demand_matrix,network, coordinated=False
):
    FC  = compute_fleet_cost(routes_data, params)
    UVC = compute_user_in_vehicle_cost(assignment, params)
    UWC = compute_user_waiting_cost(a_ijk, h_k, demand_matrix, params)

    return {"TC": FC + UVC + UWC, "FC": FC, "UVC": UVC, "UWC": UWC}