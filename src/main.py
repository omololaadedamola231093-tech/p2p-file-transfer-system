"""
P2P File Transfer System - Main Demo
"""

from src.core.node import DataPeerNode, MetadataTrackerNode
from src.core.file_metadata import FileMetadata

def main():
    print("=" * 60)
    print("P2P FILE TRANSFER SYSTEM DEMO")
    print("=" * 60)
    
    # Create tracker
    tracker = MetadataTrackerNode("TRACKER-01", "tracker.local")
    tracker.connect()
    
    # Create peers
    peer1 = DataPeerNode("PEER-01", "peer1.local", bandwidth=10.0)
    peer2 = DataPeerNode("PEER-02", "peer2.local", bandwidth=50.0)
    
    peer1.register_with_tracker(tracker)
    peer2.register_with_tracker(tracker)
    
    peer1.connect()
    peer2.connect()
    
    print("✅ Network created: 2 peers + 1 tracker")
    
    # Share a file
    file_data = b"Hello P2P World! " * 20
    file_meta = peer1.share_file(file_data, "hello.txt")
    print(f"✅ File shared: {file_meta}")
    
    # Find the file
    peers = tracker.find_peers(file_meta.file_hash)
    print(f"✅ Found {len(peers)} peers with the file")
    
    # Get a chunk
    chunk = peer1._serve_chunk(file_meta.file_hash, 0)
    if chunk:
        print(f"✅ Retrieved chunk: {len(chunk.data)} bytes")
        if chunk.verify():
            print("✅ Chunk verified!")
    
    print("=" * 60)
    print("DEMO COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    main()
