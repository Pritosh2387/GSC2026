"""
routes/network.py — Network propagation graph endpoints.

GET  /api/network/trace/{media_id} — Trace propagation graph for a specific media
GET  /api/network/graph            — Return full piracy propagation network
POST /api/network/analyze          — Run coordinated-network detection on provided data
"""

from typing import Optional

from fastapi import APIRouter, Depends, Path, Body

from auth import get_current_user
from services import network_service
from utils.logging_utils import get_logger

router = APIRouter(prefix="/api/network", tags=["Network Propagation"])
logger = get_logger("piraksha.routes.network")


@router.get(
    "/trace/{media_id}",
    summary="Trace propagation graph for a media item",
    description=(
        "Return a node-edge graph showing which Telegram channels have been "
        "detected sharing the specified media content."
    ),
)
async def trace_media(
    media_id: str = Path(..., description="Content name or media ID to trace"),
    current=Depends(get_current_user),
):
    """
    **Trace** the propagation network for a given media ID.

    Returns a graph with:
    - `nodes`: channels and media content nodes
    - `edges`: detected piracy relationships
    - `total_violations`: count of violation events
    """
    result = await network_service.get_propagation_trace(media_id)
    logger.info(
        f"Propagation trace for '{media_id}': "
        f"{result['total_violations']} violation(s)"
    )
    return result


@router.get(
    "/graph",
    summary="Return full piracy network graph",
    description=(
        "Aggregate all stored alerts into a complete propagation network graph "
        "suitable for visualization (D3.js, Cytoscape, etc.)."
    ),
)
async def full_network_graph(current=Depends(get_current_user)):
    """
    **Return** the full piracy network graph built from all detected alerts.

    Each node is either a Channel or a Content item.
    Each edge represents a confirmed piracy detection event.
    """
    graph = await network_service.get_full_network_graph()
    logger.info(
        f"Network graph returned: {graph['node_count']} nodes, "
        f"{graph['edge_count']} edges"
    )
    return graph


@router.post(
    "/analyze",
    summary="Run coordinated-network analysis",
    description=(
        "Provide fingerprint maps and account upload logs. "
        "PIRAKSHA detects coordinated upload networks and similarity clusters."
    ),
)
async def network_analysis(
    payload: dict = Body(
        ...,
        examples={
            "default": {
                "summary": "Two-user coordinated upload example",
                "value": {
                    "fingerprint_map": {
                        "user_A": [0.1, 0.2, 0.3],
                        "user_B": [0.1, 0.2, 0.31],
                    },
                    "account_logs": {
                        "user_A": [1714300000.0, 1714300060.0],
                        "user_B": [1714300005.0, 1714300065.0],
                    },
                },
            }
        },
    ),
    current=Depends(get_current_user),
):
    """
    **Analyze** a network of accounts for coordinated piracy behaviour.

    Detects:
    - Content similarity clusters (near-identical uploads across accounts)
    - Temporal coordination (uploads within 60 s of each other)
    """
    fp_map = payload.get("fingerprint_map", {})
    account_logs = payload.get("account_logs", {})
    result = network_service.run_network_analysis(fp_map, account_logs)
    logger.info(
        f"Network analysis: {len(result['clusters'])} cluster(s), "
        f"{len(result['coordinated_accounts'])} coordinated account(s)"
    )
    return result
