from middleware import *
from sys import argv

try:
    ip = argv[1]
    port = int(argv[2])
    ref = None
    
    if len(argv) >= 5:
        
        ip_ref = argv[3]
        port_ref = int(argv[4])
        hash_func , memory_bits = GetHasher(4)
        hash_ = hash_func.hash(ip_ref)
        ref = ChordNodeReference( ip_ref, port_ref , hash_ )
        
    node = ChordNode( ip , port )
    if ref:
        node.join(ref)
        
except Exception as ex:
    # node = ChordNode('127.0.0.2',8002)
    # node.join(ChordNodeReference('127.0.0.1',8001,GetHasher(4)[0].hash('127.0.0.1')))
    node = ChordNode('127.0.0.1')
    

while True:
    pass
