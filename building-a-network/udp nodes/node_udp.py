from functions import broadcast_socket, listen_socket, listen_for_discovery_response, order_supplies,grabip
import socket
import threading
import time


def main():
    broadcast_port = 21000
    listen_port = 20000
    broadcast_address = '255.255.255.255'
    ip_address = grabip() 
    print("Your IP: " + ip_address)
    

    my_details = {
    'name': input("Enter supplier name: "),
    'ip': ip_address, 
    'ingredient': input("Enter ingredient: "),
    'quality': input("Enter quality of entered ingredient: "),
    'quantity': int(input("Enter quantity available: "))
    }

    
    threading.Thread(target=broadcast_socket, args=(broadcast_address, broadcast_port)).start()
    threading.Thread(target=listen_socket, args=(broadcast_port, listen_port, my_details)).start()
    threading.Thread(target=listen_for_discovery_response, args=(listen_port,)).start()
    threading.Thread(target=order_supplies).start()
    

    




if __name__ == "__main__":
    main()
