import time
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
    
    server_limit = 20
    entry_time = [ i for i in range(1,server_limit) ]
    num_server = 0
    
    avaliable = True
    leaving_time = []
    
    start = time.time()
    t = 1
    s=''
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
                remove_node(chord_system=chord_system , target={ 'ip': president.ip , 'port': president.port } )
                remove_node(chord_system=chord_system , target={ 'ip': chord_system[-1].ip , 'port': chord_system[-1].port } )
                remove_node(chord_system=chord_system , target={ 'ip': chord_system[-1].ip , 'port': chord_system[-1].port } )
                # remove_node(chord_system=chord_system , target={ 'ip': chord_system[-1].ip , 'port': chord_system[-1].port } )
                # remove_node(chord_system=chord_system , target={ 'ip': chord_system[-1].ip , 'port': chord_system[-1].port } )
                # remove_node(chord_system=chord_system , target={ 'ip': chord_system[-1].ip , 'port': chord_system[-1].port } )
                # remove_node(chord_system=chord_system , target={ 'ip': chord_system[-1].ip , 'port': chord_system[-1].port } )
                # remove_node(chord_system=chord_system , target={ 'ip': chord_system[-1].ip , 'port': chord_system[-1].port } )
                # remove_node(chord_system=chord_system , target={ 'ip': chord_system[-1].ip , 'port': chord_system[-1].port } )
                # remove_node(chord_system=chord_system , target={ 'ip': chord_system[-1].ip , 'port': chord_system[-1].port } )
                # remove_node(chord_system=chord_system , target={ 'ip': chord_system[-1].ip , 'port': chord_system[-1].port } )
                # remove_node(chord_system=chord_system , target={ 'ip': chord_system[-1].ip , 'port': chord_system[-1].port } )
                # remove_node(chord_system=chord_system , target={ 'ip': chord_system[-1].ip , 'port': chord_system[-1].port } )
                # remove_node(chord_system=chord_system , target={ 'ip': chord_system[-1].ip , 'port': chord_system[-1].port } )
                # remove_node(chord_system=chord_system , target={ 'ip': chord_system[-1].ip , 'port': chord_system[-1].port } )
                # remove_node(chord_system=chord_system , target={ 'ip': chord_system[-1].ip , 'port': chord_system[-1].port } )
                # remove_node(chord_system=chord_system , target={ 'ip': chord_system[-1].ip , 'port': chord_system[-1].port } )
                
                # update_graph( nodes=chord_system , time=time )
                avaliable = False
            
            president =find_president(nodes=chord_system)
            
            if president is not None and not avaliable:
                remove_node(chord_system=chord_system , target={ 'ip': president.ip , 'port': president.port } )
                
            
                
        send( chord_system , time=t )
        
        for element in chord_system: # recieve msg from origin
            element.recv_data(clock=t)
        
        t += 1
        
        # s = report(nodes=chord_system , s=s , time = time.time() - start )
        # ellapse_time(nodes=chord_system)
        # input()
    
def ellapse_time(nodes):
    os.system('cls')
    for node in nodes:
        if node.answer_avaliabily():
            print(f'ip:{node.ip} port:{node.port} index:{node.index} --> ellapse time: {node.ellapse_time}')

def report(nodes , s , time):
    
    print(time)
    lider = find_president(nodes=nodes)
    str_report= f"_____number of nodes {lider.nodes_in_system}_____\n"
    for element in nodes:
        if element.answer_avaliabily():
            fg = '' 
            for item in element.finger_table :
                fg +=f"{item}\n"
                
            str_report += f"-> ip:{element.ip} port:{element.port}  index:{element.index} '\n' {fg}"
            str_report += "__________________________________\n"
    
    if s != str_report:
        os.system('cls')
        print( str_report )
        
    return str_report

def find_president(nodes):
    for element in nodes:
        if element.is_president():
            return element

def remove_node(chord_system:list , target):
    
    for index,node in enumerate(chord_system):
        if node.ip == target['ip']  and  node.port == target['port']:
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
                delivery_msg( nodes=chord_system , destination={ 'ip': dest_ip , 'port': dest_port } , data=data )
                element.env.pop(0)
                mod = True
    
    return mod

def delivery_msg( nodes , destination:node , data ):
    
    for element in nodes:
        if element.ip == destination['ip'] and element.port == destination['port']:
            element.tasks.append( data )

enviroment()
