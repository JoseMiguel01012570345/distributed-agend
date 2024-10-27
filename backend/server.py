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
    
    def find_agend(self,agend_id):
        path = self._path.joinpath(f'data_{self._id}').joinpath(f'{self._id}.json')
        file = open(f'{path}','r')
        data = json.loads(file.read())
        file.close()
        if agend_id in data['agends'].keys():
            return True
        try:
            if self._successor.find_agend_by_id(agend_id,self._id)['status'] == 'OK':
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
    
    pass