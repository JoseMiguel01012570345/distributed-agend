import socket
from chord.hashers import sha1_hash
from utils import set_json_data_to_send,get_data_from_json
from chord.chord_operations import Operation
import logging
from utils import Color

logging.basicConfig(level=logging.DEBUG,format='%(asctime)s [%(threadName)s] %(levelname)s: %(message)s')

BUFFER_SIZE = 2048

class NodeReference:
    
    def __init__(self,address,table_size=8,hasher=sha1_hash):
        self._host,self._port = address
        self._id = hasher(str(address),table_size)
        self._table_size = table_size
        pass
    
    @property
    def successor(self):
        successor = self._send_data(Operation.GET_SUCCESSOR.value,{})
        return NodeReference((successor['ip'],successor['port']),self._table_size)
    
    @property
    def predecessor(self):
        predecessor = self._send_data(Operation.GET_PREDECESSOR.value,{})
        if len(predecessor.keys()) == 0:
            return None
        return NodeReference((predecessor['ip'],predecessor['port']),self._table_size)
    
    @property
    def leader(self):
        leader = self._send_data(Operation.GET_LEADER.value,{})
        return NodeReference((leader['ip'],leader['port']),self._table_size)
    
    @property
    def id(self):
        return self._id
    
    @property
    def host(self):
        return self._host
    
    @property
    def port(self):
        return self._port

    def __str__(self):
        return f'ID: {self._id}, IP: {self._host}, PORT: {self._port}'

    def __repr__(self):
        return str(self)

    def _send_data(self,operation,data):
        try:
            _data = {'operation':operation,'data':data}
            json_data = set_json_data_to_send(_data)
            client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            client.connect((self._host,self._port))
            client.sendall(json_data)
            json_response = client.recv(BUFFER_SIZE)
            client.close()
            return get_data_from_json(json_response)
        except Exception as ex:
            return None
    
    def find_successor(self,key):
        successor = self._send_data(Operation.FIND_SUCCESSOR.value,{'id':key})
        return NodeReference((successor['ip'],successor['port']),self._table_size)
    
    def notify(self,node):
        self._send_data(Operation.NOTIFY.value,{'id':node.id,'ip':node.host,'port':node.port})
        pass
    
    def find_predecessor(self,key):
        predecessor = self._send_data(Operation.FIND_PREDECESSOR.value,{'id':key})
        if len(predecessor.keys()) == 0:
            return None      
        return NodeReference((predecessor['ip'],predecessor['port']),self._table_size)
    
    def closest_preceding_finger(self,key):
        finger = self._send_data(Operation.CLOSEST_PRECEDING_FINGER.value,{'id':key})
        if len(finger.keys()) == 0:
            return None
        return NodeReference((finger['ip'],finger['port']),self._table_size)
    
    def check_predecessor(self):
        if self._send_data(Operation.CHECK_PREDECESSOR.value,{}):
            return True
        return False
    
    def join(self,node):
        data = {'ip':node.host,'port':node.port}
        self._send_data(Operation.JOIN.value,data)
        pass
    
    def select_leader(self,node,start_id):
        data = {'leader_id':node.id,'ip':node.host,'port':node.port,'start':start_id}
        self._send_data(Operation.SELECT_LEADER.value,data)
        pass
    
    def notify_leader(self,node,start_id):
        data = {'ip':node.host,'port':node.port,'start':start_id}
        self._send_data(Operation.NOTIFY_LEADER.value,data)
        pass
    
    def store_data(self,data):
        self._send_data(Operation.STORE_DATA.value,data)
        pass
        
    pass
