import socket
import ssl
import json
from threading import Thread

def load_data_from_file(filename):
    with open(filename, 'r') as file:
        return json.load(file)

def handle_request(client_socket, client_address, json_data):
    print(f"Connection from {client_address} has been established.")
    try:
        while True:
            request_data = client_socket.recv(1024).decode().strip()
            request_parts = request_data.split()
            if len(request_parts) >= 2:
                request_type = request_parts[0]
                data = ' '.join(request_parts[1:])
                if request_type == 'exit':
                    print("Exiting...")
                    break
                elif request_type == 'update':
                    update_request = data.split(',')
                    if len(update_request) == 5:
                        oid, name, description, max_access, status = update_request
                        if oid in json_data['mibs']:
                            # Update the mib data
                            json_data['mibs'][oid]['name'] = name
                            json_data['mibs'][oid]['description'] = description
                            json_data['mibs'][oid]['max-access'] = max_access
                            json_data['mibs'][oid]['status'] = status
                            response = {"status": "success", "message": f"Updated OID {oid} successfully"}
                        else:
                            response = {"status": "error", "message": f"OID {oid} not found"}
                    else:
                        response = {"status": "error", "message": "Invalid update request format"}
                    client_socket.sendall(json.dumps(response).encode())
                    with open('data.txt', 'w') as file:
                        json.dump(json_data, file)
                elif request_type == 'query':
                    if data in json_data['mibs']:
                        # Retrieve the mib data
                        response_data = json_data['mibs'][data]
                    else:
                        response_data = {"name": "OID not found", "description": "OID not found"}
                    client_socket.sendall(json.dumps(response_data).encode())
                elif request_type == 'add':
                    add_request = data.split(',')
                    if len(add_request) == 5:
                        oid, name, description, max_access, status = add_request
                        if oid not in json_data['mibs']:
                            json_data['mibs'][oid] = {'name': name, 'description': description, 'max-access': max_access, 'status': status}
                            response = {"status": "success", "message": f"Added OID {oid} successfully"}
                        else:
                            response = {"status": "error", "message": f"OID {oid} already exists"}
                    else:
                        response = {"status": "error", "message": "Invalid add request format"}
                    client_socket.sendall(json.dumps(response).encode())
                    with open('data.txt', 'w') as file:
                        json.dump(json_data, file)
                else:
                    response = {"status": "error", "message": "Invalid request type"}
                    client_socket.sendall(json.dumps(response).encode())
            else:
                response = {"status": "error", "message": "Invalid request format"}
                client_socket.sendall(json.dumps(response).encode())
    except Exception as e:
        print("Error handling request:", e)
    finally:
        client_socket.close()

def start_server(host, port, certfile, keyfile):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((host, port))
        server_socket.listen(5)
        print(f"Server is listening on {host}:{port}...")
        while True:
            client_socket, client_address = server_socket.accept()
            ssl_socket = ssl.wrap_socket(client_socket, server_side=True, certfile="certificate.crt", keyfile="privateKey.key", ssl_version=ssl.PROTOCOL_TLS)
            print("SSL connection established.")
            client_thread = Thread(target=handle_request, args=(ssl_socket, client_address, load_data_from_file('data.txt')))
            client_thread.start()

if __name__ == "__main__":
    HOST = 'localhost'  # Server's IP address or hostname
    PORT = 12347        # Use a different port number
    CERTFILE = 'certificate.crt'  # Path to server certificate file
    KEYFILE = 'privateKey.key'    # Path to server private key file

    start_server(HOST, PORT, CERTFILE, KEYFILE)
