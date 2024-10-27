import argparse
from chord import NodeReference,Node
from backend import Server
from flask import Flask

parser = argparse.ArgumentParser()
parser.add_argument('-ip',help='Ip del nodo',default='127.0.0.1')
parser.add_argument('--port','-p',help='Puerto del nodo',default=8001)
parser.add_argument('--ui',help='Interfaz de usuario',default=None)

args = parser.parse_args()

ip = args.ip
port = int(args.port)
ui = True if args.ui else False

server = Server((ip,port),ui)
# server = Server((ip,8001),True)

while True:
    pass
