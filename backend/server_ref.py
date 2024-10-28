from utils import set_json_data_to_send,get_data_from_json,Color
from chord.chord_node_ref import NodeReference
from chord.chord_operations import Operation
from chord.hashers import sha1_hash
import socket
import time
import logging
from threading import Thread
from backend.ui_operations import UIOperation

logging.basicConfig(level=logging.DEBUG,format='%(asctime)s [%(threadName)s] %(levelname)s: %(message)s')

class ServerReference(NodeReference):
    
    def __init__(self,ip,table_size=8,hasher=sha1_hash):
        address = self.locate_server(ip)
        super().__init__(address,table_size,hasher)
        Thread(target=self.check_server_alive,daemon=True,name=f'SERVER REFERENCE CHECK SERVER ALIVE {self._host},{self._port}').start()
        pass
    
    def locate_server(self,ip):
        for i in range(8001,9000):
            client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            try:
                client.connect((ip,i))
                client.close()
                return ip,i
            except Exception as ex:
                pass
            pass
        pass
    
    def check_server_alive(self):
        while True:
            server_down = False
            client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            try:
                client.connect((self._host,self._port))
                client.close()
                pass
            except Exception as ex:
                server_down = True
                logging.error(f'{Color.RED.value}SERVER DOWN{Color.RESET.value}')
                pass
            
            if server_down:
                try:
                    self._host,self._port = self.locate_server(self._host)
                    logging.info(f'{Color.GREEN.value} NEW SERVER LOCATED AT {self._host},{self._port}')
                    pass
                except Exception as ex:
                    logging.error(f'{Color.RED.value} CAN\'T LOCATE A SERVER{Color.RESET.value}')
                    pass
                pass
            time.sleep(5)
            pass
    
    def create_event(self,agend_id,date,description):
        data = {
            'agend_id':agend_id,
            'date':date,
            'description':description
        }
        response = self._send_data(UIOperation.CREATE_EVENT.value,data)
        return response['status'] == 'OK' if response else False
    
    def create_user(self,username,password):
        data = {
            'username':username,
            'password':password
        }
        return self._send_data(UIOperation.CREATE_USER.value,data)
    
    def authenticate_user(self,username,password):
        data = {
            'username':username,
            'password':password
        }
        response = self._send_data(UIOperation.AUTHENTICATE_USER.value,data)
        return response['status'] == 'OK'

    def get_all_groups(self):
        response = self._send_data(UIOperation.GET_ALL_GROUPS.value,{})
        return response
    
    def create_group(self,groupname):
        data = {
            'groupname':groupname
        }
        response = self._send_data(UIOperation.CREATE_GROUP.value,data)
        return response['status'] == 'OK' if response else False
    
    def delete_group(self,groupname):
        data = {
            'groupname':groupname
        }
        response = self._send_data(UIOperation.DELETE_GROUP.value,data)
        return response['status'] == 'OK' if response else False
    
    def get_agends_by_group(self,groupname):
        data = {
            'groupname':groupname
        }
        response = self._send_data(UIOperation.GET_AGENDS_BY_GROUP.value,data)
        return response
    
    def create_agend(self,agend_id,groupname):
        data = {
            'agend_id':agend_id,
            'groupname':groupname
        }
        response = self._send_data(UIOperation.CREATE_AGEND.value,data)
        return response['status'] == 'OK' if response else False
    
    def delete_agend(self,agend_id):
        data = {
            'agend_id':agend_id
        }
        response = self._send_data(UIOperation.DELETE_AGEND.value,data)
        return response['status'] == 'OK' if response else False
    
    def get_events(self,agend_id):
        data = {
            'agend_id':agend_id
        }
        response = self._send_data(UIOperation.GET_EVENTS.value,data)
        return response
    
    def get_event(self,event_id):
        data = {
            'event_id':event_id
        }
        response = self._send_data(UIOperation.GET_EVENT_BY_ID.value,data)
        return response
    
    def delete_event(self,event_id):
        data = {
            'event_id':event_id
        }
        response = self._send_data(UIOperation.DELETE_EVENT.value,data)
        return response['status'] == 'OK' if response else False
    
    pass