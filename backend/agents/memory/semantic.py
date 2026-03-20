"""Semantic Memory — Medical knowledge graph layer."""

from __future__ import annotations

import logging
from typing import Any

import networkx as nx

from backend.db import supabase as db
from backend.processors.embedder import Embedder

log = logging.getLogger(__name__)


class SemanticMemory:
    """Medical concept knowledge graph stored in Supabase + NetworkX."""

    ENTITY_TYPES = [
        "imaging_modality", "anatomy", "condition", "architecture",
        "dataset", "metric", "technique", "limitation", "finding",
    ]
    RELATIONSHIP_TYPES = [
        "applied_to", "achieves", "outperforms", "limited_by",
        "not_tested_on", "requires", "used_for",
    ]

    def __init__(self) -> None:
        self.embedder = Embedder()

    def get_nodes(self, user_id: str, entity_type: str | None = None) -> list[dict]:
        """Get all nodes for a user, optionally filtered by type."""
        filters: dict[str, Any] = {"user_id": user_id}
        if entity_type:
            filters["entity_type"] = entity_type
        return db.select("semantic_nodes", filters=filters, service=True)

    def get_edges(self, user_id: str, relationship: str | None = None) -> list[dict]:
        filters: dict[str, Any] = {"user_id": user_id}
        if relationship:
            filters["relationship"] = relationship
        return db.select("semantic_edges", filters=filters, service=True)

    def query_neighbors(
        self, node_id: str, user_id: str, relationship_type: str | None = None, depth: int = 1
    ) -> list[dict]:
        """Find nodes connected to a given node."""
        edges = db.select("semantic_edges", filters={"user_id": user_id, "source_node_id": node_id}, service=True)
        if relationship_type:
            edges = [e for e in edges if e["relationship"] == relationship_type]
        target_ids = [e["target_node_id"] for e in edges]
        if not target_ids:
            return []
        nodes = []
        for tid in target_ids:
            result = db.select("semantic_nodes", filters={"id": tid}, service=True)
            nodes.extend(result)
        return nodes

    async def find_related_concepts(
        self, query: str, user_id: str, top_k: int = 10
    ) -> list[dict]:
        """Vector similarity search on semantic nodes."""
        embedding = await self.embedder.embed(query)
        # Use Supabase RPC for vector search on semantic_nodes
        try:
            results = db.get_client().rpc("match_semantic_nodes", {
                "query_embedding": embedding,
                "match_count": top_k,
                "filter_user_id": user_id,
            }).execute()
            return results.data or []
        except Exception:
            # Fallback: get all nodes and do local similarity
            nodes = self.get_nodes(user_id)
            return nodes[:top_k]

    def build_subgraph(self, user_id: str, entity_names: list[str] | None = None) -> nx.DiGraph:
        """Build a NetworkX graph from the user's knowledge graph."""
        graph = nx.DiGraph()
        nodes = self.get_nodes(user_id)
        edges = self.get_edges(user_id)

        node_map: dict[str, dict] = {}
        for n in nodes:
            if entity_names and n["entity_name"] not in entity_names:
                continue
            graph.add_node(n["id"], type=n["entity_type"], name=n["entity_name"], frequency=n.get("frequency", 1))
            node_map[n["id"]] = n

        for e in edges:
            if e["source_node_id"] in node_map and e["target_node_id"] in node_map:
                graph.add_edge(
                    e["source_node_id"], e["target_node_id"],
                    relationship=e["relationship"], weight=e.get("weight", 1.0),
                )

        return graph

    def get_gap_candidates(self, user_id: str) -> list[dict]:
        """Find entities with low connectivity — potential research gaps."""
        graph = self.build_subgraph(user_id)
        candidates = []
        for node_id in graph.nodes():
            degree = graph.degree(node_id)
            node_data = graph.nodes[node_id]
            if degree <= 2:  # Low connectivity
                candidates.append({
                    "node_id": node_id,
                    "entity_type": node_data.get("type", ""),
                    "entity_name": node_data.get("name", ""),
                    "degree": degree,
                    "frequency": node_data.get("frequency", 1),
                })
        return sorted(candidates, key=lambda x: x["degree"])
