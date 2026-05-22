import networkx as nx

from app.graph.builder import get_graph


def compute_centrality() -> dict[str, dict]:
    G = get_graph()
    if G.number_of_nodes() == 0:
        return {}
    return {
        "degree": nx.degree_centrality(G),
        "betweenness": nx.betweenness_centrality(G),
        "pagerank": nx.pagerank(G),
    }


def get_propagation_features(disease: str, region: str) -> dict:
    G = get_graph()
    node = f"disease:{disease}"
    if node not in G:
        return {}

    pr = nx.pagerank(G)
    return {
        "out_degree": G.out_degree(node),
        "in_degree": G.in_degree(node),
        "pagerank": pr.get(node, 0.0),
        "region_connections": len([
            n for n in G.successors(node) if f"region:{region}" in n
        ]),
    }
