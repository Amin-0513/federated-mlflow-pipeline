import socket
import json
import os

HOST = '127.0.0.1'
PORT = 5001
USERNAME = "Amin"

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((HOST, PORT))

print("Server:", client_socket.recv(1024).decode())

def send_file(file_path):
    filename = os.path.basename(file_path)
    filesize = os.path.getsize(file_path)

    metadata = {
        "username": USERNAME,
        "filename": filename,
        "filesize": filesize
    }

    # Send JSON metadata
    client_socket.sendall(json.dumps(metadata).encode())

    # Send file bytes
    with open(file_path, "rb") as f:
        while True:
            data = f.read(4096)
            if not data:
                break
            client_socket.sendall(data)

    print(f"Sent {filename} successfully")

# Send .pth file
send_file("brain_tumor_cnn.pth")

# Close connection
choice = input("Type 'close' to terminate the connection: ")
if choice.lower() == "close":
    client_socket.sendall(b"close")
    client_socket.close()
    print("Connection closed")
