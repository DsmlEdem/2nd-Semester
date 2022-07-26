from collections import defaultdict


def bellman_ford(graph, weight, source, update_order=None):
    n = len(graph)
    dist = {node: float('inf') for node in graph}
    prec = {node: None for node in graph}
    dist[source] = 0
    
    if update_order is not None:
        if sorted(update_order) != sorted(graph):
            raise ValueError(
                'Nodes of update_order not the same as nodes of the graph'
            )
    else:
        update_order = tuple(graph)
    
    for iteration in range(n):
        print(f'ITERATION {iteration}')
        changed = False
        for node in update_order:
            print(f'Updating node {node}...')
            for neighbor in graph[node]:
                alt = dist[neighbor] + weight[neighbor][node]
                print(f'\tIncoming from neighbor {neighbor}.', end=' ')
                if alt < dist[node]:
                    print(
                        f'Found better path.  \t'
                        f'dist[{neighbor}] + ({neighbor}-->{node})'
                        f' = {dist[neighbor]} + {weight[neighbor][node]} = {alt}'
                        f' < dist[{node}] = {dist[node]}'
                    )
                    dist[node] = alt
                    prec[node] = neighbor
                    changed = True
                else:
                    print(
                        'No better path found.\t'
                        f'dist[{neighbor}] + ({neighbor}-->{node})'
                        f' = {dist[neighbor]} + {weight[neighbor][node]} = {alt}'
                        f' >= dist[{node}] = {dist[node]}'
                    )
        if not changed:
            return dist, prec, False
        print('-' * 30)
    return dist, prec, True


def create_graph(edges):
    graph = defaultdict(list)
    weight = defaultdict(dict)
    for u, v, w in edges:
        graph[u].append(v)
        graph[v].append(u)
        weight[u][v] = w
        weight[v][u] = w
    return graph, weight


def draw_graph(edges):
    try:
        import networkx as nx
    except ImportError:
        print('networkx not installed. Cannot plot the graph')
        return
    G = nx.Graph()
    G.add_weighted_edges_from(edges)
    pos = nx.spring_layout(G)
    edge_labels = nx.get_edge_attributes(G, 'weight')
    nx.draw_networkx(G, pos)
    nx.draw_networkx_edge_labels(G, pos, edge_labels)


def bellman_cheat(edges, source, update_order=None):
    draw_graph(edges)
    dist, prec, stopped_early = bellman_ford(
        *create_graph(edges),
        source=source, update_order=update_order
    )
    print()
    print(f'Distances:  {dist}')
    print(f'Precursors: {prec}')


if __name__ == '__main__':
    edges = (
        ('F', 'E', 9),
        ('E', 'D', 6),
        ('D', 'B', 15),
        ('B', 'A', 7),
        ('A', 'F', 14),
        ('C', 'F', 2),
        ('C', 'A', 9),
        ('C', 'B', 10),
        ('C', 'D', 11),
    )
    source = 'A'
    # Always put the source node first in order if its order is not specified
    update_order = (source, 'B', 'C', 'D', 'F', 'E')

    bellman_cheat(edges, source, update_order=update_order)
