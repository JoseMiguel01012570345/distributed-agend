"""
an implementation of a chord's ring node
"""

from threading import Thread,Lock
import socket
from chord.hashers import sha1_hash
from chord.chord_node_ref import NodeReference
from utils import get_data_from_json,set_json_data_to_send,inbettwen,Color
import logging
from chord.chord_operations import Operation
import time
from pathlib import Path
import os
import json


logging.basicConfig(level=logging.DEBUG,format='%(asctime)s [%(threadName)s] %(levelname)s: %(message)s')

BUFFER_SIZE = 2048

class Node:
    
    def __init__(self,address,table_size=8,hasher=sha1_hash):
        self._path = Path()
        self._host,self._port = address
        self._id =  hasher(str(address),table_size)
        self._predecessor = None
        self._ref = NodeReference(address,table_size,hasher)
        self._successor = self._ref
        self._table_size = table_size
        self._finger_table = [self._ref] * self._table_size
        self._request_handlers = self._init_handlers()
        self._leader = self._ref
        self._init_data_store()
        Thread(target=self.server,daemon=True,name=f'SERVER NODE {self._id}').start()
        Thread(target=self.logger,daemon=True,name=f'LOGGER NODE {self._id}').start()
        Thread(target=self.fix_finger_table,daemon=True,name=f'SERVER NODE {self._id}').start()
        Thread(target=self.stabilize,daemon=True,name=f'STABILIZER NODE {self._id}').start()
        Thread(target=self.check_predecessor,daemon=True,name=f'CHECK PREDECESSOR NODE {self._id}').start()
        Thread(target=self.discover_network,daemon=True,name=f'DISCOVER NETWORK NODE {self._id}').start()
        Thread(target=self.replicate_data,daemon=True,name=f'REPLICATE DATA NODE {self._id}').start()
        pass
    
    @property
    def successor(self):
        return self._successor
    
    @property
    def predecessor(self):
        return self._predecessor
    
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
    
    def _init_data_store(self):
        if not self._path.joinpath(f'data_{self._id}').exists():
            os.mkdir(f'data_{self._id}')
            file = self._path.joinpath(f'data_{self._id}').joinpath(f'{self._id}.json')
            f = open(str(file),'w')
            content = {'groups':{},'agends':{},'users':{},'events':{}}
            f.write(json.dumps(content))
            f.close()
            pass
        pass
    
    def _init_handlers(self):
        return {
            Operation.FIND_SUCCESSOR.value:self._handle_find_successor_request,
            Operation.NOTIFY.value:self._handle_notify_request,
            Operation.FIND_PREDECESSOR.value:self._hanlde_find_predecessor_request,
            Operation.GET_SUCCESSOR.value:self._handle_get_successor_request,
            Operation.GET_PREDECESSOR.value:self._handle_get_predecessor_request,
            Operation.CLOSEST_PRECEDING_FINGER.value:self._handle_closest_preceding_finger_request,
            Operation.CHECK_PREDECESSOR.value:self._handle_check_predecessor_request,
            Operation.JOIN.value:self._handle_join_request,
            Operation.SELECT_LEADER.value:self._handle_select_leader_request,
            Operation.NOTIFY_LEADER.value:self._handle_notify_leader_request,
            Operation.GET_LEADER.value:self._handle_get_leader_request,
            Operation.STORE_DATA.value:self._handle_store_data_request,
            Operation.FIND_USER.value:self._handle_find_user_request,
            Operation.GET_ALL_GROUPS.value:self._handle_get_groups_request
        }
    
    def find_user(self,username,password,start_id):
        path = self._path.joinpath(f'data_{self._id}')
        for file in path.iterdir():
            f = open(f'{file}','r')
            data = json.loads(f.read())
            f.close()
            if username in data['users'].keys():
                return {'status':data['users'][username] == password}
            pass
        if self._successor.id != self._id:
            try:
                return self._successor.find_user(username,password,start_id)
            except Exception as ex:
                return {'status':False}
            pass
        return {'status':False}
    
    def get_groups(self,start_id,current_groups={}):
        path = self._path.joinpath(f'data_{self._id}').joinpath(f'{self._id}.json')
        file = open(f'{path}','r')
        data = json.loads(file.read())
        file.close()
        for group in data['groups'].keys():
            current_groups[group] = data['groups'][group]
            pass
        try:
            return self._successor.get_groups(current_groups)
        except Exception as ex:
            return current_groups
        pass
    
    def delete_one_group(self,groupname,start_id):
        path = self._path.joinpath(f'data_{self._id}').joinpath(f'{self._id}.json')
        file  = open(f'{path}','r')
        data = json.loads(file.read())
        file.close()
        if groupname in data['groups'].keys():
            del data['groups'][groupname]
            pass
        file = open(f'{path}','w')
        file.write(json.dumps(data))
        file.close()
        try:
            self._successor.delete_one_group(groupname,start_id)
            pass
        except Exception as ex:
            pass
        pass
    
    def notify(self,node):
        if node.id == self._id:
            return
        if self._predecessor:
            self.discard_predecessor_data()
            pass
        self._predecessor = node
        if self._successor.id == self._id:
            self._successor = node
            pass
        pass
    
    def find_successor(self,key):
        if self._successor.id == self._id:
            return self._ref
        # if self._predecessor and self._successor.id == self._predecessor.id:
        #     if inbettwen(key,self._id,self._successor.id):
        #         return self._successor
        #     return self._ref
        node = self.find_predecessor(key)
        if node.id == self._id:
            return self._successor
        return node.successor
        
    def find_predecessor(self,key):
        try:
            if inbettwen(key,self._id,self._successor.id) or self._successor.id == self._id:
                return self._ref
            if self._successor.id == self._id:
                return self._ref
            node = self.closest_preceding_finger(key)
            # if self._predecessor and self._successor.id == self._predecessor.id:
                #     if inbettwen(key,self._id,self._successor.id):
            #         return self._ref
            #     return self._successor
            while not inbettwen(key,node.id,node.successor.id):
                node = node.closest_preceding_finger(key)
                pass
            return node
        except Exception as ex:
            return self._ref
        
    def closest_preceding_finger(self,key):
        for i in range(len(self._finger_table) - 1,-1,-1):
            if inbettwen(self._finger_table[i].id,self._id,key):
                return self._finger_table[i]
            pass
        return self._ref
    
    def fix_finger_table(self):
        while True:
            for i in range(self._table_size):
                try:
                    self._finger_table[i] = self.find_successor((self._id + 2**i) % 2**self._table_size)
                    pass
                except Exception as ex:
                    pass
                pass
            time.sleep(5)
            pass
        pass
    
    def join(self,node):
        self._successor = node.find_successor(self._id)
        self._successor.notify(self._ref)
        self._predecessor = self._successor.predecessor
        if not self._predecessor or self._predecessor.id == self._id:
            self._predecessor = self._successor
            pass
        else:
            self._predecessor = self._successor.find_predecessor(self._id)
            pass
        self.start_leader_selection()
        pass
    
    def check_predecessor(self):
        while True:
            try:
                if self._predecessor and not self._predecessor.check_predecessor():
                    self.collect_predecessor_data()
                    self._predecessor = None
                    if self._predecessor.id == self._leader.id:
                        self.start_leader_selection()
                        pass
                    pass
                pass
            except Exception as ex:
                pass
            time.sleep(5)
            pass
        pass
    
    def start_leader_selection(self):
        self._successor.select_leader(self._ref,self._id)
        pass
    
    def discover_network(self):
        while True:
            if self._leader.id == self._id:
                for i in range(8001,9000):
                    client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
                    try:
                        client.connect((self._host,i))
                        client.close()
                        node = NodeReference((self._host,i),self._table_size)
                        if not node.id == self._id and node.leader.id > self._id:
                            self.join(node)
                            break
                        pass
                    except Exception as ex:
                        pass
                    pass
                pass
            time.sleep(5)
            pass
        pass
    
    def store_data(self,data):
        for key in data.keys():
            if int(key) == self._id: continue
            path = self._path.joinpath(f'data_{self._id}').joinpath(f'{key}.json')
            file = open(f'{path}','w')
            content = json.dumps(data[key])
            file.write(content)
            file.close()
            pass
        pass
    
    def discard_predecessor_data(self):
        file = self._path.joinpath(f'data_{self._id}').joinpath(f'{self._predecessor.id}.json')
        os.remove(f'{file}')
        pass
    
    def discard_successor_data(self):
        file = self._path.joinpath(f'data_{self._id}').joinpath(f'{self._successor.id}.json')
        os.remove(f'{file}')
        pass
    
    def collect_predecessor_data(self):
        my_file = self._path.joinpath(f'data_{self._id}').joinpath(f'{self._id}.json')
        f = open(f'{my_file}','r')
        data = json.loads(f.read())
        f.close()
        file = self._path.joinpath(f'data_{self._id}').joinpath(f'{self._predecessor.id}.json')
        f = open(f'{file}','r')
        data_ = json.loads(f.read())
        f.close()
        for field in data_.keys():
            for d in data_[field].keys():
                data[field][d] = data_[field][d]
                pass
            pass
        os.remove(f'{file}')
        f = open(f'{my_file}','w')
        f.write(json.dumps(data))
        f.close()
        pass
    
    def collect_successor_data(self):
        my_file = self._path.joinpath(f'data_{self._id}').joinpath(f'{self._id}.json')
        f = open(f'{my_file}','r')
        data = json.loads(f.read())
        f.close()
        file = self._path.joinpath(f'data_{self._id}').joinpath(f'{self._successor.id}.json')
        f = open(f'{file}','r')
        data_ = json.loads(f.read())
        f.close()
        for field in data_.keys():
            for d in data_[field].keys():
                data[field][d] = data_[field][d]
                pass
            pass
        os.remove(f'{file}')
        f = open(f'{my_file}','w')
        f.write(json.dumps(data))
        f.close()
        pass
    
    def collect_data(self):
        file = self._path.joinpath(f'data_{self._id}').joinpath(f'{self._id}.json')
        f = open(f'{file}','r')
        my_data = json.loads(f.read())
        f.close()
        data = {self._id:my_data}
        return data
    
    def replicate_data(self):
        while True:
            data = self.collect_data()
            try:
                if not self._successor.id == self._id:
                    self._successor.store_data(data)
                    pass
                if self._predecessor and not self._successor.id == self._predecessor:
                    self._predecessor.store_data(data)
                    pass
                pass
            except Exception as ex:
                pass
            time.sleep(10)
            pass
        pass
    
    def logger(self):
        while True:
            logging.info(f'{Color.GREEN.value}NODE {self} SUCCESSOR {self._successor} PREDECESSOR {self._predecessor}{Color.RESET.value}')
            for i in range(len(self._finger_table)):
                print((self._id + 2**i)%2**self._table_size,self._finger_table[i])
                pass
            if self._leader.id == self._id:
                logging.info(f'{Color.BLUE.value}NODE {self._id} LEADER{Color.RESET.value}')
            time.sleep(5)
            pass
        pass
    
    def stabilize(self):
        while True:
            logging.info(f'{Color.GREEN.value}STABILIZING NODE {self._id}{Color.RESET.value}')
            try:
                if self._successor.id == self._id:
                    self._predecessor = None
                    pass
                else:
                    temp = self._successor.predecessor
                    if temp and not temp.id == self._id:
                        if inbettwen(temp.id,self._id,self._successor.id):
                            self._successor = temp
                            pass
                        self._successor.notify(self._ref)
                        pass
                    pass
                if not self._predecessor and not self._successor.id == self._id:
                    predecessor = self._successor.find_predecessor(self._id)
                    if predecessor:
                        self.notify(predecessor)
                        pass
                    pass
                pass
            except Exception as ex:
                start_select_leader = self._successor.id == self._leader.id
                if self._predecessor and self._predecessor.check_predecessor():
                    temp = self._predecessor.predecessor
                    while temp and not inbettwen(self._id,self._predecessor.id,temp.id):
                        temp = temp.predecessor
                        pass
                    if temp:
                        self._successor = temp
                        self._successor.notify(self._ref)
                        pass
                    else:
                        self._successor = self._ref
                        pass
                    pass
                if not self._predecessor:
                    self._successor = self._ref
                    pass
                if start_select_leader:
                    self.start_leader_selection()
                    pass
                pass
            time.sleep(5)
            pass
        pass
    
    def server(self):
        server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
        server.bind((self._host,self._port))
        server.listen(10)
        
        while True:
            try:
                conn,_ = server.accept()
                json_data = conn.recv(BUFFER_SIZE)
                data = get_data_from_json(json_data)
                operation = data['operation']
                data_ = data['data']
                if operation in self._request_handlers.keys():
                    if not operation in [Operation.SELECT_LEADER.value,Operation.NOTIFY_LEADER.value,Operation.DELETE_ONE_GROUP.value]:
                        response = self._request_handlers[operation](**data_)
                        json_response = set_json_data_to_send(response)
                        conn.sendall(json_response)
                        pass
                    else:
                        response = {'response':'OK'}
                        json_response = set_json_data_to_send(response)
                        conn.sendall(json_response)
                        self._request_handlers[operation](**data_)
                        pass
                    pass
                conn.close()
                pass
            except Exception as ex:
                pass
            
            pass
        
        pass
    
    def _handle_find_successor_request(self,**request):
        key = request['id']
        successor = self.find_successor(key)
        return {'id':successor.id,'ip':successor.host,'port':successor.port}
    
    def _handle_notify_request(self,**request):
        host = request['ip']
        port = request['port']
        node = NodeReference((host,port),self._table_size)
        self.notify(node)
        pass
    
    def _hanlde_find_predecessor_request(self,**request):
        key = request['id']
        predecessor = self.find_predecessor(key)
        return {'id':predecessor.id,'ip':predecessor.host,'port':predecessor.port}
    
    def _handle_get_successor_request(self,**request):
        return {'ip':self._successor.host,'port':self._successor.port}
    
    def _handle_get_predecessor_request(self,**request):
        if not self._predecessor:
            return {}
        return {'ip':self._predecessor.host,'port':self._predecessor.port}
    
    def _handle_closest_preceding_finger_request(self,**request):
        finger = self.closest_preceding_finger(request['id'])
        return {'ip':finger.host,'port':finger.port}
    
    def _handle_check_predecessor_request(self,**request):
        return {'response':'OK'}
    
    def _handle_join_request(self,**request):
        ref = NodeReference((request['ip'],request['port']),self._table_size)
        self.join(ref)
        return {'response':'OK'}
    
    def _handle_notify_leader_request(self,**request):
        leader_ip = request['ip']
        leader_port = request['port']
        start = request['start']
        self._leader = NodeReference((leader_ip,leader_port),self._table_size)
        if not start == self._id:
            self._successor.notify_leader(self._leader,start)
            pass
        pass
    
    def _handle_select_leader_request(self,**request):
        leader_id = request['leader_id']
        leader_ip = request['ip']
        leader_port = request['port']
        start = request['start']
        if self._id > leader_id:
            self._successor.select_leader(self._ref,start)
            pass
        elif start == self._id:
            self._leader = NodeReference((leader_ip,leader_port),self._table_size)
            self._successor.notify_leader(self._leader,self._id)
            pass
        else:
            self._successor.select_leader(NodeReference((leader_ip,leader_port),self._table_size),start)
            pass
        return {'ip':self._leader.host,'port':self._leader.port}
    
    def _handle_get_leader_request(self,**request):
        return {'ip':self._leader.host,'port':self._leader.port}
    
    def _handle_store_data_request(self,**request):
        self.store_data(request)
        return {'response':'OK'}
    
    def _handle_find_user_request(self,**request):
        username = request['username']
        password = request['password']
        start_id = request['start']
        if start_id == self._id:
            return {'status':False}
        return self.find_user(username,password,start_id)
    
    def _handle_get_groups_request(self,**request):
        current_groups = request['current_groups']
        start_id = request['start']
        if start_id == self._id:
            return current_groups
        return self.get_groups(start_id,current_groups)
    
    def _handle_delet_one_group_request(self,**request):
        start_id = request['start']
        groupname = request['groupname']
        if self._id == start_id:
            return
        self.delete_one_group(groupname,start_id)
        pass
    
    pass