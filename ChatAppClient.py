#################################################################################################
# Authors:      Chatale C., Kerry W., Tavin J.
# Professor:    Yanyan Li
# CS 436:       Computer Networks

# Description:  Start point socket that wil receive messages
# Process:      Using TCP to ensure no data is lost
#################################################################################################

import socket           # import socket module
import threading
import os
from tkinter import *
from tkinter import messagebox

 # store hostname to connect client to server
HOST = socket.gethostbyname(socket.gethostname()) 
PORT = 8000
ADDR = (HOST, PORT)

# Creating a socket object
# AF_INET: we are going to use IPv4 addresses
# SOCK_STREAM: we are using TCP packets for communication
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


chat_window = Tk() # initialize chat window
chat_window.withdraw() # chat window currently hidden

# set login window
login_window = Toplevel()
login_window.title('Login')
login_window.resizable(width = False, height = False)
login_window.geometry('400x300')
login_label = Label(login_window, text = 'Please log in to continue', padx = 50, pady = 0)
login_label.place(relheight = 0.1, relx = 0.2, rely = 0.07)

# create a Label
user_name_label = Label(login_window, text = 'Username: ')
user_name_label.place(relheight = 0.1, relx = 0.1, rely = 0.2)
# create a entry box for typing the message
user_name_entry = Entry(login_window)
user_name_entry.place(relwidth = 0.3, relheight = 0.1, relx = 0.5, rely = 0.2)
user_name_entry.focus() # set the focus of the cursor

# create a Label for the chat room name
chat_room_label = Label(login_window, text = 'Chat Room Name:')
chat_room_label.place(relheight = 0.1, relx = 0.1, rely = 0.35)
# create an Entry for the chat room name
chat_room_entry = Entry(login_window)
chat_room_entry.place(relwidth = 0.3, relheight = 0.1, relx = 0.5, rely = 0.35)
    
# create a Label for the user's action
action_label = Label(login_window, text='[JOIN] or [CREATE] ? : ')
action_label.place(relheight = 0.1, relx = 0.1, rely = 0.5)
# create an Entry for the user's action
action_entry = Entry(login_window)
action_entry.place(relwidth = 0.3, relheight = 0.1, relx = 0.5, rely = 0.5)

# create a Continue Button along with action
go = Button(login_window, text = 'CONTINUE', command = lambda: check_login_commands())
go.place(relx = 0.35, rely = 0.7)   

# starts and initializes client
def start_client(): 
    while True:   
        try:    # try except block
            client_socket.connect(ADDR)  # Connect to the server
            messagebox.showinfo('Server', f'Connection to server\n{ADDR}\n~ Successful ~\n')
            break
        except:
            retry = messagebox.askretrycancel('Server', f'Unable to connect to server\n{ADDR} \nDo you want to try again?')    
            if not retry:
                os._exit(0) # emergency exit

# makes sure all fields in login window are filled
def get_login_info():
    while True:
        username = user_name_entry.get()        # gets username entered in login window
        chat_room = chat_room_entry.get()       # gets chat room entered in login window
        command = action_entry.get().upper()    # gets command entered in login window  
        
        if (username != '') and (chat_room != '') and (command != ''):
            break # if all fields are filled - move on
        else:
            messagebox.showerror('Missing information!', 'All fields must be filled to continue')
            return None, None, None
    start_client()  # starts client if-and-only-if all fields were filled in login window
    return username, chat_room, command

# checks login window command and acts appropriately          
def check_login_commands():        
    username, chat_room, command = get_login_info()
    
    # a second 'check' to make sure get_login_info function did not make a mistake
    if (username is None) or (chat_room is None) or (command is None):
        return
        
    out_msg = username + '|' + chat_room + '|' + command    # full msg to be sent to server
    client_socket.sendall(out_msg.encode()) # sends msg to server 
        
    print(f'check_login_commands out_msg: {out_msg}')   # prints msg sent to server - on terminal
    
    in_msg = client_socket.recv(1024).decode('utf-8')   # receives msg from server
    
    print(f'check_login_commands in_msg {in_msg}')      # print msg received from server - on terminal
    
    if in_msg != '':    # if the incomming msg is not empty - show it on a messagebox
        messagebox.showinfo('Server', in_msg)
        if in_msg == f'{chat_room} not found':
            answer = messagebox.askyesno('Server', f'Do you want to create {chat_room}?')
            if answer:
                messagebox.showinfo('Server', f'Creating {chat_room} ...') 
                #client_socket.sendall('[CREATE]'.encode())  
                chat_room_window(username, chat_room)              
            else:
                exit_application()
        elif in_msg == f'{chat_room} already exists':
            answer = messagebox.askyesno('Server', f'Do you want to join {chat_room}?') 
            if answer:
                messagebox.showinfo('Server', f'Joining {chat_room} ...')
                chat_room_window(username, chat_room) 
            else:
                exit_application()
        elif in_msg == f'{chat_room} found' or in_msg == f'{chat_room} created':
            chat_room_window(username, chat_room)              
    else:
        messagebox.showerror('Server', 'You must [JOIN] or [CREATE] a chat room to proceed')

# closes cilent socket and exits/terminates process in terminal
def exit_application():
    client_socket.sendall('[EXIT]'.encode())
    client_socket.close()
    login_window.destroy()
    os._exit(0)

# creates chat room window   
def chat_room_window(username, chat_room):    
    # show chat window
    chat_window.deiconify()
    chat_window.title(f'Welcome to {chat_room}')
    chat_window.resizable(width = False, height = False)
    chat_window.geometry('470x550')
    
    header_label= Label(chat_window, text = username, pady = 5)
    header_label.place(relwidth = 1)
    
    line = Label(chat_window, width = 450)
    line.place(relwidth = 1, rely = 0.07, relheight = 0.012)
    
    global text_box 
    text_box = Text(chat_window, width=20, height=2, padx=5, pady=5)
    text_box.place(relheight=0.745, relwidth=1, rely=0.08)
    
    bottom_label = Label(chat_window, height = 80)
    bottom_label.place(relwidth = 1, rely = 0.825)
 
    global msg_entry 
    msg_entry = Entry(bottom_label)
    msg_entry.place(relwidth = 0.74, relheight = 0.06, rely = 0.008, relx = 0.011)
    msg_entry.focus()
    
    out_msg = msg_entry.get()
    print(f'chat_room_window out_msg {out_msg}')
 
    # create a Send Button
    msg_button = Button(bottom_label, text = "Send", width = 20, command = lambda: send_button(msg_entry.get()))
    msg_button.place(relx = 0.77, rely = 0.008, relheight = 0.06, relwidth = 0.22)
    text_box.config(cursor = "arrow")
 
    scrollbar = Scrollbar(text_box) # create a scroll bar
    # place the scroll bar into the gui window
    scrollbar.place(relheight = 1, relx = 0.974)
    scrollbar.config(command = text_box.yview)
    text_box.config(state = DISABLED)
     
    threading.Thread(target = recv_msg).start()
        
# function to basically start the thread for sending messages
def send_button(msg):           
    text_box.config(state = DISABLED)
    out_msg = msg
    msg_entry.delete(0, END)
    threading.Thread(target = send_msg, args = (out_msg,)).start()

# sends the msg typed by user after clicking the send button - to server - to chat room   
def send_msg(msg):
    while True:
        out_msg = msg
        client_socket.sendall(out_msg.encode())
        break

# receives msg from server - from other user in the same chat room 
def recv_msg():
    while True:
        in_msg = client_socket.recv(1024).decode('utf-8')
        print(in_msg)
        
        if in_msg != '':
            text_box.config(state = NORMAL)
            text_box.insert(END, in_msg + '\n')
            text_box.config(state = DISABLED)
            text_box.see(END)
        else:
            print('something is wrong - recv_msg() client side')
    
def main():
    login_window.mainloop()
    
main()