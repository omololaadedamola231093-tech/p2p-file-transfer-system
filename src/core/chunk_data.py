import hashlib

class ChunkData:
    def __init__(self, file_hash: str, chunk_index: int, data: bytes):
        if not file_hash:
            raise ValueError("file_hash must be non-empty")
        if chunk_index < 0:
            raise ValueError("chunk_index must be non-negative")
        self._file_hash = file_hash
        self._chunk_index = chunk_index
        self._data = data
        self._checksum = hashlib.sha256(data).hexdigest()
    
    @property
    def file_hash(self):
        return self._file_hash
    
    @property
    def chunk_index(self):
        return self._chunk_index
    
    @property
    def data(self):
        return self._data
    
    @property
    def checksum(self):
        return self._checksum
    
    def verify(self) -> bool:
        computed = hashlib.sha256(self._data).hexdigest()
        if computed != self._checksum:
            from ..exceptions.p2p_exceptions import ChecksumMismatchError
            raise ChecksumMismatchError(
                self._file_hash, self._chunk_index,
                self._checksum, computed
            )
        return True
    
    def __eq__(self, other):
        if not isinstance(other, ChunkData):
            return NotImplemented
        return (self._file_hash == other._file_hash and 
                self._chunk_index == other._chunk_index)
    
    def __hash__(self):
        return hash((self._file_hash, self._chunk_index))
