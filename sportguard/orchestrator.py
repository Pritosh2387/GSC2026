from .fingerprinting.engine import FingerprintingEngine, ContentType
from .watermarking.embedder import WatermarkEmbedder
from .attribution.workflow import AttributionWorkflow
from .attribution.response import ResponseProtocol, OffenderType
from .network.graph import PiracyKnowledgeGraph
from .network.detection import NetworkDetectionSystem
from .network.protocol import NetworkDismantlingProtocol
from .network.predictive import PredictiveReplacementModel

class SportGuardOrchestrator:
    def __init__(self, gemini_api_key: str = None):
        self.fingerprint_engine = FingerprintingEngine(gemini_api_key)
        self.watermark_engine = WatermarkEmbedder()
        self.attribution_workflow = AttributionWorkflow()
        self.response_protocol = ResponseProtocol("./sportguard/commercial_leakers")
        
        # Feature 5: Network Detection
        self.kg = PiracyKnowledgeGraph()
        self.network_detector = NetworkDetectionSystem(self.kg)
        self.dismantler = NetworkDismantlingProtocol("./sportguard/network_evidence")
        self.predictor = PredictiveReplacementModel()

    def register_content(self, content_path: str, content_type: ContentType):
        """
        Content Registration Pipeline.
        """
        print(f"[*] Starting Registration for: {content_path}")
        fingerprint = self.fingerprint_engine.generate_fingerprint(content_path, content_type)
        print(f"[+] Fingerprint Generated (512-dim). Size: {len(fingerprint)}")
        # In real case, save to vector db
        return fingerprint

    def protect_stream(self, frames, audio, user_info, sr):
        """
        Applies forensic watermarks for a specific user session.
        """
        print(f"[*] Protecting stream for User: {user_info['user_id']}")
        w_frames, w_audio, jitters = self.watermark_engine.apply_watermark(frames, audio, user_info, sr)
        
        # Update Knowledge Graph
        self.kg.add_node(user_info['user_id'], "User")
        self.kg.add_node(user_info['device_id'], "Device")
        self.kg.add_relationship(user_info['user_id'], user_info['device_id'], "OwnsDevice")
        
        print(f"[+] Forensic Watermarks embedded. Graph updated.")
        return w_frames, w_audio, jitters

    def handle_leak_detection(self, suspect_video, suspect_audio, offender_type: OffenderType):
        """
        End-to-end leak detection and attribution workflow.
        """
        print("[!] Leak Detected! Initiating forensic attribution...")
        attribution_data = self.attribution_workflow.attribute_leak(suspect_video, suspect_audio)
        
        user_id = attribution_data.get("user_hash", "Unknown")
        
        print(f"[+] Leak attributed to User Hash: {user_id}")
        response = self.response_protocol.execute_response(user_id, offender_type, attribution_data)
        
        return response

    def run_network_analysis(self, fingerprint_map, account_logs):
        """
        Advanced Pattern Recognition and Network Dismantling.
        """
        print("[*] Running Graph Analytics & Network Detection...")
        
        # 1. Similarity Clusters
        clusters = self.network_detector.find_content_similarity_clusters(fingerprint_map)
        
        # 2. Temporal Coordination
        coordinated = self.network_detector.analyze_temporal_coordination(account_logs)
        
        if clusters or coordinated:
            print(f"[!] COORDINATED NETWORK DETECTED: {len(clusters)} similarity clusters found.")
            for i, cluster in enumerate(clusters):
                self.dismantler.initiate_coordinated_takedown(f"NET_{i}", cluster)
                self.dismantler.generate_evidence_package(f"NET_{i}", {}, {"cluster": cluster})
                
        return {"clusters": clusters, "coordinated": coordinated}
