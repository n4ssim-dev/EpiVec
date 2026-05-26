import networkx as nx

from app.graph.builder import get_graph, get_collapsed_graph


def compute_centrality() -> dict[str, dict]:
    C = get_collapsed_graph()
    if C.number_of_nodes() == 0:
        return {}
    U = C.to_undirected()
    return {
        "degree": nx.degree_centrality(U),
        "pagerank": nx.pagerank(U),
    }


def get_propagation_features(disease: str, region: str) -> dict:
    G = get_graph()
    node = f"disease:{disease}"
    if node not in G:
        return {}

    C = get_collapsed_graph()
    U = C.to_undirected()
    pr = nx.pagerank(U) if U.number_of_nodes() > 0 else {}
    region_node = f"region:{region}"
    return {
        "out_degree": G.out_degree(node),
        "in_degree": G.in_degree(node),
        "pagerank": pr.get(node, 0.0),
        "region_connections": 1 if C.has_edge(node, region_node) else 0,
    }
