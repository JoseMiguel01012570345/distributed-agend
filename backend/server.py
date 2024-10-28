from chord import Node
import json
from chord.hashers import sha1_hash
from frontend.auth_page import AuthPage
from backend.ui_operations import UIOperation
from utils import set_json_data_to_send

class Server(Node):
    
    def __init__(self,address,ui=False):
        super().__init__(address)
        self._ui_handlers = self._init_ui_handlers()
        if ui:
            page = AuthPage(self)
            pass
        pass
    
    def _init_ui_handlers(self):
        return {
            UIOperation.CREATE_USER.value:self._handle_create_user_request,
            UIOperation.AUTHENTICATE_USER.value:self._handle_authenticate_user_request,
            UIOperation.GET_ALL_GROUPS.value:self._handle_get_all_groups_request,
            UIOperation.CREATE_GROUP.value:self._handle_create_group_request,
            UIOperation.DELETE_GROUP.value:self._handle_delete_group_request,
            UIOperation.GET_AGENDS_BY_GROUP.value:self._handle_get_agends_by_group_request,
            UIOperation.CREATE_AGEND.value:self._handle_create_agend_request,
            UIOperation.DELETE_AGEND.value:self._handle_delete_agend_request,
            UIOperation.GET_EVENTS.value:self._handle_get_events_request,
            UIOperation.CREATE_EVENT.value:self._handle_create_event_request,
            UIOperation.GET_EVENT_BY_ID.value:self._handle_get_event_request,
            UIOperation.DELETE_EVENT.value:self._handle_delete_event_request
        }
    
    def handle_request(self,connection,**request):
        super().handle_request(connection,**request)
        operation = request['operation']
        data = request['data']
        if operation in self._ui_handlers.keys():
            if not operation in [UIOperation.CREATE_USER.value]:
                response = self._ui_handlers[operation](**data)
                json_response = set_json_data_to_send(response)
                connection.sendall(json_response)
                pass
            else:
                response = {'status':'OK'}
                json_response = set_json_data_to_send(response)
                connection.sendall(json_response)
                self._ui_handlers[operation](**data)
                pass
            pass
        pass
    
    def _handle_delete_event_request(self,**request):
        event_id = request['event_id']
        self.delete_event(event_id)
        return {'status':'OK'}
    
    def _handle_get_event_request(self,**request):
        event_id = request['event_id']
        return self.get_event(event_id)
    
    def _handle_create_event_request(self,**request):
        agend_id = request['agend_id']
        date = request['date']
        description = request['description']
        self.create_event(agend_id,date,description)
        return {'status':'OK'}
    
    def _handle_get_events_request(self,**request):
        agend_id = request['agend_id']
        return self.get_events(agend_id)
    
    def _handle_delete_agend_request(self,**request):
        agend_id = request['agend_id']
        self.delete_agend(agend_id)
        return {'status':'OK'}
    
    def _handle_create_agend_request(self,**request):
        agend_id = request['agend_id']
        groupname = request['groupname']
        self.create_agend(agend_id,groupname)
        return {'status':'OK'}
    
    def _handle_get_agends_by_group_request(self,**request):
        groupname = request['groupname']
        return self.get_agends_by_group(groupname)
    
    def _handle_delete_group_request(self,**request):
        groupname = request['groupname']
        self.delete_group(groupname)
        return {'status':'OK'}
    
    def _handle_create_group_request(self,**request):
        groupname = request['groupname']
        self.create_group(groupname)
        return {'status':'OK'}
    
    def _handle_create_user_request(self,**request):
        username = request['username']
        password = request['password']
        self.create_user(username,password)
        pass
    
    def _handle_authenticate_user_request(self,**request):
        username = request['username']
        password = request['password']
        if not self.authenticate_user(username,password):
            return {'status':'WRONG'}
        return {'status':'OK'}
    
    def _handle_get_all_groups_request(self,**request):
        return self.get_all_groups()
    
    def create_event(self,agend_id,date,description):
        path = self._path.joinpath(f'data_{self._id}').joinpath(f'{self._id}.json')
        file = open(f'{path}','r')
        content = file.read()
        file.close()
        data = json.loads(content)
        event_id = sha1_hash(f'{date}<--->{description}',10)
        event_id = str(event_id)
        if not event_id in data['events'].keys():
            data['events'][event_id] = {'date':date,'description':description}
            pass
        if not agend_id in data['agends'].keys():
            try:
                if not self._successor.id == self._id:
                    self._successor.store_event(event_id,agend_id,self._id)
                    pass
                pass
            except Exception as ex:
                pass
            pass
        elif not event_id in data['agends'][agend_id]:
            data['agends'][agend_id].append(event_id)
            pass
        file = open(f'{path}','w')
        file.write(json.dumps(data))
        file.close()
        pass
    
    def get_events(self,agend_id):
        events = self.get_all_events_of_agend(agend_id,self._id,[])
        return events
    
    def get_event(self,event_id):
        event = self.get_event_by_id(event_id,self._id)
        return event
    
    def create_user(self,username,password):
        path = self._path.joinpath(f'data_{self._id}').joinpath(f'{self._id}.json')
        file = open(f'{path}','r')
        data = json.loads(file.read())
        file.close()
        data['users'][username] = password
        file = open(f'{path}','w')
        file.write(json.dumps(data))
        file.close()
        pass
    
    def authenticate_user(self,username,password):
        result = self.find_user(username,password,self._id)
        if result['status']:
            return True
        return False
    
    def create_group(self,group_name):
        path = self._path.joinpath(f'data_{self._id}').joinpath(f'{self._id}.json')
        file = open(f'{path}','r')
        data = json.loads(file.read())
        file.close()
        group = {
            'agends':[]
        }
        data['groups'][group_name] = group
        file = open(f'{path}','w')
        file.write(json.dumps(data))
        file.close()
        pass
    
    def get_all_groups(self):
        groups = self.get_groups(self._id)
        return groups
    
    def delete_group(self,groupname):
        self.delete_one_group(groupname,self._id)
        pass
    
    def delete_agend(self,agend_id):
        self.delete_one_agend(agend_id,self._id)
        pass
    
    def find_agend(self,agend_id):
        path = self._path.joinpath(f'data_{self._id}').joinpath(f'{self._id}.json')
        file = open(f'{path}','r')
        data = json.loads(file.read())
        file.close()
        if agend_id in data['agends'].keys():
            return True
        try:
            if not self._successor.id == self._id and self._successor.find_agend_by_id(agend_id,self._id)['status'] == 'OK':
                return True
            return False
        except Exception as ex:
            return False
        pass

    def create_agend(self,agend_id,groupname):
        path = self._path.joinpath(f'data_{self._id}').joinpath(f'{self._id}.json')
        file = open(f'{path}','r')
        data = json.loads(file.read())
        file.close()
        if not agend_id in data['agends'].keys() and not self.find_agend(agend_id):
            data['agends'][agend_id] = []
            pass
        if not groupname in data['groups'].keys():
            try:
                if not self._successor.id == self._id:
                    self._successor.store_agend(agend_id,groupname,self._id)
                    pass
                pass
            except Exception as ex:
                pass
            pass
        elif not agend_id in data['groups'][groupname]['agends']:
            data['groups'][groupname]['agends'].append(agend_id)
            pass
        file = open(f'{path}','w')
        file.write(json.dumps(data))
        file.close()
        pass
    
    def get_agends_by_group(self,groupname):
        agends = self.get_all_agends_of_group(groupname,self._id)
        return agends
    
    def delete_event(self,event_id):
        self.delete_one_event(event_id,self._id)
        pass
    
    pass