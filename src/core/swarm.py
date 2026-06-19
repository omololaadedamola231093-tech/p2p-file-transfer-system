from typing import Set, Iterator
from .node import DataPeerNode

class Swarm:
    def __init__(self, file_hash: str):
        if not file_hash:
            raise ValueError("file_hash must be non-empty")
        self._file_hash = file_hash
        self._peers: Set[DataPeerNode] = set()
    
    @property
    def file_hash(self):
        return self._file_hash
    
    @property
    def peers(self):
        return self._peers.copy()
    
    def add_peer(self, peer: DataPeerNode):
        self._peers.add(peer)
    
    def remove_peer(self, peer: DataPeerNode):
        self._peers.discard(peer)
    
    def __len__(self):
        return len(self._peers)
    
    def __contains__(self, item):
        if isinstance(item, DataPeerNode):
            return item in self._peers
        if isinstance(item, str):
            return any(p.node_id == item for p in self._peers)
        return False
    
    def __iter__(self):
        return iter(self._peers)
    
    def __str__(self):
        return f"Swarm: {len(self._peers)} peer(s)"
