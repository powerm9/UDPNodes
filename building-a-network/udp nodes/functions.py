import socket
import threading
import time
import sys
from itertools import cycle


def grabip():
    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)
    return ip_address

hostIP = grabip()

class Supplier:
    def __init__(self, name, ip_address, ingredient, quality, quantity):
        self.name = name
        self.ip_address = ip_address
        self.ingredient = ingredient
        self.quality = quality 
        self.quantity = quantity

suppliers_list = []    
previous_suppliers_list = []
print_lock = threading.Lock()  # Lock for thread-safe printing
init_timestmp = 0
connect_timestmp = 0
rtt = 0

def broadcast_socket(broadcast_address, broadcast_port):

    broadcast_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    broadcast_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    while True:
        global init_timestmp
        try:
            message = f"PIZZA"
            broadcast_socket.sendto(message.encode(), (broadcast_address, broadcast_port))
            # print_pizza()
            print("sent pizza")
            init_timestmp = time.time()
            time.sleep(5) 
        except KeyboardInterrupt:
            broadcast_socket.close()
            break

def send_response(message, ip, port):
    """
    Sends a message to the specified IP address and port.
    """
    response_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        response_socket.sendto(message.encode(), (ip, port))
    finally:
        response_socket.close()



def listen_socket(discovery_port, listen_port, my_details):

    discovery_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    discovery_socket.bind(('0.0.0.0', discovery_port))
    while True:
        # print_listen()
        data, sender_address = discovery_socket.recvfrom(1024)

        message = data.decode()
        if (message.startswith("PIZZA")) & (hostIP not in sender_address):
            response_message = f"DETAILS {my_details['name']} {my_details['ip']} {my_details['ingredient']} {my_details['quality']} {my_details['quantity']} "
            send_response(response_message, sender_address[0], listen_port)
            print("sent details as response to pizza")

def listen_for_discovery_response(listen_port):
    global init_timestmp, connect_timestmp, rtt
    discovery_received_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    discovery_received_socket.bind(('0.0.0.0', listen_port))
    while True:
        data, sender_address = discovery_received_socket.recvfrom(1024)
        message = data.decode()
        if message.startswith("DETAILS"):
            _,name, ip_address, ingredient, quality, quantity = message.split()
            if not any(supplier.name == name for supplier in suppliers_list):
                connect_timestmp = time.time()
                rtt = abs(connect_timestmp - init_timestmp)
                new_supplier = Supplier(name, ip_address, ingredient, quality, quantity, rtt)
                suppliers_list.append(new_supplier)
                
                print("appended list")

def order_supplies():
    global previous_suppliers_list

    while True:
        if suppliers_list != previous_suppliers_list:
            print_node_list(suppliers_list)
            previous_suppliers_list = suppliers_list.copy()
        time.sleep(2)

def print_node_list(suppliers_list):
    print("\n+--------------------------------------------------------------------------------------------+")
    print("|                   Nodes                                                                    |")
    print("+--------------------------------------------------------------------------------------------+")
    for supplier in suppliers_list:
        print(f"| Name: {supplier.name}, IP Address: {supplier.ip_address}, Ingredient: {supplier.ingredient}, Quality: {supplier.quality}, Quantity: {supplier.quantity}, Rtt: {rtt}")
        print("+--------------------------------------------------------------------------------------------+")

def print_listen():
    line_characters = ['|', '/', '-', '\\']  # Characters for the rotating line
    rotating_line = cycle(line_characters)
    
    while True:
        char = next(rotating_line)
        sys.stdout.write("\rlistening " + char)
        sys.stdout.flush()  # Flush the output buffer to make sure it's displayed immediately
        time.sleep(0.1)  # Adjust the speed of rotation by changing the sleep time
