import networkx as nx
from typing import List, Dict, Any
import json

class PiracyKnowledgeGraph:
    def __init__(self):
        self.graph = nx.MultiGraph()

    def add_node(self, node_id: str, node_type: str, metadata: Dict[str, Any] = None):
        """
        Types: User, Device, IP, Payment, ContentCollection
        """
        self.graph.add_node(node_id, type=node_type, **(metadata or {}))

    def add_relationship(self, node_a: str, node_b: str, rel_type: str, metadata: Dict[str, Any] = None):
        """
        Relationships: SharedIP, CommonDevice, CoordinatedTiming, SameMonetization
        """
        self.graph.add_edge(node_a, node_b, relationship=rel_type, **(metadata or {}))

    def get_connected_clusters(self) -> List[List[str]]:
        """Identify potentially coordinated networks using graph clustering."""
        # Convert MultiGraph to Graph for connectivity analysis
        simple_graph = nx.Graph(self.graph)
        return list(nx.connected_components(simple_graph))

    def export_graph_json(self, filepath: str):
        data = nx.node_link_data(self.graph)
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=4)
            
    def get_node_details(self, node_id: str):
        return self.graph.nodes[node_id]
