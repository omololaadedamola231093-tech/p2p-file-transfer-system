class P2PError(Exception):
    pass

class ChecksumMismatchError(P2PError):
    def __init__(self, file_hash: str, chunk_idx: int, expected: str, received: str):
        self.file_hash = file_hash
        self.chunk_idx = chunk_idx
        self.expected = expected
        self.received = received
        super().__init__(
            f"Chunk {chunk_idx} checksum mismatch: {expected[:8]}... != {received[:8]}..."
        )

class PeerNotFoundError(P2PError):
    def __init__(self, peer_id: str):
        self.peer_id = peer_id
        super().__init__(f"Peer '{peer_id}' not found")

class DuplicateFileError(P2PError):
    def __init__(self, file_hash: str, filename: str):
        self.file_hash = file_hash
        self.filename = filename
        super().__init__(f"File '{filename}' already exists")
