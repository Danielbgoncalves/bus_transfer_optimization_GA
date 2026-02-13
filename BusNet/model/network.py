
import math
class Network:
    def __init__(self, nodes, links):
        self.nodes = nodes
        self.links = links
        self.dist = {}
        self.shortest_paths = None

        self.length = {}

        self._build_distances()
        self._floyd_warshall()


        for i, j in links:
            xi, yi = nodes[i]
            xj, yj = nodes[j]
            d = math.hypot(xi - xj, yi - yj)
            self.length[(i, j)] = d
            self.length[(j, i)] = d

    def _build_distances(self):

        # inicializa infinito
        for i in self.nodes:
            for j in self.nodes:
                self.dist[(i, j)] = math.inf

        # distância zero para i -> i
        for i in self.nodes:
            self.dist[(i, i)] = 0.0

        # links físicos (distância constante por link)
        for i, j in self.links:
            xi, yi = self.nodes[i]
            xj, yj = self.nodes[j]

            d = math.hypot(xi - xj, yi - yj)
            self.dist[(i, j)] = d
            self.dist[(j, i)] = d

    def _floyd_warshall(self):
        nodes = list(self.nodes.keys())

        # copia distâncias iniciais
        D = { (i, j): self.dist[(i, j)] for i in nodes for j in nodes }

        for k in nodes:
            for i in nodes:
                for j in nodes:
                    if D[(i, j)] > D[(i, k)] + D[(k, j)]:
                        D[(i, j)] = D[(i, k)] + D[(k, j)]

        self.shortest_paths = D