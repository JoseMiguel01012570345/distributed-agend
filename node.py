import time
import math
import psutil
import sys
import numpy as np

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
            'completed': self.node_stable ,
            'elected_president': self.elected_president ,
            'stable_ring' : self.stable_ring ,
            
        }
        self.ellapse_time = 0
        self.num_stabilized_nodes = 1
        self.insertion_await = False
        self.hello_await = False
        self.auth_node = False
        self.states = []
        self.stabilization = True
        self.capacity =  psutil.virtual_memory().total  # Convert bytes
        self.min_task_load = self.capacity
        self.entry_node_info = { 'ip':'' , 'port':'' }
        self.fix_fg = True
        self.missing_node = []
        self.foraing_nodes = []
        self.reset_stab = True 
        self.time = 0
    
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
            for index,node in enumerate(self.finger_table): 
                if not node['index'] in self.needed_nodes:
                    self.foraing_nodes.append(node)
                    
            # find the elements that are not in finger table
            index = 0
            while index < len(self.needed_nodes):
                
                n = self.needed_nodes[index]
                
                if not  any( [ element['index'] == n  for element in self.finger_table ] ):
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
        self.reset_stab = True
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
        
        self.remove_foraings()
    
    def node_stable(self , data ):
        
        if self.stabilization: return
        
        nodes_in_system = data['nodes_in_system']
        if nodes_in_system != self.nodes_in_system: # if nodes in system are diferent , we send a signal to the node to stabilize again
            
            node = data['node']
            self.send_data(ip=node['ip'] ,
                           port=node['port'] ,
                           data={
                                 'action':self.encode_action('stable_ring') ,
                                 'missing_nodes':self.missing_node
                                 }
                           )
            return 
        
        self.num_stabilized_nodes += 1
        if self.num_stabilized_nodes == self.nodes_in_system: # if all nodes are stable , president is stable
         
            self.stabilization = True
            self.num_stabilized_nodes = 1
            self.remove_foraings()
            print('stabilized ring with: ', self.nodes_in_system , ' nodes')
    
    def stable_ring(self , data):
        
        missing_nodes = data['missing_nodes']
        
        print(f'restaring stabilization on node ip:{self.ip} port:{self.port} index:{self.index}...')
        for m in missing_nodes:
            if not any( [ element['ip'] == m['ip'] and element['port'] == element['port'] for element in self.missing_node ] ):
                self.node_leaving( data={ 'node': m } )
                
    def remove_foraings(self): # remove all of the nodes in finger table that do not fit in finger table
        
        i = 0
        while len(self.finger_table) != int(math.log2(self.nodes_in_system)): 
            
            i = i % len(self.finger_table)
            element = self.finger_table[i]
        
            if any( [ item['ip'] == element['ip'] and item['port'] == element['port']  for item in self.foraing_nodes] ):
                self.finger_table.pop(i)
                i -= 1
                
            i += 1
        
        self.foraing_nodes.clear()
    
    def exiting_node( self , data ):
        input()
        print( data['msg'] )
        
    def send_data(self , ip , port , data=None ):
        
        env = {}
        env['ip'] = ip
        env['port'] = port
        env['data'] = data
              
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
            
            data_action = data['action']
            action = self.actions[ self.decode_action(data_action) ]

            action( data=data )
        
        '''
        TOOD: split detect_falling_nodes method into a thread
        '''
        
        self.time = clock
        self.up_state()
        self.detect_falling_nodes( )
    
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
        clock = node['clock']
        
        # we don't forward if the falling node is already taken into account
        if any( [element['ip'] == node['ip'] and element['port'] == node['port'] for element in self.missing_node] ): # case 1
            return
        elif self.stabilization: # case 2
            self.stabilization = False
        elif not self.stabilization: # case 3
            self.fix_fg = True # start again fixing the finger table
        
        self.missing_node.append(node)
        self.num_stabilized_nodes = 1
        self.interrumpt()
        
        self.remove_node( node=node ) # remove missing node
        self.nodes_in_system -= 1
        self.fix_index(clock=clock)
        
        i = 0
        k = -1
        while True and len(self.finger_table) != 0:
            
            i = i % min( int(math.log2(self.nodes_in_system)) , len(self.finger_table) )

            if i == 0: k += 1
            
            k = k % int(math.log2(self.nodes_in_system))
            
            element = self.finger_table[i]
            p = (self.index + 2 ** k ) % self.nodes_in_system
            
            if element['index'] == p:
                self.sucessor = self.finger_table[i] # change sucessor
                break
            
            i += 1
        
        data={ 'action': self.encode_action('node_leaving') , 'node': node }
        self.broadcast(data=data)
        
    def remove_node( self , node ): # remove a fallen node
        
        remove_ip = node['ip']
        remove_port = node['port']
        
        for index,element in enumerate(self.finger_table):
            if element['ip'] == remove_ip and element['port'] == remove_port:
                self.finger_table.pop(index)

    def calculate_list_memory_usage(self, lst):
        return sys.getsizeof(lst)
    
    def fix_index( self , clock ):
        
        if self.port == 8:
            print()
        state = self.binary_search( clock=clock )
        if self.missing_node[-1]['index'] <= state['index']:
            self.index -= 1
            
        for node in self.finger_table:
            
            element = self.search_node_in_state( state=state , node=node )
            
            if element['index'] > self.missing_node[-1]['index']:
                node['index'] -= 1
    
    def search_node_in_state(self , state , node):
        for element in state['finger_table']:
            if element['ip'] == node['ip'] and element['port'] == node['port']:
                return element
        
    def binary_search(self , clock ):
        
        if clock > self.states[-1]['clock']:  # if clock bypasses the actual time , return the actual state
            self.up_state(clock=clock)
            return self.states[-1]
            
        left_side = self.states[ : int(len(self.states) / 2) ]
        right_side = self.states[ int(len(self.states) / 2): ]
    
        while True:
            
            if left_side[-1]['clock'] == clock  and clock == right_side[0]['clock']:
                left_side = right_side[ : int(len(right_side) / 2) ]
                right_side = right_side[ int(len(right_side) / 2): ]
              
            elif left_side[-1]['clock'] == clock :
                return  left_side[-1]
    
            elif  clock == right_side[0]['clock']:
                return right_side[0]
            
            elif left_side[-1]['clock'] < clock < right_side[0]['clock']:
                return left_side[-1]['clock']
            
            elif  clock < left_side[-1]['clock']:
                left_side = left_side[  : int(len(left_side) / 2) ]
                right_side = left_side[ int(len(left_side) / 2) : ]
              
            elif clock > right_side[0]['clock']:
                left_side = right_side[ : int(len(right_side) / 2) ]
                right_side = right_side[  int(len(right_side) / 2): ]
            
    def recognition( self , president ): # the elected president call for stabilization of the ring
    
        data={
            'action': self.encode_action('elected_president') ,
            'president': { 'ip': president['ip'] , 'port': president['port'] }
        }
        self.distroy = False
        self.vote = False
        self.elected = True
        self.broadcast(data=data)
        self.stabilize()
        print( 'president:' , self.ip , self.port )
            
    def elected_president( self , data ):
        
        if not self.elected:
            self.elected = True
            self.president = data['president']
            self.distroy = False
            self.vote = False
            self.broadcast(data=data)
    
    def election( self , data ):
        
        if data['num_votes'] == self.nodes_in_system:
            self.recognition( president=data['node'] )
        
        data['num_votes'] += 1
        task_load = data['task_load']
        
        # taskless node is elected as president
        if self.min_task_load < task_load: 
            
            self.send_data( ip=self.sucessor['ip'] ,
                        port=self.sucessor['port'] , 
                        data={ 
                            'action': self.encode_action('election') ,
                            'num_votes': data['num_votes'] ,
                            'node': { 'ip': self.ip , 'port': self.port } ,
                            'task_load': self.min_task_load ,
                            }
                        )
                    
            return
        
        self.elected = False
        self.send_data( ip=self.sucessor['ip'] ,port=self.sucessor['port'] , data=data )
            
    def broadcast(self , data ):
        
        if not any( [
                    element['ip'] == self.president['ip'] 
                        and element['port'] == self.president['port'] 
                        for element in self.missing_node 
                        ]
                    ):
            
            self.send_data( self.president['ip'] , self.president['port'] , data=data )
            
        for element in self.finger_table:
            self.send_data( element['ip'] , element['port'] , data=data )
    
    def start_election(self): # broadcast elections to all linked nodes
        
        task_load = self.calculate_list_memory_usage(self.tasks) / self.capacity
        data = { 
                'action': self.encode_action('election') ,
                'task_load': task_load ,
                'node': { 'ip':self.ip  , 'port':self.port } ,
                'num_votes': 0 ,
                }
        
        self.election( data=data )
    
    def is_president(self , node=None):
        
        if node is not None:
            return self.president['ip'] == node['ip'] and self.president['port'] == node['port']    
        
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
        while len(self.states) > 2 * self.nodes_in_system:
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
        sucessor_index = [ element for element in self.finger_table 
                            if element['ip'] == self.sucessor['ip'] and
                            element['port'] == self.sucessor['port'] ][0]['index']
                
        self.node_response = [] # empty waitting response list
        
        data = {
            'action': self.encode_action('inserted_node') ,
            'sucessor': { 
                'ip' : sucessor['ip'] ,
                'port': sucessor['port'] ,
                'index': self.finger_table[sucessor_index]['index'] 
                },
            'inserted_node': node,
            'index': self.index + 1 ,
        }
        
        # new node is now my sucessor
        self.finger_table[sucessor_index] = node
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
        
    def detect_falling_nodes( self ):
        
        response_time = 3
        if self.time % response_time != 0:
            return
        
        self.ellapse_time = self.time - self.time % response_time
        
        if not self.answer_avaliabily(): return
        
        if len(self.node_response) != 0: # faulty nodes found
            
            for index,node in enumerate(self.node_response): # send 'node_leaving' signal of the missing node
                
                self.distroy = False
                self.node_response.pop(index)
                node['clock'] = self.time
                
                # verify the missing node is the president and it's my sucessor
                if self.is_president(node=node) and self.is_president(node=self.sucessor): 
                    
                    self.node_leaving( data={ 'node': node })
                    self.president = { 'ip':'' , 'port': '' }
                    self.stabilization = False # stabilization is now required
                    self.min_task_load = self.calculate_list_memory_usage(self.tasks) / self.capacity # my load
                    self.president = { 'ip': self.ip , 'port': self.port } # I'm the president
                    self.elected = False # president election flag
                    self.start_election()
                    print('node out: ', node )
                    
                    return
                
                # if the falling node is not the president , then skip election
                self.node_leaving( data={ 'node': node })
                
                print('node out1: ', node , { 'ip':self.ip , 'port': self.port } )
                if not self.is_president(node=node):
                    self.stabilize()
                
        else:
            
            for element in self.finger_table: # send a 'alive' signal to all links
                
                self.node_response.append( { 'ip': element['ip'] , 'port': element['port'] , 'index': element['index']} )
                
                self.send_data(
                    ip=element['ip'] ,
                    port=element['port'] ,
                    data={
                        'action': self.encode_action('alive') ,
                        'node': { 'ip': self.ip , 'port': self.port } }
                    ) # send alive signal to sucessor
    
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
            'stable_ring': 18 ,
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
            18: 'stable_ring' ,
        }
        
        return actions[action_encoded]
    