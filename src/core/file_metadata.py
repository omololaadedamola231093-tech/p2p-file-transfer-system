import hashlib
from functools import total_ordering
from .chunk_data import ChunkData

@total_ordering
class FileMetadata:
    DEFAULT_CHUNK_SIZE = 1024 * 1024  # 1MB chunks
    
    def __init__(self, filename: str, data: bytes, chunk_size: int = DEFAULT_CHUNK_SIZE):
        if not filename:
            raise ValueError("filename must be non-empty")
        self._filename = filename
        self._size_bytes = len(data)
        self._chunk_size = chunk_size
        self._chunk_count = (len(data) + chunk_size - 1) // chunk_size
        self._file_hash = hashlib.sha256(data).hexdigest()
        self._chunks = self._create_chunks(data)
    
    def _create_chunks(self, data):
        chunks = []
        for i in range(self._chunk_count):
            start = i * self._chunk_size
            end = min(start + self._chunk_size, len(data))
            chunks.append(ChunkData(self._file_hash, i, data[start:end]))
        return chunks
    
    @property
    def filename(self):
        return self._filename
    
    @property
    def size_bytes(self):
        return self._size_bytes
    
    @property
    def file_hash(self):
        return self._file_hash
    
    @property
    def chunk_count(self):
        return self._chunk_count
    
    @property
    def chunks(self):
        return self._chunks.copy()
    
    def __eq__(self, other):
        if isinstance(other, FileMetadata):
            return self._file_hash == other._file_hash
        return NotImplemented
    
    def __lt__(self, other):
        if isinstance(other, FileMetadata):
            return self._size_bytes < other._size_bytes
        return NotImplemented
    
    def __hash__(self):
        return hash(self._file_hash)
    
    def __str__(self):
        return f"File: {self._filename} ({self._size_bytes} bytes, {self._chunk_count} chunks)"
