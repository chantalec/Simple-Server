#################################################################################################
# Authors:      Chatale C., Kerry W., Tavin J.
#                * Alex - dropped the class 
#                       - he helped with the skeleton code for the first check point
#                       - that code is saved on my computer in case it is needed as proof
# Professor:    Yanyan Li
# CS 436:       Computer Networks

# Description:  End point socket that wil receive messages
# Process:      Using TCP to ensure no data is lost
#################################################################################################

import socket       # import socket module
import threading    # import threading module

# store address to connect server to client
HOST = socket.gethostbyname(socket.gethostname())
PORT = 8000
ADDR = (HOST, PORT)

# globals
clients = {}
rooms = {}
MAX_USERS = 100

# joins chat room spicified by user
def join_chat_box(client_connect, client_address, chat_room):
    rooms[chat_room].append((client_connect, client_address))
    clients[client_connect]['chat_room'] = chat_room
    print('joined chat room')

# creates chat room specified by user
def create_chat_room(client_connect, client_address, chat_room):
    rooms[chat_room] = [(client_connect, client_address)]
    clients[client_connect]['chat_room'] = chat_room
    print(f'created chat room')
    
# checks if the chat room the user wants to join exists or not
def join_command(client_connect, client_address, chat_room):
    if chat_room in rooms:  # chat room exists
        if len(rooms[chat_room]) >= MAX_USERS:  # chat room is fulll
            client_connect.sendall(f'{chat_room} is full'.encode())
        else:   # chat room not full
            client_connect.sendall(f'{chat_room} found'.encode())
            join_chat_box(client_connect, client_address, chat_room) 
    elif chat_room not in rooms:    # chat room does not exist
        client_connect.sendall(f'{chat_room} not found'.encode())
        create_chat_room(client_connect, client_address, chat_room)

# checks if the chat room the user wants to create exists or not  
def create_command(client_connect, client_address, chat_room):
    if chat_room in rooms:  # chat room exists
        client_connect.sendall(f'{chat_room} already exists'.encode())
        if len(rooms[chat_room]) >= MAX_USERS:  # chat room is ful
            client_connect.sendall(f'{chat_room} is full'.encode())
        else:   # chat room not full 
            join_chat_box(client_connect, client_address, chat_room)
    elif chat_room not in rooms:    # chat room does not exists
        client_connect.sendall(f'{chat_room} not found'.encode())
        create_chat_room(client_connect, client_address, chat_room)
        #client_connect.sendall(f'{chat_room} created'.encode())  

# checks login commands and acts accordingly            
def login_commands(client_connect, client_address, command):    
    chat_room = clients[client_connect]['chat_room']
    if command == '[JOIN]':     # user wants to join the specified chat room
        join_command(client_connect, client_address, chat_room)
    elif command == '[CREATE]': # user want to create the specified chat room
        create_command(client_connect, client_address, chat_room)
    else:   # user entered something other that join or create
        client_connect.sendall(''.encode())
    
# handles the msg from cient after user is in the chat room          
def recv_msg_from_client(client_connect, client_address):     
    username = clients[client_connect]['username']
    chat_room = clients[client_connect]['chat_room']
    while True:
        try:
            in_msg = client_connect.recv(1024).decode('utf-8')
            
            if in_msg == '[CREATE]':
                create_chat_room(client_connect, client_address, chat_room)
                break
        
            if in_msg == '[EXIT]':
                rooms[chat_room].remove((client_connect, client_address))
                del clients[client_connect]
                client_connect.close()
                print(f'Client {client_address} ({username}) disconnected')
                break
            if in_msg != '':
                out_msg = username + ':\t~ ' + in_msg
            
                for client_tuple in rooms[chat_room]:
                    client_tuple[0].sendall(out_msg.encode())
        except OSError as e:
            print(f'Error: {e}')
            break

# handles the information received from the login window in client
def client_manager(client_connect, client_address):    
    while True:        
        # receive and decode data/msg from client
        in_msg = client_connect.recv(1024).decode('utf-8')
                
        username = in_msg.split('|', 2)[0]
        chat_room = in_msg.split('|', 2)[1]
        command = in_msg.split('|', 2)[2]
                
        clients[client_connect] = {'socket': client_connect, 'username': username, 'chat_room': chat_room, 'active': True}
                                   
        print(f'\n\tusernmae: {username} \n\tchat_room: {chat_room}')
        
        login_commands(client_connect, client_address, command)
        
        break
    recv_msg_from_client(client_connect, client_address)

# starts and initializes server
def start_server():         
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(ADDR)

    print('\nStarting Server ...')
    server_socket.listen(5)
    print(f'Listening on {HOST}')       
    
    try:
        while True:
            client_connect, client_address = server_socket.accept()
            print(f'Connection with {str(client_address)} established!')
            print('\nWelcome to the Chat App')
                    
            threading.Thread(target = client_manager, args = (client_connect, client_address)).start()
    except KeyboardInterrupt:
        print(f'\n\tShutting down server {ADDR}')
        # close all client connections
        for client_connect in clients:
            clients[client_connect]['active'] = False
            clients[client_connect]['socket'].close()
        # close server socket
        server_socket.close()
        print('\tServer close\n')

start_server()