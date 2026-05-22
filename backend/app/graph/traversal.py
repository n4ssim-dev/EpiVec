import networkx as nx

from app.graph.builder import get_graph


def find_paths(source: str, target: str, max_paths: int = 3) -> list[list[str]]:
    G = get_graph()
    try:
        paths = list(nx.all_simple_paths(G, source, target, cutoff=5))
        return paths[:max_paths]
    except (nx.NodeNotFound, nx.NetworkXNoPath):
        return []


def get_neighbors(node: str, depth: int = 1) -> list[str]:
    G = get_graph()
    if node not in G:
        return []
    reachable = nx.single_source_shortest_path_length(G, node, cutoff=depth)
    return list(reachable.keys())


def get_disease_regions(disease: str) -> list[str]:
    G = get_graph()
    node = f"disease:{disease}"
    if node not in G:
        return []
    return [n for n in nx.descendants(G, node) if n.startswith("region:")]
