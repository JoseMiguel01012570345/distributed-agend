import math

class node:

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

    6. Right now every node can update his finger table asking to his links for index nodes

    Crashing in stabilization

    1. If a node is crashed while stabilization under underway , then a flooding message 'break' is send to a ring to avoid current stabilization
    2. When a node sends a 'break' message it expects 'good' message response for a time t , if no message is returned then a falling node is found .

    '''
    
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
        self.president = { 'ip': self.ip , 'port':self.port , 'index': self.index  }
        self.sucessor = {}
        self.node_response = []
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
            'retry' : self.retry ,
            'existing_node': self.exiting_node ,
            'stabilize': self.stabilize ,
            'index_response': self.index_response , 
            'find_index': self.find_index ,
            'elected_president': self.elected_president ,
            'give_ticket': self.give_ticket ,
            'set_index': self. set_index ,
            'finished': self.stable_nodes ,
            'completed': self.stable_nodes ,
            'stop_index_broadcasting': self.stop_index_broadcasting ,
            'set_president_stabilzation': self.set_president_stabilzation ,
            'president_stabilization_info': self.send_president_stabilization_info ,
            
        }
        self.reconnecting = False
        self.num_stabilized_nodes = 1
        self.insertion_await = False
        self.hello_await = False
        self.auth_node = False
        self.states = []
        self.stabilization = True
        self.entry_node_info = { 'ip':'' , 'port':'' }
        self.fix_fg = True
        self.missing_node = []
        self.time = 0
        self.given_index = -1
        self.index_setted = True
        self.aux_finger_table = []
        self.finish_indexing = True
        self.last_president = {}
        self.app_queue = []
        self.ring_queue = []
    
    def hello( self , data ):
        
        if not self.answer_avaliabily():
            return
        
        node= data['node']
        if self.is_president():
            self.hello_await = False
            self.auth_node = True
            self.entry_node( data=data )
            
            return
        
        if not self.is_president(): # new stabilization is requeried for the entry node
            self.stabilization = False 
        
        if self.ip == node['ip'] and self.port == node['port']: # if node exisiting node is trying to insert , refuse it
            self.send_data( ip=self.president['ip'] , port=self.president['port'] , data={
                
                'action': self.encode_action('existing_node'),
                'msg' : 'deja la gracia' ,
                
            } )
            return
        
        sucessor_ip = self.finger_table[0]['ip']
        sucessor_port = self.finger_table[0]['port']
        self.send_data( ip=sucessor_ip , port=sucessor_port , data={
                        'action': self.encode_action('hello') ,
                        'node': node
                        } 
                            )
        
    def find_index( self , data=None ):
        
        index = data['index']
        
        # if the index doesn't exist any longer , do not forward request
        if index >= self.nodes_in_system:
            return
        
        if self.index != index: # if not the index , forward message
            
            ip , port = self.select_fowarding_node(target_index=index)
            self.send_data( ip=ip , port=port , data=data )
            return
        
        origin = data['requester']
        data = {
            
            'action' : self.encode_action('index_response') ,
            'node':{
            'ip' : self.ip ,
            'port': self.port ,
            'index': self.index ,
            }
        }
        self.send_data( ip=origin['ip'] , port=origin['port'] , data=data )
    
    def index_response(self , data ):
        
        node = data['node']
        index= node['index']
        
        if self.stabilization: return
        
        if index in self.needed_nodes:
            self.needed_nodes.remove(index)
        
            self.finger_table.append( node )
            
            if len(self.needed_nodes) == 0:
                self.stabilization_completed()
         
    def stabilize( self , data=None ):
        
        
        if self.stabilization: # if node is stable , do not forward stabilization
            return
        
        if self.fix_fg:
            
            self.needed_nodes= []
            self.fix_fg = False
            
            i = 0
            while i < int(math.log2(self.nodes_in_system)):
                
                i += 1
                p = ( self.index + 2 ** ( i- 1 ) ) % self.nodes_in_system
                
                if self.index != p: # if 'p' index is not in finger table
                    self.needed_nodes.append(p)
            
            # remove all element in finger table that are not needed
            spin = True
            while spin:
                
                spin = False
                for index,node in enumerate(self.finger_table):
                    if not node['index'] in self.needed_nodes:
                        self.finger_table.pop(index)
                        spin = True
                    
            # find the elements that are not in finger table
            index = 0
            while index < len(self.needed_nodes):
                
                n = self.needed_nodes[index]
                
                if not any( [ element['index'] == n  for element in self.finger_table ] ):
                    self.find_index( data={ # find index p
                        'action': self.encode_action('find_index') ,
                        'index': n ,
                        'requester':{ 
                            'ip':self.ip , 'port': self.port 
                        }
                    } )
                else:
                    self.needed_nodes.remove(n)
                    index -= 1
                    
                index += 1
            
        if len(self.needed_nodes) == 0 and not self.stabilization: # check if there are no needed node , if so we are done
            self.stabilization_completed()
            
        self.broadcast( data={ 'action': self.encode_action('stabilize') } )
    
    def check_finger_table(self):
        # if there are missing nodes , then finger_table is not completed
        if int(math.log2(self.nodes_in_system)) > len(self.finger_table):
            return False
        
        return True
    
    def stabilization_completed(self):
        
        if self.is_president(): return
        
        self.stabilization = True
        self.fix_fg = True
        self.send_data( # send a stabilization complete signal
            ip=self.president['ip'] ,
            port=self.president['port'] ,
            data={ 
                'action':self.encode_action( 'completed' ) ,
                'nodes_in_system': self.nodes_in_system  ,
                'node': { 'ip': self.ip , 'port': self.port }
                }
            )
        
    def stable_nodes(self , data ):
        
        if self.stabilization : return
        
        nodes_in_system = data['nodes_in_system']
        
        if nodes_in_system != self.nodes_in_system:
            return
        
        self.num_stabilized_nodes += 1
        
        # print(self.num_stabilized_nodes , self.nodes_in_system)
        
        if nodes_in_system == 22 and 'index' in data:
            print('index:',data['index'])
        
        if self.num_stabilized_nodes == self.nodes_in_system:
            self.num_stabilized_nodes = 1
            self.stabilization = True
            self.finish_indexing = True
            self.distroy = False
            print('stabilized ring with: ', self.nodes_in_system , ' nodes')
            
            if len(self.missing_node) != 0:
                
                self.broadcast(data={ 'action': self.encode_action('stop_index_broadcasting') } )
    
    def exiting_node( self , data ):
        input()
        print( data['msg'] )
        
    def send_data(self , ip , port , data=None , ring=True ):
        
        env = {}
        env['ip'] = ip
        env['port'] = port
        env['data'] = data
        env['id'] = self.encode_business_id('app')
        
        if ring:
            env['id'] = self.encode_business_id('ring')
        
        self.env.append( env )
        
    def interrumpt( self ):
        self.distroy = True # block every request
        
    def select_fowarding_node( self , target_index ):
        
        if len(self.finger_table) == 0: # if no node in finger table , rely on president
            return self.president['ip'] , self.president['port']
        
        new_list = [ element for element in self.finger_table if element['index'] <= target_index ] # priorize element lower then target_index
        
        if len(new_list) == 0: # otherwise , elements bigger then target_index
            new_list = [ element for element in self.finger_table if element['index'] >= self.index ] 
        
        best_index = 0
        best_node = new_list[0]
        for element in new_list:
            if element['index'] >= best_index:
                best_index = element['index']
                best_node = element
        
        return best_node['ip'] , best_node['port']
    
    def answer_avaliabily(self):
        return not self.index is None
    
    def recv_data( self , clock=0 ):
            
        while len(self.tasks) != 0: # solve all task
            
            data = self.tasks[0]
            self.tasks.pop(0)
            
            id_ = self.decode_business_id( data['id'] )
            
            if id_ == 'ring':
                
                self.ring_queue.append(data)
                
                
                data = self.ring_queue[0]
                self.ring_queue.pop(0)
                
                action = self.decode_action( data['action'] )
                foo = self.actions[action]
                
                foo( data )
                
                continue
            
            self.app_queue.append(data)
        
        '''
        TOOD: split detect_falling_nodes method into a thread
        '''
        
        self.time = clock
        self.up_state()
        self.detect_falling_nodes()
    
    def ring_reciever(self):
        
        while len(self.ring_queue) != 0: # solve all ring tasks
        
            data = self.ring_queue[0]
            self.ring_queue.pop(0)
            
            data_action = data['action']
            action = self.actions[ self.decode_action(data_action) ]
            
            action( data=data )
    
    def app_server(self):
        pass
    
    def update_sucessor(self , data ):
        
            
        node = data['node']
        self.index = data['index']
        self.finger_table.append(node)
        self.sucessor = self.finger_table[0]
        self.nodes_in_system = self.index + 1
        self.stabilization = False
        self.send_data( 
                       ip=self.president['ip'] ,
                       port=self.president['port'] ,
                       data={ 'action': self.encode_action('wellcome') } 
                       )
        
    def node_leaving(self , data ):
        
        node = data['node']
        
        # we don't forward if the falling node is already taken into account
        if any( [element['ip'] == node['ip'] and element['port'] == node['port'] for element in self.missing_node] ): # case 1
            return
        
        self.missing_node.append(node)
        self.num_stabilized_nodes = 1
        self.interrumpt()
        
        self.remove_node( node=node ) # remove missing node
        self.nodes_in_system -= 1
    
        self.given_index = -1
        
        self.index_setted = False
        self.stabilization = False
        self.finish_indexing = False
        
        if node['index'] == self.president['index']:
            self.last_president = self.president
            self.president = { 'ip': None , 'port': None , 'index': None }
            self.elected = False
        
        data={ 'action': self.encode_action('node_leaving') , 'node': node }
        self.broadcast(data=data , use_president=True )
        
        if not self.is_president() and self.president['ip'] is not None: # ask for index to president
            self.ask_index()
        
        elif self.is_president():
            self.set_index(
                data={
                'action': self.encode_action('set_index') ,
                'count':0 ,
                'nodes_in_system': self.nodes_in_system ,
                'node': { 'ip': self.ip , 'port': self.port , 'index': self.index  }
                }
            )
        
    def remove_node( self , node ): # remove a fallen node
        
        remove_ip = node['ip']
        remove_port = node['port']
        
        for index,element in enumerate(self.finger_table):
            if element['ip'] == remove_ip and element['port'] == remove_port:
                self.finger_table.pop(index)

    def stop_index_broadcasting(self , data):
        
        if not self.finish_indexing:
            self.stabilization = True
            self.finish_indexing = True
            self.distroy = False
            self.finger_table.clear()
            self.finger_table = [ element for element in self.aux_finger_table ]
            self.broadcast(data=data)
    
    def get_president_stabilization(self):
        
        self.reconnecting = True
        self.send_data(
            ip=self.president['ip'],
            port=self.president['port'],
            data={ 
                  
                  'action': self.encode_action('president_stabilization_info') ,
                  'node': { 'ip':self.ip , 'port': self.port } 
                  
                  }
            )
    
    def set_president_stabilzation( self , data ):
        
        president_stabilization = data['stabilization']
        president_nodes_in_system = data['nodes_in_system']
        
        if president_stabilization and self.index >= president_nodes_in_system:
                    
            self.finish_indexing = True # finish indexing step
            self.reconnect()
            return
        
        self.reconnecting = False # if presindent is not stable , ring is not stable , so we are not reconnecting
    
    def reconnect(self): # reconnection to the ring because ring pushed node trying to stabilize
         
        del self.finger_table
        self.index = None
        self.finger_table = []
        
        self.retry( data={
            
            'origin':{ 
                'ip': self.president['ip'] , 'port':self.president['port'] 
            }
        } )
        
    def send_president_stabilization_info( self , data ):
        # send to requesting node stabilization information of the president , it is to say , state of the ring
        
        node = data['node']
        
        self.send_data(
            ip=node['ip'],
            port=node['port'],
            data={ 
                'action': self.encode_action('set_president_stabilzation') , 
                'stabilization': self.stabilization ,
                'nodes_in_system': self.nodes_in_system ,
            }
        )

    def check_ring_stability( self ):
        if not self.finish_indexing and not self.reconnecting and self.elected and not self.is_president():
            self.get_president_stabilization()
    
    def give_ticket(self , data ):
        
        if not self.given_index < self.nodes_in_system : return
        
        nodes_in_system = data['nodes_in_system']
        if self.nodes_in_system < nodes_in_system: return # we do not acept old request based on the number of nodes in system
        
        node = data['node']
        self.given_index += 1
        
        if self.given_index == self.index: # index can't be repeated
            self.given_index += 1
        
        # print( 'nodes_in_system:' , self.nodes_in_system ,'indexes: ', self.given_index )
        node['index'] = self.given_index
        self.send_data( # retrieve index to node
            ip=node['ip'],
            port=node['port'],
            data={
                'action': self.encode_action('set_index'),
                'node': node ,
                'nodes_in_system' : self.nodes_in_system ,
                'count': 0 ,
            }
        )
        
    def set_index( self , data ):
    
        if self.finish_indexing : return
        
        if data['count'] > self.nodes_in_system ** 2: return
            
        node = data['node']
        index = node['index']
        nodes_in_system = data['nodes_in_system']
        
        if self.nodes_in_system != nodes_in_system:
            return
        
        if self.ip == node['ip'] and self.port == node['port'] and not self.index_setted:
            
            self.index_setted = True
            
            self.index = index
            i = 0
            self.aux_finger_table = []
            self.needed_nodes.clear()
            
            n = self.nodes_in_system
            if n == 0 : n = 1
            while i < int(math.log2(n)):
                
                i += 1
                p = ( self.index + 2 ** ( i- 1 ) ) % self.nodes_in_system
                
                if self.index != p: # if 'p' index is not in finger table
                    self.needed_nodes.append(p)
                    
        elif self.index_setted and index in self.needed_nodes:
                
            if index == ( self.index + 1 ) % self.nodes_in_system : # adjust sucessor
                self.sucessor = node
            
            self.aux_finger_table.append(node)
            self.needed_nodes.remove(index)
            
            if self.is_president() and len(self.needed_nodes) == 0 :
                self.finger_table.clear()
                self.finger_table = [ element for element in self.aux_finger_table ]
            
            if len(self.needed_nodes) == 0 and not self.is_president():
                   
                self.send_data(  # send finish response
                            ip=self.president['ip'] ,
                            port=self.president['port'] ,
                            data={
                                "action": self.encode_action('finished') ,
                                'nodes_in_system' : self.nodes_in_system ,
                                'index': self.index ,
                                }
                            )
        
        data['count'] += 1
        self.broadcast(data=data)
    
    def ask_index( self ): # ask to president for index
        self.index_setted = False
        self.send_data(
            ip=self.president['ip'],
            port=self.president['port'],
            data={
                'action': self.encode_action('give_ticket') ,
                'node': {  'ip': self.ip , 'port': self.port } , 
                'nodes_in_system': self.nodes_in_system ,
            }
        )
            
    def elected_president( self , data ):
        
        if self.elected: return
        
        self.elected = True
        self.president = data['president']
        self.distroy = False
        
        if not self.is_president():
            self.ask_index()
            print( 'asking node:', self.port , 'president: ' , self.president)
        
        self.broadcast(data=data)
    
    def election( self , data ):
        
        if self.elected: return
        
        president_index = -1
        
        for indexes in range(self.nodes_in_system):
        
            if any( element['index'] == indexes for element in self.missing_node ) or \
            self.last_president['index'] > indexes:  continue
            
            if self.last_president['index'] < indexes: # circular ring
                president_index = indexes
            
            if president_index == self.president['index']: return
            
            if self.index == president_index:
                self.hello_await = False
                data = {
                    'action': self.encode_action('elected_president') ,
                    'president': { 'ip': self.ip , 'port': self.port , 'index': self.index } 
                    }
                
                self.elected_president( data=data )
            
            else:
                self.president = { 'ip': None , 'port': None , 'index': president_index }
                print( f'elected president index: {president_index} , node: {self.ip} {self.port} {self.index}' )
            
            self.broadcast(data=data)
            return
            
    def broadcast(self , data , use_president= False ):
        
        if self.president['ip'] is not None and ( use_president or len(self.finger_table) == 0 ) and not self.is_president():
            
            self.send_data( self.president['ip'] , self.president['port'] , data=data )
            
        for element in self.finger_table:
            self.send_data( element['ip'] , element['port'] , data=data )
    
    def start_election(self): # broadcast elections to all linked nodes
        data = { 'action': self.encode_action('election') }
        self.election( data=data )
    
    def is_president(self , node=None):
        
        if node is not None:
            return self.president['index'] == node['index'] 
        
        return self.president['index'] == self.index
    
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
                'target_index':self.nodes_in_system - 1 , # search for the last index
                'node': node 
                } # insert new node at penultimum ring node as its sucessor
            
            self.insertion_await = True
            self.auth_node = False
            self.send_data( ip=ip , port=port , data=data ) # send data to last link of president finger table
            self.entry_node_info = node
        
        self.missing_node.clear()
        
        # ask every link node to fix its finger table
        data = { 'action': self.encode_action('entry_node') , 'node': node }
        self.broadcast( data=data )
        self.nodes_in_system += 1
    
    def entrance_condition( self , node ):
        
        # conditions for not allowing a node to enter
        if (
            not self.__dict__.__contains__('index') or # an index is required
            (
                node.__contains__('index') and
                node['index'] < self.nodes_in_system # if the my count is higher then entry node index , I refuse it
            ) or self.insertion_await or # president can't no be waitting for a node insertion
             self.distroy or # if falling node
             self.hello_await or # waitting for an entry node to be authenticated
             ( # if ring is not stable
                 not self.stabilization and \
                 self.is_president() 
            ) 
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
        
    def up_state( self):
        
        self.states.append(
            {
            
            'finger_table': self.finger_table,
            'nodes_in_system': self.nodes_in_system,
            'index': self.index ,
            'clock': self.time , 
            
        }
            )
        while self.nodes_in_system > 0 and len(self.states) > int(math.log2(self.nodes_in_system)):
            self.states.pop(0)
    
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
        
        sucessor = self.sucessor
        sucessor_index = self.sucessor['index']
        
        self.node_response = [] # empty waitting response list
        
        data = {
            'action': self.encode_action('inserted_node') ,
            'sucessor': { 
                'ip' : sucessor['ip'] ,
                'port': sucessor['port'] ,
                'index': sucessor_index 
                },
            'inserted_node': node,
            'index': self.index + 1 ,
        }
        
        # new node is now my sucessor
        for i in range(len(self.finger_table)):
            if self.finger_table[i]['ip'] == self.sucessor['ip'] and self.finger_table[i]['port'] == self.sucessor['port']:
                self.finger_table[i] = node
                break
            
        self.sucessor = node
        
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
            self.stabilization = False
            self.fix_fg = True
            self.stabilize() # fix finger table
            
    def alive(self , data ): # this signal is a request from predecesor
        
        node = data['node']
        self.send_data( ip=node['ip'] ,
                       port=node['port'] ,
                       data={ 'action': self.encode_action('on') , 'node':{ 'ip':self.ip , 'port':self.port } } 
                       )
    
    def on( self , data ): # this signal means that sucessor is alive
        # remove all the nodes that have answer
        node = data['node'] 
        self.node_response = [ element for element in self.node_response if element['ip'] != node['ip'] and element['port'] != node['port']]
    
    def detect_unknow_falling_nodes(self , response_time ):
        
        if not self.is_president() or self.stabilization or len(self.missing_node) == 0:
            return
        
        earliest_fall = sorted([ node['clock'] for node in self.missing_node ])[-1]
        
        if self.time - earliest_fall >=  response_time * int(math.log2(self.nodes_in_system + len(self.missing_node))) and self.nodes_in_system > 1:
            
            self.node_leaving( data={ 'node': { 'ip': self.time , 'port': self.time , 'index': self.time , 'clock':self.time } } )
            print('discover unknow falling')
        
    def detect_falling_nodes( self ):
        
        response_time = 3
        self.detect_unknow_falling_nodes(response_time=response_time) # check for nodes not accesables
        
        if self.time % response_time != 0 or not self.answer_avaliabily():
            return
        
        # self.check_ring_stability() # check every period of time , wheather node is in system
        
        if len(self.node_response) != 0: # faulty nodes found
            
            
            for index,node in enumerate(self.node_response): # send 'node_leaving' signal of the missing node
                
                node['clock'] = self.time # add time to the missing node
                
                self.distroy = False
                self.node_response.pop(index)
                
                # verify the missing node is the president and it's my sucessor
                if self.is_president(node=node):
                    
                    self.node_leaving( data={ 'node': node })
                    self.elected = False # president election flag
                    self.start_election()
                    print('node out: ', node )
                    
                    return
                
                # if the falling node is not the president , then skip election
                self.node_leaving( data={ 'node': node })
                print('discover time:', self.time)
                print('node out1: ', node , { 'ip':self.ip , 'port': self.port } )
                
        else:
            
            for element in self.finger_table: # send a 'alive' signal to all links
                
                # avoid to much alive request to president if it is stable
                if self.is_president(node=element) and self.president['ip'] is not None: continue 
                
                self.node_response.append( { 'ip': element['ip'] , 'port': element['port'] , 'index': element['index']} )
                
                self.send_data(
                    ip=element['ip'] ,
                    port=element['port'] ,
                    data={
                        'action': self.encode_action('alive') ,
                        'node': { 'ip': self.ip , 'port': self.port } }
                    )

            # check every two checking cycles for the president
            if self.president['ip'] is not None and self.time % ( 2 * response_time) == 0:
                self.node_response.append( { 'ip': self.president['ip'] , 'port': self.president['port'] , 'index': self.president['index']} )
                self.send_data(
                    ip=self.president['ip'] ,
                    port=self.president['port'] ,
                    data={
                        'action': self.encode_action('alive') ,
                        'node': { 'ip': self.ip , 'port': self.port } }
                    )
            
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
            'existing_node': 11 ,
            'stabilize': 12 ,
            'index_response': 13 ,
            'find_index': 14 ,
            'completed': 15 ,
            'elected_president': 17 ,
            'finished': 18 ,
            'give_ticket': 19 ,
            'stop_index_broadcasting': 20 ,
            'set_index': 21,
            'set_president_stabilzation': 22 ,
            'president_stabilization_info' : 23 ,
            
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
            6: 'on' ,
            7: 'update_sucessor',
            8: 'inserted_node' ,
            9: 'wellcome' ,
            10: 'retry' ,
            11: 'existing_node' ,
            12: 'stabilize' ,
            13: 'index_response',
            14: 'find_index' ,
            15: 'completed' ,
            17: 'elected_president' ,
            18: 'finished' ,
            19: 'give_ticket' ,
            20: 'stop_index_broadcasting' ,
            21: 'set_index' ,
            22:'set_president_stabilzation' ,
            23:'president_stabilization_info' ,
        }
        
        return actions[action_encoded]
    
    def decode_business_id( self , id ):
        
        
        ids={
            
            0:'ring',
            1:'app',
            
        }
        
        return ids[id]

    def encode_business_id( self , id ):
        
        
        ids={
            
            'ring': 0,
            'app': 1,   
        }
        
        return ids[id]
    
    