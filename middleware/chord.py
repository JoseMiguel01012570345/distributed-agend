import json
import time
import socket
from enum import Enum
from threading import Thread
from middleware.hashers import GetHasher
from utils import *

BUFFER_SIZE = 1024
class ChordOperations(Enum):
    
    FIND_SUCCESSOR = 1
    FIND_PREDECESSOR = 2
    GET_SUCCESSOR = 3
    GET_PREDECESSOR = 4
    NOTIFY = 5
    CHECK_PREDECESSOR = 6
    CHECK_SUCCESSOR = 7
    CLOSEST_PRECEDING_FINGER = 8

class ChordNodeReference:
    
    """
    the reference to one chord node
    """
    
    def __init__(self,ip,port,key_name):
        self._id = key_name
        self._ip = ip
        self._port = port
    
    @property
    def ID(self):
        return self._id
    
    @property
    def IP(self):
        return self._ip
    
    @property
    def PORT(self):
        return self._port
    
    @property
    def Successor(self):
        response = self._send_data(ChordOperations.GET_SUCCESSOR.value).split(',')
        return ChordNodeReference(response[0],int(response[1]),int(response[2]))
    
    @property
    def Predecessor(self):
        response = self._send_data(ChordOperations.GET_PREDECESSOR.value).split(',')
        return ChordNodeReference(response[0],int(response[1]),int(response[2]))
        
    def _send_data(self,operation,data=None):
        
        json_data = json.dumps(f'{operation},{data}')
        
        try:
            client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            client.connect((self._ip,self._port))
            client.sendall(json_data.encode('utf-8'))
            response = client.recv(BUFFER_SIZE).decode()
            
            if len(response) > 0: 
                return json.loads(response)

            raise Exception( 'empty response' )
            
        except Exception as ex:
        
            print(f'Error: {ex}')
            exit(0)
    
    def find_successor(self,key):
        response = self._send_data(ChordOperations.FIND_SUCCESSOR.value , key ).split(',')
        return ChordNodeReference(response[0],int(response[1]),int(response[2]))
    
    def find_predecessor(self,key):
        response = self._send_data( ChordOperations.FIND_PREDECESSOR.value , key).split(',')
        return ChordNodeReference(response[0],int(response[1]),int(response[2]))
    
    def notify(self,node):
        self._send_data(ChordOperations.NOTIFY.value , f'{node.IP},{node.PORT},{node.ID}')
    
    def check_predecessor(self):
        response = self._send_data(ChordOperations.CHECK_PREDECESSOR.value)
        return response
    
    def check_successor(self):
        response = self._send_data(ChordOperations.CHECK_SUCCESSOR.value)
        return response
    
    def closest_preceding_finger(self,key):
        response = self._send_data( ChordOperations.CLOSEST_PRECEDING_FINGER.value , str(key) ).split(',')
        return ChordNodeReference(response[0],int(response[1]),int(response[2]))
    
    def __str__(self):
        return f'{self._ip},{self._port},{self._id}'
    
    def __repr__(self):
        return str(self)

class ChordNode:
    
    """
    a node of a chord ring
    """
    
    def __init__(self,ip,port=8001,hasher_function=GetHasher(4) ):
        
        function , bits = hasher_function
        self._memory_bits = bits
        self._max_size = 2 ** bits
        self._id = function.hash(ip)
        self._ip = ip
        self._port = port
        self._ref = ChordNodeReference(ip,port,self._id)
        self._nodes_known = [self._ref]
        self._successor = self._ref
        self._predecessor = None
        self._finger_table = [self._ref] * self._memory_bits
        self._next = 0
        
        Thread(target=self.start_server,daemon=True).start()
        Thread(target=self.stabilize,daemon=True).start()
        Thread(target=self.check_predecessor,daemon=True).start()
        Thread(target=self.fix_finger_table,daemon=True).start()
    
    @property
    def ID(self):
        return self._id
    
    @property
    def PORT(self):
        return self._port
    
    @property
    def IP(self):
        return self._ip
    
    @property
    def Successor(self):
        return self._successor
    
    @property
    def Predecessor(self):
        return self._predecessor
    
    def _inbettwen(self,key,start,end):
        
        """
        returns true if key belongs to (start,end]
        """
        
        if start < end:
            return start < key and key <= end
        
        return start < key or key <= end
    
    def closest_preceding_finger(self,key):
        
        for i in range(self._memory_bits - 1, -1 ,-1):
            if self._finger_table[i] and self._inbettwen(self._finger_table[i].ID,self._id,key):
                return self._finger_table[i]

        return self._ref
    
    def find_predecessor(self,key):
        node = self
        while self._successor and not self._inbettwen(key,self._id,self._successor.ID):
            node = node.closest_preceding_finger(key)

        return node
    
    def find_successor(self,key):
        
        if not self._successor:
            return self._ref
        
        node = self.find_predecessor(key)
        return node.Successor
    
    def join(self,node):
        
        if node:
            self._predecessor = None
            self._successor = node.find_successor(self._id)
            self._successor.notify(self._ref)

        else:
            self._successor = self._ref
            self._predecessor = None

        pass
    
    def stabilize(self):
        
        while True:
            try:
                
                if not self._successor.ID == self._id:
                    
                    x = self._successor.Predecessor
                    
                    if not x.ID == self._id:
                        if x and self._inbettwen(x.ID,self._id,self._successor.ID):
                            self._successor = x

                        self._successor.notify(self._ref)

                    if not self._predecessor: # revisar esta condicion para asegurar la integridad de chord
                    
                        node = self._ref
                    
                        while not self._inbettwen(self._id,node.ID,self._successor.ID):
                            node = node.Successor

                        self._predecessor = node
                        self._successor.notify(node)

                elif self._predecessor:
                    node = self._predecessor
                    while not self._inbettwen(self._id,self._predecessor.ID,node.ID):
                        node = node.Predecessor

                    self._successor = node
                    self.notify(node)

            except Exception as ex:
                print(f'Error while stabilzing: {ex}')

            print(f'successor {self._successor} ----- predecessor {self._predecessor}')
            time.sleep(10)
    
    def notify(self,node):

        if node.ID == self._id:
            pass

        if not self._predecessor or self._inbettwen(node.ID,self._predecessor.ID,self._id):
            self._predecessor = node
    
    def fix_finger_table(self):
        
        while True:
        
            for i in range(self._memory_bits):
                key = (self._id + 2 ** i) % self._max_size
                self._finger_table[i] = self.find_successor(key)

            time.sleep(10)
    
    def check_successor(self):
        
        if self._successor:
            response = self._successor.check_successor()
            
            if response == '[Errno 111] Connection refused':
                return False
            
            return True
        
        return False
    
    def check_predecessor(self):
        while True:
            try:
                if self._predecessor:
                    response = self._predecessor.check_predecessor()
                    if response == '[Errno 111] Connection refused':
                        self._predecessor = None

            except Exception as e:
                self._predecessor = None

            time.sleep(10)
    
    def start_server(self):
        server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
        server.bind((self._ip,self._port))
        server.listen(10)
        
        while True:
            
            time.sleep(.05)
            
            conn , addr = server.accept()
            json_data = conn.recv(BUFFER_SIZE).decode()
            data = json.loads(json_data).split(',')
            option = int(data[0])
            data_resp = None
            
            if option == ChordOperations.FIND_SUCCESSOR.value:
                key = int(data[1])
                data_resp = self.find_successor(key)

            elif option == ChordOperations.FIND_PREDECESSOR.value:
                key = int(data[1])
                data_resp = self.find_predecessor(key)

            elif option == ChordOperations.GET_SUCCESSOR.value:
                data_resp = self._successor if self._successor else self._ref

            elif option == ChordOperations.GET_PREDECESSOR.value:
                data_resp = self._predecessor if self._predecessor else self._ref

            elif option == ChordOperations.NOTIFY.value:
                key = int(data[3])
                ip = data[1]
                port = int(data[2])
                self.notify( ChordNodeReference(ip,port,key) )

            elif option == ChordOperations.CHECK_PREDECESSOR.value:
                pass

            elif option == ChordOperations.CLOSEST_PRECEDING_FINGER.value:
                key = int(data[1])
                data_resp = self.closest_preceding_finger(key)

            if data_resp:
                json_response = json.dumps(f'{data_resp.IP},{data_resp.PORT},{data_resp.ID}')
                response = json_response.encode('utf-8')
                conn.sendall(response)

            conn.close()
