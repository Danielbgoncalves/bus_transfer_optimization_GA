import matplotlib.pyplot as plt
import matplotlib.animation as animation
import networkx as nx
import numpy as np
from collections import defaultdict
import colorsys

def visualize_graph(G, nodes, links, demand_matrix):
    G = nx.Graph()

    G.add_nodes_from(nodes.keys())
    G.add_edges_from(links)

    for u, v in G.edges():
        G[u][v]["demand"] = demand_matrix[u-1, v-1] + demand_matrix[v-1, u-1]

    edge_labels = {
        (u, v): G[u][v]["demand"]
        for u, v in G.edges()
    }

    plt.figure(figsize=(10, 8))

    nx.draw(
        G,
        pos=nodes,
        with_labels=True,
        node_size=500,
        node_color="lightblue",
        edge_color="gray",
        font_size=9
    )

    nx.draw_networkx_edge_labels(
        G,
        pos=nodes,
        edge_labels=edge_labels,
        font_size=7
    )

    plt.axis("equal")
    plt.show()

# Mostra pai e filho lado a lado, com cores específicas para cada rota
def plot_parent_child_routes_with_offset(
    parent,
    child,
    node_positions,
    title_plot,
    title_parent="Pai",
    title_child="Filho",
    offset_scale=0.08
):
    nodes_to_print = node_positions.copy()
    nodes_to_print[16] = (5.8, 4.55)
    nodes_to_print[7] = (11.8, 9)
    # ===============================
    # 1. Canonicalização
    # ===============================
    def canonical_route(nodes):
        r = tuple(nodes)
        return min(r, r[::-1])

    def canonical_edge(a, b):
        return tuple(sorted((a, b)))

    # ===============================
    # 2. Coletar rotas (pai + filho)
    # ===============================
    all_routes = []
    for ind in (parent, child):
        for route in ind.routes:
            rid = canonical_route(route.nodes)
            if rid not in all_routes:
                all_routes.append(rid)

    cmap = plt.cm.get_cmap("tab20", len(all_routes))
    route_color = {rid: cmap(i) for i, rid in enumerate(all_routes)}

    # ===============================
    # 3. Contar overlaps por edge
    # ===============================
    edge_usage = defaultdict(list)
    for ind in (parent, child):
        for route in ind.routes:
            rid = canonical_route(route.nodes)
            for i in range(len(route.nodes) - 1):
                e = canonical_edge(route.nodes[i], route.nodes[i + 1])
                if rid not in edge_usage[e]:
                    edge_usage[e].append(rid)

    # ===============================
    # 4. Função interna de plot
    # ===============================
    def _plot(ax, individual, title):
        ax.set_title(title)
        ax.axis("off")

        # ---- desenhar rotas com offset
        for route in individual.routes:
            rid = canonical_route(route.nodes)
            color = route_color[rid]

            for i in range(len(route.nodes) - 1):
                a, b = route.nodes[i], route.nodes[i + 1]
                e = canonical_edge(a, b)

                x1, y1 = nodes_to_print[a]
                x2, y2 = nodes_to_print[b]

                dx, dy = x2 - x1, y2 - y1
                length = np.hypot(dx, dy)
                if length == 0:
                    continue

                px, py = -dy / length, dx / length

                overlaps = edge_usage[e]
                k = overlaps.index(rid)
                n = len(overlaps)

                offset = (k - (n - 1) / 2) * offset_scale
                ox, oy = px * offset, py * offset

                ax.plot(
                    [x1 + ox, x2 + ox],
                    [y1 + oy, y2 + oy],
                    color=color,
                    linewidth=3,
                    solid_capstyle="round"
                )

        # ---- desenhar nós e labels (por último)
        G = nx.Graph()
        G.add_nodes_from(nodes_to_print.keys())

        nx.draw_networkx_nodes(
            G,
            nodes_to_print,
            node_size=650,
            node_color="white",
            edgecolors="black",
            linewidths=1.5,
            ax=ax
        )

        nx.draw_networkx_labels(
            G,
            nodes_to_print,
            font_size=10,
            font_weight="bold",
            ax=ax
        )

    # ===============================
    # 5. Plot lado a lado
    # ===============================
    fig, axes = plt.subplots(1, 2, figsize=(15, 6))

    _plot(axes[0], parent, title_parent)
    _plot(axes[1], child, title_child)

    fig.suptitle(title_plot)
    plt.tight_layout()
    plt.show()

def plot_parent_child_routes_with_offset2(
        parent,
        child,
        node_positions,
        title_plot,
        title_parent="Pai",
        title_child="Filho",
        offset_scale=0.15
):
    nodes_to_print = node_positions.copy()
    nodes_to_print[16] = (5.8, 4.55)
    nodes_to_print[7] = (11.8, 9)

    # ===============================
    # 1. Canonicalização
    # ===============================
    def canonical_route(nodes):
        r = tuple(nodes)
        return min(r, r[::-1])

    def canonical_edge(a, b):
        return tuple(sorted((a, b)))

    # ===============================
    # 2. Coletar rotas (pai + filho)
    # ===============================
    all_routes = []
    for ind in (parent, child):
        for route in ind.routes:
            rid = canonical_route(route.nodes)
            if rid not in all_routes:
                all_routes.append(rid)

    # ===============================
    # 3. CORES MAIS DISTINTAS (HSV)
    # ===============================
    def generate_distinct_colors(n):
        """Gera n cores bem distintas usando HSV"""
        colors = []
        golden_ratio = 0.618033988749895
        hue = 0

        for i in range(n):
            hue += golden_ratio
            hue %= 1.0

            saturation = 0.65 + (i % 3) * 0.15
            value = 0.75 + (i % 2) * 0.20

            rgb = colorsys.hsv_to_rgb(hue, saturation, value)
            colors.append(rgb)

        return colors

    distinct_colors = generate_distinct_colors(len(all_routes))
    route_color = {rid: distinct_colors[i] for i, rid in enumerate(all_routes)}

    # ===============================
    # 4. Contar overlaps por edge
    # ===============================
    edge_usage = defaultdict(list)
    for ind in (parent, child):
        for route in ind.routes:
            rid = canonical_route(route.nodes)
            for i in range(len(route.nodes) - 1):
                e = canonical_edge(route.nodes[i], route.nodes[i + 1])
                if rid not in edge_usage[e]:
                    edge_usage[e].append(rid)

    # ===============================
    # 5. Função interna de plot
    # ===============================
    def _plot(ax, individual, title):
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.axis("off")
        ax.set_aspect('equal')

        # ---- desenhar rotas com offset MELHORADO
        for route in individual.routes:
            rid = canonical_route(route.nodes)
            color = route_color[rid]

            for i in range(len(route.nodes) - 1):
                a, b = route.nodes[i], route.nodes[i + 1]
                e = canonical_edge(a, b)

                x1, y1 = nodes_to_print[a]
                x2, y2 = nodes_to_print[b]

                dx, dy = x2 - x1, y2 - y1
                length = np.hypot(dx, dy)
                if length == 0:
                    continue

                px, py = -dy / length, dx / length

                overlaps = edge_usage[e]
                k = overlaps.index(rid)
                n = len(overlaps)

                offset = (k - (n - 1) / 2) * offset_scale
                ox, oy = px * offset, py * offset

                ax.plot(
                    [x1 + ox, x2 + ox],
                    [y1 + oy, y2 + oy],
                    color=color,
                    linewidth=4,
                    solid_capstyle="round",
                    alpha=0.8,
                    zorder=1
                )

        # ---- desenhar nós e labels (SEM zorder no networkx)
        G = nx.Graph()
        G.add_nodes_from(nodes_to_print.keys())

        # Desenha nós com scatter para ter controle de zorder
        node_x = [nodes_to_print[n][0] for n in G.nodes()]
        node_y = [nodes_to_print[n][1] for n in G.nodes()]

        ax.scatter(
            node_x, node_y,
            s=700,
            c='white',
            edgecolors='black',
            linewidths=2,
            zorder=2
        )

        # Labels por cima de tudo
        for node, (x, y) in nodes_to_print.items():
            ax.text(
                x, y, str(node),
                fontsize=10,
                fontweight='bold',
                ha='center',
                va='center',
                zorder=3
            )

    # ===============================
    # 6. Plot lado a lado
    # ===============================
    fig, axes = plt.subplots(1, 2, figsize=(16, 7))

    _plot(axes[0], parent, title_parent)
    _plot(axes[1], child, title_child)

    fig.suptitle(title_plot, fontsize=16, fontweight='bold')
    plt.tight_layout()
    plt.show()

def plot_fitness_by_epochs(metrics):
    iterations = [m["iteration"] for m in metrics]
    best_fitness = [m["best_fitness"] for m in metrics]

    plt.figure()
    plt.plot(iterations, best_fitness)
    plt.xlabel("Iteração")
    plt.ylabel("Best fitness")
    plt.title("Evolução do melhor fitness")
    plt.grid(True)
    plt.show()

def create_evolution_timelapse(metrics, node_positions, filename="./gifs/evolution_timelapse.gif"):
    """
    Gera um GIF animado da evolução do melhor indivíduo.
    Usa o mesmo estilo visual do plot_parent_child_routes_with_offset2.
    """

    # Configuração dos nós (Hardcoded conforme seu exemplo)
    nodes_to_print = node_positions.copy()
    if 16 in nodes_to_print: nodes_to_print[16] = (5.8, 4.55)
    if 7 in nodes_to_print: nodes_to_print[7] = (11.8, 9)

    # --- Helpers do seu código original ---
    def canonical_route(nodes):
        r = tuple(nodes)
        return min(r, r[::-1])

    def canonical_edge(a, b):
        return tuple(sorted((a, b)))

    # --- Gerenciamento de Cores Consistente ---
    # Precisamos garantir que a rota [1, 2, 3] tenha a mesma cor no frame 0 e no frame 100
    # Coletar todas as rotas únicas que aparecem em TODA a história
    all_unique_routes = set()
    for m in metrics:
        ind = m["best_ind"]
        for route in ind.routes:
            all_unique_routes.add(canonical_route(route.nodes))

    sorted_routes = sorted(list(all_unique_routes))

    # Gerador de cores HSV (mesma lógica sua)
    def generate_colors(n):
        colors = []
        golden_ratio = 0.618033988749895
        hue = 0
        for i in range(n):
            hue += golden_ratio
            hue %= 1.0
            saturation = 0.65 + (i % 3) * 0.15
            value = 0.75 + (i % 2) * 0.20
            colors.append(colorsys.hsv_to_rgb(hue, saturation, value))
        return colors

    palette = generate_colors(len(sorted_routes))
    route_color_map = {rid: col for rid, col in zip(sorted_routes, palette)}

    # --- Configuração da Figura ---
    fig, ax = plt.subplots(figsize=(10, 8))
    offset_scale = 0.15  # Mesmo valor do seu código

    def update(frame_idx):
        ax.clear()
        ax.set_aspect('equal')
        ax.axis("off")

        data = metrics[frame_idx]
        individual = data["best_ind"]
        iteration = data["iteration"]
        fitness = data["best_fitness"]
        operator = data.get("operator", "N/A")

        # Título Dinâmico
        ax.set_title(
            f"Iteração: {iteration} | Fitness: {fitness:.2f}\nOperador Anterior: {operator}",
            fontsize=14, fontweight='bold'
        )

        # 1. Calcular Overlaps (Edge Usage) para este frame
        edge_usage = defaultdict(list)
        for route in individual.routes:
            rid = canonical_route(route.nodes)
            for i in range(len(route.nodes) - 1):
                e = canonical_edge(route.nodes[i], route.nodes[i + 1])
                # Nota: Diferente do plot pai/filho, aqui só temos 1 individuo,
                # então permitimos repetição se a rota passar 2x no mesmo link (raro mas possivel)
                # ou se houver rotas sobrepostas no mesmo individuo.
                if rid not in edge_usage[e]:
                    edge_usage[e].append(rid)

        # 2. Desenhar Rotas
        for route in individual.routes:
            rid = canonical_route(route.nodes)
            color = route_color_map.get(rid, (0, 0, 0))  # Fallback black

            for i in range(len(route.nodes) - 1):
                a, b = route.nodes[i], route.nodes[i + 1]
                e = canonical_edge(a, b)

                x1, y1 = nodes_to_print[a]
                x2, y2 = nodes_to_print[b]

                dx, dy = x2 - x1, y2 - y1
                length = np.hypot(dx, dy)
                if length == 0: continue

                # Vetor perpendicular para o offset
                px, py = -dy / length, dx / length

                # Lógica de Offset
                if rid in edge_usage[e]:
                    overlaps = edge_usage[e]
                    k = overlaps.index(rid)
                    n = len(overlaps)
                    offset = (k - (n - 1) / 2) * offset_scale
                else:
                    offset = 0

                ox, oy = px * offset, py * offset

                ax.plot(
                    [x1 + ox, x2 + ox],
                    [y1 + oy, y2 + oy],
                    color=color,
                    linewidth=4,
                    solid_capstyle="round",
                    alpha=0.8,
                    zorder=1
                )

        # 3. Desenhar Nós (Por cima)
        node_x = [nodes_to_print[n][0] for n in nodes_to_print]
        node_y = [nodes_to_print[n][1] for n in nodes_to_print]

        ax.scatter(
            node_x, node_y,
            s=600,
            c='white',
            edgecolors='black',
            linewidths=2,
            zorder=2
        )

        for node, (x, y) in nodes_to_print.items():
            ax.text(
                x, y, str(node),
                fontsize=9,
                fontweight='bold',
                ha='center',
                va='center',
                zorder=3
            )

    # Criação da Animação
    # Frames reduzidos se tiver muita iteração (opcional: metrics[::5] pega de 5 em 5)
    print(f"Gerando animação com {len(metrics)} frames...")

    # --- Replicar último frame ---
    extra_last_frames = 15  # quantidade de vezes que o último frame será repetido
    frame_indices = list(range(len(metrics))) + [len(metrics) - 1] * extra_last_frames

    ani = animation.FuncAnimation(
        fig,
        update,
        frames=frame_indices,   # <-- agora usamos a lista customizada
        interval=200,
        repeat=False
    )

    # Salvar
    # Requer 'pillow' instalado (pip install pillow)
    ani.save(filename, writer='pillow', fps=5)
    print(f"GIF salvo com sucesso: {filename}")
    plt.close()