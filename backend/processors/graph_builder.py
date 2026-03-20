"""Knowledge graph builder — creates medical concept graphs from documents."""

from __future__ import annotations

import logging
from typing import Any

import networkx as nx

from backend.extractors.base import MedicalDocument
from backend.processors.embedder import Embedder
from backend.db import supabase as db

log = logging.getLogger(__name__)


class KnowledgeGraphBuilder:
    """Build and maintain a per-user medical knowledge graph."""

    def __init__(self) -> None:
        self.embedder = Embedder()

    async def build_from_document(self, doc: MedicalDocument, user_id: str) -> nx.DiGraph:
        """Extract entities from a document and build/update the knowledge graph."""
        graph = nx.DiGraph()
        mm = doc.medical_metadata
        source_id = doc.id

        # Create nodes for all entity types
        entity_map: dict[str, str] = {}  # "type:name" -> node_id

        all_entities: list[tuple[str, list[str]]] = [
            ("imaging_modality", mm.imaging_modalities),
            ("anatomy", mm.anatomies),
            ("condition", mm.conditions),
            ("architecture", mm.architectures),
            ("dataset", mm.datasets),
            ("metric", mm.metrics),
            ("technique", mm.techniques),
            ("limitation", mm.limitations),
        ]

        for entity_type, entities in all_entities:
            for entity_name in entities:
                node_key = f"{entity_type}:{entity_name}"
                node_id = await self._upsert_node(user_id, entity_type, entity_name, source_id)
                entity_map[node_key] = node_id
                graph.add_node(node_id, type=entity_type, name=entity_name)

        # Create edges based on co-occurrence within the same paper
        # Architecture applied_to anatomy/condition
        for arch in mm.architectures:
            arch_key = f"architecture:{arch}"
            if arch_key not in entity_map:
                continue
            for anatomy in mm.anatomies:
                anat_key = f"anatomy:{anatomy}"
                if anat_key in entity_map:
                    await self._upsert_edge(
                        user_id, entity_map[arch_key], entity_map[anat_key],
                        "applied_to", source_id,
                    )
                    graph.add_edge(entity_map[arch_key], entity_map[anat_key], relationship="applied_to")

            for condition in mm.conditions:
                cond_key = f"condition:{condition}"
                if cond_key in entity_map:
                    await self._upsert_edge(
                        user_id, entity_map[arch_key], entity_map[cond_key],
                        "applied_to", source_id,
                    )

        # Technique applied_to architecture
        for tech in mm.techniques:
            tech_key = f"technique:{tech}"
            if tech_key not in entity_map:
                continue
            for arch in mm.architectures:
                arch_key = f"architecture:{arch}"
                if arch_key in entity_map:
                    await self._upsert_edge(
                        user_id, entity_map[tech_key], entity_map[arch_key],
                        "applied_to", source_id,
                    )

        # Modality used_for anatomy
        for mod in mm.imaging_modalities:
            mod_key = f"imaging_modality:{mod}"
            if mod_key not in entity_map:
                continue
            for anatomy in mm.anatomies:
                anat_key = f"anatomy:{anatomy}"
                if anat_key in entity_map:
                    await self._upsert_edge(
                        user_id, entity_map[mod_key], entity_map[anat_key],
                        "used_for", source_id,
                    )

        # Limitation limited_by architecture
        for lim in mm.limitations:
            lim_key = f"limitation:{lim}"
            if lim_key not in entity_map:
                continue
            for arch in mm.architectures:
                arch_key = f"architecture:{arch}"
                if arch_key in entity_map:
                    await self._upsert_edge(
                        user_id, entity_map[lim_key], entity_map[arch_key],
                        "limited_by", source_id,
                    )

        log.info("Built graph for doc %s: %d nodes, %d edges", doc.id[:8], graph.number_of_nodes(), graph.number_of_edges())
        return graph

    async def _upsert_node(
        self, user_id: str, entity_type: str, entity_name: str, source_id: str
    ) -> str:
        """Insert or update a semantic node, return its ID."""
        existing = db.select(
            "semantic_nodes",
            filters={"user_id": user_id, "entity_type": entity_type, "entity_name": entity_name},
            service=True,
        )
        if existing:
            node = existing[0]
            source_ids = node.get("source_ids") or []
            if source_id not in source_ids:
                source_ids.append(source_id)
            db.update("semantic_nodes", node["id"], {
                "frequency": (node.get("frequency") or 0) + 1,
                "source_ids": source_ids,
            }, service=True)
            return node["id"]

        # Generate embedding
        try:
            embedding = await self.embedder.embed(f"{entity_type}: {entity_name}")
        except Exception:
            embedding = None

        row = db.insert("semantic_nodes", {
            "user_id": user_id,
            "entity_type": entity_type,
            "entity_name": entity_name,
            "embedding": embedding,
            "source_ids": [source_id],
            "frequency": 1,
        }, service=True)
        return row["id"]

    async def _upsert_edge(
        self, user_id: str, source_node_id: str, target_node_id: str,
        relationship: str, source_paper_id: str,
    ) -> None:
        """Insert or update a semantic edge."""
        existing = db.select("semantic_edges", filters={
            "user_id": user_id,
            "source_node_id": source_node_id,
            "target_node_id": target_node_id,
            "relationship": relationship,
        }, service=True)
        if existing:
            edge = existing[0]
            paper_ids = edge.get("source_paper_ids") or []
            if source_paper_id not in paper_ids:
                paper_ids.append(source_paper_id)
            db.update("semantic_edges", edge["id"], {
                "weight": (edge.get("weight") or 1.0) + 1.0,
                "source_paper_ids": paper_ids,
            }, service=True)
        else:
            db.insert("semantic_edges", {
                "user_id": user_id,
                "source_node_id": source_node_id,
                "target_node_id": target_node_id,
                "relationship": relationship,
                "weight": 1.0,
                "source_paper_ids": [source_paper_id],
            }, service=True)
