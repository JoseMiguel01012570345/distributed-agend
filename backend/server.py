from chord import Node
import json
from chord.hashers import sha1_hash
from frontend.auth_page import AuthPage

class Server(Node):
    
    def __init__(self,address,ui=False):
        super().__init__(address)
        if ui:
            page = AuthPage(self)
            pass
        pass
    
    def create_event(self,date,description):
        path = self._path.joinpath(f'data_{self._id}').joinpath(f'{self._id}.json')
        file = open(f'{path}','r')
        content = file.read()
        file.close()
        data = json.loads(content)
        event_id = sha1_hash(f'{date}<--->{description}',10)
        data['events'][event_id] = {'date':date,'description':description}
        file = open(f'{path}','w')
        content = json.dumps(data)
        file.write(data)
        file.close()
        pass
    
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
    
    def create_agend(self,agend_id,groupname):
        path = self._path.joinpath(f'data_{self._id}').joinpath(f'{self._id}.json')
        file = open(f'{path}','r')
        data = json.loads(file.read())
        file.close()
        data['agends'][agend_id] = []
        data['groups'][groupname]['agends'].append(agend_id)
        file = open(f'{path}','w')
        file.write(json.dumps(data))
        file.close()
        pass
    
    def get_agends_by_group(self,groupname):
        agends = self.get_all_agends_of_group(groupname,self._id)
        return agends
    
    pass