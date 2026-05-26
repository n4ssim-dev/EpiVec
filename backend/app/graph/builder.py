import networkx as nx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.triple import Triple

# Graphe global chargé en mémoire — reconstruit à chaque ingestion
_graph: nx.DiGraph = nx.DiGraph()


async def rebuild_graph(session: AsyncSession) -> nx.DiGraph:
    global _graph
    result = await session.execute(select(Triple))
    triples = result.scalars().all()

    G = nx.DiGraph()
    for t in triples:
        G.add_edge(
            t.subject,
            t.object,
            predicate=t.predicate,
            source=t.source,
            weight=t.confidence,
        )

    _graph = G
    return _graph


def get_graph() -> nx.DiGraph:
    return _graph


async def get_subgraph(
    disease: str | None,
    region: str | None,
    depth: int,
    session: AsyncSession,
) -> tuple[list[dict], list[dict]]:
    G = _graph if _graph.number_of_nodes() > 0 else await rebuild_graph(session)

    MAX_NODES = 200

    seed_nodes: set[str] = set()
    if disease:
        seed_nodes.add(f"disease:{disease}")
    if region:
        seed_nodes.update(n for n in G.nodes if f"region:{region}" in n)

    if not seed_nodes:
        # Sans filtre : partir des nœuds "disease:" uniquement pour rester compact
        disease_nodes = [n for n in G.nodes if n.startswith("disease:")]
        seed_nodes = set(disease_nodes[:10])

    subgraph_nodes: set[str] = set()
    for node in seed_nodes:
        if node in G:
            reachable = nx.single_source_shortest_path_length(G, node, cutoff=depth)
            subgraph_nodes.update(reachable.keys())
            if len(subgraph_nodes) >= MAX_NODES:
                break

    # Plafonner le nombre de nœuds retournés
    if len(subgraph_nodes) > MAX_NODES:
        subgraph_nodes = set(list(subgraph_nodes)[:MAX_NODES])

    sub = G.subgraph(subgraph_nodes)
    nodes = [{"id": n, "label": n} for n in sub.nodes]
    edges = [
        {"source": u, "target": v, "predicate": d.get("predicate")}
        for u, v, d in sub.edges(data=True)
    ]
    return nodes, edges
