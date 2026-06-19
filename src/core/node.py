from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from datetime import datetime

class Node(ABC):
    def __init__(self, node_id: str, address: str):
        if not node_id:
            raise ValueError("node_id must be non-empty")
        self._node_id = node_id
        self._address = address
        self._online = False
        self._message_log = []
    
    @property
    def node_id(self):
        return self._node_id
    
    @abstractmethod
    def send(self, message: dict) -> dict:
        pass
    
    @abstractmethod
    def receive(self) -> dict:
        pass
    
    def connect(self):
        self._online = True
    
    def disconnect(self):
        self._online = False
    
    def __str__(self):
        status = "Online" if self._online else "Offline"
        return f"{self.__class__.__name__}[{self._node_id}] ({status})"


class DataPeerNode(Node):
    def __init__(self, node_id: str, address: str, bandwidth: float = 100.0):
        super().__init__(node_id, address)
        self._bandwidth = bandwidth
        self._local_files = {}
        self._chunk_cache = {}
        self._tracker = None
    
    @property
    def bandwidth(self):
        return self._bandwidth
    
    def share_file(self, data: bytes, filename: str):
        from .file_metadata import FileMetadata
        meta = FileMetadata(filename, data)
        self._local_files[meta.file_hash] = meta
        self._chunk_cache[meta.file_hash] = {}
        for chunk in meta.chunks:
            self._chunk_cache[meta.file_hash][chunk.chunk_index] = chunk
        if self._tracker:
            self._tracker.register_file(meta.file_hash, self)
        return meta
    
    def register_with_tracker(self, tracker):
        self._tracker = tracker
        tracker.register_peer(self)
    
    def _serve_chunk(self, file_hash: str, chunk_idx: int):
        if file_hash in self._chunk_cache:
            return self._chunk_cache[file_hash].get(chunk_idx)
        return None
    
    def send(self, message: dict) -> dict:
        if message.get('type') == 'request_chunk':
            chunk = self._serve_chunk(
                message.get('file_hash'),
                message.get('chunk_idx')
            )
            return {'status': 'success', 'chunk_data': chunk}
        return {'status': 'unknown'}
    
    def receive(self) -> dict:
        return {'status': 'ok'}


class MetadataTrackerNode(Node):
    def __init__(self, node_id: str, address: str):
        super().__init__(node_id, address)
        self._swarm_registry = {}
        self._peer_registry = {}
    
    def register_peer(self, peer):
        self._peer_registry[peer.node_id] = peer
    
    def register_file(self, file_hash: str, peer):
        from .swarm import Swarm
        if file_hash not in self._swarm_registry:
            self._swarm_registry[file_hash] = Swarm(file_hash)
        self._swarm_registry[file_hash].add_peer(peer)
    
    def find_peers(self, file_hash: str, limit: int = 5):
        if file_hash not in self._swarm_registry:
            return []
        swarm = self._swarm_registry[file_hash]
        peers = list(swarm.peers)
        peers.sort(key=lambda p: p.bandwidth, reverse=True)
        return peers[:limit]
    
    def send(self, message: dict) -> dict:
        if message.get('type') == 'find_peers':
            peers = self.find_peers(
                message.get('file_hash'),
                message.get('limit', 5)
            )
            return {'status': 'success', 'peers': [p.node_id for p in peers]}
        return {'status': 'unknown'}
    
    def receive(self) -> dict:
        return {'status': 'ok'}
