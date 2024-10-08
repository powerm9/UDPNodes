from functions import broadcast_socket, listen_socket, listen_for_discovery_response, check_list ,grabip, menu_printer, show_nodes, negotiate_nodes, listen_for_negotiation_requests, get_ip_address, chat, alive_socket
import time
import threading


broadcast_port = 6000
listen_port = 5000
negotiation_port = 7000
chat_port =  8000
broadcast_address = '255.255.255.255'

menu = True


def start_broadcast_threads():
    
    threading.Thread(target=broadcast_socket, args=(broadcast_address, broadcast_port)).start()
    # threading.Thread(target=alive_socket, args=(broadcast_port)).start()
    threading.Thread(target=listen_socket, args=(broadcast_port, listen_port, my_details,)).start()
    threading.Thread(target=listen_for_discovery_response, args=(listen_port,)).start()
    threading.Thread(target=listen_for_negotiation_requests, args=(negotiation_port,)).start()


def main():
    global my_details, menu
    ip_address = get_ip_address()
    details = {
    'name': (" "),
    'ip': ip_address, 
    'ingredient': (""),
    'quality': (""),
    'quantity': ("")
    }

    menu_printer(details)

    my_details = {
    'name': input("Enter supplier name: "),
    'ip': ip_address, 
    'ingredient': input("Enter ingredient: "),
    'quality': input("Enter quality of entered ingredient: "),
    'quantity': int(input("Enter quantity available: "))
    }
    

    # clear_screen()
    menu_printer(my_details)
    start_broadcast_threads()

    
    while menu:
        menu_printer(my_details)

        print("Enter Selection:")
        print("1. Show nodes in communication")
        print("2. Negotiate")
        print("3. Chat")


        choice = input("")

        options = {
        '1': lambda: show_nodes(),
        '2': lambda: negotiate_nodes(),
        '3': lambda: chat(broadcast_address, broadcast_port),
        }
        

        selected_option = options.get(choice, lambda: print("Invalid choice."))
        selected_option()
        


if __name__ == "__main__":
    main()
