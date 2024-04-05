import socket
import ssl
import json

def send_request(request_type, data=None):
    HOST = 'localhost'  # Server's IP address or hostname
    PORT = 12347        # Port on which the server is listening

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        ssl_socket = ssl.wrap_socket(s, ssl_version=ssl.PROTOCOL_TLS)
        try:
            ssl_socket.connect((HOST, PORT))
            request = f"{request_type.lower()} {data}"  # Use a space as delimiter
            ssl_socket.sendall(request.encode())
            response = ssl_socket.recv(4096).decode()
            return response
        except Exception as e:
            print("Error:", e)
            return None

'''def print_oids(oids):
    print("OIDs available:")
    for oid in oids:
        print(oid)'''
def print_oids(oids, json_data):
    print("OIDs available:")
    for oid in oids:
        print(f"{oid}: {json_data['mibs'][oid]['name']}")


def main():
    with open('data.txt', 'r') as file:
        '''json_data = json.load(file)
        oids = list(json_data['mibs'].keys())
    
    print_oids(oids)  # Print all OID values'''
        json_data = json.load(file)
        oids = list(json_data['mibs'].keys())
    
        print_oids(oids, json_data)  # Print all OID values

    while True:
        print("\nChoose an option:")
        print("1. Send update request")
        print("2. Send query request")
        print("3. Add new OID")
        print("4. Exit")
        
        choice = input("Enter your choice (1/2/3/4): ")
        
        if choice == '1':
            oid = input("Enter OID: ")
            name = input("Enter new name: ")
            description = input("Enter new description: ")
            max_access = input("Enter new max-access: ")
            status = input("Enter new status: ")
            update_request = f"{oid},{name},{description},{max_access},{status}"  # Delimiter between OID, name, description, max-access, and status
            response = send_request('update', update_request)
            if response:
                print("Response (Update):", response)
            else:
                print("Failed to receive response for update request.")
        elif choice == '2':
            oid = input("Enter OID: ")
            response = send_request('query', oid)
            if response:
                print("Response (Query):", response)
            else:
                print("Failed to receive response for query request.")
        elif choice == '3':
            oid = input("Enter new OID: ")
            name = input("Enter name: ")
            description = input("Enter description: ")
            max_access = input("Enter max-access: ")
            status = input("Enter status: ")
            add_oid_request = f"{oid},{name},{description},{max_access},{status}"
            response = send_request('add', add_oid_request)
            if response:
                print("Response (Add OID):", response)
            else:
                print("Failed to receive response for add OID request.")
        elif choice == '4':
            print("Exiting...")
            send_request('exit')
            break
        else:
            print("Invalid choice. Please enter 1, 2, 3, or 4.")

if __name__ == "__main__":
    main()
