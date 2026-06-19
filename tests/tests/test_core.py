import pytest
from src.core.chunk_data import ChunkData
from src.core.file_metadata import FileMetadata
from src.core.node import DataPeerNode, MetadataTrackerNode
from src.core.swarm import Swarm
from src.exceptions.p2p_exceptions import ChecksumMismatchError, DuplicateFileError

@pytest.fixture
def sample_data():
    return b"Test data for P2P system!"

def test_chunk_creation():
    chunk = ChunkData("abc123", 0, b"Hello")
    assert chunk.file_hash == "abc123"
    assert chunk.chunk_index == 0
    assert chunk.data == b"Hello"
    assert len(chunk.checksum) == 64

def test_chunk_verification():
    chunk = ChunkData("abc123", 0, b"Hello")
    assert chunk.verify() is True

def test_chunk_corruption():
    chunk = ChunkData("abc123", 0, b"Hello")
    # Simulate corruption by creating new chunk with different data
    corrupted = ChunkData("abc123", 0, b"World")
    with pytest.raises(ChecksumMismatchError):
        corrupted.verify()

def test_file_creation(sample_data):
    meta = FileMetadata("test.txt", sample_data)
    assert meta.filename == "test.txt"
    assert meta.size_bytes == len(sample_data)
    assert len(meta.file_hash) == 64

def test_file_chunking():
    data = b"x" * (FileMetadata.DEFAULT_CHUNK_SIZE + 100)
    meta = FileMetadata("large.txt", data)
    assert meta.chunk_count == 2

def test_file_equality(sample_data):
    meta1 = FileMetadata("f1.txt", sample_data)
    meta2 = FileMetadata("f2.txt", sample_data)
    meta3 = FileMetadata("f3.txt", b"Different")
    assert meta1 == meta2
    assert meta1 != meta3

def test_swarm_add_peer():
    swarm = Swarm("abc123")
    peer = DataPeerNode("P1", "local")
    swarm.add_peer(peer)
    assert len(swarm) == 1
    assert peer in swarm

def test_swarm_contains():
    swarm = Swarm("abc123")
    peer = DataPeerNode("P1", "local")
    swarm.add_peer(peer)
    assert "P1" in swarm

def test_share_file():
    peer = DataPeerNode("P1", "local")
    meta = peer.share_file(b"Hello", "test.txt")
    assert meta.file_hash in peer._local_files  # Note: accessing private for test

def test_tracker_register():
    tracker = MetadataTrackerNode("T1", "local")
    peer = DataPeerNode("P1", "local")
    meta = peer.share_file(b"Hello", "test.txt")
    tracker.register_peer(peer)
    tracker.register_file(meta.file_hash, peer)
    found = tracker.find_peers(meta.file_hash)
    assert len(found) >= 1

def test_tracker_find_peers():
    tracker = MetadataTrackerNode("T1", "local")
    peer1 = DataPeerNode("P1", "local", bandwidth=100.0)
    peer2 = DataPeerNode("P2", "local", bandwidth=50.0)
    meta = peer1.share_file(b"Hello", "test.txt")
    peer2.share_file(b"Hello", "test.txt")
    tracker.register_peer(peer1)
    tracker.register_peer(peer2)
    tracker.register_file(meta.file_hash, peer1)
    tracker.register_file(meta.file_hash, peer2)
    found = tracker.find_peers(meta.file_hash)
    assert len(found) >= 2
    # Should be sorted by bandwidth
    assert found[0].bandwidth >= found[-1].bandwidth

def test_node_connect():
    node = DataPeerNode("P1", "local")
    assert not node._online  # accessing private for test
    node.connect()
    assert node._online

def test_node_str():
    node = DataPeerNode("P1", "local")
    assert "P1" in str(node)
