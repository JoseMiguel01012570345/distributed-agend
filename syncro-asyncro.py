import random
import node
import networkx as nx
import matplotlib.pyplot as plt
import os

os.system('cls')
def enviroment():
    
    chord_system = []

    
    # setting first node
    first_node = node.node( ip='127.0.0.0' , port=0)
    first_node.index = 0
    first_node.finger_table.append( { 'ip': first_node.ip , 'port':first_node.port , 'index':first_node.index } )
    first_node.nodes_in_system += 1
    first_node.sucessor = { 'ip': first_node.ip , 'port': first_node.port }
    
    chord_system.append(first_node)
    
    # setting president
    president = { 'ip':first_node.ip , 'port':first_node.port , 'index':first_node.index }
    first_node.president = president
    
    server_limit = 100
    entry_time = [ i for i in range(1,server_limit) ]
    num_server = 0
    
    avaliable = True
    leaving_time = []
    sleep = []
    
    time = 0
    while True:
        
        # os.system('cls')
        
        if len(entry_time) > 0: # testing entry node
            
            entry_time = [ item - 1 for item in entry_time ]
            
            if any( [ item <= 0 for item in entry_time ] ):
            
                index = [ index  for index,item in enumerate(entry_time) if item == 0 ][0]
                entry_time.pop(index)
                
                num_server += 1
                new_node = node.node( ip=f'127.0.0.{num_server}' , port=num_server , president=president )
                chord_system.append(new_node)
        
        elif len(entry_time) == 0:
            
            inserted = inserted_nodes(chord_system=chord_system)
            president = find_president(nodes=chord_system)
            
            # remove the president 
            if president is not None and  inserted == server_limit and \
                not president.insertion_await and  \
                president.stabilization and \
                avaliable:
                server_limit -= 1
                remove_president(chord_system=chord_system)
                avaliable = False
                print('president out')
                
        mod = send( chord_system , time=time )
        
        for element in chord_system: # recieve msg from origin
            if len(element.tasks) > 0:
                # if element.tasks[0]['action'] == 10:
                #     print(f'{element.ip}_{element.port} retrying...')
                    
                element.recv_data()
                mod = True
        
        if not mod and len(entry_time) == 0:
            break
            
        time += 1
        # print(time)
    
    update_graph( nodes=chord_system , time=time )

def find_president(nodes):
    for element in nodes:
        if element.is_president():
            return element

def remove_president(chord_system:list):
    
    for index,node in enumerate(chord_system):
        if node.is_president():
            chord_system.pop(index)
            return

def inserted_nodes(chord_system:list):
    
    inserted = 0
    for node in chord_system:
        if node.answer_avaliabily():
            inserted += 1
    
    return inserted
    
def update_graph( nodes:list , time:int ):
    
    graph = nx.DiGraph()
    
    for node in nodes:
        for item in node.finger_table:
            graph.add_edge( f"{node.ip}_{node.port}" , f"{ item['ip'] }_{ item['port'] }" )
    
    
    nx.draw( graph , with_labels=True)
    plt.show()
    # plt.savefig('./graph.jpg')
   
def send( chord_system , time=0 ):
    mod = False
    
    for element in chord_system: # delivery msg from origin to destination
        if len(element.env) > 0:
            while len(element.env) != 0:
                
                msg = element.env[0]
                dest_ip = msg['ip']
                dest_port = msg['port']
                data = msg['data']
                data['origin'] = { 'ip': element.ip , 'port': element.port } # add origin to data
                data['clock'] = time 
                delivery_msg( nodes=chord_system , destination={ 'ip': dest_ip , 'port': dest_port } , data=data )
                element.env.pop(0)
                mod = True
    
    return mod

def delivery_msg( nodes , destination:node , data ):
    
    for element in nodes:
        if element.ip == destination['ip'] and element.port == destination['port']:
            element.tasks.append( data )

enviroment()