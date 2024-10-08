import socket
import threading
import time
import sys
from itertools import cycle
import os

stopThreads = False     
broadcasting = False
pinging = False
nodecount = 0
negotiation_port = 7000
suppliers_list = []    
previous_suppliers_list = []
print_lock = threading.Lock()  # Lock for thread-safe printing
init_timestmp = 0
connect_timestmp = 0
rtt = 0
chatprint = False

# broadcast_port = 6000
# listen_port = 5000
# broadcast_address = '255.255.255.255'


def thread_start():
    global stopThreads
    stopThreads = False

def thread_stop():
    global stopThreads
    stopThreads = True

def grabip():
    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)
    return ip_address

def get_ip_address():
    try:
        # Create a socket object
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # Connect to a known address, doesn't actually send any data
        s.connect(("8.8.8.8", 80))

        # Get the socket's own address
        ip_address = s.getsockname()[0]

        return ip_address
    except Exception as e:
        print("Error:", e)
        return None


hostIP = get_ip_address()



class Supplier:
    def __init__(self, name, ip_address, ingredient, quality, quantity, connection, rtt):
        self.name = name
        self.ip_address = ip_address
        self.ingredient = ingredient
        self.quality = quality 
        self.quantity = quantity
        self.connection = connection
        self.rtt = rtt

def send_msg(address, port, name, usermessage):
    msg = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    msg.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    message = f"CHAT {name} {usermessage}"
    try:
        msg.sendto(message.encode(), (address, port))
    finally:
        msg.close()

def alive_socket(broadcast_port):
    alive_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    print("alive socket started")
    while True:
        print("alive socket")
        if len(suppliers_list) > 0:
            for supplier in suppliers_list:
                messageALIVE = f"ALIVE"
                ip = supplier.ip_address
                print("alive sent")
                alive_socket.sendto(messageALIVE.encode(), (ip, broadcast_port))


def broadcast_socket(broadcast_address, broadcast_port):
    broadcast_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    broadcast_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    while broadcasting == False:
        global init_timestmp
        message = f"PIZZA"
        broadcast_socket.sendto(message.encode(), (broadcast_address, broadcast_port))
        # print_pizza()
        # print("sent pizza")
        init_timestmp = time.time()
        time.sleep(1)

    broadcast_socket.shutdown(socket.SHUT_RDWR)
    broadcast_socket.close
    print("Broadcast pizza thread exited...")


# def send_response(message, ip, port):
#     """
#     Sends a message to the specified IP address and port.
#     """
#     response_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#     try:
#         response_socket.sendto(message.encode(), (ip, port))
#     finally:
#         response_socket.close()



def listen_socket(discovery_port, listen_port, my_details):
    global suppliers_list

    discovery_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    discovery_socket.bind(('0.0.0.0', discovery_port))
    
    while True:
        data, sender_address = discovery_socket.recvfrom(1024)
        message = data.decode()
        
        if (message.startswith("PIZZA")) & (hostIP not in sender_address):
            response_message = f"DETAILS {my_details['name']} {my_details['ip']} {my_details['ingredient']} {my_details['quality']} {my_details['quantity']}"
            discovery_socket.sendto(response_message.encode(), (sender_address[0], listen_port))
            
        if message.startswith("ALIVE"):
            response_message = f"YES {my_details['name']} {my_details['ip']} {my_details['ingredient']} {my_details['quality']} {my_details['quantity']}"
            discovery_socket.sendto(response_message.encode(), (sender_address[0], listen_port))
        
        if message.startswith("YES"):
            _, name, ip_address, ingredient, quality, quantity = message.split()
            for supplier in suppliers_list:
                supplier.connection = 0  # Set all connections to 0 initially
            for supplier in suppliers_list:
                print(supplier)
                if supplier.ip_address == ip_address:
                    supplier.name = name
                    supplier.ip_address = ip_address
                    supplier.ingredient = ingredient
                    supplier.quality = quality
                    supplier.quantity = quantity
                    supplier.connection = 1  # Set connection to 1 for the supplier with the matching IP
                    menu_printer(my_details)
                    break  

        if message.startswith("CHAT"):
            _, name, *chatmsg = message.split()
            chatmsg = ' '.join(chatmsg)
            if chatprint == True:
                print(f'[{name}]: {chatmsg}')
                
            
            


            


        # if message.startswith("YES"):
        #     _, name, ip_address, ingredient, quality, quantity = message.split()

        # time.sleep(1)
        



def listen_for_discovery_response(listen_port):
    global init_timestmp, connect_timestmp, rtt, nodecount
    discovery_received_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    discovery_received_socket.bind(('0.0.0.0', listen_port))
    while True:
        data, sender_address = discovery_received_socket.recvfrom(1024)
        message = data.decode()
        if message.startswith("DETAILS"):
            # print("received details")
            _,name, ip_address, ingredient, quality, quantity = message.split()
            if not any(supplier.name == name for supplier in suppliers_list):
                connect_timestmp = time.time()
                rtt = abs(connect_timestmp - init_timestmp)
                rtt *= 1000
                rtt = round(rtt, 2)
                new_supplier = Supplier(name, ip_address, ingredient, quality, quantity, 1, rtt)
                suppliers_list.append(new_supplier)
            
                nodecount = nodecount + 1
                
                # print("appended list")


def check_list():
    global previous_suppliers_list, rtt
    print_node_list(suppliers_list)
    while stopThreads == False:
        if suppliers_list != previous_suppliers_list:

            os.system('cls' if os.name == 'nt' else 'clear')
            print_node_list(suppliers_list)
            previous_suppliers_list = suppliers_list.copy()
            
        time.sleep(2)
    # print("Checklist printer thread exited...")


def print_node_list(suppliers_list):
    menu_printer(my_details)
    print("|                                 NODES                                                    |")
    print("|------------------------------------------------------------------------------------------|")
    print("|     Name      |  IP Address   | Ingredients | Quality | Quantity | RTT (ms) | Connection |")
    print("|------------------------------------------------------------------------------------------|")

    for supplier in suppliers_list:

        connect_timestmp = time.time()
        rtt = abs(connect_timestmp - init_timestmp)
        rtt *= 1000
        rtt = round(rtt, 2)
        # supplier.rtt = round(rtt, 2)
        name_column = supplier.name.center(13)  # Adjust the width as needed
        ip_address_column = supplier.ip_address.center(13)  # Adjust the width as needed
        ingredient_column = supplier.ingredient.center(11)  # Adjust the width as needed
        quality_column = str(supplier.quality).center(7)  # Adjust the width as needed
        quantity_column = str(supplier.quantity).center(8)  # Adjust the width as needed
        rtt_column = str(rtt).center(5)  # Adjust the width as needed
        con_column = str(supplier.connection).center(8)

        print(f"| {name_column} | {ip_address_column} | {ingredient_column} | {quality_column} | {quantity_column} | {rtt_column}     | {con_column} |")
        print("|-------------------------------------------------------------------------------------------|")

def print_listen():
    line_characters = ['|', '/', '-', '\\']  # Characters for the rotating line
    rotating_line = cycle(line_characters)
    
    while stopThreads == False:
        char = next(rotating_line)
        sys.stdout.write("\rlistening " + char)
        sys.stdout.flush()  # Flush the output buffer to make sure it's displayed immediately
        time.sleep(0.1)  # Adjust the speed of rotation by changing the sleep time
    # print("Listen printer thread done...")
        

def negotiate(requested_ingredient, requested_quantity, requested_quality):
    global my_details
# Simple negotiation logic: accept if quantity is sufficient and quality matches
    # print("Requested ingredient:" , requested_ingredient)
    # print("Requested quantity: ", requested_quantity)
    # print("Requested quality:", requested_quality)
    # Turn requested ingredient into an int

    if my_details['ingredient'] == requested_ingredient and my_details['quantity'] >= requested_quantity and my_details['quality'] == requested_quality:
        my_details['quantity'] = (my_details['quantity']) - requested_quantity
        # display_quantity  = int(self.quantity) - int(requested_quantity)  # Deduct the quantity
        # self.quantity = display_quantity
        

        return f"Accepted. Their remaining quantity: {my_details['quantity']} {requested_quantity}"
    return f"Rejected, they want: {requested_quantity}, you only have: {my_details['quantity']} "



def listen_for_negotiation_requests(port):
    negotiation_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    negotiation_socket.bind(('0.0.0.0', port))
    global updatequantity
    while True:
        data, sender_address = negotiation_socket.recvfrom(1024)
        message = data.decode()

        if message.startswith("NEGOTIATE"):
            _, ingredient, quantity, quality = message.split()
            for supplier in suppliers_list:
                # if supplier.ip_address == sender_address[0]:  # Avoid self-negotiation
                #     continue
                response = negotiate(ingredient, int(quantity), quality)
                response_message = f"Negotiation {response} "
                negotiation_socket.sendto(response_message.encode(), (sender_address[0], port))
                # Assuming one supplier per IP for simplicity
            
        if message.startswith("Negotiation Accepted."):
            words = message.split()
            updatequantity = ' '.join(words[6:])
            updatequantity = int(updatequantity)
            first_words = ' '.join(words[:6])
            my_details['quantity'] += updatequantity
            menu_printer(my_details)
            # time.sleep(1)
            print_node_list(suppliers_list)
            print(first_words)

        if message.startswith("Rejected"):
            print(message)
            

def negotiating(negotiation_port):
    global negotiate_socket
    negotiate_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    print("\nPick a node you may like to trade with from above")

    try: 
        while True:
            name = input("\nName: ")
            quantity = int(input("Quantity: ").strip())
            
            for supplier in suppliers_list:
                if name == supplier.name:
                    target_ip = supplier.ip_address
                    ingredient = supplier.ingredient
                    quality = supplier.quality
                
            # Assuming the negotiation port is known and fixed for simplicity
            message = f"NEGOTIATE {ingredient} {quantity} {quality}"
            negotiate_socket.sendto(message.encode(), (target_ip, negotiation_port))
            break
    except KeyboardInterrupt:
        menu_printer(my_details)
        





def menu_printer(details):
    global my_details, nodecount
    my_details = details
    menuquality = str(details['quality'])
    menuquantity = str(details['quantity'])
    menuname     = str(details['name'])
    nodecnt_str = str(nodecount)
    os.system('cls' if os.name == 'nt' else 'clear')

    print("--------------------------------------------------------------------------------------")
    print(" ███╗   ██╗ ██████╗ ██████╗ ███████╗    ███████╗                        Matthew")
    print(" ████╗  ██║██╔═══██╗██╔══██╗██╔════╝    ╚════██║                          Maria")
    print(" ██╔██╗ ██║██║   ██║██║  ██║█████╗          ██╔╝                          Sarah")
    print(" ██║╚██╗██║██║   ██║██║  ██║██╔══╝         ██╔╝                          Isabel")
    print(" ██║ ╚████║╚██████╔╝██████╔╝███████╗       ██║   ")
    print(" ╚═╝  ╚═══╝ ╚═════╝ ╚═════╝ ╚══════╝       ╚═╝   ")     
    print("                                                                               ")     
    print(" ██████╗ ███████╗████████╗ █████╗ ██╗██╗     ███████╗    Name: ",menuname.rjust(15))
    print(" ██╔══██╗██╔════╝╚══██╔══╝██╔══██╗██║██║     ██╔════╝██╗ IP: ", details['ip'].rjust(17))
    print(" ██║  ██║█████╗     ██║   ███████║██║██║     ███████╗╚═╝ Ingredient: ", details['ingredient'].rjust(9)) 
    print(" ██║  ██║██╔══╝     ██║   ██╔══██║██║██║     ╚════██║██╗ Quality: ", menuquality.rjust(12)) 
    print(" ██████╔╝███████╗   ██║   ██║  ██║██║███████╗███████║╚═╝ Quantity: ", menuquantity.rjust(11))
    print(" ╚═════╝ ╚══════╝   ╚═╝   ╚═╝  ╚═╝╚═╝╚══════╝╚══════╝    Nodes Found: ", nodecnt_str.rjust(8))
    print("--------------------------------------------------------------------------------------")  
           
# def clear_screen():
#     os.system('cls' if os.name == 'nt' else 'clear')

                                                       
def show_nodes():
    global menu
    menu = False
    menu_printer(my_details)

    thread_start()
    try: 
        
        threading.Thread(target=check_list,).start()
        threading.Thread(target=print_listen).start()
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        thread_stop()
        menu = True
        menu_printer(my_details)
        
def negotiate_nodes():
    global menu

    menu = False
    # menu_printer(my_details)
    thread_start()
    try: 
        threading.Thread(target=check_list,).start()
        time.sleep(0.5)
        threading.Thread(target=negotiating, args=(negotiation_port,)).start()

        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        global negotiate_socket
        negotiate_socket.close()
        menu = True
        # menu_printer(my_details)
def chat(address, port):
    global menu, chatprint
    menu = False
    chatprint = True
    name = my_details['name']
    try:
        menu_printer(my_details)
        usermessage = "has joined the chat"
        print("Welcome to the chat, enter input:")
        send_msg(address, port, name, usermessage)
        while True:

            usermessage = input("")
            send_msg(address, port, name, usermessage)
    except: KeyboardInterrupt

    try:
        menu_printer
        chatprint = True
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
            chatprint = False
            menu = True

# def print_targets():

