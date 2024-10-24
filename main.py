import argparse
from chord import NodeReference,Node

parser = argparse.ArgumentParser()
parser.add_argument('-ip',help='Ip del nodo')
parser.add_argument('--port','-p',help='Puerto del nodo',default=8001)
parser.add_argument('-ip2',help='Ip del nodo al cual unirse')
parser.add_argument('--port2','-p2',help='Puerto del nodo al cual unirse')

args = parser.parse_args()

ip = args.ip
port = int(args.port)
ip2 = args.ip2
port2 = int(args.port2) if args.port2 else None

ref = None

if ip2 and port2:
    ref = NodeReference((ip2,port2))
    pass
if ip and port:
    node = Node((ip,port))
    if ref:
        node.join(ref)
        pass
    pass
else:
    node = Node(('127.0.0.1',8001))
    # ref = NodeReference(('127.0.0.1',8001))
    # node.join(ref)
    pass

while True:
    pass