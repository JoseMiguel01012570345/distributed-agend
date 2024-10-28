from backend.server_ref import ServerReference
from frontend.auth_page import AuthPage
from argparse import ArgumentParser

parser = ArgumentParser()
parser.add_argument('-ip',default='127.0.0.1',help='Ip de la red al que se desea conectar')

args = parser.parse_args()

ref = ServerReference(args.ip)
page = AuthPage(ref)