from itertools import product
from BusNet.genetic_algorithm.run_ga import run_ga, choose_operator, redistribute_equal
from BusNet.model.route import build_adjacency
from BusNet.model.network import Network
from BusNet.model.individual import generate_population

from BusNet.datas.demand_matrix import DEMAND
from BusNet.datas.nodes import NODES
from BusNet.datas.links import LINKS
from BusNet.plots.visualize_graphs import plot_fitness_by_epochs, plot_parent_child_routes_with_offset2

import math



def comparar_distancias_rede(network):
    """
    Compara a distância Euclidiana (direta) com o Shortest Path (grafo).
    Identifica pares onde a diferença (SP - Euclidiana) é negativa.
    """
    nodes = network.nodes
    sp = network.shortest_paths

    print(f"{'Par O-D':<10} | {'Euclidiana':<12} | {'Shortest Path':<15} | {'Diferença'}")
    print("-" * 60)

    erros_encontrados = 0
    node_ids = sorted(nodes.keys())

    for i in node_ids:
        for j in node_ids:
            if i >= j:  # Evita duplicatas (1-2 e 2-1) e diagonal principal
                continue

            # 1. Distância Euclidiana usando as coordenadas (X, Y)
            x1, y1 = nodes[i]
            x2, y2 = nodes[j]
            dist_euclid = math.hypot(x1 - x2, y1 - y2)

            # 2. Distância do Caminho Mínimo calculada pelo Floyd-Warshall
            dist_sp = sp.get((i, j), float('inf'))

            # Diferença (Se negativa, o Shortest Path é menor que a linha reta)
            diff = dist_sp - dist_euclid

            if diff < -1e-7:
                print(f"{i:2d}-{j:<4d} | {dist_euclid:<12.4f} | {dist_sp:<15.4f} | {diff:.4f} (NEGATIVO)")
                erros_encontrados += 1
            else:
                print(f"{i:2d}-{j:<4d} | {dist_euclid:<12.4f} | {dist_sp:<15.4f} | {diff:.4f} (POSITIVO)")

    if erros_encontrados == 0:
        print("\nSucesso: Nenhuma inconsistência encontrada. SP >= Euclidiana em todos os pares.")
    else:
        print(f"\nTotal de inconsistências encontradas: {erros_encontrados}")

network = Network(NODES, LINKS)

comparar_distancias_rede(network)