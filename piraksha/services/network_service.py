"""
services/network_service.py — Propagation graph and network-detection helpers.

Wraps the existing SportGuard PiracyKnowledgeGraph, NetworkDetectionSystem,
and NetworkDismantlingProtocol.
"""

from typing import Optional
from config import settings
from database import get_db
from utils.logging_utils import get_logger

logger = get_logger("piraksha.network_service")


def _build_knowledge_graph():
    """Instantiate the PiracyKnowledgeGraph from the SportGuard module."""
    from sportguard.network.graph import PiracyKnowledgeGraph
    return PiracyKnowledgeGraph()


async def get_propagation_trace(media_id: str) -> dict:
    """
    Return the propagation trace for a given media_id.

    Looks up detection history in MongoDB and builds a graph structure.
    """
    db = get_db()
    nodes = []
    edges = []

    if db is not None:
        # Gather all alerts/detections referencing this media
        cursor = db.alerts.find({"matched_content": {"$regex": media_id, "$options": "i"}})
        async for doc in cursor:
            doc["_id"] = str(doc["_id"])
            channel = doc.get("channel_name", "unknown")
            nodes.append({"id": channel, "type": "Channel", "label": channel})
            nodes.append({"id": media_id, "type": "Media", "label": media_id})
            edges.append({
                "source": channel,
                "target": media_id,
                "relation": "shared_pirated_copy",
                "similarity": doc.get("similarity_score", 0),
            })

    # Deduplicate nodes by id
    seen = set()
    unique_nodes = []
    for n in nodes:
        if n["id"] not in seen:
            seen.add(n["id"])
            unique_nodes.append(n)

    return {
        "media_id": media_id,
        "nodes": unique_nodes,
        "edges": edges,
        "total_violations": len(edges),
    }


async def get_full_network_graph() -> dict:
    """
    Return the full piracy propagation network built from all stored detections.
    """
    db = get_db()
    nodes = []
    edges = []

    if db is not None:
        cursor = db.alerts.find().sort("created_at", -1).limit(200)
        async for doc in cursor:
            channel = doc.get("channel_name", "Unknown")
            content = doc.get("matched_content", "Unknown")
            nodes.append({"id": channel, "type": "Channel"})
            nodes.append({"id": content, "type": "Content"})
            edges.append({
                "source": channel,
                "target": content,
                "relation": "piracy_detected",
                "score": doc.get("similarity_score", 0),
            })

    # Deduplicate
    seen = set()
    unique_nodes = []
    for n in nodes:
        k = n["id"]
        if k not in seen:
            seen.add(k)
            unique_nodes.append(n)

    return {
        "nodes": unique_nodes,
        "edges": edges,
        "node_count": len(unique_nodes),
        "edge_count": len(edges),
    }


def run_network_analysis(fingerprint_map: dict, account_logs: dict) -> dict:
    """
    Run the full SportGuard network-analysis pipeline.

    Args:
        fingerprint_map: {user_id: numpy_array}
        account_logs: {user_id: [unix_timestamps]}
    """
    import numpy as np
    from sportguard.network.graph import PiracyKnowledgeGraph
    from sportguard.network.detection import NetworkDetectionSystem

    kg = PiracyKnowledgeGraph()
    detector = NetworkDetectionSystem(kg)

    # Convert lists to numpy arrays
    fp_map_np = {
        uid: np.array(fp, dtype=np.float32)
        for uid, fp in fingerprint_map.items()
    }

    clusters = detector.find_content_similarity_clusters(fp_map_np)
    coordinated = detector.analyze_temporal_coordination(account_logs)

    logger.info(
        f"Network analysis done: {len(clusters)} cluster(s), "
        f"{len(coordinated)} coordinated account(s)"
    )
    return {"clusters": clusters, "coordinated_accounts": coordinated}
