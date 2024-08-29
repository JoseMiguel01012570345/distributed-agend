import time
import math
import psutil

'''

TODO:

Entry node:

1. Node ask president insertion
2. Every node in system updates its finger table
3. President finds lowest index node ,  and gives to entry node as succesor
4. New node ask for sucessor's finger table


Leaving node:

1. Every node ask to its links for 'live' response , if given a time , such response is not returned , a falling node is found
2. Given a falling node , this node is notify through all of the network , and each node in system , removes it from finger table
3. Provious node from the falling one , is intended to reconect the ring and fix its finger table , so this ask for ip and port of the node that better
    fix n = max((m+1) - 2^i) , where i >= 1 and m is the missing node, in here n is an existing node to his finger table connections . If every node from 
    the finger table is fallen , then ask to president . Note that i is the lowest posible

4. When requested node n is found then , the connector node ask to n for its finger table ,  and adjust his finger table, where his successor is the m + 1 node ,
    since in n's finger table the m + 1 's ip and port are registred

At this moment the ring is already connected , so we have to update every finger table . 

5. Previous falling node ask nodes from his index to update them index , when the last node updates his index ( last node is that whose succesor index is lower ) ,
    then broadcast to the ring for nodes in system count to be updated

6. Right now every node can update his finger table ask to his links for index nodes

Crashing in stabilization

1. If a node is crashed while stabilization under underway , then a flooding message 'break' is send to a ring to avoid current stabilization
2. When a node sends a 'break' message it expects 'good' message response for a time t , if no message is returned then a falling node is found .

'''

class node:
    
    def __init__(self , ip , port  , president=None ):
        
        self.init_var()
        
        self.ip = ip
        self.port = port
        self.president = president
        
        if president is not None:
            self.send_data( 
                            ip=president['ip']  ,
                            port=president['port'] ,
                            data={ 
                                  'action': self.encode_action('entry_node') ,
                                  'node':{ 'ip':self.ip , 'port':self.port  } 
                                  } 
                            )
    
    def init_var(self):
        
        self.index = None
        self.finger_table=[]
        self.nodes_in_system = 0
        self.distroy = False 
        self.tasks=[]
        self.env = []
        self.ip = ''
        self.port = 0
        self.node_response = []
        self.president = { 'ip': self.ip , 'port':self.port , 'index': self.index  }
        self.actions = {
            
            'hello' : self.hello ,
            'node_leaving': self.node_leaving ,
            'election': self.election ,
            'entry_node': self.entry_node ,
            'alive': self.alive,
            'on': self.on ,
            'insert_node': self.insert_node ,
            'update_sucessor':self.update_sucessor ,
            'inserted_node' : self.inserted_node ,
            'wellcome': self.wellcome ,
            'retry' : self.retry
            
        }
        self.insertion_await = False
        self.hello_await = False
        self.auth_node = False
        self.last_state = {
            
            'finger_table': self.finger_table,
            'nodes_in_system': self.nodes_in_system,
        }
        
        self.capacity =  psutil.virtual_memory().total  # Convert bytes
        self.entry_node_info = { 'ip':'' , 'port':'' }
    
    def hello( self , data ):
        
        if not self.answer_avaliabily():
            return
        
        node= data['node']
        if self.is_president():
            self.hello_await = False
            self.auth_node = True
            self.entry_node( data=data )
            
            return
        
        if self.ip == node['ip'] and self.port == node['port']: # if node exisiting node is trying to insert , refuse it
            self.send_data( ip=self.president['ip'] , port=self.president['port'] , data={
                
                'action': self.encode_action('exisitng_node'),
                'node' : node
                
            } )
            
            return 
            
        sucessor_ip = self.finger_table[0]['ip']
        sucessor_port = self.finger_table[0]['port']
        self.send_data( ip=sucessor_ip , port=sucessor_port , data={
                        'action': self.encode_action('hello') ,
                        'node': node
                        } 
                            )
        
        
    def find_next(self):
        pass
        
    def send_data(self , ip , port , data=None ):
        
        env = {}
        env['ip'] = ip
        env['port'] = port
        env['data'] = data
              
        self.env.append( env )
        
    def interrumpt( self ):
        
        self.distroy = True # block every request
        #_________________________________step back to the last state_______________________________________
        self.nodes_in_system = self.last_state['nodes_in_system'] 
        self.finger_table = self.last_state['finger_table'] 
        #_________________________________________________________________________
        
    def select_fowarding_node( self , target_index ):
        
        ip , port = None , None
        if target_index <= self.index or target_index >= self.finger_table[-1]['index']:
            
            ip = self.finger_table[-1]['ip'] 
            port = self.finger_table[-1]['port'] 
            
        elif self.index < target_index < self.finger_table[-1]['index']:
            
            for index,element in enumerate(self.finger_table):
                
                if element['index'] > target_index:
                    return self.finger_table[ index - 1 ]['ip'] , self.finger_table[ index - 1 ]['port']
        
        return ip , port
    
    def answer_avaliabily(self):
        return not self.index is None
    
    def recv_data( self ):

        data = self.tasks[0]
        self.tasks.pop(0)
        
        if self.distroy and time.time() - self.start_breaking < self.breaking_time:
            return
    
        data_action = data['action']
        action = self.actions[ self.decode_action(data_action) ]

        action( data=data )
    
    def update_sucessor(self , data ):
        
            
        node = data['node']
        self.index = data['index']
        self.finger_table.append(node)
        self.nodes_in_system = self.index + 1
        self.send_data( 
                       ip=self.president['ip'] ,
                       port=self.president['port'] ,
                       data={ 'action': self.encode_action('wellcome') } 
                       )
        
    def node_leaving(self , data ):
        
        node = data['node']
        self.interrumpt()
        
        data={ 'action': self.encode_action('node_leaving') , 'node': node  }
        self.remove_node( node=node ) # remove missing node
        self.broadcast(data=data)
        
        if node['ip'] == self.president['ip'] and node['port'] == self.president['port']: # verify the missing node is the president
            self.start_election()
        
    def remove_node( self , node ):
        
        remove_ip = node['ip']
        remove_port = node['port']
        remove_index = node['index']
        
        for index,element in enumerate(self.finger_table):
            if element['ip'] == remove_ip and element['port'] == remove_port and element['index'] == remove_index:
                self.finger_table.pop(index)        
    
    def election( self , data ):
        
        task_load = data['task_load']
        node = data['node']
        ip = node['ip']
        port = node['port']
        
        if len(self.tasks) / self.capacity > task_load: # taskless node is elected has president
            self.president = { 'ip': ip , 'port': port }
            self.broadcast( data=data )
    
    def broadcast(self , data ):
        for element in self.finger_table:
            self.send_data( element['ip'] , element['port'] , data=data )
    
    def start_election(self): # broadcast elections to all linked nodes
        
        data = { 
                'action': self.encode_action('election') ,
                'task_load': len(self.tasks) ,
                'node': { 'ip':self.ip  , 'port':self.port } ,
            }
        
        self.broadcast( data=data )
    
    def is_president(self):
        return self.president['ip'] == self.ip and self.president['port'] == self.port
    
    def entry_node(self , data ):
        
        node = data['node']
                
        if not self.entrance_condition(node=node):
            return
        
        # only presidents have previleges , insert node if and only if it is hasn't been rquested to
        if self.is_president() and not node.__contains__('index'):
            
            node['index'] = self.nodes_in_system # give new node an index
            ip = self.finger_table[-1]['ip']
            port = self.finger_table[-1]['port']
            
            data = { 
                'action': self.encode_action('insert_node') ,
                'index': self.nodes_in_system ,
                'target_index':self.nodes_in_system - 1 , # search for the last index
                'node': node } # insert new node at penultimum ring node as its sucessor
            
            self.insertion_await = True
            self.auth_node = False
            self.send_data( ip=ip , port=port , data=data ) # send data to last link of president finger table
            self.entry_node_info = node
        
        # ask every link node to fix its finger table
        data = { 'action': self.encode_action('entry_node') , 'node': node }
        self.broadcast( data=data )
        self.fix_finger_table( node=node )
    
    def entrance_condition( self , node ):
        
        # conditions for not allowing a node to enter
        if (
            not self.__dict__.__contains__('index') or # an index is required
            (
                node.__contains__('index') and
                node['index'] < self.nodes_in_system # if the my count is higher then entry node index , I refuse it
            ) or self.insertion_await or # president can't no be waitting for a node insertion
             self.distroy or # if falling node
             self.hello_await # waitting for an entry node to be authenticated
        ): 
                
            if self.is_president() and \
                (
                    node['ip'] != self.entry_node_info['ip'] and
                    node['port'] != self.entry_node_info['port']
                ):
                
                 self.send_data(
                                    ip=node['ip'] ,
                                    port=node['port'] ,
                                    data={
                                    'action': self.encode_action('retry') 
                                    }
                                )
            
            return False
        
        # if node is not autheticated by the president, forward authentication to sucessor
        if self.is_president() and not self.auth_node:
            sucessor_ip = self.finger_table[0]['ip']
            sucessor_port = self.finger_table[0]['port']
            self.hello_await = True
            self.send_data( ip=sucessor_ip , port=sucessor_port , data={
                        'action': self.encode_action('hello') ,
                        'node':node 
                        }
                            )
            return False
        
        return True
    
    def fix_finger_table(self , node ):
        
        # if message of insertion is has arrived and node insertion is not complited , ignore
        if not self.answer_avaliabily():
            return
        
        self.up_last_state()
        self.nodes_in_system += 1
        if self.index + 2 ** ( len(self.finger_table) + 1 ) == self.nodes_in_system:
            self.finger_table.append( { 'ip': node['ip'] , 'port': node['port'] , 'index': self.nodes_in_system - 1 } )
    
    def up_last_state(self):
        
        self.last_state = {
            
            'finger_table': self.finger_table,
            'nodes_in_system': self.nodes_in_system,
        }
    
    def retry(self , data ): # retry to connect to system
        
        if not self.index is None:
            return
        
        president_ip = data['origin']['ip']
        president_port = data['origin']['port']
        
        self.send_data \
        ( 
            ip=president_ip  ,
            port=president_port ,
            data={ 
                    'action': self.encode_action('entry_node') ,
                    'node':{ 'ip':self.ip , 'port':self.port  } 
                } 
        )    
    
    def insert_node( self , data ):
        
        node = data['node']
        target_index = data['target_index']
        
        if node['ip'] == self.ip and node['port'] == self.port: # if the presumed insert node is me, then I return a None node
            
            data = {  'action': self.encode_action('inserted_node') , 'sucessor': None }
            self.send_data(self.president['ip'] , self.president['port'] , data=data )
            return
        
        if target_index != self.index: # forward the message
            
            ip , port = self.select_fowarding_node( target_index=target_index )
            self.send_data(ip=ip , port=port , data=data )
            return
            
        sucessor_ip = self.finger_table[0]['ip']
        sucessor_port = self.finger_table[0]['port']
        sucessor_index = self.finger_table[0]['index']
        
        # new node is now my sucessor
        self.finger_table[0]['ip'] = node['ip']
        self.finger_table[0]['port'] = node['port']
        self.finger_table[0]['index'] = node['index']
        
        data = {
            'action': self.encode_action('inserted_node') ,
            'sucessor': { 'ip' : sucessor_ip , 'port': sucessor_port , 'index': sucessor_index },
            'inserted_node': node,
            'index': self.index + 1 ,
        }
        
        self.send_data( self.president['ip'] , self.president['port'] , data=data )
    
    def inserted_node(self , data ):
        
        if not self.is_president(): # in case the request is forwarded to a node that is not a president
            self.send_data( self.president['ip'] , self.president['port'] , data=data )
        
        if data['sucessor'] is None: # in case a request node is already in system
            return
        
        # if everything goes well , then this is the president and we will return to the new node, its sucessor
        
        new_node = data['inserted_node']
        
        data = {
            'action':self.encode_action('update_sucessor') ,
            'node': data['sucessor'] ,
            'index': data['index'] ,
        }
        
        self.send_data( new_node['ip'] , new_node['port'] , data=data ) # ask entry node to update sucessor
    
    def wellcome(self , data ):
        
        if self.insertion_await:
            self.insertion_await = False
            self.entry_node_info = { 'ip':'' , 'port':'' }
            
    def alive(self , data ): # this signal is a request from predecesor
        
        node = data['node']
        self.send_data( node['ip'] , node['port'] , data={ 'action': self.encode_action('on') } )
    
    def on( self , data ): # this signal means that sucessor is alive
        
        if len(self.node_response) > 0:
            self.node_response = None
    
    def detect_falling_nodes( self ):
        
        response_time = 1.0 * self.nodes_in_system
        if self.node_response is not None and time.time() - self.node_response[0]['time'] >= response_time: # faulty node found
            m = self.node_response[0]['node']
            self.node_leaving( m )
            
        sucessor = self.finger_table[0]
        self.node_response= { 'node':sucessor , 'time': time.time() } # add sucessor to 'wait for response'
        self.send_data( sucessor[0]['ip'] , sucessor['port'] , data={ 'action': self.encode_action('alive') } ) # send alive signal to sucessor
    
    def encode_action(self , action ):
        
        actions={
            'election': 0 ,
            'alive': 1 ,
            'hello': 2 ,
            'node_leaving': 3,
            'entry_node' : 4,
            'insert_node': 5 ,
            'on': 6 ,
            'update_sucessor': 7,
            'inserted_node': 8 ,
            'wellcome': 9,
            'retry':10 ,
        }
        
        return actions[action]
    
    def decode_action(self , action_encoded ):
        
        actions={
            0: 'election',
            1: 'alive',
            2: 'hello' ,
            3: 'node_leaving',
            4: 'entry_node',
            5: 'insert_node',
            7: 'update_sucessor',
            8: 'inserted_node' ,
            9: 'wellcome' ,
            10 : 'retry' ,
        }
        
        return actions[action_encoded]
    