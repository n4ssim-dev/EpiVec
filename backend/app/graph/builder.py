import networkx as nx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.triple import Triple

_graph: nx.DiGraph = nx.DiGraph()
_collapsed_graph: nx.DiGraph = nx.DiGraph()


def _collapse_id(node_id: str) -> str:
    if node_id.startswith("region:"):
        return node_id.split("@")[0]
    return node_id


def _build_collapsed(G: nx.DiGraph) -> nx.DiGraph:
    """Retourne un graphe où region:XX@date → region:XX (dédupliqué)."""
    C = nx.DiGraph()
    for u, v, d in G.edges(data=True):
        cu, cv = _collapse_id(u), _collapse_id(v)
        if cu != cv and not C.has_edge(cu, cv):
            C.add_edge(cu, cv, predicate=d.get("predicate"))
    return C


async def rebuild_graph(session: AsyncSession) -> nx.DiGraph:
    global _graph, _collapsed_graph
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
    _collapsed_graph = _build_collapsed(G)
    return _graph


def get_graph() -> nx.DiGraph:
    return _graph


def get_collapsed_graph() -> nx.DiGraph:
    return _collapsed_graph


async def get_subgraph(
    disease: str | None,
    region: str | None,
    depth: int,
    session: AsyncSession,
) -> tuple[list[dict], list[dict]]:
    global _collapsed_graph
    if _graph.number_of_nodes() == 0:
        await rebuild_graph(session)

    C = _collapsed_graph
    MAX_NODES = 200

    seed_nodes: set[str] = set()
    if disease:
        seed_nodes.add(f"disease:{disease}")
    if region:
        seed_nodes.update(n for n in C.nodes if n == f"region:{region}")

    if not seed_nodes:
        seed_nodes = {n for n in C.nodes if n.startswith("disease:")}

    subgraph_nodes: set[str] = set()
    for node in seed_nodes:
        if node in C:
            reachable = nx.single_source_shortest_path_length(C, node, cutoff=depth)
            subgraph_nodes.update(reachable.keys())

    if len(subgraph_nodes) > MAX_NODES:
        kept = set(seed_nodes & subgraph_nodes)
        others = list(subgraph_nodes - kept)
        kept.update(others[: MAX_NODES - len(kept)])
        subgraph_nodes = kept

    sub = C.subgraph(subgraph_nodes)
    nodes = [{"id": n, "label": n} for n in sub.nodes]
    edges = [
        {"source": u, "target": v, "predicate": d.get("predicate")}
        for u, v, d in sub.edges(data=True)
    ]
    return nodes, edges
